# 🚀 Como Adicionar Variáveis no Railway - Passo a Passo

## ✅ Arquivo Gerado Automaticamente!

O arquivo `RAILWAY_VARIABLES.txt` foi criado com **todas as 24 variáveis** do seu `.env`!

---

## 📋 Método Rápido (Raw Editor) - RECOMENDADO

### Passo 1: Abrir o Arquivo
1. Abra o arquivo `RAILWAY_VARIABLES.txt` na pasta do projeto
2. Selecione **TODO o conteúdo** (Ctrl+A)
3. Copie (Ctrl+C)

### Passo 2: No Railway
1. Acesse https://railway.app
2. Faça login e selecione seu projeto **IgnisBot**
3. Clique em **"Settings"** (no menu lateral esquerdo)
4. Clique em **"Variables"** (abaixo de Settings)
5. Clique no botão **"Raw Editor"** (canto superior direito)
6. Cole o conteúdo copiado (Ctrl+V)
7. Clique em **"Save"**

### ✅ Pronto!
Todas as 24 variáveis foram adicionadas de uma vez!

---

## ⚠️ IMPORTANTE: Ajustar DB_HOST

O arquivo gerado tem `DB_HOST=localhost`, mas você precisa alterar para o host do seu banco de dados na nuvem.

### Como fazer:
1. No Railway, após adicionar as variáveis
2. Encontre a variável `DB_HOST`
3. Clique nela para editar
4. Altere de `localhost` para o host real do seu banco:
   - Se usar Railway Database: será algo como `containers-us-west-xxx.railway.app`
   - Se usar outro serviço: use o host fornecido pelo serviço
5. Salve

---

## 📋 Método Alternativo: Adicionar Manualmente

Se preferir adicionar uma por uma:

1. No Railway: Settings > Variables
2. Clique em **"New Variable"**
3. Para cada linha do arquivo `RAILWAY_VARIABLES.txt`:
   - **Name**: parte antes do `=` (ex: `DISCORD_TOKEN`)
   - **Value**: parte depois do `=` (ex: `MTM3NTg5...`)
   - Clique em **"Add"**
4. Repita para todas as 24 variáveis

---

## ✅ Verificar se Funcionou

1. **No Railway:**
   - Vá em Settings > Variables
   - Você deve ver todas as 24 variáveis listadas

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
- O arquivo `RAILWAY_VARIABLES.txt` contém informações sensíveis
- **NÃO** commite este arquivo no Git
- **NÃO** compartilhe este arquivo
- Após usar, você pode deletar o arquivo se quiser

---

## 📝 Variáveis Encontradas (24 total)

✅ Todas estas variáveis estão no arquivo:
- DISCORD_TOKEN
- DISCORD_CLIENT_ID
- DISCORD_GUILD_ID
- DB_HOST ⚠️ (precisa ajustar)
- DB_USER
- DB_PASSWORD
- DB_NAME
- ROBLOX_COOKIE
- E mais 16 outras...

---

## 🆘 Problemas?

### Variável não encontrada
- Verifique se copiou TODO o conteúdo
- Verifique se salvou após colar
- Verifique se não há espaços extras

### Bot não inicia
- Verifique os logs no Railway
- Verifique se `DB_HOST` está correto
- Verifique se todas as variáveis foram adicionadas

### Erro de conexão com banco
- Verifique se `DB_HOST` não é `localhost`
- Verifique se o banco permite conexões externas
- Verifique `DB_USER`, `DB_PASSWORD`, `DB_NAME`

---

## 🎉 Pronto!

Após adicionar as variáveis e ajustar o `DB_HOST`, seu bot estará rodando 24/7 na nuvem!

