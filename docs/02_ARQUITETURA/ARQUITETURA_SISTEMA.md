# 🏗️ ARQUITETURA DO SISTEMA - IGNISBOT

**Versão:** 1.0  
**Última atualização:** 2024

---

## 1. VISÃO GERAL

O **IgnisBot** é um bot Discord desenvolvido em Python que implementa um sistema de gamificação baseado em pontos e ranks. A arquitetura segue o padrão modular usando COGs (Command Groups) do discord.py.

---

## 2. ARQUITETURA GERAL

```
┌─────────────────────────────────────────────────────────────┐
│                     DISCORD API                             │
│                  (discord.py 2.3+)                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        │ Eventos/Interações
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    IGNISBOT CORE                            │
│                  (ignis_main.py)                            │
│  • Bot Instance                                             │
│  • Event Handlers                                           │
│  • COG Loader                                               │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│    COGs      │ │    UTILS     │ │   DATABASE   │
│              │ │              │ │              │
│ • userinfo   │ │ • config     │ │ • MySQL Pool │
│ • add        │ │ • database   │ │ • Queries    │
│ • remove     │ │ • audit_log  │ │ • Tables     │
│ • vc_log     │ │ • logger     │ │              │
│ • leaderboard│ │ • checks     │ │              │
│ • data_privacy│ │ • consent    │ │              │
│ • legal      │ │              │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## 3. COMPONENTES PRINCIPAIS

### 3.1 Core (ignis_main.py)

**Responsabilidades:**
- Inicialização do bot Discord
- Carregamento de COGs
- Gerenciamento de eventos globais
- Sincronização de comandos slash

**Fluxo de Inicialização:**
```
1. Carregar configurações (utils.config)
2. Inicializar banco de dados (utils.database.initialize_db)
3. Carregar todos os COGs
4. Sincronizar comandos slash com Discord
5. Bot online e pronto
```

### 3.2 COGs (Command Groups)

Os COGs são módulos modulares que agrupam funcionalidades relacionadas:

#### 3.2.1 COGs de Funcionalidade
- **userinfo.py:** Exibe informações do usuário (pontos, rank, progresso)
- **add.py:** Adiciona pontos a usuários (comando administrativo)
- **remove.py:** Remove pontos de usuários (comando administrativo)
- **vc_log.py:** Registra pontos para membros em canais de voz
- **leaderboard.py:** Exibe ranking dos top 10 usuários
- **rank.py:** Gerenciamento de ranks (funcionalidade adicional)

#### 3.2.2 COGs de Conformidade
- **data_privacy.py:** Comandos de privacidade LGPD
  - `/export_my_data`: Exportação de dados
  - `/delete_my_data`: Direito ao esquecimento
  - `/consent`: Gerenciamento de consentimento
  
- **legal.py:** Documentos legais
  - `/privacy`: Política de privacidade
  - `/terms`: Termos de uso
  - `/sla`: Service Level Agreement

### 3.3 Utils (Utilitários)

#### 3.3.1 config.py
**Responsabilidade:** Gerenciamento de configurações
- Carregamento de variáveis de ambiente
- Validação de configurações obrigatórias
- Centralização de constantes

#### 3.3.2 database.py
**Responsabilidade:** Camada de acesso a dados
- Pool de conexões MySQL (aiomysql)
- Funções de CRUD para usuários
- Inicialização de schema
- Função `get_pool()` para acesso ao pool

**Padrão de Uso:**
```python
pool = get_pool()
async with pool.acquire() as conn:
    async with conn.cursor() as cursor:
        await cursor.execute("SELECT ... WHERE id = %s", (user_id,))
```

#### 3.3.3 audit_log.py
**Responsabilidade:** Auditoria LGPD (Art. 10)
- Registro de operações com dados pessoais
- Histórico de auditoria por usuário
- Suporte a detalhes JSON

#### 3.3.4 consent_manager.py
**Responsabilidade:** Gerenciamento de consentimento LGPD
- Verificação de consentimento
- Registro de consentimento/revogação
- Versionamento de políticas

#### 3.3.5 logger.py
**Responsabilidade:** Sistema de logging estruturado
- Logging em formato JSON para arquivo
- Logging legível para console
- Rotação automática de arquivos
- Integração com audit log

#### 3.3.6 checks.py
**Responsabilidade:** Verificações de permissão
- Restrição de comandos por canal
- Suporte para comandos texto e slash

---

## 4. BANCO DE DADOS

### 4.1 Estrutura

#### Tabela: `users`
```sql
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    points INT DEFAULT 0,
    `rank` VARCHAR(50) DEFAULT 'Civitas aspirant',
    progress INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
```

#### Tabela: `user_consent`
```sql
CREATE TABLE user_consent (
    user_id BIGINT PRIMARY KEY,
    consent_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    consent_version VARCHAR(20) DEFAULT '1.0',
    base_legal VARCHAR(50) DEFAULT 'consentimento',
    consent_given BOOLEAN DEFAULT FALSE,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
)
```

#### Tabela: `data_audit_log`
```sql
CREATE TABLE data_audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    data_type VARCHAR(100) NOT NULL,
    performed_by BIGINT,
    purpose TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    details JSON,
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_action_type (action_type)
)
```

### 4.2 Pool de Conexões

- **Tecnologia:** aiomysql
- **Configuração:** Pool com 1-5 conexões
- **Uso:** Todas as operações usam o pool (não conexões diretas)
- **Timeout:** 5 segundos para conexão

---

## 5. FLUXO DE DADOS

### 5.1 Comando do Usuário

```
Usuário → Discord → IgnisBot → COG → Utils → Database
                                       ↓
                                   Audit Log
```

### 5.2 Exemplo: Adicionar Pontos

```
1. Usuário executa /add @member 100 "Evento"
2. AddPointsCog.add() é chamado
3. Verifica canal permitido (checks.py)
4. Busca usuário (database.get_user)
5. Atualiza pontos (database.update_points)
   ├── Executa UPDATE no banco
   └── Registra em audit_log
6. Retorna embed com resultado
```

### 5.3 Exemplo: Exportar Dados (LGPD)

```
1. Usuário executa /export_my_data
2. DataPrivacyCog.export_my_data() é chamado
3. Registra acesso (audit_log.log_data_operation)
4. Coleta dados:
   ├── users (database.get_user)
   ├── consent (consent_manager.get_consent_info)
   └── audit_history (audit_log.get_user_audit_history)
5. Monta JSON
6. Envia como arquivo Discord
```

---

## 6. SEGURANÇA

### 6.1 Proteção SQL Injection

✅ **Todas as queries usam parametrização:**
```python
await cursor.execute("SELECT ... WHERE user_id = %s", (user_id,))
```

✅ **Nenhuma concatenação de strings em SQL**

### 6.2 Proteção de Credenciais

✅ **Variáveis de ambiente via .env**
✅ **Validação na inicialização**
✅ **.gitignore protege arquivos sensíveis**

### 6.3 Controle de Acesso

✅ **Restrição por canal (checks.py)**
✅ **Comandos administrativos protegidos**
✅ **Audit log de ações administrativas**

---

## 7. PADRÕES DE DESIGN

### 7.1 Modularidade
- COGs isolados por funcionalidade
- Utils compartilhados
- Fácil adicionar/remover funcionalidades

### 7.2 Separação de Responsabilidades
- COGs: Lógica de negócio e interação Discord
- Utils: Funcionalidades reutilizáveis
- Database: Acesso a dados apenas

### 7.3 Tratamento de Erros
- Try/except em operações críticas
- Logging de erros
- Mensagens amigáveis ao usuário

---

## 8. DEPENDÊNCIAS EXTERNAS

### 8.1 Principais
- **discord.py 2.3+:** API do Discord
- **aiomysql 0.2+:** Cliente MySQL assíncrono
- **python-dotenv:** Carregamento de .env

### 8.2 Padrão Python
- **asyncio:** Programação assíncrona
- **typing:** Type hints
- **json:** Serialização (audit log)

---

## 9. LOGGING E AUDITORIA

### 9.1 Logging de Sistema
- **Arquivo:** `logs/ignisbot.log` (JSON estruturado)
- **Console:** Formato legível
- **Rotação:** 10MB, 5 backups

### 9.2 Audit Log (LGPD)
- **Tabela:** `data_audit_log`
- **Registro:** Todas as operações com dados pessoais
- **Retenção:** 6 meses

---

## 10. EXTENSIBILIDADE

### 10.1 Adicionar Novo COG

1. Criar arquivo em `cogs/nome.py`
2. Implementar classe herdando `commands.Cog`
3. Adicionar ao `ignis_main.py`:
   ```python
   from cogs.nome import NomeCog
   await self.add_cog(NomeCog(self))
   ```

### 10.2 Adicionar Nova Funcionalidade de Banco

1. Criar função em `utils/database.py`
2. Usar pool de conexões
3. Usar parametrização SQL
4. Registrar em audit_log se manipular dados pessoais

---

## 11. DIAGRAMA DE SEQUÊNCIA

### Exemplo: Processo de Adicionar Pontos

```
Admin    Discord    IgnisBot    AddCog    Database    AuditLog
  │         │           │          │          │           │
  │──/add──>│           │          │          │           │
  │         │──event───>│          │          │           │
  │         │           │──exec───>│          │           │
  │         │           │          │──get────>│           │
  │         │           │          │<──user───│           │
  │         │           │          │──update─>│           │
  │         │           │          │          │           │
  │         │           │          │──log─────┼──────────>│
  │         │           │          │          │           │
  │         │<──embed───│<──result─│          │           │
  │<────────┘           │          │          │           │
```

---

## 12. CONSIDERAÇÕES DE PERFORMANCE

### 12.1 Otimizações
- Pool de conexões (evita overhead de conexão)
- Índices no banco de dados
- Cache de comandos Discord (sincronização por guild)

### 12.2 Limitações Atuais
- Sem cache em memória (todas as queries vão ao banco)
- Sem rate limiting implementado (pendente)
- Sem batch operations para múltiplos usuários

---

## 13. MELHORIAS FUTURAS

### 13.1 Curto Prazo
- [ ] Cache Redis para dados frequentes
- [ ] Rate limiting por usuário
- [ ] Métricas e monitoramento

### 13.2 Médio Prazo
- [ ] Migração para arquitetura de microsserviços (se escalar)
- [ ] CDN para assets estáticos
- [ ] Load balancing (se múltiplas instâncias)

---

**Documento mantido por:** AI-AuditEng  
**Versão:** 1.0  
**Última atualização:** 2024

