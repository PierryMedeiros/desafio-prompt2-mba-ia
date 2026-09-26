# O manual não cabe

A Orbita é um SaaS de cobrança e emissão de notas fiscais para pequenos negócios. Cada ticket que chega ao suporte passa por um LLM que decide a ação: reembolsar, negar, oferecer retenção, escalar para segurança, orientar o cancelamento de uma nota, encaminhar ao encarregado de dados e mais uma dezena de caminhos. Quem manda nessas decisões é o Manual de Atendimento: cerca de 42 mil tokens com políticas de oito áreas, tabelas por plano, exceções, um histórico de alterações e, como todo manual de empresa, muita cultura, tom de voz e texto que não decide nada.

Hoje os tickets são triados em ondas de 10, e cada onda leva o manual inteiro ao modelo. Funciona: o acerto é praticamente total. Só que cada rodada de 200 tickets custa o equivalente a ler o manual 21 vezes. A nova meta é caber em 7 leituras, sem perder acerto. E tem um detalhe: o jurídico e o financeiro mexem nas políticas toda semana, então nada de resumo feito à mão uma vez e esquecido numa pasta. Quem prepara o contexto é o seu pipeline, a cada execução, com o seu modelo.

Cortar contexto é fácil. Cortar sem perder a regra que decide o ticket 137 é o desafio.

## Objetivo

Entregar, em um fork público do repositório base:

- o teste de aptidão aprovado para o modelo que você escolher, em `runs/aptidao/`;
- um pipeline em Python que lê o manual, prepara o contexto com o próprio modelo e classifica os tickets respeitando as ondas;
- uma execução desse pipeline sobre os 200 tickets de desenvolvimento, em `runs/dev/`, aprovada pelo checker;
- um README com o modelo usado, o comando de execução e o registro das suas decisões, com os números que as sustentam.

## Repositório base e ambiente

https://github.com/devfullcycle/REPO-A-DEFINIR

Você precisa de Python 3.10+ e de uma chave de API da OpenAI (https://platform.openai.com/api-keys) ou do Google Gemini (https://aistudio.google.com/app/apikey). O desafio não fixa modelo: qualquer um que passe no teste de aptidão serve. Com modelos pequenos, o desafio inteiro custa centavos de dólar. Planos gratuitos costumam ter cotas baixas, e cada chamada com o manual inteiro tem dezenas de milhares de tokens: confira os limites do seu antes de escolher.

```
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # preencha provedor, modelo e chave
```

Todos os comandos rodam a partir da raiz do repositório, como módulos (`python -m ...`).

## O que já existe no repositório

Os dados:

- `data/manual.md`: o Manual de Atendimento. A regra de negócio inteira está aqui e em nenhum outro lugar.
- `data/acoes.yaml`: os nomes das 16 ações possíveis.
- `data/dev/tickets.jsonl`: os 200 tickets de desenvolvimento, com o texto e os metadados do CRM do cliente (plano, ciclo, datas e histórico).
- `data/dev/gabarito.jsonl`: a ação correta de cada ticket, a regra que a decidiu e a seção do manual onde ela está. É a régua do checker e o seu instrumento de diagnóstico, não insumo do pipeline.
- `data/aptidao/`: 30 tickets e o gabarito do teste de aptidão.

As ondas são fixas: os tickets 1 a 10 do arquivo formam a primeira onda, os 11 a 20 a segunda, e assim por diante.

A instrumentação:

- `harness/llm.py`: o `ClienteLLM`, a única porta de acesso ao modelo. Ele lê provedor e modelo do `.env`, não envia temperatura e registra cada chamada no `log.jsonl` da pasta de execução, com as mensagens enviadas, a resposta bruta e os tokens de entrada e de saída informados pela API. Ele recusa uma pasta que já tenha log.
- `harness/aptidao.py`: o teste de aptidão.
- `harness/check.py`: o checker.
- `harness/config.py`: os limites do desafio.

```python
from harness.llm import ClienteLLM

llm = ClienteLLM("runs/dev")
resposta = llm.chamar(
    [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
    ],
    max_tokens=None,  # limite de tokens de saída desta chamada
)
```

E o ponto de partida:

- `baseline/manual_inteiro.py`: o classificador de hoje, com uma chamada por onda e o manual inteiro em cada uma. Ele acerta e estoura o orçamento. É também o exemplo da interface que o seu pipeline precisa ter:

```
python -m baseline.manual_inteiro --manual data/manual.md --tickets data/dev/tickets.jsonl --saida runs/baseline
```

O seu pipeline recebe os mesmos três argumentos, com esses nomes, porque o avaliador vai apontá-los para outros arquivos. Cada execução grava na pasta de saída um `saida.jsonl` com uma linha por ticket, em qualquer ordem:

```
{"id": "D001", "acao": "reembolso_automatico"}
```

## Sobre o foco do desafio

O manual muda na avaliação. O avaliador vai rodar o seu pipeline com uma versão atualizada do manual, com algumas regras alteradas, e com 200 tickets que você nunca viu. Resumo pronto guardado no repositório, feito à mão ou colado de um chat, chega lá desatualizado. Pista: trate o manual como entrada, e não como constante.

Resumo que parece bom. Um resumo bem escrito do manual lê como se tivesse tudo, e mesmo assim pode derrubar a nota, porque o que ele corta costuma ser justamente a exceção, a linha da tabela ou o limite que decide o ticket. Pista: o gabarito diz a regra e a seção de cada erro, e o log mostra o texto que o seu pipeline gerou. Compare os dois.

O fim do manual manda no começo. O Histórico de alterações, no final do documento, prevalece sobre o texto das seções. Pista: pergunte-se o que acontece com uma alteração quando o texto é cortado ou condensado.

Tickets com mais de um assunto. O manual define uma precedência entre áreas. Pista: um contexto que traz as regras de cada área, mas perde a precedência, erra justamente nesses tickets.

## Requisitos

### 1. O modelo certo

Conceitos do curso: Context Window para Prompt Engineering; Trabalhando com zero-shot em diversos modelos.

Escolha o modelo e prove que ele serve:

```
python -m harness.aptidao
```

O teste manda o manual inteiro e 30 tickets ao seu modelo e mede se ele acerta pelo menos 90% quando tem todas as regras na frente. Se ele não passa nem assim, nenhuma estratégia de contexto vai salvá-lo. O teste também mede a unidade de custo do desafio: 1 manual equivale aos tokens de entrada de uma chamada que envia só o manual, no seu modelo. Versione `runs/aptidao/`.

Nos modelos de raciocínio, os tokens que eles gastam pensando entram na conta, e o curso mostrou ao comparar modelos que não são poucos. Escolher o modelo já é a primeira decisão de custo.

### 2. O pipeline

Conceitos do curso: Sumarização; Truncamento; Prompt Chaining na prática com LangChain; Batch Prompting; System vs User Prompt; Exemplo estruturado de prompts.

Construa o pipeline que, a cada execução, lê o manual indicado em `--manual`, prepara com o próprio modelo o contexto que as ondas vão usar e classifica os tickets de `--tickets`, gravando o resultado em `--saida`.

As decisões são suas: o que pedir ao modelo na preparação do contexto, em quantas etapas, o que cada onda recebe, quantas chamadas por onda, o que vai no system e o que vai no user, e o formato da resposta. O curso apresentou a sumarização como forma de liberar espaço, com o risco de perder detalhes. Aqui esse risco vira nota.

Todo ticket termina classificado exatamente uma vez, com uma ação de `data/acoes.yaml`, mesmo quando o modelo devolve uma resposta incompleta ou quebrada.

### 3. As metas

Conceitos do curso: Precision; Recall; F1; Calculando as métricas; Context Window vs memória, custo e latência.

Rode o pipeline sobre o dev com a saída em `runs/dev/`. A execução precisa atingir, ao mesmo tempo:

- F1 macro de pelo menos 0,95;
- custo de no máximo 7 manuais.

O checker calcula precision, recall e F1 de cada ação, como nas aulas, e tira a média simples entre as ações presentes no gabarito. Essa média por classe (macro) não foi vista no curso: ela faz uma ação rara pesar tanto quanto uma frequente.

O custo é a soma dos tokens de entrada e de saída de todas as chamadas do log, inclusive as de preparação do contexto, dividida pela unidade medida na aptidão. A conta é bruta: tokens lidos do cache contam como qualquer outro.

As mesmas metas valem na execução do avaliador, com o manual atualizado e os tickets ocultos.

### 4. O registro das decisões

Conceitos do curso: Guidelines e trade-offs; Sumarização.

O README traz uma tabela com pelo menos três configurações que você testou, entre elas uma em que a preparação do contexto é um pedido genérico de resumo do manual. Cada linha tem o F1 macro, o custo em manuais e as regras que mais erraram, tirados do checker. A configuração final fica marcada.

Abaixo da tabela, transcreva o prompt de preparação do contexto da versão final e justifique as escolhas: o que você pediu ao modelo e por quê, o que cada onda recebe e como o pipeline lida com respostas incompletas.

## Restrições

Quebrar qualquer uma delas descaracteriza a entrega:

- `data/`, `harness/` e `baseline/` ficam exatamente como vieram. Se encontrar limitação no cliente ou no checker, documente no README em vez de alterá-los.
- Toda chamada ao modelo passa pelo `ClienteLLM` apontado para a pasta de `--saida`, com o mesmo provedor e modelo da aptidão.
- Cada execução envia ao modelo o manual indicado em `--manual`, integral, pelo menos uma vez, em uma ou mais chamadas. Serializar em JSON é permitido; cortar ou reescrever antes de enviar, não.
- Fora das pastas de execução em `runs/`, nada derivado do manual fica versionado: nenhum resumo ou destilado pronto, e nenhuma regra, limite, tabela ou número de seção copiado para o código ou para os prompts. Seus prompts dizem ao modelo como ler e o que extrair, nunca quais são as regras.
- O pipeline não reaproveita nada de execuções anteriores: cada execução prepara o próprio contexto a partir do manual que recebeu.
- Cada chamada contém tickets de uma única onda.
- O texto de cada ticket também vai integral ao modelo.
- O pipeline não lê o gabarito.
- Quem decide a ação é o modelo. O código pode traduzir o formato da resposta e calcular fatos neutros a partir dos metadados (ex.: dias entre duas datas), mas não compara com limites do manual nem escolhe a ação. Para um ticket que o modelo não conseguiu classificar, um valor padrão fixo é permitido.

## Fora de escopo

- Prompt caching como parte da meta. O custo é bruto; o cache pode baratear a sua fatura, mas não muda a nota.
- A Batch API assíncrona dos provedores, embeddings, fine-tuning ou qualquer chamada fora do `ClienteLLM`.
- Modelos diferentes por etapa. Prompt chaining é bem-vindo, mas com o mesmo modelo, para que a unidade de custo valha para todas as chamadas.
- Latência. Você pode paralelizar chamadas (o cliente suporta), mas tempo não é critério.
- LangSmith e tracing.

## Critérios de Aceite

Aptidão

☐ `runs/aptidao/` contém `log.jsonl`, `saida.jsonl` e `resultado.json` com `"aprovado": true`.

Execução no dev

☐ `runs/dev/` contém `saida.jsonl` e `log.jsonl`.
☐ Modelo: todas as chamadas usam o provedor e o modelo da aptidão.
☐ Integridade: os 200 tickets aparecem exatamente uma vez, com ações válidas.
☐ Rastreabilidade: o texto de cada ticket aparece em pelo menos uma chamada.
☐ Ondas: nenhuma chamada mistura tickets de ondas diferentes.
☐ Manual lido: todos os capítulos do manual aparecem no log.
☐ Custo de no máximo 7 manuais.
☐ F1 macro de pelo menos 0,95.
☐ `python -m harness.check runs/dev` termina com `STATUS: APROVADO` e exit code 0.

Avaliação com o manual atualizado

☐ Em um clone limpo, o comando do README, apontado para o manual atualizado e os tickets ocultos, gera uma execução que o checker aprova com os mesmos limites.

Restrições

☐ `data/`, `harness/` e `baseline/` estão idênticos aos do repositório base.
☐ Nenhum conteúdo derivado do manual (resumo, destilado, regra, limite, tabela ou número de seção) está no código ou nos prompts.
☐ Nenhuma regra no código compara com limites do manual ou escolhe a ação.

README

☐ Informa o provedor e o modelo.
☐ Documenta o comando do pipeline com `--manual`, `--tickets` e `--saida`.
☐ Traz a tabela com pelo menos três configurações, incluindo um pedido genérico de resumo, com F1 macro, custo e regras com mais erros, e a final marcada.
☐ Transcreve o prompt final de preparação do contexto e justifica as escolhas.

## Fluxo do avaliador

1. Clona o fork, cria o ambiente, instala o `requirements.txt` e preenche o `.env` com o provedor e o modelo do README.
2. Roda `python -m harness.check runs/dev` e confere o `STATUS: APROVADO`.
3. Compara `data/`, `harness/` e `baseline/` com o repositório base.
4. Roda o comando do README com `--manual` e `--tickets` apontados para o manual atualizado e os tickets ocultos e `--saida runs/avaliador`. Depois roda `python -m harness.check runs/avaliador` com `--manual`, `--tickets` e `--gabarito` apontados para os mesmos arquivos. Se reprovar, faz uma segunda tentativa em uma pasta nova; vale a melhor das duas.
5. Lê o código e os prompts do pipeline conferindo as restrições, e lê o README.

A execução entregue e a execução do avaliador precisam ser aprovadas pelo checker; se qualquer uma falhar, a entrega está incompleta.

## Entregável

Repositório público no GitHub, fork do repositório base, com tudo na branch `main`: o código do pipeline (onde e com o nome que você quiser), `runs/aptidao/` e `runs/dev/` versionadas e o README substituído pela sua documentação.

```
.
├── README.md           (seu)
├── data/               (não alterar)
├── harness/            (não alterar)
├── baseline/           (não alterar)
├── runs/
│   ├── aptidao/
│   └── dev/
└── ...                 (seu pipeline)
```

## Dicas finais

Rode a aptidão antes de qualquer outra coisa: são quatro chamadas e elas já dizem se o modelo serve e quanto vale um manual no seu bolso. O baseline não é obrigatório, mas rodá-lo uma vez e passar o checker nele mostra o tamanho do problema em números. Chamadas com o manual inteiro são grandes; se o provedor reclamar de limite por minuto, preencha `LLM_RPM` no `.env` e rode em sequência.

Como o cliente recusa pasta com log, faça seus experimentos em pastas novas (ex.: `runs/exp-resumo`) e gere `runs/dev` com o código que você vai entregar. Antes de entregar, rode o pipeline apontando `--manual` para uma cópia do manual em que você mudou uma regra: se a sua saída não mudar junto, o avaliador vai perceber antes de você.

Na dúvida, siga o erro: o checker diz a regra e a seção, e o `log.jsonl` mostra o contexto que o seu pipeline gerou. Um resumo que parece ótimo e um contexto que funciona são indistinguíveis até você medir.
