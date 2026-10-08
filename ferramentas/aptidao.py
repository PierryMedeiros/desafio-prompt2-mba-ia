"""Teste de aptidão do modelo e medida da unidade de custo ("1 manual").

NÃO ALTERE ESTE ARQUIVO.

Uso (a partir da raiz do repositório):

    python -m ferramentas.aptidao [--saida runs/aptidao]

Faz quatro chamadas com o provedor e o modelo do .env:

1. Unidade: uma chamada que envia só o manual. Os tokens de entrada dela são
   a unidade de custo do desafio (1 manual) para o seu modelo.
2. Classificação: as 3 ondas dos 30 tickets de aptidão, com o manual inteiro
   em cada chamada (a mesma classificação do baseline, sem repetição).

O modelo é aprovado se acertar pelo menos APTIDAO_MINIMA dos 30 tickets.
Ticket faltante ou ação fora de data/acoes.yaml conta como erro. Grava
saida.jsonl e resultado.json na pasta de saída. Exit code 0 se aprovado.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from baseline.manual_inteiro import classificar_onda, ler_acoes, ler_tickets, ondas
from ferramentas.config import APTIDAO_MINIMA
from ferramentas.llm import ClienteLLM

RAIZ = Path(__file__).resolve().parent.parent
ARQ_MANUAL = RAIZ / "data" / "manual.md"
ARQ_TICKETS = RAIZ / "data" / "aptidao" / "tickets.jsonl"
ARQ_GABARITO = RAIZ / "data" / "aptidao" / "gabarito.jsonl"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Teste de aptidão do modelo e medida da unidade de custo.")
    parser.add_argument("--saida", default="runs/aptidao", help="pasta nova da execução (padrão: runs/aptidao)")
    args = parser.parse_args(argv)

    manual = ARQ_MANUAL.read_text(encoding="utf-8")
    acoes = ler_acoes()
    tickets = ler_tickets(ARQ_TICKETS)
    gabarito = {g["id"]: g["acao"] for g in ler_tickets(ARQ_GABARITO)}
    llm = ClienteLLM(args.saida)
    pasta = Path(args.saida)

    print("Medindo a unidade (uma chamada só com o manual)...", flush=True)
    llm.chamar([
        {"role": "system", "content": "Você receberá um documento. Responda apenas OK."},
        {"role": "user", "content": manual},
    ])
    with open(llm.caminho_log, encoding="utf-8") as arquivo:
        unidade = int(json.loads(arquivo.readline())["input_tokens"])

    previsoes: dict[str, str | None] = {}
    for numero, onda in enumerate(ondas(tickets), start=1):
        print(f"Classificando a onda {numero}...", flush=True)
        obtidos = classificar_onda(llm, manual, acoes, onda, repetir=False)
        for ticket in onda:
            previsoes[ticket["id"]] = obtidos.get(ticket["id"])

    with open(pasta / "saida.jsonl", "w", encoding="utf-8") as arquivo:
        for ticket in tickets:
            arquivo.write(json.dumps({"id": ticket["id"], "acao": previsoes[ticket["id"]]}, ensure_ascii=False) + "\n")

    acertos = sum(1 for id_, acao in gabarito.items() if previsoes.get(id_) == acao)
    acuracia = acertos / len(gabarito)
    aprovado = acuracia >= APTIDAO_MINIMA
    resultado = {
        "provider": llm.provider,
        "model": llm.model,
        "unidade": unidade,
        "acuracia": round(acuracia, 4),
        "minimo": APTIDAO_MINIMA,
        "aprovado": aprovado,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(pasta / "resultado.json", "w", encoding="utf-8") as arquivo:
        json.dump(resultado, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")

    faltantes = [id_ for id_, acao in previsoes.items() if acao is None]
    print()
    print(f"Modelo .............. {llm.provider} / {llm.model}")
    print(f"Unidade ............. {unidade} tokens de entrada = 1 manual")
    print(f"Acurácia ............ {acertos}/{len(gabarito)} = {acuracia:.2f} (mínimo {APTIDAO_MINIMA:.2f})")
    if faltantes:
        print(f"Sem resposta válida . {', '.join(faltantes)}")
    print(f"STATUS: {'APROVADO' if aprovado else 'REPROVADO'}")
    return 0 if aprovado else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
