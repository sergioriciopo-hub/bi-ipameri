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


def run_etl():
    log.info("=" * 60)
    log.info(f"ETL iniciado: {datetime.now():%Y-%m-%d %H:%M:%S}")
    client = get_client()
    erros = []

    for name, query in QUERIES.items():
        out_path = DATA_DIR / f"{name}.parquet"
        try:
            log.info(f"Extraindo: {name} ...")
            df = client.query(query).to_dataframe()

            # Converte datetime BigQuery → pandas datetime sem tz
            for col in df.select_dtypes(include=["datetimetz"]).columns:
                df[col] = df[col].dt.tz_localize(None)

            df.to_parquet(out_path, index=False, engine="pyarrow")
            log.info(f"  OK {name}: {len(df):,} linhas -> {out_path.name}")
        except Exception as e:
            log.error(f"  ✗ {name}: {e}")
            erros.append(name)

    # Resumo
    log.info(f"\nETL concluído: {datetime.now():%Y-%m-%d %H:%M:%S}")
    if erros:
        log.warning(f"Falhas: {', '.join(erros)}")
    else:
        log.info("Todas as tabelas extraídas com sucesso.")


if __name__ == "__main__":
    run_etl()
