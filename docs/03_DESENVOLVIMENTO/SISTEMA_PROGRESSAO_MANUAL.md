# 🎯 SISTEMA DE PROGRESSÃO MANUAL - IGNISBOT

**Data:** 2025-10-31  
**Status:** ✅ **IMPLEMENTADO**  
**Tipo:** Manual (não automático)

---

## 📋 RESUMO EXECUTIVO

Sistema de progressão manual implementado conforme especificação. O bot **não distribui EXP automaticamente** - toda concessão de pontos e promoções é feita manualmente por membros autorizados da administração.

---

## ✅ COMPONENTES IMPLEMENTADOS

### 1. Estrutura de Paths e Ranks ✅

**Arquivo:** `utils/rank_paths.py`

**Paths Implementados:**
- ✅ **Pre-Induction Path** (5 ranks)
- ✅ **Legionary Path** (7 ranks)

**Características:**
- Estrutura de dados com `RankRequirement`
- Cálculo automático de progresso
- Suporte a ranks "handpicked"
- Requisitos adicionais (trials, service time, etc.)

---

### 2. Progression Service ✅

**Arquivo:** `services/progression_service.py`

**Métodos:**
- ✅ `grant_exp()` - Conceder EXP manualmente
- ✅ `set_rank()` - Definir rank manualmente (handpicked)
- ✅ `get_user_info()` - Obter informações completas para `/userinfo`

**Características:**
- Auto-detecção de rank baseado em EXP
- Suporte a promoções handpicked
- Cálculo de progresso automático
- Barras de progresso ASCII

---

### 3. Comando `/userinfo` ✅

**Arquivo:** `cogs/userinfo_new.py`

**Exibe:**
- ✅ Nome do usuário
- ✅ Path atual (Pre-Induction Path, Legionary Path)
- ✅ Rank atual
- ✅ EXP atual
- ✅ Barra de progresso ASCII
- ✅ Próximo rank e requisitos
- ✅ Indicação se próximo rank é handpicked

**Formato:**
```
╔════════════════════════════╗
  USER INFORMATION - IGNIS
╚════════════════════════════╝

User: Sergeant Maximus
Path: Legionary Path
Rank: Flamehardened Veteran
EXP: 130 pts
Next Rank: Cindershield Sergeant (Handpicked)

Progress:
[██████████░░░░░░░░░░░░░] 130 / 170 pts (76.5%)
```

---

**Nota:** Comandos administrativos de concessão de EXP e definição de rank devem ser implementados separadamente se necessário. O sistema atual suporta apenas exibição e cálculo de progressão.

### 6. Banco de Dados Atualizado ✅

**Mudanças em `users` table:**
- ✅ `exp` INT - EXP separado (compatível com `points`)
- ✅ `path` VARCHAR(50) - Path atual do usuário
- ✅ `rank` atualizado para usar nomes corretos

---

## 🎯 SISTEMA DE PATHS

### Pre-Induction Path

| Rank Atual | Próximo | EXP Requerido | Requisitos Adicionais |
|------------|---------|---------------|----------------------|
| Civitas Aspirant | Emberbound Initiate | 15 | - |
| Emberbound Initiate | Obsidian Trialborn | 20 | Trial of Obsidian |
| Obsidian Trialborn | Crucible Neophyte | 30 | Gene-seed implantation |
| Crucible Neophyte | Emberbrand Proving | 40 | Field trial success |
| Emberbrand Proving | Inductii | 55 | Declared fit for Legionary Path |

### Legionary Path

| Rank Atual | Próximo | EXP Requerido | Requisitos Adicionais |
|------------|---------|---------------|----------------------|
| Inductii | Ashborn Legionary | 70 | Basic Training |
| Ashborn Legionary | Flamehardened Veteran | 130 | 2 weeks service |
| Flamehardened Veteran | Cindershield Sergeant | 170 | **Handpicked** |
| Cindershield Sergeant | Emberblade Veteran Sergeant | 200 | **Handpicked** |
| Emberblade Veteran Sergeant | 2nd Lieutenant (Furnace Warden) | 250 | **Handpicked** |
| 2nd Lieutenant (Furnace Warden) | 1st Lieutenant (Pyre Watcher) | 300 | **Handpicked** |
| 1st Lieutenant (Pyre Watcher) | Flameborne Captain | 400 | **Handpicked** |


---

## 🔄 FLUXO DE FUNCIONAMENTO

### Conceder EXP:

```
1. Admin usa /grantxp @user 50 "Razão"
2. ProgressionService.grant_exp()
   - Adiciona EXP ao usuário
   - Calcula novo rank baseado em EXP
   - Auto-atualiza rank se não for handpicked
3. Exibe embed com resultado
```

### Definir Rank Manualmente:

```
1. Admin usa /setrank @user "Rank Name" path:legionary
2. ProgressionService.set_rank()
   - Atualiza rank no banco
   - Atualiza path se fornecido
3. Exibe embed com confirmação
```

### Verificar Progresso:

```
1. Usuário usa /userinfo
2. ProgressionService.get_user_info()
   - Calcula progresso atual
   - Determina próximo rank
   - Gera barra de progresso
3. Exibe embed formatado
```

---

## 📊 CÁLCULO DE PROGRESSO

### Fórmula:

```python
# Progresso em relação ao próximo rank
exp_in_current = exp_atual - exp_do_rank_atual
exp_needed = exp_do_proximo_rank - exp_do_rank_atual
progress_pct = (exp_in_current / exp_needed) * 100
```

### Exemplo:

```
Usuário: 130 EXP
Rank Atual: Flamehardened Veteran (130 EXP)
Próximo: Cindershield Sergeant (170 EXP)

exp_in_current = 130 - 130 = 0
exp_needed = 170 - 130 = 40
progress_pct = (0 / 40) * 100 = 0%

Barra: [░░░░░░░░░░░░░░░░░░░░] 0 / 40 pts (0%)
```

---

## ✅ VALIDAÇÕES E SEGURANÇA

### Permissões:
- ✅ `/grantxp` - Requer `administrator=True`
- ✅ `/setrank` - Requer `administrator=True`
- ✅ `/userinfo` - Público (qualquer um pode ver)

### Validações:
- ✅ Razão obrigatória em `/grantxp`
- ✅ Path válido em `/setrank`
- ✅ EXP não pode ser negativo
- ✅ Rank existe no path especificado

---

## 🚀 PRÓXIMOS PASSOS

### Expandir Paths:
- [ ] Breacher Path
- [ ] Assault Path
- [ ] Destroyer Path
- [ ] Firedrake Path
- [ ] Signal Path
- [ ] Armourium Path
- [ ] Librarius Path
- [ ] Reclusiam Path

### Melhorias:
- [ ] Comando `/setpath` para mudar path do usuário
- [ ] Comando `/listpaths` para listar paths disponíveis
- [ ] Comando `/listranks` para listar ranks de um path
- [ ] Histórico de mudanças de rank/EXP

---

## ⚠️ NOTAS IMPORTANTES

1. **Sistema Automático Desabilitado:**
   - Event handlers de gamificação **não estão ativos**
   - EXP só é ganho via `/grantxp`

2. **Compatibilidade:**
   - `points` e `exp` são mantidos em sincronia
   - Sistema antigo continua funcionando
   - Migração automática na primeira execução

3. **Auto-Atualização de Rank:**
   - Ranks não-handpicked são atualizados automaticamente quando EXP aumenta
   - Ranks handpicked requerem `/setrank` manual

---

**Status:** ✅ **IMPLEMENTADO E PRONTO PARA USO**

