'' Inicia o BI Ipameri em background — processo independente do terminal
'' Fechar esta janela NÃO encerra o Streamlit
'' Para parar: usar parar_bi.vbs ou Task Manager (python.exe)

Dim oShell
Set oShell = CreateObject("WScript.Shell")

'' Caminho curto evita problema com acento no usuário (SRGIOR~1)
Dim python
python = "C:\Users\SRGIOR~1\AppData\Local\Programs\Python\PYTHON~1\python.exe"

Dim cmd
cmd = """" & python & """ -m streamlit run ""C:\BI_Ipameri\app.py"" --server.headless true --server.port 8501"

'' intWindowStyle=0 = janela oculta | bWaitOnReturn=False = não aguarda
oShell.Run cmd, 0, False

'' Aguarda 3s e abre o browser
WScript.Sleep 3000
oShell.Run "http://localhost:8501", 1, False

MsgBox "BI Águas de Ipameri iniciado!" & vbCrLf & "Acesse: http://localhost:8501" & vbCrLf & vbCrLf & "Para encerrar: execute parar_bi.vbs", 64, "BI Ipameri"
