# Diário do teste (aluno simulado)

Início: 28/09/2026 15:19 (horário local, -03). Horários das etapas conferidos pelos timestamps dos `log.jsonl` (UTC-3).

## Etapa 0: leitura do enunciado e do repositório (15:19 a 15:20 lendo README/harness; leitura dos capítulos de regra em paralelo às aptidões)

- Li README, `harness/*.py`, `baseline/manual_inteiro.py`, `.env.example`, `data/acoes.yaml` e os capítulos 13 a 22 do manual (os de regra). Os capítulos 1 a 12 só folheei pelos títulos (cultura, história, tom de voz, macros gerais, FAQ do time).
- Branch `solucao-aluno-teste` criada a partir da `main`.
- O `.env` já veio preenchido com `LLM_PROVIDER=google`, `LLM_MODEL=gemini-3.5-flash-lite`, `LLM_RPM=12`.

### Dúvidas do enunciado

1. **"Repositório base e ambiente: https://github.com/devfullcycle/REPO-A-DEFINIR"**. O link do repositório base é um placeholder. Decisão: trabalho no clone que já tenho (origin = fork do usuário). Anotado como problema do enunciado: o aluno real não saberia de onde fazer fork.
2. **"Entregar, em um fork público do repositório base ... com tudo na branch `main`"** vs. a instrução do teste de trabalhar na branch `solucao-aluno-teste`. Decisão: sigo a instrução do teste (branch separada); para um aluno real, a entrega seria na main.
3. **Setup do README usa `venv/`**, mas o repositório já tem `.venv/` (o `.gitignore` cobre os dois). Decisão: uso o `.venv` que já existe.
4. **"Escolha o modelo como o README orienta"**: o README não recomenda um modelo, só diz que "qualquer um que passe no teste de aptidão serve", que modelos pequenos custam centavos e que tokens de raciocínio contam. O `.env` já vem com `gemini-3.5-flash-lite`. Decisão: começo com ele (pequeno, barato, contexto grande) e só troco se reprovar na aptidão ou se os tokens de raciocínio estourarem o orçamento. Dúvida que fica: o README não diz como saber se um modelo é "de raciocínio" nem como desligar o raciocínio, e o `ClienteLLM` não expõe nenhum parâmetro para isso (só `max_tokens`).
5. **"calcular fatos neutros a partir dos metadados (ex.: dias entre duas datas)"**: não fica claro se datas citadas no *texto* do ticket (ex.: data de emissão da nota, data da recusa de retenção) também contam como "metadados". A data de emissão da nota fiscal, por exemplo, só existe no texto. Decisão: calculo dias entre `data_abertura` e cada data que aparece no texto também (é uma conta neutra, não compara com nenhum limite), e deixo o modelo decidir qual data é a referência.
6. **Contagem de meses de casa**: o manual define uma regra de calendário (dia inexistente vira dia 1 do mês seguinte). Calcular "meses completos" no código seria copiar regra do manual? Decisão: calculo meses completos pelo método de calendário padrão (diferença de meses, menos 1 se o dia de abertura for menor que o dia de `cliente_desde`), que é conta neutra e por acaso coincide com a regra do manual; anoto no README como fato neutro.
7. **Custo**: 7 manuais para 200 tickets e 20 ondas, e o manual precisa ir inteiro pelo menos uma vez (1 manual). Sobram ~6 manuais para 20 ondas + saída da preparação: cada onda pode gastar ~0,28 manual. É uma conta que o README não faz para o aluno, mas dá para deduzir.

## Etapa 1: aptidão e escolha do modelo (15:20 a 15:30, ~10 min)

| Modelo | Unidade (tokens) | Acurácia | Resultado | Observação |
|---|---|---|---|---|
| google / gemini-3.5-flash-lite (o que veio no `.env`) | 45.477 | 20/30 = 0,67 | REPROVADO | ~92 tokens de saída por onda: não "pensou" |
| openai / gpt-4.1-mini | 42.776 | 18/30 = 0,60 | REPROVADO | não é de raciocínio; 9 s no total |

- Trava: `python -c "load_dotenv()"` via stdin quebra (`AssertionError` em `find_dotenv`); resolvi passando o caminho `load_dotenv('.env')` num script. Não afeta o harness, só o meu script de listar modelos.
- Trava: o `ClienteLLM` recusa pasta com log. Para testar vários modelos gerei a aptidão em pastas `runs/apt-<modelo>` (`--saida`) e renomeio a escolhida para `runs/aptidao` no fim. O README não diz se pode rodar a aptidão mais de uma vez nem o que fazer com a pasta de uma aptidão reprovada; decidi que pode (é o que um aluno faria ao trocar de modelo).
- Descoberta útil: como o `load_dotenv` não sobrescreve variáveis já existentes, dá para testar modelos em paralelo com `LLM_PROVIDER=... LLM_MODEL=... python -m harness.aptidao --saida ...` sem editar o `.env`.
- Observação: o README diz que com o manual inteiro "o acerto é praticamente total", mas dois modelos pequenos não-raciocínio ficaram em 60-67%. Para o aluno, a frase "Com modelos pequenos, o desafio inteiro custa centavos" sugere que um modelo pequeno qualquer serve; na prática só modelos de raciocínio parecem passar, e aí os tokens de raciocínio pesam no orçamento de 7 manuais.
| openai / gpt-5.4-mini | 42.775 | 21/30 = 0,70 | REPROVADO | ~75 tokens de saída por onda: raciocínio padrão desligado |
| google / gemini-3.5-flash | — | — | não rodou | `503 UNAVAILABLE ... high demand` nas 6 tentativas do cliente, já na chamada da unidade |
| **openai / gpt-5-mini** | **42.775** | **30/30 = 1,00** | **APROVADO** | ~2.200 tokens de saída (raciocínio) por onda de 10 |

- Decisão: gpt-5-mini. Troquei o `.env` para `LLM_PROVIDER=openai`, `LLM_MODEL=gpt-5-mini`, `LLM_RPM=` vazio (OpenAI não reclamou de limite). Renomeei `runs/apt-gpt-5-mini` para `runs/aptidao`. As pastas das aptidões reprovadas ficam fora do commit.
- Conta de custo com o raciocínio: ~2,2 mil tokens de saída por onda × 20 ondas ≈ 1 manual só de "pensamento". Sobra pouco para o contexto de cada onda.
- Dúvida: o README diz "Com modelos pequenos, o desafio inteiro custa centavos". Com o manual inteiro, os três modelos pequenos sem raciocínio reprovaram; o que passou é de raciocínio. O aluno descobre isso gastando aptidões.
- Tempo da etapa 1: ~10 min pelos timestamps dos logs (a espera do 503 do Gemini esgotar as 6 retentativas correu em paralelo).

## Etapa 2: pipeline e experimentos (15:30 a 16:03, ~33 min)

- Código em `pipeline/triagem.py` e `pipeline/prompts.py`, rodado com `python -m pipeline.triagem`.
- Arquitetura v1: 1 chamada de preparação (system = pedido de extração; user = manual integral) + 1 chamada por onda (system = caderno de regras; user = JSON dos 10 tickets com `fatos` de calendário) + 1 reenvio só dos tickets faltantes da onda + padrão fixo `suporte_padrao`.
- Reaproveitei `interpretar`, `ler_acoes`, `ler_tickets` e `ondas` do baseline (importar não é alterar). Dúvida: o README não diz se pode importar do `baseline/`; como o próprio `harness/aptidao.py` importa, assumi que pode.
- A flag `--preparo generico` existe só para gerar a linha "resumo genérico" da tabela exigida.

### Configurações testadas (todas gpt-5-mini, 200 tickets de dev)

| # | Pasta | O que mudou | F1 macro | Custo (manuais) | US$ aprox. | Status |
|---|---|---|---|---|---|---|
| 1 | exp-01-resumo | resumo genérico, saída `<id> <ação>` | 0,928 | 4,69 | 0,135 | reprovado (F1) |
| 2 | exp-02-extracao | extração estruturada v1 | 0,992 | 7,55 | 0,171 | reprovado (custo) |
| 3 | exp-03-extracao-enxuta | v1 + "cada regra uma vez, sem recapitulação, sem procedimentos"; JSON sem indent | 0,970 | 5,41 | 0,143 | aprovado |
| 4a | exp-04a-justificativa | v3 + saída `<id> \| área \| passo \| ação` | 0,997 | 6,39 | 0,187 | aprovado |
| 4b | exp-04b-justificativa | igual à 4a (medir variância) | 0,983 | 5,90 | 0,180 | aprovado |
| 5 | exp-05-area-teto | v3 + saída `<id> \| área \| ação` + teto de 2.500 palavras | 0,964 | 5,30 | 0,154 | aprovado, mas perdeu exceção |
| 6 | **dev (final)** | v3 + saída curta + "exceção antes da regra geral", sem teto | **0,980** | **5,62** | 0,161 | **aprovado** |
| — | exp-06-manual-alterado | final, manual com entrada nova no histórico, 30 tickets | 0,931 vs gabarito original | 1,88 (máx. 1,05) | 0,049 | ver abaixo |

- Variância: a mesma configuração (4a/4b) variou 0,983–0,997 de F1 e 5,90–6,39 de custo. O tamanho do caderno gerado varia ~25% entre execuções (17,8k a 22,1k caracteres). O README não fala dessa variância e ela importa: o avaliador roda uma vez (com uma segunda chance), então é preciso margem nos dois critérios.
- Custo em dólares: estimado com os preços públicos por 1M tokens (gpt-5-mini US$ 0,25 entrada / 2,00 saída; os preços de gpt-5.4-mini e gemini-3.5-* são estimativas minhas). **Total gasto ~US$ 1,46**, dentro do teto de US$ 2.

### Teste do manual alterado (dica final do README)

- Acrescentei ao histórico de uma cópia do manual: teto de aprovação automática do Essencial de R$ 200 para R$ 50 para chamados abertos a partir de 01/03/2026. Esperado: D011, D025, D167 → `reembolso_com_analise`.
- Resultado: o caderno incorporou a alteração dentro do passo do teto com a condição de data; D025 e D167 mudaram corretamente, nenhum outro mudou. D011 não mudou porque já estava errado no dev (o modelo inventa um cancelamento).
- **Trava**: para economizar rodei só 3 ondas (30 tickets). O checker reprova em custo porque o orçamento escala linearmente com o nº de tickets (7 × 30/200 = 1,05) e a preparação custa ~1 manual fixo. O README não avisa isso; o aluno que seguir a dica com um subconjunto vai ver "REPROVADO" e pode achar que quebrou algo. Também não há gabarito para o manual alterado: o aluno precisa calcular à mão o que deveria mudar.

### Requisitos/critérios que pareceram contraditórios, impossíveis ou inverificáveis

1. **"nenhuma regra, limite, tabela ou número de seção copiado para o código ou para os prompts"** vs. **"calcular fatos neutros ... (ex.: dias entre duas datas)"**: a regra de contagem de dias/meses é do manual (13.5, 13.6). Se o código calcula "meses completos", está implementando uma convenção do manual? Decidi que conta de calendário padrão é neutra, mas o critério é interpretativo e o aluno não tem como verificar antes da correção.
2. **"Nenhum conteúdo derivado do manual ... nos prompts"**: é inverificável para o aluno onde fica a fronteira entre "dizer como ler" e "dizer quais são as regras". Ex.: escrever no prompt "as exceções costumam estar em FAQ e em notas de macro" é derivado do manual? Eu considerei que não (é descrição da estrutura, não de regra), mas um avaliador rigoroso pode discordar.
3. **"Com modelos pequenos, o desafio inteiro custa centavos"** + **"o acerto é praticamente total"** com o manual inteiro: três modelos pequenos reprovaram na aptidão (60-70%). Só passou um modelo de raciocínio. A frase induz o aluno a escolher o modelo errado primeiro.
4. **Critério "Em um clone limpo ... gera uma execução que o checker aprova"**: inverificável pelo aluno (não há manual atualizado nem tickets ocultos). O único proxy é a dica de mudar uma regra, que esbarra na trava de custo do subconjunto acima.
5. **Entregável "fork público ... tudo na branch main"** vs. link do repositório base `REPO-A-DEFINIR`: impossível fazer fork de um placeholder.
6. **"Versione runs/aptidao"**: o checker lê `runs/aptidao` por padrão, mas o README não diz o que fazer com aptidões reprovadas de modelos anteriores (manter? apagar?). Mantive em `runs/apt-*` como evidência.

## Etapa 3: README e entrega (16:03 a ~16:15, ~12 min)

- README substituído pela documentação da solução (modelo, comando, tabela com 7 linhas incluindo o resumo genérico, prompt final transcrito, justificativas, teste do manual alterado, limitações do harness).
- `data/`, `harness/`, `baseline/`: `git diff` vazio.
- Grep por valores do manual (R$, "14 dias", números de seção) em `pipeline/`: nada.
- Resultado final do checker em `runs/dev`: **STATUS: APROVADO**, exit 0, F1 0,980, custo 5,62 manuais.

**Tempo total: ~55 min** (15:19 a ~16:15). Tempo de parede dominado por esperar execuções (~3 min cada, 9 execuções completas).
