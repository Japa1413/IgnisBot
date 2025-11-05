# 🧪 GUIA PARA EXPANDIR COBERTURA DE TESTES - IGNISBOT

**Versão:** 1.0  
**Data:** 2025-10-31  
**Objetivo:** Aumentar cobertura de testes de ~30% para 80%

---

## 📊 SITUAÇÃO ATUAL

### Testes Existentes

**Arquivos:**
- `tests/test_points_service.py` - 3 testes
- `tests/test_user_repository.py` - 4 testes
- `tests/test_cache_service.py` - 6 testes

**Total:** ~13 testes

**Cobertura Estimada:** ~30%

---

## 🎯 PLANO DE EXPANSÃO

### Fase 1: Serviços Críticos (16 horas)

#### 1.1 Expandir `test_points_service.py`

**Testes Atuais:**
- ✅ `test_add_points`
- ✅ `test_remove_points`
- ✅ `test_remove_points_user_not_found`

**Testes a Adicionar:**
- [ ] `test_add_points_without_consent` - Validação LGPD
- [ ] `test_remove_points_without_consent` - Validação LGPD
- [ ] `test_add_points_check_consent_false` - Bypass de consentimento
- [ ] `test_remove_points_check_consent_false` - Bypass de consentimento
- [ ] `test_add_points_creates_transaction` - Estrutura de retorno
- [ ] `test_remove_points_dispatches_event` - Integração com eventos

**Esforço:** 4 horas

---

#### 1.2 Criar `test_consent_service.py`

**Testes a Criar:**
- [ ] `test_has_consent_true`
- [ ] `test_has_consent_false`
- [ ] `test_has_consent_none`
- [ ] `test_grant_consent`
- [ ] `test_revoke_consent`
- [ ] `test_consent_version_check`
- [ ] `test_consent_expired`

**Esforço:** 4 horas

---

#### 1.3 Criar `test_audit_service.py`

**Testes a Criar:**
- [ ] `test_log_operation`
- [ ] `test_log_operation_with_details`
- [ ] `test_log_operation_performed_by`
- [ ] `test_log_operation_error_handling`

**Esforço:** 2 horas

---

#### 1.4 Criar `test_user_service.py`

**Testes a Criar:**
- [ ] `test_get_user_cache_hit`
- [ ] `test_get_user_cache_miss`
- [ ] `test_ensure_exists_new_user`
- [ ] `test_ensure_exists_existing_user`

**Esforço:** 3 horas

---

#### 1.5 Expandir `test_cache_service.py`

**Testes a Adicionar:**
- [ ] `test_cache_ttl_expiration`
- [ ] `test_cache_statistics_reset`
- [ ] `test_cache_concurrent_access`
- [ ] `test_cache_multiple_users`

**Esforço:** 3 horas

---

### Fase 2: Repositórios (12 horas)

#### 2.1 Expandir `test_user_repository.py`

**Testes a Adicionar:**
- [ ] `test_get_user_without_cache`
- [ ] `test_get_or_create_existing`
- [ ] `test_get_or_create_new`
- [ ] `test_update_points_negative`
- [ ] `test_update_points_large_value`
- [ ] `test_get_all_leaderboard`

**Esforço:** 4 horas

---

#### 2.2 Criar `test_audit_repository.py`

**Testes a Criar:**
- [ ] `test_create_audit_log`
- [ ] `test_create_audit_log_with_details`
- [ ] `test_get_audit_history`
- [ ] `test_cleanup_old_logs`

**Esforço:** 3 horas

---

#### 2.3 Criar `test_consent_repository.py`

**Testes a Criar:**
- [ ] `test_get_consent`
- [ ] `test_create_consent`
- [ ] `test_update_consent`
- [ ] `test_revoke_consent`
- [ ] `test_consent_version`

**Esforço:** 3 horas

---

#### 2.4 Criar `test_base_repository.py`

**Testes a Criar:**
- [ ] `test_execute_query_fetch_one`
- [ ] `test_execute_query_fetch_all`
- [ ] `test_execute_query_as_dict`
- [ ] `test_execute_query_error_handling`

**Esforço:** 2 horas

---

### Fase 3: Integração COGs (8 horas)

#### 3.1 Criar `test_add_cog.py`

**Testes a Criar:**
- [ ] `test_add_points_success`
- [ ] `test_add_points_consent_error`
- [ ] `test_add_points_validation_error`
- [ ] `test_add_points_event_dispatch`

**Esforço:** 2 horas

---

#### 3.2 Criar `test_remove_cog.py`

**Testes a Criar:**
- [ ] `test_remove_points_success`
- [ ] `test_remove_points_user_not_found`
- [ ] `test_remove_points_consent_error`

**Esforço:** 2 horas

---

#### 3.3 Criar `test_data_privacy_cog.py`

**Testes a Criar:**
- [ ] `test_export_my_data`
- [ ] `test_delete_my_data_confirmation`
- [ ] `test_delete_my_data_execution`
- [ ] `test_consent_grant`
- [ ] `test_consent_revoke`
- [ ] `test_correct_my_data`

**Esforço:** 4 horas

---

### Fase 4: Testes de Integração (6 horas)

#### 4.1 Criar `test_integration_points_flow.py`

**Cenários:**
- [ ] Fluxo completo: Add → Verify → Remove → Verify
- [ ] Fluxo com cache: Add → Cache hit → Verify
- [ ] Fluxo com audit: Add → Verify audit log
- [ ] Fluxo com consent: Grant → Add → Verify

**Esforço:** 3 horas

---

#### 4.2 Criar `test_integration_lgpd_flow.py`

**Cenários:**
- [ ] Fluxo completo: Grant → Export → Correct → Revoke → Delete
- [ ] Verificar rastreabilidade em cada passo

**Esforço:** 3 horas

---

## 📊 MÉTRICAS DE SUCESSO

### Cobertura por Módulo

| Módulo | Meta | Status Atual | Ações |
|--------|------|--------------|-------|
| `services/` | 80% | ~40% | Expandir testes existentes |
| `repositories/` | 85% | ~30% | Criar novos arquivos |
| `cogs/` | 70% | 0% | Criar testes de integração |
| `utils/` | 60% | 0% | Criar testes básicos |

**Cobertura Geral Meta:** 80%

---

## 🛠️ FERRAMENTAS E CONFIGURAÇÃO

### pytest.ini

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --cov=services
    --cov=repositories
    --cov=cogs
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
```

### requirements-dev.txt

Já inclui:
- ✅ pytest>=7.4.0
- ✅ pytest-asyncio>=0.21.0
- ✅ pytest-cov>=4.1.0
- ✅ pytest-mock>=3.12.0

---

## 📝 TEMPLATE DE TESTE

### Para Services

```python
"""Test template for services"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from domain.protocols import UserRepositoryProtocol

@pytest.fixture
def mock_dependencies():
    """Create mocked dependencies"""
    mock_repo = MagicMock(spec=UserRepositoryProtocol)
    mock_repo.get = AsyncMock(return_value={"user_id": 123, "points": 100})
    return {"user_repo": mock_repo}


@pytest.mark.asyncio
async def test_service_method(mock_dependencies):
    """Test description"""
    # Arrange
    service = ServiceClass(**mock_dependencies)
    
    # Act
    result = await service.method_under_test()
    
    # Assert
    assert result is not None
    mock_dependencies["user_repo"].get.assert_called_once()
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### Infraestrutura
- [x] pytest configurado
- [x] Protocols criados para DI
- [x] Testes básicos existem
- [ ] CI/CD configurado (pendente)

### Testes Unitários
- [ ] Serviços expandidos
- [ ] Repositórios completos
- [ ] Utils básicos

### Testes de Integração
- [ ] Fluxos principais testados
- [ ] Fluxos LGPD testados

---

## 🎯 PRIORIZAÇÃO

### Prioridade 🔴 Crítica (Esta Semana)
1. Expandir `test_points_service.py` (validação LGPD)
2. Criar `test_consent_service.py` (LGPD crítico)
3. Expandir `test_user_repository.py` (base de tudo)

### Prioridade 🟡 Alta (Próximas 2 Semanas)
4. Criar testes de repositórios restantes
5. Criar testes básicos de COGs
6. Testes de integração principais

### Prioridade 🟢 Média (Próximo Mês)
7. Testes de edge cases
8. Testes de performance
9. Testes de stress

---

## 📚 RECURSOS

### Documentação
- [`domain/protocols.py`](../../domain/protocols.py) - Protocols para mocks
- [`pytest.ini`](../../pytest.ini) - Configuração pytest
- [`tests/`](../../tests/) - Testes existentes como referência

### Exemplos
- `tests/test_points_service.py` - Exemplo de teste com DI
- `tests/test_cache_service.py` - Exemplo de teste assíncrono

---

**Última atualização:** 2025-10-31  
**Versão:** 1.0  
**Meta:** 80% cobertura em 6 semanas

