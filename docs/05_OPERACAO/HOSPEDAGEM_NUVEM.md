# ☁️ Hospedagem em Nuvem - IgnisBot 24/7

## 📋 Visão Geral

Este guia explica como hospedar o IgnisBot em serviços de nuvem para que ele funcione 24/7 sem depender do seu computador pessoal.

---

## 🎯 Opções de Hospedagem

### 1. **Railway** (Recomendado - Grátis para começar)
- ✅ Fácil de usar
- ✅ Deploy automático via Git
- ✅ 500 horas grátis/mês
- ✅ Suporte a Docker

### 2. **Render**
- ✅ Plano grátis disponível
- ✅ Deploy automático
- ✅ Fácil configuração

### 3. **DigitalOcean / VPS Linux**
- ✅ Controle total
- ✅ Mais barato a longo prazo
- ⚠️ Requer conhecimento técnico

### 4. **Heroku**
- ✅ Popular e confiável
- ⚠️ Não oferece mais plano grátis

---

## 🚀 Opção 1: Railway (Recomendado)

### Passo 1: Criar Conta

1. Acesse: https://railway.app
2. Faça login com GitHub
3. Crie um novo projeto

### Passo 2: Conectar Repositório

1. Clique em "New Project"
2. Selecione "Deploy from GitHub repo"
3. Escolha o repositório do IgnisBot
4. Railway detectará automaticamente o Dockerfile

### Passo 3: Configurar Variáveis de Ambiente

1. Vá em "Variables"
2. Adicione todas as variáveis do seu `.env`:
   - `DISCORD_TOKEN`
   - `DATABASE_HOST`
   - `DATABASE_USER`
   - `DATABASE_PASSWORD`
   - `DATABASE_NAME`
   - `ROBLOX_COOKIE`
   - E todas as outras necessárias

### Passo 4: Deploy

1. Railway iniciará o deploy automaticamente
2. Aguarde a conclusão
3. O bot estará rodando 24/7!

### Passo 5: Verificar Logs

1. Vá em "Deployments"
2. Clique no deployment mais recente
3. Veja os logs em tempo real

### Gerenciamento

- **Reiniciar**: Clique em "Redeploy"
- **Ver logs**: Aba "Deployments" → Logs
- **Atualizar**: Faça push no GitHub, Railway atualiza automaticamente

---

## 🚀 Opção 2: Render

### Passo 1: Criar Conta

1. Acesse: https://render.com
2. Faça login com GitHub
3. Crie uma conta (plano grátis disponível)

### Passo 2: Criar Web Service

1. Clique em "New +"
2. Selecione "Web Service"
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: `ignisbot`
   - **Environment**: `Docker`
   - **Region**: Escolha o mais próximo
   - **Branch**: `main` ou `master`
   - **Root Directory**: `.` (raiz)

### Passo 3: Configurar Variáveis

1. Vá em "Environment"
2. Adicione todas as variáveis do `.env`

### Passo 4: Deploy

1. Clique em "Create Web Service"
2. Render iniciará o build
3. Aguarde a conclusão

### Gerenciamento

- **Reiniciar**: "Manual Deploy" → "Deploy latest commit"
- **Logs**: Aba "Logs"
- **Atualizar**: Push no GitHub atualiza automaticamente

---

## 🐧 Opção 3: VPS Linux (DigitalOcean, AWS, etc.)

### Pré-requisitos

- VPS Linux (Ubuntu 20.04+ recomendado)
- Acesso SSH
- Domínio (opcional)

### Passo 1: Conectar ao VPS

```bash
ssh root@seu-vps-ip
```

### Passo 2: Executar Script de Deploy

1. Faça upload dos arquivos do bot para o VPS:
   ```bash
   scp -r . root@seu-vps-ip:/tmp/ignisbot
   ```

2. Conecte ao VPS:
   ```bash
   ssh root@seu-vps-ip
   cd /tmp/ignisbot
   ```

3. Execute o script de deploy:
   ```bash
   chmod +x scripts/deploy_vps.sh
   sudo ./scripts/deploy_vps.sh
   ```

### Passo 3: Configurar .env

```bash
nano /opt/ignisbot/.env
# Cole todas as variáveis de ambiente
chown ignisbot:ignisbot /opt/ignisbot/.env
```

### Passo 4: Iniciar Serviço

```bash
systemctl start ignisbot
systemctl enable ignisbot
systemctl status ignisbot
```

### Gerenciamento

```bash
# Ver status
systemctl status ignisbot

# Ver logs
journalctl -u ignisbot -f

# Reiniciar
systemctl restart ignisbot

# Parar
systemctl stop ignisbot

# Atualizar código
cd /opt/ignisbot
git pull  # ou fazer upload dos arquivos
systemctl restart ignisbot
```

---

## 🐳 Opção 4: Docker em VPS

### Passo 1: Instalar Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### Passo 2: Clonar/Copiar Código

```bash
cd /opt
git clone seu-repositorio ignisbot
cd ignisbot
```

### Passo 3: Configurar .env

```bash
nano .env
# Adicione todas as variáveis
```

### Passo 4: Build e Run

```bash
docker-compose up -d
```

### Gerenciamento

```bash
# Ver logs
docker-compose logs -f

# Reiniciar
docker-compose restart

# Parar
docker-compose down

# Atualizar
git pull
docker-compose up -d --build
```

---

## 🔐 Segurança

### Recomendações Importantes

1. **Nunca commite o arquivo `.env`**
   - Adicione `.env` ao `.gitignore`
   - Use variáveis de ambiente do serviço

2. **Use senhas fortes**
   - Para banco de dados
   - Para tokens do Discord

3. **Mantenha atualizado**
   - Atualize dependências regularmente
   - Aplique patches de segurança

4. **Backup regular**
   - Faça backup do banco de dados
   - Mantenha cópias dos arquivos importantes

---

## 📊 Monitoramento

### Verificar Status

1. **Railway/Render**: Dashboard do serviço
2. **VPS**: `systemctl status ignisbot`
3. **Docker**: `docker-compose ps`

### Logs

1. **Railway**: Aba "Deployments" → Logs
2. **Render**: Aba "Logs"
3. **VPS**: `journalctl -u ignisbot -f`
4. **Docker**: `docker-compose logs -f`

### Comando `/health` no Discord

Use o comando `/health` no Discord para verificar:
- Status do bot
- Recursos do sistema (CPU, memória, disco)
- Status das integrações

---

## 💰 Custos Estimados

| Serviço | Plano Grátis | Plano Pago |
|---------|--------------|------------|
| **Railway** | 500h/mês | $5-20/mês |
| **Render** | Disponível | $7-25/mês |
| **DigitalOcean** | Não | $5-12/mês |
| **AWS EC2** | Não | $5-15/mês |

**Recomendação**: Comece com Railway (plano grátis) e migre para VPS se necessário.

---

## 🆘 Troubleshooting

### Bot não inicia

1. Verifique os logs do serviço
2. Verifique se todas as variáveis de ambiente estão configuradas
3. Teste localmente primeiro

### Bot para de funcionar

1. Verifique os logs
2. Verifique o status do serviço
3. Reinicie o serviço

### Erro de conexão com banco de dados

1. Verifique se o banco está acessível
2. Verifique credenciais
3. Verifique firewall/security groups

### Alto uso de recursos

1. Use o comando `/health` para verificar
2. Considere otimizar o código
3. Considere upgrade do plano

---

## 📚 Recursos Adicionais

- **Railway Docs**: https://docs.railway.app
- **Render Docs**: https://render.com/docs
- **Docker Docs**: https://docs.docker.com
- **Systemd Docs**: https://www.freedesktop.org/software/systemd/man/systemd.service.html

---

## ✅ Checklist de Deploy

- [ ] Conta criada no serviço escolhido
- [ ] Repositório conectado (ou arquivos enviados)
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy executado com sucesso
- [ ] Bot responde no Discord
- [ ] Comando `/health` funciona
- [ ] Logs estão sendo gerados
- [ ] Backup configurado (opcional)

---

## 🎉 Pronto!

Seu bot agora está rodando 24/7 na nuvem! 🚀

