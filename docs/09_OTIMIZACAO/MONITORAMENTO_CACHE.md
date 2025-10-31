# 📊 MONITORAMENTO DE CACHE - FASE 2

**Data:** 2025-10-31  
**Status:** 🔄 Implementado

---

## 🎯 OBJETIVO

Documentar como monitorar e validar o sistema de cache implementado na Fase 2.

---

## 📈 ESTATÍSTICAS DE CACHE

### Como Obter Estatísticas

```python
from utils.cache import get_cache_stats

# Obter estatísticas atuais
stats = get_cache_stats()
print(f"Cache Hit Rate: {stats['hit_rate']}")
print(f"Hits: {stats['hits']}")
print(f"Misses: {stats['misses']}")
print(f"Entries: {stats['entries']}")
```

### Interpretação

- **Hit Rate:** Percentual de requisições atendidas pelo cache
- **Hits:** Número de vezes que o cache forneceu dados
- **Misses:** Número de vezes que foi necessário buscar no banco
- **Entries:** Número de usuários atualmente em cache

---

## 🧪 TESTES RECOMENDADOS

### Teste 1: Verificar Cache Hit
1. Execute `/userinfo @user` pela primeira vez (cache miss)
2. Execute `/userinfo @user` novamente dentro de 30 segundos (cache hit)
3. Verifique logs - segunda execução deve ser mais rápida

### Teste 2: Verificar Invalidação
1. Execute `/add @user 10`
2. Execute `/userinfo @user` imediatamente
3. Deve mostrar dados atualizados (cache foi invalidado)

### Teste 3: Monitorar Hit Rate
1. Execute vários comandos que usam `get_user()`
2. Use `get_cache_stats()` para verificar hit rate
3. Esperado: 60-80% após uso repetido

---

## 📊 MÉTRICAS ESPERADAS

### Após Uso Normal (1 hora)
- **Hit Rate:** 60-80%
- **Hits:** Varia conforme uso
- **Misses:** Varia conforme uso
- **Entries:** ~10-50 usuários (depende da atividade)

---

## 🔧 CONFIGURAÇÃO

### TTL do Cache
```python
from utils.cache import set_cache_ttl

# Alterar TTL para 60 segundos (padrão: 30)
set_cache_ttl(60)
```

### Limpar Cache Manualmente
```python
from utils.cache import clear_cache

# Limpar todo o cache
clear_cache()
```

---

## 📝 LOGS

O cache gera logs de debug:
- `Cache hit para user_id {id}` - Quando dados vêm do cache
- `Cache miss para user_id {id}` - Quando precisa buscar no banco
- `Cache invalidado para user_id {id}` - Quando cache é invalidado

**Nível de log:** DEBUG

---

**Última atualização:** 2025-10-31

