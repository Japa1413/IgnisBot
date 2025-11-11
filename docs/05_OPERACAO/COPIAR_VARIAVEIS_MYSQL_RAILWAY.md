# 📋 Copiar Variáveis do MySQL para IgnisBot

## 🎯 Objetivo

Copiar as variáveis de conexão do serviço MySQL e configurá-las no serviço ignisbot.

---

## 📝 Passo a Passo Visual

### 1️⃣ Abrir o Serviço MySQL

1. No Railway, clique no card **MySQL** (o que está funcionando)
2. Vá na aba **"Variables"** (lateral esquerda)

### 2️⃣ Copiar as Variáveis

Você verá variáveis como estas:

```
MYSQLHOST=containers-us-west-123.railway.app
MYSQLUSER=root
MYSQLPASSWORD=anAaBcReAOiQZcEWbYbGSQeCzLoyzHWV
MYSQLDATABASE=railway
MYSQLPORT=3306
```

**Copie cada valor:**
- `MYSQLHOST` → será `DB_HOST`
- `MYSQLUSER` → será `DB_USER`
- `MYSQLPASSWORD` → será `DB_PASSWORD`
- `MYSQLDATABASE` → será `DB_NAME`
- `MYSQLPORT` → será `3306` (geralmente)

### 3️⃣ Abrir o Serviço IgnisBot

1. No Railway, clique no card **ignisbot** (o que está com erro)
2. Vá em **Settings** (lateral esquerda)
3. Vá em **Variables** (aba dentro de Settings)

### 4️⃣ Adicionar/Atualizar Variáveis

Para cada variável abaixo, clique em **"New Variable"** ou edite se já existir:

#### ✅ DB_HOST

- **Nome:** `DB_HOST`
- **Valor:** Cole o valor de `MYSQLHOST` que você copiou
- **Exemplo:** `containers-us-west-123.railway.app`
- ⚠️ **IMPORTANTE:** Use o host externo (com `.railway.app`), **NÃO** use `mysql.railway.internal`!

#### ✅ DB_USER

- **Nome:** `DB_USER`
- **Valor:** Cole o valor de `MYSQLUSER` que você copiou
- **Exemplo:** `root`

#### ✅ DB_PASSWORD

- **Nome:** `DB_PASSWORD`
- **Valor:** Cole o valor de `MYSQLPASSWORD` que você copiou
- **Exemplo:** `anAaBcReAOiQZcEWbYbGSQeCzLoyzHWV`

#### ✅ DB_NAME

- **Nome:** `DB_NAME`
- **Valor:** Cole o valor de `MYSQLDATABASE` que você copiou
- **Exemplo:** `railway`

#### ✅ DB_PORT (Opcional, mas recomendado)

- **Nome:** `DB_PORT`
- **Valor:** `3306` (ou o valor de `MYSQLPORT` se diferente)
- **Exemplo:** `3306`

### 5️⃣ Salvar e Aguardar

1. Após adicionar todas as variáveis, o Railway **reiniciará automaticamente** o serviço
2. Aguarde alguns segundos
3. Vá em **Deployments** para ver o novo deployment

### 6️⃣ Verificar Logs

1. Clique no deployment mais recente
2. Veja os logs de runtime
3. Procure por:

**✅ Sucesso:**
```
Database pool initialized
Connected to database successfully
Bot is ready!
```

**❌ Erro:**
Se ainda der erro de conexão, verifique:
- Se copiou o host correto (deve ter `.railway.app`)
- Se todas as variáveis foram salvas
- Se o MySQL está "Running"

---

## 🔍 Mapeamento Completo

| Variável MySQL | Variável IgnisBot | Obrigatório |
|----------------|-------------------|-------------|
| `MYSQLHOST` | `DB_HOST` | ✅ Sim |
| `MYSQLUSER` | `DB_USER` | ✅ Sim |
| `MYSQLPASSWORD` | `DB_PASSWORD` | ✅ Sim |
| `MYSQLDATABASE` | `DB_NAME` | ✅ Sim |
| `MYSQLPORT` | `DB_PORT` | ⚠️ Opcional (padrão: 3306) |

---

## ⚠️ Erros Comuns

### Erro: "Can't connect to MySQL server"

**Causa:** Host incorreto ou banco não acessível.

**Solução:**
- Verifique se copiou o `MYSQLHOST` correto
- Certifique-se de usar o host externo (com `.railway.app`)
- Verifique se o MySQL está "Running"

### Erro: "Access denied"

**Causa:** Credenciais incorretas.

**Solução:**
- Verifique se copiou `DB_USER` e `DB_PASSWORD` corretamente
- Confirme no serviço MySQL

### Erro: "Unknown database"

**Causa:** Nome do banco incorreto.

**Solução:**
- Verifique se copiou `DB_NAME` corretamente
- Confirme no serviço MySQL

---

## ✅ Checklist Final

- [ ] MySQL aberto e variáveis copiadas
- [ ] `DB_HOST` configurado (host externo)
- [ ] `DB_USER` configurado
- [ ] `DB_PASSWORD` configurado
- [ ] `DB_NAME` configurado
- [ ] `DB_PORT` configurado (3306)
- [ ] Bot reiniciado
- [ ] Logs verificados
- [ ] Conexão bem-sucedida

---

## 🎉 Após Configurar

Quando funcionar, você verá:
- ✅ Deployment successful
- ✅ Bot conectado ao banco
- ✅ Bot online no Discord
- ✅ Comando `/health` mostra Database: HEALTHY

---

**Última atualização:** 2025-01-11

