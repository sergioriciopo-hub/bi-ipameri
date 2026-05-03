"""Reescreve pg_cockpit com layout vertical (todos os gráficos full-width, empilhados)."""
from pathlib import Path

APP = Path(__file__).parent.parent / "app.py"

NEW_COCKPIT = r'''
def pg_cockpit(D, d0, d1):
    hoje = date.today()

    # ── Filtro local — padrão 12 meses (independente do filtro da sidebar) ────
    _OPCOES = ["Últimos 6 Meses", "Últimos 12 Meses", "Últimos 24 Meses", "Todo o Histórico"]
    if "cockpit_periodo" not in st.session_state:
        st.session_state["cockpit_periodo"] = "Últimos 12 Meses"

    hdr_col, fil_col = st.columns([5, 1])
    with hdr_col:
        page_header("🏠 Executivo", "")
    with fil_col:
        st.markdown("<div style='padding-top:12px'></div>", unsafe_allow_html=True)
        sel_loc = st.selectbox(
            "Período", _OPCOES,
            index=_OPCOES.index(st.session_state.get("cockpit_periodo", "Últimos 12 Meses")),
            key="cockpit_periodo", label_visibility="collapsed",
        )

    if sel_loc == "Últimos 6 Meses":
        ld0 = pd.Timestamp(hoje.replace(day=1) - relativedelta(months=5))
    elif sel_loc == "Últimos 12 Meses":
        ld0 = pd.Timestamp(hoje.replace(day=1) - relativedelta(months=11))
    elif sel_loc == "Últimos 24 Meses":
        ld0 = pd.Timestamp(hoje.replace(day=1) - relativedelta(months=23))
    else:
        ld0 = pd.Timestamp(date(2023, 1, 1))
    ld1 = pd.Timestamp(hoje)

    # ── Dados filtrados pelo período local ────────────────────────────────────
    fat      = filtrar(D["fat"],  "dt_ref",          ld0, ld1)
    arr_d_f  = arr_d_por_credito(D, ld0, ld1)
    inad     = D["inad"]
    srv      = filtrar(D["srv"], "dt_solicitacao",   ld0, ld1)
    cor_exec = filtrar(D["cor"], "dt_fim_execucao",  ld0, ld1)
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

    c1, c2, c3, c4, c5, c6 = st.columns(6)
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
                textposition="top center", textfont=dict(size=9, color=COR["azul_esc"]),
            ))
        if not arr_m.empty:
            va = arr_m.set_index("Mês").reindex(todos)["Valor"].fillna(0)
            fig1.add_trace(go.Scatter(
                x=todos, y=va, name="Arrecadação",
                fill="tozeroy", fillcolor="rgba(39,174,96,0.45)",
                line=dict(color=COR["verde"], width=2),
                mode="lines+markers+text",
                text=[f"{v/1000:.0f} Mil" for v in va],
                textposition="bottom center", textfont=dict(size=9, color="#1a6b3c"),
            ))
        fig1.update_layout(
            title="Faturamento e Arrecadação Mensal (R$)",
            margin=dict(t=40, b=10, l=0, r=0), height=400,
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
            textposition="top center", textfont=dict(size=9),
            line=dict(color=COR["azul"], width=2), marker=dict(size=5),
        ))
        fig2.add_trace(go.Scatter(
            x=eco_m["Mês"], y=eco_m["Esgoto"], name="Economias Esgoto",
            mode="lines+markers+text",
            text=eco_m["Esgoto"].apply(lambda v: f"{int(v):,}".replace(",", ".")),
            textposition="bottom center", textfont=dict(size=9),
            line=dict(color=COR["amarelo"], width=2), marker=dict(size=5),
        ))
        fig2.update_layout(
            title="Economias Ativas + Cortadas",
            margin=dict(t=40, b=10, l=0, r=0), height=400,
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
            "vl_fat":  ("vl_total_faturado", "sum"),
            "vl_agua": ("vl_agua",            "sum"),
            "vl_esgo": ("vl_esgoto",           "sum"),
            "vl_serv": ("vl_servico",          "sum"),
            "nr_eco":  ("nr_economia_agua",    "sum"),
        }
        cols_agg["vl_tbas"] = (
            ("vl_servico_basico_agua", "sum")
            if "vl_servico_basico_agua" in fm.columns
            else ("vl_servico", "sum")
        )
        agg = fm.groupby("Mês").agg(**cols_agg).reset_index()
        agg = agg[agg["nr_eco"] > 0]
        meses_fm = _sort_meses(agg["Mês"].tolist())
        agg = agg.set_index("Mês").reindex(meses_fm).reset_index()
        fig3 = go.Figure()
        series_fm = [
            ("Faturamento Total",    agg["vl_fat"]  / agg["nr_eco"], COR["verde"]),
            ("Consumo Água",         agg["vl_agua"] / agg["nr_eco"], COR["azul"]),
            ("Produção Esgoto",      agg["vl_esgo"] / agg["nr_eco"], "#7B3F00"),
            ("Tarifa Básica+Serv.",  (agg["vl_tbas"] + agg["vl_serv"]) / agg["nr_eco"], COR["amarelo"]),
        ]
        textpos = ["top center", "top center", "bottom center", "bottom center"]
        for (nome, vals, cor_v), tp in zip(series_fm, textpos):
            fig3.add_trace(go.Scatter(
                x=meses_fm, y=vals.round(1), name=nome,
                mode="lines+markers+text",
                text=vals.round(1).apply(lambda v: f"{v:.1f}"),
                textposition=tp, textfont=dict(size=9),
                line=dict(color=cor_v, width=2), marker=dict(size=4),
            ))
        fig3.update_layout(
            title="Fatura Média por Economia (R$/Economia)",
            margin=dict(t=40, b=10, l=0, r=0), height=400,
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
            textposition="top center", textfont=dict(size=9),
            line=dict(color=COR["azul"], width=2), marker=dict(size=4),
        ))
        if has_ev:
            nr_ee = agg_v["nr_ee"].replace(0, float("nan"))
            y_esgo = (agg_v["vol_e"] / nr_ee).round(1)
            fig4.add_trace(go.Scatter(
                x=meses_vf, y=y_esgo, name="Esgoto",
                mode="lines+markers+text",
                text=y_esgo.apply(lambda v: f"{v:.1f}" if v == v else ""),
                textposition="bottom center", textfont=dict(size=9),
                line=dict(color=COR["esgoto"], width=2), marker=dict(size=4),
            ))
        fig4.update_layout(
            title="Volume Faturado por Economia (m³/Economia)",
            margin=dict(t=40, b=10, l=0, r=0), height=400,
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
            text=df_per["Rótulo"], textposition="outside", textfont=dict(size=9),
            marker_color=[_cb(v) for v in df_per["pct"]],
        ))
        fig5.update_layout(
            title="Inadimplência por Período de Medição",
            margin=dict(t=40, b=10, l=0, r=0), height=400,
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
            text=fi_g["Txt"], textposition="inside", insidetextanchor="middle",
            textfont=dict(color="white", size=12),
            marker_color=COR["vermelho"],
        ))
        fig6.update_layout(
            title="Inadimplência Geral",
            margin=dict(t=40, b=10, l=0, r=0), height=300,
            xaxis=dict(title="", visible=False),
            yaxis=dict(title="", autorange="reversed"),
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
        fu2 = fat_all2.copy() if not fat_all2.empty else pd.DataFrame()
        if not fu2.empty and "nr_lig_agua" in fu2.columns:
            fu2["dt_ref"] = pd.to_datetime(fu2["dt_ref"])
            fu2 = fu2[fu2["dt_ref"] == fu2["dt_ref"].max()]
            total_lig = int(fu2["nr_lig_agua"].sum())
            st.metric("Total Ligações", f"{total_lig:,}".replace(",", "."),
                      help="Execute o ETL para ver o detalhamento por situação.")
        else:
            st.info("Execute o ETL para atualizar.")

    # ── Rodapé ────────────────────────────────────────────────────────────────
    fat_max_dt = pd.to_datetime(D["fat"]["dt_ref"]).max() if not D["fat"].empty else None
    if fat_max_dt is not None:
        st.caption(
            f"ℹ️ Faturamento disponível até **{fat_max_dt.strftime('%B/%Y').capitalize()}** · "
            f"Inadimplência: snapshot da data de atualização"
        )
'''

content = APP.read_text(encoding="utf-8")
start = content.find("\ndef pg_cockpit(D, d0, d1):")
end   = content.find("\ndef pg_faturamento(D, d0, d1):")
if start == -1 or end == -1:
    raise RuntimeError(f"Marcadores não encontrados: start={start}, end={end}")
new_content = content[:start] + NEW_COCKPIT + "\n" + content[end:]
APP.write_text(new_content, encoding="utf-8")
print(f"OK — {len(new_content)} chars")
