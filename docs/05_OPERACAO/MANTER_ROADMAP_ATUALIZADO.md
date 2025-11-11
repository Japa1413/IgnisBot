# 📋 Como Manter Roadmap Sempre Atualizado

## 🎯 Objetivo

Garantir que o roadmap seja sempre postado automaticamente quando houver atualizações no projeto.

---

## ⚠️ Problema Identificado

O parser de roadmap não estava detectando atualizações porque:
1. As seções no `ROADMAP_MELHORIAS.md` não seguiam o formato esperado
2. O parser procura por seções específicas: "New Features", "Fixes & Improvements", "Upcoming Features"
3. O hash de conteúdo não mudava mesmo com atualizações

---

## ✅ Solução Implementada

### 1. Estrutura Corrigida no ROADMAP_MELHORIAS.md

O arquivo agora tem seções que o parser reconhece:

```markdown
## ✅ MELHORIAS IMPLEMENTADAS

### New Features
- Item 1
- Item 2

### Fixes & Improvements
- Fix 1
- Fix 2

## Upcoming Features
- Feature 1
- Feature 2
```

### 2. Script de Atualização Automática

Criado `scripts/atualizar_roadmap_automatico.py` que:
- Extrai informações do `CHANGELOG.md` (seção [Unreleased])
- Atualiza automaticamente as seções "New Features" e "Fixes & Improvements"
- Garante que o parser sempre encontre conteúdo atualizado

### 3. Correção no Código do Bot

Modificado `cogs/roadmap.py` para:
- Permitir postagem forçada mesmo se título já existe (quando `force_post=True`)
- Melhorar detecção de mudanças

---

## 📋 Processo para Manter Atualizado

### Sempre que Fizer Atualizações:

1. **Atualizar CHANGELOG.md:**
   - Adicione na seção `[Unreleased]`
   - Use as seções: `#### Added`, `#### Changed`, `#### Fixed`

2. **Executar Script de Atualização:**
   ```bash
   python scripts/atualizar_roadmap_automatico.py
   ```
   
   Isso atualizará automaticamente o `ROADMAP_MELHORIAS.md` com as informações do CHANGELOG.

3. **Commit e Push:**
   ```bash
   git add docs/02_ARQUITETURA/ROADMAP_MELHORIAS.md CHANGELOG.md
   git commit -m "Atualizar roadmap com novas features"
   git push origin main
   ```

4. **Reiniciar Bot (Opcional):**
   - O bot postará automaticamente no próximo startup
   - Ou aguarde a verificação automática (a cada 2 horas)

---

## 🔄 Fluxo Automático

1. **Você atualiza o CHANGELOG.md**
2. **Executa o script** → Atualiza ROADMAP_MELHORIAS.md
3. **Faz commit e push**
4. **Bot detecta mudanças** (hash muda)
5. **Bot posta automaticamente** no canal de roadmap

---

## 🛠️ Uso do Script

### Executar Manualmente:

```bash
python scripts/atualizar_roadmap_automatico.py
```

### Integrar no Workflow:

Você pode adicionar o script ao seu processo de commit:

```bash
# .git/hooks/pre-commit (exemplo)
python scripts/atualizar_roadmap_automatico.py
git add docs/02_ARQUITETURA/ROADMAP_MELHORIAS.md
```

---

## 📝 Estrutura Esperada no CHANGELOG.md

```markdown
## [Unreleased]

### 🚀 Título da Atualização (2025-01-11)

#### Added
- Nova feature 1
- Nova feature 2

#### Changed
- Mudança 1
- Mudança 2

#### Fixed
- Correção 1
- Correção 2
```

---

## ✅ Checklist

- [ ] CHANGELOG.md atualizado com seção [Unreleased]
- [ ] Script executado: `python scripts/atualizar_roadmap_automatico.py`
- [ ] ROADMAP_MELHORIAS.md tem seções "New Features" e "Fixes & Improvements"
- [ ] Commit e push realizados
- [ ] Bot reiniciado ou aguardando verificação automática
- [ ] Mensagem verificada no canal de roadmap

---

## 🔍 Verificar se Funcionou

### No Bot (Logs):
```
[ROADMAP] Posting roadmap update. Old hash: ..., New hash: ...
[ROADMAP] ✅ Roadmap update posted on startup
```

### No Discord:
- Canal `#roadmap` deve ter nova mensagem
- Embed com título, features, fixes e upcoming

---

## ⚠️ Troubleshooting

### Bot não posta mesmo após atualizar:

1. **Verificar seções no ROADMAP_MELHORIAS.md:**
   - Deve ter "### New Features" ou "### Fixes & Improvements"
   - Itens devem estar em formato de lista (`- item`)

2. **Verificar CHANGELOG.md:**
   - Deve ter seção `[Unreleased]`
   - Deve ter `#### Added`, `#### Changed` ou `#### Fixed`

3. **Executar script manualmente:**
   ```bash
   python scripts/atualizar_roadmap_automatico.py
   ```

4. **Forçar postagem:**
   - Use comando `/roadmap` manualmente
   - Ou reinicie o bot (force_post=True no startup)

---

**Última atualização:** 2025-01-11

