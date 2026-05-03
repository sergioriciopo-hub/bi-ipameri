"""
Varredura final: FAT0043, faturamento_comercial, painel_arrecadacao_contabil
"""
from pathlib import Path
from google.cloud import bigquery
from google.oauth2 import service_account

KEY_PATH = Path(r"C:\Users\SérgioRiciopo\AGUAS DE IPAMERI\03 COMERCIAL - Documentos\01 - Projetos e Propostas\Jtech\DATA SET\ipameri type service account_28.04.2026.json")
PROJECT  = "br-ist-jtech-clientes"
DATASET  = "jtechbi_ipameri"

creds  = service_account.Credentials.from_service_account_file(str(KEY_PATH))
client = bigquery.Client(credentials=creds, project=PROJECT)

def q(sql):
    return client.query(sql).to_dataframe()

def tbl(name):
    return f"`{PROJECT}.{DATASET}.{name}`"

FAT0015 = {'2026-03': 914243.59, '2026-04': 1085383.06}

# Helper: schema de uma tabela
def schema(table):
    return q(f"""
        SELECT column_name, data_type
        FROM `{PROJECT}.{DATASET}.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name = '{table}'
        ORDER BY ordinal_position
    """)

# ── 1. FAT0043 ────────────────────────────────────────────────────────────────
print("\n=== 1. FAT0043 — schema ===")
try:
    sc = schema('FAT0043')
    for _, r in sc.iterrows():
        print(f"  {r['column_name']:40s} {r['data_type']}")
    am = q(f"SELECT * FROM {tbl('FAT0043')} LIMIT 3")
    print(am.to_string(index=False))
    # ver se tem dt_ref e valores de faturamento
    cols = sc['column_name'].tolist()
    money_cols = [c for c in cols if 'vl_' in c or 'valor' in c.lower()]
    print(f"  Colunas monetárias: {money_cols}")
    # totais Mar/Abr se tiver dt_ref
    if 'dt_ref' in cols:
        tot = q(f"""
            SELECT FORMAT_DATE('%Y-%m', CAST(dt_ref AS DATE)) AS mes,
                   {', '.join(f'ROUND(SUM(COALESCE({c},0)),2) AS {c}' for c in money_cols[:6])}
            FROM {tbl('FAT0043')}
            WHERE CAST(dt_ref AS DATE) IN ('2026-03-01','2026-04-01')
            GROUP BY mes ORDER BY mes
        """)
        print(tot.to_string(index=False))
except Exception as e:
    print(f"  Erro: {e}")

# ── 2. faturamento_comercial ──────────────────────────────────────────────────
print("\n=== 2. faturamento_comercial — schema ===")
try:
    sc2 = schema('faturamento_comercial')
    for _, r in sc2.iterrows():
        print(f"  {r['column_name']:40s} {r['data_type']}")
    cols2 = sc2['column_name'].tolist()
    money2 = [c for c in cols2 if 'vl_' in c]
    print(f"  Colunas vl_*: {money2}")
    # totais Mar/Abr
    if 'dt_ref' in cols2:
        tot2 = q(f"""
            SELECT FORMAT_DATE('%Y-%m', CAST(dt_ref AS DATE)) AS mes,
                   {', '.join(f'ROUND(SUM(COALESCE({c},0)),2) AS {c}' for c in money2[:8])},
                   COUNT(*) AS qtd
            FROM {tbl('faturamento_comercial')}
            WHERE CAST(dt_ref AS DATE) IN ('2026-03-01','2026-04-01')
            GROUP BY mes ORDER BY mes
        """)
        print(tot2.to_string(index=False))
except Exception as e:
    print(f"  Erro: {e}")

# ── 3. faturamento_contabil vs faturamento_comercial — comparação direta ──────
print("\n=== 3. faturamento_contabil totais Mar/Abr (referência) ===")
try:
    ref = q(f"""
        SELECT FORMAT_DATE('%Y-%m', CAST(dt_ref AS DATE)) AS mes,
               ROUND(SUM(COALESCE(vl_agua,0)+COALESCE(vl_servico_basico_agua,0)
                   +COALESCE(vl_esgoto,0)+COALESCE(vl_servico_basico_esgoto,0)
                   +COALESCE(vl_lixo,0)+COALESCE(vl_servico,0)
                   +COALESCE(vl_abatimento,0)-COALESCE(vl_cancelamento,0)),2) AS liquido_contabil,
               COUNT(*) AS qtd
        FROM {tbl('faturamento_contabil')}
        WHERE CAST(dt_ref AS DATE) IN ('2026-03-01','2026-04-01')
        GROUP BY mes ORDER BY mes
    """)
    for _, r in ref.iterrows():
        fat = FAT0015.get(r['mes'], None)
        gap = fat - r['liquido_contabil'] if fat else None
        print(f"  {r['mes']}  liquido_contabil={r['liquido_contabil']:,.2f}  qtd={r['qtd']}  gap_fat0015={gap:+,.2f}")
except Exception as e:
    print(f"  Erro: {e}")

# ── 4. painel_arrecadacao_contabil ────────────────────────────────────────────
print("\n=== 4. painel_arrecadacao_contabil — schema ===")
try:
    sc4 = schema('painel_arrecadacao_contabil')
    for _, r in sc4.iterrows():
        print(f"  {r['column_name']:40s} {r['data_type']}")
    am4 = q(f"SELECT * FROM {tbl('painel_arrecadacao_contabil')} LIMIT 3")
    print(am4.to_string(index=False))
except Exception as e:
    print(f"  Erro: {e}")

# ── 5. CAD0028 e MED0017 — schemas rápidos ────────────────────────────────────
for nome in ['CAD0028', 'MED0017']:
    print(f"\n=== {nome} — schema ===")
    try:
        sc = schema(nome)
        for _, r in sc.iterrows():
            print(f"  {r['column_name']:40s} {r['data_type']}")
        am = q(f"SELECT * FROM {tbl(nome)} LIMIT 2")
        print(am.to_string(index=False))
    except Exception as e:
        print(f"  Erro: {e}")

print("\n=== FIM ===")
