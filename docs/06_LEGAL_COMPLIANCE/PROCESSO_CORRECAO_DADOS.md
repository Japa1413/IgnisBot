# 📝 PROCESSO DE CORREÇÃO DE DADOS - IGNISBOT

**Versão:** 1.0  
**Última atualização:** 2025-10-31  
**Base Legal:** LGPD Art. 18, III (Direito de Correção)

---

## 📋 VISÃO GERAL

Este documento descreve o processo completo para exercer o direito de correção de dados (LGPD Art. 18, III).

---

## 🎯 COMANDO DISPONÍVEL

### `/correct_my_data`

**Descrição:** Solicitar correção de dados incorretos ou incompletos.

**Parâmetros:**
- `field`: Campo a corrigir (`points`, `rank`, `progress`)
- `current_value`: Valor atual (opcional, para referência)
- `correct_value`: Valor correto desejado
- `reason`: Motivo da correção (obrigatório)

**Exemplo:**
```
/correct_my_data field:points current_value:100 correct_value:150 reason:"Erro no cálculo de pontos do evento"
```

---

## 🔄 PROCESSO

### Passo 1: Solicitação do Usuário

1. Usuário executa `/correct_my_data`
2. Preenche campos obrigatórios
3. Sistema registra solicitação em audit log

**Tempo:** Imediato

---

### Passo 2: Revisão Administrativa

1. Administrador recebe notificação (via logs ou sistema)
2. Administrador analisa solicitação
3. Valida se correção é justificada

**SLA:** 72 horas (conforme LGPD Art. 8º, §3º)

---

### Passo 3: Aprovação/Rejeição

**Se Aprovado:**
- Administrador executa correção manual
- Dados são atualizados no banco
- Usuário recebe notificação de confirmação

**Se Rejeitado:**
- Administrador informa motivo
- Usuário pode solicitar revisão

**SLA:** 15 dias úteis (conforme LGPD Art. 18, §3º)

---

## ✅ CAMPOS QUE PODEM SER CORRIGIDOS

| Campo | Tipo | Processo | SLA |
|-------|------|----------|-----|
| **points** | Integer | Revisão administrativa | 15 dias úteis |
| **rank** | String | Revisão administrativa | 15 dias úteis |
| **progress** | Integer | Revisão administrativa | 15 dias úteis |

---

## 📝 REQUISITOS

### Justificativa Obrigatória

Todas as solicitações devem incluir:
- **Reason:** Motivo claro da correção
- **Evidence:** Recomenda-se evidência (screenshot, log, etc.)

### Campos Não Corrigíveis Automaticamente

- `user_id`: Identificador único (não pode ser alterado)
- `created_at`: Data de criação (imutável)
- `updated_at`: Atualizado automaticamente

---

## 🔍 VALIDAÇÃO

### Antes de Aprovar

Administrador deve verificar:
- [ ] Justificativa é válida
- [ ] Valor solicitado é razoável
- [ ] Não há tentativa de fraude
- [ ] Evidência foi fornecida (se aplicável)

---

## 📊 REGISTRO E AUDITORIA

### Audit Log

Todas as solicitações são registradas em `data_audit_log`:

```
action_type: "CORRECTION_REQUEST"
data_type: "[field]"
user_id: [USER_ID]
details: {
  "field": "[field]",
  "current_value": "[value]",
  "requested_value": "[value]",
  "reason": "[reason]",
  "status": "pending|approved|rejected"
}
```

---

## ⏱️ PRAZOS LEGAIS

### LGPD Art. 18, §3º

**Prazo máximo para resposta:** 15 dias úteis

**Começa a contar:** A partir do recebimento da solicitação

**Exceções:**
- Casos complexos podem ser estendidos por mais 15 dias (total 30)
- Usuário deve ser notificado da extensão

---

## 📧 COMUNICAÇÃO

### Notificação ao Usuário

**Após Solicitação:**
```
✅ Solicitação registrada
ID: #[ID]
Prazo de resposta: 15 dias úteis
```

**Após Aprovação:**
```
✅ Correção aprovada e aplicada
Campo: [field]
Novo valor: [value]
```

**Após Rejeição:**
```
❌ Correção rejeitada
Motivo: [reason]
```

---

## 🔄 APELAÇÃO

Se solicitação for rejeitada:

1. Usuário pode solicitar revisão
2. Fornecer evidências adicionais
3. Contatar DPO diretamente (`CONTROLLER_EMAIL`)

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [x] Comando `/correct_my_data` implementado
- [x] Registro em audit log
- [x] Processo documentado
- [ ] Sistema de aprovação automática (pendente)
- [x] SLA definido (15 dias úteis)
- [ ] Notificações automáticas (pendente)

---

## 📚 REFERÊNCIAS LEGAIS

- **LGPD Art. 18, III:** Direito de Correção
- **LGPD Art. 8º, §3º:** Prazo de Resposta
- **LGPD Art. 10:** Registro de Atividades

---

**Última atualização:** 2025-10-31  
**Versão:** 1.0

