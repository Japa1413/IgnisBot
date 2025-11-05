# 📋 POLÍTICA DE RETENÇÃO DE LOGS DE AUDITORIA - IGNISBOT

**Versão:** 1.0  
**Última atualização:** 2025-10-31  
**Base Legal:** LGPD Art. 15 (Prazo de Retenção) + Art. 7º, II (Obrigação Legal)

---

## 📊 VISÃO GERAL

Este documento esclarece a política de retenção de logs de auditoria (`data_audit_log`) e como ela se relaciona com o direito ao esquecimento (LGPD Art. 18, VI).

---

## ⚖️ CONFLITO DE INTERESSES LEGAIS

### Direito ao Esquecimento vs. Obrigação Legal

**LGPD Art. 18, VI:** Titular tem direito à exclusão de dados pessoais.

**LGPD Art. 7º, II:** Processamento pode ser realizado para cumprimento de obrigação legal.

**LGPD Art. 10:** Controlador deve manter registro de operações de tratamento.

**Resolução:** Logs de auditoria são necessários para conformidade legal (Art. 10) e podem ser mantidos mesmo após solicitação de exclusão, mediante base legal adequada.

---

## 📋 POLÍTICA APLICADA

### 1. Retenção Padrão

**Período:** 6 meses (180 dias)

**Base Legal:** LGPD Art. 7º, II (Cumprimento de obrigação legal)

**Justificativa:**
- Necessário para auditoria e conformidade (LGPD Art. 10)
- Período permite investigação de incidentes
- Alinhado com boas práticas de segurança

**Implementação:**
- Script `scripts/cleanup_audit_logs.py` remove automaticamente logs > 6 meses
- Execução recomendada: Diária

---

### 2. Solicitação de Exclusão (`/delete_my_data`)

**Quando usuário solicita exclusão completa:**

**O que é excluído:**
- ✅ Dados da tabela `users` (pontos, ranks, progresso)
- ✅ Dados da tabela `user_consent`
- ⚠️ **Logs de auditoria (`data_audit_log`) NÃO são excluídos imediatamente**

**Justificativa para Não Excluir Logs Imediatamente:**

1. **Base Legal Alternativa (Art. 7º, II):**
   - Logs são necessários para cumprir obrigação legal de auditoria (Art. 10)
   - Retenção por 6 meses é necessária para conformidade

2. **Anonimização ao Invés de Exclusão:**
   - Logs são anonimizados (user_id removido ou substituído por hash)
   - Mantém rastreabilidade para auditoria sem identificar titular

3. **Prazo de Retenção Aplicado:**
   - Logs relacionados ao usuário são mantidos até completarem 6 meses
   - Após 6 meses, são automaticamente excluídos pelo script de limpeza

---

## 🔄 PROCESSO DE ANONIMIZAÇÃO

### Quando Usuário Solicita Exclusão

**Passo 1: Exclusão de Dados Pessoais**
- Excluir dados de `users` e `user_consent`
- Registrar ação em audit log (antes da anonimização)

**Passo 2: Anonimização de Logs**
- Atualizar logs de auditoria relacionados:
  ```sql
  UPDATE data_audit_log 
  SET user_id = NULL,  -- ou hash anônimo
      details = JSON_SET(details, '$.anonymized', TRUE)
  WHERE user_id = [USER_ID]
  ```

**Passo 3: Retenção por 6 Meses**
- Logs anonimizados são mantidos por 6 meses
- Após período, são excluídos automaticamente

---

## 📝 DOCUMENTAÇÃO PARA O USUÁRIO

### No Comando `/delete_my_data`

**Mensagem atualizada:**
```
⚠️ IMPORTANTE: O que será excluído:

✅ Dados pessoais (pontos, ranks, progresso)
✅ Registro de consentimento
⚠️ Logs de auditoria serão anonimizados e mantidos por 6 meses
   (necessário para conformidade legal - LGPD Art. 10)

Após 6 meses, todos os registros serão permanentemente excluídos.
```

---

## 🎯 ALTERNATIVAS CONSIDERADAS

### Opção 1: Exclusão Imediata de Logs (REJEITADA)

**Motivo:**
- Viola LGPD Art. 10 (Registro de Atividades)
- Remove capacidade de auditoria
- Risco de não-conformidade

---

### Opção 2: Anonimização com Retenção (APROVADA)

**Vantagens:**
- Cumpre direito ao esquecimento (dados pessoais removidos)
- Mantém capacidade de auditoria (logs anonimizados)
- Base legal clara (Art. 7º, II)
- Prazo definido (6 meses)

---

### Opção 3: Retenção Indefinida (REJEITADA)

**Motivo:**
- Viola LGPD Art. 15 (Prazo de Retenção)
- Sem base legal para retenção indefinida

---

## ✅ CHECKLIST DE CONFORMIDADE

- [x] Política de retenção documentada
- [x] Base legal identificada (Art. 7º, II)
- [x] Processo de anonimização definido
- [ ] Implementar anonimização em código (pendente)
- [x] Comunicação ao usuário atualizada
- [x] Script de limpeza automática implementado

---

## 📚 REFERÊNCIAS LEGAIS

- **LGPD Art. 7º, II:** Base Legal - Cumprimento de obrigação legal
- **LGPD Art. 10:** Registro de atividades
- **LGPD Art. 15:** Prazo de retenção
- **LGPD Art. 18, VI:** Direito ao esquecimento

---

**Última atualização:** 2025-10-31  
**Versão:** 1.0  
**Status:** ✅ Documentado | ⚠️ Implementação de anonimização pendente

