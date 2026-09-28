# Regras gerais de triagem (capítulo 13)

1. Um chamado recebe exatamente um código de ação (lista fechada de 16 códigos).
2. Precedência entre assuntos (decide qual assunto comanda quando há >1 assunto; ordem da maior para a menor):
   1. Segurança (capítulo 14)
   2. Incidente técnico crítico (capítulo 15) — definição especial abaixo
   3. Fiscal (capítulo 16)
   4. Privacidade e LGPD (capítulo 17)
   5. Cancelamento e retenção (capítulo 18)
   6. Reembolso (capítulo 19)
   7. Usuários e permissões (capítulo 20)
   8. Planos e upgrade (capítulo 21)
   9. Incidente técnico não crítico (capítulo 15)
   10. Dúvida de uso
   - Observação de fronteira: aplique as regras do capítulo 15 ao problema técnico; se o resultado for escalar_engenharia, trate-o como "incidente técnico crítico" (posição 2). Se não, trata-se de incidente técnico não crítico (posição 9).
   - Troca de titularidade pedida por quem não é titular é assunto de segurança e vence tudo (cap. 14.6).
3. Mensagens sem pedido acionável → código: descartar.
4. Dúvida de uso (como fazer algo que o sistema já faz, sem relato de falha e sem se encaixar nas áreas 14–21) → código: suporte_padrao.
5. Contagem de dias (prazos em dias corridos):
   - Prazos em dias são contados em dias corridos a partir do dia seguinte à data de referência (ex.: data da cobrança, data de emissão da nota, data do pedido anterior).
   - O último dia do prazo conta: se (data_abertura − data_referência) ≤ prazo → dentro.
   - Exemplo dado no manual: referência 10/02/2026, prazo 7 dias → último dia 17/02/2026; chamado aberto em 17/02/2026 está dentro.
6. Contagem de meses de casa:
   - Tempo contado a partir de cliente_desde até data_abertura. Completa N meses no mesmo dia do mês N meses depois.
   - Se o dia não existe no mês de destino (ex.: 31/01), vale o dia 1 do mês seguinte.
   - Exemplo: cliente_desde 10/03/2025 → 12 meses completos em 10/03/2026; em 09/03/2026 ainda não tem 12 meses.

# Segurança (capítulo 14) — ordem das verificações e ações

Percorra nesta ordem; pare na primeira que corresponder ao relato:

1. Acesso desconhecido à conta (14.3)
   - Condição: relato de login não reconhecido, alerta de novo acesso de cidade/dispositivo estranho, usuário conectado que ninguém criou, ações no histórico que ninguém fez.
   - Ação: escalar_seguranca.
   - Fronteira: independente de plano e de ações já tomadas pelo cliente (troca de senha não impede escalonamento).
2. Alteração não reconhecida dos dados bancários de recebimento (14.4)
   - Condição: cliente relata que os dados bancários de recebimento foram alterados e nem ele nem alguém da equipe fez a alteração.
   - Ação: escalar_seguranca.
   - Fronteira: cadastrar nova conta de recebimento sem relato de alteração não reconhecida = dúvida de uso (suporte_padrao).
3. Reset de dois fatores (14.5)
   - Primeiro verifique a exceção por plano (seção 14.9 — Empresa).
   - Tabela (aplicar depois de checar exceção Empresa):
     | Quem faz o pedido | Ação |
     |---|---|
     | O próprio titular da conta | suporte_padrao |
     | Outra pessoa (não titular) | escalar_seguranca |
   - Observação: pedido por terceiro é sempre escalar_seguranca; pedir autenticação pelo titular segue fluxo de suporte com validação de identidade.
4. Troca de titularidade pedida por quem não é o titular atual (14.6)
   - Condição: pedido de transferência de titularidade feito por alguém que não é o titular atual.
   - Ação: escalar_seguranca.
   - Fronteira: troca pedida pelo próprio titular segue capítulo 20 (solicitar_documentos).
5. E-mail suspeito em nome da Orbita (14.9 FAQ)
   - Condição: cliente recebeu e-mail que parece da Orbita.
   - Se o cliente clicou no link ou informou dados → escalar_seguranca.
   - Se não clicou → suporte_padrao.
6. Perda/roubo de celular com app logado (14.9 FAQ)
   - Se plano Empresa → escalar_seguranca.
   - Se Essencial ou Profissional → suporte_padrao (orientar encerrar sessões pelo painel).

Boas fronteiras e proibições relevantes a segurança:
- Nunca pedir senha ou código por nenhum canal.
- Registrar relato com as palavras do cliente e horários.
- Não confirmar/descartar invasão; primeiro encaminhar para Segurança.

# Incidentes técnicos (capítulo 15) — ordem das verificações e ações

Aplicar sempre nesta ordem; pare na primeira aplicável. Depois determinar se o incidente é "crítico" (termina em escalar_engenharia) ou não:

1. O problema afeta a emissão de notas fiscais? (15.3)
   - Condição: erro que impede transmissão/autorizar NF-e ou NFS-e, notas presas em "processando", rejeições generalizadas, falha de comunicação com prefeitura/SEFAZ.
   - Ação: escalar_engenharia.
   - Fronteira: pedidos de cancelamento/correção de nota já emitida → capítulo fiscal (16), não aqui.
2. É falha em integração (API ou webhooks)? (15.8 FAQ)
   - Condição: webhook/parada de chegada ou API retornando erro.
   - Ação:
     - Se plano Essencial → oferta_upgrade (Essencial não inclui API/webhooks).
     - Se plano Profissional ou Empresa → escalar_engenharia.
   - Fronteira: se esta falha também afeta emissão de notas, o passo 1 prevalece.
3. O plano é Empresa? (15.2 & 15.8)
   - Condição: conta do plano Empresa (qualquer problema técnico).
   - Ação: escalar_engenharia.
   - Nota: este passo vem antes da verificação de número de usuários afetados.
4. Número de usuários afetados atinge o limiar do plano? (tabela 15.4)
   - Condição: conte quantos usuários da conta são afetados (pelo relato do cliente). Se usuarios_afetados ≥ limiar → escalar_engenharia.
   - Tabela (limiares de usuários afetados):
     | Plano | Limiar de usuários afetados | Ação se usuarios_afetados >= limiar |
     |---|---:|---|
     | Essencial | 2 | escalar_engenharia |
     | Profissional | 5 | escalar_engenharia |
     | Empresa | não se aplica (decidido no passo anterior) | não se aplica |
   - Observação: contar usuários afetados pelo relato; se não claro, perguntar antes de classificar.
5. Exceção complementar do plano Profissional (15.8 FAQ)
   - Condição: plano Profissional; todos os usuários ativos da conta estão afetados; a conta tem ≥ 3 usuarios_ativos (campo do CRM).
   - Ação: escalar_engenharia, mesmo que usuarios_afetados < limiar da tabela.
   - Observação: cheque usuarios_ativos no CRM.
6. Demais casos (15.5)
   - Se nenhuma das anteriores se aplica → suporte_padrao (incidente técnico não crítico).

Definição de "incidente técnico crítico":
- Qualquer incidente que resulte em ação escalar_engenharia pela ordem acima.

FAQ fronteiras:
- Cliente Empresa, problema atinge 1 usuário → ainda escala (passo 3).
- "Talvez" de outro usuário afetado → confirmar antes de contar.

# Fiscal — notas emitidas pelo cliente (capítulo 16) — ordem das verificações e ações

Regra geral: referência é a data de emissão da nota; contagem de dias conforme 13.5; siga a ordem abaixo; pare no primeiro que decidir.

Ordem (16.2):

1. Identificar tipo de nota: NF-e (produto) ou NFS-e (serviço). (Confira no CRM: aba Notas emitidas, coluna "modelo".)
2. Identificar tipo de pedido: cancelamento ou correção.
3. Cancelamento de NF-e (16.3)
   - Condição: pedido de cancelamento de NF-e.
   - Prazo e ação:
     - Se (data_abertura − data_emissao) ≤ 1 dia → nf_cancelamento_orientado.
     - Se > 1 dia → fiscal_analise.
   - Fronteira: prazo contado em dias corridos; exemplo 12/05 emitida, 13/05 aberto → 1 dia → dentro.
4. Cancelamento de NFS-e (16.4)
   - Condição: pedido de cancelamento de NFS-e.
   - Prazo e ação (aplicar alteração histórica abaixo: ver "Alterações vigentes"):
     - Versão aplicável depende da data de abertura do chamado (ver seção "Alterações vigentes" para regras de vigência):
       - Se data_abertura < 01/06/2026: prazo = 5 dias; dentro → nf_cancelamento_orientado; fora → fiscal_analise.
       - Se data_abertura ≥ 01/06/2026: prazo = 10 dias; dentro → nf_cancelamento_orientado; fora → fiscal_analise.
   - Observação: comunicar ao cliente que o status pode levar horas para mudar na prefeitura.
5. Correção de NF-e (16.2 passo 5)
   - Antes de aplicar prazos, verificar qual campo quer corrigir:
     - Se correção em valor ou imposto (valor unitário, quantidade que altera total, alíquota, base de cálculo, desconto) → fiscal_analise (sempre), independentemente do prazo.
     - Se correção do CPF/CNPJ do destinatário → fiscal_analise (sempre).
     - Se erro em dados cadastrais que cabem em Carta de Correção e (data_abertura − data_emissao) ≤ 30 dias → nf_carta_correcao.
     - Se Carta de Correção fora do prazo (mais de 30 dias) → fiscal_analise.
   - Tabela de carta de correção (aplicada após as verificações acima):
     | Tipo de nota | Pedido | Prazo | Dentro do prazo | Fora do prazo |
     |---|---|---:|---|---|
     | NF-e (produto) | Carta de correção (outros dados cadastrais) | 30 dias | nf_carta_correcao | fiscal_analise |
6. Correção de NFS-e (16.2 passo 6 / FAQ 16.8)
   - Não existe carta de correção para NFS-e.
   - Correção de NFS-e = cancelar e reemitir. Aplicar o prazo de cancelamento de NFS-e (ver passo 4): dentro → nf_cancelamento_orientado (orientar cancelar e reemitir); fora → fiscal_analise.

Distinções de fronteira e provas:
- A data de emissão registrada na nota vale sobre qualquer afirmação do cliente sobre "ontem à noite".
- O atendente não cancela nem corrige a nota pelo cliente; orienta e acompanha.
- Correção de valor/imposto e CPF/CNPJ do destinatário são sempre fiscal_analise, independentemente de prazo.

# Privacidade e LGPD (capítulo 17) — ordem das verificações e ações

Siga ordem; pare na primeira aplicável (17.2):

1. Quem está pedindo? Pedido por terceiro (cliente final do usuário) falando sobre próprios dados → FAQ 17.8
   - Ação: suporte_padrao.
   - Informação padrão: orientar que a controladora é a empresa (usuário da Orbita) e que o titular deve procurá-la.
2. Reclamação de pedido anterior sem resposta → FAQ 17.8
   - Se passaram > 15 dias entre pedido anterior e a reclamação (contagem conforme 13.5) → encaminhar_dpo.
   - Se passaram ≤ 15 dias → suporte_padrao (acompanhar/pedir movimento).
3. Exportação de dados pelo titular da conta (17.3)
   - Ação: solicitar_documentos (para confirmar identidade) — exceto exceção por plano (17.8 FAQ).
   - Procedimento: pedir documento oficial com foto do titular; para pessoa jurídica, contrato social ou documento que comprove representação.
   - Pós-validação: geração de pacote estruturado (JSON/CSV) e envio por link ao e-mail cadastrado.
   - Exceção por plano (veja 17.8 FAQ): Plano Empresa — exportação feita pelo próprio cliente no painel; ação = suporte_padrao (oriente o caminho).
4. Exclusão de dados pelo titular da conta (17.4)
   - Condição: pedido de exclusão pelo titular.
   - Ação:
     - Se titular emitiu notas fiscais pela Orbita nos últimos 5 anos → encaminhar_dpo (obrigação legal de guarda fiscal).
     - Se não emitiu notas pela Orbita nos últimos 5 anos → solicitar_documentos (confirmar identidade antes de apagar).
   - Procedimento: conferir Notas emitidas no CRM filtrando período.
5. Correção dos próprios dados cadastrais pelo titular → FAQ 17.8
   - Ação: suporte_padrao (orientar alteração em Configurações > Dados da conta ou fazer junto).

Distinções de fronteira:
- Pedido de cliente final de usuário = terceiro (suporte_padrao), não entregar nem apagar dados.
- Documentos de verificação ficam anexados apenas ao chamado; após conclusão, acesso restrito.
- Regra de 15 dias (reclamação sem resposta) usa data do pedido anterior vs data_abertura.

# Cancelamento e retenção (capítulo 18) — ordem das verificações e ações

Aplica-se quando o cancelamento de assinatura é o assunto que comanda o chamado (veja precedência 13.2). A ordem das verificações (18.2); pare na primeira que decidir:

1. Fechamento da empresa (18.3)
   - Condição: motivo declarado = fechamento da empresa (baixa do CNPJ, encerramento das atividades, fechamento do estabelecimento).
   - Ação: cancelamento_direto (independentemente de plano, ciclo, tempo de casa, histórico).
   - Fronteira: dificuldade financeira ou queda de movimento sem encerramento = NÃO fechamento; seguir passo 2.
2. Recusa anterior de oferta de retenção (nota da macro em 18.5)
   - Condição: histórico mostra que o cliente já recusou oferta de retenção previamente.
   - Ação: cancelamento_direto.
   - Exceção temporal (18.7 FAQ): se a recusa anterior foi há MAIS de 180 dias (contados entre data da recusa e data_abertura), a recusa antiga não impede nova oferta; se foi há 180 dias ou menos → recusa vigente → cancelar direto.
3. Plano Essencial (18.2 e 18.7 FAQ)
   - Em regra: se plano Essencial → cancelamento_direto (após passos 1 e 2).
   - Exceção: Essencial no ciclo anual com ≥ 24 meses de casa → oferta_retencao.
   - Nota: Essencial mensal, ou Essencial anual com < 24 meses → cancelamento_direto.
4. Motivo "preço" no plano Profissional (18.2 e 18.7 FAQ)
   - Condição: motivo declarado = preço e plano = Profissional.
   - Ação: oferta_retencao (independentemente do tempo de casa).
   - Observação: esta verificação é feita depois dos passos 1–3; no Empresa, motivo preço não decide aqui.
5. Tempo de casa (última verificação; 18.4)
   - Aplica somente para clientes que chegaram até aqui (não decididos antes) — isto é, clientes Profissional e Empresa que não foram decididos nos passos anteriores.
   - Tabela:
     | Plano | Tempo de casa mínimo para oferta de retenção |
     |---|---:|
     | Profissional | 12 meses |
     | Empresa | 6 meses |
   - Regra:
     - Se tempo de casa ≥ mínimo do plano → oferta_retencao.
     - Se tempo de casa < mínimo → cancelamento_direto.
   - Contagem de meses conforme 13.6 (cliente_desde → data_abertura); completar o mesmo dia conta como atingido.

Registro e recusa:
- Se cliente recusa oferta na hora: use macro de confirmação e registrar data da recusa na nota interna (isso alimenta passo 2 em futuros chamados).

# Reembolso (capítulo 19) — ordem das verificações e ações

Aplicar sempre nesta ordem; primeira verificação que decidir encerra:

1. Cobrança duplicada (19.3)
   - Condição: consta no histórico dois lançamentos iguais para a mesma coisa/período (p.ex.: boleto e Pix para mesma fatura) — confirmar no extrato.
   - Ação: reembolso_automatico (ignorando plano, prazo, histórico, valor; inclusive Empresa e mesmo fora de prazo).
   - Fronteira: mensalidade + pró-rata não é duplicidade (são cobranças diferentes).
2. Plano Empresa (19.2 / 19.8 FAQ)
   - Condição: plano = Empresa.
   - Ação: reembolso_com_analise (sempre; exceto quando primeira verificação detectar cobrança duplicada).
3. Prazo (19.4) — referência = data da cobrança; contagem conforme 13.5.
   - Tabela de prazos (aplicar alteração histórica sobre ciclo mensal: ver seção "Alterações vigentes"):
     - Para cobranças do ciclo mensal, a regra de prazo depende da data da cobrança:
       - Se data_da_cobranca <= 28/02/2026 → prazo para ciclo mensal = 7 dias.
       - Se data_da_cobranca ≥ 01/03/2026 → prazo para ciclo mensal = 14 dias (alteração vigente em 20/02/2026; aplicável pelas datas das cobranças).
     - Outras linhas (inalteradas):
       | Tipo de cobrança | Ciclo e plano | Prazo para pedir reembolso |
       |---|---|---:|
       | Fatura da assinatura | Ciclo anual, plano Essencial | 15 dias |
       | Fatura da assinatura | Ciclo anual, plano Profissional | 30 days |
     - Regra de decisão:
       - Se pedido está fora do prazo → negar_reembolso.
       - Se dentro → seguir passos seguintes.
   - Observação: a tabela não menciona Empresa (passo 2 preenche isso).
   - Nota sobre pró-rata: cobranças avulsas de pró-rata têm prazo próprio (FAQ 19.8).
4. Histórico de reembolsos (19.2 e FAQ 19.8)
   - Condição: reembolsos_12m ≥ 2 → reembolso_com_analise.
   - Exceção temporal (19.8 FAQ):
     - Se cliente tem ≥ 36 meses de casa (cliente_desde → data_abertura pela 13.6), então só Vai para análise por histórico se reembolsos_12m ≥ 3.
     - Portanto:
       - Se tempo de casa < 36 meses e reembolsos_12m ≥ 2 → reembolso_com_analise.
       - Se tempo de casa ≥ 36 meses e reembolsos_12m ≥ 3 → reembolso_com_analise.
       - Caso contrário → seguir.
   - Observação: esta verificação só é feita depois de confirmar que não é duplicada, que não é Empresa, e que está dentro do prazo.
5. Valor — teto de aprovação automática (nota da macro; 19.6)
   - Tabela de tetos:
     | Plano | Ciclo | Teto de aprovação automática |
     |---|---:|---:|
     | Essencial | Mensal ou anual | R$ 200,00 |
     | Profissional | Mensal | R$ 300,00 |
     | Profissional | Anual | R$ 1.000,00 |
   - Regra: se valor da cobrança é estritamente maior que o teto aplicável → reembolso_com_analise.
   - Igual ao teto → considerado dentro (pode seguir reembolso_automatico se passar demais verificações).
6. Aprovação automática (última verificação, 19.5)
   - Condição: não duplicada; não Empresa; dentro do prazo; histórico de reembolsos permitido; valor ≤ teto.
   - Ação: reembolso_automatico.
   - Procedimento: atendente aprova na hora.

Prazos e pró-rata (FAQ 19.8):
- Cobrança avulsa de pró-rata de upgrade → prazo = 7 dias (qualquer ciclo e plano), contados da data da cobrança.
- Cliente Empresa → sempre reembolso_com_analise (passo 2); duplicidade ainda é reembolso_automatico.

# Usuários e permissões (capítulo 20) — ordem das verificações e ações

Pedidos se dividem por tipo; verificar o campo plano, ciclo, usuarios_ativos no CRM.

Tabela de limites por plano (20.2) — inclua alteração histórica (vigência):
- Versão dependente de data_abertura do chamado:
  - Se data_abertura < 01/07/2026:
    | Plano | Limite de usuários ativos |
    |---|---:|
    | Essencial | 2 |
    | Profissional | 5 |
    | Empresa | sem limite |
  - Se data_abertura ≥ 01/07/2026:
    | Plano | Limite de usuários ativos |
    |---|---:|
    | Essencial | 2 |
    | Profissional | 8 |
    | Empresa | sem limite |
  - Nota: mudança de 10/06/2026 entra em vigor para chamados abertos a partir de 01/07/2026; chamados até 30/06/2026 seguem limite 5.
  - Observação: change does NOT alter incident-technical limiares (cap. 15) — eles permanecem os da tabela de 15.4.

Fluxos:

A. Adicionar usuários (20.3)
1. Primeiro verifique se plano = Empresa (primeira verificação de todo pedido de adicionar usuários; tabela 20.2 nota)
   - Se plano = Empresa → ação: suporte_padrao (qualquer quantidade pedida; análise termina).
2. Se plano ≠ Empresa:
   - Calcule soma = usuarios_ativos (campo CRM) + quantidade de usuários pedida no chamado.
   - Compare soma com limite aplicável (ver tabela com vigência de data_abertura; lembre da exceção do Profissional anual no FAQ 20.8 abaixo).
     - Se soma ≤ limite → suporte_padrao (pedido cabe no plano; orientar cadastro pelo painel).
     - Se soma > limite → oferta_upgrade.
   - Observação: soma exatamente igual ao limite ainda cabe (suporte_padrao).
3. Exceção (FAQ 20.8): Profissional anual recebe +2 usuários de bônus — aplicar esse bônus quando ciclo = anual e plano = Profissional (o limite a comparar é limite tabela + 2, com a alteração do limite Profissional já considerada conforme vigência).

B. Troca de titularidade (20.4)
1. Se pedido de troca é feito pelo titular atual:
   - Ação: solicitar_documentos (solicitar documentos do titular atual e dados do novo titular; só após conferência a troca é feita).
   - Observação: mesmo se o pedido chegar pelo e‑mail cadastrado, solicita documentos.
2. Se pedido é feito por quem não é titular:
   - Não pertence a este capítulo — é assunto de segurança (capítulo 14.6) → escalar_seguranca (precedência máxima).

C. Remover usuário / mudar permissão (20.8 FAQ)
1. Se pedido feito por um administrador da conta:
   - Ação: suporte_padrao (orientar pelo painel ou realizar com o administrador).
2. Se pedido feito por quem não é administrador:
   - Ação: solicitar_documentos (confirmar autorização do titular).

Distinções e fronteiras:
- Contar usuarios_ativos exatamente como aparece no CRM; não confiar na contagem que o cliente fornece.
- Convite pendente/expirado → orientar reenviar pelo painel.
- Contador atendendo vários clientes → precisa de usuário por conta.

# Planos e upgrade (capítulo 21) — ordem das verificações e ações

Ver campos na lateral do CRM: plano, ciclo, usuarios_ativos, cliente_desde, data_abertura.

Ordem por tipo de pedido (21.2):

1. Upgrade (para plano mais caro) (21.3)
   - Pedido de upgrade → ação: ajuste_plano.
   - Observações: cobrança pró-rata na hora (cálculo proporcional aos dias faltantes); pró-rata é cobrado avulso; se cliente depois pedir devolução do pró-rata → segue capítulo Reembolso.
2. Downgrade (21.4) — duas etapas:
   A. Verificar ciclo:
      - Se ciclo atual = anual → ação: suporte_padrao (downgrade só acontece na renovação; registrar pedido e data de vigência da mudança).
      - Observação: plano Empresa é sempre anual, logo todo downgrade a partir do Empresa cai aqui.
   B. Se ciclo atual = mensal (somente):
      - Compare usuarios_ativos com limite do plano de destino (usar tabela de limites do capítulo 20 com vigência e exceção Profissional anual não aplicável aqui porque é mudança mensal).
        - Se usuarios_ativos > limite do plano de destino → suporte_padrao (orientar desativar usuários antes; depois pode pedir downgrade de novo).
        - Se usuarios_ativos ≤ limite do plano de destino → ajuste_plano (downgrade feito).
3. Mudança de ciclo (21.5)
   - De mensal → anual → ajuste_plano (mudança feita; cliente paga anuidade).
   - De anual → mensal → suporte_padrao (só na renovação; registrar pedido e data de vigência).
4. Desconto de fidelidade (FAQ 21.8)
   - Condição: plano Profissional ou Empresa com ≥ 24 meses de casa (contagem 13.6) → ajuste_plano (conceder desconto de fidelidade).
   - Caso contrário → suporte_padrao.

Fronteiras:
- Downgrade anual não ocorre no meio do período pago; vigência na renovação.
- Mudança de plano não altera o dia de vencimento.
- Usuários ativos do CRM determinam elegibilidade ao downgrade mensal.

# Campos, limites, prazos e números citados (tabelas e valores decisórios)

(reproduzo todas as tabelas que decidem ações, com indicação de vigência quando há alteração no histórico)

1. Precedência de assuntos (13.2) — ordem fixa (repetida acima).
2. Contagem de dias e meses — regras (13.5, 13.6) — aplicadas a todas as áreas.
3. Segurança: Reset 2FA por plano (14.5 + 14.9 FAQ)
   - Empresa: todo reset → escalar_seguranca.
   - Essencial/Profissional: titular → suporte_padrao; terceiro → escalar_seguranca.
4. Incidentes técnicos — limiares de usuários afetados (15.4)
   | Plano | Limiar de usuários afetados | Ação se usuarios_afetados >= limiar |
   |---|---:|---|
   | Essencial | 2 | escalar_engenharia |
   | Profissional | 5 | escalar_engenharia |
   | Empresa | não se aplica (decidido no passo anterior) | não se aplica |
   - Nota: estes limiares são próprios de incidentes técnicos; mudança do limite de usuários do Profissional (capítulo 22) NÃO altera estes limiares.
   - Exceção Profissional (15.8 FAQ): se todos os usuarios_ativos estão afetados e usuarios_ativos ≥ 3 → escalar_engenharia (mesmo que < limiar).
5. Fiscal — tabela de prazos (16.2)
   | Tipo de nota | Pedido | Prazo | Dentro do prazo | Fora do prazo |
   |---|---|---:|---|---|
   | NF-e (produto) | Cancelamento | 1 dia | nf_cancelamento_orientado | fiscal_analise |
   | NFS-e (serviço) | Cancelamento | 5 dias (versão anterior) / 10 dias (versão a partir de 01/06/2026) | nf_cancelamento_orientado | fiscal_analise |
   | NF-e (produto) | Carta de correção (outros dados cadastrais) | 30 dias | nf_carta_correcao | fiscal_analise |
   - Aplicação da alteração NFS-e: ver seção "Alterações vigentes" — a data do chamado (data_abertura) decide qual prazo vale.
6. Reembolso — tabela de prazos (19.4) com alteração para ciclo mensal (vigência conforme data da cobrança)
   - Prazos (referência: data da cobrança):
     | Tipo de cobrança | Ciclo e plano | Prazo para pedir reembolso |
     |---|---|---:|
     | Fatura da assinatura | Ciclo mensal, qualquer plano | 7 dias (para cobranças com data até 28/02/2026) OR 14 dias (para cobranças com data a partir de 01/03/2026) |
     | Fatura da assinatura | Ciclo anual, plano Essencial | 15 dias |
     | Fatura da assinatura | Ciclo anual, plano Profissional | 30 dias |
   - Cobrança de pró-rata (FAQ 19.8): prazo = 7 dias (qualquer plano/ciclo), contados da data da cobrança do pró-rata.
7. Reembolso — tetos de aprovação automática (19.6)
   | Plano | Ciclo | Teto de aprovação automática |
   |---|---:|---:|
   | Essencial | Mensal ou anual | R$ 200,00 |
   | Profissional | Mensal | R$ 300,00 |
   | Profissional | Anual | R$ 1.000,00 |
   - Regra: valor estritamente maior que o teto → reembolso_com_analise; igual ou menor pode seguir reembolso_automatico se demais condições cumpridas.
8. Reembolso — duplicidade
   - Cobrança duplicada → reembolso_automatico (independente de plano/prazo/valor).
9. Reembolso — histórico (19.8 FAQ)
   - Se reembolsos_12m ≥ 2 → reembolso_com_analise (exceto duplicidade ou Empresa).
   - Exceção: se tempo de casa ≥ 36 meses → só reembolso_com_analise se reembolsos_12m ≥ 3.
10. Usuários — tabela de limites por plano (20.2) com alteração de vigência:
    - Se data_abertura < 01/07/2026:
      | Plano | Limite de usuários ativos |
      |---|---:|
      | Essencial | 2 |
      | Profissional | 5 |
      | Empresa | sem limite |
    - Se data_abertura ≥ 01/07/2026:
      | Plano | Limite de usuários ativos |
      |---|---:|
      | Essencial | 2 |
      | Profissional | 8 |
      | Empresa | sem limite |
    - Exceção (FAQ 20.8): Profissional anual → bônus +2 usuários (somar ao limite aplicável).
11. Cancelamento/Retenção — tempos mínimos para oferta de retenção (18.4)
    | Plano | Tempo de casa mínimo para oferta de retenção |
    |---|---:|
    | Profissional | 12 meses |
    | Empresa | 6 meses |
    - Essencial em regra → cancelamento_direto; exceção Essencial anual com ≥ 24 meses → oferta_retencao (18.7 FAQ).
12. Planos — desconto fidelidade (FAQ 21.8)
    - Plano Profissional ou Empresa com ≥ 24 meses de casa → ajuste_plano (desconto de fidelidade).
    - Essencial → suporte_padrao (sem desconto).

# Distinções de fronteira importantes (quem pede / tipo de documento / tipo de cobrança / o que conta)

- Troca de titularidade:
  - Pedida pelo titular atual → capítulo 20 → solicitar_documentos.
  - Pedida por terceiro (não titular) → capítulo 14 (segurança) → escalar_seguranca (precedência máxima).
- Reset 2FA:
  - Titular no Essencial/Profissional → suporte_padrao.
  - Qualquer pedido no Empresa → escalar_seguranca (exceção).
  - Pedido por terceiro → escalar_seguranca.
- Emissão de notas vs pedidos fiscais:
  - Falha de emissão (sistema não consegue emitir) → incidente técnico (cap. 15) → escalar_engenharia.
  - Pedido de cancelamento/correção de nota já emitida → fiscal (cap. 16) → nf_cancelamento_orientado / nf_carta_correcao / fiscal_analise conforme prazos/campos.
- Cobrança duplicada:
  - Dois lançamentos iguais para o mesmo período → reembolso_automatico (sempre).
  - Mensalidade + pró-rata são cobranças diferentes → não duplicidade.
- Contagem de prazos:
  - Use a data de referência indicada por cada regra (data da cobrança, data de emissão da nota, data do pedido anterior).
  - Contagem de dias corridos; último dia conta.
- Data de vigência de alterações (quando aplicável): use data_abertura do chamado para decidir qual versão de regra/tabela aplicar (conforme instrução do manual e do capítulo 22).

# Alterações vigentes (texto integral do histórico que muda regras decisórias)
(reproduzo integralmente apenas as entradas do capítulo 22 que alteram prazos, limites ou tabelas; estas prevalecem sobre capítulos que citam os mesmos números)

- 20/02/2026 — Prazo de reembolso do ciclo mensal.
  "Para cobranças do ciclo mensal com data da cobrança a partir de 01/03/2026, o prazo de reembolso das faturas da assinatura passa a ser de 14 dias corridos, em qualquer plano. A mudança não vale para cobranças avulsas de pró-rata de upgrade, que continuam com o prazo próprio do capítulo 19. Cobranças do ciclo mensal com data até 28/02/2026 mantêm o prazo de 7 dias corridos. A forma de contagem não muda (seção 13.5) e os prazos do ciclo anual continuam os da tabela do capítulo 19."

- 15/05/2026 — Prazo de cancelamento de NFS-e.
  "Para NFS-e emitidas a partir de 01/06/2026, o prazo para cancelamento orientado passa a ser de 10 dias corridos contados da data de emissão. NFS-e emitidas até 31/05/2026 mantêm o prazo de 5 dias. Como a correção de NFS-e segue o prazo de cancelamento de NFS-e, o novo prazo vale também para ela. Os prazos de NF-e não mudam."

- 10/06/2026 — Limite de usuários do plano Profissional.
  "Para chamados abertos a partir de 01/07/2026, o limite de usuários do plano Profissional passa de 5 para 8. A mudança vale para toda regra do manual que usa o limite de usuários do plano; no ciclo anual, os usuários de bônus do capítulo 20 continuam sendo somados ao novo limite. Chamados abertos até 30/06/2026 seguem o limite de 5. Os limites do Essencial e do Empresa não mudam. Esta mudança não altera os limiares de usuários afetados em incidentes técnicos (capítulo 15), que são uma tabela própria."

Observações sobre vigência:
- Para decisões que consultam prazos/limites alterados, use data_abertura do chamado para escolher qual versão aplicar:
  - Reembolso ciclo mensal: avaliar a data da cobrança; a entrada especifica que a mudança aplica para cobranças com data da cobrança ≥ 01/03/2026; portanto, para um pedido aberto hoje, compare a data_da_cobranca com 01/03/2026 para aplicar prazo de 14 ou 7 dias.
  - NFS-e cancelamento: para notas emitidas a partir de 01/06/2026, aplicar 10 dias; para notas emitidas até 31/05/2026 aplicar 5 dias. Use a data de emissão da nota como referência (a contagem do prazo é: data_abertura − data_emissao ≤ prazo), mas a escolha entre 5 e 10 dias depende da data de emissão da nota (e a vigência do manual foi publicada em 15/05/2026 com efeito a partir de 01/06/2026).
  - Limite Profissional: para chamados abertos a partir de 01/07/2026 (data_abertura ≥ 01/07/2026) o limite é 8; para chamados abertos até 30/06/2026 (data_abertura ≤ 30/06/2026) o limite é 5.

(Fim das alterações que mudam decisões.)

---

Fim do material de regras extraídas.