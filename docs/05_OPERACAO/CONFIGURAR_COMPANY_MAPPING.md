# 🏢 Configurar Mapeamento de Company por Rank

## 📋 Visão Geral

O Ignis pode determinar automaticamente a company de um usuário baseado no seu rank no grupo Roblox. Isso é usado para:

1. **Nickname**: Formato `{Company}. {Rank} {Username}`
2. **Organização**: Agrupar membros por company

## ⚙️ Como Funciona

Quando o Bloxlink usa `/verify` ou `/update`:

1. **Ignis detecta a atualização**
   - Detecta quando os cargos do Discord são atualizados
   - Obtém o rank do usuário no grupo Roblox (6340169)

2. **Ignis determina a company**
   - Consulta o mapeamento rank → company
   - Usa o mapeamento configurado

3. **Ignis atualiza o nickname**
   - Formato: `{Company}. {Rank} {Username}`
   - Exemplo: `6. Legionary NarutoNotNaruto1`

## 📝 Configuração

### Método 1: Mapeamento por Nome do Rank (Recomendado)

Mais preciso, usa o nome exato do cargo no Roblox:

```python
# Exemplo de configuração
RANK_NAME_TO_COMPANY_MAP = {
    "Legionary": 6,
    "Captain": 1,
    "Sergeant": 2,
    "Techmarine": 3,
    # ... adicione mais mapeamentos
}
```

### Método 2: Mapeamento por Número do Rank

Usa o número do rank (1, 2, 3, etc.):

```python
# Exemplo de configuração
RANK_TO_COMPANY_MAP = {
    1: 1,   # Rank 1 → Company 1
    2: 1,   # Rank 2 → Company 1
    10: 2,  # Rank 10 → Company 2
    20: 3,  # Rank 20 → Company 3
    # ... adicione mais mapeamentos
}
```

## 🔧 Como Configurar

### Opção 1: Via Código (Temporário)

Edite `services/company_mapping_service.py` e adicione os mapeamentos:

```python
RANK_NAME_TO_COMPANY_MAP = {
    "Legionary": 6,
    "Captain": 1,
    # ... seus mapeamentos
}
```

### Opção 2: Via Comando (Futuro)

Um comando `/company map` será implementado para configurar via Discord.

## 📊 Exemplo de Mapeamento Completo

```python
# Mapeamento por nome do rank (mais preciso)
RANK_NAME_TO_COMPANY_MAP = {
    # Company 1
    "Captain": 1,
    "Lieutenant": 1,
    "Sergeant": 1,
    
    # Company 2
    "Veteran": 2,
    "Elite": 2,
    
    # Company 3
    "Specialist": 3,
    "Techmarine": 3,
    
    # Company 6 (Legionary)
    "Legionary": 6,
    "Neophyte": 6,
    
    # ... adicione todos os ranks
}
```

## 🔄 Fluxo Completo

```
1. Moderador usa /update @usuário (Bloxlink)
   ↓
2. Bloxlink consulta rank no Roblox
   ↓
3. Bloxlink atribui cargos no Discord (baseado nos binds)
   ↓
4. Ignis detecta mudança de cargos
   ↓
5. Ignis obtém rank do Roblox
   ↓
6. Ignis determina company baseado no mapeamento
   ↓
7. Ignis atualiza nickname: {Company}. {Rank} {Username}
```

## ⚠️ Troubleshooting

### Company não está sendo determinada

1. Verifique se o mapeamento está configurado
2. Verifique se o rank do usuário está no mapeamento
3. Verifique os logs: `logs/ignisbot.log`
4. Use `/userinfo @usuário` para ver o rank atual

### Nickname não está sendo atualizado

1. Verifique se o bot tem permissão `Manage Nicknames`
2. Verifique se o prefixo está configurado para o rank
3. Verifique se a company foi determinada
4. Verifique os logs: `logs/ignisbot.log`

## 📚 Próximos Passos

1. **Configurar mapeamentos**: Adicione os mapeamentos rank → company
2. **Testar**: Use `/update @usuário` e verifique o nickname
3. **Ajustar**: Ajuste os mapeamentos conforme necessário

---

**Nota**: O mapeamento é configurado no código por enquanto. Um sistema de configuração via arquivo JSON será implementado no futuro.


