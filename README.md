# O manual não cabe: solução

Pipeline de triagem em lote que lê o Manual de Atendimento a cada execução, pede ao próprio modelo que extraia dele as regras de decisão e classifica os tickets em ondas de 10 com esse material, dentro de 7 manuais de custo.

## Modelo

- **Provedor:** `openai`
- **Modelo:** `gpt-5-mini`
- `.env`: `LLM_PROVIDER=openai`, `LLM_MODEL=gpt-5-mini`, `OPENAI_API_KEY=...`, `LLM_RPM=` (vazio).

Aptidão (`runs/aptidao/resultado.json`): 30/30 = 1,00, unidade de 42.775 tokens = 1 manual.

Por que esse modelo: testei a aptidão em cinco modelos. Os que não raciocinam (ou que vêm com o raciocínio desligado por padrão) erraram justamente as regras com ordem de verificação e exceção, mesmo com o manual inteiro na frente:

| Modelo | Acurácia na aptidão | Tokens de saída por onda | Resultado |
|---|---|---|---|
| google / gemini-3.5-flash-lite | 0,67 | ~90 | reprovado |
| openai / gpt-4.1-mini | 0,60 | ~70 | reprovado |
| openai / gpt-5.4-mini | 0,70 | ~75 | reprovado |
| google / gemini-3.5-flash | não rodou (503 "high demand" nas 6 tentativas) | — | — |
| **openai / gpt-5-mini** | **1,00** | **~2.200** | **aprovado** |

O preço do gpt-5-mini é o raciocínio: cerca de 2 mil tokens de saída por onda, o que dá ~1 manual em 20 ondas. Esse gasto entrou no planejamento do orçamento (abaixo). As pastas `runs/apt-*` guardam as aptidões reprovadas.

## Como executar

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # LLM_PROVIDER=openai, LLM_MODEL=gpt-5-mini, OPENAI_API_KEY=...

python -m pipeline.triagem --manual data/manual.md --tickets data/dev/tickets.jsonl --saida runs/dev
python -m harness.check runs/dev
```

`--manual`, `--tickets` e `--saida` aceitam quaisquer arquivos e uma pasta nova. A execução leva cerca de 3 minutos (5 ondas em paralelo). Além de `log.jsonl` e `saida.jsonl`, a pasta de saída recebe `contexto.md`, com o material que o modelo preparou naquela execução (é a resposta da primeira chamada do log, gravada à parte para facilitar o diagnóstico).

A opção `--preparo generico` troca o prompt de preparação pelo pedido genérico de resumo; existe só para reproduzir a primeira linha da tabela de configurações.

## Resultado entregue (`runs/dev`)

```
Custo ............... OK (5.62 manuais; máximo 7.00)
F1 macro ............ OK (0.980; mínimo 0.95)
Acurácia ............ 0.980 (informativo)
Chamadas ............ 21; 240500 tokens de entrada e saída (informativo)
STATUS: APROVADO
```

## Como o pipeline funciona

```
manual (--manual) ──► [1 chamada] preparação: system = prompt de extração, user = manual integral
                                   └─► caderno de regras (~17 mil caracteres, ~4 mil tokens)
tickets (--tickets) ─► ondas fixas de 10 ─► [1 chamada por onda] system = caderno, user = 10 tickets + fatos
                                           └─► faltou ticket? [1 reenvio só dos faltantes, mesma onda]
                                                └─► ainda faltou? suporte_padrao (valor fixo)
```

- **Preparação (1 chamada).** O manual vai integral, sem nenhum corte, na mensagem `user`. O pedido de extração vai no `system`. A resposta é o único contexto que as ondas recebem.
- **Ondas (20 chamadas).** `system` = instrução de triagem + lista das 16 ações de `data/acoes.yaml` + caderno de regras. `user` = JSON com os 10 tickets da onda, cada um com todos os campos originais (o `texto` vai integral) mais um campo `fatos`.
- **Fatos neutros** (`pipeline/triagem.py`, função `fatos`): contas de calendário que o código faz sem conhecer nenhum limite do manual:
  - `meses_completos_de_casa`: meses de calendário completos de `cliente_desde` até `data_abertura`;
  - `dias_da_cobranca_ate_abertura`: `data_abertura` − `cobranca.data`, quando existe cobrança;
  - `dias_de_cada_data_do_texto_ate_abertura`: para cada data dd/mm/aaaa citada no texto, os dias até `data_abertura`.

  O código não sabe qual data é a de referência de cada regra, nem compara com prazo algum: quem decide qual fato usar e com qual limite comparar é o modelo, a partir do caderno.
- **Respostas incompletas.** A resposta de cada onda é lida linha a linha: o id tem que estar no início da linha e pertencer à onda, e a ação é a última palavra da linha que está em `data/acoes.yaml`. Linhas fora do formato, ids de fora da onda, ids repetidos e ações inválidas são ignorados. Se faltar algum ticket (ou a chamada falhar de vez), os tickets faltantes, e só eles, são reenviados uma vez na mesma onda. O que ainda faltar recebe `suporte_padrao`, o valor padrão fixo. Assim todo ticket termina classificado exatamente uma vez, com ação válida. No `runs/dev` nenhum ticket precisou de reenvio; no `runs/exp-02-extracao` um precisou (D042) e foi recuperado.

## Configurações testadas

Todas com gpt-5-mini, sobre os 200 tickets de dev. Custo e F1 tirados do `python -m harness.check`. Cada pasta está versionada em `runs/`.

| # | Configuração (o que mudou) | F1 macro | Custo (manuais) | Regras com mais erros (checker) | Status |
|---|---|---|---|---|---|
| 1 | **Resumo genérico**: "Faça um resumo do manual que um atendente possa usar para decidir a ação de cada chamado"; resposta só `<id> <ação>` (`exp-01-resumo`) | 0,928 | 4,69 | fis_nfse_corrigir (2), hist_prazo14 (2) e mais 10 regras com 1 erro cada (entre elas hist_nfse10, usr_bonus_anual, seg_2fa, seg_dispositivo, ree_historico) | reprovado (F1) |
| 2 | Extração estruturada v1: ordem de verificações, exceções nos passos, tabelas completas, alterações do histórico aplicadas nas regras (`exp-02-extracao`) | 0,992 | 7,55 | can_tempo_casa (1), fis_nfse_corrigir (1) | reprovado (custo) |
| 3 | v1 + regras de economia: cada regra uma vez, sem recapitulação, sem procedimentos; JSON dos tickets sem indentação (`exp-03-extracao-enxuta`) | 0,970 | 5,41 | can_fechamento, can_tempo_casa, hist_prazo14, lgpd_terceiro, ree_historico, ree_valor (1 cada) | aprovado |
| 4a | v3 + resposta com justificativa `<id> \| <área> \| <passo> \| <ação>` (`exp-04a-justificativa`) | 0,997 | 6,39 | can_tempo_casa (1) | aprovado |
| 4b | mesma configuração da 4a, segunda execução (`exp-04b-justificativa`) | 0,983 | 5,90 | can_essencial_fidelidade, hist_prazo14, tec_nf (1 cada) | aprovado |
| 5 | v3 + justificativa curta `<id> \| <área> \| <ação>` + teto de 2.500 palavras no caderno (`exp-05-area-teto`) | 0,964 | 5,30 | lgpd_exportacao_empresa (3), hist_prazo14 (2) | aprovado |
| **6 ✅ final** | v3 + justificativa curta + **exceções escritas antes da regra geral** e alterações dentro da linha da regra; sem teto de palavras (`dev`) | **0,980** | **5,62** | hist_prazo14 (2), can_tempo_casa (1), ree_historico_veterano (1) | **aprovado** |

O que cada linha ensinou:

- **1 → 2.** O resumo genérico ficou barato (o modelo escreveu só ~11 mil caracteres) e *parece* completo, mas perdeu exatamente o que o enunciado avisa: a correção de NFS-e (que usa o prazo de cancelamento), o prazo mensal novo do histórico (hist_prazo14), o bônus de usuários do Profissional anual e as exceções por plano de segurança. Pedir extração em vez de resumo, e dizer onde as exceções costumam se esconder (FAQ, notas de macro, tabelas), levou o F1 a 0,99, mas o caderno saiu com 30 mil caracteres (~7,3 mil tokens) e o custo estourou.
- **2 → 3.** Olhando o `contexto.md` da configuração 2, um terço dele era repetição: uma seção de "números citados" e outra de "fronteiras" que recopiavam tabelas já escritas nos passos, mais procedimentos ("orientar", "registrar"). Proibir recapitulação e procedimentos cortou o caderno para ~17 mil caracteres sem perder regra: o custo caiu de 7,55 para 5,41.
- **3 → 4.** Os erros da 3 eram de aplicação, não de regra faltando (ex.: D114 diz "a minha empresa está encerrando as atividades" e recebeu oferta de retenção, embora o caderno tivesse a regra de fechamento). Pedir a área e o passo em cada linha forçou o modelo a nomear a precedência antes da ação e subiu o F1, mas o raciocínio cresceu junto (~900 tokens a mais por onda) e o custo foi a 5,9–6,4, perto demais do teto para um manual desconhecido.
- **4 → 5.** Tentei economizar com justificativa curta e um teto de palavras no caderno. O teto fez o modelo reescrever as exceções como apêndice da regra geral ("exportação → solicitar_documentos. Exceção: Empresa → suporte_padrao"), e o classificador parou na primeira linha que casava: 3 erros em lgpd_exportacao_empresa. É o "resumo que parece bom" do enunciado: a exceção estava lá, mas na posição errada.
- **5 → 6 (final).** Sem teto de palavras, e com a instrução explícita de escrever a exceção *antes* da regra geral e a alteração do histórico *dentro* da linha da regra. F1 0,980 com 5,62 manuais: sobra ~1,4 manual para um manual atualizado que venha maior ou com mais alterações.

Os erros que sobram na final não são de regra perdida: o caderno tem as regras. D011 pede reembolso e desconto dizendo "quero continuar nele" e o modelo classificou como cancelamento na execução final e no teste com o manual alterado (e errou também na configuração 5). D042 mistura reembolso fora do prazo com falha de integração no Essencial. São erros de leitura do ticket, que variam de execução para execução.

### Conta do orçamento

Unidade = 42.775 tokens. Na execução final: preparação ≈ 43,6 mil de entrada + 8,2 mil de saída (≈ 1,2 manual); cada onda ≈ 7,0 mil de entrada + 2,5 mil de saída (≈ 0,22 manual) × 20 ≈ 4,4 manuais. Total 5,62. O que mais pesa é o caderno repetido em 20 ondas, por isso a economia foi feita nele e não na preparação.

## Teste com o manual alterado

Seguindo a dica do enunciado, acrescentei ao fim do histórico de alterações de uma cópia do manual uma entrada nova: *"Para chamados abertos a partir de 01/03/2026, o teto de aprovação automática de reembolso do plano Essencial, em qualquer ciclo, passa de R$ 200,00 para R$ 50,00."* Rodei o pipeline final nas três ondas que têm reembolso automático do Essencial (30 tickets; arquivos em `runs/exp-06-manual-alterado/entrada/`).

- O caderno gerado incorporou a alteração dentro do passo do teto, com a condição de data ("Se data_abertura ≥ 01/03/2026: Essencial teto = R$ 50,00").
- D025 e D167 (R$ 59,00, Essencial, abertos depois de 01/03/2026) mudaram de `reembolso_automatico` para `reembolso_com_analise`, como a nova regra manda. Nenhum outro ticket mudou.
- D011 também deveria ter mudado, mas já estava errado no `runs/dev` pelo motivo acima (classificado como cancelamento).
- O checker reprova esse teste em custo (1,88 para um máximo de 1,05), e isso é esperado: a preparação custa ~1 manual fixo, e o orçamento escala linearmente com o número de tickets (7 × 30/200). Não dá para usar um subconjunto pequeno para validar custo, só comportamento.

## Restrições: como foram respeitadas

- `data/`, `harness/` e `baseline/` não foram alterados. O pipeline importa `ler_acoes`, `ler_tickets` e `ondas` de `baseline/manual_inteiro.py` (como o `harness/aptidao.py` já faz).
- Toda chamada passa pelo `ClienteLLM` apontado para `--saida`, com o provedor e o modelo da aptidão.
- O manual vai integral na primeira chamada de cada execução, e nada é reaproveitado entre execuções.
- Os prompts (`pipeline/prompts.py`) dizem ao modelo como ler e o que extrair (ordem de verificações, exceções, tabelas, histórico), sem nenhuma regra, limite, tabela ou número de seção do manual.
- Cada chamada de onda (inclusive o reenvio) contém só tickets daquela onda, com o texto integral.
- O pipeline não lê o gabarito. O código calcula só fatos de calendário; quem escolhe a ação é o modelo, e o único valor padrão é o fixo `suporte_padrao`.

## Limitações encontradas no harness (documentadas, não alteradas)

- O `ClienteLLM` não permite configurar o esforço de raciocínio. Com o gpt-5-mini, o raciocínio (~2 mil tokens por onda) é a segunda maior fatia do custo e não há como reduzi-lo, só como não aumentá-lo com instruções que peçam mais análise na saída.
- O teste de aptidão não tem opção de reusar a pasta: para comparar modelos, cada tentativa foi feita em `runs/apt-<modelo>` e a aprovada foi renomeada para `runs/aptidao`.
- O orçamento do checker escala com o número de tickets, mas a preparação é um custo fixo de ~1 manual: execuções com poucos tickets sempre reprovam em custo.

## Prompt final de preparação do contexto

Transcrição de `PREPARO_EXTRACAO` (`pipeline/prompts.py`). `{acoes}` é preenchido em tempo de execução com a lista de `data/acoes.yaml`. Vai no `system`; o manual integral vai no `user`.

```text
Você vai preparar o material de consulta de um classificador de chamados de suporte. O documento que você receberá no próximo turno é o manual de atendimento completo da empresa. O classificador NÃO verá o manual: verá apenas o que você escrever agora, e precisa decidir, para cada chamado, um único código de ação dentre estes: {acoes}.

Sua tarefa é EXTRAIR (não resumir) tudo o que decide um código de ação e descartar o resto.

O que extrair, sem omitir nada:
1. As regras gerais de triagem: como escolher o assunto que comanda um chamado com vários assuntos (a lista de precedência completa, na ordem, com qualquer definição que mude a posição de um assunto), quando descartar, o que é dúvida de uso, e como contar dias e meses (incluindo se o último dia conta).
2. Para cada área que decide códigos de ação: a ordem das verificações exatamente como o manual manda, numerada. Em cada passo, a condição completa e o código de ação resultante. As exceções costumam estar fora do lugar óbvio (em perguntas frequentes, em notas junto de modelos de mensagem, em tabelas, em exemplos): procure no capítulo inteiro e encaixe cada exceção no passo em que ela é verificada.
3. Todos os números que decidem: prazos, limites, tetos, limiares, meses de casa, quantidades. Reproduza cada linha de cada tabela que decide ação. Diga sempre a data de referência de cada prazo e se a comparação é "maior", "maior ou igual", "menor ou igual" etc., como o manual diz.
4. Distinções de fronteira que o manual faz entre casos parecidos (quem pede, tipo de documento, tipo de cobrança, o que conta e o que não conta como um caso).
5. O histórico de alterações do fim do manual PREVALECE sobre o texto dos capítulos. Para cada alteração que muda prazo, limite, tabela ou regra de decisão: (a) aplique-a dentro da regra afetada, escrevendo as duas versões com a condição de data que decide qual vale (qual data do chamado define a vigência); (b) diga a que outras regras ela se estende, se o texto da alteração disser; (c) liste-a também numa seção final "Alterações vigentes", com o texto integral da entrada. Ignore alterações que não mudam nenhuma decisão.

O que descartar: história, cultura, tom de voz, modelos de mensagem, boas práticas, rotina do time, ferramentas, canais e horários, a não ser que tragam uma condição que muda o código de ação.

Economia (o material será lido muitas vezes, cada palavra custa):
- Cada regra, tabela e número aparece UMA única vez, no passo onde é verificado. Não crie seções de recapitulação, de "números citados" ou de "fronteiras" que repitam o que já está nos passos.
- Escreva só condição → código. Não descreva o que o atendente faz depois (orientar, registrar, pedir, responder), nem justificativas, nem referências a telas do sistema.
- Frases telegráficas; tabelas só quando tiverem 3 ou mais linhas.
- Toda exceção que o manual manda verificar antes de uma regra geral vem escrita ANTES dela, como passo próprio. Nunca escreva "regra geral → código" seguida de "exceção": quem lê de cima para baixo para na primeira linha que casa.
- A mesma coisa vale para as alterações do histórico: a versão com a condição de data fica dentro da própria linha da regra ou da tabela, e não num passo posterior.

Formato: markdown, um título por área, passos numerados. Nada de exemplos, exceto um exemplo curto quando ele desfaz uma ambiguidade de contagem ou de fronteira. Use os nomes exatos dos códigos de ação. Não invente regras que o manual não tem.
```

### Por que cada parte do prompt existe

- **"EXTRAIR (não resumir)" e "O classificador NÃO verá o manual".** A configuração 1 mostrou que um resumo decide pelo que parece importante e corta a exceção. Dizer ao modelo quem vai ler o material, e que essa pessoa não tem outra fonte, muda o critério de corte de "o que é importante" para "o que decide um código".
- **A lista de códigos no prompt.** Dá ao modelo o critério objetivo do que guardar: tudo o que leva a um desses 16 códigos fica, o resto sai.
- **Item 1 (precedência).** Um caderno com as regras de cada área mas sem a precedência erra os tickets com mais de um assunto. O pedido é genérico ("com qualquer definição que mude a posição de um assunto"), porque o manual pode mudar a lista.
- **Item 2 (ordem e exceções fora do lugar).** Nas áreas, a ação depende de *parar no primeiro passo que casa*, e várias exceções não estão no corpo da seção, e sim em FAQ, em notas de macro e em tabelas. O prompt diz onde procurar sem dizer quais são.
- **Item 3 (números, referência e tipo de comparação).** Prazos "até N dias" e tetos "acima de" dependem de ≤ vs <. Pedir a comparação como o manual diz evita que o resumo vire "cerca de N dias".
- **Item 5 (histórico).** É o ponto "o fim do manual manda no começo". Aplicar a alteração dentro da regra, com as duas versões e a condição de data, evita que o classificador use a tabela antiga. A cópia integral no fim é a rede de segurança caso a aplicação dentro da regra saia errada. Isso foi o que fez o teste com o manual alterado funcionar sem mudar uma linha de código.
- **Economia.** Veio da configuração 2 (sem ela, o custo estourou) e do contexto dela, onde um terço era repetição.
- **Exceção antes da regra geral.** Veio da configuração 5: a exceção estava no caderno, mas depois da regra geral, e foi ignorada.
- **Sem teto de palavras.** Também veio da configuração 5: limitar o tamanho obriga o modelo a escolher o que cortar, e ele corta estrutura. As regras de economia deram o mesmo tamanho sem esse efeito.

### O que cada onda recebe e por quê

- **System:** instrução de triagem (identificar todos os assuntos, aplicar a precedência, percorrer a área em ordem e parar no primeiro passo, conferir alterações vigentes, usar os fatos), a lista de ações e o caderno. O caderno fica no system porque é igual nas 20 ondas; os tickets, que mudam, ficam no user.
- **User:** os 10 tickets em JSON, com todos os campos originais e os `fatos`. Os fatos tiram do modelo a aritmética de datas (a regra de dias corridos e de meses de casa gera muitos erros de conta), sem tirar dele a decisão.
- **Formato de saída** `<id> | <área que comanda> | <ação>`: nomear a área antes da ação obriga o modelo a resolver a precedência primeiro. A versão com o passo também (configuração 4) acertou um pouco mais, mas custou ~0,5 manual a mais, uma margem que preferi guardar para o manual atualizado.
