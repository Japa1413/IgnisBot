# 🚀 Como Rodar o Ignis 24/7

## 📋 Visão Geral

Este guia explica como configurar o IgnisBot para rodar 24 horas por dia, 7 dias por semana, mesmo quando você não está usando o computador ou quando ele é reiniciado.

---

## 🎯 Opções Disponíveis

### Opção 1: Task Scheduler (Recomendado para Windows)

O Task Scheduler do Windows permite que o bot inicie automaticamente quando o sistema inicia e reinicie automaticamente se ele falhar.

**Vantagens:**
- ✅ Funciona mesmo sem você estar logado
- ✅ Reinicia automaticamente após reinicialização do sistema
- ✅ Reinicia automaticamente se o bot crashar
- ✅ Não requer software adicional

**Desvantagens:**
- ⚠️ Requer privilégios de Administrador para instalar

### Opção 2: Script PowerShell de Monitoramento

Um script PowerShell que monitora o bot e o reinicia automaticamente se ele parar.

**Vantagens:**
- ✅ Fácil de usar
- ✅ Não requer privilégios de Administrador
- ✅ Logs detalhados

**Desvantagens:**
- ⚠️ Precisa estar logado no Windows
- ⚠️ Para quando você desliga o computador

---

## 🔧 Instalação - Opção 1: Task Scheduler

### Passo 1: Executar o Script de Instalação

1. Abra o PowerShell **como Administrador**
   - Clique com o botão direito no PowerShell
   - Selecione "Executar como administrador"

2. Navegue até a pasta do projeto:
   ```powershell
   cd C:\Gabriel\github\IgnisBot
   ```

3. Execute o script de instalação:
   ```powershell
   .\scripts\install_windows_service.ps1
   ```

### Passo 2: Verificar Instalação

Verifique se a tarefa foi criada:
```powershell
Get-ScheduledTask -TaskName "IgnisBot"
```

### Passo 3: Iniciar o Bot

Inicie o bot manualmente:
```powershell
Start-ScheduledTask -TaskName "IgnisBot"
```

### Passo 4: Verificar Status

Verifique se o bot está rodando:
```powershell
Get-Process python | Where-Object {$_.Path -like "*IgnisBot*"}
```

---

## 🔧 Instalação - Opção 2: Script de Monitoramento

### Passo 1: Executar o Script de Inicialização

1. Abra o PowerShell (não precisa ser Administrador)

2. Navegue até a pasta do projeto:
   ```powershell
   cd C:\Gabriel\github\IgnisBot
   ```

3. Execute o script:
   ```powershell
   .\scripts\start_ignis_24_7.ps1
   ```

### Passo 2: Deixar o PowerShell Aberto

O script abrirá uma nova janela do PowerShell que monitora o bot. **Não feche esta janela!**

---

## 📊 Gerenciamento do Serviço (Task Scheduler)

### Comandos Úteis

```powershell
# Iniciar o bot
Start-ScheduledTask -TaskName "IgnisBot"

# Parar o bot
Stop-ScheduledTask -TaskName "IgnisBot"

# Verificar status
Get-ScheduledTask -TaskName "IgnisBot"

# Ver histórico de execuções
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" | Where-Object {$_.Message -like "*IgnisBot*"}

# Remover o serviço
Unregister-ScheduledTask -TaskName "IgnisBot" -Confirm:$false
```

### Via Interface Gráfica

1. Abra o **Agendador de Tarefas** (Task Scheduler)
   - Pressione `Win + R`
   - Digite `taskschd.msc`
   - Pressione Enter

2. Procure por "IgnisBot" na lista de tarefas

3. Clique com o botão direito para:
   - Executar
   - Desabilitar
   - Propriedades
   - Excluir

---

## 🔍 Verificação e Monitoramento

### Verificar se o Bot Está Rodando

```powershell
# Ver processos Python do Ignis
Get-Process python | Where-Object {$_.Path -like "*IgnisBot*"}

# Ver logs
Get-Content logs\ignisbot.log -Tail 50

# Verificar status via Discord
# Use o comando /health no Discord
```

### Logs

Os logs estão disponíveis em:
- **Bot logs**: `logs/ignisbot.log`
- **Monitor logs** (Opção 2): `logs/monitor.log`

---

## ⚠️ Troubleshooting

### Bot não inicia automaticamente

1. Verifique se a tarefa está habilitada:
   ```powershell
   Get-ScheduledTask -TaskName "IgnisBot" | Select-Object State
   ```

2. Verifique os logs do Task Scheduler:
   - Abra o Agendador de Tarefas
   - Encontre a tarefa "IgnisBot"
   - Clique em "Histórico" para ver erros

### Bot para de funcionar

1. Verifique os logs:
   ```powershell
   Get-Content logs\ignisbot.log -Tail 100
   ```

2. Verifique se há erros no Python:
   ```powershell
   python ignis_main.py
   ```

3. Reinicie o serviço:
   ```powershell
   Stop-ScheduledTask -TaskName "IgnisBot"
   Start-Sleep -Seconds 5
   Start-ScheduledTask -TaskName "IgnisBot"
   ```

### Bot consome muita memória/CPU

1. Use o comando `/health` no Discord para verificar recursos
2. Verifique os logs para identificar problemas
3. Considere reiniciar o bot periodicamente

---

## 🔐 Segurança

### Recomendações

1. **Não compartilhe suas credenciais**
   - Mantenha o arquivo `.env` seguro
   - Não commite tokens no Git

2. **Use um usuário dedicado** (Opcional)
   - Crie um usuário do Windows apenas para o bot
   - Execute o serviço com este usuário

3. **Firewall**
   - Certifique-se de que o firewall permite conexões do bot

---

## 📚 Recursos Adicionais

- **Documentação do Task Scheduler**: https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page
- **PowerShell Scripting**: https://docs.microsoft.com/en-us/powershell/

---

## 💡 Dicas

1. **Teste antes de deixar rodando 24/7**
   - Execute o bot manualmente primeiro
   - Verifique se tudo funciona corretamente

2. **Monitore os logs regularmente**
   - Verifique os logs diariamente
   - Identifique problemas antes que se tornem críticos

3. **Faça backups regulares**
   - Backup do banco de dados
   - Backup do arquivo `.env`

4. **Atualize regularmente**
   - Mantenha o Python atualizado
   - Mantenha as dependências atualizadas

---

## 🆘 Suporte

Se precisar de ajuda:
1. Verifique os logs: `logs/ignisbot.log`
2. Use o comando `/health` no Discord
3. Verifique o status do serviço: `Get-ScheduledTask -TaskName "IgnisBot"`


