"""
Águas de Ipameri — Dashboard BI
Execute: streamlit run app.py
"""

import warnings
warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from datetime import datetime, date, timedelta, time, timezone
from dateutil.relativedelta import relativedelta
from zoneinfo import ZoneInfo

# ── Config ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Águas de Ipameri | BI",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Limpar cache para evitar timestamps desincronizados
if "cache_cleared" not in st.session_state:
    st.cache_data.clear()
    st.session_state.cache_cleared = True

DATA_DIR = Path(__file__).parent / "data"

# ── Paleta ────────────────────────────────────────────────────────────────────
COR = dict(
    azul="#1A6FAD", azul_c="#4FA3D1", azul_esc="#0D3F63",
    verde="#27AE60", vermelho="#E74C3C", amarelo="#F39C12",
    cinza="#7F8C8D", branco="#FFFFFF",
    agua="#1A6FAD", esgoto="#8B5CF6", servico="#F39C12", lixo="#27AE60",
)

SEQ_AZUL = ["#D0E8F8", "#9BC8EC", "#5FA8D8", "#1A6FAD", "#0D3F63"]

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/icon?family=Material+Icons');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

* { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif !important; }

/* oculta toolbar do Streamlit para evitar header cortado */
header[data-testid="stHeader"] {
    height: 0 !important;
    overflow: visible !important;
    padding: 0 !important;
    margin: 0 !important;
}
[data-testid="stToolbar"] {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    z-index: 999 !important;
    height: auto !important;
    background: transparent !important;
    width: 100% !important;
}
#MainMenu { display:none !important; }
footer { display:none !important; }

/* ═══ SIDEBAR ═══════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e4d6d 0%, #2a5f7f 100%) !important;
    border-right: none !important;
    box-shadow: 2px 0 12px rgba(0,0,0,.08) !important;
    overflow-y:auto !important;
}
[data-testid="stSidebar"] .block-container,
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-top:1rem !important; padding-bottom:1rem !important;
    overflow-y:auto !important;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
    margin-bottom:0px !important; margin-top:0px !important;
    padding-top:0px !important; padding-bottom:0px !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] label *,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small { color:rgba(255,255,255,.88) !important; font-size: 0.95rem !important; }
[data-testid="stSidebar"] hr { border-color:rgba(255,255,255,.12) !important; margin: 1rem 0 !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background:rgba(255,255,255,.08) !important;
    border-color:rgba(255,255,255,.16) !important;
    color:white !important; border-radius:10px !important;
    transition: all 0.25s ease !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] svg { fill:white !important; }
[data-testid="stSidebar"] [data-baseweb="popover"] { background:#1e4d6d !important; }
[data-testid="stSidebar"] [data-baseweb="popover"] li { color:white !important; }
[data-testid="stSidebar"] [data-baseweb="popover"] li:hover {
    background:rgba(255,255,255,.08) !important;
}
[data-testid="stSidebar"] button {
    background:rgba(255,255,255,.1) !important;
    color:white !important;
    border:1px solid rgba(255,255,255,.18) !important;
    border-radius:10px !important; width:100% !important;
    transition: all 0.25s ease !important;
    font-weight: 500 !important;
}
[data-testid="stSidebar"] button:hover {
    background:rgba(255,255,255,.15) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,.1) !important;
}
/* ═══ RADIO — BOTÕES DE NAVEGAÇÃO ════════════════════════════════════════════ */
[data-testid="stSidebar"] [data-testid="stRadio"] {
    margin-top: 0.3rem !important;
    margin-bottom: 0.5rem !important;
    width: 100% !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 4px !important;
    overflow: visible !important;
    padding: 0 !important;
    margin: 0 !important;
    display: flex !important;
    flex-direction: column !important;
    width: 100% !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] > div > div {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
}
/* Esconder o input radio nativo (círculo/dot) */
[data-testid="stSidebar"] [data-testid="stRadio"] input[type="radio"] {
    display: none !important;
    width: 0 !important;
    height: 0 !important;
    opacity: 0 !important;
    position: absolute !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    width: 100% !important;
    box-sizing: border-box !important;
    padding: 9px 16px !important;
    border-radius: 10px !important;
    color: rgba(255,255,255,.88) !important;
    font-size: .875rem !important;
    font-weight: 500 !important;
    line-height: 1.3 !important;
    min-height: 38px !important;
    margin: 0 !important;
    cursor: pointer !important;
    transition: background 0.2s ease, box-shadow 0.2s ease, color 0.2s ease !important;
    background: rgba(255,255,255,.08) !important;
    border: 1px solid rgba(255,255,255,.10) !important;
    box-shadow: 0 1px 3px rgba(0,0,0,.12), 0 2px 6px rgba(0,0,0,.08) !important;
    position: relative !important;
    overflow: hidden !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,.15) !important;
    border-color: rgba(255,255,255,.20) !important;
    box-shadow: 0 2px 6px rgba(0,0,0,.16), 0 4px 12px rgba(0,0,0,.10) !important;
    color: white !important;
}
/* Item selecionado — destaque azul vibrante */
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: rgba(255,255,255,.22) !important;
    border-color: rgba(255,255,255,.35) !important;
    box-shadow: 0 2px 8px rgba(0,0,0,.18), 0 4px 14px rgba(0,0,0,.12) !important;
    color: white !important;
    font-weight: 700 !important;
}
/* Linha colorida à esquerda no item ativo */
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked)::before {
    content: "" !important;
    position: absolute !important;
    left: 0 !important;
    top: 20% !important;
    height: 60% !important;
    width: 3px !important;
    background: rgba(255,255,255,.85) !important;
    border-radius: 0 3px 3px 0 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label p,
[data-testid="stSidebar"] [data-testid="stRadio"] label span,
[data-testid="stSidebar"] [data-testid="stRadio"] label div {
    color: inherit !important;
    font-size: inherit !important;
    line-height: inherit !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:empty {
    display: none !important;
}
[data-testid="stSidebar"] h3 {
    margin: 0.5rem 0 0.75rem 0 !important;
    padding: 0 !important;
    font-size: 1.0rem !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] {
    margin-bottom: 1.2rem !important;
}

/* ═══ MAIN BACKGROUND ═══════════════════════════════════════════════════════ */
.stApp { background: linear-gradient(135deg, #f5f9fc 0%, #f0f6fa 100%) !important; }
.block-container {
    padding-top:4.5rem !important; padding-bottom:2.5rem !important;
    max-width:1400px !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* ═══ METRIC CARDS ══════════════════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #ffffff 0%, #fafbfc 100%) !important;
    border-radius:16px !important;
    padding:20px 24px 16px !important;
    box-shadow: 0 1px 6px rgba(0,0,0,.04), 0 4px 12px rgba(13,63,99,.06) !important;
    border:1px solid rgba(26,111,173,.06) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,.06), 0 8px 20px rgba(13,63,99,.12) !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.65rem !important; font-weight: 700 !important;
    color: #0d3f63 !important; letter-spacing: -0.5px !important;
    line-height: 1.2 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.7rem !important; color: #6a8cb5 !important;
    font-weight: 600 !important; text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
    margin-top: 0.5rem !important;
}
[data-testid="stMetricDelta"] { font-size: 0.85rem !important; font-weight: 500 !important; }

/* ═══ HEADINGS ═══════════════════════════════════════════════════════════════ */
h1 { color: #0d3f63 !important; font-weight: 700 !important; font-size: 1.45rem !important; margin: 1.5rem 0 0.75rem !important; }
h2 { color: #1e5580 !important; font-size: 1.15rem !important; font-weight: 600 !important; margin: 1.25rem 0 0.75rem !important; }
h3 { color: #2a5f7f !important; font-size: 1.0rem !important; font-weight: 600 !important; }
h4 { color: #3a6f8f !important; font-size: 0.95rem !important; font-weight: 600 !important; }
p, span, div { line-height: 1.6 !important; }

/* ═══ CHARTS ═════════════════════════════════════════════════════════════════ */
.stPlotlyChart > div {
    background: white !important; border-radius: 16px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.03), 0 4px 12px rgba(13,63,99,.05) !important;
    border: 1px solid rgba(26,111,173,.06) !important;
    padding: 8px !important;
    transition: all 0.3s ease !important;
}
.stPlotlyChart > div:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,.05), 0 8px 16px rgba(13,63,99,.08) !important;
}

/* ═══ DATAFRAMES ═════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border-radius: 14px !important; overflow: hidden !important;
    box-shadow: 0 1px 4px rgba(0,0,0,.03), 0 4px 10px rgba(13,63,99,.05) !important;
    border: 1px solid rgba(26,111,173,.06) !important;
    transition: all 0.3s ease !important;
}
[data-testid="stDataFrame"]:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,.05), 0 8px 16px rgba(13,63,99,.08) !important;
}

/* ═══ EXPANDER ═══════════════════════════════════════════════════════════════ */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, #f8fafb 0%, #f5f8fa 100%) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(26,111,173,.08) !important;
    font-weight: 600 !important; color: #0d3f63 !important;
    transition: all 0.25s ease !important;
    padding: 12px 16px !important;
}
.streamlit-expanderHeader:hover {
    background: linear-gradient(135deg, #f0f4f8 0%, #eff2f7 100%) !important;
    border-color: rgba(26,111,173,.12) !important;
}
.streamlit-expanderContent {
    background: #fafbfc !important;
    border: 1px solid rgba(26,111,173,.06) !important;
    border-top: none !important; border-radius: 0 0 12px 12px !important;
    padding: 16px !important;
}

/* ═══ INPUTS & SELECTIONS ═══════════════════════════════════════════════════ */
input[type="text"], input[type="number"], input[type="date"] {
    border-radius: 10px !important;
    border: 1px solid rgba(26,111,173,.12) !important;
    transition: all 0.25s ease !important;
    padding: 8px 12px !important;
}
input[type="text"]:focus, input[type="number"]:focus, input[type="date"]:focus {
    border-color: rgba(26,111,173,.3) !important;
    box-shadow: 0 0 0 3px rgba(26,111,173,.08) !important;
}

/* ═══ MISC ═══════════════════════════════════════════════════════════════════ */
.stAlert { border-radius: 12px !important; padding: 14px 16px !important; }
[data-baseweb="notification"] { border-radius: 12px !important; }
hr { border-color: rgba(26,111,173,.08) !important; margin: 1.5rem 0 !important; }
.stMarkdown { font-size: 0.95rem !important; }

/* Remove tooltips and descriptions */
[title] { pointer-events: none !important; }
.stTooltip { display: none !important; }

/* Force Material Icons font to load properly on sidebar collapse button */
[data-testid="stBaseButton-headerNoPadding"] span,
[data-testid="stSidebarCollapseButton"] span,
button[kind="headerNoPadding"] span,
[data-testid="stSidebar"] [data-testid="baseButton-headerNoPadding"] span {
    font-family: 'Material Symbols Rounded', 'Material Icons', 'Material Symbols Outlined' !important;
    font-size: 24px !important;
    font-weight: normal !important;
    line-height: 1 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    white-space: nowrap !important;
    direction: ltr !important;
    -webkit-font-feature-settings: 'liga' !important;
    font-feature-settings: 'liga' !important;
    -webkit-font-smoothing: antialiased !important;
}
</style>
""", unsafe_allow_html=True)


# ── Carregamento de dados ─────────────────────────────────────────────────────
@st.cache_data(ttl=60, show_spinner="Carregando dados...")
def load():
    def rd(name):
        import pyarrow.parquet as pq
        import pyarrow as pa
        p = DATA_DIR / f"{name}.parquet"
        if not p.exists():
            return pd.DataFrame()
        # Remove metadata de campo do BigQuery (ex: dbdate) que o pandas não entende
        tbl = pq.read_table(str(p))
        clean_fields = [pa.field(f.name, f.type) for f in tbl.schema]
        df = tbl.cast(pa.schema(clean_fields)).to_pandas()
        for c in df.select_dtypes(include=["datetime64[ns, UTC]", "datetimetz"]).columns:
            df[c] = pd.to_datetime(df[c], utc=True).dt.tz_localize(None)
        for c in df.select_dtypes(include=["datetime64[ns]"]).columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")
        return df

    fat      = rd("faturamento")
    alt_fat  = rd("alteracao_fatura_contabil")
    arr      = rd("arrecadacao")
    arr_d    = rd("arrecadacao_diaria")
    arr_rub  = rd("arrecadacao_rubricas")
    parr     = rd("painel_arrecadacao")
    inad     = rd("pendencia_atual")
    cor      = rd("cortes")
    rel      = rd("religacoes")
    srv      = rd("servicos")
    lei      = rd("leituras")
    bkl      = rd("backlog_servicos")
    d_bairro = rd("dim_bairro")
    d_cat    = rd("dim_categoria")
    d_cls    = rd("dim_classe")
    d_grp    = rd("dim_grupo")
    d_seq    = rd("dim_setor_operacional")
    d_frm    = rd("dim_forma_arrecadacao")
    d_lei    = rd("dim_leiturista")
    d_eqp    = rd("dim_equipe")
    d_agente   = rd("dim_agente_arrecadador")
    d_sit_lig  = rd("dim_situacao_ligacao")
    ene        = rd("energia_consolidada_completa")
    d_uc_ene   = rd("dim_unidade_consumo_energia")
    desc_ene   = rd("desconto_energia")
    frota      = rd("frota_combustivel")
    dim_vei    = rd("dim_veiculo_frota")
    prod_agua  = rd("producao_agua")
    qual_agua  = rd("qualidade_agua")

    # normaliza data_pagamento em arr_d para datetime
    if not arr_d.empty and "data_pagamento" in arr_d.columns:
        arr_d["data_pagamento"] = pd.to_datetime(arr_d["data_pagamento"])

    # normaliza mes_ano em ene para datetime
    if not ene.empty and "mes_ano" in ene.columns:
        ene["mes_ano"] = pd.to_datetime(ene["mes_ano"])
        # Filtrar dados válidos (remover totais mensais ou outros)
        if "uc" in ene.columns:
            ene = ene[~ene["uc"].isna() & (ene["uc"] != "")]

    return dict(
        fat=fat, alt_fat=alt_fat, arr=arr, arr_d=arr_d, arr_rub=arr_rub,
        parr=parr, inad=inad,
        cor=cor, rel=rel, srv=srv, lei=lei, bkl=bkl,
        ene=ene, d_uc_ene=d_uc_ene, desc_ene=desc_ene,
        frota=frota, dim_vei=dim_vei,
        prod_agua=prod_agua, qual_agua=qual_agua,
        d_bairro=d_bairro, d_cat=d_cat, d_cls=d_cls,
        d_grp=d_grp, d_seq=d_seq, d_frm=d_frm,
        d_lei=d_lei, d_eqp=d_eqp, d_agente=d_agente,
        d_sit_lig=d_sit_lig,
    )


def merge_bairro(df, D, col="id_bairro"):
    if col in df.columns and not D["d_bairro"].empty:
        return df.merge(D["d_bairro"][["id_bairro","nm_bairro_dim"]], on=col, how="left")
    return df

def merge_setor(df, D, col="id_setor_operacional"):
    if col in df.columns and not D["d_seq"].empty:
        return df.merge(D["d_seq"][["id_setor_operacional","nm_setor_operacional"]], on=col, how="left")
    return df

def merge_equipe(df, D):
    if "id_equipe" in df.columns and not D["d_eqp"].empty:
        return df.merge(D["d_eqp"][["id_equipe","nm_equipe"]], on="id_equipe", how="left")
    return df

def merge_leiturista(df, D):
    if "id_leiturista" in df.columns and not D["d_lei"].empty:
        return df.merge(D["d_lei"][["id_leiturista","nm_leiturista_dim"]], on="id_leiturista", how="left")
    return df


# ── Filtro de período ─────────────────────────────────────────────────────────
def sidebar_periodo():
    import base64
    logo_path = Path(__file__).parent / "LOGO" / "logo_aguas_de_ipameri_escuro.png"
    if logo_path.exists():
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()
        st.sidebar.markdown(f"""
<div style="padding:0 14px 8px; text-align:center;">
  <img src="data:image/png;base64,{logo_b64}"
       style="width:100%;max-width:110px;height:auto;display:block;margin:0 auto;filter:brightness(0) invert(1);" />
  <div style="font-size:0.56rem;color:rgba(255,255,255,.55);letter-spacing:1.3px;
              text-transform:uppercase;margin-top:6px;">Business Intelligence</div>
</div>
""", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
<div style="text-align:center;padding:28px 0 18px;">
    <div style="font-size:2.6rem;line-height:1;">💧</div>
    <div style="font-size:1.05rem;font-weight:700;color:white;
                margin-top:10px;letter-spacing:.4px;">Águas de Ipameri</div>
    <div style="font-size:0.62rem;color:rgba(255,255,255,.52);
                letter-spacing:1.3px;text-transform:uppercase;
                margin-top:4px;">Business Intelligence</div>
</div>
""", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        '<p style="font-size:.72rem;font-weight:600;text-transform:uppercase;'
        'letter-spacing:.9px;color:rgba(255,255,255,.65);margin:0 0 2px;">Período</p>',
        unsafe_allow_html=True,
    )

    MESES_PT = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]

    opcoes = [
        "Hoje", "Esta Semana", "Este Mês", "Mês Anterior",
        "Este Trimestre", "Trimestre Anterior",
        "Este Semestre", "Semestre Anterior",
        "Este Ano", "Ano Anterior",
        "Últimos 12 Meses", "Últimos 24 Meses",
        "Todo o Histórico",
        "── Comparativos ──",
        "📊 Mês vs Mesmo Mês Ano Anterior",
        "📊 Trimestre vs Trimestre Anterior",
        "Período Personalizado",
    ]
    sel = st.sidebar.selectbox("Periodo", opcoes, index=10, label_visibility="collapsed")

    hoje = date.today()

    # Limpa comparativo por padrão
    st.session_state["comp_periodo"] = {"ativo": False}

    # ── separador não selecionável ────────────────────────────────────────────
    if sel == "── Comparativos ──":
        sel = "Últimos 12 Meses"   # fallback

    if sel == "Hoje":
        d0, d1 = hoje, hoje
    elif sel == "Esta Semana":
        d0 = hoje - timedelta(days=hoje.weekday())
        d1 = hoje
    elif sel == "Este Mês":
        d0 = hoje.replace(day=1)
        d1 = hoje
    elif sel == "Mês Anterior":
        fim = hoje.replace(day=1) - timedelta(days=1)
        d0 = fim.replace(day=1)
        d1 = fim
    elif sel == "Este Trimestre":
        q = (hoje.month - 1) // 3
        d0 = date(hoje.year, q * 3 + 1, 1)
        d1 = hoje
    elif sel == "Trimestre Anterior":
        q = (hoje.month - 1) // 3
        fim = date(hoje.year, q * 3 + 1, 1) - timedelta(days=1)
        d0 = date(fim.year, (fim.month - 1) // 3 * 3 + 1, 1)
        d1 = fim
    elif sel == "Este Semestre":
        d0 = date(hoje.year, 1, 1) if hoje.month <= 6 else date(hoje.year, 7, 1)
        d1 = hoje
    elif sel == "Semestre Anterior":
        if hoje.month <= 6:
            d0 = date(hoje.year - 1, 7, 1)
            d1 = date(hoje.year - 1, 12, 31)
        else:
            d0 = date(hoje.year, 1, 1)
            d1 = date(hoje.year, 6, 30)
    elif sel == "Este Ano":
        d0 = date(hoje.year, 1, 1)
        d1 = hoje
    elif sel == "Ano Anterior":
        d0 = date(hoje.year - 1, 1, 1)
        d1 = date(hoje.year - 1, 12, 31)
    elif sel == "Últimos 12 Meses":
        d0 = (hoje.replace(day=1) - relativedelta(months=11))
        d1 = hoje
    elif sel == "Últimos 24 Meses":
        d0 = (hoje.replace(day=1) - relativedelta(months=23))
        d1 = hoje
    elif sel == "Todo o Histórico":
        d0 = date(2023, 1, 1)
        d1 = hoje

    elif sel == "📊 Mês vs Mesmo Mês Ano Anterior":
        # Gera lista dos últimos 24 meses para o usuário escolher
        _meses_disp = [(hoje.replace(day=1) - relativedelta(months=i)) for i in range(24)]
        _labels = [f"{MESES_PT[m.month-1]}/{m.year}" for m in _meses_disp]
        _idx_default = 1  # mês anterior como padrão
        _sel_label = st.sidebar.selectbox(
            "Mês de referência", _labels, index=_idx_default, label_visibility="visible"
        )
        _mes_ref = _meses_disp[_labels.index(_sel_label)]
        # Período principal: mês escolhido
        d0 = _mes_ref
        import calendar
        d1 = _mes_ref.replace(day=calendar.monthrange(_mes_ref.year, _mes_ref.month)[1])
        # Período comparativo: mesmo mês, ano anterior
        _comp_d0 = d0.replace(year=d0.year - 1)
        _comp_d1 = d1.replace(year=d1.year - 1)
        _lbl_atual = f"{MESES_PT[d0.month-1]}/{d0.year}"
        _lbl_comp  = f"{MESES_PT[_comp_d0.month-1]}/{_comp_d0.year}"
        st.session_state["comp_periodo"] = {
            "ativo": True,
            "tipo": "mes",
            "d0": pd.Timestamp(d0),
            "d1": pd.Timestamp(d1),
            "comp_d0": pd.Timestamp(_comp_d0),
            "comp_d1": pd.Timestamp(_comp_d1),
            "label_atual": _lbl_atual,
            "label_comp":  _lbl_comp,
        }
        # Badge visual no sidebar
        st.sidebar.markdown(
            f"""<div style="background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.18);
            border-radius:10px;padding:8px 12px;margin-top:4px;font-size:.78rem;line-height:1.5;">
            <span style="color:rgba(255,255,255,.6);">Comparando</span><br>
            <b style="color:#7dd3fc;">◉ {_lbl_atual}</b><br>
            <b style="color:#fca5a5;">◉ {_lbl_comp}</b>
            </div>""",
            unsafe_allow_html=True
        )

    elif sel == "📊 Trimestre vs Trimestre Anterior":
        # Gera lista dos últimos 8 trimestres
        _trim_list = []
        for i in range(8):
            _ref = hoje.replace(day=1) - relativedelta(months=i * 3)
            _q   = (_ref.month - 1) // 3 + 1
            _trim_list.append((_ref.year, _q))
        _trim_labels = [f"Q{q}/{ano}" for ano, q in _trim_list]
        _sel_trim = st.sidebar.selectbox(
            "Trimestre de referência", _trim_labels, index=1, label_visibility="visible"
        )
        _ano_sel, _q_sel = _trim_list[_trim_labels.index(_sel_trim)]
        # Período principal: trimestre escolhido
        _m_ini = (_q_sel - 1) * 3 + 1
        d0 = date(_ano_sel, _m_ini, 1)
        _m_fim = _m_ini + 2
        import calendar
        d1 = date(_ano_sel, _m_fim, calendar.monthrange(_ano_sel, _m_fim)[1])
        # Período comparativo: trimestre anterior
        _comp_d0 = d0 - relativedelta(months=3)
        _comp_m_fim = _comp_d0.month + 2
        _comp_d1 = date(_comp_d0.year, _comp_m_fim,
                        calendar.monthrange(_comp_d0.year, _comp_m_fim)[1])
        _lbl_atual = f"Q{_q_sel}/{_ano_sel}"
        _q_comp = (_comp_d0.month - 1) // 3 + 1
        _lbl_comp  = f"Q{_q_comp}/{_comp_d0.year}"
        st.session_state["comp_periodo"] = {
            "ativo": True,
            "tipo": "trimestre",
            "d0": pd.Timestamp(d0),
            "d1": pd.Timestamp(d1),
            "comp_d0": pd.Timestamp(_comp_d0),
            "comp_d1": pd.Timestamp(_comp_d1),
            "label_atual": _lbl_atual,
            "label_comp":  _lbl_comp,
        }
        st.sidebar.markdown(
            f"""<div style="background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.18);
            border-radius:10px;padding:8px 12px;margin-top:4px;font-size:.78rem;line-height:1.5;">
            <span style="color:rgba(255,255,255,.6);">Comparando</span><br>
            <b style="color:#7dd3fc;">◉ {_lbl_atual}</b><br>
            <b style="color:#fca5a5;">◉ {_lbl_comp}</b>
            </div>""",
            unsafe_allow_html=True
        )

    else:  # Período Personalizado
        c1, c2 = st.sidebar.columns(2)
        d0 = c1.date_input("De", value=hoje.replace(day=1), format="DD/MM/YYYY")
        d1 = c2.date_input("Até", value=hoje, format="DD/MM/YYYY")

    return pd.Timestamp(d0), pd.Timestamp(d1)


def filtrar(df, col, d0, d1):
    """Filtra pelo período [d0, d1] inclusive. Usa < d1+1d para não capturar
    registros mensais cujo dt_ref = primeiro dia do mês seguinte."""
    if df.empty or col not in df.columns:
        return df
    s = pd.to_datetime(df[col])
    return df[(s >= d0) & (s < d1 + pd.Timedelta(days=1))]


def _comp_periodo():
    """Retorna dict do período comparativo se ativo, ou None."""
    c = st.session_state.get("comp_periodo", {})
    return c if c.get("ativo") else None


def render_comp_bloco(lbl_atual, lbl_comp, rows):
    """
    Renderiza tabela comparativa entre dois períodos.
    rows = lista de (nome, val_atual, val_comp, fmt_fn, maior_melhor)
      fmt_fn(v) → str  |  maior_melhor: True=▲verde, False=▲vermelho, None=neutro
    """
    def _dp(v_a, v_c):
        if v_c is None or v_c == 0:
            return None
        return (v_a - v_c) / abs(v_c)

    def _fmt_delta(d, maior_melhor):
        if d is None:
            return "—"
        positivo = d > 0
        bom = (positivo and maior_melhor) or (not positivo and maior_melhor is False)
        cor = "#16a34a" if bom else ("#dc2626" if maior_melhor is not None else "#6b7280")
        sinal = "▲" if positivo else "▼"
        return f'<span style="color:{cor};font-weight:600;">{sinal} {abs(d):.1%}</span>'

    _html_rows = ""
    for nome, va, vc, fmt_fn, melhor in rows:
        _ta = fmt_fn(va) if va is not None else "—"
        _tc = fmt_fn(vc) if vc is not None else "—"
        _d  = _fmt_delta(_dp(va if va else 0, vc if vc else 0), melhor)
        _html_rows += (
            f'<tr style="border-top:1px solid rgba(26,111,173,.06);">'
            f'<td style="padding:7px 12px;color:#374151;font-size:.83rem;">{nome}</td>'
            f'<td style="padding:7px 12px;text-align:right;font-weight:700;color:#1A6FAD;font-size:.85rem;">{_ta}</td>'
            f'<td style="padding:7px 12px;text-align:right;color:#6b7280;font-size:.83rem;">{_tc}</td>'
            f'<td style="padding:7px 12px;text-align:right;font-size:.8rem;min-width:70px;">{_d}</td>'
            f'</tr>'
        )

    st.markdown(f"""
<div style="background:white;border-radius:14px;border:1px solid rgba(26,111,173,.10);
     box-shadow:0 2px 8px rgba(0,0,0,.05);overflow:hidden;margin:4px 0 12px;">
  <div style="background:linear-gradient(135deg,#f0f6fb,#e8f3fb);padding:8px 12px;
       display:flex;align-items:center;gap:10px;border-bottom:1px solid rgba(26,111,173,.08);">
    <span style="font-size:.72rem;font-weight:700;text-transform:uppercase;
          letter-spacing:.7px;color:#1A6FAD;">📊 Comparativo de Período</span>
  </div>
  <table style="width:100%;border-collapse:collapse;">
    <thead>
      <tr style="background:#fafcff;">
        <th style="padding:7px 12px;text-align:left;font-size:.72rem;font-weight:700;
                   text-transform:uppercase;letter-spacing:.5px;color:#64748b;">Indicador</th>
        <th style="padding:7px 12px;text-align:right;font-size:.72rem;font-weight:700;
                   text-transform:uppercase;letter-spacing:.5px;color:#1A6FAD;">◉ {lbl_atual}</th>
        <th style="padding:7px 12px;text-align:right;font-size:.72rem;font-weight:700;
                   text-transform:uppercase;letter-spacing:.5px;color:#dc2626;">◉ {lbl_comp}</th>
        <th style="padding:7px 12px;text-align:right;font-size:.72rem;font-weight:700;
                   text-transform:uppercase;letter-spacing:.5px;color:#64748b;">Δ Var.</th>
      </tr>
    </thead>
    <tbody>{_html_rows}</tbody>
  </table>
</div>
""", unsafe_allow_html=True)


def arr_d_por_credito(D, d0, d1):
    """Retorna arr_d filtrado pelo data_pagamento em [d0, d1] com data_credito D+ calculada.
    Sábado → crédito segunda (+2 dias), domingo → crédito segunda (+1 dia).
    Filtra por data_pagamento (não data_credito) para que pagamentos de fim de mês
    fiquem no mês de origem, consistente com o relatório do sistema."""
    ad = D["arr_d"].copy()
    if ad.empty:
        return ad
    ad["data_pagamento"] = pd.to_datetime(ad["data_pagamento"])

    ad["data_credito"] = ad["data_pagamento"].apply(calc_data_credito)
    return ad[(ad["data_pagamento"] >= d0) & (ad["data_pagamento"] < d1 + pd.Timedelta(days=1))]


# Feriados nacionais fixos (mês, dia) — adicione municipais/estaduais se necessário
_FERIADOS_FIXOS = {
    (1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (11, 20), (12, 25),
}
# Feriados móveis calculados (Carnaval = -47d, Sexta Santa = -2d, Corpus Christi = +60d da Páscoa)
# Páscoa calculada pelo algoritmo de Butcher
def _pascoa(ano):
    a = ano % 19; b = ano // 100; c = ano % 100
    d = b // 4;   e = b % 4;     f = (b + 8) // 25
    g = (b - f + 1) // 3;        h = (19*a + b - d - g + 15) % 30
    i = c // 4;   k = c % 4;     l = (32 + 2*e + 2*i - h - k) % 7
    m = (a + 11*h + 22*l) // 451
    mes = (h + l - 7*m + 114) // 31
    dia = ((h + l - 7*m + 114) % 31) + 1
    return date(ano, mes, dia)

def _feriados_ano(ano):
    from datetime import timedelta
    p = _pascoa(ano)
    moveis = {(p - timedelta(47)).timetuple()[1:3],   # Carnaval 2ª
              (p - timedelta(48)).timetuple()[1:3],   # Carnaval 3ª (opcional)
              (p - timedelta(2)).timetuple()[1:3],    # Sexta-feira Santa
              (p + timedelta(60)).timetuple()[1:3]}   # Corpus Christi
    return _FERIADOS_FIXOS | moveis

def _proximo_dia_util(d):
    """Retorna o próximo dia útil após d (exclusive), respeitando fds e feriados."""
    prox = pd.Timestamp(d) + pd.Timedelta(days=1)
    feriados = _feriados_ano(prox.year)
    while prox.weekday() >= 5 or (prox.month, prox.day) in feriados:
        prox += pd.Timedelta(days=1)
        if prox.year != (prox - pd.Timedelta(days=1)).year:
            feriados = _feriados_ano(prox.year)
    return prox

def calc_data_credito(data_pag):
    """Nova lógica D+: fds/feriado → próximo dia útil; se cruzar mês → mantém no mês do pagamento."""
    d = pd.Timestamp(data_pag)
    feriados = _feriados_ano(d.year)
    eh_nao_util = d.weekday() >= 5 or (d.month, d.day) in feriados
    if not eh_nao_util:
        return d
    proximo = _proximo_dia_util(d)
    if proximo.month != d.month:
        return d   # Protege o mês: mantém na data original
    return proximo

def _eh_expediente(dt):
    """True se dt cai em dia útil (seg-sex, não feriado) entre 08:00 e 18:00."""
    if pd.isna(dt):
        return False
    ts = pd.Timestamp(dt)
    if ts.weekday() >= 5:
        return False
    feriados = _feriados_ano(ts.year)
    if (ts.month, ts.day) in feriados:
        return False
    return time(8, 0) <= ts.time() < time(18, 0)

def calcular_sla_religacao(rel_df):
    """Adiciona fl_no_prazo_rel e prazo_horas ao dataframe de religações.
    SLA = dt_fim_execucao - dt_solicitacao (tempo da empresa para executar após pedido).
    Normal: 24h | Urgente expediente (seg-sex 08-18h): 6h | Urgente fora: 14h
    Expediente avaliado em dt_solicitacao."""
    if rel_df.empty or "dt_solicitacao" not in rel_df.columns or "dt_fim_execucao" not in rel_df.columns:
        return rel_df
    rel = rel_df.copy()
    rel["_dt_sol"] = pd.to_datetime(rel["dt_solicitacao"])
    rel["_dt_fim"] = pd.to_datetime(rel["dt_fim_execucao"])

    def _prazo(row):
        if row.get("id_servico_definicao") == 329:
            return 6 if _eh_expediente(row["_dt_sol"]) else 14
        return 24

    rel["prazo_horas"]     = rel.apply(_prazo, axis=1)
    rel["dt_limite_rel"]   = rel["_dt_sol"] + pd.to_timedelta(rel["prazo_horas"], unit="h")
    rel["fl_no_prazo_rel"] = rel["_dt_fim"] <= rel["dt_limite_rel"]
    return rel.drop(columns=["_dt_sol", "_dt_fim"])


# ── Helpers de visual ─────────────────────────────────────────────────────────
def fmt_brl(v):
    if v is None or (isinstance(v, float) and v != v):
        return "R$ 0"
    return f"R$ {v:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

def fmt_pct(v):
    if v is None or (isinstance(v, float) and v != v):
        return "0,0%"
    return f"{v:.1%}".replace(".", ",")

def kpi(col, label, valor, delta=None, delta_inv=False, prefixo="R$"):
    if prefixo == "R$":
        vstr = fmt_brl(valor)
    elif prefixo == "%":
        vstr = fmt_pct(valor)
    else:
        vstr = f"{valor:,.0f}".replace(",", ".") if valor else "0"

    dstr = None
    delta_html = ""
    if delta is not None:
        sinal = "+" if delta >= 0 else ""
        dstr = f"{sinal}{delta:.1%}".replace(".", ",") + " vs período ant."
        delta_color = "#0ABF53" if not delta_inv else "#FF2B2B"
        delta_html = f'<div style="font-size:0.52rem;color:{delta_color};margin-top:1px;">{dstr}</div>'

    html = f"""
    <div style="
        background:linear-gradient(135deg, rgba(100,150,200,0.08) 0%, rgba(100,150,200,0.02) 100%);
        border:1px solid rgba(100,150,200,0.15);
        border-radius:10px;
        padding:8px 10px;
        margin-bottom:4px;
        box-shadow:0 2px 8px rgba(0,0,0,0.06);
    ">
        <div style="font-size:0.8rem;color:rgba(0,0,0,0.6);margin-bottom:3px;font-weight:500;">{label}</div>
        <div style="font-size:1.2rem;font-weight:700;color:#0B3558;line-height:1.1;">{vstr}</div>
        {delta_html}
    </div>
    """
    col.markdown(html, unsafe_allow_html=True)


def kpi_str(col, label, vstr, help=None):
    """KPI com valor já formatado como string — mesma caixa visual do kpi()."""
    help_icon = f' <span title="{help}" style="cursor:help;color:rgba(0,0,0,0.35);">ⓘ</span>' if help else ""
    html = f"""
    <div style="
        background:linear-gradient(135deg, rgba(100,150,200,0.08) 0%, rgba(100,150,200,0.02) 100%);
        border:1px solid rgba(100,150,200,0.15);
        border-radius:10px;
        padding:8px 10px;
        margin-bottom:4px;
        box-shadow:0 2px 8px rgba(0,0,0,0.06);
    ">
        <div style="font-size:0.8rem;color:rgba(0,0,0,0.6);margin-bottom:3px;font-weight:500;">{label}{help_icon}</div>
        <div style="font-size:1.2rem;font-weight:700;color:#0B3558;line-height:1.1;">{vstr}</div>
    </div>
    """
    col.markdown(html, unsafe_allow_html=True)


def bar_mensal(df, col_data, col_val, title, cor=None, agrupamento="M"):
    if df.empty:
        return go.Figure()
    tmp = df.copy()
    tmp["_mes"] = pd.to_datetime(tmp[col_data]).dt.to_period(agrupamento).dt.to_timestamp()
    ag = tmp.groupby("_mes")[col_val].sum().reset_index()
    ag.columns = ["Mês", "Valor"]
    fig = px.bar(ag, x="Mês", y="Valor", title=title,
                 color_discrete_sequence=[cor or COR["azul"]],
                 text=ag["Valor"].apply(lambda v: f"<b>{v:,.0f} m³</b>".replace(",", ".")))
    fig.update_traces(textposition="inside", textangle=-90,
                      textfont=dict(size=14, color="white", family="Arial Black"),
                      insidetextanchor="middle")
    # Linha de média
    media = ag["Valor"].mean()
    cor_linha = cor or COR["azul"]
    fig.add_hline(y=media, line_dash="dash", line_color=cor_linha, line_width=1.8)
    fig.add_annotation(
        xref="paper", yref="y", x=0, y=media,
        text=f"<b>Média: {media:,.0f}".replace(",", ".") + "</b>",
        showarrow=False, xanchor="left", yanchor="bottom",
        font=dict(size=12, color=cor_linha, family="Arial Black"),
        bgcolor="rgba(255,255,255,0.75)", borderpad=2,
    )
    fig.update_layout(xaxis_title="", yaxis_title="", showlegend=False,
                      margin=dict(t=35, b=0, l=0, r=20),
                      uniformtext_minsize=9, uniformtext_mode="hide")
    fig.update_yaxes(tickformat=",.0f")
    return fig


def line_mensal(df, col_data, col_val, title, cor=None):
    if df.empty:
        return go.Figure()
    tmp = df.copy()
    tmp["_mes"] = pd.to_datetime(tmp[col_data]).dt.to_period("M").dt.to_timestamp()
    ag = tmp.groupby("_mes")[col_val].sum().reset_index()
    ag.columns = ["Mês", "Valor"]
    fig = px.line(ag, x="Mês", y="Valor", title=title, markers=True,
                  color_discrete_sequence=[cor or COR["azul"]])
    fig.update_layout(xaxis_title="", yaxis_title="", showlegend=False,
                      margin=dict(t=35, b=0, l=0, r=20))
    return fig


# ── Header executivo por página ───────────────────────────────────────────────
_PG_CORES = {
    "Executivo":                         ("#3E5F7F", "#5B8FB8"),
    "Faturamento e Medição":             ("#3E5F7F", "#5B8FB8"),
    "Arrecadação (Série Histórica)":     ("#3E5F7F", "#5B8FB8"),
    "Boletim de Arrecadação Diária":     ("#3E5F7F", "#5B8FB8"),
    "Inadimplência":                     ("#3E5F7F", "#5B8FB8"),
    "Serviços Operacionais":             ("#3E5F7F", "#5B8FB8"),
    "Cobrança e Recuperação de Receita": ("#3E5F7F", "#5B8FB8"),
    "Leituras e Hidrômetros":            ("#3E5F7F", "#5B8FB8"),
    "Frota Combustível":                 ("#3E5F7F", "#5B8FB8"),
    "Energia Elétrica":                  ("#3E5F7F", "#5B8FB8"),
    "Setores Operacionais":              ("#3E5F7F", "#5B8FB8"),
    "Tratamento":                        ("#0E6655", "#1A9278"),
}

def page_header(titulo, periodo_str=""):
    c1, c2 = _PG_CORES.get(titulo, ("#3E5F7F", "#5B8FB8"))
    per = (
        f'<div style="font-size:.90rem;color:white;font-weight:500;margin-top:6px;">'
        f'{periodo_str}</div>'
        if periodo_str else ""
    )
    st.markdown(
        f"""<div style="
            background:linear-gradient(135deg,{c1} 0%,{c2} 100%);
            border-radius:12px; padding:14px 20px 10px;
            margin-bottom:12px;
            box-shadow:0 2px 12px rgba(13,63,99,.15);">
          <div style="color:white;font-size:1.15rem;font-weight:700;
                      letter-spacing:-.2px;">{titulo}</div>
          {per}
        </div>""",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PÁGINAS
# ═══════════════════════════════════════════════════════════════════════════════

def pg_cockpit(D, d0, d1):
    page_header("Executivo",
                f"{d0.strftime('%d/%m/%Y')} a {d1.strftime('%d/%m/%Y')}")

    # ── Dados filtrados pelo período da sidebar ──────────────────────────────
    fat      = filtrar(D["fat"],  "dt_ref",          d0, d1)
    arr_d_f  = arr_d_por_credito(D, d0, d1)
    inad     = D["inad"]
    srv      = filtrar(D["srv"], "dt_solicitacao",   d0, d1)
    cor_exec = filtrar(D["cor"], "dt_fim_execucao",  d0, d1)
    if not cor_exec.empty and "id_servico_definicao" in cor_exec.columns:
        cor_exec = cor_exec[cor_exec["id_servico_definicao"] == 30]

    # ── KPIs ─────────────────────────────────────────────────────────────────
    vl_fat  = fat["vl_total_faturado"].sum()     if not fat.empty     else 0
    vl_arr  = arr_d_f["vl_arrecadado"].sum()     if not arr_d_f.empty else 0
    vl_inad = inad["vl_divida"].sum()            if not inad.empty    else 0
    idx_arr = vl_arr / vl_fat if vl_fat else None
    qtd_cor = int(cor_exec["id_servico"].nunique()) if not cor_exec.empty and "id_servico" in cor_exec.columns else 0
    qtd_sla = int(srv["qt_servico"].sum())       if not srv.empty else 0
    qtd_fpr = int(srv[srv["fl_fora_prazo"] == True]["qt_servico"].sum()) if not srv.empty else 0
    sla_ok  = (qtd_sla - qtd_fpr) / qtd_sla     if qtd_sla else 0
    qtd_lig = int(fat["nr_economia_agua"].sum()) if not fat.empty and "nr_economia_agua" in fat.columns else 0

    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Faturamento",   vl_fat)
    kpi(c2, "Arrecadação",   vl_arr)
    if idx_arr is not None:
        kpi(c3, "Eficiência Arrec.", idx_arr, prefixo="%")
    else:
        c3.metric("Eficiência Arrec.", "—")
    kpi(c4, "Inadimplência", vl_inad)

    c5, c6, c7, c8 = st.columns(4)
    kpi(c5, "Cortes Executados", qtd_cor, prefixo="")
    kpi(c6, "SLA Serviços", sla_ok, delta=sla_ok - 0.9, prefixo="%")
    kpi(c7, "Total Ligações", qtd_lig, prefixo="")
    c8.empty()

    # ── Bloco comparativo ─────────────────────────────────────────────────────
    _comp = _comp_periodo()
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _fat_c  = filtrar(D["fat"], "dt_ref", _cd0, _cd1)
        _arr_c2 = filtrar(D["arr_d"], "data_pagamento", _cd0, _cd1)
        _cor_c  = filtrar(D["cor"], "dt_fim_execucao", _cd0, _cd1)
        if not _cor_c.empty and "id_servico_definicao" in _cor_c.columns:
            _cor_c = _cor_c[_cor_c["id_servico_definicao"] == 30]
        _vf_c = _fat_c["vl_total_faturado"].sum() if not _fat_c.empty else 0
        _va_c = _arr_c2["vl_arrecadado"].sum()    if not _arr_c2.empty else 0
        _ei_c = _va_c / _vf_c if _vf_c else None
        _co_c = int(_cor_c["id_servico"].nunique()) if not _cor_c.empty and "id_servico" in _cor_c.columns else 0
        _brl  = lambda v: f"R$ {v:,.0f}".replace(",","X").replace(".",",").replace("X",".")
        render_comp_bloco(_comp["label_atual"], _comp["label_comp"], [
            ("Faturamento",       vl_fat,  _vf_c, _brl,                    True),
            ("Arrecadação",       vl_arr,  _va_c, _brl,                    True),
            ("Efic. Arrecadação", idx_arr, _ei_c, lambda v: f"{v:.1%}" if v else "—", True),
            ("Cortes Exec.",      qtd_cor, _co_c, lambda v: str(int(v)),   False),
        ])

    st.markdown("---")

    def _sort_meses(lst):
        return sorted(lst, key=lambda x: pd.to_datetime(x, format="%m/%Y"))

    # ══════════════════════════════════════════════════════════════════════════
    # 1 — Faturamento e Arrecadação Mensal
    # ══════════════════════════════════════════════════════════════════════════
    fat_m, arr_m = pd.DataFrame(), pd.DataFrame()
    if not fat.empty:
        tmp = fat.copy()
        tmp["Mês"] = pd.to_datetime(tmp["dt_ref"]).dt.strftime("%m/%Y")
        fat_m = tmp.groupby("Mês")["vl_total_faturado"].sum().reset_index()
        fat_m.columns = ["Mês", "Valor"]
    if not arr_d_f.empty:
        tmp = arr_d_f.copy()
        tmp["Mês"] = pd.to_datetime(tmp["data_pagamento"]).dt.strftime("%m/%Y")
        arr_m = tmp.groupby("Mês")["vl_arrecadado"].sum().reset_index()
        arr_m.columns = ["Mês", "Valor"]

    # Carrega dados comp para os gráficos
    _comp = _comp_periodo()
    fat_c_m, arr_c_m = pd.DataFrame(), pd.DataFrame()
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _fat_c2 = filtrar(D["fat"], "dt_ref", _cd0, _cd1)
        _arrd_c2 = filtrar(D["arr_d"], "data_pagamento", _cd0, _cd1)
        if not _fat_c2.empty:
            tmp = _fat_c2.copy(); tmp["Mês"] = pd.to_datetime(tmp["dt_ref"]).dt.strftime("%m/%Y")
            fat_c_m = tmp.groupby("Mês")["vl_total_faturado"].sum().reset_index()
            fat_c_m.columns = ["Mês", "Valor"]
        if not _arrd_c2.empty:
            tmp = _arrd_c2.copy(); tmp["Mês"] = pd.to_datetime(tmp["data_pagamento"]).dt.strftime("%m/%Y")
            arr_c_m = tmp.groupby("Mês")["vl_arrecadado"].sum().reset_index()
            arr_c_m.columns = ["Mês", "Valor"]

    todos = _sort_meses(list(set(
        (fat_m["Mês"].tolist() if not fat_m.empty else []) +
        (arr_m["Mês"].tolist() if not arr_m.empty else []) +
        (fat_c_m["Mês"].tolist() if not fat_c_m.empty else []) +
        (arr_c_m["Mês"].tolist() if not arr_c_m.empty else [])
    )))
    if todos:
        fig1 = go.Figure()
        vf = fat_m.set_index("Mês").reindex(todos)["Valor"].fillna(0) if not fat_m.empty else pd.Series([0]*len(todos), index=todos)
        va = arr_m.set_index("Mês").reindex(todos)["Valor"].fillna(0) if not arr_m.empty else pd.Series([0]*len(todos), index=todos)
        label_fat = f"Faturamento {_comp['label_atual'] if _comp else ''}".strip()
        label_arr = f"Arrecadação {_comp['label_atual'] if _comp else ''}".strip()
        if not fat_m.empty:
            fig1.add_trace(go.Bar(
                x=todos, y=vf, name=label_fat,
                marker_color=COR["azul"], opacity=0.9,
                text=[f"<b>{v/1000:.0f}k</b>" if v > 0 else "" for v in vf],
                textposition="inside", textangle=-90,
                textfont=dict(size=14, color="white"),
                insidetextanchor="middle",
            ))
        if not arr_m.empty:
            fig1.add_trace(go.Bar(
                x=todos, y=va, name=label_arr,
                marker_color=COR["verde"], opacity=0.9,
                text=[f"<b>{v/1000:.0f}k</b>" if v > 0 else "" for v in va],
                textposition="inside", textangle=-90,
                textfont=dict(size=14, color="white"),
                insidetextanchor="middle",
            ))
        if _comp and not fat_c_m.empty:
            vfc = fat_c_m.set_index("Mês").reindex(todos)["Valor"].fillna(0)
            fig1.add_trace(go.Bar(
                x=todos, y=vfc, name=f"Faturamento {_comp['label_comp']}",
                marker_color=COR["azul"], opacity=0.40,
                marker_pattern_shape="/",
                text=[f"<b>{v/1000:.0f}k</b>" if v > 0 else "" for v in vfc],
                textposition="inside", textangle=-90,
                textfont=dict(size=15, color="#0d2e50", family="Arial Black"),
                insidetextanchor="middle",
            ))
        if _comp and not arr_c_m.empty:
            vac = arr_c_m.set_index("Mês").reindex(todos)["Valor"].fillna(0)
            fig1.add_trace(go.Bar(
                x=todos, y=vac, name=f"Arrecadação {_comp['label_comp']}",
                marker_color=COR["verde"], opacity=0.40,
                marker_pattern_shape="/",
                text=[f"<b>{v/1000:.0f}k</b>" if v > 0 else "" for v in vac],
                textposition="inside", textangle=-90,
                textfont=dict(size=15, color="#0d3320", family="Arial Black"),
                insidetextanchor="middle",
            ))
        # Linhas de média
        vf_nonzero = vf[vf > 0]
        va_nonzero = va[va > 0]
        annotations_medias = []
        media_fat = media_arr = None
        if len(vf_nonzero) > 0:
            media_fat = vf_nonzero.mean()
            fig1.add_hline(y=media_fat, line_dash="dash", line_color=COR["azul"], line_width=1.5)
        if len(va_nonzero) > 0:
            media_arr = va_nonzero.mean()
            fig1.add_hline(y=media_arr, line_dash="dash", line_color=COR["verde"], line_width=1.5)
        # Texto das médias posicionado logo abaixo do título (yref=paper, topo do plot)
        if media_fat is not None:
            annotations_medias.append(dict(
                xref="paper", yref="paper", x=0.0, y=1.06,
                text=f"<b>── Média Fat.: R$ {media_fat/1000:.0f}k</b>",
                showarrow=False, xanchor="left", yanchor="top",
                font=dict(size=12, color=COR["azul"]),
            ))
        if media_arr is not None:
            annotations_medias.append(dict(
                xref="paper", yref="paper", x=0.5, y=1.06,
                text=f"<b>── Média Arrec.: R$ {media_arr/1000:.0f}k</b>",
                showarrow=False, xanchor="center", yanchor="top",
                font=dict(size=12, color="#1a6b3c"),
            ))
        fig1.update_layout(
            title="Faturamento × Arrecadação (R$)" + (f" — {_comp['label_atual']} vs {_comp['label_comp']}" if _comp else ""),
            barmode="group",
            margin=dict(t=70, b=60, l=0, r=30), height=450,
            annotations=annotations_medias,
            xaxis=dict(title="", categoryorder="array", categoryarray=todos),
            yaxis=dict(title="", tickformat=",.0f"),
            legend=dict(
                orientation="h", yanchor="top", y=-0.12,
                xanchor="center", x=0.5,
                font=dict(size=12),
            ),
            hovermode="x unified",
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Sem dados de faturamento/arrecadação no período.")

    # ══════════════════════════════════════════════════════════════════════════
    # 2 — Economias Ativas + Cortadas
    # ══════════════════════════════════════════════════════════════════════════
    if not fat.empty and "nr_economia_agua" in fat.columns:
        eco = fat.copy()
        eco["Mês"] = pd.to_datetime(eco["dt_ref"]).dt.strftime("%m/%Y")
        eco_m = eco.groupby("Mês").agg(
            Agua   =("nr_economia_agua",   "sum"),
            Esgoto =("nr_economia_esgoto", "sum"),
        ).reset_index()
        meses_eco = _sort_meses(eco_m["Mês"].tolist())
        eco_m = eco_m.set_index("Mês").reindex(meses_eco).reset_index()
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=eco_m["Mês"], y=eco_m["Agua"], name="Economias Água",
            mode="lines+markers+text",
            text=eco_m["Agua"].apply(lambda v: f"{int(v):,}".replace(",", ".")),
            textposition="top center", textfont=dict(size=13),
            line=dict(color=COR["azul"], width=2), marker=dict(size=5),
        ))
        # Adiciona Esgoto apenas se houver dados
        if eco_m["Esgoto"].sum() > 0:
            fig2.add_trace(go.Scatter(
                x=eco_m["Mês"], y=eco_m["Esgoto"], name="Economias Esgoto",
                mode="lines+markers+text",
                text=eco_m["Esgoto"].apply(lambda v: f"{int(v):,}".replace(",", ".")),
                textposition="bottom center", textfont=dict(size=13),
                line=dict(color=COR["amarelo"], width=2), marker=dict(size=5),
            ))
        fig2.update_layout(
            title="Economias Ativas + Cortadas Cavalete",
            margin=dict(t=70, b=10, l=0, r=30), height=400,
            xaxis=dict(title="", categoryorder="array", categoryarray=meses_eco),
            yaxis=dict(title=""),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 3 — Fatura Média por Economia (R$/Economia)
    # ══════════════════════════════════════════════════════════════════════════
    if not fat.empty and "nr_economia_agua" in fat.columns:
        fm = fat.copy()
        fm["Mês"] = pd.to_datetime(fm["dt_ref"]).dt.strftime("%m/%Y")
        cols_agg = {
            "vl_agua": ("vl_agua",                   "sum"),
            "vl_esgo": ("vl_esgoto",                 "sum"),
            "nr_eco":  ("nr_economia_agua",          "sum"),
        }
        if "vl_servico_basico_agua" in fm.columns:
            cols_agg["vl_tbas_a"] = ("vl_servico_basico_agua", "sum")
        if "vl_servico_basico_esgoto" in fm.columns:
            cols_agg["vl_tbas_e"] = ("vl_servico_basico_esgoto", "sum")
        if "vl_lixo" in fm.columns:
            cols_agg["vl_lixo"] = ("vl_lixo", "sum")
        if "vl_servico" in fm.columns:
            cols_agg["vl_serv"] = ("vl_servico", "sum")

        agg = fm.groupby("Mês").agg(**cols_agg).reset_index()
        agg = agg[agg["nr_eco"] > 0]

        agg["vl_tbas_a"] = agg.get("vl_tbas_a", 0).fillna(0)
        agg["vl_tbas_e"] = agg.get("vl_tbas_e", 0).fillna(0)
        agg["vl_lixo"] = agg.get("vl_lixo", 0).fillna(0)
        agg["vl_serv"] = agg.get("vl_serv", 0).fillna(0)
        agg["vl_srv_div"] = agg["vl_serv"] - agg["vl_lixo"] - agg["vl_tbas_a"] - agg["vl_tbas_e"]
        agg["vl_srv_div"] = agg["vl_srv_div"].clip(lower=0)

        meses_fm = _sort_meses(agg["Mês"].tolist())
        agg = agg.set_index("Mês").reindex(meses_fm).reset_index()

        fig3 = go.Figure()
        series_fm = [
            ("Faturamento Total",       (agg["vl_agua"] + agg["vl_tbas_a"]) / agg["nr_eco"], "#1A6FAD", "top center", 4),
            ("Consumo Água",            agg["vl_agua"] / agg["nr_eco"], "#2E7FD6", "top center", 2),
            ("Produção Esgoto",         agg["vl_esgo"] / agg["nr_eco"], "#8B4513", "bottom center", 2),
            ("Tarifa Básica + Serviços", (agg["vl_tbas_a"] + agg["vl_srv_div"]) / agg["nr_eco"], "#FF9F43", "top center", 2),
            ("Tarifa Básica Esgoto",    agg["vl_tbas_e"] / agg["nr_eco"], "#A0622D", "bottom center", 2),
            ("Lixo",                    agg["vl_lixo"] / agg["nr_eco"], "#E74C3C", "bottom center", 2),
            ("Serviços Diversos",       agg["vl_srv_div"] / agg["nr_eco"], COR["amarelo"], "top center", 2),
        ]

        for idx, (nome, vals, cor_v, textpos, width) in enumerate(series_fm):
            if vals.sum() > 0:
                fig3.add_trace(go.Scatter(
                    x=meses_fm, y=vals.round(1), name=nome,
                    mode="lines+markers+text",
                    text=vals.round(1).apply(lambda v: f"{v:.1f}" if v > 0 else ""),
                    textposition=textpos, textfont=dict(size=13),
                    line=dict(color=cor_v, width=width), marker=dict(size=4),
                    visible=(idx < 4),
                ))

        fig3.update_layout(
            title=dict(
                text="Fatura Média por Economia (R$/Economia) <span style='font-size:0.8em;cursor:help;'>ℹ️</span>",
                x=0.0, xanchor="left"
            ),
            margin=dict(t=70, b=10, l=0, r=30), height=400,
            xaxis=dict(title="", categoryorder="array", categoryarray=meses_fm),
            yaxis=dict(title=""),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            hovermode="x unified",
        )
        st.plotly_chart(fig3, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 4 — Volume Faturado por Economia (m³/Economia)
    # ══════════════════════════════════════════════════════════════════════════
    if not fat.empty and "nr_economia_agua" in fat.columns:
        vf2 = fat.copy()
        vf2["Mês"] = pd.to_datetime(vf2["dt_ref"]).dt.strftime("%m/%Y")
        has_ev = "volume_esgoto_m3" in vf2.columns
        cols_v = {
            "vol_a": ("volume_m3",          "sum"),
            "nr_ea": ("nr_economia_agua",   "sum"),
            "nr_ee": ("nr_economia_esgoto", "sum"),
        }
        if has_ev:
            cols_v["vol_e"] = ("volume_esgoto_m3", "sum")
        agg_v = vf2.groupby("Mês").agg(**cols_v).reset_index()
        agg_v = agg_v[agg_v["nr_ea"] > 0]
        meses_vf = _sort_meses(agg_v["Mês"].tolist())
        agg_v = agg_v.set_index("Mês").reindex(meses_vf).reset_index()
        fig4 = go.Figure()
        y_agua = (agg_v["vol_a"] / agg_v["nr_ea"]).round(1)
        fig4.add_trace(go.Scatter(
            x=meses_vf, y=y_agua, name="Água",
            mode="lines+markers+text",
            text=y_agua.apply(lambda v: f"{v:.1f}"),
            textposition="top center", textfont=dict(size=13),
            line=dict(color=COR["azul"], width=2), marker=dict(size=4),
        ))
        if has_ev:
            nr_ee = agg_v["nr_ee"].replace(0, float("nan"))
            y_esgo = (agg_v["vol_e"] / nr_ee).round(1)
            fig4.add_trace(go.Scatter(
                x=meses_vf, y=y_esgo, name="Esgoto",
                mode="lines+markers+text",
                text=y_esgo.apply(lambda v: f"{v:.1f}" if v == v else ""),
                textposition="bottom center", textfont=dict(size=13),
                line=dict(color=COR["esgoto"], width=2), marker=dict(size=4),
            ))
        fig4.update_layout(
            title="Volume Faturado por Economia (m³/Economia)",
            margin=dict(t=70, b=10, l=0, r=30), height=400,
            xaxis=dict(title="", categoryorder="array", categoryarray=meses_vf),
            yaxis=dict(title=""),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode="x unified",
        )
        st.plotly_chart(fig4, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 5 — Inadimplência por Período de Medição
    # ══════════════════════════════════════════════════════════════════════════
    if not inad.empty and "dt_ref_documento" in inad.columns:
        ic = inad.copy()
        ic["dt_ref_documento"] = pd.to_datetime(ic["dt_ref_documento"], errors="coerce")
        ic["Mês"] = ic["dt_ref_documento"].dt.strftime("%m/%Y")
        inad_m = ic.groupby("Mês")["vl_divida"].sum().reset_index()
        inad_m.columns = ["Mês", "vl_divida"]

        fat_hist = D["fat"].copy()
        fat_hist["Mês"] = pd.to_datetime(fat_hist["dt_ref"]).dt.strftime("%m/%Y")
        fat_mh = fat_hist.groupby("Mês")["vl_total_faturado"].sum().reset_index()
        fat_mh.columns = ["Mês", "vl_faturado"]

        df_per = inad_m.merge(fat_mh, on="Mês", how="inner")
        df_per = df_per[df_per["vl_faturado"] > 0].copy()
        df_per["pct"] = df_per["vl_divida"] / df_per["vl_faturado"] * 100
        df_per = df_per.sort_values(
            "Mês", key=lambda s: pd.to_datetime(s, format="%m/%Y")
        )

        # Manter últimos 18 meses + agrupar anteriores
        if len(df_per) > 18:
            df_anteriores = df_per.iloc[:-18].copy()
            df_per = df_per.iloc[-18:].copy()

            # Criar linha de "anteriores" com soma das porcentagens
            pct_ant = df_anteriores["pct"].sum()

            df_ant_row = pd.DataFrame({
                "Mês": ["(anteriores)"],
                "vl_divida": [df_anteriores["vl_divida"].sum()],
                "vl_faturado": [df_anteriores["vl_faturado"].sum()],
                "pct": [pct_ant],
            })
            df_per = pd.concat([df_ant_row, df_per], ignore_index=True)

        df_per["Rótulo"] = df_per["pct"].apply(lambda v: f"{v:.2f}%")

        def _cb(v):
            return COR["vermelho"] if v > 10 else COR["amarelo"] if v > 3 else COR["azul_c"]

        # Mostrar rótulos para todos os valores
        texto_condicional = df_per["Rótulo"].tolist()

        # Garantir escala mínima de 80%
        max_pct = df_per["pct"].max()
        scale_max = max(80, max_pct * 1.15)

        fig5 = go.Figure(go.Bar(
            x=df_per["Mês"], y=df_per["pct"],
            text=texto_condicional, textposition="outside", textangle=90,
            textfont=dict(size=12, family="Arial Black", color="#0B3558"),
            marker_color=[_cb(v) for v in df_per["pct"]],
            marker=dict(line=dict(width=2, color="rgba(0,0,0,0.1)")),
        ))
        fig5.update_layout(
            title="Inadimplência por Período de Medição",
            margin=dict(t=50, b=40, l=50, r=50), height=350,
            xaxis=dict(title="", categoryorder="array",
                       categoryarray=df_per["Mês"].tolist(),
                       tickangle=-45, tickfont=dict(size=11)),
            yaxis=dict(title="", ticksuffix="%", tickformat=".1f", range=[0, scale_max],
                      tickfont=dict(size=11)),
            showlegend=False,
            plot_bgcolor="rgba(245,248,250,0.8)",
            uniformtext_minsize=4, uniformtext_mode="show",
        )
        st.plotly_chart(fig5, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 6 — Inadimplência Geral
    # ══════════════════════════════════════════════════════════════════════════
    if not inad.empty and vl_fat > 0:
        FAIXA_IN = {
            "01-Até 30 dias":    "IN30",
            "02-31 a 60 dias":   "IN60",
            "03-61 a 90 dias":   "IN90",
            "04-91 a 180 dias":  "IN180",
            "05-181 a 365 dias": "IN365",
        }
        fi_g = inad[inad["faixa_atraso"].isin(FAIXA_IN)].copy()
        fi_g = fi_g.groupby("faixa_atraso")["vl_divida"].sum().reset_index()
        fi_g["Label"] = fi_g["faixa_atraso"].map(FAIXA_IN)
        fi_g["Pct"]   = fi_g["vl_divida"] / vl_fat * 100
        fi_g["Txt"]   = fi_g["Pct"].apply(lambda v: f"{v:.2f}%")
        fi_g = fi_g.sort_values("faixa_atraso")
        fig6 = go.Figure(go.Bar(
            x=fi_g["Label"], y=fi_g["Pct"], orientation="v",
            text=fi_g["Txt"], textposition="outside",
            textfont=dict(color=COR["vermelho"], size=12, family="Arial Black"),
            marker_color=COR["vermelho"],
        ))
        fig6.update_layout(
            title="Inadimplência Geral",
            margin=dict(t=40, b=50, l=0, r=20), height=350,
            xaxis=dict(title="", tickangle=-45),
            yaxis=dict(title=""),
            showlegend=False,
        )
        st.plotly_chart(fig6, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════════════
    # 7 — Ligações por Situação
    # ══════════════════════════════════════════════════════════════════════════
    fat_all2 = D["fat"]
    d_sit    = D.get("d_sit_lig", pd.DataFrame())
    tem_sit  = (not fat_all2.empty
                and "id_situacao_ligacao" in fat_all2.columns
                and "nr_lig_agua" in fat_all2.columns)
    if tem_sit:
        fu = fat_all2.copy()
        fu["dt_ref"] = pd.to_datetime(fu["dt_ref"])
        fu = fu[fu["dt_ref"] == fu["dt_ref"].max()]
        lig = fu.groupby("id_situacao_ligacao")["nr_lig_agua"].sum().reset_index()
        lig.columns = ["id_situacao_ligacao", "Qtd"]
        if not d_sit.empty and "id_situacao_ligacao" in d_sit.columns:
            nm_c = next(
                (c for c in d_sit.columns if c.startswith("nm_") or c.startswith("ds_")), None
            )
            if nm_c:
                lig = lig.merge(d_sit[["id_situacao_ligacao", nm_c]],
                                on="id_situacao_ligacao", how="left")
                lig["Situação"] = lig[nm_c].fillna(lig["id_situacao_ligacao"].astype(str))
            else:
                lig["Situação"] = lig["id_situacao_ligacao"].astype(str)
        else:
            lig["Situação"] = lig["id_situacao_ligacao"].astype(str)
        lig = lig.sort_values("Qtd", ascending=False)
        total = int(lig["Qtd"].sum())
        CORES_S = [COR["azul"], COR["vermelho"], COR["amarelo"], COR["cinza"], COR["verde"]]
        fig7 = go.Figure()
        for i, row in enumerate(lig.itertuples()):
            fig7.add_trace(go.Bar(
                x=[row.Situação], y=[row.Qtd],
                name=row.Situação, showlegend=False,
                text=[f"{int(row.Qtd):,}".replace(",", ".")],
                textposition="outside",
                marker_color=CORES_S[i % len(CORES_S)],
            ))
        fig7.add_annotation(
            text=f"Total: {total:,}".replace(",", "."),
            xref="paper", yref="paper", x=1.0, y=1.10,
            showarrow=False, font=dict(size=11, color=COR["azul_esc"]), xanchor="right",
        )
        fig7.update_layout(
            title="Ligações por Situação",
            margin=dict(t=50, b=10, l=0, r=20), height=400,
            xaxis=dict(title=""), yaxis=dict(title="", tickformat=",.0f"),
            barmode="group",
        )
        st.plotly_chart(fig7, use_container_width=True)
    else:
        st.info("Execute o ETL para ver o detalhamento por situação de ligação.")

    # ── Rodapé ────────────────────────────────────────────────────────────────
    fat_max_dt = pd.to_datetime(D["fat"]["dt_ref"]).max() if not D["fat"].empty else None
    if fat_max_dt is not None:
        st.caption(
            f"ℹ️ Faturamento disponível até **{fat_max_dt.strftime('%B/%Y').capitalize()}** · "
            f"Inadimplência: snapshot da data de atualização"
        )


def pg_faturamento(D, d0, d1):
    page_header("Faturamento e Medição",
                f"{d0.strftime('%d/%m/%Y')} a {d1.strftime('%d/%m/%Y')}")

    tab_fat, tab_lei = st.tabs(["📊 Faturamento", "📏 Leituras e Medição"])

    with tab_fat:
        _faturamento_body(D, d0, d1)

    with tab_lei:
        pg_leituras(D, d0, d1, _sub=True)


def _faturamento_body(D, d0, d1):

    fat_max = pd.to_datetime(D["fat"]["dt_ref"]).max() if not D["fat"].empty else None
    fat = filtrar(D["fat"], "dt_ref", d0, d1)

    if fat.empty:
        if fat_max is not None:
            st.error(
                f"⚠️ **Sem dados de faturamento no período selecionado.**\n\n"
                f"Os dados disponíveis vão até **{fat_max.strftime('%B/%Y').capitalize()}**. "
                f"Selecione um período até essa data para visualizar o faturamento."
            )
        else:
            st.warning("Sem dados de faturamento.")
        return

    fat = merge_bairro(fat, D)

    # ── Componentes ────────────────────────────────────────────────────────────
    # vl_total_faturado = Água+Tar.Básica+Esgoto+Lixo+Serviços+Abatimento-Cancelamento
    # Multas/Juros NÃO entram no líquido (conforme FAT0015)
    vl_liquido     = fat["vl_total_faturado"].sum()
    vl_agua        = fat["vl_agua"].sum()
    vl_tar_bas     = fat["vl_servico_basico_agua"].sum() if "vl_servico_basico_agua" in fat.columns else 0
    vl_servico     = fat["vl_servico"].sum()
    vl_lixo        = fat["vl_lixo"].sum()
    vl_multas      = fat["vl_multas_juros"].sum()   if "vl_multas_juros"  in fat.columns else 0
    vl_abat        = fat["vl_abatimento"].sum()     if "vl_abatimento"    in fat.columns else 0
    vl_cancel      = fat["vl_cancelamento"].sum()   if "vl_cancelamento"  in fat.columns else 0
    vol_m3         = fat["volume_m3"].sum()          if "volume_m3"        in fat.columns else 0
    qt_faturas     = fat["qt_fatura"].sum()          if "qt_fatura"        in fat.columns else len(fat)

    # ── KPIs linha 1 — totais ─────────────────────────────────────────────────
    c1, c2 = st.columns(2)
    kpi(c1, "💰 Total Líquido Faturado", vl_liquido)
    kpi(c2, "🔻 Abatimentos / Descontos", vl_abat)

    c3, c4 = st.columns(2)
    kpi(c3, "Qtd Faturas", int(qt_faturas), prefixo="")
    kpi(c4, "Volume (m³)", vol_m3, prefixo="")

    st.markdown("---")

    # ── KPIs linha 2 — componentes (incluso no líquido) ──────────────────────
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Água",          vl_agua)
    kpi(c2, "Tarifa Básica", vl_tar_bas)
    kpi(c3, "Serviços",      vl_servico)
    kpi(c4, "Lixo",          vl_lixo)

    # ── KPIs linha 3 — exclusões do faturamento líquido ──────────────────────
    st.caption("ℹ️ Os valores abaixo não compõem o Faturamento Líquido (conforme relatório FAT0015):")
    c1, c2, c3 = st.columns(3)
    kpi(c1, "⚠️ Multas / Juros / Cor.", vl_multas)
    kpi(c2, "🚫 Cancelamentos",         vl_cancel)
    c3.empty()

    # Nota sobre divergência residual de leituras críticas
    qt_critica = fat["fl_critica"].sum() if "fl_critica" in fat.columns else 0
    if qt_critica > 0:
        st.info(
            f"**Nota sobre divergência com o SANSYS:** {int(qt_critica)} fatura(s) com leitura crítica "
            f"(hidrômetro anômalo) estão neste período. O SANSYS substitui o consumo por uma estimativa "
            f"histórica, mas o BigQuery armazena o valor bruto pré-correção. A diferença residual entre "
            f"este painel e o FAT0015 é estrutural nessa fonte de dados — não é erro de fórmula."
        )

    # ── Bloco comparativo ─────────────────────────────────────────────────────
    _comp = _comp_periodo()
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _fat_c   = filtrar(D["fat"], "dt_ref", _cd0, _cd1)
        _vl_liq_c = _fat_c["vl_total_faturado"].sum() if not _fat_c.empty else 0
        _vl_ag_c  = _fat_c["vl_agua"].sum()           if not _fat_c.empty else 0
        _vol_c    = _fat_c["volume_m3"].sum()          if not _fat_c.empty and "volume_m3" in _fat_c.columns else 0
        _qt_c     = _fat_c["qt_fatura"].sum()          if not _fat_c.empty and "qt_fatura" in _fat_c.columns else 0
        _brl = lambda v: f"R$ {v:,.0f}".replace(",","X").replace(".",",").replace("X",".")
        render_comp_bloco(_comp["label_atual"], _comp["label_comp"], [
            ("Total Líquido Faturado", vl_liquido, _vl_liq_c, _brl,                       True),
            ("Água",                  vl_agua,    _vl_ag_c,  _brl,                       True),
            ("Volume (m³)",           vol_m3,     _vol_c,    lambda v: f"{v:,.0f} m³",   True),
            ("Qtd Faturas",           qt_faturas, _qt_c,     lambda v: f"{int(v):,}",    True),
        ])

    st.markdown("---")

    # ── Gráficos ──────────────────────────────────────────────────────────────
    _comp = _comp_periodo()
    fat_m = fat.copy()
    fat_m["_mes"] = pd.to_datetime(fat_m["dt_ref"]).dt.to_period("M").dt.to_timestamp()
    # Componentes do Faturamento Líquido (excluindo Multas/Juros)
    agg_cols = {"Água": "vl_agua", "Tarifa Básica": "vl_servico_basico_agua",
                "Serviços": "vl_servico", "Lixo": "vl_lixo"}
    agg_dict = {k: (v, "sum") for k, v in agg_cols.items() if v in fat_m.columns}
    ag = fat_m.groupby("_mes").agg(**agg_dict).reset_index().rename(columns={"_mes": "Mês"})
    ag_melt = ag.melt(id_vars="Mês", var_name="Componente", value_name="Valor")
    ag_melt = ag_melt[ag_melt["Valor"] > 0]
    # Adiciona série comparativa ao gráfico de componentes
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _fat_cg = filtrar(D["fat"], "dt_ref", _cd0, _cd1)
        if not _fat_cg.empty:
            _fm_c = _fat_cg.copy()
            _fm_c["_mes"] = pd.to_datetime(_fm_c["dt_ref"]).dt.to_period("M").dt.to_timestamp()
            _agg_c = {k: (v, "sum") for k, v in agg_cols.items() if v in _fm_c.columns}
            _ag_c  = _fm_c.groupby("_mes").agg(**_agg_c).reset_index().rename(columns={"_mes": "Mês"})
            _ag_c_melt = _ag_c.melt(id_vars="Mês", var_name="Componente", value_name="Valor")
            _ag_c_melt = _ag_c_melt[_ag_c_melt["Valor"] > 0]
            _ag_c_melt["Componente"] = _ag_c_melt["Componente"] + f" ({_comp['label_comp']})"
            ag_melt = pd.concat([ag_melt, _ag_c_melt], ignore_index=True)
    _label_comp_fat = _comp["label_comp"] if _comp else ""
    ag_melt["_texto"] = ag_melt["Valor"].apply(lambda v: f"{v/1000:.0f}k" if v >= 1000 else f"{v:.0f}")
    fig = px.bar(ag_melt, x="Mês", y="Valor", color="Componente",
                 title="Faturamento Líquido por Componente (mensal)" + (f" — {_comp['label_atual']} vs {_comp['label_comp']}" if _comp else ""),
                 color_discrete_map={
                     "Água": COR["agua"], "Tarifa Básica": "#8B5CF6",
                     "Serviços": COR["servico"], "Lixo": COR["lixo"],
                 }, barmode="group" if _comp else "stack",
                 text="_texto")
    # Estilo padrão para barras do período atual
    fig.update_traces(textposition="inside", textangle=-90,
                      textfont=dict(size=13, color="white", family="Arial"),
                      insidetextanchor="middle")
    # Destaque extra para barras do período comparativo
    if _comp:
        for trace in fig.data:
            if _label_comp_fat in trace.name:
                trace.textfont = dict(size=15, color="#1a1a1a", family="Arial Black")
    fig.update_layout(margin=dict(t=35, b=0, l=0, r=20), xaxis_title="", yaxis_title="",
                      uniformtext_minsize=8, uniformtext_mode="hide")
    fig.update_yaxes(tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True)

    # Pizza composição — somente componentes do líquido
    comp_data = {"Água": vl_agua, "Tarifa Básica": vl_tar_bas,
                 "Serviços": vl_servico, "Lixo": vl_lixo}
    comp_data = {k: v for k, v in comp_data.items() if v > 0}
    if comp_data:
        df_comp = pd.DataFrame(list(comp_data.items()), columns=["Componente", "Valor"])
        _cores_pie = {
            "Água": COR["agua"], "Tarifa Básica": "#8B5CF6",
            "Serviços": COR["servico"], "Lixo": COR["lixo"],
        }
        fig2 = go.Figure(data=[go.Pie(
            labels=df_comp["Componente"],
            values=df_comp["Valor"],
            pull=[0.04] * len(df_comp),           # leve separação suave
            marker=dict(
                colors=[_cores_pie.get(c, COR["azul"]) for c in df_comp["Componente"]],
                line=dict(color="white", width=2.5),  # borda branca suave
            ),
            textposition="auto",
            texttemplate="<b>%{label}</b><br>%{percent:.1%}",
            textfont=dict(size=13, color="white", family="Arial Black"),
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<br>%{percent:.2%}<extra></extra>",
            insidetextorientation="radial",
            outsidetextfont=dict(size=13, color="#1a1a1a", family="Arial Black"),
            hole=0.08,
        )])
        fig2.update_layout(
            title=dict(text="Composição do Faturamento Líquido", font=dict(size=15)),
            margin=dict(t=50, b=20, l=20, r=20), height=420,
            legend=dict(
                orientation="v", xanchor="left", x=1.02,
                yanchor="middle", y=0.5,
                font=dict(size=13, family="Arial"),
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="rgba(180,180,180,0.4)", borderwidth=1,
            ),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig2, use_container_width=True)
    # Volume m³ mensal
    fig3 = bar_mensal(fat, "dt_ref", "volume_m3",
                      "Volume Faturado m³ (mensal)", COR["azul_c"])
    fig3.update_yaxes(tickformat=",.0f")
    st.plotly_chart(fig3, use_container_width=True)

    # Por categoria
    if "id_categoria" in fat.columns and not D["d_cat"].empty:
        f_cat = fat.merge(D["d_cat"][["id_categoria","nm_rsf_categoria_dim"]],
                          on="id_categoria", how="left")
        ag_cat = f_cat.groupby("nm_rsf_categoria_dim")["vl_total_faturado"].sum().reset_index()
        ag_cat.columns = ["Categoria", "Valor"]
        _cores_cat = ["#AED6F1","#5DADE2","#2E86C1","#1A5276","#85C1E9","#21618C","#7FB3D3","#154360"][:len(ag_cat)]
        fig4 = go.Figure(data=[go.Pie(
            labels=ag_cat["Categoria"],
            values=ag_cat["Valor"],
            pull=[0.04] * len(ag_cat),
            marker=dict(colors=_cores_cat, line=dict(color="white", width=2.5)),
            textposition="auto",
            texttemplate="<b>%{label}</b><br>%{percent:.1%}",
            textfont=dict(size=13, color="white", family="Arial Black"),
            outsidetextfont=dict(size=13, color="#1a1a1a", family="Arial Black"),
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<br>%{percent:.2%}<extra></extra>",
            insidetextorientation="radial",
            hole=0.08,
        )])
        fig4.update_layout(
            title=dict(text="Faturamento por Categoria", font=dict(size=15)),
            margin=dict(t=50, b=20, l=20, r=20), height=420,
            legend=dict(
                orientation="v", xanchor="left", x=1.02,
                yanchor="middle", y=0.5,
                font=dict(size=13, family="Arial"),
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="rgba(180,180,180,0.4)", borderwidth=1,
            ),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Por bairro (top 15)
    if "nm_bairro_dim" in fat.columns:
        ag_b = fat.groupby("nm_bairro_dim")["vl_total_faturado"].sum()\
                  .sort_values(ascending=True).tail(15).reset_index()
        ag_b.columns = ["Bairro", "Valor"]
        # Degradê: bairro com menor valor → azul claro; maior → azul escuro
        n = len(ag_b)
        import colorsys
        def _grad_azul(i, total):
            # interpola de #AED6F1 (claro) a #1A5276 (escuro) conforme posição
            t = i / max(total - 1, 1)
            r = int(174 + t * (26  - 174))
            g = int(214 + t * (82  - 214))
            b = int(241 + t * (118 - 241))
            return f"rgb({r},{g},{b})"
        cores_grad = [_grad_azul(i, n) for i in range(n)]
        fig5 = go.Figure(go.Bar(
            x=ag_b["Valor"], y=ag_b["Bairro"], orientation="h",
            marker_color=cores_grad,
            marker=dict(line=dict(width=0)),
            text=ag_b["Valor"].apply(lambda v: f"<b>R$ {v:,.0f}</b>".replace(",", ".")),
            textposition="inside",
            textfont=dict(size=13, color="white", family="Arial Black"),
            insidetextanchor="end",
        ))
        fig5.update_layout(
            title="Top 15 Bairros — Faturamento",
            margin=dict(t=40, b=0, l=0, r=20), height=480,
            xaxis=dict(title="", tickformat=",.0f"),
            yaxis=dict(title=""),
            uniformtext_minsize=9, uniformtext_mode="hide",
        )
        st.plotly_chart(fig5, use_container_width=True)

    # Aviso de cobertura
    if fat_max is not None:
        st.info(f"Dados de faturamento disponíveis até **{fat_max.strftime('%B/%Y').capitalize()}**.")


def pg_arrecadacao(D, d0, d1):
    page_header("Arrecadação (Série Histórica)",
                f"{d0.strftime('%d/%m/%Y')} a {d1.strftime('%d/%m/%Y')}")

    # arr = arrecadacao_comercial (mensal) — rubrica breakdown e gráfico histórico
    arr      = filtrar(D["arr"],  "dt_ref",       d0, d1)
    fat      = filtrar(D["fat"],  "dt_ref",       d0, d1)
    arr_d_f  = arr_d_por_credito(D, d0, d1)   # diária D+ — KPI total arrecadado
    # parr = painel transacional (até Jun/2024) — usado só para detalhes de canal
    parr     = filtrar(D["parr"], "dt_pagamento", d0, d1)

    if arr_d_f.empty and arr.empty:
        st.warning("Sem dados de arrecadação no período selecionado.")
        return

    # KPI total: usa arr_d com D+ (mais preciso); fallback para arr se arr_d vazio
    vl_arr = (arr_d_f["vl_arrecadado"].sum() if not arr_d_f.empty
              else arr["vl_total_arrecadado"].sum() if not arr.empty else 0)
    vl_fat = fat["vl_total_faturado"].sum() if not fat.empty else 0
    efic   = vl_arr / vl_fat if vl_fat else None
    # Rubricas (água/esgoto) vêm de arr — arr_d não tem breakdown por rubrica
    vl_agua_arr = arr["vl_agua"].sum() if not arr.empty and "vl_agua" in arr.columns else 0
    vl_esg_arr  = arr["vl_esgoto"].sum() if not arr.empty and "vl_esgoto" in arr.columns else 0
    c1, c2 = st.columns(2)
    kpi(c1, "Total Arrecadado", vl_arr)
    kpi(c2, "Faturado no Período", vl_fat)

    c3, c4 = st.columns(2)
    kpi(c3, "Água Arrecadada", vl_agua_arr)
    kpi(c4, "Esgoto Arrecadado", vl_esg_arr)

    if efic is not None:
        c5, c6 = st.columns(2)
        kpi(c5, "Eficiência Arrecadação", efic, prefixo="%")
        c6.empty()
    else:
        c5, c6 = st.columns(2)
        c5.metric("Eficiência Arrecadação", "—",
                  help="Faturamento não disponível neste período para calcular eficiência")
        c6.empty()

    # ── Bloco comparativo ─────────────────────────────────────────────────────
    _comp = _comp_periodo()
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _fat_c  = filtrar(D["fat"],   "dt_ref",        _cd0, _cd1)
        _arrd_c = filtrar(D["arr_d"], "data_pagamento", _cd0, _cd1)
        _arr_c  = filtrar(D["arr"],   "dt_ref",        _cd0, _cd1)
        _va_c   = (_arrd_c["vl_arrecadado"].sum() if not _arrd_c.empty
                   else _arr_c["vl_total_arrecadado"].sum() if not _arr_c.empty else 0)
        _vf_c   = _fat_c["vl_total_faturado"].sum() if not _fat_c.empty else 0
        _ei_c   = _va_c / _vf_c if _vf_c else None
        _ag_c   = _arr_c["vl_agua"].sum()   if not _arr_c.empty and "vl_agua"   in _arr_c.columns else 0
        _eg_c   = _arr_c["vl_esgoto"].sum() if not _arr_c.empty and "vl_esgoto" in _arr_c.columns else 0
        _brl    = lambda v: f"R$ {v:,.0f}".replace(",","X").replace(".",",").replace("X",".")
        render_comp_bloco(_comp["label_atual"], _comp["label_comp"], [
            ("Total Arrecadado",       vl_arr,      _va_c, _brl,                              True),
            ("Faturado no Período",    vl_fat,      _vf_c, _brl,                              True),
            ("Eficiência Arrecadação", efic,        _ei_c, lambda v: f"{v:.1%}" if v else "—", True),
            ("Água Arrecadada",        vl_agua_arr, _ag_c, _brl,                              True),
            ("Esgoto Arrecadado",      vl_esg_arr,  _eg_c, _brl,                              True),
        ])

    st.markdown("---")
    # Arrecadação mensal (usa arr — tabela mensal, cobertura completa)
    arr_hist = D["arr"].copy()
    arr_hist["_mes"] = pd.to_datetime(arr_hist["dt_ref"]).dt.to_period("M").dt.to_timestamp()
    ag_arr = arr_hist.groupby("_mes")["vl_total_arrecadado"].sum().reset_index()
    ag_arr.columns = ["Mês", "Arrecadado"]

    fat_hist = D["fat"].copy()
    if not fat_hist.empty:
        fat_hist["_mes"] = pd.to_datetime(fat_hist["dt_ref"]).dt.to_period("M").dt.to_timestamp()
        fat_ag = fat_hist.groupby("_mes")["vl_total_faturado"].sum().reset_index()
        fat_ag.columns = ["Mês", "Faturado"]
        ag_both = ag_arr.merge(fat_ag, on="Mês", how="outer").sort_values("Mês")
    else:
        ag_both = ag_arr.rename(columns={"Arrecadado": "Arrecadado"})

    ag_m = ag_both.melt(id_vars="Mês", var_name="Tipo", value_name="Valor").dropna()
    fig = px.line(ag_m, x="Mês", y="Valor", color="Tipo", markers=True,
                  title="Faturado vs Arrecadado — Histórico completo",
                  color_discrete_map={"Faturado": COR["azul"], "Arrecadado": COR["verde"]})
    fig.add_vrect(x0=d0, x1=d1, fillcolor="rgba(26,111,173,0.08)",
                  line_width=0, annotation_text="Período atual", annotation_position="top left")
    _comp = _comp_periodo()
    if _comp:
        fig.add_vrect(x0=_comp["comp_d0"], x1=_comp["comp_d1"],
                      fillcolor="rgba(220,38,38,0.06)", line_width=0,
                      annotation_text=f"Comp. {_comp['label_comp']}", annotation_position="top right")
    fig.update_layout(margin=dict(t=35, b=0, l=0, r=20), xaxis_title="", yaxis_title="")
    fig.update_yaxes(tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True)

    # Componentes da arrecadação no período
    comp_cols = {
        "vl_agua": "Água", "vl_esgoto": "Esgoto",
        "vl_lixo": "Lixo", "vl_servico": "Serviços",
        "vl_demais_valores_arrecadados": "Demais",
    }
    comp_data = {
        nome: arr[col].sum()
        for col, nome in comp_cols.items()
        if col in arr.columns and arr[col].sum() > 0
    }
    if comp_data:
        df_comp = pd.DataFrame(list(comp_data.items()), columns=["Componente", "Valor"])
        fig2 = px.pie(df_comp, names="Componente", values="Valor",
                      title="Composição da Arrecadação",
                      color_discrete_map={
                          "Água": COR["agua"], "Esgoto": COR["esgoto"],
                          "Lixo": COR["lixo"], "Serviços": COR["servico"]
                      })
        fig2.update_layout(margin=dict(t=35, b=0, l=0, r=20))
        st.plotly_chart(fig2, use_container_width=True)
    # Índice de eficiência mensal (onde fat disponível)
    fat_hist2 = D["fat"].copy()
    if not fat_hist2.empty:
        fat_hist2["_mes"] = pd.to_datetime(fat_hist2["dt_ref"]).dt.to_period("M").dt.to_timestamp()
        f_ag = fat_hist2.groupby("_mes")["vl_total_faturado"].sum().reset_index()
        f_ag.columns = ["Mês", "Faturado"]

        a_ag2 = arr_hist.groupby("_mes")["vl_total_arrecadado"].sum().reset_index()
        a_ag2.columns = ["Mês", "Arrecadado"]

        idx_m = a_ag2.merge(f_ag, on="Mês", how="inner")
        idx_m["Eficiência"] = idx_m["Arrecadado"] / idx_m["Faturado"]

        fig3 = px.line(idx_m, x="Mês", y="Eficiência", markers=True,
                       title="Índice de Eficiência de Arrecadação",
                       color_discrete_sequence=[COR["verde"]])
        fig3.add_hline(y=0.95, line_dash="dash", line_color=COR["vermelho"],
                       annotation_text="Meta 95%")
        fig3.update_layout(margin=dict(t=35, b=0, l=0, r=20), xaxis_title="", yaxis_title="")
        fig3.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Índice de eficiência requer dados de faturamento (disponível até Abr/2024).")

    # Canal de arrecadação (painel transacional — dados até Jun/2024)
    if not parr.empty and "id_forma_arrecadacao" in parr.columns and not D["d_frm"].empty:
        pf = parr.merge(D["d_frm"][["id_forma_arrecadacao","nm_tipo_forma_arrecadacao"]],
                        on="id_forma_arrecadacao", how="left")
        ag_f = pf.groupby("nm_tipo_forma_arrecadacao")["vl_pagamento"].sum()\
                 .sort_values(ascending=False).reset_index()
        ag_f.columns = ["Forma", "Valor"]
        ag_f["Forma"] = ag_f["Forma"].str[:40]
        fig4 = px.pie(ag_f.head(8), names="Forma", values="Valor",
                      title="Canal de Pagamento (dados disponíveis)",
                      color_discrete_sequence=px.colors.qualitative.Set3)
        fig4.update_layout(margin=dict(t=35, b=0, l=0, r=20))
        st.plotly_chart(fig4, use_container_width=True)
    else:
        # usa tipo_documento da arr quando parr está vazio no período
        if "tipo_documento" in arr.columns:
            ag_td = arr.groupby("tipo_documento")["vl_total_arrecadado"].sum()\
                       .sort_values(ascending=True).tail(10).reset_index()
            ag_td.columns = ["Tipo", "Valor"]
            fig4b = px.bar(ag_td, x="Valor", y="Tipo", orientation="h",
                           title="Arrecadação por Tipo de Documento",
                           color_discrete_sequence=[COR["azul_c"]])
            fig4b.update_layout(margin=dict(t=35, b=0, l=0, r=20), xaxis_title="", yaxis_title="")
            fig4b.update_xaxes(tickformat=",.0f")
            st.plotly_chart(fig4b, use_container_width=True)


def pg_arrecadacao_diaria(D, d0, d1):
    page_header("Boletim de Arrecadação Diária",
                f"{d0.strftime('%d/%m/%Y')} a {d1.strftime('%d/%m/%Y')}")

    ad = D["arr_d"].copy()
    if ad.empty:
        st.warning("Sem dados diários de arrecadação.")
        return

    ad["data_pagamento"] = pd.to_datetime(ad["data_pagamento"])

    # Aplica lógica D+: fds/feriado → próximo dia útil; se cruzar mês, mantém no mês do pagamento
    ad["data_credito"] = ad["data_pagamento"].apply(calc_data_credito)

    # Filtra pelo data_PAGAMENTO (não data_credito) para que pagamentos de
    # sábado/domingo em fim de mês fiquem no mês correto de pagamento, evitando
    # capturar pagamentos cross-month (ex: sáb 28/fev creditando em 02/mar).
    ad_f = ad[(ad["data_pagamento"] >= d0) & (ad["data_pagamento"] < d1 + pd.Timedelta(days=1))]

    if ad_f.empty:
        st.warning("Sem dados no período selecionado.")
        return

    # Agrega por data_credito
    diario = (
        ad_f.groupby("data_credito")
        .agg(qt_docs=("qt_documentos","sum"), vl=("vl_arrecadado","sum"))
        .reset_index()
        .rename(columns={"data_credito":"Data","qt_docs":"Qtd Docs","vl":"Valor"})
        .sort_values("Data")
    )
    diario["Dia Semana"] = diario["Data"].dt.strftime("%A").map({
        "Monday":"Segunda-feira","Tuesday":"Terça-feira","Wednesday":"Quarta-feira",
        "Thursday":"Quinta-feira","Friday":"Sexta-feira","Saturday":"Sábado","Sunday":"Domingo"
    })
    diario["Acumulado"] = diario["Valor"].cumsum()
    diario["Útil"] = range(1, len(diario)+1)

    vl_total = diario["Valor"].sum()
    qtd_dias  = len(diario)
    media_dia = vl_total / qtd_dias if qtd_dias else 0
    c1, c2, c3 = st.columns(3)
    kpi(c1, "Total Arrecadado (D+)", vl_total)
    kpi(c2, "Dias Úteis", qtd_dias, prefixo="")
    kpi(c3, "Média por Dia Útil", media_dia)

    # ── Bloco comparativo ─────────────────────────────────────────────────────
    _comp = _comp_periodo()
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _ad_c  = ad[(ad["data_pagamento"] >= _cd0) & (ad["data_pagamento"] < _cd1 + pd.Timedelta(days=1))].copy()
        _vt_c  = _ad_c["vl_arrecadado"].sum() if not _ad_c.empty else 0
        # Aplica mesma lógica D+ do período atual: agrupa por data_credito
        if not _ad_c.empty:
            _ad_c["data_credito"] = _ad_c["data_pagamento"].apply(calc_data_credito)
            _qd_c = _ad_c.groupby("data_credito")["vl_arrecadado"].sum().shape[0]
            _md_c = _vt_c / _qd_c if _qd_c else 0
        else:
            _qd_c, _md_c = 0, 0
        _brl   = lambda v: f"R$ {v:,.0f}".replace(",","X").replace(".",",").replace("X",".")
        render_comp_bloco(_comp["label_atual"], _comp["label_comp"], [
            ("Total Arrecadado (D+)",  vl_total,  _vt_c, _brl,                    True),
            ("Dias Úteis",             qtd_dias,  _qd_c, lambda v: f"{int(v)}",   None),
            ("Média por Dia Útil",     media_dia, _md_c, _brl,                    True),
        ])

    st.info(
        "ℹ️ **Lógica D+**: pagamentos em finais de semana ou feriados nacionais → crédito no próximo dia útil. "
        "Se o próximo dia útil cair no mês seguinte, o crédito permanece no mês do pagamento. "
        "⚠️ Diferença residual de ~R$ 23.675 em mar/2026 (dias 20, 23, 24 e 25): "
        "registros ausentes na fonte BigQuery (`painel_arrecadacao_contabil`)."
    )

    st.markdown("---")

    _comp = _comp_periodo()
    fig = go.Figure()
    _lbl_a = _comp["label_atual"] if _comp else "Atual"
    fig.add_bar(x=diario["Data"], y=diario["Valor"],
                name=f"Arrecadação {_lbl_a}",
                marker_color=COR["azul"],
                text=diario["Valor"].apply(lambda v: f"R$ {v:,.0f}"),
                textposition="outside")
    fig.add_scatter(x=diario["Data"], y=diario["Acumulado"],
                    name=f"Acumulado {_lbl_a}", mode="lines+markers",
                    line=dict(color=COR["verde"], width=2),
                    yaxis="y2")
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _ad_c = ad[(ad["data_pagamento"] >= _cd0) & (ad["data_pagamento"] < _cd1 + pd.Timedelta(days=1))].copy()
        if not _ad_c.empty:
            # Aplica mesma lógica D+ do período atual
            _ad_c["data_credito"] = _ad_c["data_pagamento"].apply(calc_data_credito)
            _diario_c = (_ad_c.groupby("data_credito")
                         .agg(Valor=("vl_arrecadado","sum")).reset_index()
                         .rename(columns={"data_credito":"Data"}).sort_values("Data"))
            _diario_c["Acumulado"] = _diario_c["Valor"].cumsum()
            fig.add_bar(x=_diario_c["Data"], y=_diario_c["Valor"],
                        name=f"Arrecadação {_comp['label_comp']}",
                        marker_color="rgba(220,38,38,0.45)", opacity=0.7)
            fig.add_scatter(x=_diario_c["Data"], y=_diario_c["Acumulado"],
                            name=f"Acumulado {_comp['label_comp']}", mode="lines",
                            line=dict(color=COR["vermelho"], width=2, dash="dot"),
                            yaxis="y2")
    fig.update_layout(
        title="Arrecadação Diária e Acumulada (D+)" + (f" — {_comp['label_atual']} vs {_comp['label_comp']}" if _comp else ""),
        xaxis_title="", yaxis_title="Valor Diário (R$)",
        yaxis2=dict(title="Acumulado (R$)", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=1.1),
        margin=dict(t=70, b=0, l=0, r=30), height=400,
        hovermode="x unified", barmode="overlay",
    )
    fig.update_yaxes(tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True)

    # Por forma de arrecadação (agente)
    if not D["d_frm"].empty and "id_forma_arrecadacao" in ad_f.columns:
        af_frm = ad_f.merge(D["d_frm"][["id_forma_arrecadacao","nm_tipo_forma_arrecadacao"]],
                            on="id_forma_arrecadacao", how="left")
        ag_frm = (af_frm.groupby("nm_tipo_forma_arrecadacao")["vl_arrecadado"]
                  .sum().sort_values(ascending=False).reset_index())
        ag_frm.columns = ["Canal","Valor"]
        ag_frm["Canal"] = ag_frm["Canal"].str.strip()
        cores_pie = px.colors.qualitative.Pastel
        fig2 = go.Figure(data=[go.Pie(
            labels=ag_frm.head(7)["Canal"],
            values=ag_frm.head(7)["Valor"],
            textposition="auto",
            textfont=dict(size=15, color="black", family="Arial Black"),
            hovertemplate="<b>%{label}</b><br>Valor: R$ %{value:,.0f}<br>Percentual: %{percent}<extra></extra>",
            marker=dict(colors=cores_pie, line=dict(color="white", width=3)),
            domain=dict(x=[0, 0.48]),
        )])
        fig2.update_layout(
            margin=dict(t=50, b=20, l=0, r=0),
            height=420,
            font=dict(size=12, family="Arial"),
            title=dict(text="Canal de Pagamento", font=dict(size=16, color="#0B3558")),
            legend=dict(
                font=dict(size=12, family="Arial"),
                orientation="v",
                xanchor="left",
                yanchor="middle",
                x=0.51,
                y=0.5,
                bgcolor="rgba(255,255,255,0.93)",
                bordercolor="rgba(59,95,127,0.5)",
                borderwidth=2,
                title=dict(text="<b>Canais</b>", font=dict(size=13)),
                tracegroupgap=10,
            )
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Tabela detalhada — igual ao relatório do sistema
    st.markdown("#### Tabela Diária de Arrecadação")
    tbl_view = diario[["Útil","Data","Dia Semana","Qtd Docs","Valor","Acumulado"]].copy()
    tbl_view["Data"] = tbl_view["Data"].dt.strftime("%d/%m/%Y")

    # Linha de total
    total_row = pd.DataFrame([{
        "Útil": "", "Data": "TOTAL", "Dia Semana": "",
        "Qtd Docs": int(tbl_view["Qtd Docs"].sum()),
        "Valor": tbl_view["Valor"].sum(),
        "Acumulado": tbl_view["Valor"].sum(),
    }])
    tbl_view = pd.concat([tbl_view, total_row], ignore_index=True)

    st.dataframe(
        tbl_view.style
        .format({
            "Valor":     lambda v: f"R$ {v:>12,.2f}" if isinstance(v, float) else v,
            "Acumulado": lambda v: f"R$ {v:>12,.2f}" if isinstance(v, float) else v,
            "Qtd Docs":  lambda v: f"{int(v):,}"    if isinstance(v, (int,float)) and v==v else v,
        })
        .apply(lambda row: ["font-weight:bold; background:#E8F4FD"]*len(row)
               if row["Data"]=="TOTAL" else [""]*len(row), axis=1),
        use_container_width=True,
        height=600,
    )

    # Detalhamento por agente
    with st.expander("📋 Detalhamento por Agente Arrecadador"):
        if "id_agente" in ad_f.columns:
            dim_ag = (D["d_agente"][["id_agente","nm_agente_arrecadador"]]
                      if not D["d_agente"].empty
                      else pd.DataFrame(columns=["id_agente","nm_agente_arrecadador"]))
            merged = ad_f.merge(dim_ag, on="id_agente", how="left")
            merged["nm_agente_arrecadador"] = merged["nm_agente_arrecadador"].fillna(
                merged["id_agente"].astype(str)
            )
            ag_ag = (merged.groupby("nm_agente_arrecadador")["vl_arrecadado"]
                     .sum().sort_values(ascending=False).reset_index())
            ag_ag.columns = ["Agente","Valor"]
            ag_tot = pd.DataFrame([{"Agente":"TOTAL","Valor":ag_ag["Valor"].sum()}])
            ag_ag = pd.concat([ag_ag, ag_tot])
            st.dataframe(
                ag_ag.style.format({"Valor": "R$ {:,.2f}"}),
                use_container_width=True,
            )


def pg_inadimplencia(D, d0, d1):
    page_header("Inadimplência",
                f"{d0.strftime('%d/%m/%Y')} a {d1.strftime('%d/%m/%Y')}")

    inad = D["inad"]  # snapshot atual, sem filtro de data
    fat  = filtrar(D["fat"], "dt_ref", d0, d1)
    inad = merge_bairro(inad, D)

    if inad.empty:
        st.warning("Sem dados de inadimplência.")
        return

    vl_inad = inad["vl_divida"].sum()
    vl_fat  = fat["vl_total_faturado"].sum() if not fat.empty else 0
    idx_inad = vl_inad / vl_fat if vl_fat else 0
    qtd_fat  = len(inad)
    tkt_med  = vl_inad / qtd_fat if qtd_fat else 0
    qtd_corte = int(inad["fl_corte_pendente"].sum()) if "fl_corte_pendente" in inad.columns else 0
    c1, c2 = st.columns(2)
    kpi(c1, "Total Inadimplência", vl_inad)
    kpi(c2, "Índice Inadimplência", idx_inad, prefixo="%")

    c3, c4 = st.columns(2)
    kpi(c3, "Qtd Faturas Vencidas", qtd_fat, prefixo="")
    kpi(c4, "Ticket Médio", tkt_med)

    c5, c6 = st.columns(2)
    c5.metric("Com Corte Pendente", f"{qtd_corte:,}".replace(",", "."),
              delta="aguardando corte", delta_color="off")
    c6.empty()

    # ── Bloco comparativo — usa faturamento como proxy (inad é snapshot) ──────
    _comp = _comp_periodo()
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _fat_c  = filtrar(D["fat"], "dt_ref", _cd0, _cd1)
        _vf_c   = _fat_c["vl_total_faturado"].sum() if not _fat_c.empty else 0
        _ii_c   = vl_inad / _vf_c if _vf_c else None
        _brl    = lambda v: f"R$ {v:,.0f}".replace(",","X").replace(".",",").replace("X",".")
        render_comp_bloco(_comp["label_atual"], _comp["label_comp"], [
            ("Total Inadimplência (atual)", vl_inad,   None,  _brl,                              False),
            ("Faturado (referência)",       vl_fat,    _vf_c, _brl,                              True),
            ("Índice Inadimplência",        idx_inad,  _ii_c, lambda v: f"{v:.1%}" if v else "—", False),
            ("Qtd Faturas Vencidas",        qtd_fat,   None,  lambda v: f"{int(v):,}",            False),
            ("Ticket Médio",                tkt_med,   None,  _brl,                              None),
        ])
        st.caption("⚠️ Inadimplência é um snapshot atual — os valores da coluna de comparação refletem o faturamento do período anterior como referência.")

    st.markdown("---")
    st.info("ℹ️ Inadimplência exibe o **saldo atual** (snapshot mais recente), independente do período selecionado.")
    fi = inad.groupby("faixa_atraso")["vl_divida"].sum().reset_index()
    fi.columns = ["Faixa", "Valor"]
    fi["Pct"] = fi["Valor"] / fi["Valor"].sum()
    fi["Rótulo"] = fi["Pct"].apply(lambda x: f"{x:.1%}")
    fig = px.bar(fi, x="Faixa", y="Valor", text="Rótulo",
                 title="Valor da Dívida por Faixa de Atraso",
                 color="Valor",
                 color_continuous_scale=["#FFF3CD", "#E74C3C"])
    fig.update_traces(textposition="outside")
    fig.update_layout(margin=dict(t=35, b=0, l=0, r=10),
                      xaxis_title="", yaxis_title="",
                      coloraxis_showscale=False)
    fig.update_yaxes(tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True)

    fi_q = inad.groupby("faixa_atraso").size().reset_index(name="Qtd")
    _cores_inad = ["#E74C3C","#E67E22","#F1C40F","#8E44AD","#2E86C1","#17A589"][:len(fi_q)]
    fig2 = go.Figure(data=[go.Pie(
        labels=fi_q["faixa_atraso"], values=fi_q["Qtd"],
        pull=[0.04] * len(fi_q),
        marker=dict(colors=_cores_inad, line=dict(color="white", width=2.5)),
        textposition="auto",
        texttemplate="<b>%{label}</b><br>%{percent:.1%}",
        textfont=dict(size=13, color="white", family="Arial Black"),
        outsidetextfont=dict(size=13, color="#1a1a1a", family="Arial Black"),
        hovertemplate="<b>%{label}</b><br>%{value} faturas<br>%{percent:.2%}<extra></extra>",
        insidetextorientation="radial", hole=0.08,
    )])
    fig2.update_layout(
        title=dict(text="Distribuição por Qtd de Faturas", font=dict(size=15)),
        margin=dict(t=60, b=80, l=80, r=160), height=500,
        legend=dict(orientation="v", xanchor="left", x=1.02, yanchor="middle", y=0.5,
                    font=dict(size=13, family="Arial"),
                    bgcolor="rgba(255,255,255,0.85)", bordercolor="rgba(180,180,180,0.4)", borderwidth=1),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig2, use_container_width=True)
    if "nm_bairro_dim" in inad.columns:
        ag_b = inad.groupby("nm_bairro_dim")["vl_divida"].sum()\
                   .sort_values(ascending=True).tail(15).reset_index()
        ag_b.columns = ["Bairro", "Valor"]
        n_b = len(ag_b)
        cores_b = [f"rgb({int(255+i*(158-255)/(max(n_b-1,1)))},{int(204+i*(34-204)/(max(n_b-1,1)))},{int(204+i*(34-204)/(max(n_b-1,1)))})" for i in range(n_b)]
        # degradê vermelho suave → vermelho escuro
        cores_b = [f"rgb({int(252-i*94/(max(n_b-1,1)))},{int(196-i*162/(max(n_b-1,1)))},{int(196-i*162/(max(n_b-1,1)))})" for i in range(n_b)]
        fig3 = go.Figure(go.Bar(
            x=ag_b["Valor"], y=ag_b["Bairro"], orientation="h",
            marker_color=cores_b, marker=dict(line=dict(width=0)),
            text=ag_b["Valor"].apply(lambda v: f"<b>R$ {v:,.0f}</b>".replace(",",".")),
            textposition="inside", textfont=dict(size=13, color="white", family="Arial Black"),
            insidetextanchor="end",
        ))
        fig3.update_layout(
            title="Top 15 Bairros — Inadimplência",
            margin=dict(t=40, b=0, l=0, r=20), height=480,
            xaxis=dict(title="", tickformat=",.0f"), yaxis=dict(title=""),
            uniformtext_minsize=9, uniformtext_mode="hide",
        )
        st.plotly_chart(fig3, use_container_width=True)

    # Corte pendente vs não pendente
    if "fl_corte_pendente" in inad.columns:
        cp = inad.copy()
        cp["Status Corte"] = cp["fl_corte_pendente"].map(
            {True: "Corte Pendente", False: "Sem Corte"})
        ag_cp = cp.groupby("Status Corte")["vl_divida"].sum().reset_index()
        ag_cp.columns = ["Status", "Valor"]
        _map_cp = {"Corte Pendente": COR["vermelho"], "Sem Corte": COR["amarelo"]}
        fig4 = go.Figure(data=[go.Pie(
            labels=ag_cp["Status"], values=ag_cp["Valor"],
            pull=[0.04] * len(ag_cp),
            marker=dict(colors=[_map_cp.get(s, COR["azul"]) for s in ag_cp["Status"]],
                        line=dict(color="white", width=2.5)),
            textposition="auto",
            texttemplate="<b>%{label}</b><br>%{percent:.1%}",
            textfont=dict(size=13, color="white", family="Arial Black"),
            outsidetextfont=dict(size=13, color="#1a1a1a", family="Arial Black"),
            hovertemplate="<b>%{label}</b><br>R$ %{value:,.0f}<br>%{percent:.2%}<extra></extra>",
            insidetextorientation="radial", hole=0.08,
        )])
        fig4.update_layout(
            title=dict(text="Inadimplência: Corte Pendente vs Sem Corte", font=dict(size=15)),
            margin=dict(t=50, b=20, l=20, r=20), height=380,
            legend=dict(orientation="v", xanchor="left", x=1.02, yanchor="middle", y=0.5,
                        font=dict(size=13, family="Arial"),
                        bgcolor="rgba(255,255,255,0.85)", bordercolor="rgba(180,180,180,0.4)", borderwidth=1),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig4, use_container_width=True)

    # Tabela detalhada
    with st.expander("📋 Tabela — Inadimplência por Bairro e Faixa"):
        if "nm_bairro_dim" in inad.columns:
            tb = inad.groupby(["nm_bairro_dim","faixa_atraso"]).agg(
                Qtd=("vl_divida","count"),
                Valor=("vl_divida","sum")
            ).reset_index()
            tb.columns = ["Bairro","Faixa","Qtd","Valor"]
            tb = tb.sort_values("Valor", ascending=False)
            st.dataframe(
                tb.style.format({"Valor": "R$ {:,.2f}", "Qtd": "{:,}"}),
                use_container_width=True
            )


def pg_servicos(D, d0, d1):
    page_header("Serviços Operacionais",
                f"{d0.strftime('%d/%m/%Y')} a {d1.strftime('%d/%m/%Y')}")

    tab_vis, tab_det = st.tabs(["📊 Visão Geral", "📂 Detalhe por Setor"])

    with tab_vis:
        _servicos_visao_geral(D, d0, d1)

    with tab_det:
        pg_setores(D, d0, d1, _sub=True)


def _servicos_visao_geral(D, d0, d1):
    srv = filtrar(D["srv"], "dt_solicitacao", d0, d1)
    bkl = filtrar(D["bkl"], "dt_ref", d0, d1)

    if srv.empty:
        st.warning("Sem dados de serviços no período.")
        return

    srv = merge_equipe(srv, D)
    srv = merge_bairro(srv, D, col="id_bairro")
    srv = merge_setor(srv, D)

    # ── Filtro de setor ───────────────────────────────────────────────────────
    if "nm_setor_operacional" in srv.columns:
        setores_disp = sorted(srv["nm_setor_operacional"].dropna().unique().tolist())
        setor_sel = st.selectbox("🏭 Setor Operacional", ["Todos os Setores"] + setores_disp)
        if setor_sel != "Todos os Setores":
            srv = srv[srv["nm_setor_operacional"] == setor_sel]

    qtd  = int(srv["qt_servico"].sum())
    fpr  = int(srv[srv["fl_fora_prazo"] == True]["qt_servico"].sum()) if "fl_fora_prazo" in srv.columns else 0
    sla  = (qtd - fpr) / qtd if qtd else 0
    t_med = srv["qt_tempo_execucao"].mean() / 60 if "qt_tempo_execucao" in srv.columns else 0
    bkl_p = int(bkl["qt_pendente"].sum()) if not bkl.empty else 0
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Total de Serviços",  qtd,   prefixo="")
    kpi(c2, "% SLA no Prazo",     sla,   prefixo="%")
    kpi(c3, "Tempo Médio Exec. (h)", t_med, prefixo="")
    kpi(c4, "Backlog Pendente",   bkl_p, prefixo="")

    # ── Bloco comparativo ─────────────────────────────────────────────────────
    _comp = _comp_periodo()
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _srv_c = filtrar(D["srv"], "dt_solicitacao", _cd0, _cd1)
        _qtd_c = int(_srv_c["qt_servico"].sum()) if not _srv_c.empty else 0
        _fpr_c = int(_srv_c[_srv_c["fl_fora_prazo"] == True]["qt_servico"].sum()) if not _srv_c.empty and "fl_fora_prazo" in _srv_c.columns else 0
        _sla_c = (_qtd_c - _fpr_c) / _qtd_c if _qtd_c else 0
        _tm_c  = _srv_c["qt_tempo_execucao"].mean() / 60 if not _srv_c.empty and "qt_tempo_execucao" in _srv_c.columns else 0
        render_comp_bloco(_comp["label_atual"], _comp["label_comp"], [
            ("Total de Serviços",  qtd,   _qtd_c, lambda v: f"{int(v):,}",  True),
            ("% SLA no Prazo",     sla,   _sla_c, lambda v: f"{v:.1%}",     True),
            ("Tempo Médio Exec.",  t_med, _tm_c,  lambda v: f"{v:.1f}h",    False),
        ])

    st.markdown("---")
    # Por canal de atendimento — agrupa Interno (3) + Automático-Sistema (4) como "Ações Internas"
    srv_can = srv.copy()
    # Remove canais irrelevantes
    _canais_excluir = ["Automático - Sistema", "Interno"]
    srv_can = srv_can[
        ~srv_can["nm_tipo_atendimento"].str.upper().str.contains("RESERVADO", na=False) &
        ~srv_can["nm_tipo_atendimento"].isin(_canais_excluir)
    ]

    # ── Evolução mensal por canal ──────────────────────────────────────────────
    srv_can["_mes"] = pd.to_datetime(srv_can["dt_solicitacao"]).dt.strftime("%m/%Y")
    ag_can_m = srv_can.groupby(["_mes", "nm_tipo_atendimento"])["qt_servico"].sum().reset_index()
    ag_can_m.columns = ["Mês", "Canal", "Qtd"]
    meses_ord_can = sorted(ag_can_m["Mês"].unique().tolist(),
                           key=lambda x: pd.to_datetime(x, format="%m/%Y"))

    # Exclui canais irrelevantes: < 1% do total e "RESERVADO PARA O FUTURO"
    total_can = ag_can_m["Qtd"].sum()
    canais_rel = ag_can_m.groupby("Canal")["Qtd"].sum()
    canais_rel = canais_rel[
        (canais_rel / total_can >= 0.01) &
        (~canais_rel.index.str.upper().str.contains("RESERVADO"))
    ].index.tolist()
    ag_can_m = ag_can_m[ag_can_m["Canal"].isin(canais_rel)]

    _cores_can = px.colors.qualitative.Set2
    fig_can = px.bar(ag_can_m, x="Mês", y="Qtd", color="Canal",
                     barmode="group",
                     title="Serviços por Canal de Atendimento (mensal)",
                     color_discrete_sequence=_cores_can,
                     category_orders={"Mês": meses_ord_can},
                     text="Qtd")
    fig_can.update_traces(textposition="inside", textangle=-90,
                          textfont=dict(size=12, color="white", family="Arial Black"),
                          insidetextanchor="middle")
    # Linha de média por canal
    for i, canal in enumerate(ag_can_m["Canal"].unique()):
        media_c = ag_can_m[ag_can_m["Canal"] == canal]["Qtd"].mean()
        fig_can.add_hline(
            y=media_c, line_dash="dot",
            line_color=_cores_can[i % len(_cores_can)], line_width=1.5,
            annotation_text=f"<b>Méd. {canal}: {media_c:.0f}</b>",
            annotation_position="top right",
            annotation_font=dict(size=11, color=_cores_can[i % len(_cores_can)]),
        )
    fig_can.update_layout(
        margin=dict(t=50, b=50, l=0, r=20), height=450,
        xaxis=dict(title="", categoryorder="array", categoryarray=meses_ord_can),
        yaxis=dict(title=""),
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5,
                    font=dict(size=12)),
        hovermode="x unified",
        uniformtext_minsize=8, uniformtext_mode="hide",
    )
    st.plotly_chart(fig_can, use_container_width=True)

    # SLA por canal — evolução mensal
    if "fl_fora_prazo" in srv_can.columns:
        srv_sla = srv_can.copy()
        srv_sla["_mes"] = pd.to_datetime(srv_sla["dt_solicitacao"]).dt.strftime("%m/%Y")
        ag_sla_m = srv_sla.groupby(["_mes","nm_tipo_atendimento"]).agg(
            Total=("qt_servico","sum"),
            ForaPrazo=("fl_fora_prazo", lambda x: (x == True).sum())
        ).reset_index()
        ag_sla_m["%SLA"] = (ag_sla_m["Total"] - ag_sla_m["ForaPrazo"]) / ag_sla_m["Total"] * 100
        ag_sla_m.rename(columns={"_mes":"Mês","nm_tipo_atendimento":"Canal"}, inplace=True)
        meses_sla = sorted(ag_sla_m["Mês"].unique().tolist(),
                           key=lambda x: pd.to_datetime(x, format="%m/%Y"))
        fig2 = px.bar(ag_sla_m, x="Mês", y="%SLA", color="Canal",
                      barmode="group",
                      title="% SLA no Prazo por Canal (mensal)",
                      color_discrete_sequence=px.colors.qualitative.Set2,
                      category_orders={"Mês": meses_sla},
                      text=ag_sla_m["%SLA"].apply(lambda v: f"<b>{v:.0f}%</b>"))
        fig2.update_traces(textposition="inside", textangle=-90,
                           textfont=dict(size=12, color="white", family="Arial Black"),
                           insidetextanchor="middle")
        fig2.add_hline(y=90, line_dash="dash", line_color="gray", line_width=1.5,
                       annotation_text="<b>Meta 90%</b>", annotation_position="top left",
                       annotation_font=dict(size=11, color="gray"))
        fig2.update_layout(
            margin=dict(t=50, b=50, l=0, r=20), height=420,
            xaxis=dict(title="", categoryorder="array", categoryarray=meses_sla),
            yaxis=dict(title="", ticksuffix="%", range=[0, 110]),
            legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5,
                        font=dict(size=12)),
            hovermode="x unified",
            uniformtext_minsize=8, uniformtext_mode="hide",
        )
        st.plotly_chart(fig2, use_container_width=True)
    # Evolução mensal SLA — exclui solicitações internas (mesma regra de srv_can)
    srv_m = srv_can.copy()   # usa srv_can que já excluiu Interno/Automático/Reservado
    srv_m["_mes"] = pd.to_datetime(srv_m["dt_solicitacao"]).dt.strftime("%m/%Y")
    if "fl_fora_prazo" in srv_m.columns:
        srv_m["Status SLA"] = srv_m["fl_fora_prazo"].apply(
            lambda x: "Fora do Prazo" if x == True else "No Prazo"
        )
    else:
        srv_m["Status SLA"] = "No Prazo"
    ag_m = srv_m.groupby(["_mes","Status SLA"])["qt_servico"].sum().reset_index()
    ag_m.columns = ["Mês","SLA","Qtd"]
    meses_m = sorted(ag_m["Mês"].unique().tolist(), key=lambda x: pd.to_datetime(x, format="%m/%Y"))
    _comp = _comp_periodo()
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _srv_cg = filtrar(D["srv"], "dt_solicitacao", _cd0, _cd1)
        if not _srv_cg.empty:
            _sm_c = _srv_cg.copy()
            _sm_c = _sm_c[~_sm_c["nm_tipo_atendimento"].isin(_canais_excluir) &
                          ~_sm_c["nm_tipo_atendimento"].str.upper().str.contains("RESERVADO", na=False)]
            _sm_c["_mes"] = pd.to_datetime(_sm_c["dt_solicitacao"]).dt.strftime("%m/%Y")
            _sm_c["Status SLA"] = _sm_c["fl_fora_prazo"].apply(
                lambda x: f"Fora do Prazo ({_comp['label_comp']})" if x == True else f"No Prazo ({_comp['label_comp']})"
            ) if "fl_fora_prazo" in _sm_c.columns else f"No Prazo ({_comp['label_comp']})"
            _ag_mc = _sm_c.groupby(["_mes","Status SLA"])["qt_servico"].sum().reset_index()
            _ag_mc.columns = ["Mês","SLA","Qtd"]
            ag_m = pd.concat([ag_m, _ag_mc], ignore_index=True)
    # Meta: % No Prazo ≥ 90% → linha de referência sobre total mensal
    ag_total_m = ag_m[ag_m["SLA"].isin(["No Prazo","Fora do Prazo"])].groupby("Mês")["Qtd"].sum()
    meta_vals  = (ag_total_m * 0.90).reindex(meses_m)
    fig3 = px.bar(ag_m, x="Mês", y="Qtd", color="SLA", barmode="group",
                  title="Serviços Mensais — No Prazo vs Fora do Prazo" + (f" ({_comp['label_atual']} vs {_comp['label_comp']})" if _comp else ""),
                  color_discrete_map={"No Prazo": COR["verde"], "Fora do Prazo": COR["vermelho"]},
                  category_orders={"Mês": meses_m},
                  text="Qtd")
    fig3.update_traces(textposition="inside", textangle=-90,
                       textfont=dict(size=13, color="white", family="Arial Black"),
                       insidetextanchor="middle")
    # Destaque nas barras de comparativo
    if _comp:
        for trace in fig3.data:
            if _comp["label_comp"] in trace.name:
                trace.textfont = dict(size=14, color="#1a1a1a", family="Arial Black")
    # Linha de meta 90%
    fig3.add_scatter(x=meses_m, y=meta_vals.values, mode="lines+markers",
                     name="Meta 90% (No Prazo)",
                     line=dict(color="#1A5276", width=2, dash="dash"),
                     marker=dict(size=5, color="#1A5276"))
    fig3.update_layout(
        margin=dict(t=50, b=50, l=0, r=20), height=450,
        xaxis=dict(title="", categoryorder="array", categoryarray=meses_m),
        yaxis=dict(title="Qtd Serviços"),
        legend=dict(orientation="h", yanchor="top", y=-0.12, xanchor="center", x=0.5,
                    font=dict(size=12)),
        hovermode="x unified",
        uniformtext_minsize=8, uniformtext_mode="hide",
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Por equipe
    if "nm_equipe" in srv.columns:
        ag_eq = srv.groupby("nm_equipe")["qt_servico"].sum()\
                   .sort_values(ascending=True).tail(12).reset_index()
        ag_eq.columns = ["Equipe","Qtd"]
        fig4 = px.bar(ag_eq, x="Qtd", y="Equipe", orientation="h",
                      title="Serviços por Equipe (Top 12)",
                      color_discrete_sequence=[COR["azul_c"]])
        fig4.update_layout(margin=dict(t=35, b=0, l=0, r=20), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig4, use_container_width=True)

    # Backlog
    if not bkl.empty:
        st.markdown("#### Evolução do Backlog")
        bkl_m = bkl.copy()
        bkl_m["_mes"] = pd.to_datetime(bkl_m["dt_ref"]).dt.to_period("M").dt.to_timestamp()
        ag_bkl = bkl_m.groupby("_mes").agg(
            Solicitado=("qt_solicitado","sum"),
            Executado=("qt_executado","sum"),
            Pendente=("qt_pendente","sum"),
        ).reset_index().rename(columns={"_mes":"Mês"})
        ag_melt = ag_bkl.melt(id_vars="Mês", var_name="Status", value_name="Qtd")
        fig5 = px.line(ag_melt, x="Mês", y="Qtd", color="Status", markers=True,
                       title="Backlog de Serviços",
                       color_discrete_map={
                           "Solicitado": COR["azul"], "Executado": COR["verde"],
                           "Pendente": COR["vermelho"]
                       })
        fig5.update_layout(margin=dict(t=35, b=0, l=0, r=20), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig5, use_container_width=True)


def pg_cortes(D, d0, d1):
    page_header("Cobrança e Recuperação de Receita",
                f"{d0.strftime('%d/%m/%Y')} a {d1.strftime('%d/%m/%Y')}")

    cor = filtrar(D["cor"], "dt_solicitacao", d0, d1)
    rel = filtrar(D["rel"], "dt_reliagacao",  d0, d1)

    # KPI de cortes: COUNT(id_servico único) de CAVALETE FALTA PAGAMENTO (def=30)
    # filtrado por dt_fim_execucao — alinhado com Cubo Gerencial (Referencia=mês execução)
    cor_fim = filtrar(D["cor"], "dt_fim_execucao", d0, d1)
    cor_cavalete = (cor_fim[cor_fim["id_servico_definicao"] == 30]
                    if not cor_fim.empty and "id_servico_definicao" in cor_fim.columns
                    else cor_fim)
    qtd_cor = int(cor_cavalete["id_servico"].nunique()) if not cor_cavalete.empty and "id_servico" in cor_cavalete.columns else 0

    # cor por dt_solicitacao permanece para os gráficos de evolução
    if not cor.empty and "id_situacao_ligacao" in cor.columns:
        cor = cor[cor["id_situacao_ligacao"] != 1]

    cor = merge_bairro(cor, D)

    # Tempo médio de execução do corte: dt_solicitacao -> dt_fim_execucao (em horas)
    # fl_fora_prazo do sistema não é confiável (dt_limite_execucao = meia-noite do dia,
    # toda OS criada após 00:00h já nasce "fora do prazo"). Aguardar prazo definido pela empresa.
    if not cor_cavalete.empty and "dt_solicitacao" in cor_cavalete.columns and "dt_fim_execucao" in cor_cavalete.columns:
        _sol = pd.to_datetime(cor_cavalete["dt_solicitacao"])
        _fim = pd.to_datetime(cor_cavalete["dt_fim_execucao"])
        t_exec_h = (_fim - _sol).dt.total_seconds().mean() / 3600
    else:
        t_exec_h = 0
    t_med = cor_cavalete["qt_tempo_execucao"].mean() / 60 if not cor_cavalete.empty and "qt_tempo_execucao" in cor_cavalete.columns else 0

    # Religações com SLA calculado
    rel = calcular_sla_religacao(rel)

    if not rel.empty and "id_servico_definicao" in rel.columns:
        rel_normal  = rel[rel["id_servico_definicao"] == 56]
        rel_urgente = rel[rel["id_servico_definicao"] == 329]
        rel_outros  = rel[~rel["id_servico_definicao"].isin([56, 329])]
        rel_cav     = rel[rel["id_servico_definicao"].isin([56, 329])]
    else:
        rel_normal = rel_urgente = rel_outros = rel_cav = rel

    def _nuniq(df): return int(df["id_servico"].nunique()) if not df.empty and "id_servico" in df.columns else 0
    def _sla(df):   return df["fl_no_prazo_rel"].sum() / len(df) if not df.empty and "fl_no_prazo_rel" in df.columns and len(df) else 0
    def _dmed(df):  return df["dias_corte_religacao"].mean() if not df.empty and "dias_corte_religacao" in df.columns else 0

    qtd_rel         = _nuniq(rel_cav)
    qtd_rel_normal  = _nuniq(rel_normal)
    qtd_rel_urgente = _nuniq(rel_urgente)
    qtd_rel_outros  = _nuniq(rel_outros)
    sla_rel_normal  = _sla(rel_normal)
    sla_rel_urgente = _sla(rel_urgente)
    d_med           = _dmed(rel_cav)
    d_med_normal    = _dmed(rel_normal)
    d_med_urgente   = _dmed(rel_urgente)
    taxa_r = qtd_rel / qtd_cor if qtd_cor else 0

    # ── KPIs — linha 1: cortes e religações ──────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    kpi(c1, "Cortes Executados",        qtd_cor,        prefixo="")
    kpi(c2, "Religações (cavalete)",    qtd_rel,        prefixo="")
    kpi(c3, "Taxa Religação/Corte",     taxa_r,         prefixo="%")
    kpi_str(c4, "Tempo Médio Execução", f"{t_exec_h:.1f}h",
            help="Da solicitação ao fim da execução (sol→fim). SLA pendente de definição pela empresa.")
    kpi_str(c5, "Tempo Médio Operação", f"{t_med:.1f}h",
            help="Tempo cronometrado na execução em campo.")

    # ── KPIs — linha 2: SLA religações ───────────────────────────────────────
    r1, r2, r3, r4, r5 = st.columns(5)
    kpi(r1, "Normal (24h)",        qtd_rel_normal,  prefixo="")
    kpi(r2, "% Normal no Prazo",   sla_rel_normal,  prefixo="%", delta_inv=False)
    kpi(r3, "Urgente (6h/14h)",    qtd_rel_urgente, prefixo="")
    kpi(r4, "% Urgente no Prazo",  sla_rel_urgente, prefixo="%", delta_inv=False)
    kpi_str(r5, "Outros tipos", f"{qtd_rel_outros:,}".replace(",", "."),
            help="Ramal, reativação etc.")

    st.caption(
        "SLA: Normal = 24h | Urgente expediente (seg-sex 08–18h) = 6h | "
        "Urgente fora expediente/feriado = 14h — contado a partir da solicitação (dt_solicitacao)"
    )

    # ── Bloco comparativo ─────────────────────────────────────────────────────
    _comp = _comp_periodo()
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _cor_c = filtrar(D["cor"], "dt_fim_execucao", _cd0, _cd1)
        if not _cor_c.empty and "id_servico_definicao" in _cor_c.columns:
            _cor_c = _cor_c[_cor_c["id_servico_definicao"] == 30]
        _rel_c = filtrar(D["rel"], "dt_reliagacao", _cd0, _cd1)
        _rel_c = calcular_sla_religacao(_rel_c)
        if not _rel_c.empty and "id_servico_definicao" in _rel_c.columns:
            _rel_cav_c = _rel_c[_rel_c["id_servico_definicao"].isin([56, 329])]
        else:
            _rel_cav_c = _rel_c
        _co_c  = int(_cor_c["id_servico"].nunique()) if not _cor_c.empty and "id_servico" in _cor_c.columns else 0
        _re_c  = int(_rel_cav_c["id_servico"].nunique()) if not _rel_cav_c.empty and "id_servico" in _rel_cav_c.columns else 0
        _tx_c  = _re_c / _co_c if _co_c else 0
        _sn_c  = _sla(_rel_c[_rel_c["id_servico_definicao"] == 56]) if not _rel_c.empty and "id_servico_definicao" in _rel_c.columns else 0
        render_comp_bloco(_comp["label_atual"], _comp["label_comp"], [
            ("Cortes Executados",      qtd_cor,        _co_c, lambda v: f"{int(v):,}",  False),
            ("Religações (cavalete)",  qtd_rel,        _re_c, lambda v: f"{int(v):,}",  None),
            ("Taxa Religação/Corte",   taxa_r,         _tx_c, lambda v: f"{v:.1%}",     True),
            ("SLA Religação Normal",   sla_rel_normal, _sn_c, lambda v: f"{v:.1%}",     True),
        ])

    st.markdown("---")
    if not cor.empty:
        cor_m = cor.drop_duplicates("id_servico").copy()
        cor_m["_mes"] = pd.to_datetime(cor_m["dt_solicitacao"]).dt.strftime("%m/%Y")
        ag_c = cor_m.groupby("_mes")["id_servico"].nunique().reset_index()
        ag_c.columns = ["Mês", "Qtd"]
        ag_c["Tipo"] = "Cortes"

        frames_cr = [ag_c]
        if not rel_cav.empty:
            rel_m = rel_cav.drop_duplicates("id_servico").copy()
            rel_m["_mes"] = pd.to_datetime(rel_m["dt_reliagacao"]).dt.strftime("%m/%Y")
            ag_r = rel_m.groupby("_mes")["id_servico"].nunique().reset_index()
            ag_r.columns = ["Mês", "Qtd"]
            ag_r["Tipo"] = "Religações"
            frames_cr.append(ag_r)

        df_cr = pd.concat(frames_cr)
        _comp = _comp_periodo()
        if _comp:
            _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
            _cor_cg = filtrar(D["cor"], "dt_solicitacao", _cd0, _cd1)
            _rel_cg = filtrar(D["rel"], "dt_reliagacao",  _cd0, _cd1)
            if not _cor_cg.empty:
                _cg_m = _cor_cg.drop_duplicates("id_servico").copy()
                _cg_m["_mes"] = pd.to_datetime(_cg_m["dt_solicitacao"]).dt.strftime("%m/%Y")
                _ag_cg = _cg_m.groupby("_mes")["id_servico"].nunique().reset_index()
                _ag_cg.columns = ["Mês","Qtd"]; _ag_cg["Tipo"] = f"Cortes ({_comp['label_comp']})"
                df_cr = pd.concat([df_cr, _ag_cg])
            if not _rel_cg.empty:
                _rg_m = _rel_cg.drop_duplicates("id_servico").copy()
                _rg_m["_mes"] = pd.to_datetime(_rg_m["dt_reliagacao"]).dt.strftime("%m/%Y")
                _ag_rg = _rg_m.groupby("_mes")["id_servico"].nunique().reset_index()
                _ag_rg.columns = ["Mês","Qtd"]; _ag_rg["Tipo"] = f"Religações ({_comp['label_comp']})"
                df_cr = pd.concat([df_cr, _ag_rg])
        meses_ord = sorted(df_cr["Mês"].unique(), key=lambda x: pd.to_datetime(x, format="%m/%Y"))
        _cor_s = df_cr[df_cr["Tipo"] == "Cortes"].set_index("Mês")["Qtd"].reindex(meses_ord, fill_value=0)
        _rel_s = df_cr[df_cr["Tipo"] == "Religações"].set_index("Mês")["Qtd"].reindex(meses_ord, fill_value=0)
        fig = go.Figure()
        fig.add_bar(
            x=meses_ord, y=_cor_s.values, name="Cortes",
            marker_color=COR["vermelho"],
            text=_cor_s.values,
            textposition="inside",
            textangle=-90,
            insidetextanchor="middle",
            textfont=dict(family="Arial Black", color="white", size=13),
        )
        fig.add_bar(
            x=meses_ord, y=_rel_s.values, name="Religações",
            marker_color=COR["verde"],
            text=_rel_s.values,
            textposition="inside",
            textangle=-90,
            insidetextanchor="middle",
            textfont=dict(family="Arial Black", color="white", size=13),
        )
        if _comp:
            _label_c = _comp["label_comp"]
            _cor_c_s = df_cr[df_cr["Tipo"] == f"Cortes ({_label_c})"].set_index("Mês")["Qtd"].reindex(meses_ord, fill_value=0)
            _rel_c_s = df_cr[df_cr["Tipo"] == f"Religações ({_label_c})"].set_index("Mês")["Qtd"].reindex(meses_ord, fill_value=0)
            fig.add_bar(
                x=meses_ord, y=_cor_c_s.values, name=f"Cortes ({_label_c})",
                marker=dict(color=COR["vermelho"], pattern_shape="/", opacity=0.5),
                text=_cor_c_s.values, textposition="inside", textangle=-90,
                insidetextanchor="middle",
                textfont=dict(family="Arial Black", color="#0d2e50", size=12),
            )
            fig.add_bar(
                x=meses_ord, y=_rel_c_s.values, name=f"Religações ({_label_c})",
                marker=dict(color=COR["verde"], pattern_shape="/", opacity=0.5),
                text=_rel_c_s.values, textposition="inside", textangle=-90,
                insidetextanchor="middle",
                textfont=dict(family="Arial Black", color="#0d2e50", size=12),
            )
        # Médias — apenas dos meses com valor > 0 (exclui meses parciais zerados)
        _media_cor = _cor_s[_cor_s > 0].mean() if (_cor_s > 0).any() else 0
        _media_rel = _rel_s[_rel_s > 0].mean() if (_rel_s > 0).any() else 0
        fig.add_hline(y=_media_cor, line_dash="dash", line_color=COR["vermelho"], line_width=1.8)
        fig.add_annotation(
            xref="paper", yref="y", x=1, y=_media_cor,
            text=f"<b>Média Cortes: {_media_cor:,.0f}</b>".replace(",", "."),
            showarrow=False, xanchor="right", yanchor="bottom",
            font=dict(size=11, color=COR["vermelho"], family="Arial Black"),
            bgcolor="rgba(255,255,255,0.8)", borderpad=2,
        )
        fig.add_hline(y=_media_rel, line_dash="dash", line_color=COR["verde"], line_width=1.8)
        fig.add_annotation(
            xref="paper", yref="y", x=1, y=_media_rel,
            text=f"<b>Média Religações: {_media_rel:,.0f}</b>".replace(",", "."),
            showarrow=False, xanchor="right", yanchor="top",
            font=dict(size=11, color=COR["verde"], family="Arial Black"),
            bgcolor="rgba(255,255,255,0.8)", borderpad=2,
        )
        fig.update_layout(
            title="Cortes vs Religações (mensal)" + (f" — {_comp['label_atual']} vs {_comp['label_comp']}" if _comp else ""),
            barmode="group",
            margin=dict(t=40, b=0, l=0, r=20),
            xaxis_title="", yaxis_title="",
            legend=dict(
                orientation="v",
                yanchor="top", y=1,
                xanchor="left", x=1.01,
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="rgba(0,0,0,0.1)", borderwidth=1,
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Distribuição por tempo de execução (sol→fim) — em faixas de horas
    if not cor_cavalete.empty and "dt_solicitacao" in cor_cavalete.columns and "dt_fim_execucao" in cor_cavalete.columns:
        cex = cor_cavalete.drop_duplicates("id_servico").copy()
        cex["h_exec"] = (pd.to_datetime(cex["dt_fim_execucao"]) - pd.to_datetime(cex["dt_solicitacao"])).dt.total_seconds() / 3600
        bins   = [0, 4, 8, 24, 48, float("inf")]
        labels = ["Até 4h", "4h-8h", "8h-24h", "24h-48h", "Acima 48h"]
        cex["Faixa"] = pd.cut(cex["h_exec"], bins=bins, labels=labels, right=True)
        ag_faixa = cex["Faixa"].value_counts().reindex(labels).reset_index()
        ag_faixa.columns = ["Faixa", "Qtd"]
        fig2 = px.bar(ag_faixa, x="Faixa", y="Qtd", text="Qtd",
                      title="Cortes: Tempo de Execução (sol→fim)",
                      color_discrete_sequence=[COR["azul"]])
        fig2.update_traces(textposition="outside")
        fig2.update_layout(margin=dict(t=35, b=0, l=0, r=10),
                           xaxis_title="", yaxis_title="Protocolos")
        st.plotly_chart(fig2, use_container_width=True)
    if "nm_bairro_dim" in cor.columns:
        ag_b = cor.groupby("nm_bairro_dim")["qt_servico"].sum()\
                  .sort_values(ascending=True).tail(15).reset_index()
        ag_b.columns = ["Bairro","Qtd"]
        fig3 = px.bar(ag_b, x="Qtd", y="Bairro", orientation="h",
                      title="Top 15 Bairros — Cortes",
                      color_discrete_sequence=[COR["vermelho"]])
        fig3.update_layout(margin=dict(t=35, b=0, l=0, r=20), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig3, use_container_width=True)

    if not rel.empty and "dias_corte_religacao" in rel.columns and "id_servico_definicao" in rel.columns:
        rel_hist = rel.copy()
        rel_hist["Tipo Religação"] = rel_hist["id_servico_definicao"].map(
            {56: "Normal", 329: "Urgente"}).fillna("Outros")
        bins_d   = [0, 1, 2, 3, 4, 5, float("inf")]
        labels_d = ["1 dia", "2 dias", "3 dias", "4 dias", "5 dias", "Acima de 5 dias"]
        rel_hist["Faixa"] = pd.cut(rel_hist["dias_corte_religacao"],
                                   bins=bins_d, labels=labels_d, right=True)
        ag_h = (rel_hist.groupby(["Faixa", "Tipo Religação"], observed=True)
                        .size().reset_index(name="Qtd"))
        fig4 = px.bar(ag_h, x="Faixa", y="Qtd", color="Tipo Religação",
                      barmode="stack", text="Qtd",
                      title="Tempo entre abertura e encerramento das Ordens de Corte",
                      color_discrete_map={"Normal": COR["azul_c"], "Urgente": COR["vermelho"], "Outros": COR["cinza"]},
                      category_orders={"Faixa": labels_d})
        fig4.update_traces(textposition="inside", textfont=dict(size=13))
        fig4.update_layout(margin=dict(t=35, b=0, l=0, r=20),
                           xaxis_title="", yaxis_title="Qtd")
        st.plotly_chart(fig4, use_container_width=True)

    # Valor pendência nos cortes
    if not cor.empty and "vl_pendencia_atual" in cor.columns:
        st.markdown("#### Valor de Inadimplência nos Cortes")
        cor_bk = cor.copy()
        if "nm_bairro_dim" in cor_bk.columns:
            ag_vl = cor_bk.groupby("nm_bairro_dim")["vl_pendencia_atual"].sum()\
                          .sort_values(ascending=False).head(10).reset_index()
            ag_vl.columns = ["Bairro","Valor Pendência"]
            st.dataframe(
                ag_vl.style.format({"Valor Pendência": "R$ {:,.2f}"}),
                use_container_width=True
            )


def pg_leituras(D, d0, d1, _sub=False):
    if not _sub:
        page_header("Leituras e Hidrômetros",
                    f"{d0.strftime('%d/%m/%Y')} a {d1.strftime('%d/%m/%Y')}")

    lei = filtrar(D["lei"], "dt_ref", d0, d1)

    if lei.empty:
        st.warning("Sem dados de leitura no período.")
        return

    lei = merge_leiturista(lei, D)
    lei = merge_bairro(lei, D)

    qtd_lei = int(lei["qt_leitura"].sum())
    vol_lid = int(lei["qt_volume_lido"].sum())
    vol_fat = int(lei["qt_volume_faturado"].sum())
    criticas = int((lei["fl_critica"] == True).sum()) if "fl_critica" in lei.columns else 0
    efic_lei = (lei["fl_erro_leitura"] == 0).sum() / len(lei) if len(lei) else 0
    perdas   = vol_lid - vol_fat
    idx_perd = perdas / vol_lid if vol_lid else 0
    c1, c2, c3 = st.columns(3)
    kpi(c1, "Leituras Realizadas", qtd_lei, prefixo="")
    kpi(c2, "Volume Lido (m³)", vol_lid, prefixo="")
    kpi(c3, "Volume Faturado (m³)", vol_fat, prefixo="")

    c4, c5 = st.columns(2)
    kpi(c4, "Leituras Críticas", criticas, prefixo="")
    kpi(c5, "Índice de Perdas", idx_perd, prefixo="%")

    # ── Bloco comparativo ─────────────────────────────────────────────────────
    _comp = _comp_periodo()
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _lei_c   = filtrar(D["lei"], "dt_ref", _cd0, _cd1)
        _qtd_c   = int(_lei_c["qt_leitura"].sum())        if not _lei_c.empty else 0
        _vlid_c  = int(_lei_c["qt_volume_lido"].sum())    if not _lei_c.empty else 0
        _vfat_c  = int(_lei_c["qt_volume_faturado"].sum()) if not _lei_c.empty else 0
        _perd_c  = _vlid_c - _vfat_c
        _iperd_c = _perd_c / _vlid_c if _vlid_c else 0
        _crit_c  = int((_lei_c["fl_critica"] == True).sum()) if not _lei_c.empty and "fl_critica" in _lei_c.columns else 0
        render_comp_bloco(_comp["label_atual"], _comp["label_comp"], [
            ("Leituras Realizadas",  qtd_lei,  _qtd_c,  lambda v: f"{int(v):,}",    True),
            ("Volume Lido (m³)",     vol_lid,  _vlid_c, lambda v: f"{int(v):,} m³", None),
            ("Volume Faturado (m³)", vol_fat,  _vfat_c, lambda v: f"{int(v):,} m³", True),
            ("Leituras Críticas",    criticas, _crit_c, lambda v: f"{int(v):,}",    False),
            ("Índice de Perdas",     idx_perd, _iperd_c,lambda v: f"{v:.1%}",       False),
        ])

    st.markdown("---")
    lei_m = lei.copy()
    lei_m["_mes"] = pd.to_datetime(lei_m["dt_ref"]).dt.to_period("M").dt.to_timestamp()
    ag = lei_m.groupby("_mes").agg(
        Lido=("qt_volume_lido","sum"),
        Faturado=("qt_volume_faturado","sum")
    ).reset_index().rename(columns={"_mes":"Mês"})
    ag_m = ag.melt(id_vars="Mês", var_name="Tipo", value_name="m³")
    _comp = _comp_periodo()
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _lei_cg = filtrar(D["lei"], "dt_ref", _cd0, _cd1)
        if not _lei_cg.empty:
            _lc = _lei_cg.copy()
            _lc["_mes"] = pd.to_datetime(_lc["dt_ref"]).dt.to_period("M").dt.to_timestamp()
            _ag_c = _lc.groupby("_mes").agg(Lido=("qt_volume_lido","sum"),Faturado=("qt_volume_faturado","sum")).reset_index().rename(columns={"_mes":"Mês"})
            _ag_c_m = _ag_c.melt(id_vars="Mês", var_name="Tipo", value_name="m³")
            _ag_c_m["Tipo"] = _ag_c_m["Tipo"] + f" ({_comp['label_comp']})"
            ag_m = pd.concat([ag_m, _ag_c_m], ignore_index=True)
    fig = px.line(ag_m, x="Mês", y="m³", color="Tipo", markers=True,
                  title="Volume Lido vs Faturado (m³ mensal)" + (f" — {_comp['label_atual']} vs {_comp['label_comp']}" if _comp else ""),
                  color_discrete_map={"Lido": COR["azul"], "Faturado": COR["verde"]})
    if _comp:
        for trace in fig.data:
            if _comp["label_comp"] in trace.name:
                trace.line = dict(dash="dot")
                trace.opacity = 0.6
    fig.update_layout(margin=dict(t=35, b=0, l=0, r=20), xaxis_title="", yaxis_title="")
    fig.update_yaxes(tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True)

    # ════ Leituras por Referência (Mês) - Stacked por Leiturista ════════════════════
    lei_ref = lei.copy()
    lei_ref["_mes"] = pd.to_datetime(lei_ref["dt_ref"]).dt.to_period("M").dt.to_timestamp()

    if not lei_ref.empty and "nm_leiturista_dim" in lei_ref.columns:
        # Agregação por mês E leiturista
        ag_ref_lr = lei_ref.groupby(["_mes", "nm_leiturista_dim"]).agg(
            Leituras=("qt_leitura","sum")
        ).reset_index()

        # Agregação por mês (para calcular %Críticas do mês)
        ag_ref_totais = lei_ref.groupby("_mes").agg(
            Críticas=("fl_critica", lambda x: (x == True).sum()),
            Total_Leituras=("qt_leitura","sum")
        ).reset_index()
        ag_ref_totais["%Críticas"] = ag_ref_totais["Críticas"] / ag_ref_totais["Total_Leituras"]

        # Mesclar para ter %Críticas em cada linha
        ag_ref_lr = ag_ref_lr.merge(ag_ref_totais[["_mes", "%Críticas"]], on="_mes")

        # Formatar mês
        ag_ref_lr["Referência"] = ag_ref_lr["_mes"].dt.strftime("%b/%Y")
        ag_ref_lr = ag_ref_lr.sort_values("_mes", ascending=True)

        # Criar gráfico stacked por leiturista (vertical)
        fig2 = px.bar(ag_ref_lr, x="Referência", y="Leituras", color="nm_leiturista_dim",
                      barmode="stack",
                      title="",
                      labels={"nm_leiturista_dim": "Leiturista", "Leituras": "Quantidade"})

        # Atualizar cores para melhor visualização
        fig2.update_traces(marker=dict(line=dict(width=0)))

        # Adicionar %Críticas acima de cada barra
        for idx, row in ag_ref_totais.iterrows():
            fig2.add_annotation(
                x=row["_mes"].strftime("%b/%Y"),
                y=row["Total_Leituras"],
                text=f"{row['%Críticas']:.1%}",
                showarrow=False,
                yshift=10,
                font=dict(size=11, color="#E74C3C", family="Arial Black")
            )

        fig2.update_layout(
            margin=dict(t=35, b=120, l=0, r=20),
            xaxis_title="", yaxis_title="Quantidade de Leituras",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.25,
                xanchor="center",
                x=0.5,
                font=dict(size=10),
                bgcolor="rgba(255,255,255,0.9)",
                bordercolor="rgba(0,0,0,0.2)",
                borderwidth=1
            ),
            hovermode="x unified"
        )
        st.markdown("### Leituras por Referência (Mês) - Distribuição por Leiturista + <span style='color:#E74C3C'>Porcentagens de Leituras Criticadas</span>", unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)

        # Mostrar tabela com detalhe mensal e %Críticas
        st.subheader("Resumo de Leituras por Mês")
        resumo = ag_ref_totais.copy()
        resumo["Referência"] = resumo["_mes"].dt.strftime("%b/%Y")
        resumo.columns = ["_mes", "Críticas", "Total_Leituras", "%Críticas", "Referência"]
        resumo["%Críticas"] = resumo["%Críticas"].apply(lambda x: f"{x:.2%}")
        resumo = resumo[["Referência", "Total_Leituras", "Críticas", "%Críticas"]].sort_values("Referência", ascending=False)
        resumo.columns = ["Referência", "Total de Leituras", "Leituras Críticas", "%Críticas"]
        st.dataframe(resumo.reset_index(drop=True), use_container_width=True)
    # ════ CÁLCULO DE EFICIÊNCIA DE LEITURA ════════════════════════════════════════
    # Passo 1: Total de Leituras Realizadas por Mês (referência)
    lei_m = lei.copy()
    lei_m["_mes"] = pd.to_datetime(lei_m["dt_ref"]).dt.to_period("M").dt.to_timestamp()
    total_leituras = lei_m.groupby("_mes").agg(
        Total_Leituras=("qt_leitura","sum")
    ).reset_index()
    total_leituras.columns = ["Mês", "Total_Leituras"]

    # Passo 2: Ordens de Correção Executadas (ID=42, Situação=3 "Encerrado - Executado")
    srv_m = D["srv"].copy()
    srv_correcoes = srv_m[
        (srv_m["id_servico_definicao"] == 42) &  # Serviço 1042 (ALTERAÇÃO DE FATURA - ERRO LEITURA)
        (srv_m["id_situacao_servico"] == 3) &    # Situação 3 = Encerrado - Executado
        (srv_m["dt_fim_execucao"].notna())       # Data de execução preenchida
    ] if "id_servico_definicao" in srv_m.columns else pd.DataFrame()

    if not srv_correcoes.empty:
        srv_correcoes["_mes"] = pd.to_datetime(srv_correcoes["dt_fim_execucao"]).dt.to_period("M").dt.to_timestamp()
        ordens_executadas = srv_correcoes.groupby("_mes").agg(
            Ordens_Executadas=("qt_servico","sum")
        ).reset_index()
        ordens_executadas.columns = ["Mês", "Ordens_Executadas"]
    else:
        ordens_executadas = pd.DataFrame(columns=["Mês", "Ordens_Executadas"])

    # Passo 3: Mesclar dados
    ag_ef = total_leituras.merge(ordens_executadas, on="Mês", how="left")
    ag_ef["Ordens_Executadas"] = ag_ef["Ordens_Executadas"].fillna(0)

    # Passo 4: Calcular Eficiência = (Total Leituras - Ordens Corrigidas) / Total Leituras
    ag_ef["Eficiência"] = (ag_ef["Total_Leituras"] - ag_ef["Ordens_Executadas"]) / ag_ef["Total_Leituras"]

    # Criar gráfico com duas linhas
    fig3 = go.Figure()
    # Formatação com 2 casas decimais para mostrar valores exatos
    text_eficiencia = [f"{val:.2%}" for val in ag_ef["Eficiência"]]
    fig3.add_trace(go.Scatter(x=ag_ef["Mês"], y=ag_ef["Eficiência"], mode="lines+markers+text",
                               name="Eficiência de Leitura", line=dict(color=COR["verde"], width=3),
                               marker=dict(size=8), text=text_eficiencia, textposition="top center",
                               textfont=dict(size=13, color=COR["verde"], family="Arial Black"),
                               yaxis="y1"))
    fig3.add_trace(go.Scatter(x=ag_ef["Mês"], y=ag_ef["Ordens_Executadas"], mode="lines+markers",
                               name="Ordens de Correção Executadas", line=dict(color=COR["amarelo"], width=3, dash="dash"),
                               marker=dict(size=6), yaxis="y2"))
    fig3.add_hline(y=0.95, line_dash="dash", line_color=COR["vermelho"],
                   annotation_text="Meta 95%", yref="y1")
    fig3.update_layout(
        title="Eficiência de Leitura (sem erros)",
        margin=dict(t=35, b=0, l=0, r=20), xaxis_title="",
        yaxis=dict(title="Eficiência (%)", tickformat=".1%"),
        yaxis2=dict(title="Qtd Alterações Executadas", overlaying="y", side="right", range=[-50, 50]),
        hovermode="x unified",
        legend=dict(x=0.5, y=1.15, orientation="h", xanchor="center", yanchor="top"),
    )
    st.plotly_chart(fig3, use_container_width=True)

    # Por bairro — perdas por alteração de fatura (cancelamento/reemissão)
    alt_fat_filtered = filtrar(D["alt_fat"], "dt_ref", d0, d1)
    if not alt_fat_filtered.empty and "ch_rsf_bairro_dim" in alt_fat_filtered.columns:
        # Merge com tabela de bairro para ter o nome
        alt_fat_filtered = alt_fat_filtered.merge(
            D["d_bairro"][["id_bairro", "nm_bairro_dim"]],
            left_on="ch_rsf_bairro_dim",
            right_on="id_bairro",
            how="left"
        )

        # Agrupar por bairro e somar abatimentos (perdas em R$)
        perdas_bairro = alt_fat_filtered.groupby("nm_bairro_dim").agg(
            Perda_Valor=("vl_abatimento", lambda x: abs(x.sum())),  # Converter para positivo
            Qtd_Alteracoes=("id_localizacao_dim", "count")
        ).reset_index().sort_values("Perda_Valor", ascending=True).tail(12)

        if not perdas_bairro.empty and perdas_bairro["Perda_Valor"].sum() > 0:
            fig4 = px.bar(perdas_bairro, x="Perda_Valor", y="nm_bairro_dim", orientation="h",
                          title="Perdas por Bairro - Abatimentos em Alterações de Fatura (R$)",
                          color="Perda_Valor",
                          color_continuous_scale=["#27AE60","#F39C12","#E74C3C"],
                          hover_data={"Qtd_Alteracoes": True})
            # Adicionar valores dentro das barras
            fig4.update_traces(
                text=[f"R$ {val:,.2f}" for val in perdas_bairro["Perda_Valor"]],
                textposition="inside",
                textfont=dict(size=13, color="white", family="Arial Black")
            )
            fig4.update_layout(margin=dict(t=35, b=0, l=0, r=20),
                               xaxis_title="R$", yaxis_title="",
                               coloraxis_showscale=False)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Sem perdas detectadas no período selecionado")


# ── Frota Combustível ─────────────────────────────────────────────────────────
def pg_frota_combustivel(D, d0, d1):
    page_header("Frota Combustível",
                f"{d0.strftime('%d/%m/%Y')} a {d1.strftime('%d/%m/%Y')}")

    frota = D["frota"].copy()

    if frota.empty:
        st.warning("Sem dados de frota.")
        return

    # Filtra por período
    frota_f = frota[(frota["Data"] >= d0) & (frota["Data"] < d1 + pd.Timedelta(days=1))]

    if frota_f.empty:
        st.warning("Sem dados no período selecionado.")
        return

    # KPIs (cartões)
    vl_consumo_total = frota_f["Quantidade"].sum()
    vl_gasto_total = frota_f["Valor_Total"].sum()
    vl_km_total = frota_f["Km_Rodados"].sum()
    eff_media = vl_km_total / vl_consumo_total if vl_consumo_total > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Combustível Consumido", vl_consumo_total, prefixo="")
    kpi(c2, "Custo Total", vl_gasto_total, prefixo="R$")
    kpi(c3, "Km Rodados", vl_km_total, prefixo="")
    kpi(c4, "Eficiência Média", eff_media, prefixo="")

    # ── Bloco comparativo ─────────────────────────────────────────────────────
    _comp = _comp_periodo()
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _fr_c   = frota[(frota["Data"] >= _cd0) & (frota["Data"] < _cd1 + pd.Timedelta(days=1))]
        _cons_c = _fr_c["Quantidade"].sum()   if not _fr_c.empty else 0
        _gast_c = _fr_c["Valor_Total"].sum()  if not _fr_c.empty else 0
        _km_c   = _fr_c["Km_Rodados"].sum()   if not _fr_c.empty else 0
        _eff_c  = _km_c / _cons_c             if _cons_c else 0
        _brl    = lambda v: f"R$ {v:,.0f}".replace(",","X").replace(".",",").replace("X",".")
        render_comp_bloco(_comp["label_atual"], _comp["label_comp"], [
            ("Combustível Consumido (L)", vl_consumo_total, _cons_c, lambda v: f"{v:,.0f} L", None),
            ("Custo Total",              vl_gasto_total,   _gast_c, _brl,                    None),
            ("Km Rodados",               vl_km_total,      _km_c,   lambda v: f"{v:,.0f} km", True),
            ("Eficiência Média (km/L)",  eff_media,        _eff_c,  lambda v: f"{v:.2f}",     True),
        ])

    st.markdown("---")

    # Gráfico 1: Consumo por Motorista (top 8)
    frota_motorista = frota_f.groupby("Motorista").agg({
        "Quantidade": "sum",
        "Valor_Total": "sum",
        "Km_Rodados": "sum"
    }).reset_index()
    frota_motorista = frota_motorista.nlargest(8, "Valor_Total")
    frota_motorista = frota_motorista.sort_values("Valor_Total", ascending=True)

    fig_motorista = go.Figure(data=[
        go.Bar(
            y=frota_motorista["Motorista"],
            x=frota_motorista["Quantidade"],
            orientation="h",
            text=[f"{v:.0f} L" for v in frota_motorista["Quantidade"].values],
            textposition="outside",
            marker_color=COR["azul"],
            showlegend=False
        )
    ])
    fig_motorista.update_layout(
        title="Consumo de Combustível por Motorista (Top 8)",
        xaxis_title="Litros",
        yaxis_title="",
        margin=dict(t=50, b=0, l=250, r=30),
        height=400
    )
    st.plotly_chart(fig_motorista, use_container_width=True)

    st.markdown("---")

    # Gráfico 2: Consumo por Veículo (top 8)
    frota_veiculo = frota_f.groupby("Veiculo").agg({
        "Quantidade": "sum",
        "Valor_Total": "sum",
        "Km_Rodados": "sum"
    }).reset_index()
    frota_veiculo = frota_veiculo.nlargest(8, "Valor_Total")
    frota_veiculo = frota_veiculo.sort_values("Valor_Total", ascending=True)

    fig_veiculo = go.Figure(data=[
        go.Bar(
            y=frota_veiculo["Veiculo"],
            x=frota_veiculo["Quantidade"],
            orientation="h",
            text=[f"{v:.0f} L" for v in frota_veiculo["Quantidade"].values],
            textposition="outside",
            marker_color=COR["azul"],
            showlegend=False
        )
    ])
    fig_veiculo.update_layout(
        title="Consumo de Combustível por Veículo (Top 8)",
        xaxis_title="Litros",
        yaxis_title="",
        margin=dict(t=50, b=0, l=150, r=30),
        height=400
    )
    st.plotly_chart(fig_veiculo, use_container_width=True)

    st.markdown("---")

    # Gráfico 3: Evolução Temporal
    frota_diaria = frota_f.groupby("Data").agg({"Quantidade":"sum","Valor_Total":"sum","Km_Rodados":"sum"}).reset_index().sort_values("Data")
    _comp = _comp_periodo()
    fig_temporal = go.Figure()
    fig_temporal.add_trace(go.Scatter(
        x=frota_diaria["Data"], y=frota_diaria["Quantidade"],
        name=f"Litros {_comp['label_atual'] if _comp else 'Atual'}",
        mode="lines+markers", line=dict(color=COR["azul"], width=2), marker=dict(size=5)
    ))
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _fr_cg = frota[(_comp["comp_d0"] <= frota["Data"]) & (frota["Data"] < _comp["comp_d1"] + pd.Timedelta(days=1))]
        if not _fr_cg.empty:
            _fd_c = _fr_cg.groupby("Data").agg({"Quantidade":"sum"}).reset_index().sort_values("Data")
            fig_temporal.add_trace(go.Scatter(
                x=_fd_c["Data"], y=_fd_c["Quantidade"],
                name=f"Litros {_comp['label_comp']}",
                mode="lines+markers", line=dict(color=COR["vermelho"], width=2, dash="dot"),
                marker=dict(size=5, symbol="circle-open"), opacity=0.7
            ))
    fig_temporal.update_layout(
        title="Consumo de Combustível (Evolução)" + (f" — {_comp['label_atual']} vs {_comp['label_comp']}" if _comp else ""),
        margin=dict(t=50, b=0, l=0, r=30), height=350, hovermode="x unified",
        legend=dict(orientation="h", y=1.1)
    )
    fig_temporal.update_yaxes(tickformat=".0f")
    st.plotly_chart(fig_temporal, use_container_width=True)

    st.markdown("---")

    # Gráfico 4: Custo por Km
    frota_scatter = frota_f[frota_f["Km_Rodados"] > 0].copy()

    fig_scatter = px.scatter(
        frota_scatter,
        x="Km_Rodados",
        y="Custo_Por_Km",
        hover_data={"Motorista": True, "Veiculo": True, "Data": True},
        title="Custo por Km (por Transação)",
        labels={"Km_Rodados": "Km Rodados", "Custo_Por_Km": "R$/km"},
        color_discrete_sequence=[COR["azul"]]
    )
    fig_scatter.update_layout(margin=dict(t=50, b=0, l=0, r=30), height=350)
    fig_scatter.update_xaxes(tickformat=".0f")
    fig_scatter.update_yaxes(tickformat="$,.2f")
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("---")

    # Tabela de detalhes
    st.markdown("#### Tabela Detalhada")
    tbl = frota_f[[
        "Data", "Motorista", "Veiculo", "Quantidade",
        "Valor_Total", "Km_Rodados", "Km_Por_Litro",
        "Custo_Por_Km", "Cidade", "Estabelecimento"
    ]].copy()
    tbl = tbl.sort_values("Data", ascending=False)

    tbl_view = tbl.copy()
    tbl_view["Data"] = tbl_view["Data"].dt.strftime("%d/%m/%Y")
    tbl_view.columns = [
        "Data", "Motorista", "Veículo", "Litros",
        "Valor (R$)", "Km", "Eficiência (km/L)",
        "Custo/Km (R$)", "Cidade", "Estabelecimento"
    ]

    # Formatação de valores
    tbl_view["Valor (R$)"] = tbl_view["Valor (R$)"].apply(lambda x: f"R$ {x:,.2f}")
    tbl_view["Custo/Km (R$)"] = tbl_view["Custo/Km (R$)"].apply(lambda x: f"R$ {x:.2f}")
    tbl_view["Litros"] = tbl_view["Litros"].apply(lambda x: f"{x:.2f}")
    tbl_view["Km"] = tbl_view["Km"].apply(lambda x: f"{x:.0f}")
    tbl_view["Eficiência (km/L)"] = tbl_view["Eficiência (km/L)"].apply(lambda x: f"{x:.2f}")

    st.dataframe(tbl_view, use_container_width=True, hide_index=True, height=500)

    # Resumo final
    st.markdown("---")
    st.markdown("#### Resumo")
    col1, col2, col3 = st.columns(3)
    kpi(col1, "Total Transações", len(frota_f), prefixo="")
    kpi(col2, "Custo Médio/Transação", frota_f['Valor_Total'].mean(), prefixo="R$")
    kpi(col3, "Litros Médio/Transação", frota_f['Quantidade'].mean(), prefixo="")


# ── Energia ───────────────────────────────────────────────────────────────────
def pg_energia(D, d0, d1):
    page_header("Energia Elétrica",
                f"{d0.strftime('%d/%m/%Y')} a {d1.strftime('%d/%m/%Y')}")

    ene = D["ene"].copy()
    d_uc = D["d_uc_ene"].copy()

    if ene.empty:
        st.warning("Sem dados de energia.")
        return

    # Filtra por período
    ene_f = ene[(ene["mes_ano"] >= d0) & (ene["mes_ano"] < d1 + pd.Timedelta(days=1))]

    if ene_f.empty:
        st.warning("Sem dados no período selecionado.")
        return

    # KPIs (cartões)
    vl_total = ene_f["valor_r"].sum()
    vl_media = ene_f["valor_r"].mean()
    vl_agua_total = D["fat"][
        (D["fat"]["dt_ref"] >= d0) & (D["fat"]["dt_ref"] < d1 + pd.Timedelta(days=1))
    ]["vl_total_faturado"].sum() if not D["fat"].empty else 0
    pct_fat = (vl_total / vl_agua_total * 100) if vl_agua_total > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Custo Total Energia", vl_total, prefixo="R$")
    kpi(c2, "Custo Médio Mensal", vl_media, prefixo="R$")
    kpi(c3, "% do Faturamento", pct_fat, prefixo="%")
    kpi(c4, "UCs Ativas", len(d_uc) if not d_uc.empty else 0, prefixo="")

    # ── Bloco comparativo ─────────────────────────────────────────────────────
    _comp = _comp_periodo()
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _ene_c  = ene[(ene["mes_ano"] >= _cd0) & (ene["mes_ano"] < _cd1 + pd.Timedelta(days=1))]
        _fat_c  = filtrar(D["fat"], "dt_ref", _cd0, _cd1)
        _vt_c   = _ene_c["valor_r"].sum()  if not _ene_c.empty else 0
        _vm_c   = _ene_c["valor_r"].mean() if not _ene_c.empty else 0
        _vf_c   = _fat_c["vl_total_faturado"].sum() if not _fat_c.empty else 0
        _pf_c   = (_vt_c / _vf_c * 100) if _vf_c else 0
        _brl    = lambda v: f"R$ {v:,.0f}".replace(",","X").replace(".",",").replace("X",".")
        render_comp_bloco(_comp["label_atual"], _comp["label_comp"], [
            ("Custo Total Energia",  vl_total, _vt_c, _brl,                  False),
            ("Custo Médio Mensal",   vl_media, _vm_c, _brl,                  False),
            ("% do Faturamento",     pct_fat,  _pf_c, lambda v: f"{v:.1f}%", False),
        ])

    st.markdown("---")

    # Gráfico: por UC (largura total)
    ene_uc = ene_f.groupby("uc")["valor_r"].sum().sort_values(ascending=True)
    fig_uc = px.bar(
        y=ene_uc.index, x=ene_uc.values,
        orientation="h",
        title="Custo por Unidade de Consumo",
        labels={"x": "R$", "y": ""},
        color_discrete_sequence=[COR["azul"]]
    )
    fig_uc.update_layout(margin=dict(t=50, b=0, l=200, r=30), height=500, showlegend=False)
    fig_uc.update_traces(text=[f"R$ {v:,.0f}" for v in ene_uc.values], textposition="outside")
    st.plotly_chart(fig_uc, use_container_width=True)

    st.markdown("---")

    # Série temporal
    ene_ts = ene_f.groupby("mes_ano")["valor_r"].sum().reset_index()
    ene_ts = ene_ts.sort_values("mes_ano")
    _comp = _comp_periodo()
    fig_ts = go.Figure()
    fig_ts.add_trace(go.Scatter(
        x=ene_ts["mes_ano"], y=ene_ts["valor_r"],
        name=f"Energia {_comp['label_atual'] if _comp else 'Atual'}",
        mode="lines+markers", line=dict(color=COR["azul"], width=2), marker=dict(size=6)
    ))
    if _comp:
        _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
        _ene_c = ene[(_comp["comp_d0"] <= ene["mes_ano"]) & (ene["mes_ano"] < _comp["comp_d1"] + pd.Timedelta(days=1))]
        if not _ene_c.empty:
            _ene_ts_c = _ene_c.groupby("mes_ano")["valor_r"].sum().reset_index().sort_values("mes_ano")
            fig_ts.add_trace(go.Scatter(
                x=_ene_ts_c["mes_ano"], y=_ene_ts_c["valor_r"],
                name=f"Energia {_comp['label_comp']}",
                mode="lines+markers", line=dict(color=COR["vermelho"], width=2, dash="dot"),
                marker=dict(size=6, symbol="circle-open"), opacity=0.7
            ))
    fig_ts.update_layout(
        title="Evolução do Custo de Energia" + (f" — {_comp['label_atual']} vs {_comp['label_comp']}" if _comp else ""),
        margin=dict(t=50, b=0, l=0, r=30), height=400, hovermode="x unified",
        legend=dict(orientation="h", y=1.1)
    )
    fig_ts.update_yaxes(tickformat="$,.0f")
    st.plotly_chart(fig_ts, use_container_width=True)

    st.markdown("---")

    # Tabela de detalhes
    st.markdown("#### Tabela de Energia por Período")
    cols_avail = ["uc", "mes_ano", "valor_r"]
    if "tipo_contrato" in ene_f.columns:
        cols_avail.append("tipo_contrato")
    if "fornecedor" in ene_f.columns:
        cols_avail.append("fornecedor")

    tbl = ene_f[cols_avail].copy()
    tbl = tbl.sort_values("mes_ano")
    tbl["mes_ano_str"] = tbl["mes_ano"].dt.strftime("%m/%Y")

    tbl_cols = ["uc", "mes_ano_str", "valor_r"]
    if "tipo_contrato" in cols_avail:
        tbl_cols.insert(3, "tipo_contrato")
    if "fornecedor" in cols_avail:
        tbl_cols.append("fornecedor")

    tbl_view = tbl[tbl_cols].copy()
    col_names = ["UC", "Período", "Valor (R$)"]
    if "tipo_contrato" in cols_avail:
        col_names.insert(3, "Tipo Contrato")
    if "fornecedor" in cols_avail:
        col_names.append("Fornecedor")
    tbl_view.columns = col_names

    # Total por período
    total_per = tbl_view.groupby("Período")["Valor (R$)"].sum().reset_index()
    total_row = pd.DataFrame([{
        "UC": "TOTAL", "Período": "", "Valor (R$)": tbl_view["Valor (R$)"].sum(),
        "Tipo Contrato": "", "Fornecedor": ""
    }])
    tbl_view = pd.concat([tbl_view, total_row], ignore_index=True)

    st.dataframe(
        tbl_view.style
        .format({"Valor (R$)": lambda v: f"R$ {v:>10,.2f}" if isinstance(v, float) else v})
        .apply(lambda row: ["font-weight:bold; background:#E8F4FD"]*len(row)
               if row["UC"]=="TOTAL" else [""]*len(row), axis=1),
        use_container_width=True,
        height=400,
    )

    # Dimensão UCs
    if not d_uc.empty:
        st.markdown("---")
        st.markdown("#### Unidades de Consumo")
        d_uc_view = d_uc.copy()
        d_uc_view.columns = ["UC", "Localização", "Tipo Contrato", "Fornecedor", "Status"]
        st.dataframe(d_uc_view, use_container_width=True)

    # Análise de Desconto (Matrix e EchoEnergia)
    desc_ene = D.get("desc_ene", pd.DataFrame())
    if not desc_ene.empty:
        desc_f = desc_ene[(desc_ene["mes_ano"] >= f"{d0.month:02d}/{d0.year}") &
                          (desc_ene["mes_ano"] <= f"{d1.month:02d}/{d1.year}")]

        st.markdown("---")
        st.markdown("## Análise de Descontos Contratuais")
        st.markdown("**Fornecedores:** Matrix e EchoEnergia")

        if not desc_f.empty:
            col1, col2, col3 = st.columns(3)

            # KPIs de desconto
            desc_total = desc_f["desconto_r"].sum()
            desc_media_pct = desc_f["desconto_pct"].mean()
            valor_economizado = desc_f["desconto_r"].sum()

            with col1:
                kpi(col1, "Desconto Total (R$)", desc_total, prefixo="R$")
            with col2:
                kpi(col2, "Desconto Médio (%)", desc_media_pct, prefixo="%")
            with col3:
                kpi(col3, "Economia Gerada", valor_economizado, prefixo="R$")

            st.markdown("")

            # Gráfico de desconto por fornecedor
            desc_fornecedor = desc_f.groupby("fornecedor")[["desconto_r", "desconto_pct"]].agg({"desconto_r": "sum", "desconto_pct": "mean"}).reset_index()
            fig_desc = px.bar(desc_fornecedor, x="fornecedor", y="desconto_r",
                             title="Desconto Total por Fornecedor",
                             labels={"fornecedor": "Fornecedor", "desconto_r": "Desconto (R$)"},
                             color="fornecedor",
                             color_discrete_map={"Matrix": COR["azul"], "EchoEnergia": COR["verde"]})
            fig_desc.update_layout(margin=dict(t=50, b=0, l=0, r=20), height=350, showlegend=False)
            fig_desc.update_traces(text=[f"R$ {v:,.0f}" for v in desc_fornecedor["desconto_r"]], textposition="outside")
            st.plotly_chart(fig_desc, use_container_width=True)

            # Tabela detalhada
            st.markdown("#### Descontos por Período e UC")
            desc_table = desc_f[["uc", "mes_ano", "valor_pago", "valor_cheio", "desconto_r", "desconto_pct", "fornecedor"]].copy()
            desc_table.columns = ["UC", "Período", "Valor Pago", "Valor Cheio", "Desconto (R$)", "Desconto (%)", "Fornecedor"]
            desc_table = desc_table.sort_values("Período", ascending=False)

            st.dataframe(
                desc_table.style
                .format({"Valor Pago": "R$ {:,.2f}", "Valor Cheio": "R$ {:,.2f}",
                        "Desconto (R$)": "R$ {:,.2f}", "Desconto (%)": "{:.2f}%"}),
                use_container_width=True,
                height=400
            )
        else:
            st.info("Sem dados de desconto no período selecionado.")


# ══════════════════════════════════════════════════════════════════════════════
# COCKPIT — SETORES OPERACIONAIS
# ══════════════════════════════════════════════════════════════════════════════

# Setores com ação direta externa
_SETORES_OP = ["Corte", "Religação", "Operacional", "Fiscalização", "Hidrometria", "Repavimentação"]

def _render_setor_bloco(srv_bloco, setor_nome, cor_barra, _key_prefix=""):
    """Renderiza os dois gráficos de cada setor: SLA prazo e serviços por equipe."""
    df = srv_bloco[srv_bloco["nm_setor_operacional"] == setor_nome].copy() if setor_nome != "_TODOS" else srv_bloco.copy()
    # Considera apenas serviços executados (id_situacao_servico == 3)
    if "id_situacao_servico" in df.columns:
        df = df[df["id_situacao_servico"] == 3]
    if df.empty:
        st.info(f"Sem dados para {setor_nome} no período.")
        return

    qtd   = int(df["qt_servico"].sum())
    fpr   = int(df[df["fl_fora_prazo"] == True]["qt_servico"].sum()) if "fl_fora_prazo" in df.columns else 0
    np_   = qtd - fpr
    sla   = np_ / qtd * 100 if qtd else 0

    col1, col2 = st.columns(2)

    # ── Gráfico A — No Prazo vs Fora do Prazo ──────────────────────────────
    fig_sla = go.Figure()
    fig_sla.add_trace(go.Bar(
        x=["No Prazo", "Fora do Prazo"], y=[np_, fpr],
        marker_color=[COR["verde"], COR["vermelho"]],
        text=[f"<b>{np_:,}</b>".replace(",","."), f"<b>{fpr:,}</b>".replace(",",".")],
        textposition="inside", textangle=-90,
        textfont=dict(size=14, color="white", family="Arial Black"),
        insidetextanchor="middle",
        width=0.5,
    ))
    fig_sla.add_annotation(
        xref="paper", yref="paper", x=0.5, y=1.08,
        text=f"<b>SLA: {sla:.1f}%</b> {'✅' if sla >= 90 else '⚠️' if sla >= 75 else '❌'}",
        showarrow=False, font=dict(size=14, color="#1A5276"), xanchor="center",
    )
    fig_sla.update_layout(
        title="Atendimento — No Prazo vs Fora",
        margin=dict(t=55, b=10, l=0, r=10), height=300,
        xaxis=dict(title=""), yaxis=dict(title="Qtd", tickformat=",.0f"),
        showlegend=False,
    )
    _slug = setor_nome.replace(" ", "_").replace("/", "_")
    col1.plotly_chart(fig_sla, use_container_width=True,
                      key=f"{_key_prefix}sla_{_slug}")

    # ── Gráfico B — Serviços por equipe ────────────────────────────────────
    if "nm_equipe" in df.columns:
        ag_eq = df.groupby("nm_equipe")["qt_servico"].sum().sort_values(ascending=True).reset_index()
        ag_eq.columns = ["Equipe", "Qtd"]
        ne = len(ag_eq)
        cores_e = [f"rgb({int(44+i*(26-44)/(max(ne-1,1)))},{int(130+i*(82-130)/(max(ne-1,1)))},{int(201+i*(118-201)/(max(ne-1,1)))})" for i in range(ne)]
        fig_eq = go.Figure(go.Bar(
            x=ag_eq["Qtd"], y=ag_eq["Equipe"], orientation="h",
            marker_color=cores_e[::-1],
            text=ag_eq["Qtd"].apply(lambda v: f"<b>{int(v):,}</b>".replace(",",".")),
            textposition="inside", textfont=dict(size=12, color="white", family="Arial Black"),
            insidetextanchor="end",
        ))
        fig_eq.update_layout(
            title="Serviços por Equipe",
            margin=dict(t=40, b=0, l=0, r=10), height=max(260, ne*36),
            xaxis=dict(title=""), yaxis=dict(title=""),
            uniformtext_minsize=8, uniformtext_mode="hide",
        )
        col2.plotly_chart(fig_eq, use_container_width=True,
                          key=f"{_key_prefix}eq_{_slug}")


def pg_setores(D, d0, d1, _sub=False):
    if not _sub:
        page_header("Setores Operacionais",
                    f"{d0.strftime('%d/%m/%Y')} a {d1.strftime('%d/%m/%Y')}")

    srv = filtrar(D["srv"], "dt_solicitacao", d0, d1)
    if srv.empty:
        st.warning("Sem dados de serviços no período.")
        return

    srv = merge_equipe(srv, D)
    srv = merge_setor(srv, D)
    srv = srv.dropna(subset=["nm_setor_operacional"])

    # Classifica setores
    srv["_bloco"] = srv["nm_setor_operacional"].apply(
        lambda s: "Operacional" if s in _SETORES_OP else "Interno"
    )

    srv_op  = srv[srv["_bloco"] == "Operacional"]
    srv_int = srv[srv["_bloco"] == "Interno"]

    # Para KPIs: filtra apenas executados (situação 3)
    _exec = lambda df: df[df["id_situacao_servico"] == 3] if "id_situacao_servico" in df.columns else df

    # ════════════════════════════════════════════════════════════════════════
    # BLOCO 1 — SERVIÇOS OPERACIONAIS
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div style='background:linear-gradient(90deg,#1A5276,#2E86C1);border-radius:10px;
    padding:12px 20px;margin-bottom:16px'>
    <span style='color:white;font-size:18px;font-weight:700'>⚙️ Serviços Operacionais</span>
    <span style='color:#AED6F1;font-size:13px;margin-left:12px'>Ações diretas externas</span>
    </div>""", unsafe_allow_html=True)

    # KPIs bloco operacional (apenas executados)
    srv_op_ex = _exec(srv_op)
    if not srv_op_ex.empty:
        qtd_op  = int(srv_op_ex["qt_servico"].sum())
        fpr_op  = int(srv_op_ex[srv_op_ex["fl_fora_prazo"] == True]["qt_servico"].sum()) if "fl_fora_prazo" in srv_op_ex.columns else 0
        sla_op  = (qtd_op - fpr_op) / qtd_op if qtd_op else 0
        tmed_op = srv_op_ex["qt_tempo_execucao"].mean() / 60 if "qt_tempo_execucao" in srv_op_ex.columns else 0
        c1, c2, c3 = st.columns(3)
        kpi(c1, "Total Operacional",    qtd_op,  prefixo="")
        kpi(c2, "% SLA no Prazo",       sla_op,  prefixo="%")
        kpi(c3, "Tempo Médio Exec. (h)", tmed_op, prefixo="")

    # Tabs por setor operacional
    setores_presentes = [s for s in _SETORES_OP if s in srv_op.get("nm_setor_operacional", pd.Series()).unique()]
    if setores_presentes:
        tabs = st.tabs([f"📂 {s}" for s in setores_presentes])
        for tab, setor in zip(tabs, setores_presentes):
            with tab:
                _render_setor_bloco(srv_op, setor, COR["azul"], _key_prefix="op_")

    st.markdown("---")

    # ════════════════════════════════════════════════════════════════════════
    # BLOCO 2 — SERVIÇOS INTERNOS
    # ════════════════════════════════════════════════════════════════════════
    st.markdown("""
    <div style='background:linear-gradient(90deg,#5D6D7E,#808B96);border-radius:10px;
    padding:12px 20px;margin-bottom:16px'>
    <span style='color:white;font-size:18px;font-weight:700'>🏢 Serviços Internos</span>
    <span style='color:#D5D8DC;font-size:13px;margin-left:12px'>Sem ação direta externa</span>
    </div>""", unsafe_allow_html=True)

    srv_int_ex = _exec(srv_int)
    if not srv_int_ex.empty:
        qtd_int  = int(srv_int_ex["qt_servico"].sum())
        fpr_int  = int(srv_int_ex[srv_int_ex["fl_fora_prazo"] == True]["qt_servico"].sum()) if "fl_fora_prazo" in srv_int_ex.columns else 0
        sla_int  = (qtd_int - fpr_int) / qtd_int if qtd_int else 0
        tmed_int = srv_int_ex["qt_tempo_execucao"].mean() / 60 if "qt_tempo_execucao" in srv_int_ex.columns else 0
        c1, c2, c3 = st.columns(3)
        kpi(c1, "Total Interno",         qtd_int,  prefixo="")
        kpi(c2, "% SLA no Prazo",        sla_int,  prefixo="%")
        kpi(c3, "Tempo Médio Exec. (h)", tmed_int, prefixo="")

        # Renomeia setores internos para exibir no tab
        setores_int = sorted(srv_int["nm_setor_operacional"].unique().tolist())
        tabs_int = st.tabs([f"📋 {s}" for s in setores_int])
        for tab, setor in zip(tabs_int, setores_int):
            with tab:
                _render_setor_bloco(srv_int, setor, COR["cinza"], _key_prefix="int_")


# ══════════════════════════════════════════════════════════════════════════════
# COCKPIT — TRATAMENTO
# ══════════════════════════════════════════════════════════════════════════════
def pg_tratamento(D, d0, d1):
    page_header("Tratamento",
                f"{d0.strftime('%d/%m/%Y')} a {d1.strftime('%d/%m/%Y')}")

    prod = D["prod_agua"].copy()
    qual = D["qual_agua"].copy()

    # ── Tabs principais ────────────────────────────────────────────────────────
    tab_prod, tab_qual = st.tabs(["💧 Produção de Água", "🔬 Qualidade da Água"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — PRODUÇÃO
    # ══════════════════════════════════════════════════════════════════════════
    with tab_prod:
        if prod.empty:
            st.warning("Sem dados de produção. Execute scripts/etl_tratamento.py.")
            return

        prod["data"] = pd.to_datetime(prod["data"])

        # Filtra pelo período selecionado
        prod_f = prod[(prod["data"] >= d0) & (prod["data"] <= d1)]

        if prod_f.empty:
            st.info("Sem dados de produção no período. Exibindo histórico completo.")
            prod_f = prod.copy()

        # ── KPIs ──────────────────────────────────────────────────────────────
        vol_ip  = prod_f["vol_ipameri"].sum()
        vol_dom = prod_f["vol_domiciano"].sum()
        vol_tot = prod_f["vol_total"].sum()
        pct_dom = (vol_dom / vol_tot * 100) if vol_tot > 0 else 0

        c1, c2, c3, c4 = st.columns(4)
        kpi(c1, "Volume Ipameri (m³)",   vol_ip,  prefixo="")
        kpi(c2, "Volume Domiciano (m³)", vol_dom, prefixo="")
        kpi(c3, "Volume Total (m³)",     vol_tot, prefixo="")
        kpi(c4, "% Domiciano",           pct_dom, prefixo="%")

        # Comparativo
        _comp = _comp_periodo()
        if _comp:
            _cd0, _cd1 = _comp["comp_d0"], _comp["comp_d1"]
            prod_c = prod[(prod["data"] >= _cd0) & (prod["data"] <= _cd1)]
            _ip_c  = prod_c["vol_ipameri"].sum()
            _dom_c = prod_c["vol_domiciano"].sum()
            _tot_c = prod_c["vol_total"].sum()
            _brl   = lambda v: f"{v:,.0f} m³"
            render_comp_bloco(_comp["label_atual"], _comp["label_comp"], [
                ("Volume Ipameri",   vol_ip,  _ip_c,  _brl, True),
                ("Volume Domiciano", vol_dom, _dom_c, _brl, True),
                ("Volume Total",     vol_tot, _tot_c, _brl, True),
            ])

        st.markdown("---")

        # ── Gráfico 1 — Volume histórico por sistema ───────────────────────────
        prod_hist = prod.copy()
        prod_hist["Mes"] = prod_hist["data"].dt.strftime("%m/%Y")

        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=prod_hist["data"], y=prod_hist["vol_ipameri"],
            name="Ipameri", mode="lines+markers",
            line=dict(color=COR["azul"], width=2),
            fill="tozeroy", fillcolor="rgba(26,111,173,0.12)",
        ))
        fig1.add_trace(go.Scatter(
            x=prod_hist["data"], y=prod_hist["vol_domiciano"],
            name="Domiciano Ribeiro", mode="lines+markers",
            line=dict(color=COR["verde"], width=2),
            fill="tozeroy", fillcolor="rgba(39,174,96,0.12)",
        ))
        fig1.add_trace(go.Scatter(
            x=prod_hist["data"], y=prod_hist["vol_total"],
            name="Total", mode="lines",
            line=dict(color="#7C3AED", width=2, dash="dot"),
        ))
        # Destaca período selecionado
        fig1.add_vrect(x0=d0, x1=d1, fillcolor="rgba(26,111,173,0.07)",
                       line_width=0, annotation_text="Período", annotation_position="top left")
        fig1.update_layout(
            title="Volume Produzido Mensal (m³) — Histórico",
            margin=dict(t=40, b=0, l=0, r=20), height=350,
            legend=dict(orientation="h", y=1.12),
        )
        fig1.update_yaxes(tickformat=",.0f")
        st.plotly_chart(fig1, use_container_width=True)

        # ── Gráfico 2 — Composição % Ipameri vs Domiciano (barras empilhadas) ──
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=prod_hist["data"], y=prod_hist["vol_ipameri"],
            name="Ipameri", marker_color=COR["azul"],
        ))
        fig2.add_trace(go.Bar(
            x=prod_hist["data"], y=prod_hist["vol_domiciano"],
            name="Domiciano Ribeiro", marker_color=COR["verde"],
        ))
        fig2.update_layout(
            title="Composição do Volume Total (m³)",
            barmode="stack", margin=dict(t=40, b=0, l=0, r=20), height=320,
            legend=dict(orientation="h", y=1.12),
        )
        fig2.update_yaxes(tickformat=",.0f")
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")
        st.markdown("#### Gasto de Insumos (kg/mês)")

        # ── Gráfico 3 — Insumos ────────────────────────────────────────────────
        insumos_hist = prod[prod[["cal_kg","cloro_kg","fluor_kg","pac_kg","naclo_kg"]].notna().any(axis=1)].copy()
        insumos_hist["data"] = pd.to_datetime(insumos_hist["data"])

        insumos_map = {
            "cal_kg":   ("CAL",   "#F59E0B"),
            "cloro_kg": ("Cloro", "#3B82F6"),
            "fluor_kg": ("Flúor", "#10B981"),
            "pac_kg":   ("PAC",   "#8B5CF6"),
            "naclo_kg": ("NaClO", "#EF4444"),
        }

        fig3 = go.Figure()
        for col, (label, cor_) in insumos_map.items():
            if col in insumos_hist.columns:
                vals = insumos_hist[col].fillna(0)
                if vals.sum() > 0:
                    fig3.add_trace(go.Bar(
                        x=insumos_hist["data"], y=vals,
                        name=label, marker_color=cor_,
                    ))

        # Período filtrado
        insumos_f = insumos_hist[(insumos_hist["data"] >= d0) & (insumos_hist["data"] <= d1)]
        fig3.add_vrect(x0=d0, x1=d1, fillcolor="rgba(26,111,173,0.07)",
                       line_width=0, annotation_text="Período", annotation_position="top left")
        fig3.update_layout(
            title="Insumos de Tratamento — Histórico Mensal (kg)",
            barmode="stack", margin=dict(t=40, b=0, l=0, r=20), height=340,
            legend=dict(orientation="h", y=1.12),
        )
        fig3.update_yaxes(tickformat=",.0f")
        st.plotly_chart(fig3, use_container_width=True)

        # KPIs insumos do período
        if not insumos_f.empty:
            c1, c2, c3, c4, c5 = st.columns(5)
            kpi(c1, "CAL (kg)",   insumos_f["cal_kg"].sum(),   prefixo="")
            kpi(c2, "Cloro (kg)", insumos_f["cloro_kg"].sum(), prefixo="")
            kpi(c3, "Flúor (kg)", insumos_f["fluor_kg"].sum(), prefixo="")
            kpi(c4, "PAC (kg)",   insumos_f["pac_kg"].sum(),   prefixo="")
            kpi(c5, "NaClO (kg)", insumos_f["naclo_kg"].sum(), prefixo="")

        # Tabela resumo
        st.markdown("#### Tabela de Produção Mensal")
        tbl = prod_f[["data","vol_ipameri","vol_domiciano","vol_total"]].copy()
        tbl.columns = ["Mês", "Ipameri (m³)", "Domiciano (m³)", "Total (m³)"]
        tbl["Mês"] = tbl["Mês"].dt.strftime("%m/%Y")
        tbl = tbl.sort_values("Mês", ascending=False)
        st.dataframe(
            tbl.style.format({"Ipameri (m³)": "{:,.0f}", "Domiciano (m³)": "{:,.0f}", "Total (m³)": "{:,.0f}"}),
            use_container_width=True, hide_index=True,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — QUALIDADE
    # ══════════════════════════════════════════════════════════════════════════
    with tab_qual:
        if qual.empty:
            st.warning("Sem dados de qualidade. Execute scripts/etl_tratamento.py.")
            return

        qual["mes_ref"] = pd.to_datetime(qual["mes_ref"])

        # Seletor de mês (relatório disponível)
        meses_disp = sorted(qual["mes_ref"].dt.strftime("%m/%Y").unique(), reverse=True)
        mes_sel = st.selectbox("Relatório Aqualit", meses_disp, key="qual_mes")
        mes_ts  = pd.to_datetime(mes_sel, format="%m/%Y")
        qual_m  = qual[qual["mes_ref"] == mes_ts].copy()

        # Seletor de sistema
        sistemas = sorted(qual_m["sistema"].unique())
        sis_sel  = st.radio("Sistema", sistemas, horizontal=True, key="qual_sis")
        qual_s   = qual_m[qual_m["sistema"] == sis_sel].copy()

        if qual_s.empty:
            st.info("Sem pontos para o sistema selecionado.")
            return

        # ── Padrões de conformidade (Portaria GM/MS 888/2021) ─────────────────
        PADROES = {
            "fluor":    (0.6,  0.9,  "mg/L"),
            "cor":      (None, 15.0, "uH"),
            "turbidez": (None, 5.0,  "NTU"),
            "crl":      (0.2,  2.0,  "mg/L"),
            "ph":       (6.0,  9.5,  ""),
        }

        def semaforo(param, val):
            if val is None or (isinstance(val, float) and pd.isna(val)):
                return "⚪"
            lo, hi, _ = PADROES.get(param, (None, None, ""))
            if lo is not None and val < lo:
                return "🔴"
            if hi is not None and val > hi:
                return "🔴"
            return "🟢"

        def semaforo_micro(val):
            if val is None:
                return "⚪"
            v = str(val).upper().strip()
            return "🔴" if v == "PRESENTE" else ("🟢" if v == "AUSENTE" else "⚪")

        # ── KPIs de conformidade ───────────────────────────────────────────────
        params_num = [p for p in ["fluor", "cor", "turbidez", "crl", "ph"]
                      if p in qual_s.columns and qual_s[p].notna().any()]

        cols_kpi = st.columns(len(params_num) + 2)
        for i, p in enumerate(params_num):
            vals = qual_s[p].dropna()
            conforme = sum(1 for v in vals if semaforo(p, v) == "🟢")
            total_v  = len(vals)
            pct = conforme / total_v * 100 if total_v else 0
            label = {"fluor": "Flúor", "cor": "Cor", "turbidez": "Turbidez",
                     "crl": "Cloro Res.", "ph": "pH"}.get(p, p)
            cols_kpi[i].metric(label, f"{conforme}/{total_v}", f"{pct:.0f}% ✓")

        # E.Coli
        if "ecoli" in qual_s.columns:
            ec_vals = qual_s["ecoli"].dropna()
            ec_ok   = sum(1 for v in ec_vals if str(v).upper() == "AUSENTE")
            cols_kpi[-2].metric("E.Coli", f"{ec_ok}/{len(ec_vals)}", f"{ec_ok/len(ec_vals)*100:.0f}% ✓" if len(ec_vals) else "")
        # Coli Totais
        if "coli_tot" in qual_s.columns:
            ct_vals = qual_s["coli_tot"].dropna()
            ct_ok   = sum(1 for v in ct_vals if str(v).upper() == "AUSENTE")
            cols_kpi[-1].metric("Col. Totais", f"{ct_ok}/{len(ct_vals)}", f"{ct_ok/len(ct_vals)*100:.0f}% ✓" if len(ct_vals) else "")

        st.markdown("---")

        # ── Tabela semáforo por ponto ──────────────────────────────────────────
        st.markdown(f"#### Pontos de Coleta — {sis_sel} | {mes_sel}")

        rows_tbl = []
        for _, r in qual_s.iterrows():
            row = {"Nº": r.get("numero", ""), "Ponto": r.get("ponto", "")}

            if sis_sel == "Ipameri":
                row["Flúor"]  = f"{semaforo('fluor', r.get('fluor'))} {r.get('fluor','')}" if pd.notna(r.get("fluor")) else "—"
                row["E.B.A."] = f"{r.get('eba','')}" if pd.notna(r.get("eba")) else "—"

            row["Cor"]      = f"{semaforo('cor',      r.get('cor'))}      {r.get('cor','')}"      if pd.notna(r.get("cor"))      else "—"
            row["Turbidez"] = f"{semaforo('turbidez', r.get('turbidez'))} {r.get('turbidez','')}" if pd.notna(r.get("turbidez")) else "—"
            row["E.Coli"]   = f"{semaforo_micro(r.get('ecoli'))} {r.get('ecoli','')}"             if r.get("ecoli") else "—"
            row["C.Totais"] = f"{semaforo_micro(r.get('coli_tot'))} {r.get('coli_tot','')}"       if r.get("coli_tot") else "—"
            row["CRL"]      = f"{semaforo('crl', r.get('crl'))} {r.get('crl','')}"               if pd.notna(r.get("crl"))      else "—"
            row["pH"]       = f"{semaforo('ph',  r.get('ph'))}  {r.get('ph','')}"                if pd.notna(r.get("ph"))       else "—"

            rows_tbl.append(row)

        df_tbl = pd.DataFrame(rows_tbl)
        st.dataframe(df_tbl, use_container_width=True, hide_index=True, height=600)

        # ── Gráfico radar médias ───────────────────────────────────────────────
        st.markdown("#### Médias dos Parâmetros Numéricos")
        med_data = []
        param_labels = {"fluor": "Flúor (mg/L)", "cor": "Cor (uH)", "turbidez": "Turbidez (NTU)",
                        "crl": "CRL (mg/L)", "ph": "pH"}
        for p, lbl in param_labels.items():
            if p in qual_s.columns and qual_s[p].notna().any():
                media = qual_s[p].mean()
                lo, hi, _ = PADROES.get(p, (None, None, ""))
                med_data.append({"Parâmetro": lbl, "Média": round(media, 3),
                                 "Limite Mín": lo, "Limite Máx": hi})

        if med_data:
            df_med = pd.DataFrame(med_data)
            fig_med = go.Figure()
            fig_med.add_trace(go.Bar(
                x=df_med["Parâmetro"], y=df_med["Média"],
                marker_color=[
                    "#16a34a" if (
                        (row["Limite Mín"] is None or row["Média"] >= row["Limite Mín"]) and
                        (row["Limite Máx"] is None or row["Média"] <= row["Limite Máx"])
                    ) else "#dc2626"
                    for _, row in df_med.iterrows()
                ],
                text=[str(v) for v in df_med["Média"]],
                textposition="outside",
            ))
            fig_med.update_layout(
                title=f"Médias dos Parâmetros — {sis_sel} | {mes_sel}",
                margin=dict(t=40, b=0, l=0, r=20), height=320, showlegend=False,
            )
            st.plotly_chart(fig_med, use_container_width=True)


# ── Navegação ─────────────────────────────────────────────────────────────────
def main():
    D    = load()
    d0, d1 = sidebar_periodo()

    paginas = {
        "Executivo":                          pg_cockpit,
        "Faturamento e Medição":              pg_faturamento,
        "Arrecadação (Série Histórica)":      pg_arrecadacao,
        "Boletim de Arrecadação Diária":      pg_arrecadacao_diaria,
        "Inadimplência":                      pg_inadimplencia,
        "Serviços Operacionais":              pg_servicos,
        "Cobrança e Recuperação de Receita":  pg_cortes,
        "Energia Elétrica":      pg_energia,
        "Frota Combustível":     pg_frota_combustivel,
        "Tratamento":            pg_tratamento,
    }

    st.sidebar.markdown("### Cockpits")
    cockpit_list = [k for k in paginas.keys() if k.strip()]
    pg_sel = st.sidebar.radio("Cockpits", cockpit_list, label_visibility="hidden", horizontal=False)

    st.sidebar.markdown("---")
    agora_br = datetime.now(ZoneInfo("America/Sao_Paulo"))
    st.sidebar.caption(f"Atualizado: {agora_br.strftime('%d/%m/%Y %H:%M')}")
    if st.sidebar.button("↻ Recarregar dados"):
        st.cache_data.clear()
        st.rerun()

    paginas[pg_sel](D, d0, d1)


if __name__ == "__main__":
    main()
