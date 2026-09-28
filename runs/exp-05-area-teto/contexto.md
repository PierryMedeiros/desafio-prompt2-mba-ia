# Triagem e regras gerais
1. Precedência entre assuntos (da maior para a menor) — escolha o assunto que comanda o chamado:  
   1) Segurança; 2) Incidente técnico crítico (incidente técnico que termina em escalar_engenharia); 3) Fiscal; 4) Privacidade/LGPD; 5) Cancelamento e retenção; 6) Reembolso; 7) Usuários e permissões; 8) Planos e upgrade; 9) Incidente técnico não crítico; 10) Dúvida de uso.

2. Mensagens sem pedido acionável → descartar.

3. Dúvida de uso (pergunta sobre como fazer algo que o sistema já faz, sem relato de falha e sem caber em capítulos 14–21) → suporte_padrao.

4. Contagem de dias (prazo em dias): dias corridos a partir do dia seguinte à data de referência (ex.: data da cobrança, data de emissão da nota, data de pedido anterior). Se (data_abertura − data_referência) ≤ prazo → dentro; se maior → fora. (Último dia conta.)

5. Contagem de meses de casa (cliente_desde): completa N meses no mesmo dia do mês, N meses depois; se o dia não existe no mês de destino (ex.: 31) vale dia 1 do mês seguinte.

---

# Segurança (capítulo 14) — ordem das verificações
Percorra nesta ordem e aplique a primeira que se encaixar; cada passo → código.

1. Acesso desconhecido à conta (login não reconhecido, alerta de novo acesso de cidade/dispositivo estranho, usuário conectado não reconhecido, ações no histórico que ninguém fez) → escalar_seguranca.

2. Alteração não reconhecida dos dados bancários de recebimento (cliente relata que nem ele nem alguém da equipe fez a alteração) → escalar_seguranca.

3. Reset de autenticação em dois fatores — verifique exceção por plano antes (passo 3.1). Se exceção não se aplicar, tabela:
   - pedido feito pelo próprio titular da conta → suporte_padrao
   - pedido feito por outra pessoa (não titular) → escalar_seguranca

   3.1 Exceção por plano (verificar primeiro): se plano = Empresa → qualquer pedido de reset de dois fatores → escalar_seguranca.

4. Troca de titularidade pedida por quem NÃO é o titular atual → escalar_seguranca.

5. E-mail suspeito em nome da Orbita (FAQ):  
   - se o cliente clicou no link ou informou dados após o e-mail → escalar_seguranca  
   - se não clicou → suporte_padrao

6. Perda/roubo de celular com app da Orbita logado (FAQ):  
   - se plano = Empresa → escalar_seguranca  
   - se plano ≠ Empresa → suporte_padrao

---

# Incidentes técnicos (capítulo 15) — ordem das verificações
Aplique na ordem e pare na primeira aplicável; cada passo → código.

1. Problema afeta emissão de notas fiscais (NF-e ou NFS-e: erros ao transmitir, notas presas em "processando", rejeições que aparecem para qualquer nota, falha de comunicação com prefeitura/SEFAZ) → escalar_engenharia.

2. Falha em integração (API ou webhooks):  
   - se plano = Essencial → oferta_upgrade  
   - se plano = Profissional ou Empresa → escalar_engenharia  
   (Se também afeta emissão de notas, passo 1 decide.)

3. Plano = Empresa (qualquer problema técnico relatado) → escalar_engenharia.

4. Número de usuários afetados ≥ limiar do plano (contar usuários afetados pelo relato; se não claro, perguntar): tabela de limiares (igual ou maior → escalar_engenharia)

| Plano | Limiar de usuários afetados |
|---|---|
| Essencial | 2 |
| Profissional | 5 |
| Empresa | não se aplica (decidido no passo 3) |

5. Exceção complementar Profissional: se plano = Profissional e "todos os usuários ativos da conta estão afetados" e usuarios_ativos ≥ 3 → escalar_engenharia. (Verificar usuarios_ativos na lateral do CRM.)

6. Demais casos (nenhuma das anteriores se aplicou) → suporte_padrao.

---

# Fiscal — notas emitidas pelo cliente (capítulo 16)
Ordem das verificações (parar na primeira aplicável). Referência de prazo = data de emissão da nota; contagem de dias conforme Triagem.

1. Identificar tipo de nota: NF-e (modelo 55) ou NFS-e (municipal).  
2. Identificar tipo de pedido: cancelamento ou correção.  
3. Cancelamento de NF-e: se (data_abertura − data_emissão) ≤ 1 dia → nf_cancelamento_orientado; se > 1 dia → fiscal_analise. (Prazo contado desde data de emissão; último dia conta.)  
4. Cancelamento de NFS-e: (ver item 5 sobre alteração vigente) — regra base: se (data_abertura − data_emissão) ≤ 5 dias → nf_cancelamento_orientado; se > 5 dias → fiscal_analise. (Alteração vigente pode mudar para 10 dias para notas emitidas a partir de 01/06/2026; ver "Alterações vigentes".)  
5. Correção de NF-e — antes de prazos, verificar campo:
   - Se erro em valor ou imposto (valor unitário, quantidade que altera total, alíquota, base de cálculo, desconto) → fiscal_analise (independentemente de dias).
   - Se erro no CPF ou CNPJ do destinatário → fiscal_analise (independentemente de dias).
   - Se erro em dado cadastral que pode ser corrigido por carta de correção (endereço, razão social, descrição do produto) e (data_abertura − data_emissão) ≤ 30 dias → nf_carta_correcao; se > 30 dias → fiscal_analise.
6. Correção de NFS-e: não há carta de correção para NFS-e; correção → cancelar e reemitir. Aplicar prazo de cancelamento de NFS-e (passo 4) para decidir: dentro do prazo → nf_cancelamento_orientado; fora → fiscal_analise.

---

# Privacidade e LGPD (capítulo 17) — ordem das verificações
Siga a ordem e aplique a primeira correspondência; cada passo → código.

1. Pedido feito por terceiro (cliente final do usuário falando sobre seus próprios dados) → suporte_padrao.

2. Reclamação de pedido anterior sem resposta: calcular dias entre data do pedido anterior e data_abertura (contagem conforme Triagem).  
   - se (data_abertura − data_pedido_anterior) > 15 dias → encaminhar_dpo  
   - se ≤ 15 dias → suporte_padrao

3. Exportação de dados pelo titular da conta → solicitar_documentos (confirmar identidade: documento com foto; para pessoa jurídica, contrato social ou equivalente).  
   - Exceção: plano = Empresa → exportação feita pelo próprio cliente no painel → suporte_padrao (orientar o caminho no painel).

4. Exclusão de dados pelo titular: consulte se há notas fiscais emitidas pela Orbita nos últimos 5 anos (ver aba Notas emitidas no CRM):  
   - se emitiu notas nos últimos 5 anos → encaminhar_dpo  
   - se NÃO emitiu notas nos últimos 5 anos → solicitar_documentos

5. Correção dos próprios dados cadastrais pelo titular (e-mail, telefone, endereço) → suporte_padrao.

---

# Cancelamento e retenção (capítulo 18) — ordem das verificações
Aplique em sequência; a primeira que decidir encerra; códigos: oferta_retencao ou cancelamento_direto.

1. Fechamento da empresa (baixa do CNPJ, encerramento de atividades, fechamento do estabelecimento) → cancelamento_direto.

2. Recusa anterior de oferta de retenção: antes de avaliar passos seguintes, se histórico mostra que o cliente já recusou UMA oferta de retenção anterior e essa recusa foi feita há ≤ 180 dias (contagem de dias conforme Triagem, da data da recusa até data_abertura) → cancelamento_direto. (Se recusa anterior foi > 180 dias → desconsiderar e prosseguir.)

3. Plano Essencial: regra geral → cancelamento_direto. Exceção: se plano = Essencial, ciclo = anual e tempo de casa ≥ 24 meses (contagem conforme Triagem) → oferta_retencao.

4. Motivo = preço e plano = Profissional → oferta_retencao (independentemente do tempo de casa). (Se motivo = preço e plano ≠ Profissional, não aplica este passo.)

5. Tempo de casa (só chega aqui clientes Profissional e Empresa que não foram decididos nos passos anteriores): tabela — se tempo de casa ≥ mínimo do plano → oferta_retencao; se < mínimo → cancelamento_direto.

| Plano | Tempo mínimo para oferta_retencao |
|---|---|
| Profissional | 12 meses |
| Empresa | 6 meses |

(Contagem de meses conforme Triagem; completar N meses no dia correspondente conta como atingido.)

---

# Reembolso (capítulo 19) — ordem das verificações
Referência de prazo = data da cobrança; contagem conforme Triagem. Aplique em ordem; primeira que decidir encerra.

1. Cobrança duplicada (dois lançamentos iguais para mesma coisa) → reembolso_automatico (ignora plano, prazo, histórico, valor). Confirme duplicidade nos registros.

2. Plano = Empresa → reembolso_com_analise (aplica após verificar duplicidade; duplicidade continua a devolver automaticamente).

3. Prazo: comparar (data_abertura − data_da_cobrança) com tabela abaixo; se fora do prazo → negar_reembolso. (Exceção: pró-rata de upgrade tem prazo próprio — ver passo 3.1.)

Tabela de prazos (tabela com linhas decisórias):

| Tipo de cobrança | Ciclo e plano | Prazo (dias corridos desde data da cobrança) |
|---|---|---|
| Fatura da assinatura | Ciclo mensal, qualquer plano | 7 dias (ver ALTERAÇÃO para cobranças com data ≥ 01/03/2026) |
| Fatura da assinatura | Ciclo anual, plano Essencial | 15 dias |
| Fatura da assinatura | Ciclo anual, plano Profissional | 30 dias |

3.1 Exceção de pró-rata: cobrança avulsa de pró-rata de upgrade → prazo = 7 dias (qualquer ciclo, qualquer plano), contado da data da cobrança.

3.2 Alteração vigente (ver "Alterações vigentes"): para cobranças do ciclo mensal com data_da_cobrança ≥ 01/03/2026 → prazo = 14 dias; para cobranças do ciclo mensal com data_da_cobrança ≤ 28/02/2026 → prazo = 7 dias. (Data de referência: data_da_cobrança.)

4. Histórico de reembolsos (campo reembolsos_12m no CRM):  
   - se reembolsos_12m ≥ 2 → reembolso_com_analise (aplica somente se não foi decisão por duplicidade, não Empresa e dentro do prazo).  
   - Exceção: se tempo de casa ≥ 36 meses (contagem conforme Triagem) → limiar aumenta: se reembolsos_12m ≥ 3 → reembolso_com_analise; se reembolsos_12m < 3 → prosseguir.

5. Valor — teto de aprovação automática (compare valor_da_cobrança com teto; se valor > teto → reembolso_com_analise; se ≤ teto → segue) — tabela:

| Plano | Ciclo | Teto de aprovação automática |
|---|---|---|
| Essencial | Mensal ou anual | R$ 200,00 |
| Profissional | Mensal | R$ 300,00 |
| Profissional | Anual | R$ 1.000,00 |

(Um valor exatamente igual ao teto não está acima; segue para aprovação automática.)

6. Aprovação automática (casos que passaram por 1–5 sem serem decididos) → reembolso_automatico.

---

# Usuários e permissões (capítulo 20)
Três tipos de pedido: adicionar usuários; troca de titularidade; remoção/mudança de permissão. Use usuarios_ativos do CRM.

1. Tabela oficial de limite de usuários (usa-se ao adicionar; se plano = Empresa, análise termina no passo 1.1):

| Plano | Limite de usuários ativos |
|---|---|
| Essencial | 2 |
| Profissional | 5 (ver ALTERAÇÃO para chamados abertos a partir de 01/07/2026) |
| Empresa | sem limite |

1.1 Se plano = Empresa → qualquer pedido de adicionar usuários → suporte_padrao.

2. Adicionar usuários (quando plano ≠ Empresa): calcule soma = usuarios_ativos + quantidade_pedida e compare com limite do plano (ver passo 1 e exceção do ciclo anual no passo 2.2):  
   - se soma ≤ limite → suporte_padrao  
   - se soma > limite → oferta_upgrade

2.2 Exceção Profissional anual: se plano = Profissional e ciclo = anual → limite utilizado = tabela do plano + 2 usuários de bônus; use esse limite na comparação.

2.3 Alteração vigente do limite (ver "Alterações vigentes"): para chamados abertos a partir de 01/07/2026 o limite do Profissional é 8; para chamados abertos até 30/06/2026 o limite do Profissional é 5. (Quando Profissional anual, some o bônus de +2 ao limite aplicável.)

3. Troca de titularidade pedida pelo titular atual → solicitar_documentos (solicitar documentos que comprovem identidade do titular atual e dados do novo titular).  
   - Se a troca é pedida por quem NÃO é o titular atual → (não é área de usuários) → escalar_seguranca (capítulo 14).

4. Remover usuário ou mudar permissão:  
   - pedido feito por administrador da conta → suporte_padrao  
   - pedido feito por quem não é administrador → solicitar_documentos

---

# Planos e upgrade (capítulo 21)
Siga a sequência por tipo de pedido.

1. Upgrade (ir para plano mais caro) → ajuste_plano (feito na hora; cobrança pró-rata). (Sem outras verificações.)

2. Downgrade (ir para plano mais barato) — duas etapas:
   2.1 Se ciclo atual = anual → downgrade só na renovação → suporte_padrao (registrar pedido; mudança entra na renovação). (Anota: plano Empresa é sempre anual, logo qualquer downgrade de Empresa → suporte_padrao.)  
   2.2 Se ciclo atual = mensal → comparar usuarios_ativos com limite do plano de destino (usar tabela de limites do capítulo 20, considerando exceção Profissional anual/bonus se aplicável):  
     - se usuarios_ativos > limite_destino → suporte_padrao (orientar desativar usuários antes)  
     - se usuarios_ativos ≤ limite_destino → ajuste_plano

3. Mudança de ciclo (sem mudar de plano):  
   - de mensal → anual → ajuste_plano (feita)  
   - de anual → mensal → suporte_padrao (só na renovação)

4. Desconto de fidelidade (sem mudança de plano): FAQ — se plano = Profissional ou Empresa e tempo de casa ≥ 24 meses → ajuste_plano (aplicar desconto de fidelidade); se tempo de casa < 24 meses ou plano = Essencial → suporte_padrao. (Contagem de meses conforme Triagem; completar 24 meses no dia conta.)

---

# Alterações vigentes (texto integral das entradas do histórico que alteram regras decisórias)
12/01/2026 — Horário de sábado. (não altera decisões de código — omitido)

20/02/2026 — Prazo de reembolso do ciclo mensal. Para cobranças do ciclo mensal com data da cobrança a partir de 01/03/2026, o prazo de reembolso das faturas da assinatura passa a ser de 14 dias corridos, em qualquer plano. A mudança não vale para cobranças avulsas de pró-rata de upgrade, que continuam com o prazo próprio do capítulo 19. Cobranças do ciclo mensal com data até 28/02/2026 mantêm o prazo de 7 dias corridos. A forma de contagem não muda (seção 13.5) e os prazos do ciclo anual continuam os da tabela do capítulo 19.

15/05/2026 — Prazo de cancelamento de NFS-e. Para NFS-e emitidas a partir de 01/06/2026, o prazo para cancelamento orientado passa a ser de 10 dias corridos contados da data de emissão. NFS-e emitidas até 31/05/2026 mantêm o prazo de 5 dias. Como a correção de NFS-e segue o prazo de cancelamento de NFS-e, o novo prazo vale também para ela. Os prazos de NF-e não mudam.

10/06/2026 — Limite de usuários do plano Profissional. Para chamados abertos a partir de 01/07/2026, o limite de usuários do plano Profissional passa de 5 para 8. A mudança vale para toda regra do manual que usa o limite de usuários do plano; no ciclo anual, os usuários de bônus do capítulo 20 continuam sendo somados ao novo limite. Chamados abertos até 30/06/2026 seguem o limite de 5. Os limites do Essencial e do Empresa não mudam. Esta mudança não altera os limiares de usuários afetados em incidentes técnicos (capítulo 15), que são uma tabela própria.

22/07/2026 — Feriados regionais. (não altera decisões de código — omitido)