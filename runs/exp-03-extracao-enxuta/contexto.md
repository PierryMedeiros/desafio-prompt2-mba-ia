# Triagem e regras gerais

1. Quando o chamado traz mais de um assunto, escolher o assunto de maior precedência (da maior para a menor) → código decidido pela regra da área correspondente:
   1. Segurança (capítulo 14)
   2. Incidente técnico crítico (capítulo 15; definido quando as regras do capítulo 15 resultam em escalar_engenharia)
   3. Fiscal (capítulo 16)
   4. Privacidade e LGPD (capítulo 17)
   5. Cancelamento e retenção (capítulo 18)
   6. Reembolso (capítulo 19)
   7. Usuários e permissões (capítulo 20)
   8. Planos e upgrade (capítulo 21)
   9. Incidente técnico não crítico (capítulo 15; qualquer desfecho de incidente técnico que NÃO seja escalar_engenharia)
   10. Dúvida de uso (suporte_padrao)
2. Mensagem sem pedido acionável (spam, propaganda, teste, texto sem sentido) e sem outro assunto → descartar.
3. Dúvida de uso (pergunta sobre como fazer algo que o sistema já faz, sem relato de falha e sem enquadrar-se em 14–21) → suporte_padrao.
4. Contagem de dias (prazos): todos os prazos em dias são em dias corridos, contados a partir do dia seguinte à data de referência. Procedimento: calcular dias = diferença entre data_abertura e data_de_referencia; se dias ≤ prazo → dentro do prazo; se dias > prazo → fora do prazo. (Último dia conta.)
5. Contagem de meses de casa (tempo de cliente): tempo contado a partir de cliente_desde; o cliente completa N meses quando data_abertura ≥ cliente_desde + N meses; se o dia não existe no mês de destino (ex.: 31/01 → fevereiro) vale o dia 1 do mês seguinte.

---

# Segurança (capítulo 14)

Siga esta ordem. Pare na primeira condição que corresponder ao relato e aplique o código indicado.

1. Acesso desconhecido à conta (login, alerta de novo acesso de cidade/dispositivo estranho, usuário conectado não reconhecido, ações no histórico não reconhecidas) → escalar_seguranca.
2. Alteração não reconhecida dos dados bancários de recebimento (cliente relata alteração já ocorrida que ele não reconhece) → escalar_seguranca.
3. Reset de dois fatores:
   - Verificar exceção por plano (veja passo 3.a). Se não aplicar, então:
     - Pedido feito pelo próprio titular da conta → suporte_padrao.
     - Pedido feito por outra pessoa (funcionário, contador, sócio que não é titular, procurador) → escalar_seguranca.
   3.a Exceção por plano (verificar antes): plano Empresa → qualquer pedido de reset de dois fatores, mesmo se feito pelo próprio titular → escalar_seguranca.
4. Troca de titularidade pedida por quem não é o titular atual → escalar_seguranca.
5. E-mail suspeito em nome da Orbita:
   - Cliente clicou no link ou informou dados após o e-mail → escalar_seguranca.
   - Cliente não clicou nem informou dados → suporte_padrao.
6. Perda ou roubo de celular com app logado:
   - Plano Empresa → escalar_seguranca.
   - Planos Essencial ou Profissional → suporte_padrao.
7. Regras complementares (aplicadas no passo relevante acima):
   - Nunca pedir senha/código/SMS/app autenticador (boa prática, não altera código).
   - Ao telefone registrar relato com data/hora antes de encerrar (boa prática).

---

# Incidentes técnicos (capítulo 15)

Aplique as verificações nesta ordem; pare na primeira que se aplicar.

1. O problema afeta a emissão de notas fiscais (erro ao transmitir NF-e/NFS-e, notas em "processando", rejeições generalizadas, falha de comunicação com prefeitura/SEFAZ) → escalar_engenharia.
2. Falha em integração (API ou webhooks):
   - Se plano Essencial → oferta_upgrade.
   - Se plano Profissional ou Empresa → escalar_engenharia.
   - (Se a falha também impede emissão de notas, passo 1 decide.)
3. Plano Empresa → escalar_engenharia.
4. Número de usuários afetados ≥ limiar do plano → escalar_engenharia, com a tabela:
   - Essencial: limiar = 2 → se usuários_afetados ≥ 2 → escalar_engenharia.
   - Profissional: limiar = 5 → se usuários_afetados ≥ 5 → escalar_engenharia.
   - Empresa: não se aplica (já decidido no passo 3).
   (Contar usuários afetados pelo relato do cliente; se incerto, perguntar.)
5. Exceção complementar ao Profissional (verificada após a tabela e antes do passo 6): se TODOS os usuarios_ativos da conta estão afetados e usuarios_ativos ≥ 3 → escalar_engenharia (mesmo quando usuarios_afetados < limiar da linha 4).
   - Conferir usuarios_ativos na lateral do CRM.
6. Demais casos (nenhuma das anteriores se aplicou) → suporte_padrao.

---

# Fiscal — notas emitidas pelo cliente (capítulo 16)

Siga esta ordem; a referência de prazo é a data de emissão da nota; contagem conforme seção 13.5.

1. Identificar tipo de nota: NF-e (produto) ou NFS-e (serviço) → próximo passo conforme tipo.
2. Identificar tipo de pedido: cancelamento ou correção.
3. Cancelamento de NF-e:
   - Se chamado aberto com dias_passados (data_abertura − data_emissao) ≤ 1 → nf_cancelamento_orientado.
   - Se dias_passados > 1 → fiscal_analise.
4. Cancelamento de NFS-e:
   - Se data_emissao da NFS-e < 01/06/2026:
     - se dias_passados ≤ 5 → nf_cancelamento_orientado
     - se dias_passados > 5 → fiscal_analise
   - Se data_emissao da NFS-e ≥ 01/06/2026:
     - se dias_passados ≤ 10 → nf_cancelamento_orientado
     - se dias_passados > 10 → fiscal_analise
   (observação: a mudança de prazo para 10 dias aplica-se a NFS-e emitidas a partir de 01/06/2026; ver "Alterações vigentes".)
5. Correção de NF-e — verificar nesta subordem:
   1. Correção em valor ou imposto (valor unitário, quantidade que altera o total, alíquota, base de cálculo, desconto) → fiscal_analise (sempre, qualquer prazo).
   2. Correção de CPF ou CNPJ do destinatário → fiscal_analise (sempre, qualquer prazo).
   3. Se não for os casos acima (erro em dados cadastrais como endereço, razão social, descrição de produto):
      - se dias_passados ≤ 30 → nf_carta_correcao
      - se dias_passados > 30 → fiscal_analise
6. Correção de NFS-e:
   - Não existe carta de correção para NFS-e; correção = cancelar e reemitir.
   - Aplicar o mesmo prazo de cancelamento de NFS-e (passo 4) para decidir nf_cancelamento_orientado ou fiscal_analise.
7. Observações operacionais:
   - Sempre conferir número da nota e data de emissão no CRM antes de decidir.
   - A carta de correção não corrige valores, impostos nem documento do destinatário (esses sempre → fiscal_analise).

---

# Privacidade e LGPD (capítulo 17)

Siga esta ordem; pare na primeira verificação aplicável.

1. Quem está pedindo? Pedido feito por terceiro (cliente final do usuário sobre os próprios dados que o usuário cadastrou) → suporte_padrao.
2. Reclamação de pedido anterior sem resposta:
   - Calcular dias = data_abertura − data_do_pedido_anterior.
   - Se dias > 15 → encaminhar_dpo.
   - Se dias ≤ 15 → suporte_padrao.
3. Exportação de dados pelo titular da conta:
   - Geral: confirmar identidade (documento com foto; se PJ, contrato social ou prova de representação) → solicitar_documentos.
   - Exceção: plano Empresa → exportação feita pelo próprio cliente no painel → suporte_padrao (orientar o caminho no painel).
4. Exclusão de dados pelo titular:
   - Se titular emitiu notas fiscais pela Orbita nos últimos 5 anos (verificar Notas emitidas no CRM com filtro de período) → encaminhar_dpo.
   - Se não emitiu notas fiscais pela Orbita nos últimos 5 anos → solicitar_documentos.
5. Correção dos próprios dados cadastrais pelo titular → suporte_padrao (orientar edição em Configurações > Dados da conta).
6. Boas práticas decisórias:
   - Sempre usar e-mail cadastrado para envio de exportação.
   - Se dúvida se quem escreve é titular ou terceiro, comparar e-mail de origem com cadastro; se incerto, pedir confirmação documental.

---

# Cancelamento e retenção (capítulo 18)

Aplique esta ordem estrita; a primeira verificação que decidir encerra a análise.

1. Fechamento da empresa (baixa do CNPJ, encerramento de atividades, fechamento do estabelecimento) → cancelamento_direto.
2. Recusa anterior de oferta de retenção:
   - Se existir recusa anterior registrada com dias = data_abertura − data_da_recusa:
     - Se dias ≤ 180 → cancelamento_direto.
     - Se dias > 180 → desconsiderar recusa anterior e continuar para passo 3.
3. Plano Essencial:
   - Regra geral: se plano = Essencial → cancelamento_direto.
   - Exceção: Essencial com ciclo anual e tempo_de_casa ≥ 24 meses (cliente_desde + 24 meses ≤ data_abertura) → oferta_retencao.
4. Motivo "preço" no plano Profissional → oferta_retencao (independentemente do tempo de casa).
5. Tempo de casa (última verificação; usar cliente_desde e regra de meses da seção 13.6):
   - Se plano = Profissional e tempo_de_casa ≥ 12 meses → oferta_retencao.
   - Se plano = Empresa e tempo_de_casa ≥ 6 meses → oferta_retencao.
   - Se abaixo desses mínimos → cancelamento_direto.
6. Observações:
   - A oferta de retenção é apresentada UMA única vez, salvo recusa anterior com >180 dias (passo 2).
   - Contar meses conforme seção 13.6; se completa exatamente no dia da abertura, considera atingido.

---

# Reembolso (capítulo 19)

Siga esta ordem; referência de prazo = data da cobrança; contagem conforme seção 13.5.

1. Cobrança duplicada (dois lançamentos iguais para a mesma coisa) → reembolso_automatico (ignora plano, prazo, histórico e valor). Confirmar duplicidade nos lançamentos.
2. Plano Empresa → reembolso_com_analise (exceto duplicidade que já decidiu).
3. Prazo (comparar data_abertura − data_da_cobrança):
   - Para cobranças do ciclo mensal:
     - Se data_da_cobrança ≤ 28/02/2026 → prazo = 7 dias.
     - Se data_da_cobrança ≥ 01/03/2026 → prazo = 14 dias.
     - (Aplicar o prazo correspondente à data_da_cobrança do lançamento.)
   - Para fatura da assinatura no ciclo anual:
     - Plano Essencial (anual) → prazo = 15 dias.
     - Plano Profissional (anual) → prazo = 30 dias.
   - Se pedido fora do prazo correspondente → negar_reembolso.
   - Observação: cobranças avulsas de pró-rata de upgrade têm prazo próprio = 7 dias (valendo para qualquer ciclo/plano); aplicar esse prazo ao tipo "prorata".
4. Histórico de reembolsos (reembolsos_12m no CRM):
   - Se reembolsos_12m ≥ 2 → reembolso_com_analise.
   - Exceção para clientes com tempo_de_casa ≥ 36 meses: exigir reembolsos_12m ≥ 3 para enviar à análise; se reembolsos_12m < 3 → continuar para passo 5.
5. Valor — tetos de aprovação automática (comparação estrita):
   - Se valor_da_cobrança > teto_correspondente → reembolso_com_analise.
   - Se valor_da_cobrança ≤ teto_correspondente → segue para aprovação automática.
   - Tabela de tetos (comparar plano e ciclo):
     - Essencial (mensal ou anual) → teto = R$ 200,00.
     - Profissional (mensal) → teto = R$ 300,00.
     - Profissional (anual) → teto = R$ 1.000,00.
   - Observação: cobrança duplicada sempre reembolso_automatico independentemente do teto.
6. Aprovação automática:
   - Se passou por 1–5 sem decisão e valor ≤ teto → reembolso_automatico.
7. Observações adicionais:
   - Prazo dos ciclos mensais mudou para 14 dias para cobranças com data_da_cobrança ≥ 01/03/2026 (ver "Alterações vigentes"). Pró-rata sempre 7 dias.
   - Quando reembolso_automatico → informar prazo de devolução (até 10 dias úteis; operação financeira).

---

# Usuários e permissões (capítulo 20)

Pedidos divididos por tipo; siga a sequência aplicável.

A. Tabela de limites de usuários (usar o limite efetivo dependendo da data do chamado):
   - Versão para chamados com data_abertura ≤ 30/06/2026:
     - Essencial → limite = 2
     - Profissional → limite = 5
     - Empresa → sem limite
   - Versão para chamados com data_abertura ≥ 01/07/2026:
     - Essencial → limite = 2
     - Profissional → limite = 8
     - Empresa → sem limite
   (A mudança do limite do Profissional de 5 para 8 vale para chamadas abertas a partir de 01/07/2026; ver "Alterações vigentes".)
   - Exceção de ciclo anual: Profissional com ciclo anual recebe +2 usuários de bônus ao comparar limites (aplicar o bônus sobre o limite vigente).
   - Contar usuarios_ativos exatamente como aparece no CRM.

B. Adicionar usuários — ordem:
   1. Se plano = Empresa → suporte_padrao (qualquer quantidade pedida).
   2. Caso contrário, calcular soma = usuarios_ativos + quantidade_pedida (usar usuarios_ativos do CRM e limite conforme A incluindo bônus anual):
      - Se soma ≤ limite → suporte_padrao.
      - Se soma > limite → oferta_upgrade.

C. Troca de titularidade:
   - Pedido feito pelo titular atual → solicitar_documentos (pedir documentos que comprovem identidade do titular atual e dados do novo titular).
   - Pedido feito por quem NÃO é o titular atual → (não é desta área) → escalar_seguranca (capítulo 14, seção 14.6).

D. Remover usuário ou mudar permissão:
   - Pedido feito por administrador da conta → suporte_padrao.
   - Pedido feito por quem não é administrador → solicitar_documentos (confirmar autorização do titular).

E. Observações:
   - Nunca inventar número de usuários; usar usuarios_ativos do CRM.
   - Para Profissional anual, ao adicionar usuários conte o bônus de +2 antes da comparação.

---

# Planos e upgrade (capítulo 21)

Ver campos na lateral: plano, ciclo, usuarios_ativos, cliente_desde, data_abertura. Escolher o tipo de pedido e aplicar a sequência.

1. Upgrade (qualquer origem/destino/ciclo) → ajuste_plano (upgrade realizado na hora; cobrança pró-rata).
2. Downgrade — em duas verificações:
   1. Se ciclo atual = anual → suporte_padrao (downgrade só ocorre na renovação; registrar pedido e data de renovação; encerrar análise).
   2. Se ciclo atual = mensal → comparar usuarios_ativos com limite do plano de destino (usar tabela da seção 20.2 vigente na data do chamado; quando destino = Profissional anual, considerar bônus só se aplicável à conta):
      - Se usuarios_ativos > limite_do_plano_de_destino → suporte_padrao (orientar desativar usuários; depois pedir downgrade de novo).
      - Se usuarios_ativos ≤ limite_do_plano_de_destino → ajuste_plano (downgrade efetuado).
3. Mudança de ciclo (sem mudar de plano):
   - Mensal → Anual → ajuste_plano (feito).
   - Anual → Mensal → suporte_padrao (só na renovação; registrar pedido).
4. Desconto de fidelidade:
   - Plano Profissional ou Empresa e tempo_de_casa ≥ 24 meses → ajuste_plano (aplicar desconto de fidelidade).
   - Demais casos (incluindo Essencial qualquer tempo) → suporte_padrao.
5. Dúvida sobre preço → suporte_padrao.

---

# Alterações vigentes (entradas do histórico que mudam prazos, limites ou tabelas; cada entrada vale por sua condição de data do chamado)

1. 20/02/2026 — Prazo de reembolso do ciclo mensal.
   - Texto integral: "Para cobranças do ciclo mensal com data da cobrança a partir de 01/03/2026, o prazo de reembolso das faturas da assinatura passa a ser de 14 dias corridos, em qualquer plano. A mudança não vale para cobranças avulsas de pró-rata de upgrade, que continuam com o prazo próprio do capítulo 19. Cobranças do ciclo mensal com data até 28/02/2026 mantêm o prazo de 7 dias corridos. A forma de contagem não muda (seção 13.5) e os prazos do ciclo anual continuam os da tabela do capítulo 19."
   - Aplicação: na regra de Reembolso (capítulo 19, seção de prazos) aplicar 7 dias para cobranças com data_da_cobrança ≤ 28/02/2026; aplicar 14 dias para cobranças com data_da_cobrança ≥ 01/03/2026. Não altera prazo de pró-rata (permanece 7 dias).

2. 15/05/2026 — Prazo de cancelamento de NFS-e.
   - Texto integral: "Para NFS-e emitidas a partir de 01/06/2026, o prazo para cancelamento orientado passa a ser de 10 dias corridos contados da data de emissão. NFS-e emitidas até 31/05/2026 mantêm o prazo de 5 dias. Como a correção de NFS-e segue o prazo de cancelamento de NFS-e, o novo prazo vale também para ela. Os prazos de NF-e não mudam."
   - Aplicação: na regra Fiscal (capítulo 16, cancelamento/correção de NFS-e) usar 5 dias para NFS-e com data_emissao ≤ 31/05/2026; usar 10 dias para NFS-e com data_emissao ≥ 01/06/2026. A mesma data-condição aplica-se à correção de NFS-e (cancelar+reemitir).

3. 10/06/2026 — Limite de usuários do plano Profissional.
   - Texto integral: "Para chamados abertos a partir de 01/07/2026, o limite de usuários do plano Profissional passa de 5 para 8. A mudança vale para toda regra do manual que usa o limite de usuários do plano; no ciclo anual, os usuários de bônus do capítulo 20 continuam sendo somados ao novo limite. Chamados abertos até 30/06/2026 seguem o limite de 5. Os limites do Essencial e do Empresa não mudam. Esta mudança não altera os limiares de usuários afetados em incidentes técnicos (capítulo 15), que são uma tabela própria."
   - Aplicação: na regra de Usuários e Permissões (capítulo 20) e em qualquer verificação que use o limite de usuários por plano, aplicar limite Profissional = 5 se data_abertura ≤ 30/06/2026; aplicar limite Profissional = 8 se data_abertura ≥ 01/07/2026. Para Profissional anual, quando houver bônus de +2 usuários, somar o bônus ao limite vigente.

---