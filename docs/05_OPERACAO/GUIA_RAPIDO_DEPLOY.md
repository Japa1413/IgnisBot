# 🚀 Guia Rápido - Deploy IgnisBot 24/7 na Nuvem

## ⚡ Opção Mais Rápida: Railway (Recomendado)

### Passo 1: Preparar Código
```bash
# Certifique-se de que todos os arquivos estão commitados
git add .
git commit -m "Preparar para deploy"
git push
```

### Passo 2: Criar Conta Railway
1. Acesse: https://railway.app
2. Faça login com GitHub
3. Clique em "New Project"
4. Selecione "Deploy from GitHub repo"
5. Escolha seu repositório do IgnisBot

### Passo 3: Configurar Variáveis
1. No projeto Railway, vá em "Variables"
2. Adicione TODAS as variáveis do seu `.env`:
   - `DISCORD_TOKEN`
   - `DATABASE_HOST`
   - `DATABASE_USER`
   - `DATABASE_PASSWORD`
   - `DATABASE_NAME`
   - `ROBLOX_COOKIE`
   - `GUILD_ID`
   - E todas as outras que você usa

### Passo 4: Deploy Automático
- Railway detectará o Dockerfile automaticamente
- O deploy iniciará automaticamente
- Aguarde alguns minutos
- Pronto! Bot rodando 24/7! 🎉

---

## 🐧 Opção Alternativa: VPS Linux

### Se você tem um VPS:

1. Conecte ao VPS:
```bash
ssh root@seu-vps-ip
```

2. Faça upload dos arquivos:
```bash
# No seu computador
scp -r . root@seu-vps-ip:/tmp/ignisbot
```

3. Execute o script de deploy:
```bash
# No VPS
cd /tmp/ignisbot
chmod +x scripts/deploy_vps.sh
sudo ./scripts/deploy_vps.sh
```

4. Configure o .env:
```bash
nano /opt/ignisbot/.env
# Cole todas as variáveis
chown ignisbot:ignisbot /opt/ignisbot/.env
```

5. Inicie o serviço:
```bash
systemctl start ignisbot
systemctl enable ignisbot
systemctl status ignisbot
```

---

## ✅ Verificar se Está Funcionando

1. **No Discord**: Use o comando `/health`
2. **Railway**: Veja os logs no dashboard
3. **VPS**: `journalctl -u ignisbot -f`

---

## 📚 Documentação Completa

Veja `docs/05_OPERACAO/HOSPEDAGEM_NUVEM.md` para mais detalhes.

