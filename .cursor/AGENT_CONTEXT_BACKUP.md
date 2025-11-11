# 🤖 BACKUP DO CONTEXTO DO AGENTE CURSOR - IGNISBOT

**Data do Backup:** 2025-01-11  
**Versão do Projeto:** Operacional 24/7 no Railway  
**Status:** ✅ Todas as funcionalidades implementadas e testadas

---

## 📋 RESUMO DO PROJETO

**IgnisBot** é um bot Discord completo para o servidor Age of Warfare, desenvolvido em Python usando `discord.py`. O bot está operacional 24/7 no Railway e inclui:

- Sistema de pontos e gamificação
- Integração com Roblox (Bloxlink + Roblox Groups API)
- Sistema de eventos (Salamanders Event Panel)
- Monitoramento de recursos (`/health`)
- Sistema de roadmap automatizado
- Conformidade LGPD completa
- Arquitetura em camadas (Layered Architecture)

---

## 🏗️ ESTRUTURA DO PROJETO

```
IgnisBot/
├── ignis_main.py          # Arquivo principal do bot
├── requirements.txt       # Dependências Python
├── .env                   # Variáveis de ambiente (NÃO COMMITAR)
├── env.example            # Template de variáveis de ambiente
├── Dockerfile             # Containerização para Railway
├── railway.json           # Configuração Railway
│
├── cogs/                  # Comandos do bot (discord.py)
│   ├── process.py         # Induction Process Button
│   ├── roadmap.py         # Roadmap automático
│   ├── health.py          # Health check com recursos do sistema
│   ├── rank.py            # Gerenciamento de ranks e nicknames
│   └── ...
│
├── services/              # Lógica de negócio
│   ├── roblox_groups_service.py    # API Roblox Groups
│   ├── bloxlink_service.py         # API Bloxlink
│   ├── company_mapping_service.py  # Mapeamento rank → company
│   └── ...
│
├── repositories/          # Acesso a dados (MySQL)
│   ├── user_repository.py
│   └── ...
│
├── events/                # Event handlers
│   ├── role_sync_handler.py        # Sincronização automática de roles
│   ├── bloxlink_command_detector.py # Detecta /verify e /update
│   └── ...
│
├── utils/                 # Utilitários
│   ├── config.py          # Carregamento de variáveis de ambiente
│   ├── database.py        # Pool de conexões MySQL
│   ├── roadmap_parser.py  # Parser de roadmap (com tradução PT→EN)
│   └── ...
│
└── docs/                  # Documentação completa (PT-BR)
    ├── 02_ARQUITETURA/
    ├── 03_DESENVOLVIMENTO/
    ├── 05_OPERACAO/
    └── ...
```

---

## 🔑 VARIÁVEIS DE AMBIENTE ESSENCIAIS

### Obrigatórias

```env
# Discord
DISCORD_TOKEN=seu_token_discord
DISCORD_CLIENT_ID=seu_client_id
DISCORD_GUILD_ID=id_do_servidor

# Database (MySQL)
DB_HOST=host_do_mysql
DB_USER=usuario_mysql
DB_PASSWORD=senha_mysql
DB_NAME=ignis
DB_PORT=3306  # Opcional, padrão 3306

# Roblox Integration (Opcional)
ROBLOX_COOKIE=seu_cookie_roblox
```

### Opcionais (mas recomendadas)

```env
# Database Pool
DB_POOL_MIN=2
DB_POOL_MAX=10

# Canais Discord
STAFF_CMDS_CHANNEL_ID=id_canal_comandos
ROADMAP_CHANNEL_ID=id_canal_roadmap

# Bloxlink
BLOXLINK_API_KEY=chave_api_bloxlink
```

**⚠️ IMPORTANTE:** Use `env.example` como template. NUNCA faça commit do arquivo `.env`!

---

## 🚀 COMANDOS IMPORTANTES

### Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Executar bot
python ignis_main.py

# Testes
pytest
```

### Docker (Railway)

```bash
# Build local (teste)
docker build -t ignisbot .

# Run local (teste)
docker run --env-file .env ignisbot
```

### Git

```bash
# Status
git status

# Commit
git add .
git commit -m "Descrição das mudanças"
git push origin main
```

---

## 📊 FUNCIONALIDADES PRINCIPAIS

### 1. Induction Process Button
- **Arquivo:** `cogs/process.py`
- **Funcionalidade:** Botão que aceita usuários no grupo Roblox principal (ID: 6340169) e altera rank no grupo secundário (ID: 6496437)
- **Grupos Roblox:**
  - `6340169`: Aceita pedido (sem alterar rank)
  - `6496437`: Altera rank de 238 para 240
  - `36088185`: Adicionado à lista de verificação

### 2. Roadmap Automático
- **Arquivo:** `cogs/roadmap.py` + `utils/roadmap_parser.py`
- **Funcionalidade:** Posta automaticamente atualizações do roadmap no Discord
- **Características:**
  - Extrai dados de `docs/02_ARQUITETURA/ROADMAP_MELHORIAS.md` e `CHANGELOG.md`
  - Traduz automaticamente PT→EN antes de postar
  - Posta apenas 1 mensagem no startup (evita duplicatas)
  - Usa lock assíncrono para prevenir postagens concorrentes

### 3. Health Check System
- **Arquivo:** `cogs/health.py` + `utils/health_check.py`
- **Comando:** `/health`
- **Informações:**
  - Uso de memória (RAM) em MB e GB
  - Uso de CPU em porcentagem
  - Uso de GPU (se disponível via pynvml)
  - Uso de disco em GB
  - Status detalhado do banco de dados

### 4. Sincronização Automática de Roles
- **Arquivo:** `events/role_sync_handler.py`
- **Funcionalidade:** Detecta mudanças de roles no Discord (quando Bloxlink executa `/update`) e atualiza automaticamente:
  - Rank no banco de dados
  - Nickname com prefixo da company (ex: "6. Legionary Username")

### 5. Event Panel (Salamanders)
- **Arquivo:** `cogs/event_buttons.py`
- **Funcionalidade:** Painel interativo para criação de eventos
- **Tipos:** Patrol, Combat Training, Basic Training, Raids, Rally, Custom

---

## 🔧 CONFIGURAÇÕES IMPORTANTES

### IDs de Canais Discord

```python
# Canais principais
ROADMAP_CHANNEL_ID = 1375941285839638536
STAFF_CMDS_CHANNEL_ID = 1375941286267326530
TERMINAL_CHANNEL_ID = 1375941286267326532  # Para /update

# Roles
SALAMANDERS_ROLE_ID = 1376831480931815424
```

### IDs de Grupos Roblox

```python
# Grupo principal (aceita pedidos)
AOW_MAIN_GROUP_ID = 6340169

# Grupo secundário (altera ranks)
AOW_RANK_GROUP_ID = 6496437

# Grupo adicional
AOW_GROUP_3_ID = 36088185
```

### Mapeamento Rank → Company

O mapeamento está em `services/company_mapping_service.py`:
- Ranks específicos têm prefixos fixos (ex: "IA.", "IG.", "6.", "A.")
- Outros ranks usam número da company do banco de dados

---

## 🐳 DEPLOYMENT NO RAILWAY

### Configuração Railway

1. **Variáveis de Ambiente:**
   - Copiar todas as variáveis do `.env` para Railway
   - **IMPORTANTE:** `DB_HOST` deve ser o host PÚBLICO do MySQL (não `mysql.railway.internal`)
   - Exemplo: `DB_HOST=turntable.proxy.rlwy.net` e `DB_PORT=27262`

2. **Dockerfile:**
   - Multi-stage build otimizado
   - Copia arquivos de documentação necessários para roadmap parser
   - Usa usuário não-root (`ignisbot`)

3. **Healthcheck:**
   - Desabilitado no `railway.json` (bot não é servidor HTTP)

### Comandos Railway

```bash
# Ver logs
railway logs

# Ver variáveis
railway variables

# Deploy manual
railway up
```

---

## 📝 NOTAS DE DESENVOLVIMENTO

### Tradução Automática

O sistema de roadmap traduz automaticamente PT→EN:
- **Arquivo:** `utils/roadmap_parser.py` → função `translate_to_english()`
- **Aplicado em:** Título, descrição, features, fixes, upcoming
- **Método:** Dicionário de traduções + substituição de palavras

### Prevenção de Duplicatas

O roadmap usa múltiplas estratégias para evitar postagens duplicadas:
1. Lock assíncrono (`asyncio.Lock`)
2. Flags de controle (`startup_posted`, `bot.roadmap_startup_posted`)
3. Verificação de mensagens existentes no canal
4. Hash de conteúdo para detectar mudanças

### Arquitetura

- **Layered Architecture:** Separação clara entre apresentação (cogs), lógica (services), e dados (repositories)
- **Event-Driven:** Handlers automáticos para eventos do Discord
- **Type Safety:** Uso de Protocols para type hints
- **Dependency Injection:** Manual, mas funcional

---

## 🐛 TROUBLESHOOTING COMUM

### Erro: "ModuleNotFoundError: No module named 'utils.config'"
- **Solução:** Verificar `PYTHONPATH` no Dockerfile
- **Fix aplicado:** `ENV PYTHONPATH=/app:$PYTHONPATH` e `sys.path.insert(0, '/app')` no `ignis_main.py`

### Erro: "Can't connect to MySQL server"
- **Solução Railway:** Usar host PÚBLICO do MySQL, não interno
- **Verificar:** `DB_HOST` e `DB_PORT` corretos

### Erro: "'cryptography' package is required"
- **Solução:** Adicionar `cryptography>=41.0.0` ao `requirements.txt`
- **Motivo:** MySQL usa `caching_sha2_password` authentication

### Roadmap não posta / posta múltiplas vezes
- **Solução:** Verificar flags `startup_posted` e lock assíncrono
- **Logs:** Verificar logs com `[ROADMAP]` prefix

---

## 📚 DOCUMENTAÇÃO IMPORTANTE

### Documentação Principal

- **Arquitetura:** `docs/02_ARQUITETURA/`
- **Desenvolvimento:** `docs/03_DESENVOLVIMENTO/`
- **Operação:** `docs/05_OPERACAO/`
- **Roadmap:** `docs/02_ARQUITETURA/ROADMAP_MELHORIAS.md`
- **Changelog:** `CHANGELOG.md` (em inglês)

### Guias de Deployment

- **Railway:** `docs/05_OPERACAO/HOSPEDAGEM_NUVEM.md`
- **MySQL Config:** `docs/05_OPERACAO/CONFIGURAR_HOST_MYSQL_RAILWAY.md`
- **Troubleshooting:** `docs/05_OPERACAO/RESOLVER_ERRO_CONEXAO_BANCO.md`

---

## 🔄 ESTADO ATUAL DO PROJETO

### ✅ Implementado e Funcionando

- [x] Bot operacional 24/7 no Railway
- [x] Induction Process Button
- [x] Roadmap automático com tradução PT→EN
- [x] Health check com monitoramento de recursos
- [x] Sincronização automática de roles
- [x] Event Panel (Salamanders)
- [x] Integração Bloxlink + Roblox Groups API
- [x] Sistema de pontos e gamificação
- [x] Conformidade LGPD

### 🚧 Em Desenvolvimento / Planejado

- [ ] Health Check System Avançado (métricas de performance)
- [ ] Melhorias no sistema de logging
- [ ] Dashboard de monitoramento

---

## 💡 DICAS PARA NOVO WORKSPACE

1. **Clonar repositório:**
   ```bash
   git clone https://github.com/Japa1413/IgnisBot.git
   cd IgnisBot
   ```

2. **Configurar ambiente:**
   ```bash
   cp env.example .env
   # Editar .env com suas credenciais
   ```

3. **Instalar dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar banco de dados:**
   ```bash
   mysql -u root -p < Ignis.sql
   ```

5. **Executar bot:**
   ```bash
   python ignis_main.py
   ```

6. **Para Railway:**
   - Conectar repositório GitHub ao Railway
   - Configurar variáveis de ambiente
   - Deploy automático via GitHub push

---

## 📞 INFORMAÇÕES DE CONTATO

- **Repositório:** https://github.com/Japa1413/IgnisBot
- **Status:** Operacional 24/7 no Railway
- **Última Atualização:** 2025-01-11

---

## 🎯 PRÓXIMOS PASSOS SUGERIDOS

1. Monitorar logs por 24-48h para validar estabilidade
2. Implementar Health Check System Avançado
3. Melhorar sistema de logging com contexto estruturado
4. Criar dashboard de monitoramento

---

**Pela vontade do Imperador e pela glória do Omnissiah!** ⚙️🔥

---

*Este arquivo deve ser atualizado sempre que houver mudanças significativas no projeto.*

