@echo off
REM ── Criação de Tarefa Agendada – Águas de Ipameri ETL ─────────────────────
REM Execute este arquivo como ADMINISTRADOR uma única vez

set SCRIPT_PATH=C:\Users\SérgioRiciopo\AGUAS DE IPAMERI\03 COMERCIAL - Documentos\01 - Projetos e Propostas\Claude\BI_Ipameri\scripts\run_etl.bat

echo Criando tarefa agendada "ETL_Ipameri_BI"...

schtasks /create /tn "ETL_Ipameri_BI" ^
  /tr "\"%SCRIPT_PATH%\"" ^
  /sc DAILY ^
  /st 06:00 ^
  /ru "%USERNAME%" ^
  /rl HIGHEST ^
  /f

if %errorlevel% == 0 (
    echo.
    echo Tarefa criada com sucesso!
    echo  - Nome: ETL_Ipameri_BI
    echo  - Horario: 06:00 diariamente
    echo  - Script: %SCRIPT_PATH%
    echo.
    echo Verifique em: Agendador de Tarefas ^> Biblioteca do Agendador de Tarefas
) else (
    echo ERRO ao criar a tarefa. Execute como Administrador.
)

pause
