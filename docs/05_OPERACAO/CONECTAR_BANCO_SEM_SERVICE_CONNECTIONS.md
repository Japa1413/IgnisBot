# 🔗 Conectar Banco sem Service Connections

## ⚠️ Problema

A opção "Service Connections" não aparece no Railway, ou você não consegue encontrá-la.

## ✅ Solução: Usar Host Externo

Mesmo sem Service Connections, você pode conectar usando o host externo do banco.

---

## 📋 Passo a Passo

### Passo 1: Obter Host do Banco

1. **No Railway Dashboard:**
   - Vá no serviço do **banco de dados MySQL** (não no projeto IgnisBot)
   - Clique no banco de dados
   - Vá em **"Variables"** (aba lateral)
   - Procure por `MYSQLHOST` ou `MYSQL_HOST`
   - **Copie o valor** (ex: `containers-us-west-123.railway.app`)

### Passo 2: Obter Outras Variáveis

No mesmo lugar (Variables do banco), copie também:
- `MYSQLUSER` ou `MYSQL_USER` → será seu `DB_USER`
- `MYSQLPASSWORD` ou `MYSQL_PASSWORD` → será seu `DB_PASSWORD`
- `MYSQLDATABASE` ou `MYSQL_DATABASE` → será seu `DB_NAME`
- `MYSQLPORT` ou `MYSQL_PORT` → será sua porta (geralmente 3306)

### Passo 3: Atualizar Variáveis no Projeto IgnisBot

1. **No Railway:**
   - Vá no projeto **IgnisBot**
   - Clique em **Settings**
   - Vá em **Variables**

2. **Atualize ou adicione estas variáveis:**

   **DB_HOST:**
   - Se já existe, clique para editar
   - Cole o host que você copiou (ex: `containers-us-west-123.railway.app`)
   - **NÃO use** `mysql.railway.internal` - use o host externo!
   - Salve

   **DB_USER:**
   - Atualize com o valor de `MYSQLUSER`
   - Geralmente é `root`
   - Salve

   **DB_PASSWORD:**
   - Atualize com o valor de `MYSQLPASSWORD`
   - Salve

   **DB_NAME:**
   - Atualize com o valor de `MYSQLDATABASE`
   - Geralmente é `railway`
   - Salve

   **DB_PORT (opcional):**
   - Se não existe, adicione
   - Valor: `3306` (padrão MySQL)
   - Salve

### Passo 4: Verificar

1. **Aguarde o bot reiniciar** (Railway reinicia automaticamente após mudar variáveis)

2. **Veja os logs:**
   - Vá em **Deployments**
   - Clique no deployment mais recente
   - Veja os logs de runtime
   - Procure por:
     - ✅ "Database pool initialized"
     - ✅ "Connected to database successfully"
     - ❌ Se ainda der erro, veja a mensagem

---

## 🔍 Exemplo de Variáveis Corretas

### Se o banco está no Railway:

```
DB_HOST=containers-us-west-123.railway.app
DB_USER=root
DB_PASSWORD=anAaBcReAOiQZcEWbYbGSQeCzLoyzHWV
DB_NAME=railway
DB_PORT=3306
```

**IMPORTANTE:** Use o host **externo** (com `.railway.app`), não `mysql.railway.internal`!

---

## 🆘 Se Ainda Não Funciona

### Erro: "Can't connect"

**Possíveis causas:**
1. Host incorreto
2. Firewall bloqueando
3. Banco não permite conexões externas

**Soluções:**
1. Verifique se copiou o host correto
2. Verifique se o banco está "Running"
3. Tente usar o IP do banco (se disponível)

### Erro: "Access denied"

**Causa:** Credenciais incorretas.

**Solução:**
- Verifique se copiou `DB_USER` e `DB_PASSWORD` corretamente
- Confirme no serviço do banco

### Erro: "Unknown database"

**Causa:** Nome do banco incorreto.

**Solução:**
- Verifique `DB_NAME`
- Confirme no serviço do banco

---

## 📝 Checklist

- [ ] Host do banco copiado (MYSQLHOST)
- [ ] `DB_HOST` atualizado com host externo
- [ ] `DB_USER` atualizado
- [ ] `DB_PASSWORD` atualizado
- [ ] `DB_NAME` atualizado
- [ ] `DB_PORT` configurado (3306)
- [ ] Bot reiniciado
- [ ] Logs verificados
- [ ] Conexão bem-sucedida

---

## ✅ Após Configurar

Quando funcionar, você verá nos logs:
- "Database pool initialized"
- "Connected to database successfully"
- Bot iniciando normalmente
- Comando `/health` mostra Database: HEALTHY

---

**Última atualização:** 2025-01-11

