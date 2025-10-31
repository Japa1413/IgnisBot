# 🔒 POLÍTICA DE PRIVACIDADE - IGNISBOT

**Última atualização:** 2024  
**Versão:** 1.0  
**Vigência:** Conforme LGPD (Lei nº 13.709/2018)

---

## 1. IDENTIFICAÇÃO DO CONTROLADOR

O **IgnisBot** é um bot para Discord desenvolvido e mantido por desenvolvedores independentes.

**Contato para questões de privacidade:**  
Configure a variável `CONTROLLER_EMAIL` no arquivo `.env` do projeto para definir o e-mail de contato.

---

## 2. DADOS COLETADOS

### 2.1 Dados Pessoais Coletados

O IgnisBot coleta e processa os seguintes dados pessoais:

| Categoria | Dados Coletados | Finalidade |
|-----------|-----------------|------------|
| **Identificação** | ID do Discord (user_id) | Identificação única do usuário no sistema |
| **Dados de Gamificação** | Pontos (points), Rank, Progresso | Funcionalidade principal do bot (sistema de ranking) |
| **Dados de Uso** | Logs de comandos executados, eventos de voz | Auditoria e melhorias do serviço |
| **Dados de Perfil Discord** | Nome de usuário, avatar, roles (apenas quando necessário) | Exibição de informações no bot |

### 2.2 Dados NÃO Coletados

O IgnisBot **NÃO coleta**:
- Mensagens privadas ou conteúdo de mensagens
- Dados de outros servidores além daquele onde o bot está configurado
- Informações de pagamento ou financeiras
- Localização geográfica

---

## 3. BASE LEGAL E FINALIDADE

### 3.1 Base Legal (LGPD Art. 7º)

O processamento de dados pessoais é baseado em:

- **Consentimento do titular** (Art. 7º, I): O usuário consente explicitamente ao usar o bot
- **Execução de contrato** (Art. 7º, V): Fornecimento de serviços solicitados pelo usuário

### 3.2 Finalidade do Tratamento

Os dados são processados para:

1. **Fornecimento do Serviço:**
   - Sistema de gamificação (pontos e ranks)
   - Leaderboards e rankings
   - Comandos de informação do usuário

2. **Melhoria do Serviço:**
   - Análise de uso do bot
   - Correção de bugs
   - Desenvolvimento de novas funcionalidades

3. **Conformidade Legal:**
   - Cumprimento de obrigações legais (LGPD)
   - Auditoria e registro de atividades

---

## 4. DIREITOS DO TITULAR (LGPD Art. 18)

Você tem os seguintes direitos sobre seus dados pessoais:

### 4.1 Direito de Acesso (Art. 18, II)
- **Como exercer:** Use o comando `/export_my_data` no Discord
- **O que recebe:** Arquivo JSON com todos os seus dados pessoais armazenados

### 4.2 Direito de Retificação (Art. 18, III)
- **Como exercer:** Entre em contato com o administrador do servidor
- **Aplicação:** Correção de dados incorretos ou incompletos

### 4.3 Direito à Portabilidade (Art. 18, V)
- **Como exercer:** Use o comando `/export_my_data` no Discord
- **Formato:** Dados exportados em formato JSON estruturado

### 4.4 Direito ao Esquecimento (Art. 18, VI)
- **Como exercer:** Use o comando `/delete_my_data` no Discord
- **Atenção:** Esta ação é **irreversível** e deleta todos os seus dados

### 4.5 Revogação de Consentimento (Art. 8º, §5º)
- **Como exercer:** Use o comando `/consent revoke` no Discord
- **Efeito:** Revoga o consentimento, mas alguns dados podem ser mantidos se houver outra base legal

---

## 5. ARMAZENAMENTO E SEGURANÇA

### 5.1 Local de Armazenamento
- **Banco de Dados:** MySQL (armazenado localmente ou em servidor do desenvolvedor)
- **Logs:** Arquivos locais no servidor onde o bot está hospedado

### 5.2 Medidas de Segurança
- **Acesso:** Credenciais protegidas via variáveis de ambiente
- **Conexão:** Pool de conexões com timeout
- **Auditoria:** Registro de todas as operações com dados pessoais
- **Logs:** Sistema de logging estruturado com rotação

### 5.3 Prazo de Retenção
- **Dados ativos:** Mantidos enquanto o usuário usar o bot
- **Após exclusão:** Dados removidos imediatamente após solicitação
- **Logs de auditoria:** Retidos por até 6 meses (conforme necessidade legal)

---

## 6. COMPARTILHAMENTO DE DADOS

### 6.1 Não Compartilhamos Seus Dados
O IgnisBot **NÃO compartilha** dados pessoais com:
- Terceiros
- Empresas de publicidade
- Serviços de análise externos
- Outros servidores Discord

### 6.2 Exceções Legais
Dados podem ser compartilhados apenas se:
- Requerido por ordem judicial
- Necessário para cumprimento de obrigação legal
- Para proteção de direitos do controlador ou terceiros

---

## 7. CONSENTIMENTO

### 7.1 Consentimento Necessário
Para usar o IgnisBot, você precisa:
1. Ler e aceitar esta Política de Privacidade
2. Conceder consentimento via comando `/consent grant`

### 7.2 Retirada de Consentimento
Você pode retirar seu consentimento a qualquer momento usando `/consent revoke`.

---

## 8. COOKIES E TECNOLOGIAS SIMILARES

O IgnisBot **não utiliza** cookies ou tecnologias de rastreamento no navegador, pois opera exclusivamente dentro do Discord.

---

## 9. ALTERAÇÕES NESTA POLÍTICA

Esta política pode ser atualizada periodicamente. Quando houver mudanças significativas:

- **Notificação:** Usuários serão notificados no servidor Discord
- **Nova Versão:** Versão da política será atualizada
- **Novo Consentimento:** Pode ser necessário conceder novo consentimento

---

## 10. CONTATO E EXERCÍCIO DE DIREITOS

Para exercer seus direitos ou esclarecer dúvidas:

1. **Via Bot:** Use os comandos `/export_my_data`, `/delete_my_data`, `/consent`
2. **Via Discord:** Entre em contato com administradores do servidor
3. **Via E-mail:** (Configure `CONTROLLER_EMAIL` no `.env`)

**Prazo de Resposta:** Até 15 dias úteis (conforme LGPD Art. 18, §3º)

---

## 11. ENcarregado DE DADOS (DPO) - LGPD Art. 41

### 11.1 Responsabilidades do DPO

O **Encarregado de Dados (DPO)** é responsável por:
- Receber comunicações dos titulares sobre privacidade e proteção de dados
- Orientar sobre práticas de proteção de dados pessoais
- Comunicar-se com a ANPD (Autoridade Nacional de Proteção de Dados) quando necessário
- Realizar o controle interno da conformidade com a LGPD

### 11.2 Como Contatar o DPO

**⚠️ IMPORTANTE: Configure as informações abaixo**

**Nome:** [DEFINIR NOME DO DPO]  
**E-mail:** [Configurar `CONTROLLER_EMAIL` no `.env`]  
**Telefone:** [Opcional]

**Para questões de privacidade:**
- **E-mail:** [EMAIL] (assunto: "[LGPD]" ou "[Privacidade]")
- **Prazo de Resposta:** Até 15 dias úteis (conforme LGPD Art. 18, §3º)

**Nota:** Se você é o proprietário/desenvolvedor do bot, você pode ser o próprio DPO. Configure o `CONTROLLER_EMAIL` no arquivo `.env` com seu e-mail.

---

## 12. NOTIFICAÇÃO DE INCIDENTES - LGPD Art. 48

### 12.1 Compromisso

Caso ocorra qualquer incidente de segurança que possa resultar em risco ou dano aos titulares, o IgnisBot se compromete a:

1. **Notificar a ANPD** em até 72 horas após o conhecimento do incidente
2. **Notificar os titulares afetados** imediatamente após avaliação

### 12.2 Procedimento

O procedimento completo está documentado em: `docs/PLANO_RESPOSTA_INCIDENTES.md`

---

## 13. CONFORMIDADE

### 13.1 Legislação Aplicável
Esta política está em conformidade com:
- **LGPD** (Lei nº 13.709/2018) - Brasil
- **GDPR** (Regulamento Geral sobre Proteção de Dados) - UE (se aplicável)

### 13.2 Registro de Atividades
Todas as operações com dados pessoais são registradas em log de auditoria, conforme LGPD Art. 10.

---

## 14. GLOSSÁRIO

- **Dado Pessoal:** Informação relacionada a pessoa natural identificada ou identificável
- **Titular:** Pessoa natural a quem se referem os dados pessoais
- **Controlador:** Responsável pelas decisões sobre o tratamento de dados pessoais
- **Tratamento:** Operação com dados pessoais (coleta, armazenamento, uso, etc.)

---

**Esta política foi elaborada conforme os requisitos da LGPD e está sujeita a atualizações periódicas.**

**Versão:** 1.0 | **Data:** 31/10/2025

