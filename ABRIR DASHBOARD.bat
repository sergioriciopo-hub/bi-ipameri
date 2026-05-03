@echo off
title Dashboard - Aguas de Ipameri
cd /d "%~dp0"
echo.
echo  =========================================
echo   Dashboard - Aguas de Ipameri
echo  =========================================
echo.
echo  Iniciando servidor...
echo  O navegador abrira automaticamente em:
echo  http://localhost:8501
echo.
echo  Para fechar: pressione Ctrl+C nesta janela.
echo  =========================================
echo.
streamlit run app.py
pause
