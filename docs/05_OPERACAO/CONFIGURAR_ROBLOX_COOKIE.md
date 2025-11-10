# Como Configurar o ROBLOX_COOKIE

## O que é o ROBLOX_COOKIE?

O `ROBLOX_COOKIE` é necessário para que o Ignis possa realizar operações nos grupos do Roblox, como:
- Aceitar membros em grupos
- Alterar ranks de membros
- Verificar informações de grupos

## Como Obter o Cookie do Roblox

### Método 1: Via Navegador (Recomendado)

1. **Abra o Roblox no navegador** (Chrome, Firefox, Edge, etc.)
2. **Faça login** na sua conta do Roblox
3. **Abra as Ferramentas de Desenvolvedor**:
   - **Chrome/Edge**: Pressione `F12` ou `Ctrl+Shift+I`
   - **Firefox**: Pressione `F12` ou `Ctrl+Shift+I`
4. **Vá para a aba "Application"** (Chrome) ou "Armazenamento" (Firefox)
5. **No menu lateral, expanda "Cookies"**
6. **Clique em `https://www.roblox.com`**
7. **Procure pelo cookie chamado `.ROBLOSECURITY`**
8. **Copie o valor** (será uma string longa)

### Método 2: Via Console do Navegador

1. **Abra o Roblox no navegador** e faça login
2. **Abra o Console** (`F12` → aba "Console")
3. **Digite o seguinte comando**:
   ```javascript
   document.cookie.split('; ').find(row => row.startsWith('.ROBLOSECURITY=')).split('=')[1]
   ```
4. **Pressione Enter** e copie o valor retornado

## Como Configurar no Ignis

### Passo 1: Abra o arquivo `.env`

O arquivo `.env` está na raiz do projeto IgnisBot.

### Passo 2: Adicione ou edite a linha

```env
ROBLOX_COOKIE=seu_cookie_aqui
```

**Exemplo:**
```env
ROBLOX_COOKIE=_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1V2W3X4Y5Z6
```

### Passo 3: Salve o arquivo

### Passo 4: Reinicie o bot

Após adicionar o cookie, reinicie o bot para que a configuração seja carregada.

## ⚠️ IMPORTANTE - Segurança

1. **NUNCA compartilhe seu cookie** com ninguém
2. **NUNCA faça commit** do arquivo `.env` no Git
3. **O cookie dá acesso total** à sua conta do Roblox
4. **Se o cookie vazar**, alguém pode:
   - Fazer login na sua conta
   - Roubar seus Robux
   - Roubar seus itens
   - Alterar configurações da conta

## Verificação

Após configurar, você pode verificar se está funcionando:

1. Use o comando `/process` no Discord
2. Clique no botão "Induction Process"
3. Se o cookie estiver correto, o processo funcionará
4. Se ainda aparecer erro, verifique:
   - Se o cookie está correto (sem espaços extras)
   - Se o cookie não expirou (faça login novamente no Roblox)
   - Se o bot foi reiniciado após adicionar o cookie

## Problemas Comuns

### Cookie Expirado
- **Sintoma**: Erro de autenticação
- **Solução**: Faça login novamente no Roblox e obtenha um novo cookie

### Cookie Inválido
- **Sintoma**: Erro "Authentication failed"
- **Solução**: Verifique se copiou o cookie completo (é uma string muito longa)

### Cookie Não Funciona
- **Sintoma**: Erro "Invalid or expired cookie"
- **Solução**: 
  1. Verifique se está usando a conta correta (deve ter permissões no grupo)
  2. Verifique se a conta tem permissões para aceitar membros e alterar ranks
  3. Obtenha um novo cookie

## Permissões Necessárias

A conta do Roblox usada deve ter:
- **Permissão para aceitar membros** no grupo 6340169
- **Permissão para alterar ranks** no grupo 6496437
- **Rank suficiente** para realizar essas operações

