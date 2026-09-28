Resumo prático para triagem — guia rápido que o atendente usa para decidir a AÇÃO de cada chamado

Primeiros passos (sempre, antes de decidir)
- Leia o chamado inteiro (mensagens, anexos, histórico).
- Verifique a lateral do CRM: plano, ciclo, cliente_desde, data_abertura, reembolsos_12m, usuarios_ativos e, em pedidos de reembolso, a cobrança (data e valor).
- Resuma em uma frase o pedido principal. Identifique todos os assuntos citados.
- Lembre: todo chamado recebe 1 único código de ação. Trate outros assuntos na mesma resposta, mas registre o código do assunto que "comanda" o chamado.
- Antes de enviar a resposta, registre o campo Ação no helpdesk (é obrigatório).
- Se dúvida, pare e pergunte ao líder / canal #atendimento-apoio.

Lista curta dos códigos de ação (usar o que mais se aplica)
- escalar_seguranca — segurança (acesso/alteração bancária/titularidade por terceiro/reset 2FA por terceiro)
- escalar_engenharia — incidentes técnicos críticos (ver regras de criticidade)
- fiscal_analise — casos fiscais complexos fora de prazo/que exigem avaliação contábil
- nf_cancelamento_orientado — orientar cancelamento de nota (dentro do prazo)
- nf_carta_correcao — carta de correção para NF-e (dentro do prazo)
- encaminhar_dpo — casos que precisam do DPO (ex.: exclusão com notas emitidas)
- reembolso_automatico — reembolso aprovado pelo atendente (duplicidade sempre)
- reembolso_com_analise — reembolso enviado ao financeiro
- negar_reembolso — reembolso negado (fora do prazo)
- oferta_retencao — apresentar proposta de retenção (oufera)
- cancelamento_direto — cancelar assinatura sem oferta
- ajuste_plano — mudança de plano / upgrade / downgrade quando aplicável
- suporte_padrao — dúvidas de uso, operações rotineiras, ações que o atendimento resolve
- solicitar_documentos — quando preciso validar identidade para LGPD/troca titularidade/etc.
- descartar — spam / mensagens sem pedido

Regra geral de precedência entre assuntos (capítulo 13.2)
(da maior para a menor precedência — se aplicar, use o código da área correspondente)
1. Segurança
2. Incidente técnico crítico (escalar_engenharia)
3. Fiscal
4. Privacidade / LGPD
5. Cancelamento / retenção
6. Reembolso
7. Usuários e permissões
8. Planos e upgrade
9. Incidente técnico não crítico
10. Dúvida de uso

Área por área: decisões rápidas e ações (ordem de verificação resumida)

Segurança (usar escalar_seguranca)
- Verifique nesta ordem: acesso desconhecido; alteração não reconhecida de dados bancários; reset 2FA pedido por terceiro; troca de titularidade pedida por terceiro; e-mails suspeitos ou perda do celular com app logado (ver exceções por plano).
- Reset 2FA: se quem pede NÃO for o titular → escalar_seguranca. Exceção: plano Empresa → sempre escalar_seguranca.
- Alteração de dados bancários não reconhecida → escalar_seguranca (sempre).
- Macro típica: avisar que foi encaminhado à Segurança + orientar troca de senha/checar usuários.

Incidentes técnicos (decidir se é crítico → escalar_engenharia)
- Ordem de verificação (pare na primeira que se aplicar):
  1. Afeta emissão de notas? → escalar_engenharia (sempre).
  2. Falha de integração (API/webhooks)? → Essencial: oferta_upgrade; Profissional/Empresa: escalar_engenharia.
  3. Plano Empresa? → escalar_engenharia (qualquer número de usuários afetados).
  4. Número de usuários afetados ≥ limiar do plano? → escalar_engenharia.
     - Limiar (incidentes, não confundir com limite de usuários): Essencial = 2, Profissional = 5 (Empresa não aplica).
     - Exceção Profissional: se TODOS os usuários ativos são afetados e usuarios_ativos ≥ 3 → escalar_engenharia.
  5. Caso contrário → suporte_padrao.
- Reúna: prints, horário, navegador/app, quantos usuários, número de nota (se aplicável).

Fiscal — notas emitidas pelo cliente
- Sempre calcule prazo a partir da data de emissão da nota.
- Ordem:
  1. Identificar tipo de nota: NF-e (produto) ou NFS-e (serviço).
  2. Cancelamento NF-e: dentro de 1 dia → nf_cancelamento_orientado; depois → fiscal_analise.
  3. Cancelamento NFS-e: prazo atualizado (ver histórico) — NFS-e emitidas a partir de 01/06/2026 têm prazo de 10 dias; antes mantêm 5 dias → nf_cancelamento_orientado / fiscal_analise.
  4. Carta de correção NF-e: correções de dados cadastrais (endereço, razão social, descrição) até 30 dias → nf_carta_correcao; depois → fiscal_analise.
  5. Correção de valor, imposto ou CPF/CNPJ do destinatário → sempre fiscal_analise (independe de prazo).
- Macro: orientar passo a passo para cancelar ou emitir carta de correção; encaminhar à equipe fiscal quando necessário.

Privacidade / LGPD
- Ordem:
  1. Pedido vindo de terceiro (cliente final do usuário)? → suporte_padrao (orientar procurar a empresa que detém os dados).
  2. Reclamação por falta de resposta anterior? → se >15 dias desde o pedido original → encaminhar_dpo; se ≤15 dias → suporte_padrao.
  3. Exportação de dados pelo titular → solicitar_documentos (confirma identidade); exceção: Empresa pode exportar pelo painel → suporte_padrao.
  4. Exclusão de dados: se emitiu notas nos últimos 5 anos → encaminhar_dpo; se não → solicitar_documentos.
- Sempre usar etiqueta "LGPD" e anexar documentos apenas ao chamado.

Cancelamento e retenção (oferta_retencao ou cancelamento_direto)
- Ordem (pare na primeira que decidir):
  1. Fechamento da empresa (baixa do CNPJ / encerramento atividades) → cancelamento_direto.
  2. Recusa anterior de oferta de retenção? se recusou em ≤180 dias → cancelamento_direto; se recusa >180 dias → ignorar e seguir regr a.
  3. Plano Essencial → em regra cancelamento_direto; exceção: Essencial anual com ≥24 meses de casa → oferta_retencao.
  4. Motivo = preço e plano = Profissional → oferta_retencao (independentemente do tempo de casa).
  5. Tempo de casa (quando chegou até aqui): Profissional ≥12 meses → oferta_retencao; Empresa ≥6 meses → oferta_retencao; caso contrário → cancelamento_direto.
- Registre recusa de oferta (data) na nota interna.

Reembolso (reembolso_automatico / reembolso_com_analise / negar_reembolso)
- Ordem:
  1. Cobrança duplicada? → reembolso_automatico (sempre).
  2. Plano Empresa? → reembolso_com_analise (financeiro).
  3. Prazo (compare data da cobrança com data_abertura; ver tabela e histórico de alterações!):
     - Fatura assin. mensal: prazo (ver histórico) — confirma se há alteração (ex.: mudança para 14 dias para cobranças com data a partir de 01/03/2026). Conferir capítulo 22 antes de aplicar.
     - Anual Essencial: 15 dias; Anual Profissional: 30 dias (tabela base).
     - Pró-rata de upgrade: prazo de 7 dias (sempre).
     - Se fora do prazo → negar_reembolso.
  4. Histórico de reembolsos (reembolsos_12m): se ≥2 → reembolso_com_analise (exceção clientes com ≥36 meses → só quando reembolsos_12m ≥3). Confira regras no capítulo 19.
  5. Valor: tetos de aprovação automática (se abaixo ou igual → reembolso_automatico; se acima → reembolso_com_analise).
     - Tetos: Essencial R$200, Profissional mensal R$300, Profissional anual R$1.000.
- Macro: use reembolso aprovado / em análise / negado conforme decisão. Explique prazo de estorno.

Usuários e permissões
- Tabela de limite de usuários (checar histórico para datas):
  - Essencial = 2
  - Profissional = 8 (alterado para 8 para chamados abertos a partir de 01/07/2026 — antes era 5)
  - Empresa = sem limite
- Pedido de adicionar usuários:
  - Se plano Empresa → suporte_padrao (aceita).
  - Caso contrário: soma usuarios_ativos + quantidade pedida ≤ limite → suporte_padrao (orientar pelo painel); se > limite → oferta_upgrade.
  - Profissional anual tem bônus de +2 usuários no limite (aplicar antes da comparação).
- Troca de titularidade:
  - Solicitada pelo titular atual → solicitar_documentos (validar documentos).
  - Solicitada por terceiro → é segurança → escalar_seguranca.
- Remoção/mudança de permissão: se pedido por administrador → suporte_padrao; se por não administrador → solicitar_documentos.

Planos e upgrade
- Upgrade → ajuste_plano (feito na hora; cobrar pró-rata).
- Downgrade:
  - Se ciclo anual → suporte_padrao (sofre só na renovação; registrar a solicitação).
  - Se ciclo mensal → comparar usuarios_ativos com limite do plano destino: se dentro → ajuste_plano; se acima → suporte_padrao (orientar desativar usuários antes).
- Mudança de ciclo:
  - Mensal → anual → ajuste_plano (imediato).
  - Anual → mensal → suporte_padrao (só na renovação).
- Descontos de fidelidade: Profissional/Empresa com ≥24 meses de casa → ajuste_plano possível; Essencial não tem desconto.

Boas práticas transversais (imediatas)
- Nunca peça senha, código de verificação, dados completos de cartão ou códigos 2FA. Em caso de suspeita, oriente e escale.
- Sempre registre uma nota interna clara: o que o cliente pediu, o que você verificou, o que fez e próximo passo.
- Use macros como ponto de partida; personalize: nome, data, valor e próximo passo.
- Antes de usar números (prazos, limites, preços), confira o capítulo 22 (Histórico) — ele prevalece sobre tabelas.
- Se o caso depende de outro time, mantenha o cliente atualizado mínimo a cada 2 dias úteis (compromisso: nenhum chamado fica >2 dias úteis sem atualização).
- Se for urgente (ameaça financeira, acesso comprometido) chame líder de turno e escale conforme as regras (segurança/incidente).
- Encerrar: sempre indique o próximo passo e assine com seu nome + Time Orbita.

Resumo rápido “qual ação escolher” (cheat-sheet)
- Acesso estranho / alteração de conta bancária / troca de titular por terceiro / reset 2FA por terceiro → escalar_seguranca
- Emissão de nota não ocorre / notas em “processando” / transmissão com erro → escalar_engenharia
- Pedido de cancelar NF-e dentro de 1 dia → nf_cancelamento_orientado; NFS-e dentro do prazo aplicável → nf_cancelamento_orientado; fora do prazo → fiscal_analise
- Pedido de exclusão com notas nos últimos 5 anos → encaminhar_dpo; exportação do titular → solicitar_documentos
- Pedido de cancelamento de assinatura:
  - fechamento do negócio → cancelamento_direto
  - recusa anterior recente → cancelamento_direto
  - É Essencial (regra geral) → cancelamento_direto (exceção Essencial anual ≥24 meses)
  - Profissional com motivo preço ou tempo de casa acima do mínimo → oferta_retencao
- Cobrança duplicada → reembolso_automatico
- Reembolso Empresa ou casos fora de prazo / alto valor / histórico → reembolso_com_analise
- Adicionar usuário que cabe no plano → suporte_padrao; se passa do limite → oferta_upgrade
- Upgrade de plano / mensal→anual → ajuste_plano; downgrade anual → entra na renovação (suporte_padrao)

Se ficar em dúvida: pare, confirme os campos do CRM, pergunte ao líder / canal #atendimento-apoio e nunca prometa prazos que dependem de outro time. Use este resumo como checklist de decisão e consulte o capítulo específico do manual para a resposta completa e a macro apropriada antes de enviar.