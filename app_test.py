import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="BI Ipameri - Teste", layout="wide")

st.title("BI Aguas de Ipameri - Teste de Acesso")

st.write("[OK] Streamlit esta funcionando")

try:
    DATA_DIR = Path("data")
    ene = pd.read_parquet(DATA_DIR / "energia_consolidada_completa.parquet")
    st.success(f"[OK] Dados carregados: {len(ene)} registros de energia")

    st.write("### Amostra dos dados:")
    st.dataframe(ene.head(10))

except Exception as e:
    st.error(f"[ERRO] Ao carregar dados: {e}")

st.write("---")

menu = st.radio("Selecione:", ["Teste", "Energia"])

if menu == "Energia":
    st.subheader("Energia")

    try:
        d_uc = pd.read_parquet(DATA_DIR / "dim_unidade_consumo_energia.parquet")
        st.write(f"Dimensao UC: {len(d_uc)} unidades")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Custo", f"R$ {ene['valor_r'].sum():,.0f}")
        with col2:
            st.metric("UCs", len(ene['uc'].unique()))
        with col3:
            st.metric("Registros", len(ene))

        st.write("### Dados por UC")
        st.dataframe(ene.groupby('uc')['valor_r'].sum().sort_values(ascending=False).head(10))

    except Exception as e:
        st.error(f"[ERRO] Pagina de energia: {e}")
