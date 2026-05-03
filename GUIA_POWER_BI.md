# Águas de Ipameri — Guia Power BI

## 1. Estrutura dos Arquivos

```
BI_Ipameri/
├── data/                        ← Parquet gerados pelo ETL (22 arquivos, ~9 MB)
│   ├── faturamento.parquet
│   ├── arrecadacao.parquet
│   ├── painel_arrecadacao.parquet
│   ├── pendencia_atual.parquet
│   ├── cortes.parquet
│   ├── religacoes.parquet
│   ├── servicos.parquet
│   ├── leituras.parquet
│   ├── backlog_servicos.parquet
│   └── dim_*.parquet            ← 13 tabelas dimensão
├── scripts/
│   ├── etl_bigquery.py          ← ETL principal
│   ├── run_etl.bat              ← Atalho para rodar o ETL
│   ├── agendar_task_scheduler.bat  ← Cria tarefa diária automática
│   ├── power_bi_queries_M.pq   ← Queries M para Power Query
│   └── power_bi_DAX_medidas.dax ← Medidas DAX
└── GUIA_POWER_BI.md             ← Este arquivo
```

---

## 2. Configuração no Power BI Desktop

### 2.1 Criar Parâmetro BASE_PATH

1. Power BI Desktop → **Transformar Dados** → **Gerenciar Parâmetros** → **Novo Parâmetro**
2. Preencher:
   - Nome: `BASE_PATH`
   - Tipo: **Texto**
   - Valor atual: `C:\Users\SérgioRiciopo\AGUAS DE IPAMERI\03 COMERCIAL - Documentos\01 - Projetos e Propostas\Claude\BI_Ipameri\data\`

### 2.2 Carregar cada tabela (Parquet)

Para cada tabela abaixo:
1. **Obter Dados** → **Arquivo Parquet**
2. Selecionar o arquivo `.parquet` em `data/`
3. No Power Query → **Editor Avançado** → colar a query M correspondente do arquivo `power_bi_queries_M.pq`

| Nome da Tabela no PBI | Arquivo Parquet |
|---|---|
| Faturamento | faturamento.parquet |
| Arrecadacao | arrecadacao.parquet |
| PainelArrecadacao | painel_arrecadacao.parquet |
| Inadimplencia | pendencia_atual.parquet |
| Cortes | cortes.parquet |
| Religacoes | religacoes.parquet |
| Servicos | servicos.parquet |
| Leituras | leituras.parquet |
| Backlog | backlog_servicos.parquet |
| DimBairro | dim_bairro.parquet |
| DimGrupo | dim_grupo.parquet |
| DimCategoria | dim_categoria.parquet |
| DimClasse | dim_classe.parquet |
| DimEquipe | dim_equipe.parquet |
| DimSetor | dim_setor_operacional.parquet |
| DimFormaPagamento | dim_forma_arrecadacao.parquet |
| DimLeiturista | dim_leiturista.parquet |
| DimServico | dim_servico_definicao.parquet |

### 2.3 Criar Tabela Calendário

1. **Transformar Dados** → **Nova Consulta** → **Consulta em Branco**
2. Nome: `Calendario`
3. **Editor Avançado** → colar a query da seção "TABELA CALENDÁRIO" do arquivo `power_bi_queries_M.pq`

### 2.4 Criar Tabela de Medidas

1. **Modelagem** → **Nova Tabela** → nomear como `Medidas` → inserir fórmula: `Medidas = ROW("x", 1)`
2. Adicionar cada medida do arquivo `power_bi_DAX_medidas.dax` via **Nova Medida**

---

## 3. Relacionamentos (Modelo Estrela)

Criar relacionamentos em **Modelagem → Gerenciar Relacionamentos**:

| De (Fato) | Campo | Para (Dimensão) | Campo |
|---|---|---|---|
| Faturamento | dt_ref (data) | Calendario | Data |
| Faturamento | id_bairro | DimBairro | id_bairro |
| Faturamento | id_grupo | DimGrupo | id_grupo |
| Faturamento | id_categoria | DimCategoria | id_categoria |
| Faturamento | id_classe | DimClasse | id_classe |
| Arrecadacao | dt_ref (data) | Calendario | Data |
| PainelArrecadacao | dt_pagamento (data) | Calendario | Data |
| Inadimplencia | dt_vencimento (data) | Calendario | Data |
| Cortes | dt_solicitacao (data) | Calendario | Data |
| Religacoes | dt_reliagacao (data) | Calendario | Data |
| Servicos | dt_solicitacao (data) | Calendario | Data |
| Leituras | dt_ref (data) | Calendario | Data |
| Backlog | dt_ref (data) | Calendario | Data |

---

## 4. Estrutura dos Dashboards

### Página 1 — COCKPIT EXECUTIVO
KPIs: Faturamento, Arrecadação, % Eficiência, Inadimplência, Cortes, SLA
Filtros: Período (slicer tipo lista: Diário/Mensal/Trimestral/Semestral/Anual + intervalo de datas)

### Página 2 — FATURAMENTO
- Gráfico de linha: Faturamento mensal (água + esgoto + serviços)
- Gráfico de colunas agrupadas: Componentes do faturamento
- Treemap: Faturamento por bairro
- Cartão: Ticket médio | Total faturado | Volume m³
- Tabela: Ranking por bairro/categoria

### Página 3 — ARRECADAÇÃO
- Gráfico área: Faturado vs Arrecadado (mensal)
- Gráfico pizza: Canal de arrecadação (forma de pagamento)
- Velocímetro (gauge): Índice de eficiência (meta: 95%)
- Linha: Evolução do índice de arrecadação

### Página 4 — INADIMPLÊNCIA
- Gráfico de barras: Inadimplência por faixa de atraso (valor e qtd)
- Donut: Distribuição do risco (recuperável vs difícil)
- Mapa: Inadimplência por bairro (se coordenadas disponíveis)
- Tabela: Top 20 maiores inadimplentes
- KPI: Índice de inadimplência vs meta

### Página 5 — OPERACIONAL — SERVIÇOS
- Gráfico de colunas: Serviços por tipo/canal de atendimento
- Gauge: % SLA atendido (meta: 90%)
- Gráfico de linhas: Evolução do backlog
- Heatmap: Serviços por dia da semana x hora
- Cartão: Tempo médio de execução

### Página 6 — CORTES E RELIGAÇÕES
- Gráfico de colunas: Cortes por mês
- Linha dupla: Cortes vs Religações
- Cartão: Dias médios corte → religação
- Donut: % cortes no prazo
- Barra: Top bairros com mais cortes

### Página 7 — LEITURAS
- Linha: Eficiência de leitura mensal
- Barra: Volume lido vs faturado
- KPI: % leituras críticas
- Tabela: Leituristas com mais erros/críticas
- Índice de perdas aparentes

---

## 5. Filtros Temporais (Slicer)

Criar um **Slicer de Data** conectado à tabela `Calendario[Data]`:
- Tipo: **Intervalo de datas** (permite período livre)
- Botões rápidos via Favoritos do Power BI:
  - Hoje | Mês atual | Trimestre | Semestre | Ano | Últimos 12 meses

---

## 6. Atualização Diária Automática

### Opção A — Task Scheduler (recomendado)
1. Execute `agendar_task_scheduler.bat` como **Administrador** (uma única vez)
2. O ETL rodará automaticamente às 06:00 todos os dias
3. Abra o Power BI Desktop → **Atualizar** para carregar os novos dados

### Opção B — Power BI Service com Refresh Agendado
1. Publique o .pbix no Power BI Service
2. No dataset → **Atualização Agendada** → configurar para 06:30 (após ETL)
3. Necessário: Gateway de dados configurado com a pasta `data/` acessível

### Opção C — SharePoint/OneDrive (se a pasta for sincronizada)
Se a pasta `BI_Ipameri/data/` estiver sincronizada com SharePoint:
1. No Power BI Service, conecte via SharePoint Online
2. O refresh acontece automaticamente sem Gateway

---

## 7. Publicação no Power BI Service

1. Power BI Desktop → **Página Inicial** → **Publicar**
2. Selecionar workspace: "Águas de Ipameri" (criar se necessário)
3. Após publicar, acesse app.powerbi.com
4. Criar **App** com os dashboards para compartilhar com a equipe

---

## 8. Atualização do ETL

Se precisar rodar manualmente:
```bat
cd "...\BI_Ipameri\scripts"
python etl_bigquery.py
```

Log disponível em: `BI_Ipameri\etl.log`
