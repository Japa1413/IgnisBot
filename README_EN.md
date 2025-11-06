# IgnisBot

<div align="center">

![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Discord.py](https://img.shields.io/badge/discord.py-2.3%2B-5865F2?style=flat-square&logo=discord&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-6DB33F?style=flat-square)
![Status](https://img.shields.io/badge/status-production-2E7D32?style=flat-square)
![LGPD](https://img.shields.io/badge/LGPD-95%25-1565C0?style=flat-square)

**Automation and management platform for Discord communities with enterprise architecture and regulatory compliance.**

[Features](#features) • [Documentation](#documentation) • [Installation](#installation) • [Architecture](#architecture)

[Português](README.md)

</div>

---

## Overview

IgnisBot is an automation platform for Discord developed with layered architecture and enterprise patterns. The system provides progression management, event automation, activity monitoring, and compliance with data protection regulations.

### Key Characteristics

- **Layered Architecture:** Clear separation between presentation, business logic, and data access
- **Regulatory Compliance:** Complete LGPD/GDPR implementation with audit trail
- **High Availability:** Distributed cache system and optimized connection pool
- **Technical Documentation:** 110+ documents organized following IEEE/ISO standards
- **CMMI Maturity:** Level 4 with defined processes and quantitative metrics

---

## Features

### Progression Management

Hierarchical rank system with manual control of points and experience. Supports multiple progression paths and automatic synchronization with Discord roles.

**Main Commands:**
- `/userinfo [member]` - Display user profile with progress metrics
- `/add <member> <points> [reason]` - Add points (requires administrative permissions)
- `/remove <member> <points> [reason]` - Remove points (requires administrative permissions)
- `/vc_log <channel> <amount> <type>` - Log voice channel participation
- `/leaderboard` - Display user rankings

### Event Automation

Event management system with interactive interface, confirmation workflows, and modals for custom configuration. Supports multiple event types and integration with external systems.

**Features:**
- Persistent event panel
- Customizable confirmation workflows
- Integration with notification systems
- Event lifecycle management

### Monitoring and Logging

Real-time monitoring system for member activities, voice channels, and server events. Structured logging with integration to analytics systems.

**Features:**
- Voice channel activity tracking
- Member join/leave monitoring
- Structured JSON logging
- Integration with analytics systems

### Integrations

Support for integration with external platforms for user verification, data synchronization, and process automation.

**Available Integrations:**
- User verification via external APIs
- Role and permission synchronization
- Integration with management systems

### Compliance and Privacy

Complete implementation of privacy controls and regulatory compliance with LGPD/GDPR support.

**Compliance Features:**
- Consent management
- Personal data export
- Right to be forgotten
- Data correction
- Complete audit trail

---

## Installation

### Prerequisites

- Python 3.10 or higher
- MySQL 5.7+ or 8.0+
- Discord application token
- Database credentials

### Initial Setup

```bash
# Clone repository
git clone https://github.com/Japa1413/IgnisBot.git
cd IgnisBot

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp env.example .env
# Edit .env with your credentials
```

### Database Setup

```bash
mysql -u root -p < Ignis.sql
```

### Execution

```bash
python ignis_main.py
```

Complete configuration documentation available at [`docs/03_DESENVOLVIMENTO/SETUP_CRITICO.md`](docs/03_DESENVOLVIMENTO/SETUP_CRITICO.md).

---

## Configuration

### Environment Variables

**Required:**
```env
DISCORD_TOKEN=your_token_here
DISCORD_CLIENT_ID=your_client_id
DISCORD_GUILD_ID=your_guild_id
DB_HOST=localhost
DB_USER=username
DB_PASSWORD=password
DB_NAME=ignis
```

**Optional:**
```env
# Integrations
BLOXLINK_API_KEY=api_key
ROBLOX_GROUP_ID=group_id
ROBLOX_COOKIE=cookie

# Compliance
CONTROLLER_EMAIL=email@example.com
PRIVACY_POLICY_URL=https://...
TERMS_OF_USE_URL=https://...

# Performance
DB_POOL_MIN=2
DB_POOL_MAX=10

# Channels
STAFF_CMDS_CHANNEL_ID=channel_id
INDUCTION_CHANNEL_ID=channel_id
EVENT_PANEL_CHANNEL_ID=channel_id
EVENT_ANNOUNCEMENT_CHANNEL_ID=channel_id
ACTIVITY_LOG_CHANNEL_ID=channel_id
```

---

## Documentation

### Technical Documentation

- [System Architecture](docs/02_ARQUITETURA/ARQUITETURA_SISTEMA.md)
- [Security Analysis](docs/02_ARQUITETURA/ANALISE_SEGURANCA.md)
- [Configuration Guide](docs/03_DESENVOLVIMENTO/SETUP_CRITICO.md)
- [Complete Catalog](docs/CATALOGO_DOCUMENTACAO.md)

### Legal Documentation

- [Privacy Policy](docs/06_LEGAL_COMPLIANCE/POLITICA_PRIVACIDADE.md)
- [Terms of Use](docs/06_LEGAL_COMPLIANCE/TERMOS_USO.md)
- [SLA](docs/06_LEGAL_COMPLIANCE/SLA.md)
- [LGPD Compliance](docs/06_LEGAL_COMPLIANCE/LGPD_COMPLIANCE.md)

---

## Architecture

### Layered Structure

```
┌─────────────────────────────────────┐
│     DISCORD API (discord.py)        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     PRESENTATION LAYER               │
│     (COGs - Command Groups)          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     SERVICE LAYER                    │
│     (Business Logic)                 │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     REPOSITORY LAYER                 │
│     (Data Access)                   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│     DATABASE (MySQL)                │
└─────────────────────────────────────┘
```

### Key Components

- **Event-Driven Architecture:** Event system for component communication
- **Dependency Injection:** Protocol-based design for testability
- **Cache System:** Distributed cache with configurable TTL
- **Connection Pool:** Optimized database connection management
- **Structured Logging:** JSON logging with automatic rotation

---

## Project Status

### Maturity Metrics

| Metric | Status |
|--------|--------|
| CMMI Level | 4 (Managed) |
| LGPD Compliance | 95% |
| Production Status | Operational |
| Test Coverage | 60-70% |
| Documentation | 110+ documents |

### Security

- Credentials protected via environment variables
- Parameterized queries (SQL injection protection)
- Structured logging with rotation
- Zero critical vulnerabilities identified
- Cache with automatic invalidation
- Optimized connection pool

### Legal Compliance

- Complete privacy policy
- Terms of use implemented
- Data subject rights (6/6)
- Incident response plan
- Audit trail (LGPD Art. 10)

---

## Available Commands

### Management
- `/userinfo [member]` - User profile
- `/add <member> <points> [reason]` - Add points
- `/remove <member> <points> [reason]` - Remove points
- `/vc_log <channel> <amount> <type>` - Voice channel log
- `/leaderboard` - User rankings

### Events
- `/event_panel [channel]` - Event panel

### Administration
- `/induction <user> [instructions]` - Induction process
- `/company [member] [company]` - Company management
- `/rank_refresh [member]` - Refresh rank

### Privacy
- `/export_my_data` - Export data
- `/delete_my_data` - Delete data
- `/correct_my_data` - Correct data
- `/consent [action]` - Manage consent

### Documentation
- `/privacy` - Privacy policy
- `/terms` - Terms of use
- `/sla` - Service Level Agreement

---

## Project Structure

```
IgnisBot/
├── cogs/                    # Command modules
├── services/                # Business logic
├── repositories/            # Data access
├── events/                  # Event handlers
├── utils/                   # Utilities
├── docs/                    # Documentation
├── tests/                   # Tests
└── scripts/                 # Automation
```

---

## Security and Privacy

### Implementations

- Environment variables for credentials
- SQL injection protection (parameterized queries)
- Complete audit logging
- Structured logging with rotation
- Role-based access control
- Optimized connection pool

### LGPD Compliance

The system implements complete LGPD compliance:

- Consent management
- Data subject rights (6/6)
- Audit trail
- Privacy policy
- Configurable data retention

---

## Testing

### Coverage

- Services: PointsService, CacheService, ConsentService, UserService
- Repositories: UserRepository with cache integration
- Edge cases: Validation, error handling, cache invalidation

### Execution

```bash
pytest tests/ -v
pytest tests/ --cov=services --cov=repositories --cov-report=html
```

---

## Performance

### Optimizations

- Distributed cache with TTL (default: 2-5 minutes)
- Connection pool (2-10 connections)
- Optimized queries with indexes
- On-demand loading

### Metrics

- Response time: < 500ms average
- Connection pool: 2-10 (auto-scaling)
- Cache hit rate: 70-80%
- Memory usage: Optimized

---

## Development

### Standards

- Python 3.10+ with type hints
- PEP 8 compliant
- Docstrings for public functions
- Specific exceptions for business logic

### Maturity

- CMMI Level 4
- IEEE/ISO documentation
- Git version control
- Documentation automation

---

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md) for detailed history.

### Recent Updates

- Event management system
- Real-time activity monitoring
- External system integration
- Automatic role synchronization
- Progress visualization improvements

---

## Security

**Important:**
- Never commit `.env` file
- Never hardcode credentials
- Always use environment variables
- Revoke old credentials
- Configure all variables before execution

---

## License

MIT License - See [LICENSE](LICENSE) for details.

---

## Contributing

Contributions are welcome. Follow guidelines:

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open Pull Request

### Guidelines

- Follow PEP 8
- Add tests for new features
- Update documentation
- Ensure tests pass

---

## Support

- [Documentation Catalog](docs/CATALOGO_DOCUMENTACAO.md)
- [Documentation Index](docs/README.md)
- [Configuration Guide](docs/03_DESENVOLVIMENTO/SETUP_CRITICO.md)
- [LGPD Compliance](docs/06_LEGAL_COMPLIANCE/LGPD_COMPLIANCE.md)

---

## Roadmap

### Completed
- Gamification system
- LGPD compliance (95%)
- Event management
- Activity monitoring
- External integrations
- Complete technical documentation

### In Progress
- Test coverage (target: 80%+)
- Event type customization
- Advanced scheduling

### Planned
- CI/CD pipeline
- Rate limiting
- Analytics dashboard
- Multi-language support
- Web dashboard

---

## Statistics

- **Commands:** 30+ slash commands
- **Documentation:** 110+ documents
- **Test Coverage:** 60-70%
- **Quality:** Production-ready
- **Performance:** Optimized

---

## Acknowledgments

- **Discord.py:** Discord API wrapper
- **Community:** Contributors and testers

---

<div align="center">

IgnisBot - Automation and Management System

[GitHub](https://github.com/Japa1413/IgnisBot) • [Documentation](docs/CATALOGO_DOCUMENTACAO.md) • [Português](README.md)

</div>
