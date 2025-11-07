# 📋 Guia de Comandos - IgnisBot

**Last Updated:** 2025-11-07

---

## Comandos de Gamificação

### `/userinfo [member]`
Exibe informações do usuário com progressão.

**Canais:** Canal específico (configurável)  
**Permissões:** Todos

**Exemplo:**
```
/userinfo
/userinfo @usuario
```

---

### `/add <member> <points> <reason>`
Adiciona pontos a um usuário.

**Canais:** Canal de staff apenas  
**Permissões:** Moderador ou Administrador

**Parâmetros:**
- `member`: Membro do Discord
- `points`: Pontos para adicionar (1-100,000)
- `reason`: Motivo (obrigatório)

**Exemplo:**
```
/add @usuario 100 Participação em evento
```

---

### `/remove <member> <points> <reason>`
Remove pontos de um usuário.

**Canais:** Canal de staff apenas  
**Permissões:** Moderador ou Administrador

**Parâmetros:**
- `member`: Membro do Discord
- `points`: Pontos para remover
- `reason`: Motivo (obrigatório)

**Exemplo:**
```
/remove @usuario 50 Penalidade
```

---

### `/vc_log <vc_name> <amount> <event_type>`
Registra pontos para todos os membros em um canal de voz.

**Canais:** Canal de staff apenas  
**Permissões:** Moderador ou Administrador

**Parâmetros:**
- `vc_name`: Nome do canal Vox-link (obrigatório)
- `amount`: Quantidade de pontos
- `event_type`: Tipo de evento

**Canais Vox-link:**
- Vox-link Ⅰ
- Vox-link ⅠⅠ
- Vox-link ⅠⅠⅠ
- Vox-link Ⅳ

**Exemplo:**
```
/vc_log "Vox-link Ⅰ" 50 Treinamento
```

---

### `/leaderboard [limit]`
Exibe ranking de usuários por pontos.

**Canais:** Qualquer canal  
**Permissões:** Todos

**Parâmetros:**
- `limit`: Número de usuários (padrão: 10)

**Exemplo:**
```
/leaderboard
/leaderboard 20
```

---

## Comandos de Indução

### `/induction <roblox_username>`
Inicia processo de indução para um jogador.

**Canais:** Canal de staff apenas  
**Permissões:** Moderador ou Administrador

**Parâmetros:**
- `roblox_username`: Nome de usuário do Roblox (não display name)

**Exemplo:**
```
/induction bielmaximo10
```

---

## Comandos de Privacidade (LGPD)

### `/consent [action]`
Gerencia consentimento para processamento de dados.

**Canais:** Qualquer canal  
**Permissões:** Todos

**Ações:**
- `grant`: Conceder consentimento
- `revoke`: Revogar consentimento
- `status`: Verificar status

**Exemplo:**
```
/consent grant
/consent revoke
/consent status
```

---

### `/export_my_data`
Exporta todos os seus dados pessoais.

**Canais:** Qualquer canal  
**Permissões:** Todos

**Resposta:** Arquivo JSON com todos os dados

---

### `/delete_my_data`
Solicita exclusão de todos os seus dados.

**Canais:** Qualquer canal  
**Permissões:** Todos

**Atenção:** Esta ação é irreversível!

---

### `/correct_my_data`
Solicita correção de dados pessoais.

**Canais:** Qualquer canal  
**Permissões:** Todos

---

## Comandos Legais

### `/privacy`
Exibe política de privacidade.

**Canais:** Qualquer canal  
**Permissões:** Todos

---

### `/terms`
Exibe termos de uso.

**Canais:** Qualquer canal  
**Permissões:** Todos

---

### `/sla`
Exibe informações sobre SLA (Service Level Agreement).

**Canais:** Qualquer canal  
**Permissões:** Todos

---

## Comandos de Sistema

### `/health`
Verifica saúde do bot e status do sistema.

**Canais:** Qualquer canal  
**Permissões:** Todos

**Informações:**
- Status do banco de dados
- Status do cache
- Status das integrações
- Latência de comandos

---

### `/cache_stats`
Exibe estatísticas do cache.

**Canais:** Qualquer canal  
**Permissões:** Todos

**Informações:**
- Taxa de acerto (hit rate)
- Número de hits/misses
- Entradas no cache

---

### `/help`
Lista todos os comandos disponíveis.

**Canais:** Qualquer canal  
**Permissões:** Todos

---

## Restrições de Canal

Alguns comandos só funcionam em canais específicos:

- **Canal de Staff:** `/add`, `/remove`, `/vc_log`, `/induction`
- **Canal de Userinfo:** `/userinfo`
- **Qualquer Canal:** Todos os outros comandos

Use `/help` para ver informações detalhadas sobre restrições.

---

## Permissões Necessárias

### Comandos Administrativos
Requerem uma das seguintes permissões:
- `manage_messages` OU
- `administrator` OU
- Ser dono do servidor

### Comandos Públicos
Todos os usuários podem usar.

---

**Para mais informações, consulte o README.md principal**

