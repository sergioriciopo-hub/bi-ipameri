'' Para o BI Ipameri (encerra o processo python/streamlit na porta 8501)

Dim oShell
Set oShell = CreateObject("WScript.Shell")

'' Mata todos os processos python que estejam rodando o streamlit
oShell.Run "cmd /c taskkill /f /im python.exe /fi ""WINDOWTITLE eq streamlit*"" 2>nul", 0, True

'' Fallback: mata pela porta 8501
oShell.Run "cmd /c FOR /F ""tokens=5"" %a IN ('netstat -aon ^| find "":8501""') DO taskkill /f /PID %a 2>nul", 0, True

MsgBox "BI Ipameri encerrado.", 64, "BI Ipameri"
