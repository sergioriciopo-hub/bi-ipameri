# 📤 Guia de Publicação - BI Ipameri

## Descrição

Scripts automatizados para publicar alterações tanto **localmente** quanto **online** (GitHub + Streamlit Cloud).

## Scripts Disponíveis

### 1. **PowerShell** (Recomendado para Windows)

```powershell
# Sem parâmetro (interativo):
./scripts/publish.ps1

# Com mensagem pré-definida:
./scripts/publish.ps1 -message "Sua mensagem de commit aqui"
```

**Exemplo:**
```powershell
./scripts/publish.ps1 -message "Melhorar layout do cockpit Faturamento"
```

### 2. **Bash** (Para Terminal/Git Bash)

```bash
bash scripts/publish.sh
```

## O que o Script Faz?

```
1️⃣  Verifica alterações (git status)
2️⃣  Adiciona arquivos modificados (git add)
3️⃣  Solicita mensagem de commit
4️⃣  Realiza commit local
5️⃣  Envia para GitHub (git push)
6️⃣  Streamlit Cloud faz auto-deploy
```

## Fluxo Rápido

### PowerShell (Recomendado)
```powershell
cd "C:\Users\SérgioRiciopo\AGUAS DE IPAMERI\03 COMERCIAL - Documentos\01 - Projetos e Propostas\Claude\BI_Ipameri"
./scripts/publish.ps1
```

### Git Bash
```bash
cd "/c/Users/SérgioRiciopo/AGUAS DE IPAMERI/03 COMERCIAL - Documentos/01 - Projetos e Propostas/Claude/BI_Ipameri"
bash scripts/publish.sh
```

## Automatizando com Alias (Opcional)

### PowerShell

Adicione ao seu perfil PowerShell (`$PROFILE`):
```powershell
function Publicar {
    param([string]$msg = "")
    & "C:\Users\SérgioRiciopo\AGUAS DE IPAMERI\03 COMERCIAL - Documentos\01 - Projetos e Propostas\Claude\BI_Ipameri\scripts\publish.ps1" -message $msg
}
```

Depois use:
```powershell
Publicar "Sua mensagem"
# ou apenas
Publicar  # modo interativo
```

### Bash

Adicione ao `.bashrc` ou `.bash_profile`:
```bash
alias publicar='bash ~/path/to/scripts/publish.sh'
```

Depois use:
```bash
publicar
```

## Formato da Mensagem de Commit

As mensagens devem seguir este padrão:

```
Descrição breve do que foi feito

- Ponto específico 1
- Ponto específico 2
- Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

**Exemplo:**
```
Melhorar distribuição de KPIs no cockpit

- Faturamento: de 3+1 para 2-2 (layout mais equilibrado)
- Arrecadação: de 4+1 para 2-2-2 (proporção melhor)
- Resultado: elemento sem sobreposição

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

## Fluxo de Trabalho Recomendado

```
1. Fazer alterações no código
2. Testar localmente (st.run, navegador, etc)
3. Executar: ./scripts/publish.ps1
4. Digitar mensagem descrevendo as mudanças
5. Aguardar 30-60s para Streamlit Cloud fazer deploy
6. Verificar: https://bi-ipameri.streamlit.app/
```

## Solução de Problemas

### "Permission denied"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Git não reconhecido
- Instale Git: https://git-scm.com/download/win
- Reinicie o terminal

### Erro ao fazer push
- Verifique conexão com internet
- Verifique credenciais Git (git config user.name/email)
- Tente: `git push origin main` manualmente para ver erro específico

## Verificação

Para verificar o status de publicação:
```bash
git log -1 --oneline    # Último commit
git status              # Status atual
git remote -v           # Verificar GitHub
```

---

**Dashboard ao vivo:** https://bi-ipameri.streamlit.app/
