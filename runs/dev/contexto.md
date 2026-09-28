# Triagem e regras gerais
1. Cada chamado recebe exatamente um código de ação; quando o cliente traz vários assuntos, escolha o assunto de maior precedência abaixo e registre o código correspondente (um único código).  
2. Precedência entre assuntos — da maior para a menor (aplique na ordem):  
   1) Segurança (capítulo 14)  
   2) Incidente técnico crítico (capítulo 15; ver definição em 3)  
   3) Fiscal (capítulo 16)  
   4) Privacidade / LGPD (capítulo 17)  
   5) Cancelamento e retenção (capítulo 18)  
   6) Reembolso (capítulo 19)  
   7) Usuários e permissões (capítulo 20)  
   8) Planos e upgrade (capítulo 21)  
   9) Incidente técnico não crítico (capítulo 15)  
   10) Dúvida de uso  
   - Observação: “Incidente técnico crítico” = aplique as regras do capítulo 15 ao problema técnico; se o resultado for escalar_engenharia, o incidente é crítico (posição 2); se não for, é não crítico (posição 9).  
3. Mensagem sem pedido acionável (spam, propaganda, teste de formulário, texto sem sentido) e sem outro assunto real → descartar.  
4. Dúvida de uso (pergunta sobre como fazer algo que o sistema já faz, sem relato de falha e sem se encaixar nas áreas 14–21) → suporte_padrao.  
5. Contagem de dias (prazo em dias): dias corridos, contados a partir do dia seguinte à data de referência; o último dia conta. Condição de verificação: calcule (data_abertura − data_referência) em dias; se menor ou igual ao prazo, está dentro. Exemplo telegráfico: referência 10/02/2026, prazo 7 dias → 17/02/2026 ainda dentro.  
6. Contagem de meses de casa: conte a partir do campo cliente_desde; o cliente completa N meses no mesmo dia do mês, N meses depois. Se o dia não existe no mês de destino, vale o dia 1 do mês seguinte. Exemplo telegráfico: cliente_desde 31/01 → 1º dia do mês seguinte em meses subsequentes.  
7. Campos decisórios do CRM (use sempre a lateral do CRM, não a alegação do cliente): plano, ciclo, cliente_desde (DD/MM/AAAA), data_abertura (DD/MM/AAAA), reembolsos_12m (inteiro), usuarios_ativos (inteiro), cobranca (DD/MM/AAAA e R$).  

---

# Segurança (capítulo 14)
Percorra a lista nesta ordem; pare na primeira condição que for verdadeira.

1. Exceção por plano (ver FAQ): se o pedido for reset de 2FA e o plano for Empresa → escalar_seguranca.  
2. Acesso desconhecido à conta (login/alerta/usuário não reconhecido / ações no histórico que o cliente não fez) → escalar_seguranca.  
3. Alteração não reconhecida dos dados bancários de recebimento (cliente diz que nem ele nem alguém da equipe fez a alteração) → escalar_seguranca.  
4. Reset da autenticação em dois fatores (quando não se aplica a exceção por plano):  
   - pedido feito pelo próprio titular da conta → suporte_padrao  
   - pedido feito por outra pessoa (não titular) → escalar_seguranca  
5. Troca de titularidade pedida por quem não é o titular atual → escalar_seguranca.  
6. E-mail suspeito em nome da Orbita:  
   - se o cliente clicou no link ou informou dados → escalar_seguranca  
   - se não clicou nem informou dados → suporte_padrao  
7. Perda ou roubo de celular com app da Orbita logado:  
   - plano Empresa → escalar_seguranca  
   - planos Essencial ou Profissional → suporte_padrao

---

# Incidentes técnicos (capítulo 15)
Aplique estas verificações sempre nesta ordem; pare na primeira que se aplicar.

1. O problema afeta a emissão de notas fiscais (NF-e ou NFS-e: transmissão, notas presas em "processando", rejeições generalizadas, falha de comunicação com prefeitura/SEFAZ)? → escalar_engenharia.  
2. Falha em integração (API ou webhooks):  
   - se o plano do cliente for Essencial → oferta_upgrade  
   - se o plano for Profissional ou Empresa → escalar_engenharia  
   - nota: se a falha de integração também impede emissão de notas, passo 1 prevalece.  
3. Plano Empresa (qualquer problema técnico relatado em conta Empresa) → escalar_engenharia.  
4. Número de usuários afetados >= limiar do plano (conte pelos usuários afetados relatados; se incerto, pergunte): tabela de limiares (verificação 4)  
   | Plano | Limiar de usuários afetados | Ação se number >= limiar |
   |---|---:|---|
   | Essencial | 2 | escalar_engenharia |
   | Profissional | 5 | escalar_engenharia |
   | Empresa | não se aplica (decidido no passo 3) | não se aplica |
   - condição exata: “igual ou maior” (>= limiar) → escalar_engenharia.  
   - Observação: os limiares desta tabela são próprios de incidentes técnicos e NÃO mudam com alterações no limite de usuários do plano (histórico registra que limiares permanecem).  
5. Exceção complementar para Profissional: se todos os usuários ativos da conta estão afetados e usuarios_ativos (campo CRM) >= 3 → escalar_engenharia (mesmo que count < limiar da tabela).  
6. Demais casos (nenhuma das anteriores se aplicou) → suporte_padrao.

---

# Fiscal — notas emitidas pelo cliente (capítulo 16)
Siga a ordem; a referência de prazo é a data de emissão da nota (use o campo da nota); contagem de dias conforme seção 13.5.

1. Identificar tipo de nota: NF-e (produto) ou NFS-e (serviço) — confira no CRM pela coluna "modelo".  
2. Identificar tipo de pedido: cancelamento ou correção.  
3. Cancelamento de NF-e: se (data_abertura − data_emissão) ≤ 1 dia → nf_cancelamento_orientado; se > 1 dia → fiscal_analise.  
4. Cancelamento de NFS-e: (prazo sujeito à alteração histórica) — versão aplicada:  
   - NFS-e emitida até 31/05/2026: se (data_abertura − data_emissão) ≤ 5 dias → nf_cancelamento_orientado; se > 5 dias → fiscal_analise.  
   - NFS-e emitida a partir de 01/06/2026: se (data_abertura − data_emissão) ≤ 10 dias → nf_cancelamento_orientado; se > 10 dias → fiscal_analise.  
   - Observação: correção de NFS-e segue o mesmo prazo de cancelamento de NFS-e (a alteração estende-se às correções de NFS-e).  
5. Correção de NF-e — verifique o campo que o cliente quer corrigir, nesta ordem:  
   a) Se correção envolve valor ou imposto (valor unitário, quantidade que altera total, alíquota, base de cálculo, desconto) → fiscal_analise (independente de prazo).  
   b) Se correção envolve CPF ou CNPJ do destinatário → fiscal_analise (independente de prazo).  
   c) Se é outro dado cadastral passível de Carta de Correção (endereço, razão social, descrição do produto) → aplicar prazo da carta: se (data_abertura − data_emissão) ≤ 30 dias → nf_carta_correcao; se > 30 dias → fiscal_analise.  
6. Correção de NFS-e: não existe carta de correção para NFS-e; correção = cancelar e reemitir. Aplique o prazo de cancelamento de NFS-e do passo 4 para decidir: dentro → nf_cancelamento_orientado; fora → fiscal_analise.  
7. Observação de autoridade de data: sempre use a data de emissão registrada na nota (não a alegada pelo cliente) para aplicar prazos.

---

# Privacidade e LGPD (capítulo 17)
Siga a ordem; pare na primeira que se aplicar.

1. Pedido feito por terceiro (cliente final do usuário falando dos próprios dados do controlador) → suporte_padrao.  
2. Reclamação de pedido anterior sem resposta: calcule dias entre data do pedido anterior e data_abertura.  
   - se > 15 dias → encaminhar_dpo  
   - se ≤ 15 dias → suporte_padrao  
   - (contagem conforme seção 13.5).  
3. Exportação de dados pelo titular da conta → solicitar_documentos (exigir confirmação de identidade: documento oficial com foto; para pessoa jurídica, contrato social ou documento de representação).  
   - Exceção: no plano Empresa, o titular pode gerar a exportação pelo painel (Configurações > Privacidade > Exportar dados) → suporte_padrao (orientar o caminho no painel); esta exceção vale só para exportação.  
4. Exclusão de dados pelo titular: verificar notas emitidas nos últimos 5 anos (referência: aba Notas emitidas no CRM):  
   - se emitiu notas fiscais pela Orbita nos últimos 5 anos → encaminhar_dpo  
   - se não emitiu notas fiscais pela Orbita nos últimos 5 anos → solicitar_documentos (confirmar identidade antes de executar exclusão)  
   - condição exata: “nos últimos 5 anos” contados até data_abertura; confira o filtro de período no CRM.  
5. Correção dos próprios dados cadastrais pelo titular (e-mail, telefone, endereço) → suporte_padrao (não pedir documentos).

---

# Cancelamento e retenção (capítulo 18)
Aplique as verificações exatamente nesta ordem; pare na primeira que decidir.

1. Fechamento da empresa (baixa do CNPJ, encerramento das atividades, fechamento do estabelecimento) → cancelamento_direto (independente de plano, ciclo, tempo de casa ou histórico).  
2. Recusa anterior de oferta de retenção: antes de oferecer retenção, verifique histórico.  
   - se houve recusa anterior de oferta de retenção e tal recusa foi feita há ≤ 180 dias (contados até data_abertura) → cancelamento_direto.  
   - se recusa anterior foi feita há > 180 dias → **desconsidera recusa antiga** e continue a ordem normalmente.  
3. Plano Essencial: (após passos 1 e 2)  
   - regra geral: se plano = Essencial → cancelamento_direto (sem oferta)  
   - exceção: Essencial no ciclo anual com tempo de casa ≥ 24 meses (cliente_desde → data_abertura, ver seção 13.6) → oferta_retencao.  
4. Motivo "preço" e plano Profissional: se motivo declarado = preço e plano = Profissional → oferta_retencao (independente do tempo de casa). (Se plano = Empresa, o motivo preço não decide aqui; continue.)  
5. Tempo de casa (aplica-se agora apenas a clientes Profissional e Empresa que chegaram até aqui): comparar cliente_desde → data_abertura (seção 13.6):  
   | Plano | Tempo mínimo para oferta_retencao |
   |---|---:|
   | Profissional | 12 meses |
   | Empresa | 6 meses |
   - se tempo de casa ≥ mínimo do plano → oferta_retencao  
   - se tempo de casa < mínimo do plano → cancelamento_direto  
   - observação: completar exatamente o mínimo no dia da abertura conta como atingido.

---

# Reembolso (capítulo 19)
Aplique as verificações nesta ordem; a referência de prazo é a data da cobrança; contagem conforme seção 13.5.

1. Cobrança duplicada (duas cobranças iguais pelo mesmo período) → reembolso_automatico (ignora as demais verificações; vale independentemente de plano, prazo, histórico e valor).  
2. Plano Empresa → reembolso_com_analise (aplica-se após verificar duplicidade; duplicidade ainda devolvida automaticamente).  
3. Prazo — tabela (referência: data da cobrança). ATENÇÃO: alteração histórica sobre ciclo mensal; aplicar conforme data da cobrança:  
   | Tipo de cobrança | Ciclo e plano | Prazo para pedir reembolso |
   |---|---|---:|
   | Fatura da assinatura | Ciclo mensal, cobranças com data até 28/02/2026 | 7 dias |
   | Fatura da assinatura | Ciclo mensal, cobranças com data a partir de 01/03/2026 | 14 dias |
   | Fatura da assinatura | Ciclo anual, plano Essencial | 15 dias |
   | Fatura da assinatura | Ciclo anual, plano Profissional | 30 dias |
   - se pedido estiver fora do prazo aplicável → negar_reembolso  
   - observação: cobranças avulsas de pró-rata de upgrade têm prazo próprio (exceção abaixo).  
4. Histórico de reembolsos (campo reembolsos_12m):  
   - regra geral: se reembolsos_12m ≥ 2 → reembolso_com_analise (aplica-se somente após passar por duplicidade, passo 2 e prazo)  
   - exceção para clientes com ≥ 36 meses de casa (cliente_desde → data_abertura): só enviar para análise se reembolsos_12m ≥ 3 (ou seja, para ≥36 meses de casa, limiar de análise por histórico = 3).  
5. Valor / teto de aprovação automática (antes de aprovar automaticamente, compare o valor com o teto): tabela de tetos (passo 5 nota)  
   | Plano | Ciclo | Teto de aprovação automática |
   |---|---|---:|
   | Essencial | Mensal ou anual | R$ 200,00 |
   | Profissional | Mensal | R$ 300,00 |
   | Profissional | Anual | R$ 1.000,00 |
   - condição: se valor da cobrança > teto (estritamente maior) → reembolso_com_analise; se valor ≤ teto → segue para aprovação automática.  
6. Aprovação automática (última verificação): se passou por todos os passos anteriores sem ser decidido → reembolso_automatico.  
7. Exceção pró-rata (FAQ): cobrança avulsa de pró-rata de upgrade → prazo de 7 dias, em qualquer ciclo e plano (referência: data da cobrança). Aplicar passos 1,2,4,5 depois de verificar o prazo do pró-rata.

---

# Usuários e permissões (capítulo 20)
Ordem por tipo de pedido; usar usuarios_ativos do CRM; quando aplicar limites, considere histórico de alteração de limites (ver seção Alterações vigentes).

1. Pedido de adicionar usuários — verificação em ordem:  
   a) Se plano = Empresa → suporte_padrao (sem limite).  
   b) Se plano ≠ Empresa: calcule soma = usuarios_ativos (CRM) + quantidade_pedida; compare com limite do plano (tabela oficial, podendo haver alteração por data): tabela de limite oficial (aplicável conforme data de abertura do chamado):  
      | Plano | Limite de usuários ativos |
      |---|---:|
      | Essencial | 2 |
      | Profissional (versão pré-01/07/2026) | 5 |
      | Profissional (a partir de 01/07/2026 para chamados abertos nessa data ou depois) | 8 |
      | Empresa | sem limite |
      - Exceção: Profissional no ciclo anual recebe +2 usuários de bônus ao limite acima (aplicar o bônus ao limite vigente conforme a data do chamado).  
      - Ação: se soma ≤ limite (após aplicar bônus quando for o caso) → suporte_padrao; se soma > limite → oferta_upgrade.  
2. Troca de titularidade:  
   - pedido feito pelo titular atual → solicitar_documentos (exigir documentos que comprovem identidade do titular atual e dados do novo titular)  
   - pedido feito por quem não é o titular atual → encaminhar_seguranca (assunto de segurança; não é desta área)  
3. Remoção de usuário ou mudança de permissão:  
   - pedido feito por administrador da conta → suporte_padrao (orientar ou executar pelo painel)  
   - pedido feito por quem não é administrador → solicitar_documentos (confirmar autorização do titular antes de executar)

---

# Planos e upgrade (capítulo 21)
Siga a sequência conforme tipo de pedido.

1. Upgrade (mudar para plano superior) → ajuste_plano (sempre). (Cobrança pró-rata aplicada automaticamente; se o cliente depois pedir devolução do pró-rata, trata-se de reembolso — capítulo 19.)  
2. Downgrade — duas etapas:  
   a) Se ciclo atual = anual → suporte_padrao (downgrade só ocorre na renovação; registre pedido e data de vigência na renovação).  
   b) Se ciclo atual = mensal → compare usuarios_ativos com limite do plano de destino (use tabela de limites vigente na data_abertura, incluindo bônus do Profissional anual e alteração de limite a partir de 01/07/2026):  
      - se usuarios_ativos > limite_do_destino → suporte_padrao (orientar desativar usuários; depois o cliente pode pedir downgrade de novo)  
      - se usuarios_ativos ≤ limite_do_destino → ajuste_plano (downgrade executado)  
3. Mudança de ciclo sem mudar de plano:  
   - de mensal para anual → ajuste_plano (muda na hora)  
   - de anual para mensal → suporte_padrao (só na renovação)  
4. Desconto de fidelidade (sem mudar de plano):  
   - se plano = Profissional ou Empresa e tempo de casa ≥ 24 meses → ajuste_plano (conceder desconto de fidelidade)  
   - caso contrário → suporte_padrao (explicar política; Essencial nunca tem desconto)

---

# Alterações vigentes (entradas do histórico que mudam prazos/limites/tabelas — texto integral de cada entrada)
- 20/02/2026 — Prazo de reembolso do ciclo mensal.  
  "Para cobranças do ciclo mensal com data da cobrança a partir de 01/03/2026, o prazo de reembolso das faturas da assinatura passa a ser de 14 dias corridos, em qualquer plano. A mudança não vale para cobranças avulsas de pró-rata de upgrade, que continuam com o prazo próprio do capítulo 19. Cobranças do ciclo mensal com data até 28/02/2026 mantêm o prazo de 7 dias corridos. A forma de contagem não muda (seção 13.5) e os prazos do ciclo anual continuam os da tabela do capítulo 19."

- 15/05/2026 — Prazo de cancelamento de NFS-e.  
  "Para NFS-e emitidas a partir de 01/06/2026, o prazo para cancelamento orientado passa a ser de 10 dias corridos contados da data de emissão. NFS-e emitidas até 31/05/2026 mantêm o prazo de 5 dias. Como a correção de NFS-e segue o prazo de cancelamento de NFS-e, o novo prazo vale também para ela. Os prazos de NF-e não mudam."

- 10/06/2026 — Limite de usuários do plano Profissional.  
  "Para chamados abertos a partir de 01/07/2026, o limite de usuários do plano Profissional passa de 5 para 8. A mudança vale para toda regra do manual que usa o limite de usuários do plano; no ciclo anual, os usuários de bônus do capítulo 20 continuam sendo somados ao novo limite. Chamados abertos até 30/06/2026 seguem o limite de 5. Os limites do Essencial e do Empresa não mudam. Esta mudança não altera os limiares de usuários afetados em incidentes técnicos (capítulo 15), que são uma tabela própria."

(essas três entradas prevalecem sobre os textos dos capítulos; na aplicação das regras acima as versões e condições de data foram incorporadas.)