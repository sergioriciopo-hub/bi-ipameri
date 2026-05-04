# Script de Publicação Automatizada - BI Ipameri
# Automatiza: git add → git commit → git push

param(
    [string]$message = ""
)

$ErrorActionPreference = "Stop"

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  📤 Publicando alterações (Local + Online)" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Mudar para o diretório do projeto
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectDir = Split-Path -Parent $scriptDir
Set-Location $projectDir

# 1. Verificar status
Write-Host "1️⃣  Verificando alterações..." -ForegroundColor Yellow
git status
Write-Host ""

# 2. Adicionar arquivos
Write-Host "2️⃣  Adicionando arquivos modificados..." -ForegroundColor Yellow
git add app.py scripts/*.py scripts/*.ps1 scripts/*.bat 2>$null
Write-Host ""

# 3. Obter mensagem de commit
if ([string]::IsNullOrEmpty($message)) {
    Write-Host "3️⃣  Digite sua mensagem de commit:" -ForegroundColor Yellow
    $message = Read-Host "Mensagem"
}

if ([string]::IsNullOrEmpty($message)) {
    Write-Host "❌ Nenhuma mensagem de commit fornecida. Abortando..." -ForegroundColor Red
    exit 1
}

# 4. Fazer commit
Write-Host ""
Write-Host "4️⃣  Realizando commit..." -ForegroundColor Yellow
$commitMsg = @"
$message

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
"@

try {
    git commit -m $commitMsg
} catch {
    Write-Host "⚠️  Nenhuma alteração para fazer commit" -ForegroundColor Yellow
    exit 0
}

# 5. Fazer push
Write-Host ""
Write-Host "5️⃣  Enviando para o GitHub (online)..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✅ Publicação concluída com sucesso!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Dashboard atualizada em: https://bi-ipameri.streamlit.app/" -ForegroundColor Cyan
