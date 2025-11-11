# 🔧 Corrigir Host Errado no Railway

## ❌ Erro Atual

```
Can't connect to MySQL server on 'ignisbot.railway.internal'
OSError: [Errno 111] Connect call failed
```

**Problema:** O `DB_HOST` está configurado com o host do **IgnisBot** em vez do host do **MySQL**.

---

## ✅ Solução: Usar Host do MySQL

O `${{RAILWAY_PRIVATE_DOMAIN}}` está resolvendo para o domínio do IgnisBot, não do MySQL.

### Opção 1: Usar Host Público do MySQL (Mais Simples)

1. **No serviço MySQL:**
   - Vá em **"Connect"** ou **"Data"**
   - Procure por **"Public Networking"** ou **"Public Domain"**
   - Copie o host público (ex: `containers-us-west-123.railway.app`)

2. **No serviço IgnisBot:**
   - Settings → Variables
   - Edite `DB_HOST`
   - Cole o host público do MySQL
   - **NÃO use** `${{RAILWAY_PRIVATE_DOMAIN}}` ou `ignisbot.railway.internal`
   - Salve

### Opção 2: Usar Variável Específica do MySQL

Se o MySQL tem uma variável específica:

1. **No serviço MySQL:**
   - Settings → Variables
   - Procure por uma variável que contenha o host do MySQL
   - Pode ser algo como `MYSQL_PRIVATE_DOMAIN` ou similar
   - Copie o valor

2. **No serviço IgnisBot:**
   - Settings → Variables
   - Adicione uma nova variável com o nome que você encontrou
   - Use `${{NOME_DA_VARIAVEL}}` no `DB_HOST`

### Opção 3: Conectar Serviços (Se Disponível)

1. **No Railway:**
   - Vá no projeto
   - Procure por opção de conectar serviços
   - Conecte o IgnisBot ao MySQL
   - Railway criará variáveis automaticamente

---

## 📋 Configuração Correta

### No IgnisBot, configure:

```
DB_HOST=<HOST_PUBLICO_DO_MYSQL>
DB_USER=root
DB_PASSWORD=hiwaQeixxvKFwLDpHbMZvkzuQNxajdQY
DB_NAME=railway
DB_PORT=3306
```

**Onde `<HOST_PUBLICO_DO_MYSQL>` é:**
- O host público do MySQL (com `.railway.app`)
- **NÃO** use `ignisbot.railway.internal`
- **NÃO** use `${{RAILWAY_PRIVATE_DOMAIN}}` (resolve para IgnisBot)

---

## 🔍 Como Encontrar o Host Correto

### Método 1: Via MySQL Variables

1. No serviço MySQL → Settings → Variables
2. Procure por variáveis que contenham um host
3. Pode estar em:
   - `MYSQLHOST`
   - `MYSQL_HOST`
   - `PUBLIC_DOMAIN`
   - Ou similar

### Método 2: Via Connect/Data

1. No serviço MySQL
2. Vá em **"Connect"** ou **"Data"**
3. Veja a string de conexão ou informações de rede
4. Copie o host público

### Método 3: Via Logs do MySQL

1. No serviço MySQL → Logs
2. Às vezes o Railway mostra o host nos logs de inicialização

---

## ⚠️ Erros Comuns

### Erro: "Connect call failed"

**Causa:** Host incorreto ou MySQL não acessível.

**Solução:**
- Verifique se está usando o host do MySQL, não do IgnisBot
- Use o host público (com `.railway.app`)
- Verifique se o MySQL está "Running"

### Erro: "ignisbot.railway.internal"

**Causa:** `DB_HOST` está usando o domínio do IgnisBot.

**Solução:**
- Mude `DB_HOST` para o host do MySQL
- Não use `${{RAILWAY_PRIVATE_DOMAIN}}` se resolve para IgnisBot

---

## ✅ Checklist

- [ ] Host do MySQL identificado (público ou privado específico)
- [ ] `DB_HOST` atualizado com host do MySQL
- [ ] `DB_USER` = `root`
- [ ] `DB_PASSWORD` = senha correta
- [ ] `DB_NAME` = `railway`
- [ ] `DB_PORT` = `3306`
- [ ] Bot reiniciado
- [ ] Logs verificados
- [ ] Conexão bem-sucedida

---

## 🎯 Exemplo de Configuração Correta

Se o MySQL tem host público `containers-us-west-123.railway.app`:

```
DB_HOST=containers-us-west-123.railway.app
DB_USER=root
DB_PASSWORD=hiwaQeixxvKFwLDpHbMZvkzuQNxajdQY
DB_NAME=railway
DB_PORT=3306
```

---

**Última atualização:** 2025-01-11

