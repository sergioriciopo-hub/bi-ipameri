@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM ETL - Águas de Ipameri | BigQuery → Parquet (Task Scheduler)
REM Agendar: Task Scheduler diário às 06:00 AM
REM ═══════════════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

REM Diretório do projeto
cd /d "C:\Users\SérgioRiciopo\AGUAS DE IPAMERI\03 COMERCIAL - Documentos\01 - Projetos e Propostas\Claude\BI_Ipameri"

REM Executar script Python
python scripts\etl_bigquery.py

REM Capturar exit code
set EXIT_CODE=%errorlevel%

REM Log da execução
echo.
echo ============================================================
if %EXIT_CODE% equ 0 (
    echo [OK] ETL executado com sucesso em %date% %time%
) else (
    echo [ERRO] ETL falhou com código: %EXIT_CODE%
)
echo ============================================================

exit /b %EXIT_CODE%
