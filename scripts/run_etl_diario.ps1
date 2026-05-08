# ETL Diario Completo - BigQuery + Frota Combustivel
# Agendado para: todos os dias as 07:30

$projectDir = "C:\BI_Ipameri"
$logDir     = Join-Path $projectDir "scripts\logs"
$logFile    = Join-Path $logDir ("etl_diario_" + (Get-Date -Format "yyyyMMdd_HHmm") + ".log")

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
}

function Log($msg) {
    $line = "[$(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')] $msg"
    Add-Content $logFile $line
    Write-Host $line
}

Log "======================================================"
Log "INICIO ETL DIARIO - Aguas de Ipameri"
Log "======================================================"

Set-Location $projectDir
$erros = 0

# ── 1. ETL BigQuery (todos os parquets) ───────────────────────────────────────
Log "Iniciando ETL BigQuery..."
try {
    $output = python "scripts\etl_bigquery.py" 2>&1
    Add-Content $logFile ($output | Out-String)
    Log "ETL BigQuery concluido com SUCESSO"
} catch {
    Log "ERRO no ETL BigQuery: $_"
    $erros++
}

# ── 2. ETL Frota Combustivel ──────────────────────────────────────────────────
Log "Iniciando ETL Frota..."
try {
    $output = python "scripts\etl_frota_combustivel.py" 2>&1
    Add-Content $logFile ($output | Out-String)
    Log "ETL Frota concluido com SUCESSO"
} catch {
    Log "ERRO no ETL Frota: $_"
    $erros++
}

# ── 3. Publicar no GitHub → Streamlit Cloud ──────────────────────────────────
Log "Publicando no GitHub (Streamlit Cloud)..."
$today = Get-Date -Format "dd/MM/yyyy"

try {
    # Adicionar todos os parquets rastreados (modificados pelo ETL)
    & git add "data/" 2>&1 | Out-Null
    # Adicionar scripts se houver alteracoes (ex: etl_bigquery.py atualizado)
    & git add "scripts/" 2>&1 | Out-Null

    $commitMsg = & git commit -m "Dados atualizados - $today [auto]" 2>&1

    if ($LASTEXITCODE -eq 0 -and $commitMsg -notmatch "nothing to commit") {
        Add-Content $logFile ($commitMsg | Out-String)
        $pushOut = & git push origin main 2>&1
        Add-Content $logFile ($pushOut | Out-String)
        Log "Publicado no GitHub com SUCESSO - Streamlit Cloud atualizara em ~2 min"
    } else {
        Log "Sem alteracoes para publicar"
    }
} catch {
    Log "ERRO na publicacao GitHub: $_"
    $erros++
}

# ── Resultado final ───────────────────────────────────────────────────────────
Log "======================================================"
if ($erros -eq 0) {
    Log "ETL DIARIO CONCLUIDO COM SUCESSO"
    exit 0
} else {
    Log "ETL DIARIO CONCLUIDO COM $erros ERRO(S) - verificar log"
    exit 1
}
