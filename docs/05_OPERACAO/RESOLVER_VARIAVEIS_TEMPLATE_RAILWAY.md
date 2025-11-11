# 🔧 Resolver Variáveis de Template do Railway

## ⚠️ Problema

As variáveis do MySQL mostram templates como `${{RAILWAY_PRIVATE_DOMAIN}}` em vez de valores reais.

---

## ✅ Solução 1: Usar Variáveis do Railway (Recomendado)

Se o **IgnisBot** e o **MySQL** estão no **mesmo projeto**, você pode usar as variáveis do Railway diretamente!

### Passo a Passo:

1. **No serviço IgnisBot:**
   - Settings → Variables
   - Adicione estas variáveis:

   **DB_HOST:**
   - Nome: `DB_HOST`
   - Valor: `${{RAILWAY_PRIVATE_DOMAIN}}`
   - ⚠️ **Use exatamente assim, com `${{}}`!**

   **DB_USER:**
   - Nome: `DB_USER`
   - Valor: `root`

   **DB_PASSWORD:**
   - Nome: `DB_PASSWORD`
   - Valor: `${{MYSQL_ROOT_PASSWORD}}`
   - ⚠️ **Use exatamente assim, com `${{}}`!**

   **DB_NAME:**
   - Nome: `DB_NAME`
   - Valor: `railway`

   **DB_PORT:**
   - Nome: `DB_PORT`
   - Valor: `3306`

2. **Salvar e aguardar:**
   - Railway resolverá automaticamente as variáveis `${{}}`
   - Bot reiniciará automaticamente

---

## ✅ Solução 2: Obter Valores Reais (Se não funcionar)

Se a Solução 1 não funcionar, você precisa dos valores reais:

### Passo 1: Ver Valores Reais no MySQL

1. **No serviço MySQL:**
   - Vá em **Settings → Variables**
   - Procure por variáveis que **NÃO** começam com `${{}}`
   - Ou veja em **"Connect"** ou **"Data"** para ver a string de conexão

### Passo 2: Alternativa - Usar RAILWAY_PRIVATE_DOMAIN

Se você não consegue ver os valores, tente:

1. **No serviço IgnisBot:**
   - Settings → Variables
   - Adicione:

   **RAILWAY_PRIVATE_DOMAIN:**
   - Nome: `RAILWAY_PRIVATE_DOMAIN`
   - Valor: Copie do serviço MySQL (se disponível)

   **MYSQL_ROOT_PASSWORD:**
   - Nome: `MYSQL_ROOT_PASSWORD`
   - Valor: `hiwaQeixxvKFwLDpHbMZvkzuQNxajdQY` (o valor que você viu)

   **DB_HOST:**
   - Nome: `DB_HOST`
   - Valor: `${{RAILWAY_PRIVATE_DOMAIN}}`

   **DB_PASSWORD:**
   - Nome: `DB_PASSWORD`
   - Valor: `${{MYSQL_ROOT_PASSWORD}}`

---

## ✅ Solução 3: Usar Host Público (Mais Simples)

Se as soluções acima não funcionarem, use o host público:

### Passo 1: Obter Host Público

1. **No serviço MySQL:**
   - Vá em **"Connect"** ou **"Data"**
   - Procure por **"Public Networking"** ou **"Public Domain"**
   - Copie o host público (ex: `containers-us-west-123.railway.app`)

### Passo 2: Configurar no IgnisBot

1. **No serviço IgnisBot:**
   - Settings → Variables
   - Adicione:

   **DB_HOST:**
   - Nome: `DB_HOST`
   - Valor: O host público que você copiou

   **DB_USER:**
   - Nome: `DB_USER`
   - Valor: `root`

   **DB_PASSWORD:**
   - Nome: `DB_PASSWORD`
   - Valor: `hiwaQeixxvKFwLDpHbMZvkzuQNxajdQY`

   **DB_NAME:**
   - Nome: `DB_NAME`
   - Valor: `railway`

   **DB_PORT:**
   - Nome: `DB_PORT`
   - Valor: `3306`

---

## 📋 Configuração Recomendada (Solução 1)

Adicione estas variáveis no **IgnisBot**:

```
DB_HOST=${{RAILWAY_PRIVATE_DOMAIN}}
DB_USER=root
DB_PASSWORD=${{MYSQL_ROOT_PASSWORD}}
DB_NAME=railway
DB_PORT=3306
```

**E também adicione:**

```
MYSQL_ROOT_PASSWORD=hiwaQeixxvKFwLDpHbMZvkzuQNxajdQY
RAILWAY_PRIVATE_DOMAIN=${{RAILWAY_PRIVATE_DOMAIN}}
```

**OU** se você conseguir ver o valor real de `RAILWAY_PRIVATE_DOMAIN` no MySQL, use o valor real em vez de `${{}}`.

---

## 🔍 Como Ver Valores Reais

### Método 1: Via Railway CLI

1. Instale Railway CLI
2. Execute: `railway variables`
3. Veja os valores resolvidos

### Método 2: Via Logs

1. No serviço MySQL, veja os logs
2. Às vezes o Railway mostra valores reais nos logs de inicialização

### Método 3: Via Connect/Data

1. No serviço MySQL
2. Vá em **"Connect"** ou **"Data"**
3. Veja a string de conexão completa
4. Extraia o host e porta

---

## ⚠️ Importante

- `${{VARIABLE}}` é uma sintaxe de template do Railway
- Railway resolve automaticamente quando ambos os serviços estão no mesmo projeto
- Se não funcionar, use valores reais ou host público

---

## ✅ Checklist

- [ ] Variáveis adicionadas no IgnisBot
- [ ] `DB_HOST` configurado (com `${{}}` ou valor real)
- [ ] `DB_USER` = `root`
- [ ] `DB_PASSWORD` configurado (com `${{}}` ou valor real)
- [ ] `DB_NAME` = `railway`
- [ ] `DB_PORT` = `3306`
- [ ] Bot reiniciado
- [ ] Logs verificados
- [ ] Conexão bem-sucedida

---

**Última atualização:** 2025-01-11

