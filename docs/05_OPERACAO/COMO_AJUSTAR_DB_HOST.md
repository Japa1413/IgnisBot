# 🔧 Como Ajustar DB_HOST no Railway

## 📋 Situação Atual

O arquivo `RAILWAY_VARIABLES.txt` tem:
```
DB_HOST=localhost
```

Isso precisa ser alterado para o host real do seu banco de dados.

---

## 🎯 Opção 1: Usar Railway Database (Recomendado)

### Passo 1: Criar Database no Railway

1. No Railway, clique em **"New"** (canto superior direito)
2. Selecione **"Database"**
3. Escolha **"MySQL"** (ou o tipo que você usa)
4. Railway criará automaticamente um banco de dados

### Passo 2: Obter as Variáveis

1. Clique no banco de dados criado
2. Vá em **"Variables"**
3. Railway já criou automaticamente:
   - `MYSQLHOST` (ou similar) - Este é o seu DB_HOST
   - `MYSQLUSER` - Este é o seu DB_USER
   - `MYSQLPASSWORD` - Este é o seu DB_PASSWORD
   - `MYSQLDATABASE` - Este é o seu DB_NAME
   - `MYSQLPORT` - Porta (geralmente 3306)

### Passo 3: Atualizar Variáveis no Projeto

1. No seu projeto IgnisBot, vá em **Settings > Variables**
2. Atualize as variáveis:
   - `DB_HOST` = valor de `MYSQLHOST` (ex: `containers-us-west-xxx.railway.app`)
   - `DB_USER` = valor de `MYSQLUSER` (geralmente `root`)
   - `DB_PASSWORD` = valor de `MYSQLPASSWORD`
   - `DB_NAME` = valor de `MYSQLDATABASE`
   - Adicione também `DB_PORT` = valor de `MYSQLPORT` (se necessário)

### Passo 4: Conectar os Serviços

1. No projeto IgnisBot, clique em **"Settings"**
2. Vá em **"Connect"** ou **"Service Connections"**
3. Clique em **"Connect Database"** ou **"Add Service"**
4. Selecione o banco de dados que você criou
5. Railway conectará automaticamente

---

## 🎯 Opção 2: Usar Banco de Dados Externo

Se você já tem um banco de dados em outro serviço (ex: PlanetScale, AWS RDS, etc.):

### Passo 1: Obter Informações de Conexão

Você precisa das seguintes informações do seu provedor de banco:
- **Host**: ex: `us-east.connect.psdb.cloud` ou `xxx.rds.amazonaws.com`
- **Porta**: geralmente `3306` para MySQL
- **Usuário**: seu usuário do banco
- **Senha**: sua senha do banco
- **Nome do banco**: nome do banco de dados

### Passo 2: Adicionar no Railway

1. No projeto IgnisBot, vá em **Settings > Variables**
2. Atualize as variáveis:
   - `DB_HOST` = host do seu banco (ex: `us-east.connect.psdb.cloud`)
   - `DB_USER` = usuário do banco
   - `DB_PASSWORD` = senha do banco
   - `DB_NAME` = nome do banco
   - `DB_PORT` = porta (geralmente `3306`)

### Passo 3: Verificar Firewall

Certifique-se de que o banco permite conexões do Railway:
- Adicione os IPs do Railway na whitelist do banco
- Ou permita conexões de qualquer IP (menos seguro, mas mais fácil)

---

## 🎯 Opção 3: Usar Banco Local (Não Recomendado para Produção)

Se você realmente precisa usar um banco local:

⚠️ **ATENÇÃO**: Isso só funciona se o Railway conseguir acessar seu computador, o que geralmente não é possível.

**Não recomendado** para produção. Use Railway Database ou banco externo.

---

## 📝 Exemplo de Variáveis Corretas

### Railway Database:
```
DB_HOST=containers-us-west-123.railway.app
DB_USER=root
DB_PASSWORD=abc123xyz
DB_NAME=railway
DB_PORT=3306
```

### PlanetScale:
```
DB_HOST=us-east.connect.psdb.cloud
DB_USER=abc123
DB_PASSWORD=xyz789
DB_NAME=ignis
DB_PORT=3306
```

### AWS RDS:
```
DB_HOST=mydb.123456789.us-east-1.rds.amazonaws.com
DB_USER=admin
DB_PASSWORD=senha123
DB_NAME=ignis
DB_PORT=3306
```

---

## ✅ Verificar se Está Funcionando

### 1. Verificar Logs no Railway

1. Vá em **Deployments**
2. Clique no deployment mais recente
3. Veja os logs
4. Procure por mensagens de conexão com banco

### 2. Testar no Discord

1. Use o comando `/health` no Discord
2. Verifique a seção "Database"
3. Deve mostrar status "HEALTHY"

### 3. Verificar Erros Comuns

**Erro: "Can't connect to MySQL server"**
- Verifique se `DB_HOST` está correto
- Verifique se o banco permite conexões externas
- Verifique firewall/security groups

**Erro: "Access denied"**
- Verifique `DB_USER` e `DB_PASSWORD`
- Verifique se o usuário tem permissões

**Erro: "Unknown database"**
- Verifique se `DB_NAME` está correto
- Verifique se o banco existe

---

## 🔄 Atualizar Código (Se Necessário)

Se seu código usa nomes diferentes de variáveis, você pode precisar ajustar:

### Verificar em `utils/config.py` ou similar:

```python
# Pode estar assim:
DB_HOST = os.getenv("DATABASE_HOST")  # Mas Railway tem DB_HOST

# Ajuste para:
DB_HOST = os.getenv("DB_HOST") or os.getenv("DATABASE_HOST")
```

---

## 🆘 Troubleshooting

### Problema: Não consigo encontrar as variáveis do Railway Database

**Solução:**
1. Clique no serviço do banco de dados
2. Vá em **"Variables"** (não Settings)
3. Lá você verá todas as variáveis de conexão

### Problema: Railway não conecta ao banco externo

**Solução:**
1. Verifique se o host está correto
2. Verifique se a porta está aberta
3. Verifique se o banco permite conexões do Railway
4. Alguns bancos precisam de SSL - adicione `DB_SSL=true` se necessário

### Problema: Erro de timeout

**Solução:**
1. Verifique se o host está correto
2. Verifique se não há firewall bloqueando
3. Tente aumentar o timeout no código

---

## 📚 Recursos

- [Railway Database Docs](https://docs.railway.app/databases)
- [Railway Variables Docs](https://docs.railway.app/develop/variables)

---

## ✅ Checklist

- [ ] Banco de dados criado/configurado
- [ ] Variáveis de conexão obtidas
- [ ] `DB_HOST` atualizado no Railway
- [ ] `DB_USER` atualizado
- [ ] `DB_PASSWORD` atualizado
- [ ] `DB_NAME` atualizado
- [ ] `DB_PORT` adicionado (se necessário)
- [ ] Logs verificados (sem erros de conexão)
- [ ] Comando `/health` testado no Discord
- [ ] Bot funcionando corretamente

---

## 🎉 Pronto!

Após ajustar o `DB_HOST` e as outras variáveis de banco, seu bot estará conectado ao banco de dados e funcionando 24/7!

