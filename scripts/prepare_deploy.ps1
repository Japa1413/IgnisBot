# IgnisBot - Preparação Automática para Deploy
# Este script prepara tudo para o deploy na nuvem

$ErrorActionPreference = "Continue"

Write-Host "=== IgnisBot - Preparação para Deploy ===" -ForegroundColor Cyan
Write-Host ""

# Verificar se está em um repositório Git
Write-Host "[1/5] Verificando repositório Git..." -ForegroundColor Yellow
$gitStatus = git status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Não é um repositório Git. Inicializando..." -ForegroundColor Yellow
    git init
    git branch -M main
    Write-Host "✅ Repositório Git inicializado" -ForegroundColor Green
} else {
    Write-Host "✅ Repositório Git encontrado" -ForegroundColor Green
}

# Verificar se há arquivos não commitados
Write-Host ""
Write-Host "[2/5] Verificando arquivos não commitados..." -ForegroundColor Yellow
$uncommitted = git status --porcelain
if ($uncommitted) {
    Write-Host "📝 Arquivos não commitados encontrados:" -ForegroundColor Yellow
    Write-Host $uncommitted -ForegroundColor Gray
    Write-Host ""
    $commit = Read-Host "Deseja fazer commit agora? (s/n)"
    if ($commit -eq "s" -or $commit -eq "S") {
        git add .
        $message = Read-Host "Mensagem do commit (ou Enter para usar padrão)"
        if ([string]::IsNullOrWhiteSpace($message)) {
            $message = "Preparar para deploy na nuvem"
        }
        git commit -m $message
        Write-Host "✅ Commit realizado" -ForegroundColor Green
    }
} else {
    Write-Host "✅ Todos os arquivos estão commitados" -ForegroundColor Green
}

# Verificar remote
Write-Host ""
Write-Host "[3/5] Verificando repositório remoto..." -ForegroundColor Yellow
$remotes = git remote -v
if ([string]::IsNullOrWhiteSpace($remotes)) {
    Write-Host "⚠️  Nenhum repositório remoto configurado" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para fazer deploy na nuvem, você precisa:" -ForegroundColor Cyan
    Write-Host "1. Criar um repositório no GitHub" -ForegroundColor White
    Write-Host "2. Adicionar o remote:" -ForegroundColor White
    Write-Host "   git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git" -ForegroundColor Gray
    Write-Host "3. Fazer push:" -ForegroundColor White
    Write-Host "   git push -u origin main" -ForegroundColor Gray
    Write-Host ""
    $addRemote = Read-Host "Deseja adicionar um remote agora? (s/n)"
    if ($addRemote -eq "s" -or $addRemote -eq "S") {
        $remoteUrl = Read-Host "Cole a URL do repositório GitHub"
        if (-not [string]::IsNullOrWhiteSpace($remoteUrl)) {
            git remote add origin $remoteUrl
            Write-Host "✅ Remote adicionado" -ForegroundColor Green
            $push = Read-Host "Deseja fazer push agora? (s/n)"
            if ($push -eq "s" -or $push -eq "S") {
                git push -u origin main
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ Push realizado com sucesso!" -ForegroundColor Green
                }
            }
        }
    }
} else {
    Write-Host "✅ Repositório remoto configurado:" -ForegroundColor Green
    Write-Host $remotes -ForegroundColor Gray
    $push = Read-Host "Deseja fazer push agora? (s/n)"
    if ($push -eq "s" -or $push -eq "S") {
        git push
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Push realizado com sucesso!" -ForegroundColor Green
        }
    }
}

# Verificar .env
Write-Host ""
Write-Host "[4/5] Verificando arquivo .env..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ Arquivo .env encontrado" -ForegroundColor Green
    Write-Host "⚠️  IMPORTANTE: Você precisará adicionar essas variáveis no Railway/Render" -ForegroundColor Yellow
} else {
    Write-Host "⚠️  Arquivo .env não encontrado" -ForegroundColor Yellow
    Write-Host "Criando template .env.example..." -ForegroundColor Gray
    $envTemplate = @"
# Discord
DISCORD_TOKEN=seu_token_aqui

# Database
DATABASE_HOST=seu_host
DATABASE_USER=seu_usuario
DATABASE_PASSWORD=sua_senha
DATABASE_NAME=seu_banco

# Roblox
ROBLOX_COOKIE=seu_cookie

# Guild
GUILD_ID=seu_guild_id
"@
    $envTemplate | Out-File -FilePath ".env.example" -Encoding UTF8
    Write-Host "Template criado (.env.example)" -ForegroundColor Green
}

# Criar checklist
Write-Host ""
Write-Host "[5/5] Criando checklist de deploy..." -ForegroundColor Yellow
$checklistContent = "# Checklist de Deploy - IgnisBot`n`n## Antes de começar:`n- Código commitado e no GitHub`n- Arquivo .env com todas as variáveis`n`n## Deploy no Railway (Recomendado):`n`n1. Acesse https://railway.app`n2. Faça login com GitHub`n3. Clique em New Project`n4. Selecione Deploy from GitHub repo`n5. Escolha seu repositório`n6. Vá em Variables e adicione TODAS as variáveis do .env`n7. Aguarde o deploy (alguns minutos)`n8. Verifique os logs`n9. Teste o bot no Discord com /health`n`n## Verificar se está funcionando:`n- Bot responde no Discord`n- Comando /health funciona`n- Logs não mostram erros`n`n## Pronto!"
$checklistContent | Out-File -FilePath "CHECKLIST_DEPLOY.md" -Encoding UTF8
Write-Host "Checklist criado (CHECKLIST_DEPLOY.md)" -ForegroundColor Green

Write-Host ""
Write-Host "=== Preparação Concluída ===" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Cyan
Write-Host "1. Se ainda não fez, faça push para o GitHub" -ForegroundColor White
Write-Host "2. Acesse https://railway.app e crie um projeto" -ForegroundColor White
Write-Host "3. Conecte seu repositório GitHub" -ForegroundColor White
Write-Host "4. Adicione todas as variáveis de ambiente" -ForegroundColor White
Write-Host "5. Aguarde o deploy automático" -ForegroundColor White
Write-Host ""
Write-Host "📖 Veja CHECKLIST_DEPLOY.md para o checklist completo" -ForegroundColor Yellow
Write-Host ""

