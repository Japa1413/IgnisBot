# 📊 MATRIZ DE BASE LEGAL - IGNISBOT

**Versão:** 1.0  
**Última atualização:** 2025-10-31  
**Objetivo:** Documentar qual base legal se aplica a cada tipo de processamento

---

## 📋 VISÃO GERAL

Conforme LGPD Art. 7º, todo processamento de dados pessoais deve ter uma base legal válida. Esta matriz documenta qual base legal se aplica a cada tipo de operação.

---

## 🔗 MATRIZ BASE LEGAL × OPERAÇÃO

| Tipo de Operação | Base Legal | Artigo LGPD | Validação Implementada | Status |
|------------------|------------|-------------|------------------------|--------|
| **Processamento de Pontos** | Consentimento | Art. 7º, I | ✅ `PointsService` valida consentimento | ✅ |
| **Processamento de Ranks** | Consentimento | Art. 7º, I | ✅ Via `PointsService` | ✅ |
| **Logs de Voz (VC Log)** | Consentimento | Art. 7º, I | ✅ Via `PointsService` | ✅ |
| **Logs de Auditoria** | Obrigação Legal | Art. 7º, II | ⚠️ Documentado | ✅ |
| **Retenção de Logs (6 meses)** | Obrigação Legal | Art. 7º, II | ✅ Script de limpeza | ✅ |
| **Exibição de Leaderboard** | Consentimento | Art. 7º, I | ✅ Usuário precisa ter dado consentimento | ✅ |
| **Exportação de Dados** | Execução de Contrato | Art. 7º, V | ✅ Comando próprio | ✅ |
| **Exclusão de Dados** | Execução de Direito | Art. 18, VI | ✅ Comando próprio | ✅ |

---

## 📝 DETALHAMENTO POR OPERAÇÃO

### 1. Processamento de Pontos (Pontos, Ranks, Progresso)

**Base Legal:** **Consentimento** (Art. 7º, I)

**Justificativa:**
- Dados são processados apenas após consentimento explícito do usuário
- Usuário pode revogar consentimento a qualquer momento
- Sistema valida consentimento antes de processar

**Validação:**
- ✅ `PointsService.add_points()` verifica `has_consent()`
- ✅ `PointsService.remove_points()` verifica `has_consent()`
- ✅ Raise `ValueError` se consentimento não dado

**Registro:**
- Base legal registrada em `user_consent.base_legal = "consentimento"`
- Operação auditada em `data_audit_log`

---

### 2. Logs de Auditoria

**Base Legal:** **Obrigação Legal** (Art. 7º, II)

**Justificativa:**
- LGPD Art. 10 exige registro de atividades
- Necessário para conformidade legal
- Retenção por 6 meses conforme política interna

**Validação:**
- ⚠️ Não requer consentimento (base legal diferente)
- ✅ Script de limpeza automática implementado

**Registro:**
- Base legal: "obrigacao_legal"
- Registrado em `data_audit_log`

---

### 3. Retenção de Logs (6 meses)

**Base Legal:** **Obrigação Legal** (Art. 7º, II)

**Justificativa:**
- Necessário para auditoria e conformidade
- Período de 6 meses conforme política interna
- Limpeza automática após período

**Implementação:**
- ✅ Script `cleanup_audit_logs.py`
- ✅ Configurável via `RETENTION_DAYS = 180`

---

### 4. Exibição de Leaderboard

**Base Legal:** **Consentimento** (Art. 7º, I)

**Justificativa:**
- Exibe dados pessoais (pontos, ranks)
- Requer consentimento do usuário
- Usuários sem consentimento são filtrados da listagem

**Validação:**
- ✅ **IMPLEMENTADO:** Query SQL filtra apenas usuários com consentimento ativo
- ✅ Apenas usuários com `consent_given = TRUE` aparecem no leaderboard

**Implementação:**
- Query SQL com JOIN em `user_consent` filtra consentimento
- Usuários sem consentimento não aparecem na listagem

---

### 5. Exportação de Dados (`/export_my_data`)

**Base Legal:** **Execução de Contrato** (Art. 7º, V)

**Justificativa:**
- Exercício de direito do titular (LGPD Art. 18, II e V)
- Não requer consentimento adicional
- É parte do contrato de serviço

**Validação:**
- ✅ Não requer validação de consentimento (base legal diferente)
- ✅ Usuário solicita explicitamente

---

### 6. Exclusão de Dados (`/delete_my_data`)

**Base Legal:** **Execução de Direito** (Art. 18, VI)

**Justificativa:**
- Exercício do direito ao esquecimento
- Não requer consentimento
- É direito do titular

**Validação:**
- ✅ Não requer validação de consentimento (base legal diferente)
- ✅ Requer confirmação explícita do usuário

---

## 🔍 VALIDAÇÃO DE BASE LEGAL NO CÓDIGO

### Implementação Atual

**Localização:** `services/points_service.py`

```python
# Valida consentimento antes de processar
if check_consent:
    has_consent = await self.consent_service.has_consent(user_id)
    if not has_consent:
        raise ValueError("User has not given consent...")
```

### Registro de Base Legal

**Tabela:** `user_consent`

```sql
base_legal VARCHAR(50) DEFAULT 'consentimento'
```

**Valores Possíveis:**
- `"consentimento"` - Art. 7º, I (padrão)
- `"obrigacao_legal"` - Art. 7º, II (logs)
- `"execucao_contrato"` - Art. 7º, V (exportação)

---

## ⚠️ GAPS IDENTIFICADOS

### 1. Leaderboard Sem Validação de Consentimento

**Problema:**
- `LeaderboardCog.leaderboard()` não valida consentimento
- Exibe dados pessoais sem verificação

**Impacto:**
- Violação potencial de LGPD Art. 7º, I
- Exibição de dados sem base legal válida

**Recomendação:**
- Adicionar validação de consentimento antes de exibir
- Ou filtrar usuários sem consentimento da listagem

---

## ✅ CHECKLIST DE CONFORMIDADE

### Base Legal Documentada
- [x] Matriz de base legal criada
- [x] Todas as operações mapeadas
- [x] Validação documentada

### Implementação
- [x] Validação de consentimento em pontos
- [x] Script de limpeza de logs
- [ ] Validação em leaderboard (pendente)

### Registro
- [x] Base legal armazenada em `user_consent`
- [x] Operações auditadas em `data_audit_log`

---

**Última atualização:** 2025-10-31  
**Versão:** 1.0

