# ✅ Como Verificar se o Banco Está Funcionando

## 🎯 Teste Rápido (2 minutos)

### 1. Verificar Logs no Railway

1. Acesse https://railway.app
2. Selecione seu projeto **IgnisBot**
3. Vá em **"Deployments"**
4. Clique no deployment mais recente
5. Veja os logs

**Procure por estas mensagens:**

✅ **Funcionando:**
- "Database pool initialized"
- "Connected to database"
- "Database connection successful"
- Sem erros de conexão

❌ **Problema:**
- "Can't connect to MySQL server"
- "Access denied for user"
- "Unknown database"
- Qualquer erro relacionado a MySQL/database

### 2. Testar no Discord

1. Abra o Discord
2. Use o comando: `/health`
3. Verifique a seção **"Database"**

**Deve mostrar:**
- ✅ Status: **HEALTHY**
- ⏱️ Latency: um número (ex: 5.23ms)
- 🔌 Pool Size: números
- 📊 Utilization: percentual

**Se mostrar erro:**
- ❌ Status: **UNHEALTHY** ou **ERROR**
- Mensagem de erro específica

### 3. Testar Comando do Bot

1. Use qualquer comando do bot (ex: `/userinfo`)
2. Se o bot responder normalmente = banco funcionando!
3. Se o bot não responder ou der erro = pode ser problema de banco

---

## 🔍 Análise Detalhada dos Logs

### Logs que Indicam Sucesso:

```
[INFO] Database pool initialized: 2-10 connections
[INFO] Connected to database successfully
[INFO] Database health check passed
```

### Logs que Indicam Problema:

```
[ERROR] Can't connect to MySQL server on 'mysql.railway.internal'
[ERROR] Access denied for user 'root'@'xxx'
[ERROR] Unknown database 'railway'
[ERROR] Connection timeout
```

---

## 🛠️ Se Encontrar Erros

### Erro: "Can't connect to MySQL server"

**Possíveis causas:**
1. `DB_HOST` incorreto
2. Banco não está rodando
3. Firewall bloqueando

**Soluções:**
1. Verifique se `DB_HOST` = `mysql.railway.internal`
2. Verifique se o banco está "Running" no Railway
3. Se o banco está em outro projeto, pode precisar do host externo

### Erro: "Access denied"

**Possíveis causas:**
1. `DB_USER` ou `DB_PASSWORD` incorretos
2. Usuário não tem permissões

**Soluções:**
1. Verifique se `DB_USER` = `root`
2. Verifique se `DB_PASSWORD` está correto (sem espaços)
3. Confirme as credenciais no serviço do banco no Railway

### Erro: "Unknown database"

**Possíveis causas:**
1. `DB_NAME` incorreto
2. Banco não foi criado

**Soluções:**
1. Verifique se `DB_NAME` = `railway`
2. Verifique se o banco existe no Railway

---

## ✅ Checklist de Verificação

- [ ] Logs mostram "Database pool initialized"
- [ ] Sem erros de conexão nos logs
- [ ] Comando `/health` mostra Database: HEALTHY
- [ ] Bot responde aos comandos normalmente
- [ ] Variáveis configuradas corretamente

**Se todos estão ✅, seu banco está funcionando perfeitamente!**

---

## 💡 Importante

**Você NÃO precisa de uma conexão explícita no Railway se:**
- ✅ As variáveis estão configuradas
- ✅ Os logs não mostram erros
- ✅ O comando `/health` funciona

A conexão explícita é apenas uma conveniência. O que realmente importa é que as variáveis estejam corretas e o bot consiga conectar!

