# Regras gerais de triagem

1. Precedência entre assuntos (maior → menor):
   1. Segurança (capítulo 14)
   2. Incidente técnico crítico (capítulo 15 — incidente cujo desfecho é escalar_engenharia)
   3. Fiscal (capítulo 16)
   4. Privacidade / LGPD (capítulo 17)
   5. Cancelamento e retenção (capítulo 18)
   6. Reembolso (capítulo 19)
   7. Usuários e permissões (capítulo 20)
   8. Planos e upgrade (capítulo 21)
   9. Incidente técnico não crítico (capítulo 15)
   10. Dúvida de uso

2. Mensagem sem pedido acionável → descartar.

3. Dúvida de uso (sistema faz o que cliente pergunta, não há relato de falha e não encaixa em 14–21) → suporte_padrao.

4. Um chamado = um código de ação: quando há vários assuntos, registre o código do assunto de maior precedência (ver lista acima); trate os demais como secundários sem mudar o código.

5. Contagem de dias (prazos):
   - Prazos em dias = dias corridos contados a partir do dia seguinte à data de referência (ex.: data da cobrança, data de emissão da nota, data do pedido anterior).
   - O último dia conta: se (data_abertura − data_referência) ≤ prazo então está dentro.
   - Sempre indique a data de referência usada pela regra.

6. Contagem de meses de casa:
   - Tempo contado a partir de cliente_desde; completa N meses no mesmo dia do mês N meses depois.
   - Se o dia não existe no mês destino (ex.: 31/01 → fevereiro), vale o dia 1 do mês seguinte.
   - Compare cliente_desde → data_abertura com operador "maior ou igual" (ex.: completar 12 meses no próprio dia conta como ≥ 12 meses).

---

# Segurança (capítulo 14) — ordem das verificações

Percorra esta lista nesta ordem; aplique a primeira condição verdadeira → código.

1. Relato de acesso desconhecido (login/alerta/dispositivo/ações no histórico não reconhecidas) → escalar_seguranca.

2. Relato de alteração não reconhecida dos dados bancários de recebimento (alteração já efetuada e não reconhecida pelo titular) → escalar_seguranca.

3. Reset de autenticação em dois fatores:
   - Se o plano é Empresa → escalar_seguranca.
   - Else, se quem solicita é o próprio titular → suporte_padrao.
   - Else, se quem solicita é outra pessoa (funcionário, contador, sócio que não é titular, procurador) → escalar_seguranca.

4. Troca de titularidade pedida por quem não é o titular atual → escalar_seguranca.

5. E-mail suspeito em nome da Orbita:
   - Se o cliente clicou no link ou informou dados → escalar_seguranca.
   - Se o cliente não clicou → suporte_padrao.
   - (Quando em dúvida sobre clique, pergunte antes de classificar.)

6. Perda ou roubo de celular com o app logado:
   - Se o plano é Empresa → escalar_seguranca.
   - Else (Essencial ou Profissional) → suporte_padrao.

7. Se nenhuma das situações acima → não é caso de segurança (voltar à seção 13).

---

# Incidentes técnicos (capítulo 15) — ordem das verificações

Aplique sempre nesta ordem; pare na primeira condição aplicável → código.

1. O problema afeta a emissão de notas fiscais (NF-e/NFS-e: transmissão, notas em "processando", rejeições gerais, comunicação com prefeitura/SEFAZ) → escalar_engenharia.

2. Falha em integração (API ou webhooks):
   - Se também afeta emissão de notas, a regra 1 já decidiu.
   - Se o plano é Essencial → oferta_upgrade.
   - Else (Profissional ou Empresa) → escalar_engenharia.

3. Plano Empresa (conta é Empresa) → escalar_engenharia.

4. Número de usuários afetados >= limiar do plano (contar usuários afetados pelo relato; se incerto, perguntar):
   - Limiares (tabela de verificação):
     - Essencial: limiar = 2 → se usuarios_afetados >= 2 → escalar_engenharia
     - Profissional: limiar = 5 → se usuarios_afetados >= 5 → escalar_engenharia
     - Empresa: não se aplica (já decidido no passo 3)
   - Comparação: "maior ou igual" (>=).

5. Exceção complementar (Profissional): se todos os usuarios_ativos da conta estão afetados E usuarios_ativos ≥ 3 (checar usuarios_ativos no CRM) → escalar_engenharia.

6. Se nenhuma das anteriores → suporte_padrao.

Observação: os limiares de incidentes técnicos acima são os da seção 15.4 e permanecem fixos (não mudam com alterações de limite de usuários do plano usadas em outras áreas).

---

# Fiscal — notas emitidas pelo cliente (capítulo 16) — ordem das verificações

Referência de prazo: data de emissão da nota; contagem conforme seção 13.5. Siga a ordem e pare na primeira condição aplicável → código.

1. Identificar tipo de nota: NF-e (produto) ou NFS-e (serviço). (Se cliente não disser, conferir na aba Notas emitidas do CRM, coluna "modelo".)

2. Identificar tipo de pedido: cancelamento ou correção.

3. Cancelamento de NF-e:
   - Se (data_abertura − data_emissao) ≤ 1 dia → nf_cancelamento_orientado.
   - Else (dias > 1) → fiscal_analise.

4. Cancelamento de NFS-e:
   - Dependendo da data de emissão da nota:
     - Se data_emissao ≤ 31/05/2026 → prazo = 5 dias; se (data_abertura − data_emissao) ≤ 5 → nf_cancelamento_orientado; else fiscal_analise.
     - If data_emissao ≥ 01/06/2026 → prazo = 10 dias; if (data_abertura − data_emissao) ≤ 10 → nf_cancelamento_orientado; else fiscal_analise.
   - (A regra de vigência depende da data de emissão da NFS-e; ver seção "Alterações vigentes".)

5. Correção de NF-e — verificar campos nesta ordem:
   1. Se o pedido envolve valor ou imposto (valor unitário, quantidade que altera total, alíquota, base de cálculo, desconto) → fiscal_analise (independentemente de prazo).
   2. Else, se o pedido envolve CPF ou CNPJ do destinatário → fiscal_analise (independentemente de prazo).
   3. Else, (erro em outros dados cadastrais que a carta de correção permite: endereço, razão social, descrição do produto) → aplicar carta de correção:
      - Se (data_abertura − data_emissao) ≤ 30 dias → nf_carta_correcao.
      - Else → fiscal_analise.
   - (Comparações: "menor ou igual" ou "maior" conforme acima.)

6. Correção de NFS-e:
   - Não existe carta de correção para NFS-e; tratar como cancelamento+reemissão:
     - Use o prazo aplicável ao cancelamento de NFS-e (ver item 4 acima): dentro do prazo → nf_cancelamento_orientado; fora → fiscal_analise.

7. Se nenhum dos itens acima se aplica → fiscal_analise.

---

# Privacidade e LGPD (capítulo 17) — ordem das verificações

Siga esta ordem; aplique a primeira condição verdadeira → código.

1. Pedido feito por terceiro (cliente final do usuário que fala sobre seus próprios dados) → suporte_padrao.

2. Reclamação de pedido de privacidade anterior sem resposta:
   - Calcule dias = (data_abertura − data_do_pedido_anterior).
   - Se days > 15 → encaminhar_dpo.
   - Else (days ≤ 15) → suporte_padrao.

3. Exportação de dados pedida pelo titular da conta:
   - Se plano = Empresa → suporte_padrao (exceção: exportação feita pelo próprio cliente no painel).
   - Else → solicitar_documentos (confirmar identidade com documento oficial com foto; para pessoa jurídica, contrato social ou documento de representação).
   - (Exportação é sempre gerada para o e-mail cadastrado do titular; não enviar para outro endereço.)

4. Exclusão de dados pedida pelo titular:
   - Se o titular emitiu notas fiscais pela Orbita nos últimos 5 anos (verificar Notas emitidas no CRM, filtro de período) → encaminhar_dpo.
   - Else → solicitar_documentos (confirmar identidade antes de executar).
   - (Comparação temporal: emitir notas nos últimos 5 anos → "sim" ou "não".)

5. Correção de dados cadastrais pelo titular (e-mail/telefone/endereço) → suporte_padrao.

6. Se nenhuma das verificações acima se aplica → registrar nota interna e escalar conforme instruções do capítulo 17.

---

# Cancelamento e retenção (capítulo 18) — ordem das verificações

Aplicar nesta ordem; a primeira condição verdadeira decide → código.

1. Fechamento da empresa (baixa do CNPJ, encerramento de atividades, fechamento do estabelecimento) → cancelamento_direto.

2. Recusa anterior de oferta de retenção:
   - Se existir recusa anterior registrada e (data_abertura − data_recusa) ≤ 180 dias → cancelamento_direto.
   - If (data_abertura − data_recusa) > 180 dias → ignorar recusa antiga (seguir passos seguintes).
   - (Contagem de 180 dias: dias corridos, seção 13.5.)

3. Plano Essencial:
   - Regra geral → cancelamento_direto.
   - Exceção: Essencial no ciclo anual E tempo de casa ≥ 24 meses (cliente_desde → data_abertura, seção 13.6) → oferta_retencao.

4. Motivo = preço e plano = Profissional → oferta_retencao (independentemente do tempo de casa).

5. Tempo de casa (aplica-se só a chamados que chegaram até aqui; contar meses segundo seção 13.6):
   - Se plano = Profissional:
     - Se tempo de casa ≥ 12 meses → oferta_retencao.
     - Else → cancelamento_direto.
   - If plano = Empresa:
     - If tempo de casa ≥ 6 months → oferta_retencao.
     - Else → cancelamento_direto.

---

# Reembolso (capítulo 19) — ordem das verificações

Referência de prazo: data da cobrança; contagem conforme seção 13.5. Aplique na ordem; a primeira condição verdadeira decide → código.

1. Cobrança duplicada (mesma cobrança lançada duas vezes para o mesmo período ou pagamento duplicado confirmado no extrato) → reembolso_automatico (ignora plano, prazo, histórico e valor).

2. Plano Empresa → reembolso_com_analise (exceto se já decidido como duplicada no passo 1).

3. Prazo (comparar data_abertura − data_cobranca com os prazos abaixo); se fora do prazo → negar_reembolso.
   - Para faturas da assinatura:
     - Se tipo = ciclo mensal:
       - Se data_da_cobranca ≤ 28/02/2026 → prazo = 7 dias; condição para estar dentro: (data_abertura − data_cobranca) ≤ 7.
       - If data_da_cobranca ≥ 01/03/2026 → prazo = 14 dias; condição: (data_abertura − data_cobranca) ≤ 14.
       - (Vigência baseada na data da cobrança; ver histórico de alterações.)
     - If ciclo anual & plano Essencial → prazo = 15 dias; condition: ≤15.
     - If ciclo anual & plano Profissional → prazo = 30 days; condition: ≤30.
   - Exceção: cobrança avulsa de pró-rata de upgrade → prazo = 7 dias (vale para qualquer ciclo e plano); referência = data da cobrança do pró-rata.

4. Histórico de reembolsos (campo reembolsos_12m no CRM):
   - Se reembolsos_12m ≥ 2 → reembolso_com_analise.
   - Exceção por tempo de casa: se tempo de casa ≥ 36 meses → o limiar sobe: reembolsos_12m ≥ 3 → reembolso_com_analise; se reembolsos_12m < 3 então prosseguir.
   - (Esta verificação só ocorre depois de confirmar que não é duplicada, que não é Empresa e que está dentro do prazo.)

5. Valor (teto de aprovação automática): compare valor da cobrança com teto; se valor estritamente maior que teto → reembolso_com_analise; se ≤ teto → seguir.
   - Tabelas de tetos:
     - Essencial (mensal ou anual): teto = R$ 200,00.
     - Profissional (mensal): teto = R$ 300,00.
     - Profissional (anual): teto = R$ 1.000,00.
   - (Comparação: "estritamente maior" → encaminhar para análise; "menor ou igual" → possível aprovação automática.)

6. Aprovação automática:
   - Se passou pelos passos anteriores sem ter sido decidido → reembolso_automatico.

---

# Usuários e permissões (capítulo 20) — limites e verificações

1. Tabela de limite de usuários ativos por plano (usar usuarios_ativos do CRM; contar o titular; comparar com operadores abaixo):
   - Limites vigentes (condição por data de abertura, ver seção "Alterações vigentes"):
     - Essencial → limite = 2.
     - Profissional → limite = 5 (para chamados com data_abertura ≤ 30/06/2026) OR limite = 8 (para chamados com data_abertura ≥ 01/07/2026).
     - Empresa → sem limite (ilimitado).
   - Observação: para Profissional anual aplica-se bônus de +2 usuários ao limite (aplicar o bônus sobre o limite vigente conforme data_abertura).

2. Pedido de adicionar usuários (se o plano = Empresa → suporte_padrao e parar).
   - Else (não Empresa): compute soma = usuarios_ativos (CRM) + quantidade_pedida.
     - If soma ≤ limite_do_plano (considerando bônus Profissional anual quando aplicável) → suporte_padrao.
     - If soma > limite_do_plano → oferta_upgrade.
     - (Comparação: soma menor ou igual → cabe; soma estritamente maior → oferta_upgrade.)

3. Troca de titularidade pedida pelo titular atual → solicitar_documentos (validar documentos do titular atual e do novo titular).
   - Troca pedida por quem não é titular → não é área de usuários: escalar_seguranca (ver capítulo 14).

4. Remover usuário ou mudar permissão:
   - Pedido feito por administrador da conta → suporte_padrao.
   - Pedido feito por quem não é administrador → solicitar_documentos (confirmar autorização do titular).

---

# Planos e upgrade (capítulo 21) — ordem das verificações

1. Upgrade (ir para plano superior) → ajuste_plano (qualquer plano de origem, qualquer ciclo, ajuste feito na hora; cobrança pró-rata).

2. Downgrade:
   1. Verificar ciclo:
      - Se ciclo atual = anual → suporte_padrao (downgrade só na renovação; registrar pedido e informar data de renovação; parar).
      - Else (ciclo mensal) → ir para verificação 2.2.
   2. (Só para ciclo mensal) Comparar usuarios_ativos com limite do plano de destino (tabela do capítulo 20, considerar bônus Profissional anual apenas se destino for Profissional anual — aqui estamos em downgrade mensal portanto comparar com limite padrão do plano de destino):
      - If usuarios_ativos > limite_do_plano_destino → suporte_padrao (orientar desativar usuários; depois cliente pode pedir downgrade de novo).
      - Else (usuarios_ativos ≤ limite_do_plano_destino) → ajuste_plano (downgrade efetuado).

3. Mudança de ciclo (sem mudar de plano):
   - Mensal → Anual → ajuste_plano (mudança feita).
   - Anual → Mensal → suporte_padrao (só na renovação; registrar e informar data).

4. Desconto de fidelidade (sem mudança de plano):
   - If plano ∈ {Profissional, Empresa} AND tempo_de_casa ≥ 24 meses → ajuste_plano (desconto de fidelidade).
   - Else → suporte_padrao.
   - Plano Essencial → suporte_padrao (não há desconto de fidelidade).

5. Dúvida sobre preço → suporte_padrao.

---

# Alterações vigentes (entradas do capítulo 22 que mudam prazos/limites/regras)

1. 20/02/2026 — Prazo de reembolso do ciclo mensal.
   - Texto integral:
     "20/02/2026 — Prazo de reembolso do ciclo mensal. Para cobranças do ciclo mensal com data da cobrança a partir de 01/03/2026, o prazo de reembolso das faturas da assinatura passa a ser de 14 dias corridos, em qualquer plano. A mudança não vale para cobranças avulsas de pró-rata de upgrade, que continuam com o prazo próprio do capítulo 19. Cobranças do ciclo mensal com data até 28/02/2026 mantêm o prazo de 7 dias corridos. A forma de contagem não muda (seção 13.5) e os prazos do ciclo anual continuam os da tabela do capítulo 19."
   - Aplicação nas regras:
     - Em Reembolso (passo 3: Prazo), para fatura da assinatura, tipo ciclo mensal:
       - Se data_da_cobranca ≤ 28/02/2026 → prazo = 7 dias (condição: data_da_cobranca até 28/02/2026).
       - If data_da_cobranca ≥ 01/03/2026 → prazo = 14 dias (condição: data_da_cobranca a partir de 01/03/2026).
     - Estende-se: não altera prazos de pró-rata (pró-rata continua com prazo próprio = 7 dias) e não altera prazos do ciclo anual.

2. 15/05/2026 — Prazo de cancelamento de NFS-e.
   - Texto integral:
     "15/05/2026 — Prazo de cancelamento de NFS-e. Para NFS-e emitidas a partir de 01/06/2026, o prazo para cancelamento orientado passa a ser de 10 dias corridos contados da data de emissão. NFS-e emitidas até 31/05/2026 mantêm o prazo de 5 dias. Como a correção de NFS-e segue o prazo de cancelamento de NFS-e, o novo prazo vale também para ela. Os prazos de NF-e não mudam."
   - Aplicação nas regras:
     - Em Fiscal (passo 4: Cancelamento de NFS-e e passo 6: Correção de NFS-e), use:
       - If data_emissao ≤ 31/05/2026 → prazo_cancelamento = 5 dias.
       - If data_emissao ≥ 01/06/2026 → prazo_cancelamento = 10 dias.
     - Extensão: aplica-se também às correções de NFS-e (correção de NFS-e usa o prazo de cancelamento de NFS-e).

3. 10/06/2026 — Limite de usuários do plano Profissional.
   - Texto integral:
     "10/06/2026 — Limite de usuários do plano Profissional. Para chamados abertos a partir de 01/07/2026, o limite de usuários do plano Profissional passa de 5 para 8. A mudança vale para toda regra do manual que usa o limite de usuários do plano; no ciclo anual, os usuários de bônus do capítulo 20 continuam sendo somados ao novo limite. Chamados abertos até 30/06/2026 seguem o limite de 5. Os limites do Essencial e do Empresa não mudam. Esta mudança não altera os limiares de usuários afetados em incidentes técnicos (capítulo 15), que são uma tabela própria."
   - Aplicação nas regras:
     - Em Usuários e permissões (tabela de limite) e em Planos/Downgrade (verificação de usuarios_ativos vs limite), aplicar:
       - If data_abertura ≤ 30/06/2026 → limite Profissional = 5.
       - If data_abertura ≥ 01/07/2026 → limite Profissional = 8.
     - Extensão: vale para todas as regras que usam o limite de usuários do plano (capítulo 20 e capítulos que consultam esse limite), exceto limiares de incidentes técnicos (capítulo 15) que permanecem inalterados.

---