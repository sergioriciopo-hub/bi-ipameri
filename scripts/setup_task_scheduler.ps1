# ═══════════════════════════════════════════════════════════════════════════
# Setup Task Scheduler - ETL Águas de Ipameri
# Executar como Administrador
# ═══════════════════════════════════════════════════════════════════════════

$taskName = "ETL-BigQuery-Ipameri"
$taskFolder = "Águas de Ipameri"
$scriptPath = "C:\Users\SérgioRiciopo\AGUAS DE IPAMERI\03 COMERCIAL - Documentos\01 - Projetos e Propostas\Claude\BI_Ipameri\scripts\run_etl.bat"
$time = "06:00"

Write-Host "═════════════════════════════════════════════════════════════"
Write-Host "Configurando Task Scheduler para ETL"
Write-Host "═════════════════════════════════════════════════════════════"
Write-Host ""

# Verificar se a tarefa já existe
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "[!] Tarefa existente encontrada. Removendo..."
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
    Start-Sleep -Seconds 2
}

# Criar trigger (diariamente às 06:00)
$trigger = New-ScheduledTaskTrigger -Daily -At $time

# Criar ação
$action = New-ScheduledTaskAction -Execute $scriptPath

# Configurações
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -WakeToRun `
    -RunOnlyIfNetworkAvailable `
    -StartWhenAvailable

# Registrar tarefa
Write-Host "[*] Criando tarefa: $taskName"
Write-Host "    Pasta: $taskFolder"
Write-Host "    Script: $scriptPath"
Write-Host "    Horário: $time (diariamente)"
Write-Host ""

try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -TaskPath "\$taskFolder\" `
        -Trigger $trigger `
        -Action $action `
        -Settings $settings `
        -RunLevel Highest `
        -Force | Out-Null
    
    Write-Host "[OK] Tarefa criada com sucesso!"
    Write-Host ""
    Write-Host "Detalhes:"
    Get-ScheduledTask -TaskName $taskName | Format-List
}
catch {
    Write-Host "[ERRO] Falha ao criar tarefa:"
    Write-Host $_.Exception.Message
}

Write-Host ""
Write-Host "═════════════════════════════════════════════════════════════"
Write-Host "Setup completo!"
Write-Host "═════════════════════════════════════════════════════════════"
