# ✅ Configurar Host MySQL no Railway

## 🎯 Host do MySQL Identificado

Você forneceu:
```
turntable.proxy.rlwy.net:27262
```

Isso significa:
- **Host:** `turntable.proxy.rlwy.net`
- **Porta:** `27262`

---

## 📋 Configuração no IgnisBot

### No serviço IgnisBot → Settings → Variables:

#### 1. DB_HOST
- **Nome:** `DB_HOST`
- **Valor:** `turntable.proxy.rlwy.net`
- ⚠️ **IMPORTANTE:** Use apenas o host, **SEM** a porta!

#### 2. DB_PORT
- **Nome:** `DB_PORT`
- **Valor:** `27262`
- ⚠️ **IMPORTANTE:** A porta é diferente do padrão (3306)!

#### 3. DB_USER
- **Nome:** `DB_USER`
- **Valor:** `root`

#### 4. DB_PASSWORD
- **Nome:** `DB_PASSWORD`
- **Valor:** `hiwaQeixxvKFwLDpHbMZvkzuQNxajdQY`

#### 5. DB_NAME
- **Nome:** `DB_NAME`
- **Valor:** `railway`

---

## ✅ Configuração Completa

Adicione/edite estas variáveis no IgnisBot:

```
DB_HOST=turntable.proxy.rlwy.net
DB_PORT=27262
DB_USER=root
DB_PASSWORD=hiwaQeixxvKFwLDpHbMZvkzuQNxajdQY
DB_NAME=railway
```

---

## ⚠️ Importante

1. **Host e Porta Separados:**
   - `DB_HOST` = apenas o host (sem porta)
   - `DB_PORT` = apenas a porta

2. **Porta Não Padrão:**
   - A porta `27262` é diferente do padrão MySQL (3306)
   - Certifique-se de configurar `DB_PORT=27262`

3. **Após Salvar:**
   - Railway reiniciará automaticamente
   - Aguarde alguns segundos
   - Verifique os logs

---

## 🔍 Verificar Logs

Após configurar, veja os logs do IgnisBot:

**✅ Sucesso:**
```
Database pool initialized
Connected to database successfully
Bot is ready!
```

**❌ Erro:**
Se ainda der erro, verifique:
- Se `DB_HOST` está sem porta
- Se `DB_PORT` está configurado como `27262`
- Se todas as variáveis foram salvas

---

## 📝 Checklist

- [ ] `DB_HOST` = `turntable.proxy.rlwy.net` (sem porta)
- [ ] `DB_PORT` = `27262` (porta correta)
- [ ] `DB_USER` = `root`
- [ ] `DB_PASSWORD` = senha correta
- [ ] `DB_NAME` = `railway`
- [ ] Bot reiniciado
- [ ] Logs verificados
- [ ] Conexão bem-sucedida

---

**Última atualização:** 2025-01-11

