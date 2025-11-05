# 🏛️ GOVERANÇA DE DADOS - IGNISBOT

**Versão:** 1.0  
**Última atualização:** 2025-10-31  
**Status:** ⚠️ **PENDENTE CONFIGURAÇÃO**

---

## 📋 VISÃO GERAL

Este documento identifica as responsabilidades e estrutura de governança para tratamento de dados pessoais no IgnisBot, conforme exigido pela LGPD (Lei nº 13.709/2018).

---

## 👥 IDENTIFICAÇÃO DE RESPONSÁVEIS

### 1. CONTROLADOR DOS DADOS (LGPD Art. 5º, VI)

**⚠️ PENDENTE:** Definir controlador dos dados

**Definição:** É a pessoa natural ou jurídica, de direito público ou privado, a quem competem as decisões referentes ao tratamento de dados pessoais.

**O que deve ser definido:**
- Nome completo ou razão social
- CNPJ (se pessoa jurídica) ou CPF (se pessoa física)
- Endereço completo
- Telefone de contato
- E-mail de contato

**Configuração:**
1. Preencher informações abaixo
2. Atualizar `POLITICA_PRIVACIDADE.md` (Seção 1)
3. Configurar variáveis de ambiente no `.env` (se aplicável)

---

**CONTROLADOR (Exemplo - Substituir pelos dados reais):**

```
Nome/Razão Social: [DEFINIR]
CNPJ/CPF: [DEFINIR]
Endereço: [DEFINIR]
Telefone: [DEFINIR]
E-mail: [Configurar CONTROLLER_EMAIL no .env]
```

---

### 2. ENCARREGADO DE DADOS (DPO) - LGPD Art. 41

**⚠️ PENDENTE:** Designar DPO

**Definição:** Pessoa indicada pelo controlador e operador para atuar como canal de comunicação entre o controlador, os titulares dos dados e a Autoridade Nacional de Proteção de Dados (ANPD).

**Responsabilidades:**
- Receber comunicações dos titulares sobre privacidade
- Orientar sobre práticas de proteção de dados
- Comunicar-se com a ANPD quando necessário
- Realizar controle interno da conformidade com a LGPD

**Configuração:**
1. Escolher DPO (pode ser o próprio desenvolvedor para uso não-comercial)
2. Preencher informações abaixo
3. Atualizar `POLITICA_PRIVACIDADE.md` (Seção 11)
4. Configurar `CONTROLLER_EMAIL` no `.env`

---

**DPO (Exemplo - Substituir pelos dados reais):**

```
Nome: [DEFINIR NOME DO DPO]
E-mail: [Configurar CONTROLLER_EMAIL no .env]
Telefone: [Opcional]
```

**Guia Completo:** Ver [`docs/03_DESENVOLVIMENTO/CONFIGURAR_DPO.md`](../03_DESENVOLVIMENTO/CONFIGURAR_DPO.md)

---

### 3. PROCESSADORES DE DADOS (LGPD Art. 5º, VII)

**Definição:** Pessoa natural ou jurídica, de direito público ou privado, que realiza o tratamento de dados pessoais em nome do controlador.

**Processadores Identificados:**

| Processador | Localização | Dados Processados | Base Legal |
|-------------|-------------|-------------------|------------|
| **Discord Inc.** | EUA | Dados de API do Discord (nomes, avatares, IDs) | Contrato/Consentimento |
| **Hosting Provider** | [A DEFINIR] | Dados do banco de dados MySQL | Contrato |
| **Desenvolvedor/Mantenedor** | [A DEFINIR] | Dados técnicos, logs | Contrato |

**Medidas de Garantia:**
- ⚠️ Revisar termos de serviço do Discord (pendente)
- ⚠️ Cláusulas contratuais de proteção de dados (pendente)
- ⚠️ Verificar conformidade com GDPR (se aplicável) (pendente)

---

## 📊 MATRIZ DE RESPONSABILIDADES

| Responsabilidade | Controlador | DPO | Processador |
|-----------------|-------------|-----|-------------|
| Decisões sobre tratamento | ✅ | - | - |
| Comunicação com titulares | ✅ | ✅ | - |
| Comunicação com ANPD | ✅ | ✅ | - |
| Implementação técnica | - | - | ✅ |
| Execução do tratamento | - | - | ✅ |
| Auditoria interna | ✅ | ✅ | - |

---

## 🔄 PROCESSO DE GOVERNANÇA

### 1. Tomada de Decisão sobre Tratamento

**Responsável:** Controlador

**Processo:**
1. Controlador decide sobre finalidade e base legal
2. DPO avalia conformidade com LGPD
3. Processador implementa tecnicamente
4. Auditoria registra decisões

---

### 2. Resposta a Requisições de Titulares

**Responsável:** DPO (com suporte do Controlador)

**Processo:**
1. Titular solicita via comando Discord ou e-mail
2. DPO recebe e analisa solicitação
3. DPO coordena resposta técnica (se necessário)
4. DPO responde ao titular em até 15 dias úteis (LGPD Art. 18, §3º)

---

### 3. Notificação de Incidentes

**Responsável:** Controlador + DPO

**Processo:**
1. Detecção de incidente
2. Avaliação de risco
3. Notificação à ANPD em até 72h (se aplicável)
4. Notificação aos titulares afetados
5. Documentação do incidente

**Documento:** Ver [`PLANO_INCIDENTES.md`](PLANO_INCIDENTES.md)

---

### 4. Revisão Periódica de Conformidade

**Frequência:** Semestral

**Responsável:** DPO

**Processo:**
1. Revisar políticas e procedimentos
2. Verificar conformidade com mudanças na legislação
3. Avaliar eficácia de medidas de segurança
4. Atualizar documentação se necessário
5. Reportar ao Controlador

---

## 📝 CHECKLIST DE CONFIGURAÇÃO

### Controlador
- [ ] Nome/Razão Social definido
- [ ] CNPJ/CPF identificado
- [ ] Contatos configurados
- [ ] Política de Privacidade atualizada

### DPO
- [ ] DPO designado
- [ ] Nome do DPO documentado
- [ ] E-mail do DPO configurado (`CONTROLLER_EMAIL`)
- [ ] Política de Privacidade atualizada (Seção 11)
- [ ] DPO informado sobre responsabilidades

### Processadores
- [ ] Termos de serviço do Discord revisados
- [ ] Cláusulas contratuais verificadas
- [ ] Hosting provider identificado
- [ ] Garantias de proteção documentadas

---

## 📚 REFERÊNCIAS LEGAIS

- **LGPD Art. 5º, VI:** Definição de Controlador
- **LGPD Art. 5º, VII:** Definição de Processador
- **LGPD Art. 41:** Encarregado de Dados (DPO)
- **LGPD Art. 46:** Medidas de Segurança
- **LGPD Art. 48:** Notificação de Incidentes

---

## ⚠️ STATUS ATUAL

**Conformidade de Governança:** 🟡 **60%**

**Pendências:**
- ⚠️ Controlador não identificado
- ⚠️ DPO não designado
- ⚠️ Processadores não totalmente documentados

**Ações Necessárias:**
1. Preencher informações de Controlador
2. Designar e configurar DPO
3. Documentar processadores adequadamente
4. Revisar e atualizar este documento após preenchimento

---

**Documento mantido por:** DPO (após designação)  
**Próxima revisão:** Após configuração inicial  
**Versão:** 1.0

