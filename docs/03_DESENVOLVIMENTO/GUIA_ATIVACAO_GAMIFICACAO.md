# 🚀 GUIA DE ATIVAÇÃO: SISTEMA DE GAMIFICAÇÃO (FASE 1)

**Data:** 2025-10-31  
**Status:** ✅ **PRONTO PARA ATIVAÇÃO**

---

## 📋 PRÉ-REQUISITOS

- [x] Banco de dados MySQL configurado
- [x] Bot Discord configurado
- [x] Variáveis de ambiente configuradas (`.env`)

---

## ✅ ETAPAS DE ATIVAÇÃO

### 1. Atualizar Banco de Dados

As tabelas serão criadas automaticamente na próxima inicialização do bot (já integrado em `utils/database.py`).

**Ou execute manualmente:**
```bash
mysql -u ignis_user -p ignis < migrations/001_gamification_core.sql
```

---

### 2. Executar Migração de Dados

Converte pontos existentes para XP (1:1):

```bash
python scripts/migrate_to_gamification.py
```

**O que faz:**
- Converte `users.points` → `user_progression.total_xp`
- Calcula nível inicial baseado em XP
- Cria entries em `user_progression`
- Preserva ranks existentes

---

### 3. Iniciar Bot

O bot já está configurado para carregar os gamification handlers automaticamente.

```bash
python ignis_main.py
```

**Verificar no log:**
```
✅ Gamification handlers loaded (XP system active)
```

---

### 4. Validar Funcionamento

**Testar XP por Mensagens:**
1. Envie uma mensagem no servidor
2. Verifique logs: `User {id} gained 1 XP (source: message)`
3. Verifique banco: `SELECT * FROM xp_events WHERE source = 'message' LIMIT 10`

**Testar XP por Voice:**
1. Entre em um voice channel
2. Fique por 2 minutos
3. Saia do voice channel
4. Verifique logs: `User {id} gained 20 XP (2 min in VC)`
5. Verifique banco: `SELECT * FROM xp_events WHERE source = 'voice' LIMIT 10`

**Verificar Níveis:**
```sql
SELECT user_id, total_xp, current_level 
FROM user_progression 
ORDER BY total_xp DESC 
LIMIT 10;
```

---

## 🔧 CONFIGURAÇÕES

### XP Rates (editável em `services/xp_service.py`):

```python
XP_RATES = {
    "voice_per_minute": 10,  # Ajuste conforme necessário
    "message": 1,
}
```

### Daily Limits (editável em `events/gamification_handlers.py`):

```python
DAILY_XP_LIMITS = {
    "voice": 500,   # Max 500 XP/dia de voice
    "message": 50,  # Max 50 XP/dia de messages
}
```

---

## 📊 MONITORAMENTO

### Queries Úteis

**XP Total por Usuário:**
```sql
SELECT u.user_id, up.total_xp, up.current_level, u.points
FROM users u
LEFT JOIN user_progression up ON u.user_id = up.user_id
ORDER BY up.total_xp DESC
LIMIT 20;
```

**XP Ganho Hoje:**
```sql
SELECT user_id, SUM(xp_amount) as xp_today
FROM xp_events
WHERE DATE(timestamp) = CURDATE()
GROUP BY user_id
ORDER BY xp_today DESC
LIMIT 10;
```

**Level Ups Recentes:**
```sql
SELECT user_id, current_level, last_level_up
FROM user_progression
WHERE last_level_up IS NOT NULL
ORDER BY last_level_up DESC
LIMIT 10;
```

---

## ⚠️ NOTAS IMPORTANTES

1. **Compatibilidade:**
   - Sistema de pontos antigo continua funcionando
   - XP é separado e complementar
   - Ranks ainda baseados em pontos (será atualizado na Fase 5)

2. **Performance:**
   - Event handlers são assíncronos e não bloqueiam
   - Daily limits são verificados rapidamente (índices)
   - Level calculations são otimizadas

3. **LGPD:**
   - Validação de consentimento em todos os handlers
   - Falha silenciosa se sem consentimento
   - Audit logging via `xp_events`

4. **Conflitos:**
   - `on_voice_state_update` no `ignis_main.py` continua funcionando
   - Nossos handlers trabalham em paralelo (não interferem)

---

## 🐛 TROUBLESHOOTING

### XP não está sendo ganho

1. **Verificar logs:**
   - Procure por `Error awarding message XP` ou `Error awarding voice XP`
   - Verifique se handlers foram carregados

2. **Verificar consentimento:**
   ```sql
   SELECT * FROM user_consent WHERE user_id = {SEU_USER_ID};
   ```
   - Usuário precisa ter `consent_given = TRUE`

3. **Verificar daily limits:**
   ```sql
   SELECT * FROM daily_xp_limits 
   WHERE user_id = {SEU_USER_ID} AND date = CURDATE();
   ```
   - Se atingiu limite, não ganhará mais XP hoje

### Níveis não estão atualizando

1. **Verificar XP total:**
   ```sql
   SELECT total_xp, current_level FROM user_progression WHERE user_id = {ID};
   ```

2. **Calcular nível manualmente:**
   ```python
   from services.level_service import level_from_xp
   level, xp_in, xp_next = level_from_xp(total_xp)
   ```

---

## ✅ CHECKLIST DE VALIDAÇÃO

Após ativação, verificar:

- [ ] Tabelas criadas no banco (`user_progression`, `xp_events`, etc.)
- [ ] Handler carregado (log: "Gamification handlers loaded")
- [ ] XP sendo ganho por mensagens (verificar `xp_events`)
- [ ] XP sendo ganho por voice (verificar `xp_events`)
- [ ] Daily limits funcionando (testar >50 mensagens, >50 min VC)
- [ ] Level ups detectados (verificar `last_level_up`)
- [ ] Consentimento validado (usuários sem consent não ganham XP)
- [ ] Performance OK (bot não está lento)

---

**Status:** ✅ **PRONTO PARA ATIVAÇÃO**  
**Próxima Fase:** Achievements System (Fase 2)

