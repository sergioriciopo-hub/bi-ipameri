"""
Diagnóstico: aux_faturamento_comercial — fórmulas candidatas + varredura restante
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

FAT = {'2026-03': 914243.59, '2026-04': 1085383.06}

# ── 1. Fórmulas candidatas separadas por mês ────────────────────────────────
for mes_dt, mes_str in [('2026-03-01','2026-03'), ('2026-04-01','2026-04')]:
    print(f"\n=== Fórmulas {mes_str} | FAT0015={FAT[mes_str]:,.2f} ===")
    r = q(f"""
        SELECT
            ROUND(SUM(COALESCE(vl_agua_fato,0)+COALESCE(vl_servico_basico_fato,0)
                +COALESCE(vl_esgoto_fato,0)+COALESCE(vl_servico_basico_esgoto_fato,0)
                +COALESCE(vl_lixo_fato,0)+COALESCE(vl_servico_fato,0)),2) AS A_bruto,
            ROUND(SUM(COALESCE(vl_agua_fato,0)+COALESCE(vl_servico_basico_fato,0)
                +COALESCE(vl_esgoto_fato,0)+COALESCE(vl_servico_basico_esgoto_fato,0)
                +COALESCE(vl_lixo_fato,0)+COALESCE(vl_servico_fato,0)
                +COALESCE(vl_desconto_vazamento_fato,0)),2) AS B_desc_vaz,
            ROUND(SUM(COALESCE(vl_agua_fato,0)+COALESCE(vl_servico_basico_fato,0)
                +COALESCE(vl_esgoto_fato,0)+COALESCE(vl_servico_basico_esgoto_fato,0)
                +COALESCE(vl_lixo_fato,0)+COALESCE(vl_servico_fato,0)
                +COALESCE(vl_desconto_vazamento_fato,0)
                +COALESCE(vl_devolvido_fato,0)),2) AS C_devolvido,
            ROUND(SUM(COALESCE(vl_agua_fato,0)+COALESCE(vl_servico_basico_fato,0)
                +COALESCE(vl_esgoto_fato,0)+COALESCE(vl_servico_basico_esgoto_fato,0)
                +COALESCE(vl_lixo_fato,0)+COALESCE(vl_servico_fato,0)
                -COALESCE(vl_cancelamento,0)),2) AS D_cancel,
            ROUND(SUM(COALESCE(vl_agua_fato,0)+COALESCE(vl_servico_basico_fato,0)
                +COALESCE(vl_esgoto_fato,0)+COALESCE(vl_servico_basico_esgoto_fato,0)
                +COALESCE(vl_lixo_fato,0)+COALESCE(vl_servico_fato,0)
                +COALESCE(vl_desconto_vazamento_fato,0)
                -COALESCE(vl_cancelamento,0)),2) AS E_desc_cancel
        FROM {tbl('aux_faturamento_comercial')}
        WHERE CAST(dt_ref AS DATE) = '{mes_dt}'
    """).iloc[0]
    fat = FAT[mes_str]
    for nome, val in [('A bruto (sem multas, sem cancel)', r['A_bruto']),
                      ('B A + desc.vaz',                   r['B_desc_vaz']),
                      ('C B + devolvido',                  r['C_devolvido']),
                      ('D A - cancelamento',               r['D_cancel']),
                      ('E A + desc.vaz - cancel',          r['E_desc_cancel'])]:
        print(f"  {nome:40s} = {val:>12,.2f}  gap={fat-val:+,.2f}")

# ── 2. Ver se fl_critica influencia o gap em aux_faturamento_comercial ────────
print("\n=== 2. Gap por fl_critica em aux_faturamento_comercial ===")
crit = q(f"""
    SELECT
        FORMAT_DATE('%Y-%m', CAST(dt_ref AS DATE)) AS mes,
        fl_critica,
        COUNT(*) AS qtd,
        ROUND(SUM(COALESCE(vl_agua_fato,0)),2) AS agua_fato,
        ROUND(SUM(COALESCE(vl_servico_basico_fato,0)),2) AS tar_bas_fato,
        ROUND(SUM(COALESCE(vl_agua_fato,0)+COALESCE(vl_servico_basico_fato,0)
            +COALESCE(vl_lixo_fato,0)+COALESCE(vl_servico_fato,0)),2) AS liquido_parcial
    FROM {tbl('aux_faturamento_comercial')}
    WHERE CAST(dt_ref AS DATE) IN ('2026-03-01','2026-04-01')
    GROUP BY mes, fl_critica
    ORDER BY mes, fl_critica
""")
print(crit.to_string(index=False))

# ── 3. Listagem de TODAS as tabelas ─────────────────────────────────────────
print("\n=== 3. Todas as tabelas do dataset ===")
tables = q(f"""
    SELECT table_name
    FROM `{PROJECT}.{DATASET}.INFORMATION_SCHEMA.TABLES`
    ORDER BY table_name
""")
for _, row in tables.iterrows():
    print(f"  {row['table_name']}")

# ── 4. pendencia_contabil ────────────────────────────────────────────────────
print("\n=== 4. pendencia_contabil — schema ===")
try:
    sc = q(f"""
        SELECT column_name, data_type
        FROM `{PROJECT}.{DATASET}.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name = 'pendencia_contabil'
        ORDER BY ordinal_position
    """)
    for _, row in sc.iterrows():
        print(f"  {row['column_name']:40s} {row['data_type']}")
    am = q(f"SELECT * FROM {tbl('pendencia_contabil')} LIMIT 3")
    print(am.to_string(index=False))
except Exception as e:
    print(f"  Erro: {e}")

# ── 5. documentos_arrecadados_contabil ──────────────────────────────────────
print("\n=== 5. documentos_arrecadados_contabil — schema ===")
try:
    sc2 = q(f"""
        SELECT column_name, data_type
        FROM `{PROJECT}.{DATASET}.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name = 'documentos_arrecadados_contabil'
        ORDER BY ordinal_position
    """)
    for _, row in sc2.iterrows():
        print(f"  {row['column_name']:40s} {row['data_type']}")
    am2 = q(f"SELECT * FROM {tbl('documentos_arrecadados_contabil')} LIMIT 3")
    print(am2.to_string(index=False))
except Exception as e:
    print(f"  Erro: {e}")

# ── 6. evolucao_documentos — schema + valores Mar ───────────────────────────
print("\n=== 6. evolucao_documentos ===")
try:
    sc3 = q(f"""
        SELECT column_name, data_type
        FROM `{PROJECT}.{DATASET}.INFORMATION_SCHEMA.COLUMNS`
        WHERE table_name = 'evolucao_documentos'
        ORDER BY ordinal_position
    """)
    for _, row in sc3.iterrows():
        print(f"  {row['column_name']:40s} {row['data_type']}")

    ev = q(f"""
        SELECT *
        FROM {tbl('evolucao_documentos')}
        WHERE CAST(dt_ref AS DATE) = '2026-03-01'
        LIMIT 5
    """)
    print(ev.to_string(index=False))
except Exception as e:
    print(f"  Erro: {e}")

print("\n=== FIM ===")
