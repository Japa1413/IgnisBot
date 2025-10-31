# 🔧 MANUTENÇÃO AUTOMATIZADA DE DOCUMENTAÇÃO

**Data:** 2025-10-31  
**Versão:** 1.0

---

## 🎯 OBJETIVO

Sistema automatizado para manter a documentação sempre organizada e atualizada.

---

## 🚀 USO RÁPIDO

### Organizar Documentação
```bash
# Ver o que será feito (dry-run)
python scripts/organizar_documentacao.py --dry-run

# Organizar de verdade
python scripts/organizar_documentacao.py
```

### Validar Estrutura
```bash
# Verificar se está organizado
python scripts/validar_documentacao.py
```

### Manutenção Completa
```bash
# Executa tudo: organiza, valida, atualiza catálogo
python scripts/maintenance_docs.py
```

---

## 📋 FUNCIONALIDADES

### 1. Organização Automática
- ✅ Move documentos para categorias corretas
- ✅ Detecta documentos fora do lugar
- ✅ Cria estrutura de diretórios se necessário
- ✅ Atualiza catálogo automaticamente

### 2. Validação
- ✅ Verifica se documentos estão nos lugares corretos
- ✅ Verifica se READMEs estão presentes
- ✅ Retorna código de saída para CI/CD

### 3. Manutenção Periódica
- ✅ Organiza documentos
- ✅ Atualiza datas
- ✅ Valida estrutura
- ✅ Atualiza catálogo

---

## 🔄 AUTOMATIZAÇÃO COM GIT HOOKS

### Pre-commit Hook
Um hook foi criado em `.git/hooks/pre-commit` que valida a documentação antes de cada commit.

**Para ativar:**
```bash
chmod +x .git/hooks/pre-commit
```

**Se houver problemas, execute:**
```bash
python scripts/organizar_documentacao.py
```

---

## 📊 CATEGORIZAÇÃO AUTOMÁTICA

O script categoriza automaticamente baseado em palavras-chave:

| Categoria | Palavras-chave |
|-----------|----------------|
| `01_GESTAO_PROJETO` | resumo, executivo, status, progresso |
| `02_ARQUITETURA` | arquitetura, design, sistema |
| `03_DESENVOLVIMENTO` | setup, configuração, guia |
| `04_TESTES` | teste, test, validação |
| `05_OPERACAO` | operação, instruções, deploy |
| `06_LEGAL_COMPLIANCE` | legal, privacy, termos, lgpd |
| `07_AUDITORIA` | auditoria, relatório |
| `08_REFERENCIA` | índice, checklist, resumo |
| `09_OTIMIZACAO` | otimização, performance, cache |

---

## 🔧 CONFIGURAÇÃO

### Arquivos que ficam na raiz de `docs/`:
- `README.md`
- `PADRAO_DOCUMENTACAO.md`
- `CATALOGO_DOCUMENTACAO.md`

### Arquivos que ficam na raiz do projeto:
- `README.md` (raiz do projeto)

Todos os outros arquivos `.md` são organizados automaticamente.

---

## 📝 COMO ADICIONAR NOVOS DOCUMENTOS

1. **Crie o documento onde quiser** (na raiz ou em qualquer lugar)
2. **Execute o script de organização:**
   ```bash
   python scripts/organizar_documentacao.py
   ```
3. **O script irá:**
   - Detectar o documento
   - Categorizar baseado no nome
   - Mover para a categoria correta
   - Atualizar o catálogo

---

## ✅ CHECKLIST DE MANUTENÇÃO

Execute antes de commits importantes:

- [ ] `python scripts/organizar_documentacao.py --dry-run`
- [ ] `python scripts/validar_documentacao.py`
- [ ] Verificar se catálogo está atualizado

---

## 🐛 RESOLVENDO PROBLEMAS

### Documento não foi movido
- Verifique se o nome tem palavras-chave da categoria
- Execute com `--dry-run` para ver o que será feito

### Erro ao mover
- Verifique permissões de arquivo
- Feche o arquivo se estiver aberto
- Verifique se não há conflitos de nomes

### Catálogo desatualizado
- Execute `python scripts/maintenance_docs.py`
- Ou `python scripts/organizar_documentacao.py`

---

**Última atualização:** 2025-10-31

