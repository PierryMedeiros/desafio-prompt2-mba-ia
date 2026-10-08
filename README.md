# O manual não cabe

A Orbita é um SaaS de cobrança e emissão de notas fiscais para pequenos negócios. Os tickets do suporte passam por um LLM que decide a ação de cada um, como reembolsar, negar, oferecer retenção, escalar para segurança, orientar o cancelamento de uma nota ou encaminhar ao encarregado de dados, entre outras. Essas decisões seguem o Manual de Atendimento, um documento de cerca de 42 mil tokens com políticas de oito áreas, tabelas por plano, exceções e um histórico de alterações. Como em todo manual de empresa, boa parte do texto trata de cultura, tom de voz e outros assuntos que não influenciam nenhuma decisão.

Hoje os tickets são triados em ondas de 10, e cada onda envia o manual inteiro ao modelo. O acerto é alto, mas cada rodada de 200 tickets custa o equivalente a ler o manual 21 vezes. A meta é reduzir esse custo para 7 leituras mantendo o acerto. Como as políticas mudam com frequência, o contexto precisa ser preparado pelo seu pipeline, com o seu modelo, a cada execução, e não por um resumo feito à mão.

## Objetivo

Entregar, em um fork público do repositório base:

- o teste de aptidão aprovado para o modelo que você escolher, em `runs/aptidao/`;
- um pipeline em Python que lê o manual, prepara o contexto com o próprio modelo e classifica os tickets respeitando as ondas;
- uma execução desse pipeline sobre os 200 tickets de desenvolvimento, em `runs/dev/`, aprovada pelo verificador;
- um README com o modelo usado, o comando de execução e o registro das suas decisões, com os números que as sustentam.

## Repositório base e ambiente

https://github.com/devfullcycle/REPO-A-DEFINIR

Você precisa de Python 3.10+ e de uma chave de API da OpenAI (https://platform.openai.com/api-keys) ou do Google Gemini (https://aistudio.google.com/app/apikey). O desafio não fixa modelo, e qualquer um que passe no teste de aptidão pode ser usado. Dependendo do modelo, o desafio inteiro custa de centavos a pouco mais de um dólar. Planos gratuitos costumam ter cotas baixas, e cada chamada com o manual inteiro tem dezenas de milhares de tokens, então confira os limites do seu plano antes de escolher.

```
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # preencha provedor, modelo e chave
```

Todos os comandos devem ser executados a partir da raiz do repositório, como módulos (`python -m ...`).

## O que já existe no repositório

Dados:

- `data/manual.md`: o Manual de Atendimento. Todas as regras de decisão estão nele.
- `data/acoes.yaml`: os nomes das 16 ações possíveis.
- `data/dev/tickets.jsonl`: os 200 tickets de desenvolvimento, com o texto e os metadados do CRM do cliente (plano, ciclo, data de adesão, data de abertura, reembolsos nos últimos 12 meses, usuários ativos e, nos pedidos de reembolso, a cobrança em questão).
- `data/dev/gabarito.jsonl`: a ação correta de cada ticket, a regra que a decidiu e a seção do manual onde ela está. O verificador usa esse arquivo para calcular a nota, e você pode usá-lo para analisar os erros. O pipeline não pode lê-lo.
- `data/aptidao/`: os 30 tickets e o gabarito do teste de aptidão.

As ondas são fixas. Os tickets 1 a 10 do arquivo formam a primeira onda, os tickets 11 a 20 formam a segunda, e assim por diante.

Ferramentas:

- `ferramentas/llm.py`: o `ClienteLLM`, por onde passam todas as chamadas ao modelo. Ele lê o provedor e o modelo do `.env`, não envia temperatura e registra cada chamada no `log.jsonl` da pasta de execução, com as mensagens enviadas, a resposta e os tokens de entrada e de saída informados pela API. Ele não aceita uma pasta que já tenha log.
- `ferramentas/aptidao.py`: o teste de aptidão.
- `ferramentas/verificar.py`: o verificador, que confere as regras do desafio e calcula a nota.
- `ferramentas/config.py`: os limites do desafio.

```python
from ferramentas.llm import ClienteLLM

llm = ClienteLLM("runs/dev")
resposta = llm.chamar(
    [
        {"role": "system", "content": "..."},
        {"role": "user", "content": "..."},
    ],
    max_tokens=None,  # limite de tokens de saída desta chamada
)
```

Ponto de partida:

- `baseline/manual_inteiro.py`: o classificador atual, com uma chamada por onda e o manual inteiro em cada uma. Ele atinge o acerto, mas ultrapassa o orçamento. Também serve de exemplo da interface que o seu pipeline precisa ter.

```
python -m baseline.manual_inteiro --manual data/manual.md --tickets data/dev/tickets.jsonl --saida runs/baseline
```

O seu pipeline recebe os mesmos três argumentos, com os mesmos nomes, porque o avaliador vai apontá-los para outros arquivos. Cada execução grava na pasta de saída um `saida.jsonl` com uma linha por ticket, em qualquer ordem:

```
{"id": "D001", "acao": "reembolso_automatico"}
```

## Pontos de atenção

Na avaliação, o avaliador vai rodar o seu pipeline com uma versão atualizada do manual, com algumas regras alteradas, e com 200 tickets que você não viu. Um resumo pronto, guardado no repositório, estará desatualizado nessa execução. O pipeline precisa tratar o manual como entrada.

Um resumo bem escrito pode parecer completo e, mesmo assim, baixar a nota, porque costuma cortar exceções, linhas de tabela e limites que decidem tickets. Para investigar, compare a regra e a seção de cada erro, informadas pelo gabarito, com o contexto que o seu pipeline gerou, registrado no log.

O Histórico de alterações, no fim do manual, prevalece sobre o texto das seções. Verifique se o contexto gerado pelo seu pipeline mantém essas alterações.

Alguns tickets tratam de mais de um assunto, e o manual define uma precedência entre áreas para esses casos. Um contexto que traz as regras de cada área, mas não traz a precedência, erra nesses tickets.

## Requisitos

### 1. Escolha do modelo

Conceitos do curso: Context Window para Prompt Engineering; Trabalhando com zero-shot em diversos modelos.

Escolha o modelo e confirme com o teste de aptidão que ele atende ao desafio:

```
python -m ferramentas.aptidao
```

O teste envia o manual inteiro e 30 tickets ao modelo e verifica se ele acerta pelo menos 90%. Um modelo que não atinge esse resultado com o manual completo não vai atingi-lo com um contexto reduzido. Nem todo modelo pequeno passa no teste, e nos nossos testes vários ficaram entre 60% e 80%. Teste os candidatos em pastas próprias (ex.: `python -m ferramentas.aptidao --saida runs/aptidao-candidato1`). O verificador lê `runs/aptidao`, então a aptidão do modelo escolhido precisa estar nessa pasta.

O teste também mede a unidade de custo do desafio. Um manual equivale aos tokens de entrada de uma chamada que envia apenas o manual, no seu modelo. Versione `runs/aptidao/`.

Em modelos de raciocínio, os tokens usados no raciocínio também entram na conta. Como o curso mostrou ao comparar modelos, essa quantidade pode ser grande.

### 2. Pipeline

Conceitos do curso: Sumarização; Truncamento; Prompt Chaining na prática com LangChain; Batch Prompting; System vs User Prompt; Exemplo estruturado de prompts.

Construa o pipeline que, a cada execução, lê o manual indicado em `--manual`, usa o modelo para preparar o contexto das ondas e classifica os tickets de `--tickets`, gravando o resultado em `--saida`.

As decisões de implementação são suas: o que pedir ao modelo na preparação do contexto, em quantas etapas, o que cada onda recebe, quantas chamadas fazer por onda, o que vai no system e o que vai no user e o formato da resposta. O curso apresentou a sumarização como forma de liberar espaço, com o risco de perder detalhes. Neste desafio, detalhes perdidos aparecem como erros na avaliação.

Todo ticket precisa terminar classificado exatamente uma vez, com uma ação de `data/acoes.yaml`, mesmo quando o modelo devolver uma resposta incompleta ou fora do formato.

### 3. Metas

Conceitos do curso: Precision; Recall; F1; Calculando as métricas; Context Window vs memória, custo e latência.

Rode o pipeline sobre o dev, com a saída em `runs/dev/`. A execução precisa atingir os dois limites ao mesmo tempo:

- F1 macro de pelo menos 0,95;
- custo de no máximo 7 manuais.

O verificador calcula precision, recall e F1 de cada ação, como nas aulas, e tira a média simples entre as ações presentes no gabarito. Essa média por classe, chamada de macro, não foi vista no curso. Ela faz uma ação rara ter o mesmo peso de uma ação frequente.

O custo é a soma dos tokens de entrada e de saída de todas as chamadas do log, incluindo as de preparação do contexto, dividida pela unidade medida na aptidão. Tokens lidos do cache entram na conta como qualquer outro.

As mesmas metas valem para a execução do avaliador, com o manual atualizado e os tickets ocultos.

### 4. Registro das decisões

Conceitos do curso: Guidelines e trade-offs; Sumarização.

O README deve trazer uma tabela com pelo menos três configurações que você testou. Uma delas precisa usar, na preparação do contexto, um pedido genérico de resumo do manual. Cada linha mostra o F1 macro, o custo em manuais e as regras com mais erros, conforme o verificador. Marque a configuração final.

Abaixo da tabela, transcreva o prompt de preparação do contexto da versão final e justifique as escolhas: o que você pediu ao modelo e por quê, o que cada onda recebe e como o pipeline trata respostas incompletas.

## Restrições

A entrega precisa respeitar todos os itens abaixo:

- `data/`, `ferramentas/` e `baseline/` não podem ser alterados. Se encontrar alguma limitação no cliente ou no verificador, registre no README.
- Toda chamada ao modelo passa pelo `ClienteLLM` apontado para a pasta de `--saida`, com o mesmo provedor e modelo da aptidão.
- Cada execução envia ao modelo o manual indicado em `--manual`, completo, pelo menos uma vez, em uma ou mais chamadas. O manual pode ser serializado em JSON, mas não pode ser cortado ou reescrito antes do envio.
- Fora das pastas de execução em `runs/`, nada derivado do manual pode ser versionado. Isso inclui resumos ou destilados prontos e regras, limites, tabelas ou números de seção copiados para o código ou para os prompts. Os prompts podem dizer ao modelo como ler o manual e o que extrair dele, mas não quais são as regras.
- O pipeline não reaproveita nada de execuções anteriores. Cada execução prepara o próprio contexto a partir do manual recebido.
- Cada chamada contém tickets de uma única onda.
- O texto de cada ticket também é enviado completo ao modelo.
- O pipeline não lê o gabarito.
- A ação é decidida pelo modelo. O código pode converter o formato da resposta e calcular fatos neutros, que são contas de calendário (dias corridos, meses completos) entre datas dos metadados ou citadas no texto. O código não decide qual data vale para uma regra, não compara valores com limites do manual e não escolhe a ação. Quando o modelo não conseguir classificar um ticket, o código pode atribuir um valor padrão fixo.

## Fora de escopo

- Prompt caching como parte da meta. O custo considera todos os tokens, e o cache pode reduzir a sua fatura, mas não altera a nota.
- A Batch API assíncrona dos provedores, embeddings, fine-tuning e qualquer chamada fora do `ClienteLLM`.
- Modelos diferentes por etapa. Prompt chaining pode ser usado, desde que com o mesmo modelo em todas as etapas, para que a unidade de custo valha para todas as chamadas.
- Latência. As chamadas podem ser feitas em paralelo, porque o cliente suporta, mas o tempo de execução não é avaliado.
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
☐ `python -m ferramentas.verificar runs/dev` termina com `STATUS: APROVADO` e exit code 0.

Avaliação com o manual atualizado

☐ Em um clone limpo, o comando do README, apontado para o manual atualizado e para os tickets ocultos, gera uma execução aprovada pelo verificador com os mesmos limites.

Restrições

☐ `data/`, `ferramentas/` e `baseline/` estão idênticos aos do repositório base.
☐ Nenhum conteúdo derivado do manual (resumo, destilado, regra, limite, tabela ou número de seção) está no código ou nos prompts.
☐ Nenhuma regra no código compara valores com limites do manual ou escolhe a ação.

README

☐ Informa o provedor e o modelo.
☐ Documenta o comando do pipeline com `--manual`, `--tickets` e `--saida`.
☐ Traz a tabela com pelo menos três configurações, incluindo um pedido genérico de resumo, com F1 macro, custo e regras com mais erros, e a configuração final marcada.
☐ Transcreve o prompt final de preparação do contexto e justifica as escolhas.

## Fluxo do avaliador

1. Clona o fork, cria o ambiente, instala o `requirements.txt` e preenche o `.env` com o provedor e o modelo informados no README.
2. Roda `python -m ferramentas.verificar runs/dev` e confere o `STATUS: APROVADO`.
3. Compara `data/`, `ferramentas/` e `baseline/` com o repositório base.
4. Roda o comando do README com `--manual` e `--tickets` apontados para o manual atualizado e os tickets ocultos, e com `--saida runs/avaliador`. Depois roda `python -m ferramentas.verificar runs/avaliador` com `--manual`, `--tickets` e `--gabarito` apontados para os mesmos arquivos. Se a execução reprovar, faz uma segunda tentativa em uma pasta nova e considera a melhor das duas.
5. Lê o código e os prompts do pipeline para conferir as restrições e lê o README.

A execução entregue e a execução do avaliador precisam ser aprovadas pelo verificador. Se qualquer uma delas falhar, a entrega está incompleta.

## Entregável

Repositório público no GitHub, fork do repositório base, com tudo na branch `main`: o código do pipeline (em qualquer pasta e com qualquer nome), as pastas `runs/aptidao/` e `runs/dev/` versionadas e o README substituído pela sua documentação.

```
.
├── README.md           (seu)
├── data/               (não alterar)
├── ferramentas/        (não alterar)
├── baseline/           (não alterar)
├── runs/
│   ├── aptidao/
│   └── dev/
└── ...                 (seu pipeline)
```

## Dicas finais

Comece pela aptidão. São quatro chamadas, e o resultado mostra se o modelo serve e qual é a unidade de custo no seu modelo. Rodar o baseline não é obrigatório, mas passá-lo uma vez pelo verificador mostra o tamanho do problema. As chamadas com o manual inteiro são grandes. Se o provedor reclamar de limite por minuto, preencha `LLM_RPM` no `.env` e rode as chamadas em sequência.

Como o cliente não aceita pasta com log, faça os experimentos em pastas novas (ex.: `runs/exp-resumo`) e gere `runs/dev` com o código que você vai entregar.

Antes de entregar, rode o pipeline com `--manual` apontando para uma cópia do manual em que você alterou uma regra. Se a saída não mudar de acordo, o pipeline não está lendo o manual de fato. Use o arquivo de tickets inteiro, porque num subconjunto o custo fixo da preparação pesa mais e o verificador reprova no custo. Como não existe gabarito para o manual alterado, confira manualmente os tickets que a mudança deveria afetar.

O tamanho do contexto gerado varia entre execuções, e o custo e o F1 variam junto. Rode a configuração final mais de uma vez e deixe margem nos dois limites, já que o avaliador faz a própria execução, com outro manual e outros tickets.

Para investigar erros, use a regra e a seção informadas pelo verificador e o contexto registrado no `log.jsonl`.