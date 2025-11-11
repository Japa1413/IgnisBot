# 📝 CHANGELOG - IGNISBOT

All notable changes to this project will be documented in this file.

---

## [Unreleased]

### 🚀 24/7 Deployment and Continuous Operation (2025-01-11)

#### Added
- **Railway Deployment** - Bot now runs 24/7 in the cloud
  - Optimized Dockerfile with multi-stage build
  - Support for custom MySQL port (DB_PORT)
  - Complete environment variables configuration
  - Healthcheck disabled (bot is not an HTTP server)
- **Resource Monitoring System** - Expanded `/health` command
  - Memory (RAM) usage in MB and GB
  - CPU usage in percentage
  - GPU usage (if available via pynvml)
  - Disk usage in GB
  - Detailed database status
- **Deployment Documentation** - Complete guides
  - `docs/05_OPERACAO/HOSPEDAGEM_NUVEM.md` - Complete hosting guide
  - `docs/05_OPERACAO/CONFIGURAR_HOST_MYSQL_RAILWAY.md` - MySQL configuration
  - `docs/05_OPERACAO/RESOLVER_ERRO_CONEXAO_BANCO.md` - Troubleshooting
  - `docs/05_OPERACAO/CORRIGIR_HOST_ERRADO_RAILWAY.md` - Host correction
  - `docs/05_OPERACAO/RESOLVER_VARIAVEIS_TEMPLATE_RAILWAY.md` - Template variables

#### Changed
- `utils/config.py` - Added support for custom `DB_PORT`
- `utils/database.py` - Added `port` parameter to MySQL connection
- `requirements.txt` - Added `cryptography>=41.0.0` for MySQL authentication
- `Dockerfile` - Optimized for production with multi-stage build
- `railway.json` - Railway configuration with healthcheck disabled

#### Fixed
- **ModuleNotFoundError** - Fixed `utils.config` import issue in Docker
- **MySQL Connection Error** - Fixed incorrect host usage (ignisbot.railway.internal → MySQL host)
- **MySQL Authentication** - Added `cryptography` package for `caching_sha2_password`
- **Custom Port** - Added support for non-standard MySQL ports

#### Files Added
- `Dockerfile` - Bot containerization
- `railway.json` - Railway configuration
- `render.yaml` - Render configuration (alternative)
- `docker-compose.yml` - Development compose
- `.dockerignore` - Files ignored in build
- `docs/05_OPERACAO/HOSPEDAGEM_NUVEM.md` - Hosting guide
- `docs/05_OPERACAO/CONFIGURAR_HOST_MYSQL_RAILWAY.md` - MySQL config
- `docs/05_OPERACAO/RESOLVER_ERRO_CONEXAO_BANCO.md` - Troubleshooting
- `docs/05_OPERACAO/CORRIGIR_HOST_ERRADO_RAILWAY.md` - Host correction
- `docs/05_OPERACAO/RESOLVER_VARIAVEIS_TEMPLATE_RAILWAY.md` - Template variables
- `docs/05_OPERACAO/COPIAR_VARIAVEIS_MYSQL_RAILWAY.md` - Visual guide
- `docs/05_OPERACAO/CONECTAR_BANCO_SEM_SERVICE_CONNECTIONS.md` - Alternative connection

#### Files Changed
- `utils/config.py` - Added `DB_PORT`
- `utils/database.py` - Added support for custom port
- `requirements.txt` - Added `cryptography`
- `utils/health_check.py` - Added `check_system_resources()`
- `cogs/health.py` - Expanded to show system resources

---

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

### ✅ Phase 1: Disruptive Gamification System (2025-10-31)

#### Core XP System Implemented
- ✅ **Multi-Source XP System** - XP separate from points
  - Voice: +10 XP/min (limited to 500 XP/day)
  - Messages: +1 XP/message (limited to 50 XP/day)
  - Automatic tracking

- ✅ **Independent Level System**
  - Exponential formula: `XP = 100 * level^1.5`
  - Levels separate from ranks
  - Automatic level up detection

- ✅ **Automatic Event Handlers**
  - `on_message()` - XP gain from messages
  - `on_voice_state_update()` - XP gain from voice channels
  - Consent validation (LGPD)
  - Daily limits applied

- ✅ **Database**
  - 4 new tables: `user_progression`, `xp_events`, `daily_xp_limits`, `level_rewards`
  - Migrations integrated in `utils/database.py`

- ✅ **Repositories and Services**
  - `XPRepository` - XP operations
  - `ProgressionRepository` - Progression and levels
  - `XPService` - XP logic with daily limits
  - `LevelService` - Level calculation and update

- ✅ **Migration Script**
  - `scripts/migrate_to_gamification.py` - Converts points → XP

#### Documentation
- ✅ `PROPOSTA_GAMIFICACAO_DISRUPTIVA.md` - Complete proposal
- ✅ `RESUMO_EXECUTIVO_GAMIFICACAO.md` - Executive summary
- ✅ `FASE1_GAMIFICACAO_IMPLEMENTADA.md` - Implementation documentation
- ✅ `GUIA_ATIVACAO_GAMIFICACAO.md` - Activation guide

### Added
- `repositories/xp_repository.py` - XP repository
- `repositories/progression_repository.py` - Progression repository
- `services/xp_service.py` - XP service
- `services/level_service.py` - Level service
- `events/gamification_handlers.py` - Automatic event handlers
- `migrations/001_gamification_core.sql` - SQL migrations
- `scripts/migrate_to_gamification.py` - Migration script

### Changed
- `utils/database.py` - Gamification tables created automatically
- `ignis_main.py` - Gamification handlers loaded
- `domain/protocols.py` - New Protocols for gamification
- `repositories/__init__.py` - New repositories exported
- `services/__init__.py` - New services exported

---

### ✅ Test Expansion (2025-10-31)

#### New Test Files
- ✅ **`test_consent_service.py`** created - 9 tests
- ✅ **`test_audit_service.py`** created - 9 tests
- ✅ **`test_user_service.py`** created - 7 tests

#### Expanded Tests
- ✅ **`test_points_service.py`** expanded - +5 tests (LGPD validation, consent)
- ✅ **`test_cache_service.py`** expanded - +3 tests (TTL, statistics, multiple users)
- ✅ **`test_user_repository.py`** expanded - +5 tests (edge cases, cache)

#### Fixes
- ✅ Bug fixed in `UserRepository.update_points` (incorrect cache access)

#### Statistics
- **Total Tests:** ~50 (was ~13)
- **Estimated Coverage:** 60-70% (was ~30%)
- **Tests Added:** +37

### Added
- `tests/test_consent_service.py` - Complete consent tests
- `tests/test_audit_service.py` - Complete audit tests
- `tests/test_user_service.py` - Complete user service tests

### Changed
- `tests/test_points_service.py`: +5 tests (LGPD validation)
- `tests/test_cache_service.py`: +3 tests (TTL, statistics)
- `tests/test_user_repository.py`: +5 tests (edge cases)
- `repositories/user_repository.py`: Bug fix in `update_points`

---

### ✅ Incremental Architecture Improvements (2025-10-31)

#### Type Safety and Testability
- ✅ **Protocols for Type Hints** created (`domain/protocols.py`)
  - `UserRepositoryProtocol`, `AuditRepositoryProtocol`, `ConsentRepositoryProtocol`
  - `CacheServiceProtocol`, `ConsentServiceProtocol`, `EventDispatcherProtocol`
  - Improved type safety (60% → 85%)
  - Zero runtime overhead

- ✅ **Manual Dependency Injection** implemented
  - `PointsService`, `UserService`, `ConsentService`, `AuditService`
  - Backward compatibility maintained (defaults preserved)
  - Facilitates testing and mocks

- ✅ **Tests Updated** to use DI
  - `tests/test_points_service.py` now uses dependency injection
  - Mocks with `spec=Protocol` for type safety

#### Configuration
- ✅ **pytest.ini** updated with coverage
  - HTML and terminal reports
  - Fail under 30% (baseline)

#### Documentation
- ✅ `docs/03_DESENVOLVIMENTO/MELHORIAS_INCREMENTAIS.md` - Complete guide
- ✅ `docs/04_TESTES/GUIA_EXPANDIR_TESTES.md` - Expansion plan
- ✅ `docs/02_ARQUITETURA/ANALISE_MIGRACAO_HEXAGONAL.md` - Complete analysis

### Changed
- `services/points_service.py`: Dependency injection support
- `services/user_service.py`: Dependency injection support
- `services/consent_service.py`: Dependency injection support
- `services/audit_service.py`: Dependency injection support
- `tests/test_points_service.py`: Uses DI for mocks

### Added
- `domain/protocols.py` - Protocols for type safety
- `domain/__init__.py` - Domain module exports

---

### ✅ Audit Corrections (2025-10-31)

#### Security and LGPD Compliance
- ✅ **Mandatory consent validation implemented** in points operations
  - Commands `/add`, `/remove` and `/vc_log` now validate consent before processing
  - Raise `ValueError` with clear message if consent not given
  - Logging of attempts without consent
  - Resolves FINDING #7 (Critical)

- ✅ **Consent validation in leaderboard**
  - SQL query filters only users with active consent
  - Compliance with LGPD Art. 7º, I

#### Documentation
- ✅ **Date and version standardization**
  - Script `update_documentation_dates.py` created
  - 24 documents updated to 2025-10-31
  - Versions updated (ARCHITECTURE: 1.0 → 2.0, LGPD: 1.0 → 2.0)

- ✅ **LGPD compliance status unification**
  - Status standardized to **95%** in all documents

- ✅ **New documents created**
  - `GOVERNANCA_DADOS.md` - Template for Controller and DPO
  - `RASTREABILIDADE_LEGAL.md` - Complete functionality → code → LGPD matrix
  - `BASE_LEGAL_MATRIZ.md` - Legal basis matrix
  - `POLITICA_RETENCAO_LOGS.md` - Retention policy
  - `PROCESSO_CORRECAO_DADOS.md` - Data correction process
  - `VALIDACAO_INCIDENTES.md` - Validation checklist
  - `PLANO_DEPRECACAO.md` - Deprecated code removal plan
  - `ANALISE_MATURIDADE_REAL.md` - Real maturity analysis

#### Features
- ✅ **Audit log cleanup script**
  - `scripts/cleanup_audit_logs.py` created
  - Removes logs > 6 months automatically
  - Scheduling documentation

- ✅ **Deprecation warnings** added
  - Removal date defined (2025-12-31)
  - Clear documentation of alternatives

### Changed
- `services/points_service.py`: Mandatory consent validation
- `cogs/add.py`: Improved consent error handling
- `cogs/remove.py`: Improved consent error handling
- `cogs/vc_log.py`: Explicit consent validation
- `cogs/leaderboard.py`: SQL query with consent filter
- Architecture documents updated

### Added
- `scripts/cleanup_audit_logs.py` - Automatic log cleanup
- `scripts/update_documentation_dates.py` - Date standardization
- `scripts/validate_consent_on_startup.py` - Consent validation
- `scripts/validate_incident_plan.py` - Incident plan validation
- `scripts/find_all_placeholders.py` - Find placeholders
- Multiple compliance and governance documents

---

## [1.0.0] - 2025-10-31

### Initial Release
- Complete gamification system
- LGPD compliance implemented
- Layered + Event-Driven architecture
- Cache system with TTL
- Basic unit tests
- Type safety with Protocols
- Manual dependency injection

---

**Format based on:** [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
