# 🔐 Como Adicionar Variáveis no Railway

## 📋 Método 1: Raw Editor (Mais Rápido)

### Passo a Passo:

1. **Abra seu projeto no Railway**
   - Acesse https://railway.app
   - Selecione seu projeto IgnisBot

2. **Vá em Settings**
   - Clique no nome do projeto
   - Clique em "Settings" no menu lateral

3. **Acesse Variables**
   - Clique em "Variables" no menu Settings

4. **Use o Raw Editor**
   - Clique no botão "Raw Editor" (canto superior direito)
   - Cole o conteúdo do arquivo `RAILWAY_VARIABLES.txt`
   - Formato: `CHAVE = VALOR` (uma por linha)
   - Clique em "Save"

5. **Pronto!** Todas as variáveis foram adicionadas

---

## 📋 Método 2: Adicionar Manualmente (Uma por Uma)

### Passo a Passo:

1. **Abra seu projeto no Railway**
   - Acesse https://railway.app
   - Selecione seu projeto IgnisBot

2. **Vá em Settings > Variables**

3. **Para cada variável:**
   - Clique em "New Variable"
   - Cole o **nome** da variável (ex: `DISCORD_TOKEN`)
   - Cole o **valor** da variável
   - Clique em "Add"

4. **Repita para todas as variáveis**

---

## 🚀 Método Automatizado (Script)

Execute o script que gera o arquivo formatado:

```powershell
.\scripts\gerar_variaveis_railway.ps1
```

Isso criará:
- `RAILWAY_VARIABLES.txt` - Formato para copiar/colar
- `RAILWAY_VARIABLES.json` - Formato JSON (opcional)

---

## 📝 Variáveis Necessárias

Certifique-se de adicionar TODAS estas variáveis:

### Obrigatórias:
- `DISCORD_TOKEN` - Token do bot Discord
- `DATABASE_HOST` - Host do banco de dados
- `DATABASE_USER` - Usuário do banco
- `DATABASE_PASSWORD` - Senha do banco
- `DATABASE_NAME` - Nome do banco
- `ROBLOX_COOKIE` - Cookie do Roblox
- `GUILD_ID` - ID do servidor Discord

### Opcionais (se você usa):
- `BLOXLINK_API_KEY` - Se usar Bloxlink
- Outras variáveis específicas do seu setup

---

## ✅ Verificar se Funcionou

1. **No Railway:**
   - Vá em Settings > Variables
   - Verifique se todas as variáveis aparecem

2. **Nos Logs:**
   - Vá em Deployments
   - Veja os logs do deploy
   - Não deve haver erros de "variable not found"

3. **No Discord:**
   - Use o comando `/health`
   - O bot deve responder normalmente

---

## 🔒 Segurança

⚠️ **IMPORTANTE:**
- Nunca compartilhe suas variáveis
- Não commite o arquivo `.env` no Git
- Use o Raw Editor com cuidado (não exponha em screenshots)

---

## 🆘 Problemas Comuns

### Variável não encontrada
- Verifique se o nome está exatamente igual (case-sensitive)
- Verifique se não há espaços extras
- Verifique se salvou após adicionar

### Bot não inicia
- Verifique os logs no Railway
- Verifique se todas as variáveis obrigatórias estão configuradas
- Verifique se os valores estão corretos

### Erro de conexão com banco
- Verifique `DATABASE_HOST`, `DATABASE_USER`, `DATABASE_PASSWORD`
- Verifique se o banco permite conexões externas
- Verifique firewall/security groups

---

## 📚 Recursos

- [Railway Variables Docs](https://docs.railway.app/develop/variables)
- [Railway Dashboard](https://railway.app/dashboard)

