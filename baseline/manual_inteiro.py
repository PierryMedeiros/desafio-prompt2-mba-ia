"""Classificador ingênuo: uma chamada por onda, com o manual inteiro em cada uma.

NÃO ALTERE ESTE ARQUIVO. Ele é o ponto de partida do desafio e o exemplo da
interface que o seu pipeline precisa ter. O teste de aptidão (ferramentas/aptidao.py)
reutiliza a função classificar_onda.

Uso (a partir da raiz do repositório):

    python -m baseline.manual_inteiro --manual data/manual.md --tickets data/dev/tickets.jsonl --saida runs/baseline

Acerta quase tudo e estoura o orçamento: cada onda paga o manual inteiro.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

from ferramentas.config import TAMANHO_ONDA
from ferramentas.llm import ClienteLLM

RAIZ = Path(__file__).resolve().parent.parent
ARQ_ACOES = RAIZ / "data" / "acoes.yaml"
ACAO_PADRAO = "suporte_padrao"

# Uma linha "ID acao", tolerando markdown, dois-pontos, hífen ou barra entre os dois.
LINHA = re.compile(r"^\s*[`*]*([A-Za-z]\d+)[`*]*\s*[:\-|]?\s*[`*]*([a-z_]+)[`*]*\s*[.;]?\s*$")


def ler_acoes() -> list[str]:
    with open(ARQ_ACOES, encoding="utf-8") as arquivo:
        return list(yaml.safe_load(arquivo))


def ler_tickets(caminho: str | Path) -> list[dict]:
    with open(caminho, encoding="utf-8") as arquivo:
        return [json.loads(linha) for linha in arquivo if linha.strip()]


def ondas(tickets: list[dict]) -> list[list[dict]]:
    """Ondas fixas: os tickets 1 a 10 do arquivo são a primeira onda, os 11 a 20 a segunda, e assim por diante."""
    return [tickets[i:i + TAMANHO_ONDA] for i in range(0, len(tickets), TAMANHO_ONDA)]


def montar_system(manual: str, acoes: list[str]) -> str:
    return (
        "Você é analista de triagem do atendimento da Orbita. Decida a ação de cada ticket "
        "seguindo o Manual de Atendimento abaixo.\n\n"
        "Cada ticket vem em JSON com o id, o texto do cliente e os metadados do CRM.\n"
        "Ações possíveis: " + ", ".join(acoes) + ".\n\n"
        "Responda somente com uma linha por ticket, no formato:\n"
        "<id> <acao>\n"
        "Sem nenhum outro texto.\n\n"
        "=== MANUAL ===\n" + manual + "\n=== FIM DO MANUAL ==="
    )


def interpretar(resposta: str, ids: set[str], acoes: list[str]) -> dict[str, str]:
    """Extrai {id: acao} da resposta, ignorando linhas fora do formato, IDs de fora e ações inválidas."""
    obtidos: dict[str, str] = {}
    for linha in resposta.splitlines():
        m = LINHA.match(linha)
        if m and m.group(1) in ids and m.group(1) not in obtidos and m.group(2) in acoes:
            obtidos[m.group(1)] = m.group(2)
    return obtidos


def classificar_onda(llm: ClienteLLM, manual: str, acoes: list[str], onda: list[dict], repetir: bool = True) -> dict[str, str]:
    """Classifica uma onda numa chamada. Com repetir=True, refaz a chamada uma vez se faltar
    algum ticket ou vier ação inválida. Devolve só os tickets que o modelo classificou."""
    ids = {t["id"] for t in onda}
    mensagens = [
        {"role": "system", "content": montar_system(manual, acoes)},
        {"role": "user", "content": json.dumps(onda, ensure_ascii=False)},
    ]
    obtidos = interpretar(llm.chamar(mensagens), ids, acoes)
    if repetir and len(obtidos) < len(ids):
        for id_, acao in interpretar(llm.chamar(mensagens), ids, acoes).items():
            obtidos.setdefault(id_, acao)
    return obtidos


def main() -> None:
    parser = argparse.ArgumentParser(description="Classificador ingênuo: manual inteiro em toda onda.")
    parser.add_argument("--manual", required=True, help="arquivo do manual (ex.: data/manual.md)")
    parser.add_argument("--tickets", required=True, help="arquivo de tickets (ex.: data/dev/tickets.jsonl)")
    parser.add_argument("--saida", required=True, help="pasta nova da execução (ex.: runs/baseline)")
    args = parser.parse_args()

    manual = Path(args.manual).read_text(encoding="utf-8")
    acoes = ler_acoes()
    tickets = ler_tickets(args.tickets)
    llm = ClienteLLM(args.saida)

    previsoes: dict[str, str] = {}
    faltantes: list[str] = []
    for numero, onda in enumerate(ondas(tickets), start=1):
        obtidos = classificar_onda(llm, manual, acoes, onda)
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


if __name__ == "__main__":
    main()
