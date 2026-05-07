# ETL Frota Combustivel - Execucao Diaria + Publicacao GitHub
# Agendado para: todos os dias as 06:00

$projectDir = "C:\Users\SérgioRiciopo\AGUAS DE IPAMERI\03 COMERCIAL - Documentos\01 - Projetos e Propostas\Claude\BI_Ipameri"
$logDir = Join-Path $projectDir "scripts\logs"
$logFile = Join-Path $logDir ("etl_frota_" + (Get-Date -Format "yyyyMMdd_HHmm") + ".log")

if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Force -Path $logDir | Out-Null
}

Add-Content $logFile "[$(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')] Iniciando ETL de Frota..."

try {
    Set-Location $projectDir

    # 1. Executar ETL
    $output = python "scripts\etl_frota_combustivel.py" 2>&1
    Add-Content $logFile ($output | Out-String)

    Add-Content $logFile "[$(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')] ETL concluido com SUCESSO"

    # 2. Git add + commit + push
    Add-Content $logFile "[$(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')] Publicando no GitHub..."
    $today = Get-Date -Format "dd/MM/yyyy"

    $null = & git add "data/frota_combustivel.parquet" "data/dim_veiculo_frota.parquet" 2>$null
    $commitMsg = & git commit -m "Atualizar dados frota combustivel - $today" 2>&1

    if ($commitMsg -match "nothing to commit") {
        Add-Content $logFile "[$(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')] Sem alteracoes nos dados - push nao necessario"
    } else {
        Add-Content $logFile ($commitMsg | Out-String)
        $null = & git push origin main 2>$null
        Add-Content $logFile "[$(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')] Publicado no GitHub com SUCESSO"
    }

    exit 0
} catch {
    Add-Content $logFile "[$(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')] ERRO: $_"
    exit 1
}