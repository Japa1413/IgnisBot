# 📊 SERVICE LEVEL AGREEMENT (SLA) - IGNISBOT

**Acordo de Nível de Serviço**  
**Versão:** 1.0  
**Última atualização: 2025-10-31  
**Vigência:** Indefinida (até revogação)

---

## 1. OBJETO DO ACORDO

Este Acordo de Nível de Serviço (SLA) estabelece os compromissos de disponibilidade, performance e suporte do **IgnisBot**, um bot Discord para gamificação e sistemas de ranking.

---

## 2. DEFINIÇÕES

### 2.1 Termos Técnicos
- **Uptime:** Tempo em que o serviço está disponível e operacional
- **Downtime:** Tempo em que o serviço está indisponível
- **MTTR:** Mean Time To Recovery (Tempo médio para recuperação)
- **MTBF:** Mean Time Between Failures (Tempo médio entre falhas)
- **SLA Target:** Meta de disponibilidade estabelecida

### 2.2 Períodos
- **Período de Medição:** 30 dias corridos (mês)
- **Janela de Manutenção:** Períodos agendados de manutenção (não contam como downtime)

---

## 3. NÍVEIS DE SERVIÇO

### 3.1 Disponibilidade (Uptime)

| Nível | Disponibilidade Mensal | Downtime Máximo/Mês | Aplicação |
|-------|------------------------|---------------------|-----------|
| **Básico** | 95% | 36 horas | Uso interno/desenvolvimento |
| **Padrão** | 99% | 7,2 horas | Uso em produção básico |
| **Premium** | 99.5% | 3,6 horas | Uso em produção crítico |
| **Enterprise** | 99.9% | 43 minutos | Uso comercial/empresarial |

**SLA Atual do IgnisBot:** **Nível Padrão (99%)**

> **Nota:** O nível atual reflete a fase de desenvolvimento e operação voluntária. Pode ser ajustado conforme necessidade.

### 3.2 Performance

#### 3.2.1 Tempo de Resposta de Comandos
- **Comandos Simples:** ≤ 2 segundos
- **Comandos com Banco de Dados:** ≤ 5 segundos
- **Comandos Complexos (leaderboard, export):** ≤ 10 segundos

#### 3.2.2 Capacidade
- **Usuários Simultâneos:** Até 10.000 usuários registrados
- **Comandos por Minuto:** Até 100 comandos/minuto por servidor
- **Eventos de Voz:** Processamento em tempo real

### 3.3 Suporte

| Tipo de Suporte | Prazo de Resposta | Horário |
|-----------------|-------------------|---------|
| **Crítico** (Bot offline, vazamento de dados) | 4 horas | 24/7 |
| **Alto** (Erro em comando essencial) | 24 horas | Dias úteis |
| **Médio** (Bug em funcionalidade) | 72 horas | Dias úteis |
| **Baixo** (Sugestão de melhoria) | 1 semana | Dias úteis |

**Canais de Suporte:**
- Discord: Canal de suporte no servidor
- E-mail: (Configure `CONTROLLER_EMAIL` no `.env`)

---

## 4. MANUTENÇÃO

### 4.1 Tipos de Manutenção

#### 4.1.1 Manutenção Programada
- **Notificação:** Pelo menos 24 horas de antecedência
- **Duração:** Geralmente até 2 horas
- **Frequência:** Mensal ou conforme necessidade
- **Contagem no SLA:** Não conta como downtime

#### 4.1.2 Manutenção de Emergência
- **Notificação:** Quando possível (pode ser durante a manutenção)
- **Aplicação:** Correções críticas de segurança ou estabilidade
- **Contagem no SLA:** Conta como downtime

### 4.2 Janelas de Manutenção Preferenciais
- **Horários:** Fins de semana ou madrugada (00:00 - 06:00 BRT)
- **Notificação:** Via anúncio no Discord quando possível

---

## 5. BACKUP E RECUPERAÇÃO

### 5.1 Estratégia de Backup

| Tipo de Dado | Frequência | Retenção | Localização |
|--------------|------------|----------|-------------|
| **Banco de Dados** | Diário (automático) | 7 dias | Servidor local/cloud |
| **Logs de Sistema** | Contínuo | 30 dias | Servidor local |
| **Logs de Auditoria (LGPD)** | Contínuo | 6 meses | Banco de dados |
| **Configuração** | Manual | Ilimitado | Repositório Git |

### 5.2 Tempo de Recuperação

| Cenário | RTO (Recovery Time Objective) | RPO (Recovery Point Objective) |
|---------|--------------------------------|--------------------------------|
| **Falha de Hardware** | 4 horas | 24 horas (último backup) |
| **Corrupção de Banco** | 2 horas | 24 horas (último backup) |
| **Falha de Software** | 1 hora | Imediato (rollback de código) |
| **Vazamento de Dados** | Imediato | N/A (procedimento específico) |

**RTO:** Tempo máximo para restaurar o serviço  
**RPO:** Perda máxima aceitável de dados (quanto tempo para trás podemos voltar)

### 5.3 Testes de Recuperação
- **Frequência:** Trimestralmente
- **Escopo:** Restauração de backup de banco de dados
- **Documentação:** Resultados registrados

---

## 6. SEGURANÇA

### 6.1 Medidas Implementadas
- ✅ Credenciais protegidas (variáveis de ambiente)
- ✅ Conexões seguras (SSL/TLS)
- ✅ Pool de conexões com timeout
- ✅ Sistema de auditoria (LGPD Art. 10)
- ✅ Logging estruturado

### 6.2 Resposta a Incidentes

#### 6.2.1 Classificação de Incidentes

| Severidade | Critério | Prazo de Resposta |
|------------|----------|-------------------|
| **Crítica** | Vazamento de dados, bot comprometido | Imediato (≤ 1 hora) |
| **Alta** | Vulnerabilidade crítica descoberta | 4 horas |
| **Média** | Vulnerabilidade média | 24 horas |
| **Baixa** | Melhorias de segurança | 1 semana |

#### 6.2.2 Procedimento de Notificação
- **Para Usuários:** Notificação no servidor Discord (se aplicável)
- **Para Autoridades (LGPD Art. 48):** Notificação à ANPD em até 72 horas
- **Para Titulares Afetados:** Notificação em até 72 horas (se dados comprometidos)

---

## 7. MONITORAMENTO

### 7.1 Métricas Monitoradas

✅ Status do bot (online/offline)  
✅ Tempo de resposta de comandos  
✅ Uso de recursos (CPU, memória)  
✅ Conexões de banco de dados  
✅ Erros e exceções  
✅ Uso de comandos (estatísticas)  

### 7.2 Alertas

| Evento | Nível | Ação |
|--------|-------|------|
| Bot offline | Crítico | Notificação imediata |
| Alta taxa de erros (>10%) | Alto | Investigação em 1 hora |
| Latência alta (>10s) | Médio | Investigação em 4 horas |
| Uso anormal de recursos | Médio | Investigação em 4 horas |

---

## 8. LIMITAÇÕES E ISENÇÕES

### 8.1 Fora de Controle

O SLA **não cobre** indisponibilidade causada por:
- Indisponibilidade da Discord API
- Problemas de infraestrutura do provedor de hospedagem
- Ataques DDoS externos
- Mudanças nas políticas do Discord
- Falhas de rede do usuário
- Manutenção não programada do Discord

### 8.2 Uso Gratuito/Voluntário

**IMPORTANTE:** Como o IgnisBot pode ser operado voluntariamente ou sem fins comerciais:

- **Sem Garantias Legais:** Não há garantias formais de disponibilidade
- **Melhor Esforço:** Os desenvolvedores se esforçam para manter o serviço disponível
- **Sem Responsabilidade Financeira:** Não há compensação por indisponibilidade

---

## 9. INDICADORES DE PERFORMANCE (KPIs)

### 9.1 Métricas Mensais

| Métrica | Meta | Medição |
|---------|------|---------|
| **Uptime** | ≥ 99% | (Tempo total - Downtime) / Tempo total |
| **MTTR** | ≤ 2 horas | Tempo médio para recuperação |
| **MTBF** | ≥ 720 horas | Tempo médio entre falhas |
| **Taxa de Erros** | < 1% | Erros / Total de comandos |
| **Satisfação de Suporte** | N/A | A implementar |

### 9.2 Relatório Mensal
- **Conteúdo:** Estatísticas de uptime, incidentes, melhorias
- **Distribuição:** Disponível mediante solicitação
- **Formato:** Documento ou dashboard (se implementado)

---

## 10. PLANO DE CONTINUIDADE DE NEGÓCIOS

### 10.1 Cenários de Contingência

#### 10.1.1 Falha do Servidor Principal
- **Ação:** Migração para servidor de backup (se disponível)
- **Tempo:** Conforme disponibilidade de infraestrutura

#### 10.1.2 Perda de Banco de Dados
- **Ação:** Restauração do último backup diário
- **Perda de Dados:** Máximo 24 horas

#### 10.1.3 Comprometimento de Segurança
- **Ação:** Desativação imediata, análise forense, correção
- **Notificação:** Conforme procedimento de incidentes de segurança

### 10.2 Documentação de Procedimentos
- Procedimentos de recuperação documentados
- Contatos de emergência atualizados
- Acesso a backups testado periodicamente

---

## 11. REVISÃO DO SLA

### 11.1 Frequência de Revisão
- **Anual:** Revisão completa do SLA
- **Conforme Necessidade:** Ajustes pontuais baseados em feedback

### 11.2 Comunicação de Mudanças
- Mudanças significativas serão comunicadas com 30 dias de antecedência
- Notificação via Discord ou e-mail

---

## 12. CONTATO E SUPORTE

### 12.1 Canais de Contato

**Suporte Técnico:**
- Discord: Canal de suporte no servidor
- E-mail: (Configure `CONTROLLER_EMAIL` no `.env`)

**Questões de Segurança:**
- E-mail: (Configure `CONTROLLER_EMAIL` no `.env`) com assunto "[SEGURANÇA]"

**Questões de Privacidade (LGPD):**
- E-mail: (Configure `CONTROLLER_EMAIL` no `.env`) com assunto "[PRIVACIDADE]"

### 12.2 Horários de Atendimento
- **Suporte Básico:** Dias úteis, 9h-18h (horário pode variar)
- **Emergências:** 24/7 conforme disponibilidade

---

## 13. APROVAÇÃO E VIGÊNCIA

Este SLA entra em vigor a partir da data de publicação e permanece válido até nova versão ou revogação.

**Versão:** 1.0  
**Data:** 31/10/2025  
**Próxima Revisão:** 2025 ou conforme necessidade

---

## ANEXOS

### Anexo A: Glossário de Termos
- **SLA:** Service Level Agreement (Acordo de Nível de Serviço)
- **RTO:** Recovery Time Objective (Objetivo de Tempo de Recuperação)
- **RPO:** Recovery Point Objective (Objetivo de Ponto de Recuperação)
- **MTTR:** Mean Time To Recovery (Tempo Médio para Recuperação)
- **MTBF:** Mean Time Between Failures (Tempo Médio entre Falhas)

### Anexo B: Histórico de Versões
- **v1.0 (2024):** Versão inicial do SLA

---

**Este SLA é fornecido como documentação de referência e não constitui garantia legal formal, especialmente em contextos de uso voluntário ou sem fins comerciais.**

**Versão:** 1.0 | **Data:** 31/10/2025

