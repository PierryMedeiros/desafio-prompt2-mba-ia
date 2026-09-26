"""Cliente único de acesso ao modelo de linguagem.

NÃO ALTERE ESTE ARQUIVO. Ele faz parte da régua do desafio: o checker confia no
log que ele grava para contar chamadas e tokens.

Toda chamada ao modelo feita pelo seu pipeline precisa passar por um ClienteLLM.
Cada chamada concluída vira uma linha em <pasta_execucao>/log.jsonl, com as
mensagens enviadas, a resposta bruta e os tokens de entrada e de saída
informados pela própria API do provedor.

Uso:

    from harness.llm import ClienteLLM

    llm = ClienteLLM("runs/run-1")
    resposta = llm.chamar(
        [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
        ],
        max_tokens=None,
    )

Configuração lida do .env (veja .env.example): LLM_PROVIDER, LLM_MODEL,
OPENAI_API_KEY ou GOOGLE_API_KEY e, opcionalmente, LLM_RPM. O cliente não
envia temperatura: cada modelo usa o seu padrão.

O cliente é thread-safe: você pode fazer chamadas em paralelo a partir de
várias threads usando a mesma instância.
"""

from __future__ import annotations

import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

PROVEDORES = ("openai", "google")
PAPEIS = {"system": SystemMessage, "user": HumanMessage, "assistant": AIMessage}

MAX_TENTATIVAS = 6
ESPERA_INICIAL_S = 2.0
TIMEOUT_S = 300


class ErroLLM(Exception):
    """Falha definitiva ao chamar o modelo (retentativas esgotadas ou resposta sem uso de tokens)."""


class ClienteLLM:
    """Porta única de acesso ao modelo, com registro de cada chamada em log.jsonl."""

    def __init__(self, pasta_execucao: str | Path):
        self.pasta = Path(pasta_execucao)
        self.pasta.mkdir(parents=True, exist_ok=True)
        self.caminho_log = self.pasta / "log.jsonl"
        if self.caminho_log.exists():
            raise FileExistsError(
                f"A pasta {self.pasta} já tem um log.jsonl. "
                "Use uma pasta nova para cada execução."
            )

        load_dotenv()
        self.provider = os.getenv("LLM_PROVIDER", "").strip().lower()
        self.model = os.getenv("LLM_MODEL", "").strip()

        if self.provider not in PROVEDORES:
            raise ValueError(
                "LLM_PROVIDER inválido ou vazio no .env. "
                'Preencha LLM_PROVIDER com "openai" ou "google".'
            )
        if not self.model:
            raise ValueError(
                "LLM_MODEL vazio no .env. Preencha LLM_MODEL com o nome de um modelo "
                "do provedor escolhido (consulte a documentação oficial do provedor)."
            )

        variavel_chave = "OPENAI_API_KEY" if self.provider == "openai" else "GOOGLE_API_KEY"
        chave = os.getenv(variavel_chave, "").strip()
        if not chave:
            raise ValueError(
                f'LLM_PROVIDER é "{self.provider}", mas {variavel_chave} está vazia no .env. '
                f"Preencha {variavel_chave} com a sua chave de API."
            )

        rpm_bruto = os.getenv("LLM_RPM", "").strip()
        try:
            self.rpm = float(rpm_bruto) if rpm_bruto else 0.0
        except ValueError:
            raise ValueError(
                f'LLM_RPM inválido no .env ("{rpm_bruto}"). Preencha com um número '
                "de requisições por minuto, ou deixe vazio para não limitar."
            ) from None
        if self.rpm < 0:
            raise ValueError("LLM_RPM não pode ser negativo. Deixe vazio (ou 0) para não limitar.")
        self._intervalo = 60.0 / self.rpm if self.rpm > 0 else 0.0

        # As retentativas são feitas por este cliente, não pelo SDK do provedor,
        # para que nenhuma tentativa aconteça fora do controle do throttle.
        # Nenhuma temperatura é enviada: cada modelo usa o seu padrão (vários modelos
        # recentes não aceitam temperatura diferente da padrão).
        if self.provider == "openai":
            from langchain_openai import ChatOpenAI

            self._modelo = ChatOpenAI(
                model=self.model,
                api_key=chave,
                max_retries=0,
                timeout=TIMEOUT_S,
            )
        else:
            from langchain_google_genai import ChatGoogleGenerativeAI

            self._modelo = ChatGoogleGenerativeAI(
                model=self.model,
                google_api_key=chave,
                max_retries=0,
                timeout=TIMEOUT_S,
            )

        self._trava_log = threading.Lock()
        self._trava_ritmo = threading.Lock()
        self._proximo_inicio = 0.0
        self._n = 0

    def chamar(self, mensagens: list[dict], max_tokens: int | None = None) -> str:
        """Envia as mensagens ao modelo, registra a chamada no log e devolve o texto da resposta.

        mensagens: lista de dicts {"role": "system" | "user" | "assistant", "content": str},
            com pelo menos uma mensagem "user".
        max_tokens: limite de tokens de saída desta chamada (None usa o padrão do provedor).
        """
        lc_mensagens = self._validar(mensagens, max_tokens)

        if max_tokens is None:
            extras = {}
        elif self.provider == "openai":
            # O langchain-openai converte para max_completion_tokens (Chat Completions)
            # ou max_output_tokens (Responses API), conforme o modelo.
            extras = {"max_tokens": max_tokens}
        else:
            extras = {"max_output_tokens": max_tokens}

        ultimo_erro: Exception | None = None
        for tentativa in range(1, MAX_TENTATIVAS + 1):
            self._aguardar_vez()
            inicio = time.monotonic()
            carimbo = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            try:
                resposta = self._modelo.invoke(lc_mensagens, **extras)
            except Exception as erro:  # noqa: BLE001
                if not _e_retentavel(erro):
                    raise ErroLLM(f"Falha ao chamar o modelo: {erro!r}") from erro
                ultimo_erro = erro
                if tentativa < MAX_TENTATIVAS:
                    time.sleep(ESPERA_INICIAL_S * 2 ** (tentativa - 1))
                continue
            duracao_ms = int((time.monotonic() - inicio) * 1000)
            break
        else:
            raise ErroLLM(
                f"O modelo falhou em {MAX_TENTATIVAS} tentativas seguidas. "
                f"Último erro: {ultimo_erro!r}"
            ) from ultimo_erro

        uso = getattr(resposta, "usage_metadata", None)
        if not uso or uso.get("input_tokens") is None or uso.get("output_tokens") is None:
            raise ErroLLM(
                "O provedor não informou o uso de tokens desta chamada; "
                "não é possível registrá-la."
            )
        detalhes = uso.get("input_token_details") or {}
        cache_read = detalhes.get("cache_read") or 0
        texto = str(resposta.text)

        registro = {
            "n": None,
            "timestamp": carimbo,
            "provider": self.provider,
            "model": self.model,
            "max_tokens": max_tokens,
            "mensagens": [{"role": m["role"], "content": m["content"]} for m in mensagens],
            "resposta": texto,
            "input_tokens": int(uso["input_tokens"]),
            "output_tokens": int(uso["output_tokens"]),
            "cache_read_tokens": int(cache_read),
            "duracao_ms": duracao_ms,
        }
        with self._trava_log:
            self._n += 1
            registro["n"] = self._n
            with open(self.caminho_log, "a", encoding="utf-8") as arquivo:
                arquivo.write(json.dumps(registro, ensure_ascii=False) + "\n")
                arquivo.flush()
        return texto

    def _validar(self, mensagens, max_tokens):
        if not isinstance(mensagens, list) or not mensagens:
            raise ValueError("mensagens deve ser uma lista não vazia de dicts com 'role' e 'content'.")
        convertidas = []
        tem_user = False
        for i, m in enumerate(mensagens):
            if not isinstance(m, dict) or "role" not in m or "content" not in m:
                raise ValueError(f"mensagens[{i}] deve ser um dict com as chaves 'role' e 'content'.")
            papel, conteudo = m["role"], m["content"]
            if papel not in PAPEIS:
                raise ValueError(
                    f"mensagens[{i}] tem role inválido ({papel!r}). "
                    "Use 'system', 'user' ou 'assistant'."
                )
            if not isinstance(conteudo, str):
                raise ValueError(f"mensagens[{i}]['content'] deve ser uma string.")
            tem_user = tem_user or papel == "user"
            convertidas.append(PAPEIS[papel](content=conteudo))
        if not tem_user:
            raise ValueError("mensagens precisa ter pelo menos uma mensagem com role 'user'.")
        if max_tokens is not None and (
            isinstance(max_tokens, bool) or not isinstance(max_tokens, int) or max_tokens <= 0
        ):
            raise ValueError("max_tokens deve ser None ou um inteiro positivo.")
        return convertidas

    def _aguardar_vez(self):
        """Garante o intervalo mínimo entre o início de chamadas consecutivas (LLM_RPM)."""
        if not self._intervalo:
            return
        with self._trava_ritmo:
            agora = time.monotonic()
            inicio = max(agora, self._proximo_inicio)
            self._proximo_inicio = inicio + self._intervalo
        espera = inicio - time.monotonic()
        if espera > 0:
            time.sleep(espera)


def _e_retentavel(erro: BaseException) -> bool:
    """Rate limit, erro 5xx, timeout ou falha de conexão, olhando a cadeia de exceções."""
    atual: BaseException | None = erro
    vistos = set()
    while atual is not None and id(atual) not in vistos:
        vistos.add(id(atual))
        if getattr(type(atual), "is_retryable", False):
            return True
        nome = type(atual).__name__
        if nome in (
            "RateLimitError",
            "APITimeoutError",
            "APIConnectionError",
            "InternalServerError",
            "ServerError",
            "TimeoutError",
            "ReadTimeout",
            "ConnectTimeout",
            "ConnectError",
        ):
            return True
        for atributo in ("status_code", "code", "status"):
            valor = getattr(atual, atributo, None)
            if isinstance(valor, int) and (valor == 429 or 500 <= valor < 600):
                return True
        atual = atual.__cause__ or atual.__context__
    return False
