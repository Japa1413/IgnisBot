# 🔧 Resolver Erro de Conexão com Banco de Dados

## ✅ Progresso: ModuleNotFoundError Resolvido!

O bot agora encontra os módulos corretamente! O problema atual é conexão com o banco de dados.

---

## ❌ Erro Atual

```
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server on 'mysql.railway.internal'")
```

**Causa:** O bot não consegue conectar ao banco de dados MySQL no Railway.

---

## 🔍 Diagnóstico

### O que o erro significa:

- `mysql.railway.internal` é um host interno do Railway
- Só funciona se o banco estiver **no mesmo projeto** e **conectado**
- Se o banco está em outro projeto ou não está conectado, esse host não funciona

---

## ✅ Soluções

### Solução 1: Conectar o Banco ao Projeto (Recomendado)

1. **No Railway Dashboard:**
   - Vá em seu projeto **IgnisBot**
   - Clique em **Settings**
   - Vá em **"Service Connections"** ou **"Connect"**
   - Clique em **"Connect Database"** ou **"Add Service"**
   - Selecione o banco MySQL que você criou
   - Railway conectará automaticamente

2. **Após conectar:**
   - O Railway criará variáveis de ambiente automaticamente
   - O host `mysql.railway.internal` funcionará
   - O bot deve conectar automaticamente

### Solução 2: Usar Host Externo (Se banco está em outro projeto)

Se o banco está em outro projeto ou você não consegue conectar:

1. **No Railway:**
   - Vá no serviço do **banco de dados**
   - Vá em **"Variables"**
   - Copie o valor de `MYSQLHOST` (ou similar)
   - Este será o host externo (ex: `containers-us-west-xxx.railway.app`)

2. **No projeto IgnisBot:**
   - Vá em **Settings > Variables**
   - Atualize `DB_HOST` com o host externo
   - Salve

3. **Verifique outras variáveis:**
   - `DB_USER` = usuário do banco
   - `DB_PASSWORD` = senha do banco
   - `DB_NAME` = nome do banco
   - `DB_PORT` = porta (geralmente 3306)

### Solução 3: Criar Banco no Mesmo Projeto

1. **No projeto IgnisBot:**
   - Clique em **"New"** ou **"+"**
   - Selecione **"Database"**
   - Escolha **"MySQL"**
   - Railway criará o banco no mesmo projeto

2. **Conectar automaticamente:**
   - Railway conectará automaticamente
   - Variáveis serão criadas automaticamente
   - `mysql.railway.internal` funcionará

---

## 🔍 Verificar Configuração Atual

### No Railway, verifique:

1. **Variáveis de Ambiente:**
   - `DB_HOST` = deve ser `mysql.railway.internal` (se banco no mesmo projeto)
   - `DB_USER` = usuário do banco
   - `DB_PASSWORD` = senha do banco
   - `DB_NAME` = nome do banco

2. **Status do Banco:**
   - O banco deve estar **"Running"**
   - Não deve estar parado ou com erro

3. **Conexão:**
   - Verifique se o banco está conectado ao projeto
   - Veja em **Settings > Service Connections**

---

## 🆘 Troubleshooting

### Erro: "Name or service not known"

**Causa:** O host `mysql.railway.internal` não pode ser resolvido.

**Soluções:**
1. Conecte o banco ao projeto (Solução 1)
2. Use o host externo (Solução 2)
3. Crie o banco no mesmo projeto (Solução 3)

### Erro: "Access denied"

**Causa:** Credenciais incorretas.

**Solução:**
- Verifique `DB_USER` e `DB_PASSWORD`
- Confirme as credenciais no serviço do banco

### Erro: "Unknown database"

**Causa:** Nome do banco incorreto.

**Solução:**
- Verifique `DB_NAME`
- Confirme o nome do banco no Railway

---

## 📝 Checklist

- [ ] Banco de dados criado no Railway
- [ ] Banco está "Running"
- [ ] Banco conectado ao projeto (Service Connections)
- [ ] Variáveis de ambiente configuradas:
  - [ ] `DB_HOST`
  - [ ] `DB_USER`
  - [ ] `DB_PASSWORD`
  - [ ] `DB_NAME`
- [ ] Logs verificados (sem erros de conexão)
- [ ] Bot conecta ao banco com sucesso

---

## ✅ Após Resolver

Quando a conexão funcionar, você verá nos logs:
- "Database pool initialized"
- "Connected to database successfully"
- Bot iniciando normalmente

---

**Última atualização:** 2025-01-11

