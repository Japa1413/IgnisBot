# 📋 PLANO DE DEPRECAÇÃO - IGNISBOT

**Versão:** 1.0  
**Última atualização:** 2025-10-31  
**Objetivo:** Remover código legado de forma segura e controlada

---

## 📊 SITUAÇÃO ATUAL

### Código Deprecated

**Localização:** `utils/database.py`

**Funções Deprecated:**
1. `get_user()` - Substituir por `UserRepository.get()`
2. `create_user()` - Substituir por `UserRepository.create()`
3. `update_points()` - Substituir por `UserRepository.update_points()`

**Razão da Deprecação:**
- Migração para arquitetura Layered (Repository Pattern)
- Melhor separação de responsabilidades
- Cache integrado automaticamente
- Melhor testabilidade

---

## 🎯 PLANO DE REMOÇÃO

### Fase 1: Identificação de Uso (CONCLUÍDA)

**Status:** ✅ **COMPLETO**

**Resultado:**
- Todas as referências identificadas
- Código migrado para nova arquitetura
- Funções mantidas apenas para compatibilidade

---

### Fase 2: Adicionar Warnings de Runtime

**Status:** 🟡 **PENDENTE**

**Ação:**
Adicionar avisos de runtime quando funções deprecated são usadas.

**Prazo:** 2025-11-15

**Código:**
```python
import warnings
warnings.warn(
    "get_user() is deprecated. Use UserRepository.get() instead.",
    DeprecationWarning,
    stacklevel=2
)
```

---

### Fase 3: Migração Completa

**Status:** 🟡 **EM PROGRESSO**

**Uso Identificado:**
- ✅ COGs migrados para `PointsService` / `UserService`
- ✅ Services migrados para Repositories
- ⚠️ Verificar código legado restante

**Prazo:** 2025-11-30

---

### Fase 4: Remoção (Data Alvo)

**Status:** 🟡 **PENDENTE**

**Data de Remoção:** 2025-12-31 (3 meses após warning)

**Ações:**
1. Remover funções deprecated de `utils/database.py`
2. Manter apenas `initialize_db()` e `get_pool()`
3. Atualizar documentação
4. Executar testes completos

---

## 📝 CHECKLIST DE REMOÇÃO

### Pré-requisitos
- [ ] Todos os COGs migrados
- [ ] Todos os Services migrados
- [ ] Nenhum uso direto de funções deprecated
- [ ] Testes passando 100%
- [ ] Warnings de runtime adicionados (mínimo 1 mês)

### Remoção
- [ ] Criar branch `remove-deprecated-code`
- [ ] Remover funções deprecated
- [ ] Atualizar imports se necessário
- [ ] Executar testes
- [ ] Atualizar documentação
- [ ] Merge após aprovação

---

## ⚠️ RISCOS

### Risco: Código Quebrado

**Mitigação:**
- Warnings de runtime por 3 meses antes da remoção
- Testes extensivos antes de remover
- Rollback plan documentado

### Risco: Extensões Externas

**Mitigação:**
- Comunicar mudanças com antecedência
- Documentar alternativas
- Fornecer período de transição

---

**Última atualização:** 2025-10-31  
**Próxima revisão:** 2025-11-15

