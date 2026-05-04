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
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap:0px !important; overflow:visible !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding:7px 12px !important; border-radius:8px !important;
    color:white !important; font-size:.85rem !important;
    transition: all 0.25s ease !important; min-height:32px !important;
    display:flex !important; align-items:center !important;
    line-height:1.2 !important; position:relative !important;
    overflow:visible !important; margin:0.15rem 0 !important;
    font-weight: 500 !important;
    background: rgba(100, 150, 200, 0.25) !important;
    border: 1px solid rgba(100, 150, 200, 0.2) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(100, 150, 200, 0.35) !important;
    border-color: rgba(100, 150, 200, 0.3) !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label p,
[data-testid="stSidebar"] [data-testid="stRadio"] label span,
[data-testid="stSidebar"] [data-testid="stRadio"] label div {
    color:white !important;
}
[data-testid="stSidebar"] h3 {
    margin:0.5rem 0 0.75rem 0 !important; padding:0 !important; font-size:1.0rem !important; font-weight: 600 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] {
    margin-bottom: 1.2rem !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] {
    margin-top:0.3rem !important; margin-bottom:0.5rem !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    padding-top:0 !important; margin-top:0 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:empty {
    display:none !important; height:0 !important; margin:0 !important; padding:0 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] > div > div {
    margin: 0 !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:nth-child(1):empty {
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
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
*[aria-label*="keyboard"] { display: none !important; }
.stTooltip { display: none !important; }
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

    # normaliza data_pagamento em arr_d para datetime
    if not arr_d.empty and "data_pagamento" in arr_d.columns:
        arr_d["data_pagamento"] = pd.to_datetime(arr_d["data_pagamento"])

    return dict(
        fat=fat, alt_fat=alt_fat, arr=arr, arr_d=arr_d, arr_rub=arr_rub,
        parr=parr, inad=inad,
        cor=cor, rel=rel, srv=srv, lei=lei, bkl=bkl,
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

    opcoes = [
        "Hoje", "Esta Semana", "Este Mês", "Mês Anterior",
        "Este Trimestre", "Trimestre Anterior",
        "Este Semestre", "Semestre Anterior",
        "Este Ano", "Ano Anterior",
        "Últimos 12 Meses", "Últimos 24 Meses",
        "Todo o Histórico", "Período Personalizado",
    ]
    sel = st.sidebar.selectbox("", opcoes, index=10, label_visibility="collapsed")

    hoje = date.today()
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
    else:
        c1, c2 = st.sidebar.columns(2)
        d0 = c1.date_input("De", value=hoje.replace(day=1))
        d1 = c2.date_input("Até", value=hoje)

    return pd.Timestamp(d0), pd.Timestamp(d1)


def filtrar(df, col, d0, d1):
    """Filtra pelo período [d0, d1] inclusive. Usa < d1+1d para não capturar
    registros mensais cujo dt_ref = primeiro dia do mês seguinte."""
    if df.empty or col not in df.columns:
        return df
    s = pd.to_datetime(df[col])
    return df[(s >= d0) & (s < d1 + pd.Timedelta(days=1))]


def arr_d_por_credito(D, d0, d1):
    """Retorna arr_d filtrado pelo data_pagamento em [d0, d1] com data_credito D+ calculada.
    Sábado → crédito segunda (+2 dias), domingo → crédito segunda (+1 dia).
    Filtra por data_pagamento (não data_credito) para que pagamentos de fim de mês
    fiquem no mês de origem, consistente com o relatório do sistema."""
    ad = D["arr_d"].copy()
    if ad.empty:
        return ad
    ad["data_pagamento"] = pd.to_datetime(ad["data_pagamento"])

    def _dc(d):
        dow = d.weekday()
        if dow == 5: return d + pd.Timedelta(days=2)
        if dow == 6: return d + pd.Timedelta(days=1)
        return d

    ad["data_credito"] = ad["data_pagamento"].apply(_dc)
    return ad[(ad["data_pagamento"] >= d0) & (ad["data_pagamento"] < d1 + pd.Timedelta(days=1))]


# Feriados nacionais fixos (mês, dia) — adicione municipais/estaduais se necessário
_FERIADOS_FIXOS = {
    (1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (12, 25),
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
    if delta is not None:
        sinal = "+" if delta >= 0 else ""
        dstr = f"{sinal}{delta:.1%}".replace(".", ",") + " vs período ant."

    col.metric(label, vstr, delta=dstr,
               delta_color="normal" if not delta_inv else "inverse")


def bar_mensal(df, col_data, col_val, title, cor=None, agrupamento="M"):
    if df.empty:
        return go.Figure()
    tmp = df.copy()
    tmp["_mes"] = pd.to_datetime(tmp[col_data]).dt.to_period(agrupamento).dt.to_timestamp()
    ag = tmp.groupby("_mes")[col_val].sum().reset_index()
    ag.columns = ["Mês", "Valor"]
    fig = px.bar(ag, x="Mês", y="Valor", title=title,
                 color_discrete_sequence=[cor or COR["azul"]])
    fig.update_layout(xaxis_title="", yaxis_title="", showlegend=False,
                      margin=dict(t=35, b=0, l=0, r=0))
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
                      margin=dict(t=35, b=0, l=0, r=0))
    return fig


# ── Header executivo por página ───────────────────────────────────────────────
_PG_CORES = {
    "🏠 Cockpit Executivo":      ("#0B3558", "#1A6FAD"),
    "💰 Faturamento":            ("#0B5563", "#17A589"),
    "🏦 Arrecadação":            ("#145A32", "#27AE60"),
    "📅 Arrecadação Diária":     ("#1A5276", "#2E86C1"),
    "⚠️ Inadimplência":          ("#922B21", "#C0392B"),
    "⚙️ Serviços Operacionais":  ("#6E2F15", "#CA6F1E"),
    "✂️ Cortes e Religações":    ("#4A235A", "#7D3C98"),
    "📊 Leituras e Hidrômetros": ("#0E6655", "#1ABC9C"),
}

def page_header(titulo, periodo_str=""):
    c1, c2 = _PG_CORES.get(titulo, ("#0B3558", "#1A6FAD"))
    per = (
        f'<div style="font-size:.90rem;color:white;font-weight:500;margin-top:6px;">'
        f'📅 {periodo_str}</div>'
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
    page_header("🏠 Executivo",
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

    c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
    kpi(c1, "💰 Faturamento",   vl_fat)
    kpi(c2, "🏦 Arrecadação",   vl_arr)
    if idx_arr is not None:
        kpi(c3, "📊 Eficiência Arrec.", idx_arr, prefixo="%")
    else:
        c3.metric("📊 Eficiência Arrec.", "—")
    kpi(c4, "⚠️ Inadimplência", vl_inad)
    c5.metric("✂️ Cortes Executados", f"{qtd_cor:,}".replace(",", "."))
    c6.metric("⚙️ SLA Serviços", fmt_pct(sla_ok),
              delta=f"{fmt_pct(sla_ok - 0.9)} vs meta 90%",
              delta_color="normal" if sla_ok >= 0.9 else "inverse")
    c7.metric("💧 Total Ligações", f"{qtd_lig:,}".replace(",", "."))

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

    todos = _sort_meses(list(
        set((fat_m["Mês"].tolist() if not fat_m.empty else []) +
            (arr_m["Mês"].tolist() if not arr_m.empty else []))
    ))
    if todos:
        fig1 = go.Figure()
        if not fat_m.empty:
            vf = fat_m.set_index("Mês").reindex(todos)["Valor"].fillna(0)
            fig1.add_trace(go.Scatter(
                x=todos, y=vf, name="Faturamento",
                fill="tozeroy", fillcolor="rgba(26,111,173,0.28)",
                line=dict(color=COR["azul"], width=2),
                mode="lines+markers+text",
                text=[f"{v/1000:.0f} Mil" for v in vf],
                textposition="top center", textfont=dict(size=11, color=COR["azul_esc"], weight="bold"),
            ))
        if not arr_m.empty:
            va = arr_m.set_index("Mês").reindex(todos)["Valor"].fillna(0)
            fig1.add_trace(go.Scatter(
                x=todos, y=va, name="Arrecadação",
                fill="tozeroy", fillcolor="rgba(39,174,96,0.45)",
                line=dict(color=COR["verde"], width=2),
                mode="lines+markers+text",
                text=[f"{v/1000:.0f} Mil" for v in va],
                textposition="bottom center", textfont=dict(size=11, color="#1a6b3c", weight="bold"),
            ))
        fig1.update_layout(
            title="Faturamento e Arrecadação Mensal (R$)",
            margin=dict(t=70, b=10, l=0, r=0), height=400,
            xaxis=dict(title="", categoryorder="array", categoryarray=todos),
            yaxis=dict(title="", tickformat=",.0f"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
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
            textposition="top center", textfont=dict(size=11, weight="bold"),
            line=dict(color=COR["azul"], width=2), marker=dict(size=5),
        ))
        # Adiciona Esgoto apenas se houver dados
        if eco_m["Esgoto"].sum() > 0:
            fig2.add_trace(go.Scatter(
                x=eco_m["Mês"], y=eco_m["Esgoto"], name="Economias Esgoto",
                mode="lines+markers+text",
                text=eco_m["Esgoto"].apply(lambda v: f"{int(v):,}".replace(",", ".")),
                textposition="bottom center", textfont=dict(size=11, weight="bold"),
                line=dict(color=COR["amarelo"], width=2), marker=dict(size=5),
            ))
        fig2.update_layout(
            title="Economias Ativas + Cortadas Cavalete",
            margin=dict(t=70, b=10, l=0, r=0), height=400,
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
            ("Água + Tarifa Básica",    (agg["vl_agua"] + agg["vl_tbas_a"]) / agg["nr_eco"], "#1A6FAD", "top center", 4),
            ("Consumo Água",            agg["vl_agua"] / agg["nr_eco"], COR["azul"], "top center", 2),
            ("Produção Esgoto",         agg["vl_esgo"] / agg["nr_eco"], "#7B3F00", "bottom center", 2),
            ("Tarifa Básica Água",      agg["vl_tbas_a"] / agg["nr_eco"], "#5BA3D0", "top center", 2),
            ("Tarifa Básica Esgoto",    agg["vl_tbas_e"] / agg["nr_eco"], "#A0622D", "bottom center", 2),
            ("Lixo",                    agg["vl_lixo"] / agg["nr_eco"], "#E74C3C", "bottom center", 2),
            ("Serviços Diversos",       agg["vl_srv_div"] / agg["nr_eco"], COR["amarelo"], "top center", 2),
        ]

        for nome, vals, cor_v, textpos, width in series_fm:
            if vals.sum() > 0:
                fig3.add_trace(go.Scatter(
                    x=meses_fm, y=vals.round(1), name=nome,
                    mode="lines+markers+text",
                    text=vals.round(1).apply(lambda v: f"{v:.1f}" if v > 0 else ""),
                    textposition=textpos, textfont=dict(size=10, weight="bold"),
                    line=dict(color=cor_v, width=width), marker=dict(size=4),
                ))

        fig3.update_layout(
            title="Fatura Média por Economia (R$/Economia)",
            margin=dict(t=70, b=10, l=0, r=0), height=400,
            xaxis=dict(title="", categoryorder="array", categoryarray=meses_fm),
            yaxis=dict(title=""),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
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
            textposition="top center", textfont=dict(size=11, weight="bold"),
            line=dict(color=COR["azul"], width=2), marker=dict(size=4),
        ))
        if has_ev:
            nr_ee = agg_v["nr_ee"].replace(0, float("nan"))
            y_esgo = (agg_v["vol_e"] / nr_ee).round(1)
            fig4.add_trace(go.Scatter(
                x=meses_vf, y=y_esgo, name="Esgoto",
                mode="lines+markers+text",
                text=y_esgo.apply(lambda v: f"{v:.1f}" if v == v else ""),
                textposition="bottom center", textfont=dict(size=11, weight="bold"),
                line=dict(color=COR["esgoto"], width=2), marker=dict(size=4),
            ))
        fig4.update_layout(
            title="Volume Faturado por Economia (m³/Economia)",
            margin=dict(t=70, b=10, l=0, r=0), height=400,
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
        df_per["Rótulo"] = df_per["pct"].apply(lambda v: f"{v:.2f}%")
        df_per = df_per.sort_values(
            "Mês", key=lambda s: pd.to_datetime(s, format="%m/%Y")
        )

        def _cb(v):
            return COR["vermelho"] if v > 10 else COR["amarelo"] if v > 3 else COR["azul_c"]

        fig5 = go.Figure(go.Bar(
            x=df_per["Mês"], y=df_per["pct"],
            text=df_per["Rótulo"], textposition="outside", textfont=dict(size=14, weight="bold"),
            marker_color=[_cb(v) for v in df_per["pct"]],
        ))
        fig5.update_layout(
            title="Inadimplência por Período de Medição",
            margin=dict(t=70, b=10, l=0, r=0), height=400,
            xaxis=dict(title="", categoryorder="array",
                       categoryarray=df_per["Mês"].tolist()),
            yaxis=dict(title="", ticksuffix="%", tickformat=".1f"),
            showlegend=False,
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
            y=fi_g["Label"], x=fi_g["Pct"], orientation="h",
            text=fi_g["Txt"], textposition="outside",
            textfont=dict(color=COR["vermelho"], size=14, family="Arial Black"),
            marker_color=COR["vermelho"],
        ))
        fig6.update_layout(
            title="Inadimplência Geral",
            margin=dict(t=40, b=10, l=0, r=0), height=300,
            xaxis=dict(title="", visible=False, range=[0, 8]),
            yaxis=dict(title="", autorange="reversed", tickangle=0),
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
            margin=dict(t=50, b=10, l=0, r=0), height=400,
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
    page_header("💰 Faturamento",
                f"{d0.strftime('%d/%m/%Y')} a {d1.strftime('%d/%m/%Y')}")

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
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "💰 Total Líquido Faturado", vl_liquido)
    kpi(c2, "🔻 Abatimentos / Descontos", vl_abat)
    c3.metric("📄 Qtd Faturas", f"{int(qt_faturas):,}".replace(",", "."))
    c4.metric("💧 Volume (m³)", f"{vol_m3:,.0f}".replace(",", "."))

    st.markdown("---")

    # ── KPIs linha 2 — componentes (incluso no líquido) ──────────────────────
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Água",          vl_agua)
    kpi(c2, "Tarifa Básica", vl_tar_bas)
    kpi(c3, "Serviços",      vl_servico)
    kpi(c4, "Lixo",          vl_lixo)

    # ── KPIs linha 3 — exclusões do faturamento líquido ──────────────────────
    st.caption("ℹ️ Os valores abaixo não compõem o Faturamento Líquido (conforme relatório FAT0015):")
    c1, c2 = st.columns(2)
    kpi(c1, "⚠️ Multas / Juros / Cor.", vl_multas)
    kpi(c2, "🚫 Cancelamentos",         vl_cancel)

    # Nota sobre divergência residual de leituras críticas
    qt_critica = fat["fl_critica"].sum() if "fl_critica" in fat.columns else 0
    if qt_critica > 0:
        st.info(
            f"**Nota sobre divergência com o SANSYS:** {int(qt_critica)} fatura(s) com leitura crítica "
            f"(hidrômetro anômalo) estão neste período. O SANSYS substitui o consumo por uma estimativa "
            f"histórica, mas o BigQuery armazena o valor bruto pré-correção. A diferença residual entre "
            f"este painel e o FAT0015 é estrutural nessa fonte de dados — não é erro de fórmula."
        )

    st.markdown("---")

    # ── Gráficos ──────────────────────────────────────────────────────────────
    fat_m = fat.copy()
    fat_m["_mes"] = pd.to_datetime(fat_m["dt_ref"]).dt.to_period("M").dt.to_timestamp()
    # Componentes do Faturamento Líquido (excluindo Multas/Juros)
    agg_cols = {"Água": "vl_agua", "Tarifa Básica": "vl_servico_basico_agua",
                "Serviços": "vl_servico", "Lixo": "vl_lixo"}
    agg_dict = {k: (v, "sum") for k, v in agg_cols.items() if v in fat_m.columns}
    ag = fat_m.groupby("_mes").agg(**agg_dict).reset_index().rename(columns={"_mes": "Mês"})
    ag_melt = ag.melt(id_vars="Mês", var_name="Componente", value_name="Valor")
    ag_melt = ag_melt[ag_melt["Valor"] > 0]
    fig = px.bar(ag_melt, x="Mês", y="Valor", color="Componente",
                 title="Faturamento Líquido por Componente (mensal)",
                 color_discrete_map={
                     "Água": COR["agua"], "Tarifa Básica": "#8B5CF6",
                     "Serviços": COR["servico"], "Lixo": COR["lixo"],
                 })
    fig.update_layout(margin=dict(t=35, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
    fig.update_yaxes(tickformat=",.0f")
    st.plotly_chart(fig, use_container_width=True)

    # Pizza composição — somente componentes do líquido
    comp_data = {"Água": vl_agua, "Tarifa Básica": vl_tar_bas,
                 "Serviços": vl_servico, "Lixo": vl_lixo}
    comp_data = {k: v for k, v in comp_data.items() if v > 0}
    if comp_data:
        df_comp = pd.DataFrame(list(comp_data.items()), columns=["Componente", "Valor"])
        fig2 = px.pie(df_comp, names="Componente", values="Valor",
                      title="Composição do Faturamento Líquido",
                      color_discrete_map={
                          "Água": COR["agua"], "Tarifa Básica": "#8B5CF6",
                          "Serviços": COR["servico"], "Lixo": COR["lixo"],
                      })
        fig2.update_layout(margin=dict(t=35, b=0, l=0, r=0))
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
        fig4 = px.pie(ag_cat, names="Categoria", values="Valor",
                      title="Faturamento por Categoria",
                      color_discrete_sequence=px.colors.qualitative.Set2)
        fig4.update_layout(margin=dict(t=35, b=0, l=0, r=0))
        st.plotly_chart(fig4, use_container_width=True)

    # Por bairro (top 15)
    if "nm_bairro_dim" in fat.columns:
        ag_b = fat.groupby("nm_bairro_dim")["vl_total_faturado"].sum()\
                  .sort_values(ascending=True).tail(15).reset_index()
        ag_b.columns = ["Bairro", "Valor"]
        fig5 = px.bar(ag_b, x="Valor", y="Bairro", orientation="h",
                      title="Top 15 Bairros — Faturamento",
                      color_discrete_sequence=[COR["azul"]])
        fig5.update_layout(margin=dict(t=35, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
        fig5.update_xaxes(tickformat=",.0f")
        st.plotly_chart(fig5, use_container_width=True)

    # Aviso de cobertura
    if fat_max is not None:
        st.info(f"ℹ️ Dados de faturamento disponíveis até **{fat_max.strftime('%B/%Y').capitalize()}**.")


def pg_arrecadacao(D, d0, d1):
    page_header("🏦 Arrecadação",
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
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Total Arrecadado", vl_arr)
    kpi(c2, "Água Arrecadada", vl_agua_arr)
    kpi(c3, "Esgoto Arrecadado", vl_esg_arr)
    kpi(c4, "Faturado no Período", vl_fat)

    if efic is not None:
        c_efic = st.columns(1)[0]
        kpi(c_efic, "Eficiência Arrecadação", efic, prefixo="%")
    else:
        st.metric("Eficiência Arrecadação", "—",
                  help="Faturamento não disponível neste período para calcular eficiência")

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
                  line_width=0, annotation_text="Período sel.", annotation_position="top left")
    fig.update_layout(margin=dict(t=35, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
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
        fig2.update_layout(margin=dict(t=35, b=0, l=0, r=0))
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
        fig3.update_layout(margin=dict(t=35, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
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
        fig4.update_layout(margin=dict(t=35, b=0, l=0, r=0))
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
            fig4b.update_layout(margin=dict(t=35, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
            fig4b.update_xaxes(tickformat=",.0f")
            st.plotly_chart(fig4b, use_container_width=True)


def pg_arrecadacao_diaria(D, d0, d1):
    page_header("📅 Arrecadação Diária",
                f"{d0.strftime('%d/%m/%Y')} a {d1.strftime('%d/%m/%Y')}")

    ad = D["arr_d"].copy()
    if ad.empty:
        st.warning("Sem dados diários de arrecadação.")
        return

    ad["data_pagamento"] = pd.to_datetime(ad["data_pagamento"])

    # Aplica lógica D+: sábado → +2 dias (segunda), domingo → +1 dia (segunda)
    def data_credito(row):
        dow = row["data_pagamento"].weekday()  # 0=seg, 5=sab, 6=dom
        if dow == 5: return row["data_pagamento"] + pd.Timedelta(days=2)
        if dow == 6: return row["data_pagamento"] + pd.Timedelta(days=1)
        return row["data_pagamento"]

    ad["data_credito"] = ad.apply(data_credito, axis=1)

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
    c2.metric("Dias Úteis", str(qtd_dias))
    kpi(c3, "Média por Dia Útil", media_dia)

    st.info(
        "ℹ️ **Lógica D+**: sábado → crédito segunda (+2 dias), domingo → crédito segunda (+1 dia). "
        "O período filtra pela **data de pagamento** — pagamentos de fim de mês que creditariam no "
        "mês seguinte ficam no mês de origem, consistente com o relatório do sistema. "
        "⚠️ Lotes **DDA Bradesco** (agente 8 / forma 10) têm ciclo D+2 processado em tabela separada "
        "não disponível na fonte atual (`painel_arrecadacao_contabil`): diferença residual de "
        "~R$ 23.675 em mar/2026 (dias 20, 23, 24 e 25) deve-se a esses lotes."
    )

    st.markdown("---")

    fig = go.Figure()
    fig.add_bar(x=diario["Data"], y=diario["Valor"],
                name="Arrecadação diária",
                marker_color=COR["azul"],
                text=diario["Valor"].apply(lambda v: f"R$ {v:,.0f}"),
                textposition="outside")
    fig.add_scatter(x=diario["Data"], y=diario["Acumulado"],
                    name="Acumulado", mode="lines+markers",
                    line=dict(color=COR["verde"], width=2),
                    yaxis="y2")
    fig.update_layout(
        title="Arrecadação Diária e Acumulada (D+)",
        xaxis_title="", yaxis_title="Valor Diário (R$)",
        yaxis2=dict(title="Acumulado (R$)", overlaying="y", side="right",
                    showgrid=False),
        legend=dict(orientation="h", y=1.1),
        margin=dict(t=70, b=0, l=0, r=0), height=400,
        hovermode="x unified",
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
        ag_frm["Canal"] = ag_frm["Canal"].str.extract(r'^(.{0,30})')
        fig2 = px.pie(ag_frm.head(7), names="Canal", values="Valor",
                      title="Canal de Pagamento",
                      color_discrete_sequence=px.colors.qualitative.Set3)
        fig2.update_layout(margin=dict(t=70, b=0, l=0, r=0), height=400,
                           legend=dict(font=dict(size=9)))
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
    page_header("⚠️ Inadimplência",
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
    c1, c2, c3, c4 = st.columns(4)
    kpi(c1, "Total Inadimplência", vl_inad)
    kpi(c2, "Índice Inadimplência", idx_inad, prefixo="%")
    c3.metric("Qtd Faturas Vencidas", f"{qtd_fat:,}".replace(",", "."))
    kpi(c4, "Ticket Médio", tkt_med)
    st.metric("Com Corte Pendente", f"{qtd_corte:,}".replace(",", "."),
              delta="aguardando corte", delta_color="off")

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
    fig2 = px.pie(fi_q, names="faixa_atraso", values="Qtd",
                  title="Distribuição por Qtd de Faturas",
                  color_discrete_sequence=px.colors.qualitative.Set3)
    fig2.update_layout(margin=dict(t=35, b=0, l=0, r=0))
    st.plotly_chart(fig2, use_container_width=True)
    if "nm_bairro_dim" in inad.columns:
        ag_b = inad.groupby("nm_bairro_dim")["vl_divida"].sum()\
                   .sort_values(ascending=True).tail(15).reset_index()
        ag_b.columns = ["Bairro", "Valor"]
        fig3 = px.bar(ag_b, x="Valor", y="Bairro", orientation="h",
                      title="Top 15 Bairros — Inadimplência",
                      color="Valor",
                      color_continuous_scale=["#FFF3CD", "#E74C3C"])
        fig3.update_layout(margin=dict(t=35, b=0, l=0, r=0),
                           xaxis_title="", yaxis_title="",
                           coloraxis_showscale=False)
        fig3.update_xaxes(tickformat=",.0f")
        st.plotly_chart(fig3, use_container_width=True)

    # Corte pendente vs não pendente
    if "fl_corte_pendente" in inad.columns:
        cp = inad.copy()
        cp["Status Corte"] = cp["fl_corte_pendente"].map(
            {True: "Corte Pendente", False: "Sem Corte"})
        ag_cp = cp.groupby("Status Corte")["vl_divida"].sum().reset_index()
        ag_cp.columns = ["Status", "Valor"]
        fig4 = px.pie(ag_cp, names="Status", values="Valor",
                      title="Inadimplência: Corte Pendente vs Sem Corte",
                      color_discrete_map={
                          "Corte Pendente": COR["vermelho"],
                          "Sem Corte": COR["amarelo"]
                      })
        fig4.update_layout(margin=dict(t=35, b=0, l=0, r=0))
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
    page_header("⚙️ Serviços Operacionais",
                f"{d0.strftime('%d/%m/%Y')} a {d1.strftime('%d/%m/%Y')}")

    srv = filtrar(D["srv"], "dt_solicitacao", d0, d1)
    bkl = filtrar(D["bkl"], "dt_ref", d0, d1)

    if srv.empty:
        st.warning("Sem dados de serviços no período.")
        return

    srv = merge_equipe(srv, D)
    srv = merge_bairro(srv, D, col="id_bairro")

    qtd  = int(srv["qt_servico"].sum())
    fpr  = int(srv[srv["fl_fora_prazo"] == True]["qt_servico"].sum()) if "fl_fora_prazo" in srv.columns else 0
    sla  = (qtd - fpr) / qtd if qtd else 0
    t_med = srv["qt_tempo_execucao"].mean() / 60 if "qt_tempo_execucao" in srv.columns else 0
    bkl_p = int(bkl["qt_pendente"].sum()) if not bkl.empty else 0
    c1, c2 = st.columns(2)
    c1.metric("Total de Serviços", f"{qtd:,}".replace(",", "."))
    kpi(c2, "% SLA no Prazo", sla, prefixo="%")
    st.metric("Tempo Médio Exec.", f"{t_med:.1f}h")
    st.metric("Backlog Pendente", f"{bkl_p:,}".replace(",", "."),
              delta_color="inverse")

    st.markdown("---")
    # Por canal de atendimento — agrupa Interno (3) + Automático-Sistema (4) como "Ações Internas"
    srv_can = srv.copy()
    srv_can["nm_tipo_atendimento"] = srv_can.apply(
        lambda r: "Ações Internas" if r.get("ch_tipo_atendimento") in (3, 4) else r["nm_tipo_atendimento"],
        axis=1,
    )
    ag_can = srv_can.groupby("nm_tipo_atendimento")["qt_servico"].sum()\
                    .sort_values(ascending=True).reset_index()
    ag_can.columns = ["Canal", "Qtd"]
    fig = px.bar(ag_can, x="Qtd", y="Canal", orientation="h",
                 title="Serviços por Canal de Atendimento",
                 color_discrete_sequence=[COR["azul"]])
    fig.update_layout(margin=dict(t=35, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    # SLA por canal
    if "fl_fora_prazo" in srv.columns:
        ag_sla = srv_can.groupby("nm_tipo_atendimento").agg(
            Total=("qt_servico","sum"),
            ForaPrazo=("fl_fora_prazo", lambda x: (x == True).sum())
        ).reset_index()
        ag_sla["No Prazo"] = ag_sla["Total"] - ag_sla["ForaPrazo"]
        ag_sla["%SLA"] = ag_sla["No Prazo"] / ag_sla["Total"]
        ag_sla = ag_sla.sort_values("%SLA")
        fig2 = px.bar(ag_sla, x="%SLA", y="nm_tipo_atendimento", orientation="h",
                      title="% SLA por Canal",
                      color="%SLA",
                      color_continuous_scale=["#E74C3C","#F39C12","#27AE60"])
        fig2.add_vline(x=0.90, line_dash="dash", line_color="gray",
                       annotation_text="Meta 90%")
        fig2.update_layout(margin=dict(t=35, b=0, l=0, r=0),
                           xaxis_title="", yaxis_title="",
                           coloraxis_showscale=False)
        fig2.update_xaxes(tickformat=".0%")
        st.plotly_chart(fig2, use_container_width=True)
    # Evolução mensal
    srv_m = srv.copy()
    srv_m["_mes"] = pd.to_datetime(srv_m["dt_solicitacao"]).dt.to_period("M").dt.to_timestamp()
    if "fl_fora_prazo" in srv_m.columns:
        srv_m["Status SLA"] = srv_m["fl_fora_prazo"].apply(
            lambda x: "Fora do Prazo" if x == True else "No Prazo"
        )
    else:
        srv_m["Status SLA"] = "No Prazo"
    ag_m = srv_m.groupby(["_mes","Status SLA"])["qt_servico"].sum().reset_index()
    ag_m.columns = ["Mês","SLA","Qtd"]
    fig3 = px.bar(ag_m, x="Mês", y="Qtd", color="SLA", barmode="stack",
                  title="Serviços Mensais (No Prazo vs Fora)",
                  color_discrete_map={"No Prazo": COR["verde"], "Fora do Prazo": COR["vermelho"]})
    fig3.update_layout(margin=dict(t=35, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
    st.plotly_chart(fig3, use_container_width=True)

    # Por equipe
    if "nm_equipe" in srv.columns:
        ag_eq = srv.groupby("nm_equipe")["qt_servico"].sum()\
                   .sort_values(ascending=True).tail(12).reset_index()
        ag_eq.columns = ["Equipe","Qtd"]
        fig4 = px.bar(ag_eq, x="Qtd", y="Equipe", orientation="h",
                      title="Serviços por Equipe (Top 12)",
                      color_discrete_sequence=[COR["azul_c"]])
        fig4.update_layout(margin=dict(t=35, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
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
        fig5.update_layout(margin=dict(t=35, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
        st.plotly_chart(fig5, use_container_width=True)


def pg_cortes(D, d0, d1):
    page_header("✂️ Cortes e Religações",
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

    # ── KPIs principais ───────────────────────────────────────────────────────
    st.metric("Cortes Executados", f"{qtd_cor:,}".replace(",", "."))
    st.metric("Religações (cavalete)", f"{qtd_rel:,}".replace(",", "."))
    st.metric("Tempo Médio Execução Corte", f"{t_exec_h:.1f}h",
              help="Da solicitação ao fim da execução (sol→fim). SLA pendente de definição pela empresa.")
    st.metric("Tempo Médio Operação Corte", f"{t_med:.1f}h",
              help="Tempo cronometrado na execução em campo.")
    st.metric("Taxa Religação/Corte", fmt_pct(taxa_r))

    st.caption(
        f"Tempo médio entre corte e pedido de religação (cavalete): "
        f"{d_med:.0f} dias  —  Normal: {d_med_normal:.0f}d  |  Urgente: {d_med_urgente:.0f}d"
    )

    st.markdown("---")
    st.markdown("##### Religações — SLA e prazo")
    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("Normal (24h)", f"{qtd_rel_normal:,}".replace(",", "."))
    kpi(r2, "% Normal no Prazo", sla_rel_normal, prefixo="%",
        delta_inv=False)
    r3.metric("Urgente (6h/14h)", f"{qtd_rel_urgente:,}".replace(",", "."))
    kpi(r4, "% Urgente no Prazo", sla_rel_urgente, prefixo="%",
        delta_inv=False)
    r5.metric("Outros tipos", f"{qtd_rel_outros:,}".replace(",", "."),
              help="Ramal, reativação etc.")

    st.markdown(
        "<small>SLA: Normal = 24h | Urgente expediente (seg-sex 08–18h) = 6h | "
        "Urgente fora expediente/feriado = 14h — contado a partir da solicitacao (dt_solicitacao)</small>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    if not cor.empty:
        cor_m = cor.copy()
        cor_m["_mes"] = pd.to_datetime(cor_m["dt_solicitacao"]).dt.strftime("%m/%Y")
        ag_c = cor_m.groupby("_mes")["qt_servico"].sum().reset_index()
        ag_c.columns = ["Mês", "Qtd"]
        ag_c["Tipo"] = "Cortes"

        frames_cr = [ag_c]
        if not rel_cav.empty:
            rel_m = rel_cav.copy()
            rel_m["_mes"] = pd.to_datetime(rel_m["dt_reliagacao"]).dt.strftime("%m/%Y")
            ag_r = rel_m.groupby("_mes")["id_servico"].nunique().reset_index()
            ag_r.columns = ["Mês", "Qtd"]
            ag_r["Tipo"] = "Religações"
            frames_cr.append(ag_r)

        df_cr = pd.concat(frames_cr)
        meses_ord = sorted(df_cr["Mês"].unique())
        fig = px.line(df_cr, x="Mês", y="Qtd", color="Tipo", markers=True,
                      title="Cortes vs Religações (mensal)",
                      color_discrete_map={"Cortes": COR["vermelho"], "Religações": COR["verde"]},
                      category_orders={"Mês": meses_ord})
        fig.update_layout(margin=dict(t=35, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
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
        fig3.update_layout(margin=dict(t=35, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
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
        fig4.update_traces(textposition="inside", textfont=dict(size=11, weight="bold"))
        fig4.update_layout(margin=dict(t=35, b=0, l=0, r=0),
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


def pg_leituras(D, d0, d1):
    page_header("📊 Leituras e Hidrômetros",
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
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Leituras Realizadas", f"{qtd_lei:,}".replace(",", "."))
    c2.metric("Volume Lido (m³)", f"{vol_lid:,}".replace(",", "."))
    c3.metric("Volume Faturado (m³)", f"{vol_fat:,}".replace(",", "."))
    c4.metric("Leituras Críticas", f"{criticas:,}".replace(",", "."))
    kpi(c5, "Índice de Perdas", idx_perd, prefixo="%")

    st.markdown("---")
    lei_m = lei.copy()
    lei_m["_mes"] = pd.to_datetime(lei_m["dt_ref"]).dt.to_period("M").dt.to_timestamp()
    ag = lei_m.groupby("_mes").agg(
        Lido=("qt_volume_lido","sum"),
        Faturado=("qt_volume_faturado","sum")
    ).reset_index().rename(columns={"_mes":"Mês"})
    ag_m = ag.melt(id_vars="Mês", var_name="Tipo", value_name="m³")
    fig = px.line(ag_m, x="Mês", y="m³", color="Tipo", markers=True,
                  title="Volume Lido vs Faturado (m³ mensal)",
                  color_discrete_map={"Lido": COR["azul"], "Faturado": COR["verde"]})
    fig.update_layout(margin=dict(t=35, b=0, l=0, r=0), xaxis_title="", yaxis_title="")
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
            margin=dict(t=35, b=120, l=0, r=0),
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
                               textfont=dict(size=10, color=COR["verde"], family="Arial Black"),
                               yaxis="y1"))
    fig3.add_trace(go.Scatter(x=ag_ef["Mês"], y=ag_ef["Ordens_Executadas"], mode="lines+markers",
                               name="Ordens de Correção Executadas", line=dict(color=COR["amarelo"], width=3, dash="dash"),
                               marker=dict(size=6), yaxis="y2"))
    fig3.add_hline(y=0.95, line_dash="dash", line_color=COR["vermelho"],
                   annotation_text="Meta 95%", yref="y1")
    fig3.update_layout(
        title="Eficiência de Leitura (sem erros)",
        margin=dict(t=35, b=0, l=0, r=0), xaxis_title="",
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
                textfont=dict(size=11, color="white", family="Arial Black")
            )
            fig4.update_layout(margin=dict(t=35, b=0, l=0, r=0),
                               xaxis_title="R$", yaxis_title="",
                               coloraxis_showscale=False)
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("Sem perdas detectadas no período selecionado")


# ── Navegação ─────────────────────────────────────────────────────────────────
def main():
    D    = load()
    d0, d1 = sidebar_periodo()

    paginas = {
        "Executivo":             pg_cockpit,
        "Faturamento":           pg_faturamento,
        "Arrecadação":           pg_arrecadacao,
        "Arrecadação Diária":    pg_arrecadacao_diaria,
        "Inadimplência":         pg_inadimplencia,
        "Serviços Operacionais": pg_servicos,
        "Cortes e Religações":   pg_cortes,
        "Leituras":              pg_leituras,
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
