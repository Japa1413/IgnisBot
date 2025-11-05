# 🗑️ LIMPEZA DE LOGS DE AUDITORIA - IGNISBOT

**Versão:** 1.0  
**Última atualização:** 2025-10-31  
**Base Legal:** LGPD Art. 15 (Prazo de Retenção)

---

## 📋 VISÃO GERAL

Este documento descreve o processo de limpeza automática de logs de auditoria conforme política de retenção de dados (6 meses).

---

## 🎯 OBJETIVO

Garantir conformidade com LGPD Art. 15 removendo automaticamente logs de auditoria que excedem o prazo de retenção estabelecido (6 meses).

---

## ⚙️ IMPLEMENTAÇÃO

### Script de Limpeza

**Arquivo:** `scripts/cleanup_audit_logs.py`

**Funcionalidade:**
- Remove logs de auditoria (`data_audit_log`) com mais de 180 dias (6 meses)
- Registra quantidade de registros deletados
- Logging detalhado da operação

### Execução Manual

```bash
python scripts/cleanup_audit_logs.py
```

### Execução Automática (Recomendado)

#### Linux/Mac (Cron)

```bash
# Editar crontab
crontab -e

# Adicionar linha (executa diariamente às 02:00)
0 2 * * * cd /path/to/IgnisBot && /usr/bin/python3 scripts/cleanup_audit_logs.py >> logs/cleanup.log 2>&1
```

#### Windows (Task Scheduler)

1. Abrir Task Scheduler
2. Criar tarefa básica
3. Configurar:
   - **Trigger:** Diariamente às 02:00
   - **Action:** Iniciar programa
   - **Programa:** `python`
   - **Argumentos:** `scripts/cleanup_audit_logs.py`
   - **Diretório de início:** `C:\Gabriel\github\IgnisBot`

#### Windows (PowerShell - Agendar)

```powershell
# Criar agendamento diário
$action = New-ScheduledTaskAction -Execute "python" -Argument "scripts\cleanup_audit_logs.py" -WorkingDirectory "C:\Gabriel\github\IgnisBot"
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName "IgnisBot-CleanupAuditLogs" -Action $action -Trigger $trigger -Description "Cleanup old audit logs"
```

---

## 📊 POLÍTICA DE RETENÇÃO

### Período de Retenção

- **Logs de Auditoria:** 6 meses (180 dias)
- **Base Legal:** LGPD Art. 15 + Art. 7º, II (Obrigação Legal)
- **Objetivo:** Auditoria e conformidade legal

### Exceções

**Nota:** Alguns logs podem precisar de retenção maior se:
- Investigação legal em andamento
- Obrigação legal específica
- Ordem judicial

---

## 🔍 MONITORAMENTO

### Logs do Script

O script gera logs em:
- Console (stdout)
- Sistema de logging do bot (se integrado)

**Formato:**
```
INFO: Cleaned up 150 audit log records older than 180 days (cutoff: 2025-04-30T00:00:00)
```

### Verificação Manual

```sql
-- Verificar logs antigos
SELECT COUNT(*) as old_logs
FROM data_audit_log
WHERE timestamp < DATE_SUB(NOW(), INTERVAL 180 DAY);

-- Verificar data do log mais antigo
SELECT MIN(timestamp) as oldest_log
FROM data_audit_log;
```

---

## ⚠️ CONSIDERAÇÕES IMPORTANTES

### Antes da Primeira Execução

- [ ] Verificar que backup de banco está configurado
- [ ] Validar que política de retenção está correta (6 meses)
- [ ] Testar script em ambiente de desenvolvimento
- [ ] Verificar permissões de execução

### Segurança

- ✅ Script usa conexão segura ao banco (via pool)
- ✅ Operação é transacional (DELETE seguro)
- ✅ Logging de todas as operações
- ⚠️ **Backup recomendado antes da primeira execução**

---

## 📝 CONFIGURAÇÃO

### Personalizar Período de Retenção

Editar `scripts/cleanup_audit_logs.py`:

```python
# Alterar período de retenção (padrão: 180 dias)
RETENTION_DAYS = 180  # Mudar para valor desejado
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [x] Script de limpeza criado
- [ ] Script testado em desenvolvimento
- [ ] Agendamento configurado (cron/Task Scheduler)
- [ ] Backup validado
- [ ] Primeira execução testada
- [ ] Monitoramento configurado

---

## 📚 REFERÊNCIAS

- **LGPD Art. 15:** Prazo de Retenção de Dados
- **LGPD Art. 7º, II:** Base Legal - Obrigação Legal (para retenção)
- **LGPD Art. 10:** Registro de Atividades (requisito de auditoria)

---

**Última atualização:** 2025-10-31  
**Versão:** 1.0

