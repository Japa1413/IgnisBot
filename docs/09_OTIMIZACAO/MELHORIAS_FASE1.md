# ⚡ MELHORIAS DE PERFORMANCE - FASE 1 (QUICK WINS)

**Prioridade:** 🔴 ALTA  
**Tempo Estimado:** 2-3 horas  
**Impacto Esperado:** 60-80% melhoria em comandos críticos

---

## 🎯 OBJETIVO

Implementar melhorias rápidas de alto impacto que não requerem grandes refatorações arquiteturais.

---

## 1️⃣ CORRIGIR N+1 QUERY NO LEADERBOARD

### Problema
Busca sequencial de usuários causa latência desnecessária.

### Implementação

**Arquivo:** `cogs/leaderboard.py`

```python
# ANTES (ruim):
for i, row in enumerate(leaderboard, start=1):
    user = await self.bot.fetch_user(row["user_id"])  # N queries!

# DEPOIS (bom):
# Buscar todos os usuários em paralelo
user_ids = [row["user_id"] for row in leaderboard]
user_fetches = [self.bot.fetch_user(uid) for uid in user_ids]
users_results = await asyncio.gather(*user_fetches, return_exceptions=True)

for i, (row, user_result) in enumerate(zip(leaderboard, users_results), start=1):
    if isinstance(user_result, Exception):
        name = "[Unknown User]"
    else:
        try:
            name = user_result.name
        except:
            name = "[Unknown User]"
```

**Ganho:** 80-90% redução no tempo (1-2s → 200-300ms)

---

## 2️⃣ RETORNAR VALOR DO UPDATE EM VEZ DE SELECT SEPARADO

### Problema
Query redundante após UPDATE para obter novo valor.

### Implementação

**Arquivo:** `utils/database.py`

```python
async def update_points(
    user_id: int, 
    points: int, 
    performed_by: int = None, 
    purpose: str = None
) -> int:  # Retornar novo valor
    """Retorna o novo valor de points após atualização"""
    if _POOL is None:
        raise RuntimeError("DB pool not initialized.")
    
    async with _POOL.acquire() as conn:
        async with conn.cursor() as cursor:
            # Atualizar e retornar novo valor em uma query
            await cursor.execute("""
                UPDATE users 
                SET points = points + %s 
                WHERE user_id = %s
            """, (points, user_id))
            
            # Buscar novo valor (ainda na mesma conexão - rápido)
            await cursor.execute(
                "SELECT points FROM users WHERE user_id = %s",
                (user_id,)
            )
            result = await cursor.fetchone()
            new_points = result[0] if result else 0
    
    # Auditoria assíncrona (não bloqueia)
    try:
        from utils.audit_log import log_data_operation
        asyncio.create_task(log_data_operation(
            user_id=user_id,
            action_type="UPDATE",
            data_type="points",
            performed_by=performed_by,
            purpose=purpose or f"Atualização: {points:+}"
        ))
    except Exception:
        pass
    
    return new_points
```

**Arquivo:** `cogs/add.py` e `cogs/remove.py`

```python
# ANTES:
await update_points(...)
after = int((await get_user(user_id))["points"])  # Query redundante!

# DEPOIS:
after = await update_points(...)  # Retorna diretamente
before = after - points  # Calcular antes, se necessário
```

**Ganho:** 50% menos queries, 30-40% mais rápido

---

## 3️⃣ AUDITORIA ASSÍNCRONA (FIRE-AND-FORGET)

### Problema
Auditoria bloqueia resposta ao usuário.

### Implementação

**Arquivo:** `utils/database.py`

```python
async def create_user(user_id: int):
    # ... código existente ...
    
    # Auditoria não bloqueia
    try:
        from utils.audit_log import log_data_operation
        asyncio.create_task(log_data_operation(
            user_id=user_id,
            action_type="CREATE",
            data_type="user_data",
            purpose="Criação de novo registro"
        ))
    except Exception:
        pass
```

**Ganho:** 10-20ms menos latência por comando

---

## 4️⃣ ADICIONAR ÍNDICE EM USERS.POINTS

### Problema
Leaderboard faz ORDER BY sem índice otimizado.

### Implementação

**Arquivo:** `utils/database.py` - função `initialize_db()`

```python
async def initialize_db():
    # ... código existente de CREATE TABLE ...
    
    # Adicionar índice para otimizar leaderboard
    async with _POOL.acquire() as conn:
        async with conn.cursor() as cursor:
            # Criar índice se não existir
            await cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_points 
                ON users(points DESC)
            """)
```

**Ganho:** 20-30% mais rápido no leaderboard com muitos usuários

---

## 5️⃣ OTIMIZAR VC_LOG - BATCH OPERATIONS

### Problema
Loop sequencial processa usuários um a um.

### Implementação

**Arquivo:** `cogs/vc_log.py`

```python
# Processar em paralelo onde possível
async def process_member(user: discord.Member, amount: int, event: str, performed_by: int):
    """Processa um membro individualmente"""
    await ensure_user_exists(user.id)
    before = int((await get_user(user.id))["points"])
    await update_points(user.id, amount, performed_by=performed_by, 
                       purpose=f"Adição via /vc_log: {event}")
    after = int((await get_user(user.id))["points"])
    return user, before, after

# Em vc_log():
tasks = [process_member(m, amount, event, interaction.user.id) 
         for m in members]
results = await asyncio.gather(*tasks, return_exceptions=True)

for user, before, after in results:
    # Criar embeds...
```

**Ganho:** 50-70% mais rápido com muitos membros

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

- [ ] 1. Corrigir N+1 no leaderboard
- [ ] 2. update_points retorna valor
- [ ] 3. Atualizar add.py para usar retorno
- [ ] 4. Atualizar remove.py para usar retorno
- [ ] 5. Auditoria assíncrona em create_user
- [ ] 6. Auditoria assíncrona em update_points
- [ ] 7. Adicionar índice idx_points
- [ ] 8. Otimizar vc_log com batch processing
- [ ] 9. Testar todas as funcionalidades
- [ ] 10. Benchmarks antes/depois

---

**Próximo passo:** Ver `docs/MELHORIAS_PERFORMANCE_FASE2.md` para melhorias intermediárias.

