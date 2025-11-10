# 🔗 Guia Completo: Binds do Bloxlink

## 📋 Índice

1. [O que são Binds?](#o-que-são-binds)
2. [Como Funcionam os Binds](#como-funcionam-os-binds)
3. [Configuração Passo a Passo](#configuração-passo-a-passo)
4. [Integração com Ignis](#integração-com-ignis)
5. [Troubleshooting](#troubleshooting)

---

## 🎯 O que são Binds?

**Binds** são mapeamentos que conectam ranks do Roblox a cargos do Discord. Quando um usuário é verificado ou atualizado via Bloxlink, o bot automaticamente atribui os cargos correspondentes ao rank do usuário no grupo Roblox.

### Conceitos Básicos

- **Rank do Roblox**: Posição hierárquica do usuário em um grupo Roblox (ex: rank 1, rank 10, rank 50)
- **Cargo do Discord**: Role/cargo no servidor Discord que será atribuído
- **Bind**: Regra que diz "se usuário tem rank X no grupo Y, dê cargo Z no Discord"

---

## ⚙️ Como Funcionam os Binds

### Fluxo de Funcionamento

1. **Usuário é verificado/atualizado**
   - Moderador usa `/verify` ou `/update` do Bloxlink
   - Bloxlink consulta o rank do usuário no grupo Roblox

2. **Bloxlink processa os binds**
   - Verifica se há binds configurados para o grupo
   - Compara o rank do usuário com as regras de bind
   - Atribui os cargos correspondentes

3. **Ignis detecta a mudança**
   - Detecta quando os cargos são atualizados
   - Atualiza o rank no banco de dados
   - Atualiza o nickname automaticamente

### Tipos de Binds

#### 1. Bind por Rank Numérico
```
Rank 1 → Cargo "Recruta"
Rank 10 → Cargo "Soldado"
Rank 50 → Cargo "Sargento"
```

#### 2. Bind por Nome do Cargo (Role Name)
```
"Legionary" → Cargo "Legionary"
"Captain" → Cargo "Captain"
```

#### 3. Bind com Múltiplos Cargos
```
Rank 1 → Cargo "Recruta" + Cargo "Membro Verificado"
```

---

## 📝 Configuração Passo a Passo

### Passo 1: Acessar o Painel do Bloxlink

1. Acesse: https://blox.link/dashboard
2. Faça login com sua conta Discord
3. Selecione o servidor onde o Ignis está configurado

### Passo 2: Navegar até Binds

1. No menu lateral, clique em **"Binds"** ou **"Role Binds"**
2. Você verá uma lista de grupos Roblox configurados
3. Se não houver grupos, clique em **"Add Bind"** ou **"New Bind"**

### Passo 3: Configurar Bind para o Grupo Principal

1. Clique em **"Add Bind"** ou **"New Bind"**
2. Selecione o grupo Roblox: **6340169** (ou procure pelo nome do grupo)
3. Configure os mapeamentos de rank → cargo

#### Exemplo de Configuração:

```
Grupo: 6340169 (Age of Warfare - Grupo Principal)

Rank 1 → Cargo: [ID do cargo ou nome]
Rank 2 → Cargo: [ID do cargo ou nome]
Rank 10 → Cargo: [ID do cargo ou nome]
...
```

### Passo 4: Configurar Binds por Nome de Cargo (Recomendado)

Para maior precisão, configure binds usando o **nome do cargo** (role name) em vez do número do rank:

1. No painel de binds, selecione **"Role Name"** como tipo de bind
2. Configure os mapeamentos:

```
"Legionary" → Cargo Discord: "Legionary"
"Captain" → Cargo Discord: "Captain"
"Techmarine" → Cargo Discord: "Techmarine"
```

### Passo 5: Salvar e Testar

1. Clique em **"Save"** ou **"Apply"**
2. Teste usando `/update @usuário` no Discord
3. Verifique se os cargos foram atribuídos corretamente

---

## 🔄 Integração com Ignis

### Como o Ignis Trabalha com Bloxlink

O Ignis **complementa** o Bloxlink, não o substitui:

1. **Bloxlink**: Atribui cargos baseado nos binds configurados
2. **Ignis**: Atualiza nickname e sincroniza rank no banco de dados

### Fluxo Completo

```
1. Moderador usa /update @usuário
   ↓
2. Bloxlink verifica rank no Roblox
   ↓
3. Bloxlink aplica binds → Atribui cargos no Discord
   ↓
4. Ignis detecta mudança de cargos
   ↓
5. Ignis atualiza:
   - Rank no banco de dados
   - Nickname (formato: Prefix. Rank Username)
```

### Configuração Recomendada

#### No Bloxlink:
- Configure binds para **todos os ranks** que você quer mapear
- Use **nomes de cargos** quando possível (mais preciso)
- Configure o grupo principal: **6340169**

#### No Ignis:
- Prefixos de nickname já configurados (IA, IG, 6, A)
- Company numbers configuráveis via `/company set`
- Sincronização automática de ranks

---

## 🎯 Configuração de Company por Rank

O Ignis pode determinar a company baseado no rank do usuário no Roblox. Isso será usado para:

1. **Nickname**: Formato `{Company}. {Rank} {Username}`
2. **Organização**: Agrupar membros por company

### Como Funcionará

Quando o Bloxlink usar `/verify` ou `/update`:

1. Ignis detecta o comando (via webhook ou detecção de mudança)
2. Ignis consulta o rank do usuário no grupo Roblox
3. Ignis determina a company baseado no rank
4. Ignis envia informações para o Bloxlink (se necessário)
5. Bloxlink atribui cargos baseado nos binds
6. Ignis atualiza nickname com company + rank

---

## ⚠️ Troubleshooting

### Problema: Cargos não estão sendo atribuídos

**Soluções:**
1. Verifique se os binds estão configurados no painel do Bloxlink
2. Verifique se o grupo Roblox está correto (6340169)
3. Verifique se o usuário está no grupo Roblox
4. Teste com `/update @usuário` novamente
5. Verifique os logs do Bloxlink (se disponível)

### Problema: Nickname não está sendo atualizado

**Soluções:**
1. Verifique se o usuário está verificado pelo Bloxlink
2. Verifique se o bot Ignis tem permissão `Manage Nicknames`
3. Verifique se o prefixo está configurado para o rank
4. Verifique os logs em `logs/ignisbot.log`

### Problema: Binds não estão funcionando

**Soluções:**
1. Certifique-se de que o Bloxlink está no servidor
2. Verifique se o Bloxlink tem permissão `Manage Roles`
3. Verifique se os cargos estão abaixo do cargo do Bloxlink na hierarquia
4. Tente remover e recriar os binds

---

## 📚 Recursos Adicionais

- **Documentação do Bloxlink**: https://docs.blox.link
- **Painel do Bloxlink**: https://blox.link/dashboard
- **Suporte do Bloxlink**: https://blox.link/support

---

## 🔐 Permissões Necessárias

### Para o Bloxlink:
- ✅ `Manage Roles` - Para atribuir cargos
- ✅ `Manage Nicknames` - Para atualizar nicknames (opcional)

### Para o Ignis:
- ✅ `Manage Nicknames` - Para atualizar nicknames
- ✅ `View Channels` - Para detectar mudanças
- ✅ `Read Message History` - Para logs

---

## 💡 Dicas e Boas Práticas

1. **Use nomes de cargos** em vez de números de rank quando possível
2. **Teste sempre** após configurar novos binds
3. **Mantenha a hierarquia** dos cargos correta no Discord
4. **Documente** seus binds para referência futura
5. **Monitore os logs** para identificar problemas rapidamente

---

## 📞 Suporte

Se precisar de ajuda:
1. Verifique os logs: `logs/ignisbot.log`
2. Consulte a documentação do Bloxlink
3. Verifique o status: `/health` command
4. Entre em contato com o administrador do servidor

