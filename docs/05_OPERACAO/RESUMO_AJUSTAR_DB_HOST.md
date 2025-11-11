# ⚡ Resumo Rápido - Ajustar DB_HOST

## 🎯 Método Mais Rápido

### No Railway:

1. **Vá em Settings > Variables**
2. **Encontre a variável `DB_HOST`**
3. **Clique nela para editar**
4. **Altere o valor:**

   **Se usar Railway Database:**
   - Vá no serviço do banco de dados
   - Vá em "Variables"
   - Copie o valor de `MYSQLHOST` (ou similar)
   - Cole em `DB_HOST` no projeto IgnisBot

   **Se usar banco externo:**
   - Cole o host do seu banco (ex: `us-east.connect.psdb.cloud`)
   - Salve

5. **Pronto!** O bot reiniciará automaticamente

---

## 📋 Variáveis que Precisam Ajustar

Além de `DB_HOST`, verifique também:
- `DB_USER` - usuário do banco
- `DB_PASSWORD` - senha do banco  
- `DB_NAME` - nome do banco
- `DB_PORT` - porta (geralmente 3306)

---

## ✅ Verificar se Funcionou

1. Veja os logs no Railway
2. Use `/health` no Discord
3. Deve mostrar "Database: HEALTHY"

---

## 📖 Guia Completo

Veja `COMO_AJUSTAR_DB_HOST.md` para instruções detalhadas com screenshots e troubleshooting.

