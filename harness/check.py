"""Checker do desafio "Triagem em lote".

NÃO ALTERE ESTE ARQUIVO.

Uso (a partir da raiz do repositório):

    python -m harness.check                       # baseline + runs/run-1, runs/run-2, runs/run-3
    python -m harness.check runs/x [runs/y ...]   # baseline + as pastas indicadas

Primeiro valida runs/baseline como referência. Depois verifica cada pasta de
execução: integridade da saida.jsonl, rastreabilidade dos tickets no log.jsonl,
provedor e modelo, número de chamadas, F1 macro e tokens em relação à referência.
Termina com exit code 0 somente se a referência for válida e todas as pastas
verificadas forem aprovadas.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

# CALIBRAR: valores definidos pela calibração com a solução de referência.
F1_MINIMO = 0.00
# CALIBRAR: fração dos tokens da referência (0.10 = 10%).
RAZAO_TOKENS_MAXIMA = 0.00
# CALIBRAR: número máximo de chamadas ao modelo por execução, contando reenvios.
MAX_CHAMADAS = 0

RAIZ = Path(__file__).resolve().parent.parent
ARQ_TICKETS = RAIZ / "data" / "tickets.jsonl"
ARQ_GABARITO = RAIZ / "data" / "gabarito.jsonl"
ARQ_CATEGORIAS = RAIZ / "data" / "categorias.yaml"
PASTA_REFERENCIA = Path("runs/baseline")
PASTAS_PADRAO = ["runs/run-1", "runs/run-2", "runs/run-3"]
MAX_LISTADOS = 10

COMO_GERAR_BASELINE = (
    "Gere a referência numa pasta limpa (apague ou renomeie runs/baseline antes):\n"
    "    python -m baseline.classificar_um_a_um --saida runs/baseline"
)


def ler_jsonl_simples(caminho: Path) -> list[dict]:
    with open(caminho, encoding="utf-8") as arquivo:
        return [json.loads(linha) for linha in arquivo if linha.strip()]


def listar(itens: list[str]) -> str:
    mostrados = ", ".join(itens[:MAX_LISTADOS])
    resto = len(itens) - MAX_LISTADOS
    return f"{mostrados} e mais {resto}" if resto > 0 else mostrados


def pct(valor: float) -> str:
    return f"{valor * 100:.1f}%"


class Dados:
    def __init__(self):
        self.tickets = ler_jsonl_simples(ARQ_TICKETS)
        self.ids = [t["id"] for t in self.tickets]
        self.gabarito = {g["id"]: g["categoria"] for g in ler_jsonl_simples(ARQ_GABARITO)}
        with open(ARQ_CATEGORIAS, encoding="utf-8") as arquivo:
            config = yaml.safe_load(arquivo)
        self.categorias = [c["nome"] for c in config["categorias"]]


# ---------------------------------------------------------------- leitura


def ler_saida(pasta: Path, dados: Dados):
    """Devolve (previsoes, problemas). previsoes: id -> categoria (primeira ocorrência válida)."""
    caminho = pasta / "saida.jsonl"
    if not caminho.exists():
        return {}, ["saida.jsonl não encontrado"]

    problemas = []
    linhas_invalidas = []
    previsoes: dict[str, str] = {}
    contagem: dict[str, int] = {}
    categorias_invalidas = []
    ids_validos = set(dados.ids)
    extras = []

    with open(caminho, encoding="utf-8") as arquivo:
        for numero, linha in enumerate(arquivo, start=1):
            if not linha.strip():
                continue
            try:
                registro = json.loads(linha)
            except json.JSONDecodeError:
                linhas_invalidas.append(str(numero))
                continue
            if not isinstance(registro, dict) or "id" not in registro or "categoria" not in registro:
                linhas_invalidas.append(str(numero))
                continue
            id_ = str(registro["id"])
            categoria = registro["categoria"]
            contagem[id_] = contagem.get(id_, 0) + 1
            if id_ not in ids_validos:
                if contagem[id_] == 1:
                    extras.append(id_)
                continue
            if categoria not in dados.categorias:
                categorias_invalidas.append(f"{id_} ({categoria!r})")
                continue
            previsoes.setdefault(id_, categoria)

    if linhas_invalidas:
        problemas.append(
            "linhas que não são JSON com 'id' e 'categoria': " + listar(linhas_invalidas)
        )
    faltantes = [i for i in dados.ids if i not in contagem]
    duplicados = [i for i, n in contagem.items() if n > 1]
    if faltantes:
        problemas.append(f"{len(faltantes)} IDs faltantes: " + listar(faltantes))
    if duplicados:
        problemas.append(f"{len(duplicados)} IDs duplicados: " + listar(duplicados))
    if extras:
        problemas.append(f"{len(extras)} IDs que não existem em data/tickets.jsonl: " + listar(extras))
    if categorias_invalidas:
        problemas.append(
            f"{len(categorias_invalidas)} categorias fora do YAML: " + listar(categorias_invalidas)
        )
    return previsoes, problemas


def ler_log(pasta: Path):
    """Devolve (registros, problema). problema é None quando o log é legível."""
    caminho = pasta / "log.jsonl"
    if not caminho.exists():
        return [], "log.jsonl não encontrado"
    registros = []
    ruins = []
    with open(caminho, encoding="utf-8") as arquivo:
        for numero, linha in enumerate(arquivo, start=1):
            if not linha.strip():
                continue
            try:
                registro = json.loads(linha)
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
    return registros, None


# ---------------------------------------------------------------- verificações


def verificar_rastreabilidade(registros: list[dict], dados: Dados) -> list[str]:
    """Devolve os IDs cujo texto não aparece em nenhuma mensagem do log."""
    conteudos = []
    for registro in registros:
        for mensagem in registro.get("mensagens", []):
            if isinstance(mensagem, dict) and isinstance(mensagem.get("content"), str):
                conteudos.append(mensagem["content"])
    palheiro = "\x00".join(conteudos)
    ausentes = []
    for ticket in dados.tickets:
        texto = ticket["texto"]
        formas = (
            texto,
            json.dumps(texto, ensure_ascii=True)[1:-1],
            json.dumps(texto, ensure_ascii=False)[1:-1],
        )
        if not any(forma in palheiro for forma in formas):
            ausentes.append(ticket["id"])
    return ausentes


def calcular_metricas(previsoes: dict[str, str], dados: Dados):
    """Devolve (tabela, f1_macro, acuracia). tabela: categoria -> (P, R, F1, suporte)."""
    tabela = {}
    for categoria in dados.categorias:
        tp = fp = fn = 0
        for id_ in dados.ids:
            real = dados.gabarito[id_]
            previsto = previsoes.get(id_)
            if previsto == categoria and real == categoria:
                tp += 1
            elif previsto == categoria:
                fp += 1
            elif real == categoria:
                fn += 1
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * p * r / (p + r) if p + r else 0.0
        suporte = sum(1 for id_ in dados.ids if dados.gabarito[id_] == categoria)
        tabela[categoria] = (p, r, f1, suporte)
    f1_macro = sum(v[2] for v in tabela.values()) / len(tabela)
    acertos = sum(1 for id_ in dados.ids if previsoes.get(id_) == dados.gabarito[id_])
    return tabela, f1_macro, acertos / len(dados.ids)


def somar_tokens(registros: list[dict]):
    entrada = sum(int(r["input_tokens"]) for r in registros)
    saida = sum(int(r["output_tokens"]) for r in registros)
    return entrada, saida


def item(nome: str, ok: bool, detalhe: str = "") -> str:
    rotulo = f"{nome} ".ljust(21, ".")
    status = "OK" if ok else "FALHOU"
    return f"  {rotulo} {status}" + (f" ({detalhe})" if detalhe else "")


def imprimir_tabela(tabela):
    print()
    print(f"  {'Categoria':<16} {'P':>5}  {'R':>5}  {'F1':>5}  {'Suporte':>7}")
    for categoria, (p, r, f1, suporte) in tabela.items():
        print(f"  {categoria:<16} {p:>5.2f}  {r:>5.2f}  {f1:>5.2f}  {suporte:>7}")


# ---------------------------------------------------------------- referência


def validar_referencia(dados: Dados):
    pasta = RAIZ / PASTA_REFERENCIA
    problemas = []
    if not pasta.is_dir():
        problemas.append(f"a pasta {PASTA_REFERENCIA} não existe")
        return None, problemas

    previsoes, problemas_saida = ler_saida(pasta, dados)
    problemas += [f"integridade: {p}" for p in problemas_saida]

    registros, problema_log = ler_log(pasta)
    if problema_log:
        problemas.append(problema_log)
    elif registros:
        ausentes = verificar_rastreabilidade(registros, dados)
        if ausentes:
            problemas.append(
                f"rastreabilidade: {len(ausentes)} tickets sem o texto no log: " + listar(ausentes)
            )
        if len(registros) < len(dados.ids):
            problemas.append(
                f"o log tem {len(registros)} chamadas; a referência precisa de pelo menos "
                f"{len(dados.ids)} (uma por ticket)"
            )
        pares = {(r.get("provider"), r.get("model")) for r in registros}
        if len(pares) > 1:
            problemas.append("o log mistura provedores ou modelos diferentes")
    else:
        problemas.append("log.jsonl está vazio")

    if problemas:
        return None, problemas

    provider, model = registros[0].get("provider"), registros[0].get("model")
    entrada, saida = somar_tokens(registros)
    _, f1_macro, _ = calcular_metricas(previsoes, dados)
    referencia = {
        "provider": provider,
        "model": model,
        "chamadas": len(registros),
        "tokens": entrada + saida,
        "entrada": entrada,
        "saida": saida,
        "f1": f1_macro,
    }
    return referencia, []


# ---------------------------------------------------------------- execução


def verificar_execucao(nome: str, referencia: dict, dados: Dados) -> bool:
    print()
    print(nome)
    pasta = Path(nome)
    if not pasta.is_dir():
        print("  STATUS: REPROVADO (pasta não encontrada)")
        return False

    falhas = []

    previsoes, problemas_saida = ler_saida(pasta, dados)
    ok = not problemas_saida
    print(item("Integridade", ok, "; ".join(problemas_saida)))
    if not ok:
        falhas.append("Integridade")

    registros, problema_log = ler_log(pasta)

    if problema_log:
        print(item("Rastreabilidade", False, problema_log))
        falhas.append("Rastreabilidade")
    else:
        ausentes = verificar_rastreabilidade(registros, dados)
        detalhe = (
            f"{len(ausentes)} tickets sem o texto integral em nenhuma chamada do log: "
            + listar(ausentes)
            if ausentes
            else ""
        )
        print(item("Rastreabilidade", not ausentes, detalhe))
        if ausentes:
            falhas.append("Rastreabilidade")

    if problema_log:
        print(item("Modelo", False, problema_log))
        falhas.append("Modelo")
    else:
        divergentes = [
            f"chamada {r.get('n', i)} ({r.get('provider')} / {r.get('model')})"
            for i, r in enumerate(registros, start=1)
            if r.get("provider") != referencia["provider"] or r.get("model") != referencia["model"]
        ]
        if not registros:
            print(item("Modelo", False, "log.jsonl vazio"))
            falhas.append("Modelo")
        elif divergentes:
            print(
                item(
                    "Modelo",
                    False,
                    f"{len(divergentes)} chamadas diferentes da referência "
                    f"({referencia['provider']} / {referencia['model']}): " + listar(divergentes),
                )
            )
            falhas.append("Modelo")
        else:
            print(item("Modelo", True))

    chamadas = len(registros)
    ok = not problema_log and chamadas <= MAX_CHAMADAS
    print(item("Chamadas", ok, f"{chamadas}; máximo {MAX_CHAMADAS}"))
    if not ok:
        falhas.append("Chamadas")

    tabela, f1_macro, acuracia = calcular_metricas(previsoes, dados)
    ok = f1_macro >= F1_MINIMO
    print(item("F1 macro", ok, f"{f1_macro:.2f}; mínimo {F1_MINIMO:.2f}"))
    if not ok:
        falhas.append("F1 macro")

    entrada, saida = somar_tokens(registros)
    total = entrada + saida
    razao = total / referencia["tokens"]
    ok = not problema_log and razao <= RAZAO_TOKENS_MAXIMA
    print(
        item(
            "Tokens",
            ok,
            f"{total} = {pct(razao)} da referência; máximo {pct(RAZAO_TOKENS_MAXIMA)}",
        )
    )
    if not ok:
        falhas.append("Tokens")

    cache = sum(int(r.get("cache_read_tokens") or 0) for r in registros)
    duracao = sum(int(r.get("duracao_ms") or 0) for r in registros)
    print(f"  {'Cache (informativo) '.ljust(21, '.')} {cache} tokens de entrada lidos do cache")
    print(f"  {'Tempo (informativo) '.ljust(21, '.')} {duracao / 1000:.1f} s somados nas chamadas")
    print(f"  {'Acurácia (inform.) '.ljust(21, '.')} {acuracia:.2f}")

    imprimir_tabela(tabela)
    if falhas:
        print("  STATUS: REPROVADO (" + ", ".join(falhas) + ")")
        return False
    print("  STATUS: APROVADO")
    return True


def main(argv: list[str]) -> int:
    dados = Dados()

    referencia, problemas = validar_referencia(dados)
    print(f"Referência: {PASTA_REFERENCIA}")
    if referencia is None:
        print("  REFERÊNCIA INVÁLIDA")
        for problema in problemas:
            print(f"  - {problema}")
        print()
        print(COMO_GERAR_BASELINE)
        return 1

    print(f"  Provedor/modelo: {referencia['provider']} / {referencia['model']}")
    print(
        f"  Chamadas: {referencia['chamadas']} | Tokens: {referencia['tokens']} "
        f"(entrada {referencia['entrada']}, saída {referencia['saida']})"
    )
    print(f"  F1 macro: {referencia['f1']:.2f}")

    pastas = argv or PASTAS_PADRAO
    resultados = [verificar_execucao(pasta, referencia, dados) for pasta in pastas]

    print()
    aprovadas = sum(resultados)
    print(f"Resumo: {aprovadas} de {len(resultados)} pastas aprovadas.")
    return 0 if all(resultados) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
