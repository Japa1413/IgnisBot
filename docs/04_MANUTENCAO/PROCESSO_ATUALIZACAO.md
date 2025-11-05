# 🔄 PROCESSO DE ATUALIZAÇÃO - IGNISBOT

**Versão:** 1.0  
**Última atualização:** 2025-10-31

---

## 📋 VISÃO GERAL

Este documento detalha o processo passo-a-passo para atualizar dependências e componentes do IgnisBot de forma segura e controlada.

---

## 🎯 TIPOS DE ATUALIZAÇÃO

### 1. Patch Release (x.x.PATCH)
**Exemplo:** `discord.py 2.3.2 → 2.3.3`

- **Risco:** Muito baixo
- **Processo:** Simplificado
- **Tempo:** 15-30 minutos

### 2. Minor Release (x.MINOR.x)
**Exemplo:** `discord.py 2.3.x → 2.4.0`

- **Risco:** Baixo a médio
- **Processo:** Padrão
- **Tempo:** 1-2 horas

### 3. Major Release (MAJOR.x.x)
**Exemplo:** `Python 3.11 → 3.12`

- **Risco:** Alto
- **Processo:** Completo
- **Tempo:** 1-4 semanas

---

## 📝 PROCESSO PADRÃO (Minor Releases)

### Fase 1: Preparação (15 min)

#### 1.1 Verificar Informações

```bash
# Verificar versão atual
pip show <package>

# Verificar versão disponível
pip index versions <package>

# Ler changelog
# Visitar: https://github.com/<repo>/releases
```

#### 1.2 Avaliar Impacto

- [ ] Ler changelog completo
- [ ] Identificar breaking changes
- [ ] Verificar compatibilidade
- [ ] Avaliar benefícios vs. riscos

#### 1.3 Criar Branch

```bash
git checkout -b chore/update-<package>-<version>
```

---

### Fase 2: Implementação (30-60 min)

#### 2.1 Ambiente de Teste

```bash
# Criar venv de teste
python -m venv test_env
test_env\Scripts\activate

# Instalar dependências atuais
pip install -r requirements.txt
```

#### 2.2 Atualizar Dependência

```bash
# Atualizar pacote específico
pip install <package>==<version>

# OU atualizar todas (cuidado!)
pip install -r requirements.txt --upgrade
```

#### 2.3 Atualizar Requirements

```bash
# Gerar novo requirements
pip freeze > requirements.txt.new

# Comparar mudanças
diff requirements.txt requirements.txt.new

# Revisar e aprovar
# Se OK:
mv requirements.txt.new requirements.txt
```

---

### Fase 3: Testes (30-60 min)

#### 3.1 Testes Unitários

```bash
# Rodar todos os testes
pytest tests/ -v

# Verificar cobertura
pytest tests/ --cov=repositories --cov=services
```

**Critérios de Aprovação:**
- ✅ Todos os testes passando
- ✅ Cobertura mantida ou aumentada
- ✅ Sem novos warnings

#### 3.2 Testes de Integração

```bash
# Iniciar bot em modo de teste
python ignis_main.py

# Testar comandos principais:
# - /userinfo
# - /add
# - /remove
# - /vc_log
# - /leaderboard
# - /cache_stats
```

**Critérios de Aprovação:**
- ✅ Bot inicia sem erros
- ✅ Comandos funcionam corretamente
- ✅ Sem erros nos logs
- ✅ Performance aceitável

#### 3.3 Análise Estática

```bash
# Verificar segurança
bandit -r . -ll

# Verificar qualidade
pylint repositories/ services/

# Type checking
mypy repositories/ services/
```

**Critérios de Aprovação:**
- ✅ Sem vulnerabilidades críticas
- ✅ Sem erros de linting críticos
- ✅ Type checking OK

---

### Fase 4: Documentação (15 min)

#### 4.1 Atualizar CHANGELOG

```markdown
## [Unreleased]

### Changed
- Updated `discord.py` from 2.3.2 to 2.3.3
  - Fix: Memory leak em eventos
  - Perf: Melhoria em comandos slash
```

#### 4.2 Atualizar Documentação (se necessário)

- Atualizar versões em `docs/04_MANUTENCAO/MANUTENCAO_TECNOLOGIAS.md`
- Documentar breaking changes (se houver)
- Atualizar exemplos de código (se mudou)

---

### Fase 5: Deploy (30 min)

#### 5.1 Commit

```bash
git add requirements.txt
git add CHANGELOG.md
git commit -m "chore: update discord.py to 2.3.3

- Fix memory leak em eventos
- Melhoria de performance
- Todos os testes passando"
```

#### 5.2 Pull Request

- Criar PR no GitHub
- Adicionar descrição detalhada
- Linkar changelog
- Revisar código

**Template:**
```markdown
## Atualização: discord.py 2.3.2 → 2.3.3

### Mudanças
- [Item 1]
- [Item 2]

### Testes
- [x] Testes unitários passando
- [x] Testes de integração OK
- [x] Análise estática OK
- [x] Teste manual dos comandos

### Impacto
- Nenhum (compatível)
- Performance melhorada

### Checklist
- [ ] CHANGELOG atualizado
- [ ] Documentação atualizada
- [ ] Testes passando
- [ ] Sem breaking changes
```

#### 5.3 Merge e Deploy

```bash
# Após aprovação
git checkout main
git pull
git merge chore/update-<package>-<version>
git push

# Deploy (se aplicável)
```

#### 5.4 Monitoramento Pós-Deploy

**Primeira hora:**
- [ ] Bot online
- [ ] Sem erros nos logs
- [ ] Comandos funcionando

**Primeiro dia:**
- [ ] Performance mantida
- [ ] Sem incidentes
- [ ] Métricas OK

---

## 🚨 PROCESSO PARA MAJOR RELEASES

### Diferenças do Processo Padrão

#### 1. Análise Profunda (1-2 dias)

- [ ] Ler TODA a documentação
- [ ] Identificar TODOS os breaking changes
- [ ] Criar lista de mudanças necessárias
- [ ] Estimar esforço (em horas)

#### 2. Plano de Migração (1 dia)

```markdown
## Plano de Migração: Python 3.11 → 3.12

### Breaking Changes
1. Item 1
2. Item 2

### Mudanças Necessárias
- [ ] Arquivo X: Mudança Y
- [ ] Arquivo Z: Mudança W

### Estimativa
- Desenvolvimento: X horas
- Testes: Y horas
- Total: Z horas

### Riscos
- Risco 1: Mitigação
- Risco 2: Mitigação

### Rollback Plan
- Como reverter se necessário
- Backup dos dados
- Versão anterior disponível
```

#### 3. Implementação (1-2 semanas)

- Implementar mudanças gradualmente
- Commits pequenos e frequentes
- Testar após cada mudança
- Documentar progresso

#### 4. Testes Extensivos (3-5 dias)

- Todos os testes unitários
- Testes de integração completos
- Testes de carga
- Testes em staging
- Beta testing (se aplicável)

#### 5. Deploy Gradual

- Deploy em staging primeiro
- Monitorar por 1 semana
- Deploy em produção
- Monitorar intensivamente

---

## 🔄 ROLLBACK PROCEDURE

### Quando Fazer Rollback

- Erros críticos após deploy
- Performance degradada > 20%
- Vulnerabilidades introduzidas
- Incompatibilidade identificada

### Processo de Rollback

#### 1. Identificar Versão Anterior

```bash
# Verificar último commit estável
git log --oneline

# Identificar commit antes da atualização
git checkout <commit-hash>
```

#### 2. Reverter Dependências

```bash
# Reverter requirements.txt
git checkout HEAD -- requirements.txt

# Reinstalar versões anteriores
pip install -r requirements.txt
```

#### 3. Verificar e Deploy

```bash
# Testar versão anterior
pytest tests/
python ignis_main.py

# Se OK, fazer rollback
git revert <commit-hash>
git push
```

#### 4. Documentar Rollback

```markdown
## Rollback: discord.py 2.3.3 → 2.3.2

**Data:** 2025-11-01
**Motivo:** Erro crítico em eventos
**Status:** ✅ Rollback bem-sucedido

### Problema
- Descrição do problema

### Ação
- Versão revertida para 2.3.2
- Bot funcionando normalmente

### Próximos Passos
- Investigar problema
- Corrigir em próximo update
```

---

## 📊 MÉTRICAS DE SUCESSO

### Critérios de Aprovação

| Métrica | Target | Crítico |
|---------|--------|---------|
| **Testes passando** | 100% | < 100% |
| **Performance** | Mantida | Degradada > 10% |
| **Erros** | 0 | > 0 |
| **Vulnerabilidades** | 0 críticas | > 0 |

---

## ✅ CHECKLIST COMPLETO

### Pré-Atualização
- [ ] Changelog lido
- [ ] Breaking changes identificados
- [ ] Impacto avaliado
- [ ] Branch criado

### Atualização
- [ ] Dependência atualizada
- [ ] Requirements atualizados
- [ ] Testes unitários passando
- [ ] Testes de integração OK
- [ ] Análise estática OK

### Pós-Atualização
- [ ] CHANGELOG atualizado
- [ ] Documentação atualizada
- [ ] PR criado e revisado
- [ ] Deploy realizado
- [ ] Monitoramento ativo

---

**Última atualização:** 2025-10-31  
**Versão:** 1.0

