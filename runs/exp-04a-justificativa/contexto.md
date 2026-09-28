# Regras gerais de triagem (capítulo 13)

1. Precedência entre assuntos (do maior para o menor; aplica-se quando há mais de um assunto no mesmo chamado):  
   1) Segurança (capítulo 14) → decisões de segurança vencem qualquer outro assunto.  
   2) Incidente técnico crítico (capítulo 15) — definido como incidente técnico cuja aplicação das regras do capítulo 15 terminar em escalar_engenharia.  
   3) Fiscal (capítulo 16).  
   4) Privacidade e LGPD (capítulo 17).  
   5) Cancelamento e retenção (capítulo 18).  
   6) Reembolso (capítulo 19).  
   7) Usuários e permissões (capítulo 20).  
   8) Planos e upgrade (capítulo 21).  
   9) Incidente técnico não crítico (capítulo 15; qualquer desfecho de incidente técnico diferente de escalar_engenharia).  
   10) Dúvida de uso (suporte_padrao).  

2. Um chamado, um código de ação: registre um único código de ação (lista fechada de 16 códigos). Mesmo com vários pedidos, o código é o do assunto que comanda o chamado (precedência acima).  

3. Mensagens sem pedido acionável → descartar. Condição: mensagem sem pedido (spam, propaganda, teste de formulário, texto sem sentido) e sem qualquer outro assunto acionável → descartar.  

4. Dúvida de uso → suporte_padrao. Condição: pergunta sobre como fazer algo que o sistema já faz, sem relato de falha e sem se encaixar em capítulos 14–21 → suporte_padrao.  

5. Contagem de dias (prazos em dias): todos os prazos em dias são dias corridos, contados a partir do dia seguinte à data de referência (ex.: data da cobrança, data de emissão da nota, data do pedido anterior). Regra operacional: calcular dias = data_abertura − data_referência; se dias <= prazo então está dentro do prazo; o último dia conta (inclusivo).  

6. Contagem de meses de casa (cliente_desde): meses contados a partir de cliente_desde; o cliente completa N meses no mesmo dia do mês N meses depois. Se o dia não existe no mês de destino (ex.: 31/01), vale o dia 1 do mês seguinte. Data usada para contagem = data_abertura.

---

# Segurança (capítulo 14)

Percorra a lista nesta ordem; aplique a primeira situação que corresponder ao relato:

1. Acesso desconhecido à conta (login não reconhecido, alerta de novo acesso por cidade/dispositivo estranho, usuário conectado que ninguém criou, ações no histórico que ninguém fez) → escalar_seguranca.  
2. Alteração não reconhecida dos dados bancários de recebimento (o cliente relata que dados bancários mudaram e ele/não reconhece a alteração; a alteração já ocorreu) → escalar_seguranca.  
3. Reset de dois fatores — verificar exceção por plano antes da tabela: se plano = Empresa então (exceção) → escalar_seguranca. Caso contrário, aplicar:  
   - pedido feito pelo próprio titular da conta → suporte_padrao.  
   - pedido feito por outra pessoa (não titular) → escalar_seguranca.  
4. Troca de titularidade pedida por quem não é o titular atual → escalar_seguranca.  
5. E-mail suspeito em nome da Orbita (cliente clicou no link ou informou dados) → escalar_seguranca. Se não clicou nem informou dados → suporte_padrao.  
6. Perda/roubo de celular com app logado — verificar exceção por plano antes: se plano = Empresa então → escalar_seguranca; se plano ≠ Empresa (Essencial ou Profissional) → suporte_padrao.

Observações de fronteira integradas: nunca pedir senha/códigos; a definição de “titular” e “quem pede” decide reset/titularidade conforme acima.

---

# Incidentes técnicos (capítulo 15)

Aplique verificações sempre nesta ordem; pare na primeira que se aplicar:

1. Problema afeta a emissão de notas fiscais (qualquer NF-e ou NFS-e que não autoriza/permite emissão, notas presas em "processando", rejeições generalizadas, falha de comunicação com prefeitura/SEFAZ a partir da Orbita) → escalar_engenharia. (Data/plano/usuários irrelevantes.)  
2. Falha em integração (API ou webhooks):  
   - se plano = Essencial → oferta_upgrade.  
   - se plano = Profissional ou Empresa → escalar_engenharia.  
   (Se a falha também impede emissão de notas, a verificação 1 prevalece.)  
3. Plano = Empresa (qualquer problema técnico relatado por conta Empresa) → escalar_engenharia.  
4. Número de usuários afetados atinge o limiar do plano (contar usuários afetados pelo relato; se relato não claro, perguntar): se usuarios_afetados >= limiar_do_plano → escalar_engenharia. Tabela de limiares (usada aqui):  
   | Plano | Limiar de usuários afetados | Ação se usuarios_afetados >= limiar |  
   |---|---:|---|  
   | Essencial | 2 | escalar_engenharia |  
   | Profissional | 5 | escalar_engenharia |  
   | Empresa | não se aplica (decidido na verificação 3) | não se aplica |  
   Observação histórica: os limiares desta tabela são específicos a incidentes técnicos; a alteração de limite de usuários do plano Profissional (ver capítulo 22) NÃO altera estes limiares de incidentes técnicos.  
5. Exceção complementar para Profissional: se todos os usuarios_ativos da conta estão afetados E usuarios_ativos >= 3 → escalar_engenharia (mesmo que usuarios_afetados < limiar de 5). (Verificar usuarios_ativos no CRM.)  
6. Demais casos (nenhuma verificação acima se aplica) → suporte_padrao.

Fronteiras: “incidente técnico crítico” = caso que termina em escalar_engenharia por aplicação desta ordem; caso contrário é não crítico.

---

# Fiscal — notas emitidas pelo cliente (capítulo 16)

Siga esta ordem (referência de prazo = data de emissão da nota; contagem de dias conforme seção 13.5):

1. Identificar tipo de nota: NF-e (produto) ou NFS-e (serviço) (ver coluna "modelo" em Notas emitidas).  
2. Identificar tipo de pedido: cancelamento ou correção.  
3. Cancelamento de NF-e: se (data_abertura − data_emissão) ≤ 1 dia → nf_cancelamento_orientado; se > 1 dia → fiscal_analise. (Data de referência = data de emissão; comparação: menor ou igual / maior.)  
4. Cancelamento de NFS-e: regra com alteração histórica (veja abaixo). Aplicar:  
   - Se data_emissão ≤ 31/05/2026: prazo = 5 dias; se (data_abertura − data_emissão) ≤ 5 → nf_cancelamento_orientado; se >5 → fiscal_analise.  
   - Se data_emissão ≥ 01/06/2026: prazo = 10 dias; se (data_abertura − data_emissão) ≤ 10 → nf_cancelamento_orientado; se >10 → fiscal_analise.  
5. Correção de NF-e — antes de olhar prazos, verificar o campo a corrigir:  
   - Se correção em valor ou imposto (valor unitário, quantidade que altera total, alíquota, base de cálculo, desconto) → fiscal_analise (independentemente do prazo).  
   - Se correção do CPF ou CNPJ do destinatário → fiscal_analise (independentemente do prazo).  
   - Se outro dado cadastral que pode ser corrigido por carta de correção (endereço, razão social, descrição do produto) → aplicar carta de correção: se (data_abertura − data_emissão) ≤ 30 dias → nf_carta_correcao; se >30 dias → fiscal_analise. (Data de referência = data de emissão; comparação ≤ / >.)  
6. Correção de NFS-e (qualquer campo): não existe carta de correção para NFS-e. Aplica-se a regra de cancelamento de NFS-e (passo 4) — dentro do prazo de cancelamento orientado → nf_cancelamento_orientado (orientar cancelar e reemitir); fora do prazo → fiscal_analise.

Tabela de prazos (reproduzida):  
| Tipo de nota | Pedido | Prazo (dias corridos, contado da data de emissão) | Dentro do prazo → Ação | Fora do prazo → Ação |  
|---|---|---:|---|---|  
| NF-e (produto) | Cancelamento | 1 dia | nf_cancelamento_orientado | fiscal_analise |  
| NFS-e (serviço) | Cancelamento | 5 dias (para notas emitidas até 31/05/2026) • 10 dias (para notas emitidas a partir de 01/06/2026) | nf_cancelamento_orientado (se dentro do prazo aplicável) | fiscal_analise |  
| NF-e (produto) | Carta de correção (dados cadastrais permitidos) | 30 dias | nf_carta_correcao | fiscal_analise |

Fronteiras explícitas: carta de correção NÃO corrige valores, impostos nem CPF/CNPJ do destinatário — esses sempre → fiscal_analise, independentemente do prazo.

---

# Privacidade e LGPD (capítulo 17)

Siga a ordem; pare na primeira verificação que se aplicar:

1. Pedido feito por terceiro (cliente final de um usuário que fala dos próprios dados do usuário) → suporte_padrao. (Condição: quem pede é terceiro referente a dados que a empresa usuária controla.)  
2. Reclamação por pedido anterior sem resposta: se (data_abertura − data_do_pedido_anterior) > 15 dias → encaminhar_dpo; se ≤ 15 dias → suporte_padrao. (Comparação: maior / menor ou igual; contagem de dias conforme 13.5; data de referência = data do pedido anterior.)  
3. Exportação de dados pelo titular da conta: verificar exceção por plano antes: se plano = Empresa → suporte_padrao (exportação feita pelo próprio cliente no painel). Caso contrário (não-Empresa) → solicitar_documentos (exigir confirmação de identidade: documento com foto; para pessoa jurídica, contrato social ou comprovante de representação). (Condição: pedido feito pelo titular.)  
4. Exclusão de dados pelo titular da conta: verificar emissão de notas nos últimos 5 anos antes de decidir:  
   - Se o titular emitiu notas fiscais pela Orbita nos últimos 5 anos → encaminhar_dpo.  
   - Se não emitiu notas fiscais pela Orbita nos últimos 5 anos → solicitar_documentos (confirmar identidade antes de executar).  
   (Data de referência para “últimos 5 anos” = data_abertura; comparação: emitiu ≥ alguma nota no intervalo [data_abertura − 5 anos, data_abertura] → encaminhar_dpo; caso contrário → solicitar_documentos.)  
5. Correção dos próprios dados cadastrais pelo titular (e-mail, telefone, endereço) → suporte_padrao (não requer documentos). (Exceção: alteração de dados bancários não reconhecida → segurança, capítulo 14.)

Fronteiras e documentos: documentos para exportação/exclusão enviados como prova de identidade; para Empresa exportação é self-service no painel → suporte_padrao.

---

# Cancelamento e retenção (capítulo 18)

Aplique as verificações exatamente nesta ordem; a primeira que decidir encerra a análise:

1. Fechamento da empresa (baixa do CNPJ, encerramento das atividades, fechamento do estabelecimento) → cancelamento_direto (independente de plano, ciclo, tempo de casa, histórico).  
2. Recusa anterior de oferta de retenção (consultar histórico): se cliente já recusou oferta de retenção anteriormente (registro no histórico) → cancelamento_direto. (Exceção: recusa antiga >180 dias — ver passo 2 FAQ abaixo.)  
3. Plano Essencial: regra geral → cancelamento_direto (Essencial não recebe oferta). Exceção: Essencial com ciclo anual E tempo de casa ≥ 24 meses → oferta_retencao. (Tempo de casa contado por cliente_desde até data_abertura, comparação "maior ou igual".)  
4. Motivo "preço" no plano Profissional: se motivo declarado = preço E plano = Profissional → oferta_retencao (independente do tempo de casa). (Esta verificação é feita depois dos passos 1–3.)  
5. Tempo de casa (última verificação; aplica-se apenas a clientes Profissional e Empresa que chegaram até aqui): se tempo_de_casa ≥ mínimo_por_plano → oferta_retencao; se < mínimo → cancelamento_direto. Tabela de mínimos:  
   | Plano | Tempo de casa mínimo para oferta de retenção (contagem por cliente_desde → data_abertura) |  
   |---|---:|  
   | Profissional | 12 meses (≥ 12 meses → oferta_retencao; < 12 → cancelamento_direto) |  
   | Empresa | 6 months (≥ 6 meses → oferta_retencao; < 6 → cancelamento_direto) |

Notas de exceção e fronteiras integradas: recusa anterior feita há mais de 180 dias (contados da data da recusa até a data_abertura) NÃO impede nova oferta (neste caso ignorar recusa antiga e seguir passos 3–5); recusa com ≤ 180 dias → mantém cancelamento_direto.

---

# Reembolso (capítulo 19)

Aplique verificações nesta ordem; a primeira que decidir encerra a análise. Referência de prazo = data da cobrança; contagem de dias conforme seção 13.5.

1. Cobrança duplicada (dois lançamentos iguais para mesma coisa no histórico/extrato) → reembolso_automatico. (Esta verificação ignora todas as demais: plano, prazo, histórico de reembolsos e valor não importam; inclusive vale para Empresa.)  
2. Plano = Empresa → reembolso_com_analise. (Verificação feita depois da duplicidade; se duplicada, duplicidade vence.)  
3. Prazo — tabela com alteração histórica (compare data_abertura − data_da_cobranca):  
   - Para cobranças do ciclo mensal: aplicar condicional histórico:  
     • Se data_da_cobranca ≤ 28/02/2026 → prazo = 7 dias; se (data_abertura − data_da_cobranca) ≤ 7 → dentro → prosseguir; se >7 → negar_reembolso.  
     • Se data_da_cobranca ≥ 01/03/2026 → prazo = 14 dias; se (data_abertura − data_da_cobranca) ≤ 14 → dentro → prosseguir; se >14 → negar_reembolso.  
   - Para ciclo anual, plano Essencial → prazo = 15 dias; se (data_abertura − data_da_cobranca) ≤ 15 → dentro → prosseguir; se >15 → negar_reembolso.  
   - Para ciclo anual, plano Profissional → prazo = 30 days; se (data_abertura − data_da_cobranca) ≤ 30 → dentro → prosseguir; se >30 → negar_reembolso.  
   Observação: cobrança avulsa de pró-rata de upgrade tem prazo próprio 7 dias (independente de ciclo/plano) — ver FAQ; contagem a partir da data_da_cobranca.  
4. Histórico de reembolsos (campo reembolsos_12m): se reembolsos_12m ≥ 2 → reembolso_com_analise. Exceção para clientes com tempo_de_casa ≥ 36 meses: nesses clientes só enviar para análise se reembolsos_12m ≥ 3. (Comparações: maior ou igual.) Esta verificação é feita após confirmar duplicidade e prazo e plano Empresa. Nota: se o pedido já está fora do prazo, resultado = negar_reembolso independentemente do histórico.  
5. Valor (teto de aprovação automática): consultar tabela de tetos abaixo; se valor_da_cobranca > teto (estritamente maior) → reembolso_com_analise; se ≤ teto → prosseguir. Tabela de tetos de aprovação automática:  
   | Plano | Ciclo | Teto de aprovação automática |  
   |---|---|---:|  
   | Essencial | Mensal ou anual | R$ 200,00 |  
   | Profissional | Mensal | R$ 300,00 |  
   | Profissional | Anual | R$ 1.000,00 |

6. Aprovação automática (última verificação): se passou por 1–5 sem ser decidido e não duplicidade → reembolso_automatico.

Fronteiras integrais: cobrança duplicada sempre → reembolso_automatico (override); pró-rata de upgrade prazo = 7 dias (qualquer plano/ciclo); plano Empresa sempre para análise (exceto duplicidade).

---

# Usuários e permissões (capítulo 20)

Siga a sequência segundo o tipo de pedido.

Tabela oficial de limites de usuários (usar usuario_ativos do CRM). Histórico altera limite do Profissional a partir da data_abertura — versão condicional abaixo.

1. Tabela de limites de usuários (condicional por data_abertura do chamado):  
   - Para chamados abertos até 30/06/2026:  
     | Plano | Limite de usuários ativos |  
     |---|---:|  
     | Essencial | 2 |  
     | Profissional | 5 |  
     | Empresa | sem limite |  
   - Para chamados abertos a partir de 01/07/2026 (inclusive): (alteração vigente)  
     | Plano | Limite de usuários ativos |  
     |---|---:|  
     | Essencial | 2 |  
     | Profissional | 8 |  
     | Empresa | sem limite |  
   Observação da alteração: a mudança do limite do Profissional vale para "toda regra do manual que usa o limite de usuários do plano"; entretanto, a mudança NÃO altera os limiares de usuários afetados em incidentes técnicos (capítulo 15), que são uma tabela própria.

2. Pedido de adicionar usuários (aplicar primeira verificação: se plano = Empresa → suporte_padrao e parar):  
   - Se plano = Empresa → suporte_padrao (qualquer quantidade).  
   - Caso plano ≠ Empresa: calcular soma = usuarios_ativos (CRM) + quantidade_pedida; comparar com limite aplicável (tabela acima, conforme data_abertura):  
     • soma ≤ limite → suporte_padrao.  
     • soma > limite → oferta_upgrade.  
   Observação: para Profissional com ciclo anual, aplicar exceção de bônus antes de comparar: Profissional anual tem +2 usuários de bônus somados ao limite; ex.: limite_profissional (5 ou 8 conforme data) + 2 → limite efetivo para Profissional anual.

3. Troca de titularidade pedida pelo titular atual → solicitar_documentos (exigir documentos que confirmem identidade do titular atual e dados do novo titular). Se quem pede NÃO é titular atual → isto não pertence a esta área (é segurança → escalar_seguranca; precedência máxima).

4. Remover usuário ou mudar permissão:  
   - Pedido feito por administrador da conta → suporte_padrao (orientar/realizar).  
   - Pedido feito por quem NÃO é administrador → solicitar_documentos (confirmar autorização do titular).

Fronteiras: contar titular entre usuarios_ativos; sempre usar valor usuarios_ativos do CRM (não confiar em contagem do cliente).

---

# Planos e upgrade (capítulo 21)

Verifique campo do CRM (plano, ciclo, usuarios_ativos, cliente_desde, data_abertura) e siga o fluxo do tipo de pedido:

1. Upgrade (ir para plano mais caro) → ajuste_plano (sempre). Observação operacional: cobrança pró-rata é gerada; se cliente depois pedir devolução do pró-rata, aplicar capítulo Reembolso.  
2. Downgrade — duas verificações na ordem:  
   2.1. Se ciclo atual = anual → suporte_padrao (downgrade só na renovação; registrar pedido e data de vigência na renovação) → encerrar.  
   2.2. Se ciclo atual = mensal → comparar usuarios_ativos com limite do plano de destino (usar tabela de limites da seção 20.2, aplicável condicionalmente à data_abertura como na seção 20):  
     - usuarios_ativos > limite_destino → suporte_padrao (orientar desativar usuários até caber no destino).  
     - usuarios_ativos ≤ limite_destino → ajuste_plano (downgrade feito).  
3. Mudança de ciclo sem mudar de plano:  
   - Mensal → Anual → ajuste_plano (mudança feita).  
   - Anual → Mensal → suporte_padrao (só na renovação; registrar pedido e data).  
4. Desconto de fidelidade (sem mudar de plano): se plano ∈ {Profissional, Empresa} E tempo_de_casa ≥ 24 meses (contagem por cliente_desde até data_abertura; comparação ≥) → ajuste_plano (conceder desconto de fidelidade). Caso contrário → suporte_padrao. Nota: Essencial não tem desconto de fidelidade (sempre suporte_padrao).

Fronteiras: mudança para anual não altera dia de vencimento; downgrade anual sempre aguarda renovação.

---

# Alterações vigentes (capítulo 22 — entradas que mudam decisões)

1. Entrada integral (20/02/2026 — Prazo de reembolso do ciclo mensal):  
   "20/02/2026 — Prazo de reembolso do ciclo mensal. Para cobranças do ciclo mensal com data da cobrança a partir de 01/03/2026, o prazo de reembolso das faturas da assinatura passa a ser de 14 dias corridos, em qualquer plano. A mudança não vale para cobranças avulsas de pró-rata de upgrade, que continuam com o prazo próprio do capítulo 19. Cobranças do ciclo mensal com data até 28/02/2026 mantêm o prazo de 7 dias corridos. A forma de contagem não muda (seção 13.5) e os prazos do ciclo anual continuam os da tabela do capítulo 19."  
   Aplicação prática (onde inserido): capítulo Reembolso (passo 3 — Prazo). Data que define vigência: data_da_cobranca. Regras escritas no capítulo Reembolso refletem ambas as versões condicionadas a data_da_cobranca (≤28/02/2026 → 7 dias; ≥01/03/2026 → 14 dias). A alteração não estende a prazos de pró-rata (mantém 7 dias para pró-rata).

2. Entrada integral (15/05/2026 — Prazo de cancelamento de NFS-e):  
   "15/05/2026 — Prazo de cancelamento de NFS-e. Para NFS-e emitidas a partir de 01/06/2026, o prazo para cancelamento orientado passa a ser de 10 dias corridos contados da data de emissão. NFS-e emitidas até 31/05/2026 mantêm o prazo de 5 dias. Como a correção de NFS-e segue o prazo de cancelamento de NFS-e, o novo prazo vale também para ela. Os prazos de NF-e não mudam."  
   Aplicação prática (onde inserido): capítulo Fiscal (passo 4 — Cancelamento de NFS-e e passo 6 — Correção de NFS-e). Data que define vigência: data_de_emissão da NFS-e. Regras no capítulo Fiscal refletem ambas as versões condicionadas a data_de_emissão (≤31/05/2026 → 5 dias; ≥01/06/2026 → 10 dias). A alteração estende também às correções de NFS-e (que seguem o mesmo prazo).

3. Entrada integral (10/06/2026 — Limite de usuários do plano Profissional):  
   "10/06/2026 — Limite de usuários do plano Profissional. Para chamados abertos a partir de 01/07/2026, o limite de usuários do plano Profissional passa de 5 para 8. A mudança vale para toda regra do manual que usa o limite de usuários do plano; no ciclo anual, os usuários de bônus do capítulo 20 continuam sendo somados ao novo limite. Chamados abertos até 30/06/2026 seguem o limite de 5. Os limites do Essencial e do Empresa não mudam. Esta mudança não altera os limiares de usuários afetados em incidentes técnicos (capítulo 15), que são uma tabela própria."  
   Aplicação prática (onde inserido): capítulo Usuários e permissões (tabela de limites e comparação para adicionar/descida), capítulo Planos e downgrade (verificação de usuarios_ativos vs limite do plano de destino). Data que define vigência: data_abertura do chamado. Observações: a alteração aplica-se a "toda regra do manual que usa o limite de usuários do plano" (exceto limiares de incidentes técnicos, inalterados). No ciclo anual, o bônus de +2 usuários para Profissional anual deve ser somado ao novo limite (8) quando aplicável.

(As demais entradas do histórico não alteram regras de decisão de códigos e foram omitidas.)

