# Regras gerais de triagem (cap. 13)

1. Cada chamado recebe exatamente um código de ação; quando há vários assuntos, registre apenas o código do assunto de maior precedência (seção 13.1) → (um único código).
2. Precedência entre assuntos (maior → menor) — aplicar nesta ordem para decidir qual assunto comanda o chamado:
   1. Segurança (cap. 14)
   2. Incidente técnico crítico (cap. 15; só quando a aplicação das regras de cap.15 termina em escalar_engenharia)
   3. Fiscal (cap. 16)
   4. Privacidade / LGPD (cap. 17)
   5. Cancelamento e retenção (cap. 18)
   6. Reembolso (cap. 19)
   7. Usuários e permissões (cap. 20)
   8. Planos e upgrade (cap. 21)
   9. Incidente técnico não crítico (cap. 15)
   10. Dúvida de uso → suporte_padrao
3. Mensagens sem pedido acionável (spam, propaganda, texto sem sentido) e sem qualquer outro assunto → descartar.
4. Dúvida de uso (sistema já faz o que o cliente pergunta, sem relato de falha e sem entrada nas áreas 14–21) → suporte_padrao.
5. Contagem de prazos em dias: prazos em dias corridos, contados a partir do dia seguinte à data de referência (ex.: prazo de 7 dias contado da data da cobrança). O último dia conta; comparar: (data_abertura − data_referência) ≤ prazo → dentro.
   - Exemplo curto: referência 10/02/2026, prazo 7 dias → último dia 17/02/2026; chamado em 17/02/2026 está dentro.
6. Contagem de meses de casa: conta-se desde cliente_desde; o cliente completa N meses no mesmo dia do mês N meses depois; se o dia não existe no mês de destino (ex.: 31/01), vale o dia 1 do mês seguinte (seção 13.6).
7. Antes de aplicar qualquer tabela de prazos, limites ou tetos, conferir o capítulo 22 por alterações vigentes; se houver alteração que afeta a regra, aplicar a versão cuja condição temporal (data da cobrança, data de emissão, data_abertura do chamado) determine vigência.

---

# Segurança (cap. 14) — ordem das verificações (percorrer nesta ordem; pare na primeira que corresponder)

1. Se o cliente relata acesso desconhecido à conta (login/alerta/usuário/ações no histórico não reconhecidas) → escalar_seguranca.
2. Se o cliente relata alteração não reconhecida dos dados bancários de recebimento (alteração já ocorrida, não pedido de cadastrar) → escalar_seguranca.
3. Reset de dois fatores — verificar exceção por plano ANTES da tabela:
   1. Se o plano da conta é Empresa → escalar_seguranca.
   2. Caso contrário: se o pedido é feito pelo próprio titular da conta → suporte_padrao.
   3. Caso contrário (pedido feito por outra pessoa) → escalar_seguranca.
4. Troca de titularidade pedida por quem NÃO é o titular atual → escalar_seguranca.
5. E-mail suspeito em nome da Orbita:
   - Se o cliente clicou no link ou informou dados após o e-mail → escalar_seguranca.
   - Se o cliente não clicou nem informou dados → suporte_padrao.
6. Perda ou roubo de celular com o app da Orbita logado:
   - Se o plano é Empresa → escalar_seguranca.
   - Se o plano é Essencial ou Profissional → suporte_padrao.
7. Se não se encaixa em nenhuma das situações acima → não é caso de segurança (voltar à triagem geral).

---

# Incidentes técnicos (cap. 15) — ordem das verificações (parar na primeira aplicável)

1. Se o problema AFETA a emissão de notas fiscais (NF-e ou NFS-e: erros de transmissão, notas presas em "processando", rejeições generalizadas, falha de comunicação com prefeitura/SEFAZ) → escalar_engenharia.
2. Se é falha em integração (API ou webhooks):
   - Se o plano é Essencial → oferta_upgrade.
   - Se o plano é Profissional ou Empresa → escalar_engenharia.
   - (Nota: se também afeta emissão de notas, passo 1 já decidiu).
3. Se o plano é Empresa (qualquer problema técnico) → escalar_engenharia.
4. Número de usuários afetados ≥ limiar do plano → escalar_engenharia, com a tabela abaixo (contar usuários afetados pelo relato; se incerto, perguntar antes):

| Plano | Limiar de usuários afetados |
|---|---|
| Essencial | 2 |
| Profissional | 5 |
| Empresa | não se aplica |

5. Exceção do Profissional (verificação complementar): se o plano é Profissional e TODOS os usuários ativos da conta estão afetados e usuarios_ativos ≥ 3 → escalar_engenharia.
6. Se nenhuma das anteriores se aplicou → suporte_padrao.

---

# Fiscal — notas emitidas pelo cliente (cap. 16) — ordem das verificações (referência: data de emissão da nota; contagem de dias conforme 13.5)

1. Identificar tipo de nota: NF-e (modelo 55) OU NFS-e (municipal).
2. Identificar tipo de pedido: cancelamento OU correção.
3. Cancelamento de NF-e:
   - Se (data_abertura − data_emissão) ≤ 1 dia → nf_cancelamento_orientado.
   - Se (data_abertura − data_emissão) > 1 dia → fiscal_analise.
4. Cancelamento de NFS-e — prazo depende da data de emissão da NFS-e:
   - Se data_emissão da NFS-e ≤ 31/05/2026: prazo = 5 dias; se (data_abertura − data_emissão) ≤ 5 dias → nf_cancelamento_orientado; se > 5 dias → fiscal_analise.
   - Se data_emissão da NFS-e ≥ 01/06/2026: prazo = 10 dias; se (data_abertura − data_emissão) ≤ 10 dias → nf_cancelamento_orientado; se > 10 dias → fiscal_analise.
5. Correção de NF-e — verificar o campo que se quer corrigir (esta verificação vem antes de qualquer prazo):
   - Se o cliente quer corrigir VALOR ou IMPOSTO (valor unitário, quantidade que altera total, alíquota, base, desconto) → fiscal_analise (qualquer prazo).
   - Senão, se o cliente quer corrigir CPF ou CNPJ do destinatário → fiscal_analise (qualquer prazo).
   - Senão (erro em outro dado cadastral corrigível por carta de correção): se (data_abertura − data_emissão) ≤ 30 dias → nf_carta_correcao; se > 30 dias → fiscal_analise.
6. Correção de NFS-e:
   - Não existe carta de correção para NFS-e; correção = cancelar e reemitir. Aplica-se o prazo de cancelamento de NFS-e (ver passo 4): dentro do prazo → nf_cancelamento_orientado; fora → fiscal_analise.

---

# Privacidade e LGPD (cap. 17) — ordem das verificações (parar na primeira aplicável)

1. Pedido feito por TERCEIRO (cliente final do usuário da Orbita, pedindo sobre seus próprios dados que a empresa do usuário controla) → suporte_padrao.
2. Reclamação por pedido de privacidade anterior sem resposta:
   - Se (data_abertura − data_pedido_anterior) > 15 dias → encaminhar_dpo.
   - Se (data_abertura − data_pedido_anterior) ≤ 15 dias → suporte_padrao.
3. Exportação de dados pedida pelo TITULAR da conta:
   - Exceção: se plano = Empresa → exportação feita pelo próprio cliente no painel → suporte_padrao.
   - Caso contrário → solicitar_documentos (exigir confirmação de identidade: documento com foto; para pessoa jurídica, contrato social ou documento de representação) antes de gerar exportação.
4. Exclusão de dados pedida pelo TITULAR da conta:
   - Se o titular emitiu notas fiscais pela Orbita nos últimos 5 anos → encaminhar_dpo.
   - Se não emitiu notas fiscais nos últimos 5 anos → solicitar_documentos (confirmar identidade) antes de proceder.
   - (Verificar Notas emitidas no CRM para decidir.)
5. Correção dos próprios dados cadastrais (e-mail, telefone, endereço) pedida pelo TITULAR → suporte_padrao.
6. Se não se aplica nenhuma das acima → registrar e seguir instruções do DPO / escalonamento conforme nota interna.

---

# Cancelamento e retenção (cap. 18) — ordem das verificações (parar na primeira aplicável)

1. Fechamento da empresa (baixa do CNPJ, encerramento de atividades, fechamento de estabelecimento) → cancelamento_direto.
2. Recusa anterior de oferta de retenção (ver histórico do cliente):
   - Se existiu recusa anterior E (data_abertura − data_recusa_anterior) ≤ 180 dias → cancelamento_direto.
   - Se existiu recusa anterior E (data_abertura − data_recusa_anterior) > 180 dias → ignorar recusa antiga e continuar avaliação normal.
3. Plano Essencial:
   - Regra geral: se plano = Essencial → cancelamento_direto.
   - Exceção: se plano = Essencial, ciclo = anual E tempo de casa ≥ 24 meses (contados por cliente_desde até data_abertura, conforme 13.6) → oferta_retencao.
4. Motivo "preço" e plano Profissional:
   - Se motivo declarado pelo cliente = preço E plano = Profissional → oferta_retencao (independentemente do tempo de casa).
5. Tempo de casa (última verificação; só para clientes Profissional e Empresa que chegaram até aqui):
   - Se plano = Profissional E tempo de casa ≥ 12 meses → oferta_retencao; se < 12 meses → cancelamento_direto.
   - Se plano = Empresa E tempo de casa ≥ 6 meses → oferta_retencao; se < 6 meses → cancelamento_direto.

---

# Reembolso (cap. 19) — ordem das verificações (referência: data da cobrança; contagem conforme 13.5)

1. Cobrança duplicada (dois lançamentos iguais para a mesma coisa; inclui pagamento por boleto e Pix da mesma fatura) → reembolso_automatico (ignora todas as demais verificações; aplica-se inclusive para plano Empresa e fora de prazo).
2. Plano Empresa → reembolso_com_analise (aplica-se após verificar duplicidade; Empresa não recebe negar_reembolso por prazo).
3. Prazo (comparar data_abertura − data_da_cobrança; se fora do prazo → negar_reembolso), tabela com condicionais por data da cobrança:
   - Para cobranças do tipo Fatura da assinatura:
     - Se ciclo = mensal:
       - Se data_da_cobrança ≤ 28/02/2026 → prazo = 7 dias.
       - Se data_da_cobrança ≥ 01/03/2026 → prazo = 14 dias.
     - Se ciclo = anual e plano = Essencial → prazo = 15 dias.
     - Se ciclo = anual e plano = Profissional → prazo = 30 days.
   - Cobranças avulsas de pró-rata de upgrade → prazo = 7 dias (qualquer ciclo e plano).
   - Se pedido estiver fora do prazo aplicável → negar_reembolso.
4. Histórico de reembolsos (aplicado só se não é duplicada e passou passo 2 e 3):
   - Se cliente_desde < 36 meses:
     - Se reembolsos_12m ≥ 2 → reembolso_com_analise.
   - Se cliente_desde ≥ 36 meses:
     - Se reembolsos_12m ≥ 3 → reembolso_com_analise.
     - Se reembolsos_12m ≤ 2 → não enviar por histórico; prosseguir.
5. Valor / teto de aprovação automática (antes de aprovar automaticamente, conferir teto; se valor > teto → reembolso_com_analise). Teto depende de plano, ciclo e data_abertura do chamado (condicional aplicada ao plano Essencial):
   - Se data_abertura do chamado ≥ 01/03/2026:
     - Essencial (qualquer ciclo): teto = R$ 50,00.
   - Se data_abertura do chamado ≤ 29/02/2026:
     - Essencial (qualquer ciclo): teto = R$ 200,00.
   - Profissional:
     - Mensal: teto = R$ 300,00.
     - Anual: teto = R$ 1.000,00.
   - (Cobrança duplicada ignora teto; Empresa já foi enviada para análise no passo 2.)
   - Comparação: se valor da cobrança estritamente maior que teto (valor > teto) → reembolso_com_analise; se valor ≤ teto → segue.
6. Aprovação automática final:
   - Se passou todos os passos anteriores (não duplicada, não Empresa, dentro do prazo, histórico não mandou para análise e valor ≤ teto) → reembolso_automatico.
7. Quando o pedido foi decidido como fora do prazo no passo 3 → negar_reembolso.
8. Observações de contagem e referências: data de referência = data da cobrança; a contagem de dias segue 13.5.

---

# Usuários e permissões (cap. 20) — sequência por tipo de pedido

1. Pedido de ADICIONAR USUÁRIOS — verificações nesta ordem:
   1. Se plano = Empresa → suporte_padrao (sem limite).
   2. Determinar limite aplicável:
      - Se data_abertura do chamado ≥ 01/07/2026 → limite base do Profissional = 8; senão Profissional = 5. Essencial = 2; Empresa = sem limite.
      - Exceção do ciclo anual: se plano = Profissional e ciclo = anual → adicionar bônus de +2 usuários ao limite base do Profissional (o bônus é somado ao novo limite, quando aplicável).
   3. Calcular soma = usuarios_ativos (campo CRM) + quantidade de usuários pedida.
      - Se soma ≤ limite aplicável → suporte_padrao.
      - Se soma > limite aplicável → oferta_upgrade.
2. Troca de titularidade pedida pelo titular atual → solicitar_documentos (pedir documentos que comprovem identidade do titular atual e dados do novo titular).
   - Troca pedida por quem NÃO é titular → NÃO é assunto desta área (é segurança → escalar_seguranca; precedência do cap.14).
3. Remoção de usuário ou mudança de permissão:
   - Se pedido feito por ADMINISTRADOR da conta → suporte_padrao.
   - Se pedido feito por quem NÃO é administrador → solicitar_documentos (confirmar autorização do titular).

---

# Planos e upgrade (cap. 21) — sequência por tipo de pedido

1. Upgrade (ir para plano mais caro) → ajuste_plano (qualquer plano de origem, qualquer ciclo; cobrança pró-rata no momento).
2. Downgrade — duas verificações em ordem:
   1. Se ciclo atual = anual → suporte_padrao (downgrade só na renovação; registrar pedido e informar data de vigência na renovação).
   2. Se ciclo atual = mensal → comparar usuarios_ativos com LIMITE do plano de destino (usar a mesma tabela de limites do cap.20, considerando a alteração de limite do Profissional em vigor por data_abertura: Profissional = 8 se chamado aberto ≥ 01/07/2026, senão 5; incluir bônus +2 se Profissional anual quando aplicável para comparações que envolvam ciclo anual de destino):
      - Se usuarios_ativos > limite do plano de destino → suporte_padrao (orientar a desativação de usuários antes de realizar downgrade).
      - Se usuarios_ativos ≤ limite do plano de destino → ajuste_plano (downgrade feito).
3. Mudança de ciclo (sem mudar de plano):
   - De mensal para anual → ajuste_plano (mudar para anual agora, cobrança da anuidade conforme fluxo).
   - De anual para mensal → suporte_padrao (a mudança só ocorre na renovação; registrar pedido e informar data).
4. Desconto de fidelidade sem mudar de plano:
   - Se plano = Profissional OU Empresa E tempo de casa ≥ 24 meses (cliente_desde até data_abertura, conforme 13.6) → ajuste_plano.
   - Caso contrário → suporte_padrao.
5. Dúvida sobre preço (informar tabela) → suporte_padrao.

---

# Alterações vigentes (cap. 22 — textos integrais que mudam prazos, limites ou tetos; prevalecem sobre capítulos)

**20/02/2026 — Prazo de reembolso do ciclo mensal.**  
Para cobranças do ciclo mensal com data da cobrança a partir de 01/03/2026, o prazo de reembolso das faturas da assinatura passa a ser de 14 dias corridos, em qualquer plano. A mudança não vale para cobranças avulsas de pró-rata de upgrade, que continuam com o prazo próprio do capítulo 19. Cobranças do ciclo mensal com data até 28/02/2026 mantêm o prazo de 7 dias corridos. A forma de contagem não muda (seção 13.5) e os prazos do ciclo anual continuam os da tabela do capítulo 19.

**15/05/2026 — Prazo de cancelamento de NFS-e.**  
Para NFS-e emitidas a partir de 01/06/2026, o prazo para cancelamento orientado passa a ser de 10 dias corridos contados da data de emissão. NFS-e emitidas até 31/05/2026 mantêm o prazo de 5 dias. Como a correção de NFS-e segue o prazo de cancelamento de NFS-e, o novo prazo vale também para ela. Os prazos de NF-e não mudam.

**10/06/2026 — Limite de usuários do plano Profissional.**  
Para chamados abertos a partir de 01/07/2026, o limite de usuários do plano Profissional passa de 5 para 8. A mudança vale para toda regra do manual que usa o limite de usuários do plano; no ciclo anual, os usuários de bônus do capítulo 20 continuam sendo somados ao novo limite. Chamados abertos até 30/06/2026 seguem o limite de 5. Os limites do Essencial e do Empresa não mudam. Esta mudança não altera os limiares de usuários afetados em incidentes técnicos (capítulo 15), que são uma tabela própria.

**25/09/2026 — Teto de aprovação automática do plano Essencial.**  
Para chamados abertos a partir de 01/03/2026, o teto de aprovação automática de reembolso do plano Essencial, em qualquer ciclo, passa de R$ 200,00 para R$ 50,00. Os tetos do plano Profissional não mudam, e a cobrança duplicada continua fora dessa verificação.

---