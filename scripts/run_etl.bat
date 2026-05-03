@echo off
REM ── Agendador diário – Águas de Ipameri ETL ──────────────────────────────
REM Agendar no Task Scheduler:
REM   Programa : C:\Users\SérgioRiciopo\AGUAS DE IPAMERI\03 COMERCIAL - Documentos\01 - Projetos e Propostas\Claude\BI_Ipameri\scripts\run_etl.bat
REM   Horário  : 06:00 diariamente

cd /d "%~dp0"
echo [%date% %time%] Iniciando ETL Ipameri...
python etl_bigquery.py
echo [%date% %time%] ETL finalizado.
