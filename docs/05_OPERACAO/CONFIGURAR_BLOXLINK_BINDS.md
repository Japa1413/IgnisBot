# 🔗 Como Configurar Binds do Bloxlink

## 📋 Visão Geral

O IgnisBot agora gerencia automaticamente a atribuição de cargos quando um membro completa o Induction Process e recebe rank 1 no grupo principal (ID: 6340169).

## ✅ Funcionalidades Automáticas

### Atualização Automática de Nickname

O Ignis também atualiza automaticamente o nickname no formato:
```
{Prefix}. {Roblox Rank} {Roblox Username}
```

**Exemplos:**
- `IA. Civitas Aspirant NarutoNotNaruto1`
- `IG. Inductii NarutoNotNaruto1`
- `6. Legionary NarutoNotNaruto1`
- `A. Techmarine NarutoNotNaruto1`

## ⚙️ Configuração do Bloxlink

### Passo 1: Acessar o Painel do Bloxlink

1. Acesse o [painel do Bloxlink](https://blox.link/dashboard)
2. Faça login com sua conta Discord
3. Selecione o servidor onde o Ignis está configurado

### Passo 2: Configurar Binds de Cargos

1. Vá para a seção **"Binds"** ou **"Role Binds"**
2. Configure os binds para o grupo Roblox **6340169**
3. Configure os cargos do Discord para cada rank do Roblox

**Importante:**
- O Bloxlink é responsável por atribuir os cargos baseado no rank do Roblox
- O Ignis apenas atualiza o nickname automaticamente
- Configure todos os binds necessários no painel do Bloxlink

### Passo 3: Configurar Comando /update

1. Certifique-se de que o comando `/update` do Bloxlink está habilitado
2. O Ignis detecta automaticamente quando o `/update` é usado
3. Após o `/update`, o Ignis:
   - Atualiza o rank no banco de dados
   - Atribui os cargos de indução (se rank = 1)
   - Atualiza o nickname no formato correto

## 🔄 Fluxo Completo

1. **Membro completa Induction Process**
   - Recebe rank 1 no grupo 6340169 (via botão "Induction Process")

2. **Moderador usa `/update` do Bloxlink**
   - Bloxlink atualiza os cargos do Discord baseado no rank do Roblox

3. **Ignis detecta a mudança**
   - `role_sync_handler` detecta a atualização de cargos
   - Atualiza o rank no banco de dados
   - Atualiza o nickname no formato correto com o prefixo e company respectivos

## 📝 Prefixos de Nickname

O Ignis usa os seguintes prefixos baseados no rank:

| Prefixo | Ranks |
|---------|-------|
| `IA` | Civitas Aspirant, Emberbound Initiate, Obsidian Trialborn, Crucible Neophyte, Emberbrand Proving |
| `IG` | Inductii |
| `6` | Legionary, Ashborn Legionary, Support Squad, Legion Veteran, Flamehardened Veteran, Legion Elite |
| `A` | Techmarine, Chaplain, Apothecarion, Vexillarius, Destroyer, Signal Marine, Terminator Squad |

**Para ranks de Company e acima:**
- Usa o número da company configurado via `/company set`

## ⚠️ Notas Importantes

1. **Permissões do Bot:**
   - O Ignis precisa ter permissão `Manage Roles` para atribuir cargos
   - O Ignis precisa ter permissão `Manage Nicknames` para atualizar nicknames

2. **Ordem dos Cargos:**
   - Certifique-se de que os cargos de indução estão abaixo do cargo do Ignis na hierarquia do Discord

3. **Logs:**
   - Todas as operações são logadas em `logs/ignisbot.log`
   - Verifique os logs se houver problemas

## 🐛 Troubleshooting

### Nickname não está sendo atualizado

1. Verifique se o membro está verificado pelo Bloxlink
2. Verifique se o bot tem permissão `Manage Nicknames`
3. Verifique se o prefixo está configurado para o rank
4. Verifique os logs em `logs/ignisbot.log`

## 📞 Suporte

Se precisar de ajuda adicional, verifique:
- Logs do bot: `logs/ignisbot.log`
- Documentação do Bloxlink: https://docs.blox.link
- Status do servidor: `/health` command

