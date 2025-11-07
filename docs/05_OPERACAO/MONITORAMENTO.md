# 📊 Guia de Monitoramento - IgnisBot

**Last Updated:** 2025-11-07

---

## Visão Geral

O IgnisBot possui sistemas integrados de monitoramento e saúde que permitem verificar o status do bot em tempo real.

---

## Comando `/health`

O comando `/health` fornece um relatório completo do status do bot.

### Informações Exibidas

#### Status Geral
- **HEALTHY**: Todos os sistemas funcionando normalmente
- **DEGRADED**: Alguns sistemas com problemas, mas bot ainda funcional
- **UNHEALTHY**: Problemas críticos detectados

#### Database
- Status da conexão
- Latência de queries
- Tamanho do pool de conexões
- Utilização do pool

#### Cache
- Taxa de acerto (hit rate)
- Número de hits/misses
- Entradas no cache
- Evictions

#### Integrations
- Status do Bloxlink API
- Status do Roblox API
- Latência de cada integração

#### Command Latency
- Latência média de comandos
- Status de performance

---

## Monitoramento Contínuo

### Script de Monitoramento

Execute o script de monitoramento para verificação automática:

```bash
python scripts/monitor_bot.py
```

**Funcionalidades:**
- Verifica saúde do bot a cada 5 minutos
- Registra métricas em logs
- Envia alertas quando problemas são detectados
- Previne spam de alertas (máximo 1 por hora)

**Configuração:**
- `CHECK_INTERVAL`: Intervalo entre verificações (padrão: 300 segundos)
- `ALERT_THRESHOLD_ERRORS`: Alertas após N erros (padrão: 10)
- `ALERT_THRESHOLD_DEGRADED`: Alertas após N checks degradados (padrão: 3)

---

## Métricas Importantes

### Performance
- **Tempo de resposta médio**: < 2 segundos
- **Taxa de erro**: < 1%
- **Cache hit rate**: > 80% (ideal)

### Banco de Dados
- **Latência de queries**: < 50ms (ideal)
- **Pool utilization**: < 80% (evitar esgotamento)
- **Conexões livres**: Sempre manter algumas disponíveis

### Cache
- **Hit rate**: > 80% indica bom uso
- **Eviction rate**: < 5% indica TTL adequado
- **Active users**: Usuários com cache ativo

---

## Alertas

O sistema de monitoramento envia alertas quando:

1. **Health check falha** 10 vezes consecutivas
2. **Status degradado** por 3 verificações consecutivas
3. **Erros críticos** são detectados

### Configurar Notificações

Para adicionar notificações (Discord webhook, email, etc.), edite `scripts/monitor_bot.py` na função `send_alert()`.

---

## Logs

### Verificar Logs Recentes

```bash
# Últimas 50 linhas
tail -50 logs/ignisbot.log

# Filtrar por erro
grep -i error logs/ignisbot.log | tail -20

# Filtrar por health check
grep -i health logs/ignisbot.log | tail -20
```

### Estrutura de Logs

Os logs são estruturados em JSON para facilitar análise:

```json
{
  "timestamp": "2025-11-07T03:38:24.874307",
  "level": "INFO",
  "logger": "utils.database",
  "message": "✅ Synced 19 commands for guild",
  "module": "ignis_main",
  "function": "on_ready",
  "line": 127
}
```

---

## Troubleshooting

### Status DEGRADED

**Possíveis causas:**
- Integração externa temporariamente indisponível
- Cache com baixa taxa de acerto
- Latência alta em algum sistema

**Ações:**
1. Verificar logs para identificar sistema específico
2. Usar `/health` para detalhes
3. Aguardar alguns minutos e verificar novamente

### Status UNHEALTHY

**Possíveis causas:**
- Banco de dados não inicializado
- Erro crítico em algum sistema
- Falha de conexão

**Ações:**
1. Verificar se banco de dados está rodando
2. Verificar credenciais no `.env`
3. Reiniciar o bot
4. Verificar logs para detalhes do erro

---

## Próximos Passos

1. **Configurar alertas**: Adicionar notificações via Discord webhook
2. **Dashboard**: Criar dashboard visual de métricas
3. **Métricas históricas**: Armazenar métricas para análise de tendências
4. **Auto-recovery**: Implementar recuperação automática para problemas comuns

---

**Para mais informações, consulte:**
- `docs/05_OPERACAO/TROUBLESHOOTING.md` - Guia de troubleshooting
- `docs/03_DESENVOLVIMENTO/API.md` - Documentação de APIs

