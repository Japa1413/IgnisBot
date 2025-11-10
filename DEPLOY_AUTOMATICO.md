# 🚀 Deploy Automático - IgnisBot

## ✅ O que foi feito automaticamente:

1. ✅ **Código commitado** - Todas as alterações foram commitadas
2. ✅ **Push para GitHub** - Código enviado para o repositório
3. ✅ **Dockerfile criado** - Pronto para containerização
4. ✅ **Configurações criadas** - Railway e Render configurados

## 🎯 Próximo Passo (Você precisa fazer):

### Deploy no Railway (5 minutos):

1. **Acesse**: https://railway.app
2. **Faça login** com sua conta GitHub
3. **Clique em "New Project"**
4. **Selecione "Deploy from GitHub repo"**
5. **Escolha o repositório**: `Japa1413/IgnisBot`
6. **Aguarde o Railway detectar o Dockerfile** (automático)
7. **Vá em "Variables"** e adicione TODAS as variáveis do seu `.env`:
   ```
   DISCORD_TOKEN=seu_token
   DATABASE_HOST=seu_host
   DATABASE_USER=seu_usuario
   DATABASE_PASSWORD=sua_senha
   DATABASE_NAME=seu_banco
   ROBLOX_COOKIE=seu_cookie
   GUILD_ID=seu_guild_id
   ```
   (Adicione TODAS as variáveis que você tem no .env)

8. **Aguarde o deploy** (2-5 minutos)
9. **Verifique os logs** no dashboard do Railway
10. **Teste no Discord** com o comando `/health`

## 🎉 Pronto!

Seu bot estará rodando 24/7 na nuvem, sem precisar do seu computador!

## 📊 Monitoramento:

- **Logs**: Veja no dashboard do Railway
- **Status**: Use `/health` no Discord
- **Recursos**: O comando `/health` mostra CPU, memória, disco e GPU

## 🔄 Atualizações Futuras:

Quando você fizer alterações:
1. Faça commit e push normalmente
2. Railway atualiza automaticamente!

## 🆘 Problemas?

- Verifique os logs no Railway
- Use `/health` no Discord para ver status
- Verifique se todas as variáveis estão configuradas

