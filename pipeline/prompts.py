"""Prompts do pipeline.

Nenhum prompt traz regra, limite, tabela ou número de seção do manual: eles dizem
ao modelo como ler o manual e o que extrair dele, e o conteúdo vem sempre do
manual recebido em --manual, a cada execução.
"""

# ------------------------------------------------------------------ preparação

# Configuração "resumo genérico" (usada só como comparação no README).
PREPARO_GENERICO = (
    "Você receberá o manual de atendimento de uma empresa. "
    "Faça um resumo do manual que um atendente possa usar para decidir a ação de cada chamado."
)

# Configuração final: extração estruturada das regras de decisão.
PREPARO_EXTRACAO = """\
Você vai preparar o material de consulta de um classificador de chamados de suporte. \
O documento que você receberá no próximo turno é o manual de atendimento completo da empresa. \
O classificador NÃO verá o manual: verá apenas o que você escrever agora, e precisa decidir, \
para cada chamado, um único código de ação dentre estes: {acoes}.

Sua tarefa é EXTRAIR (não resumir) tudo o que decide um código de ação e descartar o resto.

O que extrair, sem omitir nada:
1. As regras gerais de triagem: como escolher o assunto que comanda um chamado com vários assuntos \
(a lista de precedência completa, na ordem, com qualquer definição que mude a posição de um assunto), \
quando descartar, o que é dúvida de uso, e como contar dias e meses (incluindo se o último dia conta).
2. Para cada área que decide códigos de ação: a ordem das verificações exatamente como o manual manda, \
numerada. Em cada passo, a condição completa e o código de ação resultante. As exceções costumam estar \
fora do lugar óbvio (em perguntas frequentes, em notas junto de modelos de mensagem, em tabelas, em \
exemplos): procure no capítulo inteiro e encaixe cada exceção no passo em que ela é verificada.
3. Todos os números que decidem: prazos, limites, tetos, limiares, meses de casa, quantidades. \
Reproduza cada linha de cada tabela que decide ação. Diga sempre a data de referência de cada prazo \
e se a comparação é "maior", "maior ou igual", "menor ou igual" etc., como o manual diz.
4. Distinções de fronteira que o manual faz entre casos parecidos (quem pede, tipo de documento, \
tipo de cobrança, o que conta e o que não conta como um caso).
5. O histórico de alterações do fim do manual PREVALECE sobre o texto dos capítulos. Para cada \
alteração que muda prazo, limite, tabela ou regra de decisão: (a) aplique-a dentro da regra afetada, \
escrevendo as duas versões com a condição de data que decide qual vale (qual data do chamado define \
a vigência); (b) diga a que outras regras ela se estende, se o texto da alteração disser; \
(c) liste-a também numa seção final "Alterações vigentes", com o texto integral da entrada. \
Ignore alterações que não mudam nenhuma decisão.

O que descartar: história, cultura, tom de voz, modelos de mensagem, boas práticas, rotina do time, \
ferramentas, canais e horários, a não ser que tragam uma condição que muda o código de ação.

Economia (o material será lido muitas vezes, cada palavra custa):
- Cada regra, tabela e número aparece UMA única vez, no passo onde é verificado. Não crie seções \
de recapitulação, de "números citados" ou de "fronteiras" que repitam o que já está nos passos.
- Escreva só condição → código. Não descreva o que o atendente faz depois (orientar, registrar, \
pedir, responder), nem justificativas, nem referências a telas do sistema.
- Frases telegráficas; tabelas só quando tiverem 3 ou mais linhas.
- Toda exceção que o manual manda verificar antes de uma regra geral vem escrita ANTES dela, \
como passo próprio. Nunca escreva "regra geral → código" seguida de "exceção": quem lê de cima \
para baixo para na primeira linha que casa.
- A mesma coisa vale para as alterações do histórico: a versão com a condição de data fica dentro \
da própria linha da regra ou da tabela, e não num passo posterior.

Formato: markdown, um título por área, passos numerados. Nada de exemplos, exceto um exemplo curto \
quando ele desfaz uma ambiguidade de contagem ou de fronteira. Use os nomes exatos dos códigos de \
ação. Não invente regras que o manual não tem.\
"""

# ------------------------------------------------------------------ ondas

SISTEMA_ONDA = """\
Você é analista de triagem do atendimento. Decida o código de ação de cada chamado \
aplicando SOMENTE as regras abaixo, extraídas do manual de atendimento vigente.

Como decidir:
- Leia o chamado inteiro e identifique todos os assuntos. Quando houver mais de um, \
o código vem do assunto de maior precedência, pelas regras de triagem abaixo.
- Dentro da área, percorra as verificações na ordem e pare na primeira que se aplicar.
- Confira sempre se uma alteração vigente muda o prazo ou o limite do caso, pela data que define a vigência.
- Cada chamado traz, em "fatos", contas de calendário já feitas a partir dos metadados e das datas \
citadas no texto (dias corridos até data_abertura e meses completos de casa). Use-as em vez de refazer as contas.

Códigos possíveis: {acoes}.

Responda somente com uma linha por chamado, na ordem recebida, no formato:
<id> | <área que comanda o chamado> | <codigo>
sem nenhum outro texto. O código é sempre o último campo da linha.

=== REGRAS ===
{regras}
=== FIM DAS REGRAS ===\
"""
