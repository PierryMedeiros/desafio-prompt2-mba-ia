"""Verificador do desafio "O manual não cabe".

NÃO ALTERE ESTE ARQUIVO.

Uso (a partir da raiz do repositório):

    python -m ferramentas.verificar <pasta>
        [--manual data/manual.md]
        [--tickets data/dev/tickets.jsonl]
        [--gabarito data/dev/gabarito.jsonl]
        [--aptidao runs/aptidao]

Verifica, nesta ordem: aptidão do modelo, modelo usado, integridade da
saida.jsonl, rastreabilidade dos tickets no log.jsonl, respeito às ondas,
leitura do manual, custo em manuais e F1 macro. Termina com exit code 0
somente se todas as verificações passarem.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

from ferramentas.config import F1_MINIMO, ORCAMENTO_MANUAIS, TAMANHO_ONDA

RAIZ = Path(__file__).resolve().parent.parent
ARQ_ACOES = RAIZ / "data" / "acoes.yaml"
MAX_LISTADOS = 10
MAX_IDS_POR_REGRA = 5

# Capítulos do manual: cada linha que começa com "## " seguido de número e ponto
# (ex.: "## 13. Triagem e regras gerais") abre um capítulo, que vai até o próximo
# título desse tipo ou até o fim do arquivo. O corpo é o texto depois da linha do
# título, sem espaços nas pontas; o título em si não precisa aparecer no log.
TITULO_CAPITULO = re.compile(r"^## (\d+)\. .*$", re.MULTILINE)


# ---------------------------------------------------------------- utilidades


def ler_jsonl(caminho: Path) -> list[dict]:
    with open(caminho, encoding="utf-8") as arquivo:
        return [json.loads(linha) for linha in arquivo if linha.strip()]


def listar(itens: list[str]) -> str:
    mostrados = ", ".join(itens[:MAX_LISTADOS])
    resto = len(itens) - MAX_LISTADOS
    return f"{mostrados} e mais {resto}" if resto > 0 else mostrados


def formas(texto: str) -> tuple[str, str, str]:
    """O texto literal e as duas serializações em JSON aceitas (sem as aspas das pontas)."""
    return (
        texto,
        json.dumps(texto, ensure_ascii=True)[1:-1],
        json.dumps(texto, ensure_ascii=False)[1:-1],
    )


def aparece(texto: str, palheiro: str) -> bool:
    return any(forma in palheiro for forma in formas(texto))


def conteudo_da_chamada(registro: dict) -> str:
    partes = []
    for mensagem in registro.get("mensagens", []):
        if isinstance(mensagem, dict) and isinstance(mensagem.get("content"), str):
            partes.append(mensagem["content"])
    return "\x00".join(partes)


def capitulos(manual: str) -> list[tuple[str, str]]:
    """Divide o manual em capítulos: lista de (título, corpo sem espaços nas pontas)."""
    titulos = list(TITULO_CAPITULO.finditer(manual))
    resultado = []
    for i, m in enumerate(titulos):
        fim = titulos[i + 1].start() if i + 1 < len(titulos) else len(manual)
        resultado.append((m.group(0)[3:].strip(), manual[m.end():fim].strip()))
    return resultado


def linha(nome: str, ok: bool, detalhe: str = "") -> str:
    rotulo = f"{nome} ".ljust(21, ".")
    return f"{rotulo} {'OK' if ok else 'FALHOU'}" + (f" ({detalhe})" if detalhe else "")


# ---------------------------------------------------------------- leitura


def ler_log(pasta: Path):
    """Devolve (registros, problema). problema é None quando o log é legível e não vazio."""
    caminho = pasta / "log.jsonl"
    if not caminho.exists():
        return [], f"{caminho} não encontrado"
    registros, ruins = [], []
    with open(caminho, encoding="utf-8") as arquivo:
        for numero, texto in enumerate(arquivo, start=1):
            if not texto.strip():
                continue
            try:
                registro = json.loads(texto)
                int(registro["input_tokens"])
                int(registro["output_tokens"])
                if not isinstance(registro["mensagens"], list):
                    raise TypeError
            except (json.JSONDecodeError, KeyError, TypeError, ValueError):
                ruins.append(str(numero))
                continue
            registros.append(registro)
    if ruins:
        return registros, "linhas ilegíveis no log.jsonl: " + listar(ruins)
    if not registros:
        return registros, "log.jsonl vazio"
    return registros, None


def ler_saida(pasta: Path, ids: list[str], acoes: list[str]):
    """Devolve (previsoes, problemas). previsoes: id -> acao (primeira ocorrência válida)."""
    caminho = pasta / "saida.jsonl"
    problemas: list[str] = []
    previsoes: dict[str, str] = {}
    contagem: dict[str, int] = {}
    invalidas, acoes_invalidas, extras = [], [], []
    validos = set(ids)
    with open(caminho, encoding="utf-8") as arquivo:
        for numero, texto in enumerate(arquivo, start=1):
            if not texto.strip():
                continue
            try:
                registro = json.loads(texto)
            except json.JSONDecodeError:
                invalidas.append(str(numero))
                continue
            if not isinstance(registro, dict) or "id" not in registro or "acao" not in registro:
                invalidas.append(str(numero))
                continue
            id_, acao = str(registro["id"]), registro["acao"]
            contagem[id_] = contagem.get(id_, 0) + 1
            if id_ not in validos:
                if contagem[id_] == 1:
                    extras.append(id_)
                continue
            if acao not in acoes:
                acoes_invalidas.append(f"{id_} ({acao!r})")
                continue
            previsoes.setdefault(id_, acao)
    if invalidas:
        problemas.append("linhas que não são JSON com 'id' e 'acao': " + listar(invalidas))
    faltantes = [i for i in ids if i not in contagem]
    duplicados = [i for i, n in contagem.items() if n > 1]
    if faltantes:
        problemas.append(f"{len(faltantes)} IDs faltantes: " + listar(faltantes))
    if duplicados:
        problemas.append(f"{len(duplicados)} IDs duplicados: " + listar(duplicados))
    if extras:
        problemas.append(f"{len(extras)} IDs que não estão no arquivo de tickets: " + listar(extras))
    if acoes_invalidas:
        problemas.append(f"{len(acoes_invalidas)} ações fora de data/acoes.yaml: " + listar(acoes_invalidas))
    return previsoes, problemas


# ---------------------------------------------------------------- métricas


def metricas(previsoes: dict[str, str], gabarito: dict[str, dict]):
    """Devolve (tabela, f1_macro, acuracia). tabela: acao -> (P, R, F1, suporte), só ações presentes no gabarito."""
    presentes = []
    for g in gabarito.values():
        if g["acao"] not in presentes:
            presentes.append(g["acao"])
    tabela = {}
    for acao in presentes:
        tp = sum(1 for i, g in gabarito.items() if previsoes.get(i) == acao and g["acao"] == acao)
        fp = sum(1 for i, g in gabarito.items() if previsoes.get(i) == acao and g["acao"] != acao)
        fn = sum(1 for i, g in gabarito.items() if previsoes.get(i) != acao and g["acao"] == acao)
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * p * r / (p + r) if p + r else 0.0
        tabela[acao] = (p, r, f1, tp + fn)
    f1_macro = sum(v[2] for v in tabela.values()) / len(tabela)
    acuracia = sum(1 for i, g in gabarito.items() if previsoes.get(i) == g["acao"]) / len(gabarito)
    return tabela, f1_macro, acuracia


# ---------------------------------------------------------------- execução


def verificar(args) -> bool:
    pasta = Path(args.pasta)
    falhas: list[str] = []

    def registrar(nome: str, ok: bool, detalhe: str = ""):
        print(linha(nome, ok, detalhe))
        if not ok:
            falhas.append(nome)

    # 1. Aptidão
    arq_aptidao = Path(args.aptidao) / "resultado.json"
    aptidao = None
    if arq_aptidao.exists():
        try:
            aptidao = json.loads(arq_aptidao.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            aptidao = None
    if aptidao is None:
        registrar("Aptidão", False, f"{arq_aptidao} não encontrado ou ilegível; rode python -m ferramentas.aptidao")
        return False
    detalhe = (f"{aptidao.get('provider')} / {aptidao.get('model')}, unidade {aptidao.get('unidade')} tokens, "
               f"acurácia {float(aptidao.get('acuracia', 0)):.2f}")
    if aptidao.get("aprovado") is not True or not isinstance(aptidao.get("unidade"), int) or aptidao["unidade"] <= 0:
        registrar("Aptidão", False, detalhe + "; o modelo não foi aprovado no teste de aptidão")
        return False
    registrar("Aptidão", True, detalhe)
    unidade = aptidao["unidade"]

    # Arquivos da execução
    if not pasta.is_dir():
        print(f"A pasta {pasta} não existe.")
        return False
    registros, problema_log = ler_log(pasta)
    if problema_log:
        print(f"Log da execução inválido: {problema_log}.")
        return False
    if not (pasta / "saida.jsonl").exists():
        print(f"{pasta / 'saida.jsonl'} não encontrado.")
        return False

    acoes = list(yaml.safe_load(ARQ_ACOES.read_text(encoding="utf-8")))
    tickets = ler_jsonl(Path(args.tickets))
    ids = [t["id"] for t in tickets]
    gabarito = {g["id"]: g for g in ler_jsonl(Path(args.gabarito))}
    manual = Path(args.manual).read_text(encoding="utf-8")
    conteudos = [conteudo_da_chamada(r) for r in registros]
    palheiro = "\x00".join(conteudos)

    # 2. Modelo
    divergentes = [
        f"chamada {r.get('n', i)} ({r.get('provider')} / {r.get('model')})"
        for i, r in enumerate(registros, start=1)
        if r.get("provider") != aptidao.get("provider") or r.get("model") != aptidao.get("model")
    ]
    registrar("Modelo", not divergentes,
              f"{len(divergentes)} chamadas diferentes da aptidão ({aptidao.get('provider')} / {aptidao.get('model')}): "
              + listar(divergentes) if divergentes else "")

    # 3. Integridade
    previsoes, problemas = ler_saida(pasta, ids, acoes)
    registrar("Integridade", not problemas, "; ".join(problemas))

    # 4. Rastreabilidade
    ausentes = [t["id"] for t in tickets if not aparece(t["texto"], palheiro)]
    registrar("Rastreabilidade", not ausentes,
              f"{len(ausentes)} tickets sem o texto integral em nenhuma chamada: " + listar(ausentes) if ausentes else "")

    # 5. Ondas: onda = posição do ticket no arquivo (a partir de 0) dividida por TAMANHO_ONDA
    onda_de = {t["id"]: pos // TAMANHO_ONDA for pos, t in enumerate(tickets)}
    infratoras = []
    for registro, conteudo in zip(registros, conteudos):
        presentes = sorted({onda_de[t["id"]] + 1 for t in tickets if aparece(t["texto"], conteudo)})
        if len(presentes) > 1:
            infratoras.append(f"chamada {registro.get('n')} mistura as ondas {', '.join(map(str, presentes))}")
    registrar("Ondas", not infratoras, "; ".join(infratoras[:MAX_LISTADOS])
              + (f" e mais {len(infratoras) - MAX_LISTADOS}" if len(infratoras) > MAX_LISTADOS else ""))

    # 6. Manual lido
    caps = capitulos(manual)
    faltando = [titulo for titulo, corpo in caps if corpo and not aparece(corpo, palheiro)]
    if not caps:
        registrar("Manual lido", False, f"nenhum capítulo encontrado em {args.manual}")
    else:
        registrar("Manual lido", not faltando,
                  f"{len(faltando)} de {len(caps)} capítulos ausentes do log: " + listar(faltando) if faltando else "")

    # 7. Custo
    tokens = sum(int(r["input_tokens"]) + int(r["output_tokens"]) for r in registros)
    manuais = tokens / unidade
    maximo = ORCAMENTO_MANUAIS * len(tickets) / 200
    registrar("Custo", manuais <= maximo, f"{manuais:.2f} manuais; máximo {maximo:.2f}")

    # 8. F1 macro
    tabela, f1_macro, acuracia = metricas(previsoes, gabarito)
    registrar("F1 macro", f1_macro >= F1_MINIMO, f"{f1_macro:.3f}; mínimo {F1_MINIMO:.2f}")
    print(f"{'Acurácia '.ljust(21, '.')} {acuracia:.3f} (informativo)")
    print(f"{'Chamadas '.ljust(21, '.')} {len(registros)}; {tokens} tokens de entrada e saída (informativo)")

    print()
    print(f"{'Ação':<27} {'P':>6} {'R':>6} {'F1':>6} {'Suporte':>8}")
    for acao, (p, r, f1, suporte) in tabela.items():
        print(f"{acao:<27} {p:>6.2f} {r:>6.2f} {f1:>6.2f} {suporte:>8}")

    # 9. Diagnóstico
    if all("regra" in g for g in gabarito.values()):
        erros = defaultdict(list)
        for id_, g in gabarito.items():
            if previsoes.get(id_) != g["acao"]:
                erros[(g["regra"], g.get("secao", "?"))].append(id_)
        print()
        print("Erros por regra (diagnóstico)")
        if not erros:
            print("  nenhum erro")
        for (regra, secao), lista in sorted(erros.items(), key=lambda x: (-len(x[1]), x[0])):
            mostrados = ", ".join(lista[:MAX_IDS_POR_REGRA]) + (" ..." if len(lista) > MAX_IDS_POR_REGRA else "")
            print(f"  {regra} (seção {secao}): {len(lista)} erro{'s' if len(lista) > 1 else ''} - {mostrados}")

    print()
    if falhas:
        print("Falharam: " + ", ".join(falhas))
    return not falhas


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Verificador do desafio O manual não cabe.")
    parser.add_argument("pasta", help="pasta da execução (com log.jsonl e saida.jsonl)")
    parser.add_argument("--manual", default="data/manual.md")
    parser.add_argument("--tickets", default="data/dev/tickets.jsonl")
    parser.add_argument("--gabarito", default="data/dev/gabarito.jsonl")
    parser.add_argument("--aptidao", default="runs/aptidao")
    args = parser.parse_args(argv)
    for nome in ("manual", "tickets", "gabarito"):
        if not Path(getattr(args, nome)).exists():
            print(f"Arquivo não encontrado: {getattr(args, nome)}")
            print("STATUS: REPROVADO")
            return 1
    aprovado = verificar(args)
    print(f"STATUS: {'APROVADO' if aprovado else 'REPROVADO'}")
    return 0 if aprovado else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
