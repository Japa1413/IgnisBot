# ⚡ GUIA RÁPIDO DE CONFIGURAÇÃO - IGNISBOT

**Tempo estimado:** 5-10 minutos  
**Status:** ⚠️ Aguardando preenchimento do `.env`

---

## 📝 PASSO 1: Preencher Arquivo `.env`

Abra o arquivo `.env` no editor de texto e substitua os valores de exemplo pelos seus valores reais:

### 🔑 Credenciais Discord (OBRIGATÓRIAS)

```env
DISCORD_TOKEN=seu_token_real_aqui
DISCORD_CLIENT_ID=seu_client_id_real_aqui
DISCORD_GUILD_ID=seu_guild_id_real_aqui
```

**Como obter:**

#### Discord Token:
1. Acesse: https://discord.com/developers/applications
2. Selecione seu bot ou crie um novo
3. Vá em **"Bot"** → Clique em **"Reset Token"** ou **"Copy"**
4. Cole no `.env` (DISCORD_TOKEN)

#### Client ID:
1. Na mesma página do Discord Developer Portal
2. Vá em **"General Information"**
3. Copie o **Application ID**
4. Cole no `.env` (DISCORD_CLIENT_ID)

#### Guild ID (ID do Servidor):
1. No Discord, ative o **Modo Desenvolvedor**:
   - Configurações → Avançado → Modo Desenvolvedor (ON)
2. Clique com botão direito no servidor → **"Copiar ID"**
3. Cole no `.env` (DISCORD_GUILD_ID)

---

### 💾 Credenciais MySQL (OBRIGATÓRIAS)

```env
DB_HOST=localhost
DB_USER=seu_usuario_mysql
DB_PASSWORD=sua_senha_mysql
DB_NAME=ignis
```

**O que fazer:**

1. **Criar banco de dados:**
   ```sql
   CREATE DATABASE ignis CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **Criar usuário (opcional, pode usar root):**
   ```sql
   CREATE USER 'ignis_user'@'localhost' IDENTIFIED BY 'senha_segura';
   GRANT ALL PRIVILEGES ON ignis.* TO 'ignis_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. **Ou usar root:**
   ```env
   DB_USER=root
   DB_PASSWORD=sua_senha_root
   ```

---

### ⚙️ Configurações Opcionais (Podem ficar como padrão)

Estas configurações já estão com valores padrão razoáveis:

```env
# Voice Channel IDs (você pode ajustar depois)
VC_CHANNEL_IDS=1375977001617199216

# Command Channel IDs (você pode ajustar depois)
STAFF_CMDS_CHANNEL_ID=1375941286267326530
USERINFO_CHANNEL_ID=1375941286267326532
SUMMARY_CHANNEL_FALLBACK_ID=1375807338094530753

# Allowed Voice Channels
ALLOWED_VC_IDS=1386490773431783434,1375941286267326524,1375941286267326525,1375941286267326526,1375941286267326527

# Logging (já configurado)
LOG_LEVEL=INFO
LOG_FILE=logs/ignisbot.log
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5

# Privacy & Compliance (opcional - configure depois se necessário)
PRIVACY_POLICY_URL=
TERMS_OF_USE_URL=
CONTROLLER_EMAIL=

# Security (já configurado)
ENABLE_RATE_LIMITING=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# Application (já configurado)
APP_ENV=production
DEBUG=false
```

---

## ✅ PASSO 2: Verificar Configuração

Depois de preencher o `.env`, execute:

```bash
python verificar_setup.py
```

**O que esperar:**
- ✅ Todas as verificações devem passar (exceto banco se MySQL não estiver rodando)
- ⚠️ Se falhar, corrija os erros indicados

---

## 🚀 PASSO 3: Executar o Bot

Quando tudo estiver configurado:

```bash
python ignis_main.py
```

**O que você verá:**
```
🔥 Logged in as IgnisBot#1234 (id=...)
✅ Purged & synced X commands for guild ...
```

---

## ⚠️ TROUBLESHOOTING

### Erro: "Variável de ambiente não configurada"
- Verifique se o `.env` está na raiz do projeto
- Verifique se não há espaços extras: `DISCORD_TOKEN=token` (não `DISCORD_TOKEN = token`)

### Erro: "Cannot connect to MySQL"
- Verifique se o MySQL está rodando: `mysql -u root -p`
- Verifique se o banco `ignis` existe
- Verifique credenciais no `.env`

### Erro: "Invalid Discord Token"
- Verifique se o token está correto (sem espaços)
- Verifique se o bot está ativado no Discord Developer Portal

### Erro: "Missing Permissions"
- Adicione o bot ao servidor com permissões adequadas
- Verifique se o bot tem as permissões necessárias no servidor

---

## 📞 PRÓXIMOS PASSOS

Após preencher o `.env`:

1. Execute: `python verificar_setup.py`
2. Se tudo estiver OK, execute: `python ignis_main.py`
3. Teste os comandos no Discord!

---

**Status:** ⏳ Aguardando você preencher o `.env`  
**Quando estiver pronto:** Execute `python ignis_main.py`

