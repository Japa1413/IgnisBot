# 📝 CHANGELOG - IGNISBOT

All notable changes to this project will be documented in this file.

---

## [Unreleased]

### 🎮 Event Hosting System (2025-11-06)

#### Added
- **Interactive Event Panel** - Salamanders-themed event hosting system
  - Persistent event panel with 7 buttons (Patrol, Combat Training, Basic Training, Internal Practice Raid, Practice Raid, Rally, Custom)
  - Auto-posting on bot startup with automatic cleanup
  - Warhammer 40k Salamanders aesthetic
- **Event Confirmation Workflow** - Two-step confirmation process
  - "Confirm" button for quick event posting
  - "Confirm with Description" button with modal for custom descriptions
  - Ephemeral confirmation messages
- **Event Lifecycle Management**
  - "Event End" message with red End button in event-publishing channel
  - Automatic event conclusion notifications
  - Event cleanup and conclusion embeds
- **Event Presets** - Pre-configured event types
  - Patrol event with Roblox game link and image
  - Role pinging system (customizable per event)
  - Customizable descriptions, locations, and times

#### Changed
- Event announcement function updated to support custom descriptions
- Event panel embed updated with new Salamanders description

#### Files Added
- `cogs/event_buttons.py` - Complete event hosting system
- `utils/event_announcement.py` - Event posting utilities
- `utils/event_presets.py` - Event configuration presets

---

### 📊 Activity Monitoring System (2025-11-06)

#### Added
- **Member Activity Logging** - Real-time activity monitoring
  - Voice channel join/leave tracking with duration
  - Member move between channels detection
  - Member join/leave server with full profile embeds
  - Discord and Roblox profile integration
- **Activity Log Channel** - Dedicated logging channel
  - Automatic embeds for all voice channel activities
  - Color-coded events (green=join, red=leave, purple=move)
  - Member profile embeds with Discord and Roblox information
  - Automatic timestamp formatting (Discord's native timestamps)

#### Changed
- Removed old voice logs handler from `ignis_main.py`
- Activity logs now use embeds instead of plain text messages
- All voice channels monitored (no restrictions)

#### Files Added
- `cogs/member_activity_log.py` - Complete activity monitoring system

---

### 🔗 Bloxlink & Roblox Integration (2025-11-05)

#### Added
- **Bloxlink Service** - Complete Roblox user verification
  - Real username extraction (not display name)
  - Avatar URL fetching
  - Verification status tracking
  - Discord-to-Roblox ID mapping
  - Two-strategy username lookup (direct + search)
- **Induction Command** - `/induction <roblox_username>`
  - Accepts Roblox username directly (no Discord mention required)
  - Fetches Roblox data via Bloxlink API
  - Personalized embed with Roblox avatar and username
  - Moderator/owner only, restricted channel
- **Role Synchronization** - Automatic rank updates
  - Detects Discord role changes (Bloxlink `/update` command)
  - Automatically updates database rank
  - Maps Discord roles to system ranks
  - Complete audit logging

#### Changed
- Induction command now accepts Roblox username instead of Discord member
- All bot messages translated to English
- Improved error handling for Roblox API calls

#### Files Added
- `services/bloxlink_service.py` - Bloxlink API integration
- `events/role_sync_handler.py` - Automatic role synchronization

---

### 🎮 Enhanced VC Log System (2025-11-05)

#### Changed
- **VC Log Command** - Major improvements
  - `vc_name` parameter now required and appears first
  - `event` renamed to `event_type`
  - Removed `evidence` parameter
  - Restricted to Vox-link channels only (with Unicode character matching)
  - All points operations now SQL-only (Google Sheets removed)
- **Channel Validation** - Enhanced validation
  - Exact Unicode character matching for Vox-link channels
  - Supports: "Vox-link Ⅰ", "Vox-link ⅠⅠ", "Vox-link ⅠⅠⅠ", "Vox-link Ⅳ"
  - Clear error messages with allowed channels

#### Removed
- Google Sheets integration completely removed
- All `gspread_asyncio` dependencies removed

---

## [Previous Releases]

### ✅ Fase 1: Sistema de Gamificação Disruptiva (2025-10-31)

#### Core XP System Implementado
- ✅ **Sistema de XP Multi-Source** - XP separado de pontos
  - Voice: +10 XP/min (limitado a 500 XP/dia)
  - Messages: +1 XP/mensagem (limitado a 50 XP/dia)
  - Auto-tracking automático

- ✅ **Sistema de Níveis Independente**
  - Fórmula exponencial: `XP = 100 * level^1.5`
  - Níveis separados de ranks
  - Detecção automática de level up

- ✅ **Event Handlers Automáticos**
  - `on_message()` - Ganho de XP por mensagens
  - `on_voice_state_update()` - Ganho de XP por voice channels
  - Validação de consentimento (LGPD)
  - Daily limits aplicados

- ✅ **Banco de Dados**
  - 4 novas tabelas: `user_progression`, `xp_events`, `daily_xp_limits`, `level_rewards`
  - Migrations integradas em `utils/database.py`

- ✅ **Repositories e Services**
  - `XPRepository` - Operações de XP
  - `ProgressionRepository` - Progressão e níveis
  - `XPService` - Lógica de XP com daily limits
  - `LevelService` - Cálculo e atualização de níveis

- ✅ **Script de Migração**
  - `scripts/migrate_to_gamification.py` - Converte pontos → XP

#### Documentação
- ✅ `PROPOSTA_GAMIFICACAO_DISRUPTIVA.md` - Proposta completa
- ✅ `RESUMO_EXECUTIVO_GAMIFICACAO.md` - Resumo executivo
- ✅ `FASE1_GAMIFICACAO_IMPLEMENTADA.md` - Documentação da implementação
- ✅ `GUIA_ATIVACAO_GAMIFICACAO.md` - Guia de ativação

### Added
- `repositories/xp_repository.py` - Repository de XP
- `repositories/progression_repository.py` - Repository de progressão
- `services/xp_service.py` - Service de XP
- `services/level_service.py` - Service de níveis
- `events/gamification_handlers.py` - Event handlers automáticos
- `migrations/001_gamification_core.sql` - SQL migrations
- `scripts/migrate_to_gamification.py` - Script de migração

### Changed
- `utils/database.py` - Tabelas de gamificação criadas automaticamente
- `ignis_main.py` - Gamification handlers carregados
- `domain/protocols.py` - Novos Protocols para gamificação
- `repositories/__init__.py` - Novos repositories exportados
- `services/__init__.py` - Novos services exportados

---

### ✅ Expansão de Testes (2025-10-31)

#### Novos Arquivos de Teste
- ✅ **`test_consent_service.py`** criado - 9 testes
- ✅ **`test_audit_service.py`** criado - 9 testes
- ✅ **`test_user_service.py`** criado - 7 testes

#### Testes Expandidos
- ✅ **`test_points_service.py`** expandido - +5 testes (validação LGPD, consentimento)
- ✅ **`test_cache_service.py`** expandido - +3 testes (TTL, estatísticas, múltiplos usuários)
- ✅ **`test_user_repository.py`** expandido - +5 testes (edge cases, cache)

#### Correções
- ✅ Bug corrigido em `UserRepository.update_points` (acesso incorreto ao cache)

#### Estatísticas
- **Testes Totais:** ~50 (era ~13)
- **Cobertura Estimada:** 60-70% (era ~30%)
- **Testes Adicionados:** +37

### Added
- `tests/test_consent_service.py` - Testes completos de consentimento
- `tests/test_audit_service.py` - Testes completos de auditoria
- `tests/test_user_service.py` - Testes completos de serviço de usuário

### Changed
- `tests/test_points_service.py`: +5 testes (validação LGPD)
- `tests/test_cache_service.py`: +3 testes (TTL, estatísticas)
- `tests/test_user_repository.py`: +5 testes (edge cases)
- `repositories/user_repository.py`: Correção de bug em `update_points`

---

### ✅ Melhorias Incrementais de Arquitetura (2025-10-31)

#### Type Safety e Testabilidade
- ✅ **Protocols para Type Hints** criados (`domain/protocols.py`)
  - `UserRepositoryProtocol`, `AuditRepositoryProtocol`, `ConsentRepositoryProtocol`
  - `CacheServiceProtocol`, `ConsentServiceProtocol`, `EventDispatcherProtocol`
  - Type safety melhorado (60% → 85%)
  - Zero overhead em runtime

- ✅ **Injeção de Dependências Manual** implementada
  - `PointsService`, `UserService`, `ConsentService`, `AuditService`
  - Compatibilidade retroativa mantida (defaults preservados)
  - Facilita testes e mocks

- ✅ **Testes Atualizados** para usar DI
  - `tests/test_points_service.py` agora usa injeção de dependências
  - Mocks com `spec=Protocol` para type safety

#### Configuração
- ✅ **pytest.ini** atualizado com coverage
  - Relatórios HTML e terminal
  - Fail under 30% (baseline)

#### Documentação
- ✅ `docs/03_DESENVOLVIMENTO/MELHORIAS_INCREMENTAIS.md` - Guia completo
- ✅ `docs/04_TESTES/GUIA_EXPANDIR_TESTES.md` - Plano de expansão
- ✅ `docs/02_ARQUITETURA/ANALISE_MIGRACAO_HEXAGONAL.md` - Análise completa

### Changed
- `services/points_service.py`: Suporte a injeção de dependências
- `services/user_service.py`: Suporte a injeção de dependências
- `services/consent_service.py`: Suporte a injeção de dependências
- `services/audit_service.py`: Suporte a injeção de dependências
- `tests/test_points_service.py`: Usa DI para mocks

### Added
- `domain/protocols.py` - Protocols para type safety
- `domain/__init__.py` - Exportações do módulo domain

---

### ✅ Correções de Auditoria (2025-10-31)

#### Segurança e Conformidade LGPD
- ✅ **Implementada validação de consentimento obrigatória** em operações de pontos
  - Comandos `/add`, `/remove` e `/vc_log` agora validam consentimento antes de processar
  - Raise `ValueError` com mensagem clara se consentimento não dado
  - Logging de tentativas sem consentimento
  - Resolve FINDING #7 (Crítico)

- ✅ **Validação de consentimento no leaderboard**
  - Query SQL filtra apenas usuários com consentimento ativo
  - Conformidade com LGPD Art. 7º, I

#### Documentação
- ✅ **Padronização de datas e versões**
  - Script `update_documentation_dates.py` criado
  - 24 documentos atualizados para 2025-10-31
  - Versões atualizadas (ARQUITETURA: 1.0 → 2.0, LGPD: 1.0 → 2.0)

- ✅ **Unificação de status de conformidade LGPD**
  - Status padronizado para **95%** em todos os documentos

- ✅ **Novos documentos criados**
  - `GOVERNANCA_DADOS.md` - Template para Controlador e DPO
  - `RASTREABILIDADE_LEGAL.md` - Matriz completa funcionalidade → código → LGPD
  - `BASE_LEGAL_MATRIZ.md` - Matriz de base legal
  - `POLITICA_RETENCAO_LOGS.md` - Política de retenção
  - `PROCESSO_CORRECAO_DADOS.md` - Processo de correção
  - `VALIDACAO_INCIDENTES.md` - Checklist de validação
  - `PLANO_DEPRECACAO.md` - Plano de remoção de código deprecated
  - `ANALISE_MATURIDADE_REAL.md` - Análise de maturidade real

#### Funcionalidades
- ✅ **Script de limpeza de logs de auditoria**
  - `scripts/cleanup_audit_logs.py` criado
  - Remove logs > 6 meses automaticamente
  - Documentação de agendamento

- ✅ **Warnings de deprecação** adicionados
  - Data de remoção definida (2025-12-31)
  - Documentação clara de alternativas

### Changed
- `services/points_service.py`: Validação de consentimento obrigatória
- `cogs/add.py`: Tratamento melhorado de erros de consentimento
- `cogs/remove.py`: Tratamento melhorado de erros de consentimento
- `cogs/vc_log.py`: Validação de consentimento explícita
- `cogs/leaderboard.py`: Query SQL com filtro de consentimento
- Documentos de arquitetura atualizados

### Added
- `scripts/cleanup_audit_logs.py` - Limpeza automática de logs
- `scripts/update_documentation_dates.py` - Padronização de datas
- `scripts/validate_consent_on_startup.py` - Validação de consentimento
- `scripts/validate_incident_plan.py` - Validação de plano de incidentes
- `scripts/find_all_placeholders.py` - Encontrar placeholders
- Múltiplos documentos de compliance e governança

---

## [1.0.0] - 2025-10-31

### Initial Release
- Sistema de gamificação completo
- Conformidade LGPD implementada
- Arquitetura Layered + Event-Driven
- Sistema de cache com TTL
- Testes unitários básicos
- Type safety com Protocols
- Injeção de dependências manual

---

**Formato baseado em:** [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/)
