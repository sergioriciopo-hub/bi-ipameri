"""Checar BI0001 e alteracao_fatura_comercial"""
from pathlib import Path
from google.cloud import bigquery
from google.oauth2 import service_account

KEY_PATH = Path(r"C:\Users\SérgioRiciopo\AGUAS DE IPAMERI\03 COMERCIAL - Documentos\01 - Projetos e Propostas\Jtech\DATA SET\ipameri type service account_28.04.2026.json")
PROJECT  = "br-ist-jtech-clientes"
DATASET  = "jtechbi_ipameri"

creds  = service_account.Credentials.from_service_account_file(str(KEY_PATH))
client = bigquery.Client(credentials=creds, project=PROJECT)

def q(sql): return client.query(sql).to_dataframe()
def tbl(name): return f"`{PROJECT}.{DATASET}.{name}`"

for nome in ['BI0001', 'alteracao_fatura_comercial']:
    print(f"\n=== {nome} — schema ===")
    try:
        sc = q(f"""
            SELECT column_name, data_type
            FROM `{PROJECT}.{DATASET}.INFORMATION_SCHEMA.COLUMNS`
            WHERE table_name = '{nome}'
            ORDER BY ordinal_position
        """)
        for _, r in sc.iterrows():
            print(f"  {r['column_name']:40s} {r['data_type']}")
        am = q(f"SELECT * FROM {tbl(nome)} LIMIT 3")
        print(am.to_string(index=False))
        # Se tem dt_ref e colunas vl_, tenta totais de Mar/Abr
        cols = sc['column_name'].tolist()
        if 'dt_ref' in cols:
            money = [c for c in cols if c.startswith('vl_')][:6]
            if money:
                tot = q(f"""
                    SELECT FORMAT_DATE('%Y-%m', CAST(dt_ref AS DATE)) AS mes,
                           {', '.join(f'ROUND(SUM(COALESCE({c},0)),2) AS {c}' for c in money)},
                           COUNT(*) AS qtd
                    FROM {tbl(nome)}
                    WHERE CAST(dt_ref AS DATE) IN ('2026-03-01','2026-04-01')
                    GROUP BY mes ORDER BY mes
                """)
                print("  Totais Mar/Abr:")
                print(tot.to_string(index=False))
    except Exception as e:
        print(f"  Erro: {e}")

print("\n=== FIM ===")
