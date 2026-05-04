# Diagnóstico do Problema de Deployment

**Data:** 2026-05-04  
**Status:** Investigando problema de acesso no Streamlit Cloud

---

## Problema Identificado

App publicado em https://bi-ipameri.streamlit.app/ não está acessível.

---

## Soluções Aplicadas

### 1. Arquivos de Dados
**Problema:** Dados de energia não estavam no repositório GitHub
**Solução:** Adicionados ao Git:
- `data/energia_consolidada_completa.parquet`
- `data/dim_unidade_consumo_energia.parquet`

### 2. Configuração Streamlit
**Problema:** `.streamlit/config.toml` tinha configurações incompatíveis com Streamlit Cloud
**Solução:** Corrigido:
- Removido `serverAddress = "localhost"` (não funciona em servidor remoto)
- Removido `port = 8501` (Streamlit Cloud define automaticamente)
- Removido `runOnSave = true` (pode causar erros)
- Adicionado `showErrorDetails = true` (para diagnóstico)

---

## O Que Fazer Agora

### Passo 1: Aguardar Redeploy
Streamlit Cloud detectou as mudanças. Aguarde 5-10 minutos para:
1. Detectar novo commit
2. Iniciar build
3. Deploy da aplicação

### Passo 2: Testar Acesso
Tente acessar:
```
https://bi-ipameri.streamlit.app/
```

### Passo 3: Se Ainda Não Funcionar

**Opção A: Verificar Logs**
1. Acesse https://share.streamlit.io/admin
2. Clique no app "bi-ipameri"
3. Vá em "Logs"
4. Procure por erros (ERRO em vermelho)

**Opção B: Verificar Status**
1. Dashboard Streamlit Cloud
2. Procure por app "bi-ipameri"
3. Verifique status (deve estar "Deployed")

**Opção C: Forçar Redeploy**
1. Acesse Streamlit Cloud dashboard
2. Clique no app
3. Menu (3 pontos) → Reboot app

---

## Testes Locais (Validação)

### Teste 1: App Simples
```bash
streamlit run app_test.py
```
Se funcionar localmente, problema é especifico do Streamlit Cloud.

### Teste 2: App Completo
```bash
streamlit run app.py
```
Se carregar sem erros, o código está OK.

### Teste 3: Dados
```bash
python << 'EOF'
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data")
ene = pd.read_parquet(DATA_DIR / "energia_consolidada_completa.parquet")
print(f"Registros: {len(ene)}")
print(f"Colunas: {ene.columns.tolist()}")
EOF
```
Se exibir 247 registros, dados estão OK.

---

## Checklist de Diagnóstico

- [ ] Verificou se commit foi pusheado (git log)
- [ ] Esperou 10 minutos para Streamlit Cloud processar
- [ ] Acessou https://bi-ipameri.streamlit.app/
- [ ] Recarregou página (Ctrl+F5)
- [ ] Verificou logs em Streamlit Cloud
- [ ] Testou app_test.py localmente
- [ ] Testou app.py localmente
- [ ] Verificou se dados existem localmente

---

## Próximos Passos

Se ainda não funcionar:

1. **Verificar GitHub**
   ```bash
   git log --oneline -5
   ```
   Deve ver últimos commits

2. **Verificar Arquivos**
   ```bash
   ls -lh data/energia*.parquet
   ```
   Deve exibir ambos os arquivos

3. **Testar Sintaxe**
   ```bash
   python -m py_compile app.py
   ```
   Não deve retornar erros

4. **Verificar Requirements**
   - Todos os pacotes em `requirements.txt` estão instalados?
   - Versões compatíveis?

---

## Possíveis Causas

1. **Configuração Streamlit** ← CORRIGIDO
2. **Dados não no repositório** ← CORRIGIDO  
3. **Erro no app.py** ← Testado localmente, OK
4. **Dependências faltando** → Verificar requirements.txt
5. **Problema no Streamlit Cloud** → Contatar suporte

---

## Links Úteis

- **App:** https://bi-ipameri.streamlit.app/
- **GitHub:** https://github.com/sergioriciopo-hub/bi-ipameri
- **Dashboard:** https://share.streamlit.io/admin
- **Docs:** https://docs.streamlit.io/streamlit-cloud

---

**Próxima atualização:** 2026-05-04 T+15min
