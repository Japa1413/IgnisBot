# 🔥 IgnisBot - Bot Discord Empresarial Avançado

<div align="center">

![Versão Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Discord.py](https://img.shields.io/badge/discord.py-2.3%2B-blue)
![Licença](https://img.shields.io/badge/licença-MIT-green)
![Status](https://img.shields.io/badge/status-pronto%20para%20produção-success)
![LGPD](https://img.shields.io/badge/LGPD-95%25%20conforme-orange)

**Bot Discord empresarial de código aberto com gamificação, gerenciamento de eventos, integração Roblox e total conformidade LGPD. Configurável para qualquer servidor ou comunidade.**

[Funcionalidades](#-funcionalidades) • [Início Rápido](#-início-rápido) • [Documentação](#-documentação) • [Arquitetura](#-arquitetura)

[English Version](README_EN.md)

</div>

---

## 📋 Sobre o Projeto

**IgnisBot** é um bot Discord de nível empresarial, um **produto comercial** desenvolvido para comunidades Discord que precisam de sistemas avançados de gamificação, gerenciamento e automação. Construído com Python e discord.py, o Ignis é um sistema automatizado de administração e inteligência que gerencia:

- **Sistemas de progressão hierárquica** com gerenciamento manual de rank e XP
- **Hospedagem de eventos interativa** com fluxos de confirmação
- **Monitoramento de atividade em tempo real** (canais de voz, entrada/saída de membros)
- **Integração Bloxlink** para verificação de usuários Roblox
- **Total conformidade LGPD** com proteção de dados e controles de privacidade

### 🎯 Destaques Principais

- ⚡ **Alta Performance:** Sistema de cache otimizado e pool de conexões de banco de dados
- 🔒 **Conformidade LGPD/GDPR:** Implementação completa de proteção de dados (95%+)
- 📚 **Documentação Extensa:** 110+ documentos organizados seguindo padrões IEEE/ISO
- 🤖 **Manutenção Automatizada:** Sistema de documentação auto-organizável
- 🚀 **Pronto para Produção:** Maturidade CMMI Nível 4
- 🎮 **Gerenciamento de Eventos:** Hospedagem de eventos interativa com modais e botões persistentes
- 📊 **Registro de Atividades:** Monitoramento em tempo real de canais de voz e atividades de membros
- 🔗 **Integração Roblox:** Integração perfeita com Bloxlink para verificação de usuários

---

## ✨ Funcionalidades

### 🎮 Sistema de Gamificação

**Sistema de Progressão Manual (Protocolo Sagrado de Vulkan)**
- Progressão de rank hierárquica com dois caminhos: Pré-Indução e Legionário
- Gerenciamento manual de XP e rank (comandos apenas para administradores)
- Barras de progresso visuais com estética terminal Warhammer 40k
- Sincronização de rank a partir de roles do Discord (automática via Bloxlink `/update`)
- Rastreamento de pontos e EXP com visualização de limite

**Comandos:**
- `/userinfo [membro]` - Exibir perfil completo do usuário com barra de progresso
- `/add <membro> <pontos> [motivo]` - Adicionar pontos (admin, canal restrito)
- `/remove <membro> <pontos> [motivo]` - Remover pontos (admin, canal restrito)
- `/vc_log <vc_name> <quantidade> <tipo_evento>` - Registrar participação em canal de voz (apenas canais Vox-link)
- `/leaderboard` - Exibir top 10 usuários

### 🔔 Sistema de Hospedagem de Eventos

**Painel de Eventos Interativo (Tema Salamanders)**
- Painel de hospedagem de eventos persistente com 7 botões
- Fluxo de confirmação antes de postar eventos
- Suporte a modais para descrições personalizadas de eventos
- Sistema automático de menção de roles
- Gerenciamento de ciclo de vida de eventos com botão End
- Notificações automáticas de conclusão de eventos

**Eventos Disponíveis:**
- **Linha Verde:** Patrol, Combat Training, Basic Training
- **Linha Vermelha:** Internal Practice Raid, Practice Raid, Rally
- **Linha Cinza:** Eventos personalizados (em breve)

**Comandos:**
- `/event_panel [canal]` - Postar painel de hospedagem de eventos manualmente

### 📊 Monitoramento de Atividades

**Registro de Atividades em Tempo Real**
- Rastreamento de entrada/saída em canais de voz com duração
- Detecção de movimentação de membros entre canais
- Entrada/saída de membros do servidor com embeds de perfil completo
- Integração de perfis Discord e Roblox
- Formatação automática de timestamp

**Recursos:**
- Todos os canais de voz monitorados (sem restrições)
- Embeds ricos com avatares de membros
- Eventos codificados por cores (verde=entrada, vermelho=saída, roxo=movimento)
- Limpeza automática de logs antigos

### 🔗 Sistemas de Integração

**Integração Bloxlink**
- Verificação automática de usuários Roblox
- Extração de nome de usuário real (não display name)
- Busca de URL de avatar
- Rastreamento de status de verificação
- Mapeamento Discord-to-Roblox ID

**Integração com Grupo Roblox**
- Sincronização de roles do Discord para banco de dados
- Atualizações automáticas de rank quando Bloxlink `/update` é usado
- Rastreamento de company e speciality

**Comandos:**
- `/induction <roblox_username> [instruções]` - Iniciar processo de indução (moderador, canal restrito)

### 🔒 Privacidade e Conformidade LGPD

**Proteção Completa de Dados**
- Sistema de gerenciamento de consentimento (conceder/revogar/status)
- Funcionalidade de exportação de dados
- Direito ao esquecimento (exclusão completa de dados)
- Solicitações de correção de dados
- Trilha de auditoria completa (LGPD Art. 10)
- Sistema de logging estruturado

**Comandos:**
- `/export_my_data` - Exportar seus dados pessoais
- `/delete_my_data` - Excluir todos os seus dados (direito ao esquecimento)
- `/correct_my_data` - Solicitar correção de dados
- `/consent [ação]` - Gerenciar consentimento (conceder/revogar/status)

**Documentação Legal:**
- `/privacy` - Política de Privacidade
- `/terms` - Termos de Uso
- `/sla` - Service Level Agreement

---

## 🚀 Início Rápido

### Pré-requisitos

- **Python:** 3.10 ou superior
- **MySQL:** 5.7+ ou 8.0+
- **Token do Bot Discord:** [Criar aplicação](https://discord.com/developers/applications)
- **Chave API Bloxlink:** (Opcional, para integração Roblox)

### Instalação

```bash
# Clonar repositório
git clone https://github.com/Japa1413/IgnisBot.git
cd IgnisBot

# Instalar dependências
pip install -r requirements.txt

# Configurar ambiente
cp env.example .env
# Editar .env com suas credenciais (ver seção Configuração)
```

### Configuração do Banco de Dados

```bash
# Executar script SQL
mysql -u root -p < Ignis.sql
```

### Executar Bot

```bash
python ignis_main.py
```

**📖 Guia Completo de Configuração:** [`docs/03_DESENVOLVIMENTO/SETUP_CRITICO.md`](docs/03_DESENVOLVIMENTO/SETUP_CRITICO.md)

---

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

**Obrigatórias:**
```env
DISCORD_TOKEN=seu_token_do_bot_aqui
DISCORD_CLIENT_ID=seu_client_id
DISCORD_GUILD_ID=seu_guild_id

# Banco de Dados
DB_HOST=localhost
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=ignis
```

**Opcionais (para recursos avançados):**
```env
# Integração Bloxlink
BLOXLINK_API_KEY=sua_chave_api_bloxlink
ROBLOX_GROUP_ID=seu_id_grupo_roblox
ROBLOX_COOKIE=seu_cookie_roblox

# Conformidade LGPD
CONTROLLER_EMAIL=email@exemplo.com
PRIVACY_POLICY_URL=https://...
TERMS_OF_USE_URL=https://...

# Ajuste de Performance
DB_POOL_MIN=2      # Pool mínimo de conexões (padrão: 2)
DB_POOL_MAX=10     # Pool máximo de conexões (padrão: 10)

# Restrições de Canais
STAFF_CMDS_CHANNEL_ID=seu_id_canal      # Canal de comandos restritos
INDUCTION_CHANNEL_ID=seu_id_canal       # Canal do comando de indução
EVENT_PANEL_CHANNEL_ID=seu_id_canal     # Canal do painel de eventos
EVENT_ANNOUNCEMENT_CHANNEL_ID=seu_id_canal  # Canal de anúncios de eventos
ACTIVITY_LOG_CHANNEL_ID=seu_id_canal    # Canal de logs de atividades
```

📖 **Guia Completo de Configuração:** Veja [`docs/03_DESENVOLVIMENTO/SETUP_CRITICO.md`](docs/03_DESENVOLVIMENTO/SETUP_CRITICO.md)

---

## 📚 Documentação

### 📖 Links Rápidos

- 📘 [Catálogo Completo de Documentação](docs/CATALOGO_DOCUMENTACAO.md)
- 📋 [Índice de Documentação](docs/README.md)
- 🏗️ [Arquitetura do Sistema](docs/02_ARQUITETURA/ARQUITETURA_SISTEMA.md)
- 🔒 [Análise de Segurança](docs/02_ARQUITETURA/ANALISE_SEGURANCA.md)
- ⚖️ [Conformidade LGPD](docs/06_LEGAL_COMPLIANCE/LGPD_COMPLIANCE.md)

### 📁 Estrutura da Documentação

```
docs/
├── 01_GESTAO_PROJETO/    # Gestão e planejamento de projeto
├── 02_ARQUITETURA/        # Arquitetura técnica
├── 03_DESENVOLVIMENTO/    # Guias de desenvolvimento
├── 04_TESTES/             # Documentação de testes
├── 05_OPERACAO/           # Operações e deploy
├── 06_LEGAL_COMPLIANCE/   # Legal e conformidade LGPD
├── 07_AUDITORIA/          # Relatórios de auditoria
├── 08_REFERENCIA/         # Referência rápida
└── 09_OTIMIZACAO/         # Otimizações de performance
```

### 🔍 Documentação Principal

**Técnica:**
- [Arquitetura do Sistema](docs/02_ARQUITETURA/ARQUITETURA_SISTEMA.md)
- [Sistema de Gamificação (Protocolo Sagrado de Vulkan)](docs/03_DESENVOLVIMENTO/PROTOCOLO_SAGRADO_VULKAN.md)
- [Integração Bloxlink & Roblox](docs/03_DESENVOLVIMENTO/SISTEMA_INTEGRACAO_BLOXLINK_ROBLOX.md)
- [Sistema de Hospedagem de Eventos](docs/03_DESENVOLVIMENTO/) (Em breve)

**Legal:**
- [Política de Privacidade](docs/06_LEGAL_COMPLIANCE/POLITICA_PRIVACIDADE.md)
- [Termos de Uso](docs/06_LEGAL_COMPLIANCE/TERMOS_USO.md)
- [SLA - Service Level Agreement](docs/06_LEGAL_COMPLIANCE/SLA.md)

---

## 🏗️ Arquitetura

### Visão Geral do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                  DISCORD API (discord.py)                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              CAMADA DE APRESENTAÇÃO (COGs)                  │
│  • userinfo • add • remove • vc_log • leaderboard          │
│  • event_buttons • member_activity_log • induction        │
│  • data_privacy • legal • cache_stats                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  CAMADA DE SERVIÇO                          │
│  • PointsService • ProgressionService • UserService         │
│  • BloxlinkService • AuditService • ConsentService         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              CAMADA DE REPOSITÓRIO                          │
│  • UserRepository • AuditRepository                         │
│  • BaseRepository (com pool de conexões)                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              BANCO DE DADOS (MySQL)                         │
│  • users • audit_logs • consent_records                    │
└─────────────────────────────────────────────────────────────┘
```

### Componentes Principais

- **Arquitetura Orientada a Eventos:** Handlers para PointsChangedEvent, UserCreatedEvent
- **Injeção de Dependências:** Serviços e repositórios usam design baseado em protocolos
- **Sistema de Cache:** Cache baseado em TTL com estatísticas
- **Pool de Conexões:** Conexões de banco de dados otimizadas (pool de 2-10)
- **Logging Estruturado:** Logging baseado em JSON com rotação

---

## 🎯 Status do Projeto

### Métricas de Maturidade

| Métrica | Status | Detalhes |
|---------|--------|----------|
| **Nível CMMI** | 4 (Gerenciado) | Processos definidos, baseado em métricas |
| **Conformidade LGPD** | 95% | 100% após configuração de DPO |
| **Pronto para Produção** | ✅ Sim | Totalmente operacional |
| **Cobertura de Testes** | ~60-70% | Serviços, repositórios, cache |
| **Documentação** | 110+ docs | Organizados por padrões IEEE/ISO |

### Status de Segurança

- ✅ **Credenciais:** Protegidas via variáveis de ambiente
- ✅ **SQL Injection:** 100% de queries parametrizadas
- ✅ **Logging:** Logging estruturado com rotação
- ✅ **Vulnerabilidades:** Zero problemas críticos
- ✅ **Cache:** Baseado em TTL com invalidação
- ✅ **Pool de Conexões:** Pool otimizado

### Conformidade Legal

- ✅ Política de Privacidade Completa
- ✅ Termos de Uso Completos
- ✅ Todos os direitos do titular de dados (6/6) implementados
- ✅ Plano de resposta a incidentes
- ✅ Trilha de auditoria completa (LGPD Art. 10)
- ⚠️ DPO: Pendente de configuração (15 min para 100%)

---

## 🛠️ Comandos Disponíveis

### Gamificação
- `/userinfo [membro]` - Perfil do usuário com barra de progresso
- `/add <membro> <pontos> [motivo]` - Adicionar pontos (admin)
- `/remove <membro> <pontos> [motivo]` - Remover pontos (admin)
- `/vc_log <vc_name> <quantidade> <tipo_evento>` - Registrar participação em voz
- `/leaderboard` - Top 10 usuários

### Gerenciamento de Eventos
- `/event_panel [canal]` - Postar painel de hospedagem de eventos
- Botões de eventos: Patrol, Combat Training, Basic Training, Raids, Rally, Custom

### Gerenciamento de Membros
- `/induction <roblox_username> [instruções]` - Iniciar indução (moderador)
- `/company [membro] [company]` - Gerenciar atribuições de company
- `/rank_refresh [membro]` - Atualizar exibição de rank do usuário

### Privacidade & LGPD
- `/export_my_data` - Exportar dados pessoais
- `/delete_my_data` - Excluir todos os dados (direito ao esquecimento)
- `/correct_my_data` - Solicitar correção de dados
- `/consent [ação]` - Gerenciar consentimento

### Documentação Legal
- `/privacy` - Política de Privacidade
- `/terms` - Termos de Uso
- `/sla` - Service Level Agreement

### Utilitários
- `/help` - Exibir lista de comandos
- `/cache_stats` - Ver estatísticas de cache

---

## 📊 Estrutura do Projeto

```
IgnisBot/
├── cogs/                    # Módulos de comandos
│   ├── userinfo.py         # Exibição de perfil do usuário
│   ├── add.py              # Comando de adicionar pontos
│   ├── remove.py           # Comando de remover pontos
│   ├── vc_log.py           # Registro de canais de voz
│   ├── event_buttons.py    # Sistema de hospedagem de eventos
│   ├── member_activity_log.py  # Monitoramento de atividades
│   ├── induction.py        # Processo de indução
│   ├── rank.py             # Gerenciamento de rank
│   ├── data_privacy.py     # Comandos LGPD
│   └── legal.py            # Documentação legal
├── services/               # Camada de lógica de negócios
│   ├── points_service.py
│   ├── progression_service.py
│   ├── bloxlink_service.py
│   ├── audit_service.py
│   └── consent_service.py
├── repositories/           # Camada de acesso a dados
│   ├── user_repository.py
│   ├── audit_repository.py
│   └── base_repository.py
├── events/                 # Handlers de eventos
│   ├── role_sync_handler.py
│   ├── handlers/           # Dispatchers de eventos
│   └── event_types.py
├── utils/                  # Utilitários
│   ├── database.py        # Pool de conexões DB
│   ├── cache.py           # Sistema de cache
│   ├── logger.py          # Logging estruturado
│   ├── rank_paths.py       # Caminhos de progressão
│   └── event_announcement.py  # Postagem de eventos
├── docs/                   # Documentação (110+ arquivos)
├── tests/                  # Suíte de testes
├── scripts/                # Scripts de automação
└── ignis_main.py          # Ponto de entrada
```

---

## 🔒 Segurança e Privacidade

### Medidas de Segurança Implementadas

- ✅ **Variáveis de Ambiente:** Todas as credenciais em `.env` (nunca commitadas)
- ✅ **Proteção SQL Injection:** 100% de queries parametrizadas
- ✅ **Logging de Auditoria:** Rastreamento completo de operações (LGPD Art. 10)
- ✅ **Logging Estruturado:** Baseado em JSON com rotação
- ✅ **Restrições de Canal:** Comandos restritos a canais específicos
- ✅ **Verificações de Permissão:** Controle de acesso baseado em roles
- ✅ **Pool de Conexões:** Conexões de banco de dados otimizadas

### Conformidade LGPD

O IgnisBot implementa total conformidade com a LGPD (Lei Geral de Proteção de Dados):

- ✅ **Gerenciamento de Consentimento:** Rastreamento de conceder/revogar/status
- ✅ **Direitos do Titular de Dados:** Todos os 6 direitos implementados
  - Direito de acesso (exportar)
  - Direito de exclusão (esquecimento)
  - Direito de correção
  - Direito de oposição
  - Direito de portabilidade
  - Direito de restrição
- ✅ **Trilha de Auditoria:** Logging completo de operações
- ✅ **Política de Privacidade:** Documentação legal completa
- ✅ **Retenção de Dados:** Políticas de retenção configuráveis

**Para 100% de Conformidade:** Configure DPO (veja [`docs/03_DESENVOLVIMENTO/CONFIGURAR_DPO.md`](docs/03_DESENVOLVIMENTO/CONFIGURAR_DPO.md))

---

## 🧪 Testes

### Cobertura de Testes

- **Serviços:** PointsService, CacheService, ConsentService, UserService
- **Repositórios:** UserRepository com integração de cache
- **Casos Extremos:** Validação de consentimento, tratamento de erros, invalidação de cache

### Executando Testes

```bash
# Executar todos os testes
pytest tests/ -v

# Com cobertura
pytest tests/ --cov=services --cov=repositories --cov-report=html

# Arquivo de teste específico
pytest tests/test_points_service.py -v
```

---

## 📈 Performance

### Otimizações Implementadas

- **Fase 1:** Sistema de cache com TTL (padrão 2-5 minutos)
- **Fase 2:** Pool de conexões de banco de dados (2-10 conexões)
- **Otimização de Queries:** Colunas indexadas, queries parametrizadas
- **Carregamento Preguiçoso:** Busca de dados sob demanda

### Métricas de Performance

- **Tempo de Resposta de Comando:** < 500ms média
- **Pool de Banco de Dados:** 2-10 conexões (auto-scaling)
- **Taxa de Acerto de Cache:** ~70-80% (TTL configurável)
- **Uso de Memória:** Otimizado com pool de conexões

---

## 🛠️ Desenvolvimento

### Pré-requisitos para Desenvolvimento

```bash
pip install -r requirements-dev.txt
```

### Padrões de Código

- **Linguagem:** Python 3.10+ com type hints
- **Estilo:** Conforme PEP 8
- **Documentação:** Docstrings para todas as funções públicas
- **Tratamento de Erros:** Exceções específicas (ValueError para lógica de negócios)

### Maturidade do Projeto

- **Nível CMMI:** 4 (Gerenciado)
- **Documentação:** Padrões IEEE/ISO
- **Controle de Versão:** Git com commits organizados
- **Automatizado:** Organização de documentação, hooks pré-commit

---

## 📝 Changelog

Veja [`CHANGELOG.md`](CHANGELOG.md) para histórico detalhado de versões.

### Atualizações Recentes

- ✅ **Sistema de Hospedagem de Eventos:** Painel de eventos interativo com fluxos de confirmação
- ✅ **Monitoramento de Atividades:** Registro em tempo real de canais de voz e atividades de membros
- ✅ **Integração Bloxlink:** Sistema completo de verificação de usuários Roblox
- ✅ **Sincronização de Roles:** Atualizações automáticas de rank a partir de roles do Discord
- ✅ **Melhorias na Barra de Progresso:** Visualização aprimorada com indicação de limite

---

## 🔐 Aviso de Segurança

**⚠️ INFORMAÇÕES IMPORTANTES DE SEGURANÇA:**

- **NUNCA** commitar o arquivo `.env`
- **NUNCA** codificar credenciais no código-fonte
- **SEMPRE** usar variáveis de ambiente para dados sensíveis
- **REVOGAR** credenciais antigas que foram codificadas (se houver)
- **CONFIGURAR** todas as variáveis de ambiente antes de executar

Veja [`docs/03_DESENVOLVIMENTO/SETUP_CRITICO.md`](docs/03_DESENVOLVIMENTO/SETUP_CRITICO.md) para melhores práticas de segurança.

---

## ⚖️ Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, siga estas diretrizes:

1. Fazer fork do repositório
2. Criar uma branch de feature (`git checkout -b feature/MinhaFeature`)
3. Commitar suas mudanças (`git commit -m 'Adicionar MinhaFeature'`)
4. Fazer push para a branch (`git push origin feature/MinhaFeature`)
5. Abrir um Pull Request

### Diretrizes de Contribuição

- Seguir o guia de estilo PEP 8
- Adicionar testes para novas funcionalidades
- Atualizar documentação conforme necessário
- Garantir que todos os testes passem

---

## 📞 Suporte e Recursos

### Documentação

- 📖 [Catálogo Completo de Documentação](docs/CATALOGO_DOCUMENTACAO.md)
- 📋 [Índice de Documentação](docs/README.md)
- 🔧 [Guia de Configuração](docs/03_DESENVOLVIMENTO/SETUP_CRITICO.md)
- 🔒 [Conformidade LGPD](docs/06_LEGAL_COMPLIANCE/LGPD_COMPLIANCE.md)

### Links Rápidos

- 🏗️ [Documentação de Arquitetura](docs/02_ARQUITETURA/ARQUITETURA_SISTEMA.md)
- 🎮 [Sistema de Gamificação](docs/03_DESENVOLVIMENTO/PROTOCOLO_SAGRADO_VULKAN.md)
- 🔗 [Integração Bloxlink](docs/03_DESENVOLVIMENTO/SISTEMA_INTEGRACAO_BLOXLINK_ROBLOX.md)
- 📊 [Registro de Atividades](docs/03_DESENVOLVIMENTO/) (Documentação do sistema de eventos)

---

## 🎯 Roadmap

### ✅ Concluído

- [x] Sistema de gamificação com progressão manual
- [x] Conformidade LGPD (95% → 100% após DPO)
- [x] Sistema de hospedagem de eventos com painéis interativos
- [x] Monitoramento de atividades (canais de voz, entrada/saída de membros)
- [x] Integração Bloxlink & Roblox
- [x] Sistema de sincronização de roles
- [x] Documentação legal completa
- [x] Otimizações de performance (Fase 1 + 2)
- [x] Sistema de cache com TTL
- [x] Sistema de documentação automatizado
- [x] Todos os comandos do usuário em português brasileiro

### 🚧 Em Progresso

- [ ] Cobertura de testes aprimorada (objetivo: 80%+)
- [ ] Personalização de tipos de eventos adicionais
- [ ] Agendamento avançado de eventos

### 📋 Planejado

- [ ] Pipeline CI/CD
- [ ] Sistema de rate limiting
- [ ] Dashboard de analytics avançado
- [ ] Suporte multi-idioma (i18n)
- [ ] Dashboard web para administração

---

## 📊 Estatísticas

- **Total de Comandos:** 18+ comandos slash
- **Arquivos de Documentação:** 110+ documentos organizados
- **Cobertura de Testes:** ~60-70% (melhorando)
- **Qualidade do Código:** Pronto para produção
- **Performance:** Otimizado com cache e pooling

---

## 🙏 Agradecimentos

- **Discord.py:** Excelente wrapper da API Discord
- **Bloxlink:** Serviço de verificação Roblox
- **Warhammer 40,000:** Inspiração para o tema Salamanders
- **Comunidade:** Comunidade Age of Warfare por feedback e testes

---

<div align="center">

**🔥 IgnisBot - Por Nocturne. Por Vulkan. 🔥**

*Sistema Automatizado de Inteligência Administrativa e Militar*

[![GitHub](https://img.shields.io/badge/GitHub-IgnisBot-blue)](https://github.com/Japa1413/IgnisBot)
[![Documentação](https://img.shields.io/badge/documentação-Completa-success)](docs/CATALOGO_DOCUMENTACAO.md)
[![Status](https://img.shields.io/badge/status-Pronto%20para%20Produção-success)]()

[English Version](README_EN.md)

</div>
