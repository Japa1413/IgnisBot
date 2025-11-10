# Script para gerar variaveis de ambiente formatadas para Railway
# Este script le o .env e cria um arquivo formatado para facil copia

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=== Gerador de Variaveis para Railway ===" -ForegroundColor Cyan
Write-Host ""

# Verificar se .env existe
if (-not (Test-Path ".env")) {
    Write-Host "ERRO: Arquivo .env nao encontrado!" -ForegroundColor Red
    Write-Host "Por favor, crie o arquivo .env primeiro." -ForegroundColor Yellow
    exit 1
}

Write-Host "Lendo arquivo .env..." -ForegroundColor Yellow

# Ler arquivo .env
$lines = Get-Content ".env" -Encoding UTF8

# Processar variaveis
$variables = @{}
$outputLines = @()

foreach ($line in $lines) {
    # Ignorar linhas vazias e comentarios
    $trimmed = $line.Trim()
    if ([string]::IsNullOrWhiteSpace($trimmed) -or $trimmed.StartsWith("#")) {
        continue
    }
    
    # Separar chave e valor
    if ($trimmed -match '^([^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        
        # Remover aspas se existirem
        if ($value.StartsWith('"') -and $value.EndsWith('"')) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        if ($value.StartsWith("'") -and $value.EndsWith("'")) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        
        $variables[$key] = $value
        $outputLines += "$key=$value"
    }
}

# Salvar em arquivo formato Railway (KEY=VALUE)
$outputFile = "RAILWAY_VARIABLES.txt"
$outputLines -join "`n" | Out-File -FilePath $outputFile -Encoding UTF8 -NoNewline

Write-Host "Arquivo criado: $outputFile" -ForegroundColor Green
Write-Host ""
Write-Host "Total de variaveis encontradas: $($variables.Count)" -ForegroundColor Cyan
Write-Host ""

# Mostrar variaveis (sem valores sensiveis)
Write-Host "Variaveis encontradas:" -ForegroundColor Yellow
foreach ($key in $variables.Keys | Sort-Object) {
    $value = $variables[$key]
    $displayValue = if ($value.Length -gt 30) { $value.Substring(0, 30) + "..." } else { $value }
    Write-Host "  - $key" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== INSTRUCOES PARA RAILWAY ===" -ForegroundColor Green
Write-Host ""
Write-Host "1. Abra o arquivo: $outputFile" -ForegroundColor White
Write-Host "2. Copie TODO o conteudo" -ForegroundColor White
Write-Host "3. No Railway:" -ForegroundColor White
Write-Host "   a. Va em seu projeto" -ForegroundColor Gray
Write-Host "   b. Clique em 'Settings'" -ForegroundColor Gray
Write-Host "   c. Clique em 'Variables'" -ForegroundColor Gray
Write-Host "   d. Clique em 'Raw Editor' (canto superior direito)" -ForegroundColor Gray
Write-Host "   e. Cole o conteudo do arquivo" -ForegroundColor Gray
Write-Host "   f. Clique em 'Save'" -ForegroundColor Gray
Write-Host ""
Write-Host "OU adicione manualmente uma por uma clicando em 'New Variable'" -ForegroundColor Yellow
Write-Host ""
