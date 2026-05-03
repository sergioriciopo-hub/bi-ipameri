"""
Investigação aprofundada do FAT0043:
- consumo_real_de_agua pode ser o valor pós-correção para fl_critica
- mes_da_fatura vs data_competencia: qual é a referência de competência?
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

# ── 1. Datas disponíveis em FAT0043 ─────────────────────────────────────────
print("=== 1. Datas disponíveis em FAT0043 ===")
datas = q(f"""
    SELECT
        FORMAT_DATE('%Y-%m', CAST(mes_da_fatura AS DATE)) AS mes_fatura,
        FORMAT_DATE('%Y-%m', CAST(data_competencia AS DATE)) AS competencia,
        COUNT(*) AS qtd,
        ROUND(SUM(valor_da_fatura_da_agua + COALESCE(valor_da_fatura_do_esgoto,0)),2) AS total_agua_esgt
    FROM {tbl('FAT0043')}
    GROUP BY mes_fatura, competencia
    ORDER BY mes_fatura DESC, competencia DESC
    LIMIT 20
""")
print(datas.to_string(index=False))

# ── 2. Totais Mar/Abr 2026 por mes_da_fatura ────────────────────────────────
print("\n=== 2. Totais FAT0043 por mes_da_fatura (Mar e Abr 2026) ===")
for mes_dt, mes_str in [('2026-03-01','2026-03'), ('2026-04-01','2026-04')]:
    r = q(f"""
        SELECT
            COUNT(*) AS qtd,
            ROUND(SUM(COALESCE(consumo_de_agua,0)),2)                  AS consumo_agua,
            ROUND(SUM(COALESCE(consumo_real_de_agua,0)),2)             AS consumo_real,
            ROUND(SUM(COALESCE(valor_da_fatura_da_agua,0)),2)          AS vl_agua,
            ROUND(SUM(COALESCE(valor_da_fatura_do_esgoto,0)),2)        AS vl_esgoto,
            ROUND(SUM(COALESCE(valor_do_servico,0)),2)                 AS vl_servico,
            ROUND(SUM(COALESCE(valor_da_fatura_do_lixo,0)),2)          AS vl_lixo,
            ROUND(SUM(COALESCE(valor_do_abatimento_terceiro,0)),2)     AS vl_abatimento,
            ROUND(SUM(COALESCE(valor_do_cancelamento,0)),2)            AS vl_cancelamento,
            ROUND(SUM(COALESCE(valor_do_desconto_de_vazamento,0)),2)   AS vl_desc_vaz,
            ROUND(SUM(COALESCE(valor_de_multas_e_juros,0)),2)          AS vl_multas,
            -- Formula FAT0015: agua+esgt+servico+lixo+abat-cancel (sem multas)
            ROUND(SUM(
                COALESCE(valor_da_fatura_da_agua,0)
                + COALESCE(valor_da_fatura_do_esgoto,0)
                + COALESCE(valor_do_servico,0)
                + COALESCE(valor_da_fatura_do_lixo,0)
                + COALESCE(valor_do_abatimento_terceiro,0)
                - COALESCE(valor_do_cancelamento,0)
            ),2) AS liquido_calculado,
            -- Formula com desc_vaz
            ROUND(SUM(
                COALESCE(valor_da_fatura_da_agua,0)
                + COALESCE(valor_da_fatura_do_esgoto,0)
                + COALESCE(valor_do_servico,0)
                + COALESCE(valor_da_fatura_do_lixo,0)
                + COALESCE(valor_do_abatimento_terceiro,0)
                - COALESCE(valor_do_cancelamento,0)
                + COALESCE(valor_do_desconto_de_vazamento,0)
            ),2) AS liquido_com_desc_vaz
        FROM {tbl('FAT0043')}
        WHERE CAST(mes_da_fatura AS DATE) = '{mes_dt}'
    """).iloc[0]
    fat = FAT0015[mes_str]
    print(f"\n  {mes_str} | FAT0015={fat:,.2f}")
    print(f"  qtd={r['qtd']}  consumo_agua={r['consumo_agua']:,.1f}  consumo_real={r['consumo_real']:,.1f}")
    print(f"  vl_agua={r['vl_agua']:,.2f}  vl_esgoto={r['vl_esgoto']:,.2f}  vl_servico={r['vl_servico']:,.2f}  vl_lixo={r['vl_lixo']:,.2f}")
    print(f"  vl_abat={r['vl_abatimento']:,.2f}  vl_cancel={r['vl_cancelamento']:,.2f}  vl_desc_vaz={r['vl_desc_vaz']:,.2f}  vl_multas={r['vl_multas']:,.2f}")
    print(f"  Fórmula A (sem desc_vaz) = {r['liquido_calculado']:,.2f}  gap={fat-r['liquido_calculado']:+,.2f}")
    print(f"  Fórmula B (com desc_vaz) = {r['liquido_com_desc_vaz']:,.2f}  gap={fat-r['liquido_com_desc_vaz']:+,.2f}")

# ── 3. Verificar se tipo_de_documento = Cancelamento afeta o total ──────────
print("\n=== 3. FAT0043 por tipo_de_documento (Mar 2026) ===")
tipos = q(f"""
    SELECT
        tipo_de_documento,
        COUNT(*) AS qtd,
        ROUND(SUM(COALESCE(valor_da_fatura_da_agua,0)),2) AS vl_agua,
        ROUND(SUM(COALESCE(valor_do_cancelamento,0)),2) AS vl_cancelamento,
        ROUND(SUM(
            COALESCE(valor_da_fatura_da_agua,0)+COALESCE(valor_da_fatura_do_esgoto,0)
            +COALESCE(valor_do_servico,0)+COALESCE(valor_da_fatura_do_lixo,0)
            +COALESCE(valor_do_abatimento_terceiro,0)-COALESCE(valor_do_cancelamento,0)
        ),2) AS liquido
    FROM {tbl('FAT0043')}
    WHERE CAST(mes_da_fatura AS DATE) = '2026-03-01'
    GROUP BY tipo_de_documento
    ORDER BY tipo_de_documento
""")
print(tipos.to_string(index=False))

# ── 4. FAT0043: somente Faturas (excluindo outros tipos) ────────────────────
print("\n=== 4. FAT0043 somente tipo='Fatura' — Mar e Abr 2026 ===")
for mes_dt, mes_str in [('2026-03-01','2026-03'), ('2026-04-01','2026-04')]:
    r = q(f"""
        SELECT
            COUNT(*) AS qtd,
            ROUND(SUM(
                COALESCE(valor_da_fatura_da_agua,0)+COALESCE(valor_da_fatura_do_esgoto,0)
                +COALESCE(valor_do_servico,0)+COALESCE(valor_da_fatura_do_lixo,0)
                +COALESCE(valor_do_abatimento_terceiro,0)-COALESCE(valor_do_cancelamento,0)
            ),2) AS liquido,
            ROUND(SUM(
                COALESCE(valor_da_fatura_da_agua,0)+COALESCE(valor_da_fatura_do_esgoto,0)
                +COALESCE(valor_do_servico,0)+COALESCE(valor_da_fatura_do_lixo,0)
                +COALESCE(valor_do_abatimento_terceiro,0)-COALESCE(valor_do_cancelamento,0)
                +COALESCE(valor_do_desconto_de_vazamento,0)
            ),2) AS liquido_desc_vaz
        FROM {tbl('FAT0043')}
        WHERE CAST(mes_da_fatura AS DATE) = '{mes_dt}'
          AND tipo_de_documento = 'Fatura'
    """).iloc[0]
    fat = FAT0015[mes_str]
    print(f"  {mes_str}  qtd={r['qtd']}  liquido={r['liquido']:,.2f}  gap={fat-r['liquido']:+,.2f}  com_desc_vaz={r['liquido_desc_vaz']:,.2f}  gap={fat-r['liquido_desc_vaz']:+,.2f}")

# ── 5. consumo_real vs consumo_de_agua — diferença (potencial fl_critica) ────
print("\n=== 5. Registros com consumo_real != consumo_de_agua (Mar 2026) ===")
dif = q(f"""
    SELECT
        COUNT(*) AS total,
        COUNTIF(consumo_real_de_agua IS NOT NULL AND consumo_real_de_agua != consumo_de_agua) AS com_diferenca,
        ROUND(SUM(CASE WHEN consumo_real_de_agua IS NOT NULL AND consumo_real_de_agua != consumo_de_agua
            THEN consumo_de_agua ELSE 0 END),2) AS soma_consumo_bruto_dif,
        ROUND(SUM(CASE WHEN consumo_real_de_agua IS NOT NULL AND consumo_real_de_agua != consumo_de_agua
            THEN consumo_real_de_agua ELSE 0 END),2) AS soma_consumo_real_dif,
        ROUND(SUM(CASE WHEN consumo_real_de_agua IS NOT NULL AND consumo_real_de_agua != consumo_de_agua
            THEN valor_da_fatura_da_agua ELSE 0 END),2) AS vl_agua_registros_dif
    FROM {tbl('FAT0043')}
    WHERE CAST(mes_da_fatura AS DATE) = '2026-03-01'
      AND tipo_de_documento = 'Fatura'
""").iloc[0]
print(f"  total={dif['total']}  com_diferenca={dif['com_diferenca']}")
print(f"  soma_consumo_bruto_dif={dif['soma_consumo_bruto_dif']:,.1f}  soma_consumo_real_dif={dif['soma_consumo_real_dif']:,.1f}")
print(f"  vl_agua_registros_dif={dif['vl_agua_registros_dif']:,.2f}")

print("\n=== FIM ===")
