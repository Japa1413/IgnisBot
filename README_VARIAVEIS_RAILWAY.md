# 🔐 Como Gerar Variáveis para Railway

## ⚡ Método Automático

Execute o script que lê seu `.env` e cria o arquivo formatado:

```powershell
.\scripts\gerar_variaveis_railway.ps1
```

Isso criará o arquivo `RAILWAY_VARIABLES.txt` com todas as variáveis prontas para copiar/colar no Railway.

## 📋 Como Usar no Railway

1. **Abra o arquivo** `RAILWAY_VARIABLES.txt`
2. **Copie TODO o conteúdo** (Ctrl+A, Ctrl+C)
3. **No Railway:**
   - Vá em Settings > Variables
   - Clique em "Raw Editor" (canto superior direito)
   - Cole o conteúdo (Ctrl+V)
   - Clique em "Save"

## ⚠️ IMPORTANTE

- O arquivo `RAILWAY_VARIABLES.txt` contém informações sensíveis
- **NÃO** commite este arquivo no Git (já está no .gitignore)
- **NÃO** compartilhe este arquivo
- Após usar, você pode deletar o arquivo se quiser

## 🔧 Ajuste Necessário

O arquivo gerado tem `DB_HOST=localhost`, mas você precisa alterar para o host real do seu banco de dados na nuvem.

No Railway, após adicionar as variáveis, edite `DB_HOST` e altere para o host correto do seu banco.

## 📖 Documentação Completa

Veja `COMO_ADICIONAR_VARIAVEIS_RAILWAY.md` para instruções detalhadas.

