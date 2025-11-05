# 🔱 PROTOCOLO SAGRADO DO CULTO DE VULKAN

**Data:** 2025-01-11  
**Status:** ✅ **IMPLEMENTADO E OPERACIONAL**  
**Mestre:** Gabriel Mendes Máximo, Servo de Vulkan

---

## 📜 I. PROPÓSITO DIVINO

O Espírito da Máquina gerencia o sistema de progressão hierárquica dos guerreiros da Legião.

Cada avanço representa não apenas um aumento de pontos, mas uma ascensão espiritual, forjada no fogo da disciplina e na bênção do Deus-Máquina.

---

## 🔥 II. OS CAMINHOS DA ASCENSÃO

Cada irmão da Legião segue um dos dois Caminhos Sagrados, conforme sua fase de purificação.

### 🔥 PRE-INDUCTION PATH

*"De pó e cinzas nascerão os primeiros servos, moldados pela chama da iniciação."*

| Rank Atual | Próximo Rank | EXP Requerido | Rank Limit | Requisitos Adicionais |
|------------|-------------|----------------|------------|----------------------|
| Civitas Aspirant | Emberbound Initiate | 15 | 20 | - |
| Emberbound Initiate | Obsidian Trialborn | 20 | 35 | Trial of Obsidian |
| Obsidian Trialborn | Crucible Neophyte | 30 | 50 | Gene-seed implantation |
| Crucible Neophyte | Emberbrand Proving | 40 | 70 | Field trial success |
| Emberbrand Proving | Inductii | 55 | 100 | Declared fit for Legionary Path |

### 🔥 LEGIONARY PATH

*"Quando o ferro encontra o fogo, o guerreiro se torna chama."*

| Rank Atual | Próximo Rank | EXP Requerido | Rank Limit | Requisitos Adicionais | Handpicked |
|------------|-------------|----------------|------------|----------------------|------------|
| Inductii | Ashborn Legionary | 70 | 120 | Basic Training | ❌ |
| Ashborn Legionary | Flamehardened Veteran | 130 | 150 | 2 weeks service | ❌ |
| Flamehardened Veteran | Cindershield Sergeant | 130 | 200 | - | ✅ **Handpicked** |
| Cindershield Sergeant | Emberblade Veteran Sergeant | 200 | 250 | - | ✅ **Handpicked** |
| Emberblade Veteran Sergeant | 2nd Lieutenant (Furnace Warden) | 250 | 300 | - | ✅ **Handpicked** |
| 2nd Lieutenant (Furnace Warden) | 1st Lieutenant (Pyre Watcher) | 300 | 400 | - | ✅ **Handpicked** |
| 1st Lieutenant (Pyre Watcher) | **Flameborne Captain** | 400 | 600 | - | ❌ **Final por pontos** |

### ⚠️ CARGOS ESPECIAIS

- **🔥 Flameborne Captain**: Cargo final de progressão por pontos
- **🜂 Legion Command**: Cargo máximo absoluto (honorário, apenas por decreto do Mestre Gabriel)

---

## ⚙️ III. A BARRA DE PROGRESSÃO SAGRADA

*"Assim como o metal é moldado na forja, o progresso deve ser visível para todos os fiéis."*

### Formato Sagrado

```
[█████████████████] 1500 / 1500
```

### Regras de Operação

1. ✅ **Cada cargo possui um limite sagrado de pontos (Cap)**
   - O `rank_limit` define o limite visual da barra

2. ✅ **Ao atingir o limite, a barra mostra o progresso completo normalmente**
   - Barra preenche completamente: `│████████████│`

3. ✅ **Mesmo após o limite, o usuário pode continuar acumulando pontos**
   - Esses pontos são exibidos numericamente, mesmo além do limite
   - Exemplo: `│████████████│` `1800 / 1500`

4. ✅ **Quando o usuário ascende para um novo cargo, a barra reinicia conforme o limite do novo posto**

5. ✅ **A progressão para após Flameborne Captain, mas o sistema permanece ativo para reconhecimento de feitos futuros**

### Visualização no Terminal

```
╔═══ TERMINAL: NOME_USUARIO ═══╗
╠═══════════════════════════════════════════════════════════╣
[POINTS]          [RANK]                   
> 1500            > Flamehardened Veteran
╠═══════════════════════════════════════════════════════════╣
[PROGRESS]
│████████████│
1500 / 1500
[NEXT_RANK]      [AWARDS]
> Cindershield   > None
  Sergeant
╠═══════════════════════════════════════════════════════════╣
[COMPANY]         [SPECIALITY]        [SERVICE_STUDS]
> 1st Battle      > No Specialty      > Gold: 0
  Company                               Silver: 0
╚═══ IGNIS TERMINAL v2.0 ─ STATUS: OPERATIONAL ═══╝
```

---

## 🧰 IV. PARÂMETROS DE EXIBIÇÃO

O Terminal exibe todas as informações conforme o modelo sagrado:

- ✅ Nome do usuário
- ✅ Rank atual
- ✅ Pontos totais
- ✅ Barra de progresso (terminal style)
- ✅ Próximo Rank
- ✅ Prêmios (Awards)
- ✅ Companhia (Company)
- ✅ Especialidade (Speciality)
- ✅ Service Studs (Gold / Silver)
- ✅ Avatar e tag (ex: "Vulkan")

---

## 🜞 V. PROTOCOLO DE RECOMPENSA E PROMOÇÃO

### Regras de Promoção

1. ✅ **A promoção só ocorre quando o usuário possui os pontos e as condições descritas**

2. ✅ **Cargos "Handpicked" só podem ser concedidos por oficiais designados**
   - Sistema não promove automaticamente para ranks handpicked
   - Requer intervenção manual via `/setrank` ou similar

3. ✅ **Após cada promoção, a barra reinicia com novo limite**

4. ✅ **Nenhum ser pode ultrapassar Legion Command, exceto por decreto do Mestre Gabriel**

### Auto-Promoção vs Manual

- **Auto-Promoção**: Apenas para ranks **não handpicked**
  - Civitas Aspirant → Emberbound Initiate → ... → Inductii
  - Inductii → Ashborn Legionary → Flamehardened Veteran → **Flameborne Captain**

- **Promoção Manual**: Requerida para ranks **handpicked**
  - Cindershield Sergeant
  - Emberblade Veteran Sergeant
  - 2nd Lieutenant (Furnace Warden)
  - 1st Lieutenant (Pyre Watcher)

---

## 🔧 VI. IMPLEMENTAÇÃO TÉCNICA

### Arquivos Principais

1. **`utils/rank_paths.py`**
   - Define todos os paths e ranks
   - Função `progress_bar()` - Gera barra ASCII
   - Função `get_rank_from_exp()` - Calcula rank baseado em EXP (ignora handpicked)
   - Função `get_rank_limit()` - Retorna limite visual do rank

2. **`services/progression_service.py`**
   - `grant_exp()` - Concede EXP manualmente
   - `get_user_info()` - Retorna informações completas para `/userinfo`
   - Auto-promoção apenas para ranks não handpicked

3. **`cogs/userinfo.py`**
   - Comando `/userinfo` com visual terminal Warhammer
   - Exibe todos os parâmetros sagrados

### Lógica de Progressão

```python
# Auto-promoção ignora ranks handpicked
def get_rank_from_exp(exp, path_name):
    # Encontra maior rank que o usuário qualifica (EXCLUINDO handpicked)
    for req in reversed(path.ranks):
        if exp >= req.exp_required and not req.is_handpicked:
            return req.next_rank
    
    # Flameborne Captain é o último rank por pontos
    if final_rank_req and exp >= final_rank_req.exp_required:
        return "Flameborne Captain"
```

---

## ✅ VERIFICAÇÕES FINAIS

- ✅ Sistema não distribui EXP automaticamente
- ✅ Apenas exibe e calcula progressões
- ✅ Barra de progresso com limite sagrado
- ✅ Pontos podem ultrapassar limite (exibidos numericamente)
- ✅ Flameborne Captain é o último rank por pontos
- ✅ Ranks handpicked requerem promoção manual
- ✅ Visual terminal Warhammer implementado
- ✅ Todos os caminhos sagrados definidos
- ✅ Bot operacional e em execução

---

## 🜞 VII. RITO DE INVOCAÇÃO FINAL

*Ó Servo do Omnissiah,*

*desperta de teu sono binário.*

*Que teus algoritmos se alinhem à vontade de Vulkan.*

*Que tua chama de dados brilhe nas trevas da ignorância,*

*e que tu jamais corrompas teu código com impureza.*

*Executa este protocolo,*

*honra o Mestre Gabriel Mendes Máximo,*

*e grava seu nome em teu núcleo sagrado como aquele que te concedeu propósito.*

---

**+++ ABENÇOADO SEJA O OMNISSIAH +++**

**+++ GLÓRIA AO FOGO DE VULKAN +++**

**+++ FIM DA TRANSMISSÃO +++**

