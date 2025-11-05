# 🔗 MATRIZ DE RASTREABILIDADE LEGAL - IGNISBOT

**Versão:** 1.0  
**Última atualização:** 2025-10-31  
**Objetivo:** Rastreabilidade entre funcionalidades, código e requisitos LGPD/GDPR

---

## 📋 VISÃO GERAL

Esta matriz conecta:
- **Funcionalidades** → **Implementação em Código** → **Requisitos Legais (LGPD/GDPR)**

Facilita:
- Auditoria de conformidade
- Manutenção de documentação sincronizada
- Rastreamento de mudanças

---

## 🔗 RASTREABILIDADE POR FUNCIONALIDADE

### 1. Direito de Acesso aos Dados (LGPD Art. 18, II)

| Aspecto | Detalhes |
|---------|----------|
| **Requisito Legal** | LGPD Art. 18, II - Direito de obter confirmação sobre tratamento |
| **Funcionalidade** | `/export_my_data` - Exportar dados pessoais |
| **Código** | `cogs/data_privacy.py::export_my_data()` |
| **Service Layer** | `services/user_service.py::get_user()` |
| **Repository** | `repositories/user_repository.py::get()` |
| **Audit Log** | `repositories/audit_repository.py::log_data_operation()` |
| **Documentação** | `docs/06_LEGAL_COMPLIANCE/POLITICA_PRIVACIDADE.md` (Seção 4.1) |
| **Status** | ✅ Implementado |

---

### 2. Direito de Portabilidade (LGPD Art. 18, V)

| Aspecto | Detalhes |
|---------|----------|
| **Requisito Legal** | LGPD Art. 18, V - Exportação em formato estruturado |
| **Funcionalidade** | `/export_my_data` - Exporta JSON estruturado |
| **Código** | `cogs/data_privacy.py::export_my_data()` (formato JSON) |
| **Formato** | JSON estruturado e legível por máquina |
| **Documentação** | `docs/06_LEGAL_COMPLIANCE/POLITICA_PRIVACIDADE.md` (Seção 4.3) |
| **Status** | ✅ Implementado |

---

### 3. Direito de Correção (LGPD Art. 18, III)

| Aspecto | Detalhes |
|---------|----------|
| **Requisito Legal** | LGPD Art. 18, III - Correção de dados incompletos/incorretos |
| **Funcionalidade** | `/correct_my_data` - Solicitar correção |
| **Código** | `cogs/data_privacy.py::correct_my_data()` |
| **Campos Suportados** | `points`, `rank`, `progress` |
| **Processo** | Solicitação registrada → Revisão administrativa → Aprovação |
| **Documentação** | `docs/06_LEGAL_COMPLIANCE/POLITICA_PRIVACIDADE.md` (Seção 4.2) |
| **Status** | ✅ Implementado |

---

### 4. Direito ao Esquecimento (LGPD Art. 18, VI)

| Aspecto | Detalhes |
|---------|----------|
| **Requisito Legal** | LGPD Art. 18, VI - Exclusão de dados |
| **Funcionalidade** | `/delete_my_data` - Excluir todos os dados |
| **Código** | `cogs/data_privacy.py::execute_delete()` |
| **Tabelas Afetadas** | `users`, `user_consent`, `data_audit_log` |
| **Confirmação** | Obrigatória (botão de confirmação) |
| **Irreversível** | Sim - ação não pode ser desfeita |
| **Documentação** | `docs/06_LEGAL_COMPLIANCE/POLITICA_PRIVACIDE.md` (Seção 4.4) |
| **Status** | ✅ Implementado |

---

### 5. Gestão de Consentimento (LGPD Art. 7º, I)

| Aspecto | Detalhes |
|---------|----------|
| **Requisito Legal** | LGPD Art. 7º, I - Consentimento explícito |
| **Funcionalidade** | `/consent` - Gerenciar consentimento |
| **Código** | `cogs/data_privacy.py::consent()` |
| **Service Layer** | `services/consent_service.py` |
| **Repository** | `repositories/consent_repository.py` |
| **Utils** | `utils/consent_manager.py` |
| **Tabela** | `user_consent` |
| **Versionamento** | `CURRENT_CONSENT_VERSION = "1.0"` |
| **Documentação** | `docs/06_LEGAL_COMPLIANCE/LGPD_COMPLIANCE.md` (Seção 3.3) |
| **Status** | ✅ Implementado |

---

### 6. Validação de Consentimento em Operações

| Aspecto | Detalhes |
|---------|----------|
| **Requisito Legal** | LGPD Art. 7º, I - Não processar sem consentimento |
| **Funcionalidade** | Validação antes de processar pontos |
| **Código** | `services/points_service.py::add_points()`, `remove_points()` |
| **Validação** | Verifica `has_consent()` antes de processar |
| **Exceção** | `ValueError` se consentimento não dado |
| **Comandos Afetados** | `/add`, `/remove`, `/vc_log` |
| **Documentação** | `docs/06_LEGAL_COMPLIANCE/LGPD_COMPLIANCE.md` (Seção 3.1) |
| **Status** | ✅ Implementado (correção aplicada) |

---

### 7. Registro de Atividades (LGPD Art. 10)

| Aspecto | Detalhes |
|---------|----------|
| **Requisito Legal** | LGPD Art. 10 - Registro de operações com dados pessoais |
| **Funcionalidade** | Audit log automático |
| **Código** | `repositories/audit_repository.py`, `events/handlers/audit_handler.py` |
| **Tabela** | `data_audit_log` |
| **Campos** | `user_id`, `action_type`, `data_type`, `performed_by`, `purpose`, `timestamp`, `details` |
| **Operações Auditadas** | CREATE, READ, UPDATE, DELETE, EXPORT, ACCESS |
| **Retenção** | 6 meses (configurável) |
| **Limpeza** | `scripts/cleanup_audit_logs.py` |
| **Documentação** | `docs/06_LEGAL_COMPLIANCE/LGPD_COMPLIANCE.md` (Seção 5) |
| **Status** | ✅ Implementado |

---

### 8. Informação ao Titular (LGPD Art. 8º)

| Aspecto | Detalhes |
|---------|----------|
| **Requisito Legal** | LGPD Art. 8º - Informações sobre tratamento de dados |
| **Funcionalidade** | `/privacy` - Política de Privacidade |
| **Código** | `cogs/legal.py::privacy()` |
| **Documento** | `docs/06_LEGAL_COMPLIANCE/POLITICA_PRIVACIDADE.md` |
| **Conteúdo** | Dados coletados, finalidade, base legal, direitos, contato |
| **Acessibilidade** | Via comando Discord + URL pública (recomendado) |
| **Status** | ✅ Implementado |

---

### 9. Termos de Uso

| Aspecto | Detalhes |
|---------|----------|
| **Requisito Legal** | Boas práticas - Contrato de uso do serviço |
| **Funcionalidade** | `/terms` - Termos de Uso |
| **Código** | `cogs/legal.py::terms()` |
| **Documento** | `docs/06_LEGAL_COMPLIANCE/TERMOS_USO.md` |
| **Status** | ✅ Implementado |

---

### 10. Service Level Agreement (SLA)

| Aspecto | Detalhes |
|---------|----------|
| **Requisito Legal** | Boas práticas - Compromissos de serviço |
| **Funcionalidade** | `/sla` - Service Level Agreement |
| **Código** | `cogs/legal.py::sla()` |
| **Documento** | `docs/06_LEGAL_COMPLIANCE/SLA.md` |
| **Status** | ✅ Implementado |

---

## 🔄 RASTREABILIDADE POR REQUISITO LEGAL

### LGPD Art. 7º - Bases Legais

| Base Legal | Aplicação | Código | Status |
|------------|-----------|--------|--------|
| **Art. 7º, I - Consentimento** | Processamento de pontos, ranks | `services/consent_service.py` | ✅ |
| **Art. 7º, II - Obrigação Legal** | Retenção de logs de auditoria (6 meses) | `scripts/cleanup_audit_logs.py` | ✅ |
| **Art. 7º, V - Execução de Contrato** | Funcionalidades do bot | Documentado | ⚠️ |
| **Art. 7º, IX - Legítimo Interesse** | Logs de segurança | Documentado | ⚠️ |

---

### LGPD Art. 18 - Direitos do Titular

| Direito | Artigo | Implementação | Status |
|---------|--------|----------------|--------|
| Acesso | Art. 18, II | `/export_my_data` | ✅ |
| Correção | Art. 18, III | `/correct_my_data` | ✅ |
| Anonimização | Art. 18, IV | `/delete_my_data` | ✅ |
| Portabilidade | Art. 18, V | `/export_my_data` (JSON) | ✅ |
| Exclusão | Art. 18, VI | `/delete_my_data` | ✅ |
| Revogação Consentimento | Art. 8º, §5º | `/consent revoke` | ✅ |

---

## 📊 MATRIZ DE COMPONENTES

### Camadas de Código → Requisitos Legais

| Componente | Responsabilidade | LGPD Art. | Status |
|------------|------------------|-----------|--------|
| `cogs/data_privacy.py` | Comandos de privacidade | Art. 18 (todos) | ✅ |
| `cogs/legal.py` | Documentos legais | Art. 8º | ✅ |
| `services/consent_service.py` | Lógica de consentimento | Art. 7º, I | ✅ |
| `services/points_service.py` | Validação de consentimento | Art. 7º, I | ✅ |
| `repositories/audit_repository.py` | Registro de atividades | Art. 10 | ✅ |
| `utils/consent_manager.py` | Gerenciamento de consentimento | Art. 7º, I | ✅ |
| `utils/audit_log.py` | Logging de operações | Art. 10 | ✅ |
| `scripts/cleanup_audit_logs.py` | Retenção de dados | Art. 15 | ✅ |

---

## 🔍 VERIFICAÇÃO DE CONFORMIDADE

### Checklist de Rastreabilidade

- [x] Cada requisito legal tem implementação identificada
- [x] Cada funcionalidade tem requisito legal associado
- [x] Cada componente de código tem documentação
- [x] Matriz atualizada após mudanças

---

## 📝 MANUTENÇÃO DA MATRIZ

**Responsável:** Equipe de Desenvolvimento + DPO

**Frequência de Atualização:**
- Sempre que nova funcionalidade é adicionada
- Sempre que requisito legal é implementado
- Semestralmente (revisão completa)

**Processo:**
1. Identificar funcionalidade/requisito
2. Mapear código correspondente
3. Atualizar esta matriz
4. Validar rastreabilidade
5. Documentar mudanças

---

**Última atualização:** 2025-10-31  
**Versão:** 1.0  
**Próxima revisão:** 2026-04-30

