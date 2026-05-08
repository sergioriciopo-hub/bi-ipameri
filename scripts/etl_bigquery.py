"""
ETL - Águas de Ipameri | BigQuery → Parquet local
Execução: python etl_bigquery.py
Agendar: Task Scheduler diário às 06:00
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

# ── Configuração ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.parent
KEY_PATH = Path(r"C:\Users\SérgioRiciopo\AGUAS DE IPAMERI\03 COMERCIAL - Documentos\01 - Projetos e Propostas\Jtech\DATA SET\ipameri type service account_28.04.2026.json")
DATA_DIR = BASE_DIR / "data"
PROJECT   = "br-ist-jtech-clientes"
DATASET   = "jtechbi_ipameri"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(BASE_DIR / "etl.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)


def get_client():
    creds = service_account.Credentials.from_service_account_file(str(KEY_PATH))
    return bigquery.Client(credentials=creds, project=PROJECT)


def tbl(name):
    return f"`{PROJECT}.{DATASET}.{name}`"


# ── Queries ───────────────────────────────────────────────────────────────────
QUERIES = {

    "faturamento": f"""
        SELECT
            dt_ref,
            ch_rsf_grupo_dim             AS id_grupo,
            ch_rsf_categoria_dim         AS id_categoria,
            ch_rsf_classe_consumidor_dim AS id_classe,
            ch_rsf_bairro_dim            AS id_bairro,
            id_localizacao_dim           AS id_localizacao,
            fl_tarifa_social,
            nr_economia,
            nr_economia_agua,
            nr_economia_esgoto,
            nr_lig_agua,
            nr_lig_esgoto,
            qt_fatura,
            vl_volume_faturado           AS volume_m3,
            qt_volume_esgoto_faturado    AS volume_esgoto_m3,
            vl_agua,
            vl_esgoto,
            vl_lixo,
            vl_servico,
            vl_servico_basico_agua,
            vl_servico_basico_esgoto,
            vl_multas_juros,
            vl_abatimento,
            vl_devolucao,
            vl_cancelamento,
            vl_imposto,
            -- Faturamento Líquido conforme FAT0015:
            -- Água + Tar.Básica + Esgoto + Lixo + Serviços + Abatimento - Cancelamento
            -- Multas/Juros são exibidas separadamente (não entram no líquido)
            -- COALESCE para tratar NULLs que propagariam para a expressão inteira
            (COALESCE(vl_agua,0) + COALESCE(vl_servico_basico_agua,0)
             + COALESCE(vl_esgoto,0) + COALESCE(vl_servico_basico_esgoto,0)
             + COALESCE(vl_lixo,0) + COALESCE(vl_servico,0)
             + COALESCE(vl_abatimento,0) - COALESCE(vl_cancelamento,0)) AS vl_total_faturado,
            faixa_faturamento,
            tipo_grupo_faturamento
        FROM {tbl('faturamento_contabil')}
        WHERE dt_ref <= DATE_SUB(DATE_TRUNC(CURRENT_DATE(), MONTH), INTERVAL 1 DAY)
    """,

    "arrecadacao": f"""
        SELECT
            dt_ref,
            ch_rsf_grupo_dim          AS id_grupo,
            ch_rsf_categoria_dim      AS id_categoria,
            ch_rsf_classe_consumidor_dim AS id_classe,
            ch_rsf_bairro_dim         AS id_bairro,
            id_localizacao_dim        AS id_localizacao,
            ds_tipo_documento_cobranca AS tipo_documento,
            vl_agua,
            vl_esgoto,
            vl_lixo,
            vl_servico,
            vl_servico_basico_agua,
            vl_servico_basico_esgoto,
            vl_demais_valores_arrecadados,
            (vl_agua
             + vl_esgoto
             + vl_lixo
             + vl_servico
             + IFNULL(vl_servico_basico_agua, 0)
             + IFNULL(vl_servico_basico_esgoto, 0)
             + vl_demais_valores_arrecadados) AS vl_total_arrecadado
        FROM {tbl('arrecadacao_comercial')}
    """,

    "painel_arrecadacao": f"""
        SELECT
            dt_pagamento,
            dt_ref,
            id_agente_arrecadador     AS id_agente,
            id_localizacao_dim        AS id_localizacao,
            ch_rsf_grupo_dim          AS id_grupo,
            ch_rsf_categoria_dim      AS id_categoria,
            ch_classe_consumidor      AS id_classe,
            ch_rsf_bairro_dim         AS id_bairro,
            ch_tipo_cobranca_dim      AS id_tipo_cobranca,
            ch_tipo_forma_arrecadacao AS id_forma_arrecadacao,
            ds_tipo_documento_cobranca AS tipo_documento,
            qt_documentos,
            qt_pagamentos,
            vl_pagamento,
            vl_tarifa
        FROM {tbl('painel_arrecadacao_comercial')}
    """,

    # Arrecadação diária por agente/forma — painel_arrecadacao_contabil (D+ ready, até Mai/2026)
    # Fonte validada: bate com relatório do sistema usando lógica D+ (FDS → próxima segunda)
    "arrecadacao_diaria": f"""
        SELECT
            DATE(dt_pagamento)                        AS data_pagamento,
            FORMAT_DATE('%A', DATE(dt_pagamento))     AS dia_semana,
            EXTRACT(DAYOFWEEK FROM DATE(dt_pagamento)) AS nr_dia_semana,
            FORMAT_DATE('%Y-%m', DATE(dt_pagamento))  AS ano_mes,
            ch_rsf_grupo_dim          AS id_grupo,
            ch_rsf_categoria_dim      AS id_categoria,
            ch_rsf_bairro_dim         AS id_bairro,
            ch_tipo_forma_arrecadacao AS id_forma_arrecadacao,
            ch_tipo_cobranca_dim      AS id_tipo_cobranca,
            id_agente_arrecadador     AS id_agente,
            SUM(qt_documentos)        AS qt_documentos,
            SUM(qt_pagamentos)        AS qt_pagamentos,
            SUM(vl_pagamento)         AS vl_arrecadado,
            SUM(IFNULL(vl_tarifa,0))  AS vl_tarifa
        FROM {tbl('painel_arrecadacao_contabil')}
        GROUP BY 1,2,3,4,5,6,7,8,9,10
    """,

    # Arrecadação mensal por rubrica — arrecadacao_comercial (fonte principal, inclui servico_basico)
    "arrecadacao_rubricas": f"""
        SELECT
            dt_ref,
            FORMAT_DATETIME('%Y-%m', dt_ref)          AS ano_mes,
            ch_rsf_bairro_dim         AS id_bairro,
            ch_rsf_categoria_dim      AS id_categoria,
            ch_rsf_grupo_dim          AS id_grupo,
            ds_tipo_documento_cobranca AS tipo_documento,
            IFNULL(vl_agua, 0)                        AS vl_agua,
            IFNULL(vl_esgoto, 0)                      AS vl_esgoto,
            IFNULL(vl_lixo, 0)                        AS vl_lixo,
            IFNULL(vl_servico, 0)                     AS vl_servico,
            IFNULL(vl_servico_basico_agua, 0)         AS vl_servico_basico_agua,
            IFNULL(vl_servico_basico_esgoto, 0)       AS vl_servico_basico_esgoto,
            IFNULL(vl_demais_valores_arrecadados, 0)  AS vl_demais,
            (IFNULL(vl_agua, 0)
             + IFNULL(vl_esgoto, 0)
             + IFNULL(vl_lixo, 0)
             + IFNULL(vl_servico, 0)
             + IFNULL(vl_servico_basico_agua, 0)
             + IFNULL(vl_servico_basico_esgoto, 0)
             + IFNULL(vl_demais_valores_arrecadados, 0)) AS vl_total
        FROM {tbl('arrecadacao_comercial')}
    """,

    "pendencia_atual": f"""
        SELECT
            dt_ref_documento,
            dt_vencimento,
            ch_rsf_grupo_dim          AS id_grupo,
            ch_rsf_categoria_dim      AS id_categoria,
            ch_rsf_classe_consumidor_dim AS id_classe,
            ch_rsf_bairro_dim         AS id_bairro,
            ch_situacao_fatura        AS id_situacao_fatura,
            ch_situacao_ligacao_agua_dim AS id_situacao_ligacao,
            id_localizacao_dim        AS id_localizacao,
            nr_dias_atraso,
            nr_faixa_fim              AS faixa_dias,
            fl_aviso_vencido,
            fl_corte_pendente,
            vl_divida,
            CASE
                WHEN nr_dias_atraso <= 30  THEN '01-Até 30 dias'
                WHEN nr_dias_atraso <= 60  THEN '02-31 a 60 dias'
                WHEN nr_dias_atraso <= 90  THEN '03-61 a 90 dias'
                WHEN nr_dias_atraso <= 180 THEN '04-91 a 180 dias'
                WHEN nr_dias_atraso <= 365 THEN '05-181 a 365 dias'
                ELSE '06-Mais de 365 dias'
            END AS faixa_atraso
        FROM {tbl('pendencia_comercial_atual')}
    """,

    "cortes": f"""
        SELECT
            id_servico,
            id_servico_definicao,
            dt_solicitacao,
            dt_limite_execucao,
            dt_fim_execucao,
            dt_vencimento_aviso,
            ch_bairro_dim             AS id_bairro,
            ch_setor_operacional      AS id_setor_operacional,
            ch_rsf_grupo_dim          AS id_grupo,
            ch_situacao_ligacao_agua  AS id_situacao_ligacao,
            ch_situacao_servico       AS id_situacao_servico,
            fl_fora_prazo,
            qt_servico,
            qt_tempo_execucao,
            qt_documentos_aviso,
            qt_documentos_parcelados,
            vl_pendencia_atual,
            vl_total_aviso_debito,
            nm_cliente,
            ch_matricula_unidade      AS matricula_unidade,
            FORMAT_DATETIME('%Y-%m', dt_solicitacao) AS ano_mes_solicitacao
        FROM {tbl('corte_executado')}
    """,

    "religacoes": f"""
        SELECT
            r.id_servico,
            r.id_servico_definicao,
            r.dt_corte,
            r.dt_reliagacao,
            -- dias corte→religação: quanto o cliente levou para pagar e pedir religação
            DATETIME_DIFF(r.dt_reliagacao, r.dt_corte, DAY)    AS dias_corte_religacao,
            -- SLA: dt_solicitacao e dt_fim_execucao vêm do painel_servico (mesma OS)
            s.dt_solicitacao,
            s.dt_fim_execucao,
            DATETIME_DIFF(s.dt_fim_execucao, s.dt_solicitacao, MINUTE) AS minutos_sla,
            r.ch_bairro_dim             AS id_bairro,
            r.ch_setor_operacional      AS id_setor_operacional,
            r.ch_rsf_grupo_dim          AS id_grupo,
            FORMAT_DATETIME('%Y-%m', r.dt_reliagacao) AS ano_mes_religacao
        FROM {tbl('religacao_executada')} r
        LEFT JOIN {tbl('painel_servico')} s USING (id_servico)
        WHERE r.dt_reliagacao IS NOT NULL
    """,

    "servicos": f"""
        SELECT
            dt_solicitacao,
            dt_limite_execucao,
            dt_fim_execucao,
            dt_cancelamento,
            dt_encerramento_os,
            ch_bairro_dim             AS id_bairro,
            ch_setor_operacional      AS id_setor_operacional,
            ch_situacao_servico       AS id_situacao_servico,
            ch_tipo_acao_servico      AS id_tipo_acao,
            ch_agrupamento_servico    AS id_agrupamento,
            ch_tipo_atendimento       AS id_tipo_atendimento,
            nm_tipo_atendimento,
            id_equipe,
            id_servico_definicao,
            fl_fora_prazo,
            qt_servico,
            qt_tempo_execucao,
            qt_tempo_deslocamento,
            qt_tempo_preparo,
            qt_tempo_preenchimento,
            FORMAT_DATETIME('%Y-%m', dt_solicitacao) AS ano_mes
        FROM {tbl('painel_servico')}
    """,

    "leituras": f"""
        SELECT
            dt_ref,
            ch_rsf_grupo_dim          AS id_grupo,
            ch_rsf_categoria_dim      AS id_categoria,
            ch_rsf_classe_consumidor_dim AS id_classe,
            ch_rsf_bairro_dim         AS id_bairro,
            ch_leiturista_dim         AS id_leiturista,
            ch_tipo_leitura           AS id_tipo_leitura,
            ch_tipo_consumo_faturado  AS id_tipo_consumo,
            ch_rsf_ocorrencia_dim     AS id_ocorrencia,
            id_rota_leitura_agua      AS id_rota,
            fl_critica,
            fl_erro_leitura,
            qt_leitura,
            qt_volume_lido,
            qt_volume_faturado,
            qt_volume_esgoto_faturado,
            nr_consumo_minimo_esperado,
            nr_consumo_maximo_esperado,
            nr_economias,
            FORMAT_DATETIME('%Y-%m', dt_ref) AS ano_mes
        FROM {tbl('dados_leitura_geral')}
    """,

    "backlog_servicos": f"""
        SELECT
            dt_ref,
            dt_solicitacao,
            ch_bairro_dim             AS id_bairro,
            ch_setor_operacional      AS id_setor_operacional,
            ch_tipo_acao_servico      AS id_tipo_acao,
            id_acao_servico,
            id_servico_definicao,
            qt_solicitado,
            qt_executado,
            qt_cancelado,
            (qt_solicitado - qt_executado - qt_cancelado) AS qt_pendente,
            FORMAT_DATETIME('%Y-%m', dt_ref) AS ano_mes
        FROM {tbl('backlog_servico')}
    """,

    "alteracao_fatura_contabil": f"""
        SELECT
            ch_instancia,
            ch_rsf_bairro_dim         AS ch_rsf_bairro_dim,
            ch_rsf_categoria_dim      AS ch_rsf_categoria_dim,
            ch_rsf_classe_consumidor_dim AS ch_rsf_classe_consumidor_dim,
            ch_rsf_grupo_dim          AS ch_rsf_grupo_dim,
            dt_ref,
            id_localizacao_dim,
            id_motivo_alteracao_fatura,
            id_usuario,
            nr_posicao,
            qt_fatura_cancelada,
            qt_fatura_reemitida,
            vl_abatimento,
            vl_cancelamento,
            vl_reemitido,
            ch_leiturista_dim,
            hash_id_chave
        FROM {tbl('alteracao_fatura_contabil')}
    """,

    # ── Dimensões ─────────────────────────────────────────────────────────────
    "dim_bairro": f"""
        SELECT ch_rsf_bairro_dim AS id_bairro, * EXCEPT(ch_rsf_bairro_dim)
        FROM {tbl('dimensao_bairro')}
    """,

    "dim_grupo": f"""
        SELECT ch_rsf_grupo_dim AS id_grupo, * EXCEPT(ch_rsf_grupo_dim)
        FROM {tbl('dimensao_grupo')}
    """,

    "dim_categoria": f"""
        SELECT ch_rsf_categoria_dim AS id_categoria, * EXCEPT(ch_rsf_categoria_dim)
        FROM {tbl('dimensao_categoria')}
    """,

    "dim_classe": f"""
        SELECT ch_rsf_classe_consumidor_dim AS id_classe, * EXCEPT(ch_rsf_classe_consumidor_dim)
        FROM {tbl('dimensao_classe_consumidor')}
    """,

    "dim_situacao_fatura": f"""
        SELECT ch_situacao_fatura AS id_situacao_fatura, * EXCEPT(ch_situacao_fatura)
        FROM {tbl('dimensao_situacao_fatura')}
    """,

    "dim_situacao_servico": f"""
        SELECT ch_situacao_servico AS id_situacao_servico, * EXCEPT(ch_situacao_servico)
        FROM {tbl('dimensao_situacao_servico')}
    """,

    "dim_agente_arrecadador": f"""
        SELECT id_agente_arrecadador AS id_agente, * EXCEPT(id_agente_arrecadador)
        FROM {tbl('dimensao_agente_arrecadador')}
    """,

    "dim_forma_arrecadacao": f"""
        SELECT ch_tipo_forma_arrecadacao AS id_forma_arrecadacao, * EXCEPT(ch_tipo_forma_arrecadacao)
        FROM {tbl('dimensao_forma_arrecadacao')}
    """,

    "dim_leiturista": f"""
        SELECT ch_leiturista_dim AS id_leiturista, * EXCEPT(ch_leiturista_dim)
        FROM {tbl('dimensao_leiturista')}
    """,

    "dim_equipe": f"""
        SELECT id_equipe, * EXCEPT(id_equipe)
        FROM {tbl('dimensao_equipe')}
    """,

    "dim_setor_operacional": f"""
        SELECT ch_setor_operacional AS id_setor_operacional, * EXCEPT(ch_setor_operacional)
        FROM {tbl('dimensao_setor_operacional')}
    """,

    "dim_ocorrencia": f"""
        SELECT ch_rsf_ocorrencia_dim AS id_ocorrencia, * EXCEPT(ch_rsf_ocorrencia_dim)
        FROM {tbl('dimensao_ocorrencia')}
    """,

    "dim_servico_definicao": f"""
        SELECT id_servico_definicao, * EXCEPT(id_servico_definicao)
        FROM {tbl('dimensao_servico_definicao')}
    """,

}


# ── Configuração incremental ──────────────────────────────────────────────────
# mode:
#   "full"    → sempre recarga total (dimensões + snapshots sem data fixa)
#   "monthly" → recarrega os últimos N meses (overlap_n=2 captura correções retroativas)
#   "daily"   → recarrega os últimos N dias (overlap_n cobre chegada tardia de dados)
#
# date_col: coluna de data usada para filtrar no BigQuery e descartar do parquet existente
# bq_date_col: nome da coluna no SQL do BigQuery (pode diferir do nome no parquet após alias)

INCREMENTAL = {
    # ── Fatos mensais ─────────────────────────────────────────────────────────
    "faturamento":               {"mode": "monthly", "overlap_n": 2, "date_col": "dt_ref",        "bq_date_col": "dt_ref"},
    "arrecadacao":               {"mode": "monthly", "overlap_n": 2, "date_col": "dt_ref",        "bq_date_col": "dt_ref"},
    "arrecadacao_rubricas":      {"mode": "monthly", "overlap_n": 2, "date_col": "dt_ref",        "bq_date_col": "dt_ref"},
    "leituras":                  {"mode": "monthly", "overlap_n": 2, "date_col": "dt_ref",        "bq_date_col": "dt_ref"},
    "alteracao_fatura_contabil": {"mode": "monthly", "overlap_n": 2, "date_col": "dt_ref",        "bq_date_col": "dt_ref"},
    # ── Fatos diários ─────────────────────────────────────────────────────────
    "painel_arrecadacao":        {"mode": "daily",   "overlap_n": 14, "date_col": "dt_pagamento", "bq_date_col": "dt_pagamento"},
    "arrecadacao_diaria":        {"mode": "daily",   "overlap_n": 14, "date_col": "data_pagamento","bq_date_col": "data_pagamento"},
    "cortes":                    {"mode": "daily",   "overlap_n": 30, "date_col": "dt_fim_execucao","bq_date_col": "dt_fim_execucao"},
    "religacoes":                {"mode": "daily",   "overlap_n": 30, "date_col": "dt_reliagacao", "bq_date_col": "dt_reliagacao"},
    "servicos":                  {"mode": "daily",   "overlap_n": 14, "date_col": "dt_solicitacao","bq_date_col": "dt_solicitacao"},
    "backlog_servicos":          {"mode": "daily",   "overlap_n": 14, "date_col": "dt_ref",        "bq_date_col": "dt_ref"},
    # ── Snapshot (sempre full — posição atual, sem histórico acumulativo) ─────
    "pendencia_atual":           {"mode": "full"},
    # ── Dimensões (sempre full — tabelas pequenas, < 15KB cada) ──────────────
    "dim_bairro":                {"mode": "full"},
    "dim_grupo":                 {"mode": "full"},
    "dim_categoria":             {"mode": "full"},
    "dim_classe":                {"mode": "full"},
    "dim_situacao_fatura":       {"mode": "full"},
    "dim_situacao_servico":      {"mode": "full"},
    "dim_agente_arrecadador":    {"mode": "full"},
    "dim_forma_arrecadacao":     {"mode": "full"},
    "dim_leiturista":            {"mode": "full"},
    "dim_equipe":                {"mode": "full"},
    "dim_setor_operacional":     {"mode": "full"},
    "dim_ocorrencia":            {"mode": "full"},
    "dim_servico_definicao":     {"mode": "full"},
}


def _cutoff_date(cfg, out_path):
    """
    Retorna a data de corte para carga incremental.
    Monthly: primeiro dia do mês (hoje - overlap_n meses).
    Daily  : hoje - overlap_n dias.
    Retorna None se o parquet não existir (força carga completa).
    """
    if not out_path.exists():
        return None
    try:
        existing = pd.read_parquet(out_path, columns=[cfg["date_col"]])
        if existing.empty:
            return None
        max_date = pd.to_datetime(existing[cfg["date_col"]]).max()
        if pd.isna(max_date):
            return None
        if cfg["mode"] == "monthly":
            cutoff = (max_date - pd.DateOffset(months=cfg["overlap_n"])).replace(day=1)
        else:  # daily
            cutoff = max_date - pd.Timedelta(days=cfg["overlap_n"])
        return cutoff
    except Exception:
        return None


def _wrap_incremental(query, bq_date_col, cutoff):
    """Envolve a query em subquery adicionando filtro de data."""
    cutoff_str = cutoff.strftime("%Y-%m-%d")
    return f"SELECT * FROM ({query}\n) _t WHERE CAST({bq_date_col} AS DATE) >= '{cutoff_str}'"


def _merge_incremental(existing_path, new_df, date_col, cutoff):
    """
    Combina parquet existente com novos dados:
    1. Remove linhas >= cutoff do parquet atual (serão substituídas).
    2. Concat com new_df.
    3. Ordena por date_col.
    """
    existing = pd.read_parquet(existing_path)
    existing[date_col] = pd.to_datetime(existing[date_col], errors="coerce")
    mask = existing[date_col] < pd.Timestamp(cutoff)
    kept = existing[mask]
    merged = pd.concat([kept, new_df], ignore_index=True)
    try:
        merged = merged.sort_values(date_col).reset_index(drop=True)
    except Exception:
        pass
    return merged


def run_etl(force_full=False):
    log.info("=" * 60)
    log.info(f"ETL iniciado: {datetime.now():%Y-%m-%d %H:%M:%S}")
    log.info(f"Modo: {'CARGA COMPLETA FORÇADA' if force_full else 'INCREMENTAL (full para dims/snapshots)'}")
    client = get_client()
    erros  = []
    stats  = {"full": 0, "incremental": 0, "linhas_novas": 0, "linhas_total": 0}

    for name, query in QUERIES.items():
        out_path = out_path = DATA_DIR / f"{name}.parquet"
        cfg      = INCREMENTAL.get(name, {"mode": "full"})

        try:
            if force_full or cfg["mode"] == "full" or not out_path.exists():
                # ── Carga completa ────────────────────────────────────────────
                log.info(f"[FULL] {name} ...")
                df = client.query(query).to_dataframe()
                _normalize_tz(df)
                df.to_parquet(out_path, index=False, engine="pyarrow")
                log.info(f"  OK {name}: {len(df):,} linhas (full) -> {out_path.name}")
                stats["full"] += 1
                stats["linhas_total"] += len(df)

            else:
                # ── Carga incremental ─────────────────────────────────────────
                cutoff = _cutoff_date(cfg, out_path)
                if cutoff is None:
                    # parquet existe mas sem data válida → full
                    log.info(f"[FULL*] {name} (sem data válida no parquet) ...")
                    df = client.query(query).to_dataframe()
                    _normalize_tz(df)
                    df.to_parquet(out_path, index=False, engine="pyarrow")
                    log.info(f"  OK {name}: {len(df):,} linhas -> {out_path.name}")
                    stats["full"] += 1
                    stats["linhas_total"] += len(df)
                else:
                    bq_col = cfg["bq_date_col"]
                    inc_query = _wrap_incremental(query, bq_col, cutoff)
                    log.info(f"[INC]  {name} (a partir de {cutoff.date()}) ...")
                    new_df = client.query(inc_query).to_dataframe()
                    _normalize_tz(new_df)

                    if new_df.empty:
                        log.info(f"  OK {name}: sem dados novos")
                    else:
                        merged = _merge_incremental(out_path, new_df, cfg["date_col"], cutoff)
                        merged.to_parquet(out_path, index=False, engine="pyarrow")
                        log.info(f"  OK {name}: +{len(new_df):,} novas | {len(merged):,} total -> {out_path.name}")
                        stats["linhas_novas"] += len(new_df)
                        stats["linhas_total"]  += len(merged)
                    stats["incremental"] += 1

        except Exception as e:
            log.error(f"  ERRO {name}: {e}")
            erros.append(name)

    # ── Resumo ────────────────────────────────────────────────────────────────
    log.info("")
    log.info(f"ETL concluído: {datetime.now():%Y-%m-%d %H:%M:%S}")
    log.info(f"  Tabelas full      : {stats['full']}")
    log.info(f"  Tabelas incrementais: {stats['incremental']}")
    log.info(f"  Linhas novas/atualizadas: {stats['linhas_novas']:,}")
    if erros:
        log.warning(f"  Falhas: {', '.join(erros)}")
    else:
        log.info("  Todas as tabelas concluídas com sucesso.")


def _normalize_tz(df):
    """Remove timezone de colunas datetime para compatibilidade com parquet."""
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_localize(None)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="Forcar carga completa de todas as tabelas")
    args = parser.parse_args()
    run_etl(force_full=args.full)
