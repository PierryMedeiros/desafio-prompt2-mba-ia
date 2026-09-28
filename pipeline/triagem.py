"""Pipeline de triagem em lote: prepara o contexto a partir do manual e classifica as ondas.

Uso (a partir da raiz do repositório):

    python -m pipeline.triagem --manual data/manual.md --tickets data/dev/tickets.jsonl --saida runs/dev

Etapas:
1. Preparação: uma chamada com o manual integral no user e, no system, o pedido de
   extração das regras de decisão (pipeline/prompts.py). A resposta é o caderno de regras.
2. Ondas: uma chamada por onda de 10 tickets, com o caderno no system e os tickets
   integrais (mais fatos de calendário calculados no código) no user.
3. Tickets sem resposta válida são reenviados uma vez, só eles, na mesma onda. O que
   ainda faltar recebe a ação padrão fixa.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

from baseline.manual_inteiro import ler_acoes, ler_tickets, ondas
from harness.llm import ClienteLLM
from pipeline import prompts

ACAO_PADRAO = "suporte_padrao"
PARALELO = 5
DATA_TEXTO = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
ID_NO_INICIO = re.compile(r"^[\s`*\-]*([A-Za-z]\d+)\b")
PALAVRA = re.compile(r"[a-z_]+")


# ------------------------------------------------------------------ fatos neutros


def _data(texto: str) -> date:
    return date.fromisoformat(texto[:10])


def meses_completos(inicio: date, fim: date) -> int:
    """Meses de calendário completos entre duas datas."""
    meses = (fim.year - inicio.year) * 12 + (fim.month - inicio.month)
    if fim.day < inicio.day:
        meses -= 1
    return meses


def fatos(ticket: dict) -> dict:
    """Contas de calendário a partir dos metadados e das datas do texto. Não compara com limite nenhum."""
    abertura = _data(ticket["data_abertura"])
    resultado = {
        "meses_completos_de_casa": meses_completos(_data(ticket["cliente_desde"]), abertura),
    }
    cobranca = ticket.get("cobranca")
    if isinstance(cobranca, dict) and cobranca.get("data"):
        resultado["dias_da_cobranca_ate_abertura"] = (abertura - _data(cobranca["data"])).days
    datas = {}
    for dia, mes, ano in DATA_TEXTO.findall(ticket["texto"]):
        try:
            d = date(int(ano), int(mes), int(dia))
        except ValueError:
            continue
        datas[f"{int(dia):02d}/{int(mes):02d}/{ano}"] = (abertura - d).days
    if datas:
        resultado["dias_de_cada_data_do_texto_ate_abertura"] = datas
    return resultado


# ------------------------------------------------------------------ resposta


def interpretar(resposta: str, ids: set[str], acoes: list[str]) -> dict[str, str]:
    """Extrai {id: acao} de linhas "<id> | ... | <acao>": o id no início e a última ação válida da linha.
    Linhas fora do formato, ids de fora da onda e ids repetidos são ignorados."""
    validas = set(acoes)
    obtidos: dict[str, str] = {}
    for linha in resposta.splitlines():
        m = ID_NO_INICIO.match(linha)
        if not m or m.group(1) not in ids or m.group(1) in obtidos:
            continue
        encontradas = [p for p in PALAVRA.findall(linha[m.end():]) if p in validas]
        if encontradas:
            obtidos[m.group(1)] = encontradas[-1]
    return obtidos


# ------------------------------------------------------------------ etapas


def preparar(llm: ClienteLLM, manual: str, acoes: list[str], modo: str) -> str:
    if modo == "generico":
        sistema = prompts.PREPARO_GENERICO
    else:
        sistema = prompts.PREPARO_EXTRACAO.format(acoes=", ".join(acoes))
    return llm.chamar([
        {"role": "system", "content": sistema},
        {"role": "user", "content": manual},
    ])


def classificar(llm: ClienteLLM, regras: str, acoes: list[str], onda: list[dict]) -> dict[str, str]:
    sistema = prompts.SISTEMA_ONDA.format(acoes=", ".join(acoes), regras=regras)

    def chamar(tickets: list[dict]) -> dict[str, str]:
        conteudo = json.dumps([{**t, "fatos": fatos(t)} for t in tickets], ensure_ascii=False)
        mensagens = [{"role": "system", "content": sistema}, {"role": "user", "content": conteudo}]
        try:
            resposta = llm.chamar(mensagens)
        except Exception as erro:  # noqa: BLE001
            print(f"  falha na chamada: {erro}", file=sys.stderr, flush=True)
            return {}
        return interpretar(resposta, {t["id"] for t in tickets}, acoes)

    obtidos = chamar(onda)
    faltantes = [t for t in onda if t["id"] not in obtidos]
    if faltantes:
        obtidos.update(chamar(faltantes))
    return obtidos


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Triagem em lote com contexto preparado pelo modelo.")
    parser.add_argument("--manual", required=True, help="arquivo do manual (ex.: data/manual.md)")
    parser.add_argument("--tickets", required=True, help="arquivo de tickets (ex.: data/dev/tickets.jsonl)")
    parser.add_argument("--saida", required=True, help="pasta nova da execução (ex.: runs/dev)")
    parser.add_argument("--preparo", choices=("extracao", "generico"), default="extracao",
                        help="prompt de preparação do contexto (padrão: extracao; generico só para comparação)")
    args = parser.parse_args(argv)

    manual = Path(args.manual).read_text(encoding="utf-8")
    acoes = ler_acoes()
    tickets = ler_tickets(args.tickets)
    llm = ClienteLLM(args.saida)

    print("Preparando o contexto a partir do manual...", flush=True)
    regras = preparar(llm, manual, acoes, args.preparo)
    (Path(args.saida) / "contexto.md").write_text(regras, encoding="utf-8")
    print(f"Contexto preparado: {len(regras)} caracteres", flush=True)

    lista_ondas = ondas(tickets)
    with ThreadPoolExecutor(max_workers=PARALELO) as executor:
        resultados = list(executor.map(lambda onda: classificar(llm, regras, acoes, onda), lista_ondas))

    previsoes: dict[str, str] = {}
    faltantes: list[str] = []
    for numero, (onda, obtidos) in enumerate(zip(lista_ondas, resultados), start=1):
        for ticket in onda:
            if ticket["id"] not in obtidos:
                faltantes.append(ticket["id"])
            previsoes[ticket["id"]] = obtidos.get(ticket["id"], ACAO_PADRAO)
        print(f"onda {numero}: {len(obtidos)} de {len(onda)} tickets classificados", flush=True)

    with open(Path(args.saida) / "saida.jsonl", "w", encoding="utf-8") as arquivo:
        for ticket in tickets:
            arquivo.write(json.dumps({"id": ticket["id"], "acao": previsoes[ticket["id"]]}, ensure_ascii=False) + "\n")
    if faltantes:
        print(f"{len(faltantes)} tickets sem resposta válida receberam {ACAO_PADRAO}: {', '.join(faltantes)}")
    print(f"saida.jsonl gravada em {args.saida}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
