# Script de Verificação de Manutenção - IgnisBot (PowerShell)
# Executa verificações de saúde e manutenção

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "VERIFICAÇÃO DE MANUTENÇÃO - IGNISBOT" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$Passed = 0
$Failed = 0
$Warnings = 0

# Função para verificar comando
function Test-Command {
    param($Command)
    if (Get-Command $Command -ErrorAction SilentlyContinue) {
        Write-Host "✅ $Command encontrado" -ForegroundColor Green
        $script:Passed++
        return $true
    } else {
        Write-Host "❌ $Command não encontrado" -ForegroundColor Red
        $script:Failed++
        return $false
    }
}

# Verificar comandos
Write-Host "Verificando comandos necessários..."
Test-Command "python"
Test-Command "pip"
Test-Command "git"

# Verificar Safety
Write-Host ""
Write-Host "--- Verificando Vulnerabilidades (Safety) ---" -ForegroundColor Yellow
if (Get-Command safety -ErrorAction SilentlyContinue) {
    $safetyOutput = safety check --json 2>&1 | ConvertFrom-Json
    if ($safetyOutput.vulnerabilities.Count -eq 0) {
        Write-Host "✅ Nenhuma vulnerabilidade encontrada" -ForegroundColor Green
        $Passed++
    } else {
        Write-Host "⚠️ Vulnerabilidades encontradas:" -ForegroundColor Yellow
        safety check
        $Warnings++
    }
} else {
    Write-Host "⚠️ Safety não instalado (pip install safety)" -ForegroundColor Yellow
    $Warnings++
}

# Verificar dependências desatualizadas
Write-Host ""
Write-Host "--- Verificando Dependências Desatualizadas ---" -ForegroundColor Yellow
$outdated = pip list --outdated 2>&1
if ($outdated -match "Package") {
    Write-Host "⚠️ Dependências desatualizadas encontradas:" -ForegroundColor Yellow
    pip list --outdated
    $Warnings++
} else {
    Write-Host "✅ Todas as dependências estão atualizadas" -ForegroundColor Green
    $Passed++
}

# Verificar testes
Write-Host ""
Write-Host "--- Verificando Testes ---" -ForegroundColor Yellow
if (Get-Command pytest -ErrorAction SilentlyContinue) {
    try {
        pytest tests/ -v --tb=short 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Todos os testes passando" -ForegroundColor Green
            $Passed++
        } else {
            Write-Host "❌ Alguns testes falharam" -ForegroundColor Red
            $Failed++
        }
    } catch {
        Write-Host "⚠️ Erro ao executar testes" -ForegroundColor Yellow
        $Warnings++
    }
} else {
    Write-Host "⚠️ pytest não instalado" -ForegroundColor Yellow
    $Warnings++
}

# Resumo
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "RESUMO" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "✅ Passou: $Passed" -ForegroundColor Green
Write-Host "❌ Falhou: $Failed" -ForegroundColor Red
Write-Host "⚠️ Avisos: $Warnings" -ForegroundColor Yellow
Write-Host ""

if ($Failed -eq 0) {
    Write-Host "✅ Sistema saudável!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "❌ Problemas encontrados. Verifique acima." -ForegroundColor Red
    exit 1
}

