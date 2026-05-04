# Deploy Online - Streamlit Cloud

## Opção 1: Streamlit Cloud (Recomendado - Gratuito)

### Pré-requisitos
- Conta GitHub com repositório contendo o projeto
- Conta Streamlit Cloud (gratuita em https://streamlit.io/cloud)

### Passos

#### 1. Preparar repositório GitHub
```bash
# Commits estão em dia
git add .
git commit -m "Setup para deploy online"
git push origin main
```

#### 2. Criar conta Streamlit Cloud
- Acesse https://streamlit.io/cloud
- Clique "Sign up" ou "Sign in with GitHub"
- Autorize acesso ao repositório

#### 3. Deploy
1. Na dashboard Streamlit Cloud, clique "New app"
2. Selecione:
   - Repository: `AGUAS-DE-IPAMERI.../BI_Ipameri` (ou seu repo)
   - Branch: `main`
   - Main file path: `app.py`
3. Clique "Deploy"

#### 4. Configuração (Opcional)
- Adicione secrets (se houver credenciais)
- Configure variáveis de ambiente
- Defina quantidade de workers

**Resultado:** App fica em `https://[seu-username]-bi-ipameri.streamlit.app`

---

## Opção 2: Render (Alternativa Gratuita)

### Setup
1. Criar arquivo `render.yaml` na raiz do projeto
2. Conectar repositório GitHub
3. Deploy automático

Vantagens:
- Sem limite de tempo (Streamlit Cloud dorme apps inativos)
- Suporta cron jobs

---

## Opção 3: Heroku (Descontinuado)

Heroku encerrou plano gratuito em Nov/2022. Considere Render ou Railway.

---

## Opção 4: Railway (Recomendado se Render não funcionar)

1. Crie conta em https://railway.app
2. Conecte repositório GitHub
3. Configure:
   - Build: Python
   - Start: `streamlit run app.py --server.port=8080`

---

## Arquivo de Requisitos

O arquivo `requirements.txt` já está configurado com todas as dependências:
- streamlit
- pandas
- plotly
- pyarrow
- openpyxl
- python-dateutil
- requests

---

## Acessar App Online

Após deploy, acesse:

**Streamlit Cloud:**
```
https://[seu-username]-bi-ipameri.streamlit.app
```

**Render:**
```
https://bi-ipameri.onrender.com (ou nome customizado)
```

---

## Secrets e Configurações

Se o app precisar de credenciais (API keys, senhas), use:

### Streamlit Cloud
1. Dashboard → App settings → Secrets
2. Adicione em formato YAML:
```yaml
[connections.sql]
dialect = "postgresql"
host = "localhost"
port = 5432
```

### Arquivo local (.streamlit/secrets.toml)
```toml
[database]
host = "localhost"
user = "admin"
password = "senha"
```

⚠️ **NÃO commite secrets.toml no GitHub!**

---

## Monitoramento

### Logs
- Streamlit Cloud: Dashboard → App → Logs
- Render: Dashboard → Logs

### Performance
- Monitore uso de memória
- Ajuste workers se necessário
- Optimize cache (@st.cache_data)

---

## Troubleshooting

### Erro: "ModuleNotFoundError"
- Verifique requirements.txt
- Certifique-se de que todas as dependências estão listadas

### App lento online
- Aumente cache TTL
- Optimize queries SQL/parquet
- Use st.spinner para operações longas

### Não consegue conectar ao banco de dados
- Use variáveis de ambiente (secrets)
- Verifique IP whitelist no banco de dados
- Teste conexão localmente primeiro

---

## Scripts de Deploy (Automático)

### GitHub Actions (CI/CD automático)
Crie `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Streamlit Cloud
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: streamlit run app.py --logger.level=error
```

---

## URL Final para Compartilhar

Após deploy, compartilhe:

```
https://[seu-app].streamlit.app

Acesso: Menu > Cockpits > Energia Eletrica
```

---

**Dúvidas?** Veja documentação oficial:
- Streamlit Cloud: https://docs.streamlit.io/streamlit-cloud
- Render: https://render.com/docs
- Railway: https://railway.app/docs
