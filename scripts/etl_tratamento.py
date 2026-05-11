"""
ETL - Cockpit Tratamento
Lê PRODUÇÃO DE ÁGUA.xlsx (aba TOTAL) e Resultados Qualidade YYYY.xlsx
(um arquivo por ano, uma aba por mês, seções IPAMERI + DOMICIANO na mesma aba)

Exporta:
  data/producao_agua.parquet   — volumes mensais + insumos
  data/qualidade_agua.parquet  — pontos de qualidade por mês/sistema
"""
import re
import glob
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "Planilhas"
DATA = ROOT / "data"

# ─── Produção de Água ──────────────────────────────────────────────────────────

def etl_producao():
    path = PLAN / "PRODUÇÃO DE ÁGUA.xlsx"
    df = pd.read_excel(path, sheet_name="TOTAL", header=None)

    rows = []
    for _, r in df.iterrows():
        raw = r[0]
        if not isinstance(raw, (str, pd.Timestamp)) and pd.isna(raw):
            continue
        try:
            dt = pd.to_datetime(raw, errors="raise")
        except Exception:
            continue

        def _f(v):
            try:
                return float(v) if pd.notna(v) else None
            except Exception:
                return None

        vol_ip  = _f(r[2])
        vol_dom = _f(r[4])
        vol_tot = _f(r[6])

        if vol_tot == 0 and vol_ip is None and vol_dom is None:
            continue
        if vol_ip is None and vol_dom is None and vol_tot is None:
            continue

        rows.append({
            "data":          dt,
            "vol_ipameri":   vol_ip   if vol_ip   else 0.0,
            "vol_domiciano": vol_dom  if vol_dom  else 0.0,
            "vol_total":     vol_tot  if vol_tot  else 0.0,
            "cal_kg":    _f(r[8]),
            "cloro_kg":  _f(r[9]),
            "fluor_kg":  _f(r[10]),
            "pac_kg":    _f(r[11]),
            "naclo_kg":  _f(r[12]),
        })

    out = pd.DataFrame(rows)
    out["data"] = pd.to_datetime(out["data"]).dt.normalize()
    out = out[out["vol_total"] > 0].reset_index(drop=True)
    out.to_parquet(DATA / "producao_agua.parquet", index=False)
    print(f"producao_agua: {len(out)} linhas | {out['data'].min().strftime('%m/%Y')} a {out['data'].max().strftime('%m/%Y')}")
    return out


# ─── Qualidade da Água — Resultados Qualidade YYYY.xlsx ───────────────────────

_PADROES = {
    # (min, max) — None = sem limite nesse lado — Portaria GM/MS 888/2021
    "fluor":    (0.6,  0.9),
    "cor":      (None, 15.0),
    "turbidez": (None, 5.0),
    "crl":      (0.2,  2.0),
    "ph":       (6.0,  9.5),
}

_MESES_PT = {
    "JANEIRO": 1, "FEVEREIRO": 2, "MARÇO": 3, "MARCO": 3,
    "ABRIL": 4, "MAIO": 5, "JUNHO": 6, "JULHO": 7, "AGOSTO": 8,
    "SETEMBRO": 9, "OUTUBRO": 10, "NOVEMBRO": 11, "DEZEMBRO": 12,
}

# Linhas especiais que não são pontos de distribuição — ignorar
_LINHAS_ESPECIAIS = {"MÉDIA", "MEDIA", "SAÍDA DO TRATAMENTO MENSAL", "SAIDA DO TRATAMENTO MENSAL",
                     "SAÍDA DO POÇO MENSAL", "SAIDA DO POCO MENSAL", "CAPTAÇÃO MENSAL", "CAPTACAO MENSAL"}


def _fv(v):
    try:
        return float(v) if pd.notna(v) else None
    except Exception:
        return None


def _parse_ausente(v):
    if isinstance(v, str):
        return v.strip().upper()
    return None


def _is_especial(val):
    """Retorna True se a linha é MÉDIA ou linha especial de saída/captação."""
    if val is None:
        return False
    s = str(val).strip().upper()
    return s in _LINHAS_ESPECIAIS or s.startswith("MÉDIA") or s.startswith("MEDIA")


def _parse_aba(df, mes_ref):
    """
    Parseia uma aba com estrutura:
      Linha 0: título "RESULTADOS AQUALIT IPAMERI - Mês/Ano"
      Linha 1: vazia
      Linha 2: header (N°, PONTO, NaN, NaN, NaN, FLUOR, E.B.A., COR, TURB, E.COLI, C.T., CRL, PH)
      Linhas 3+: pontos Ipameri
      [linha MÉDIA]
      [linhas especiais: saída tratamento, captação]
      Linha "RESULTADOS AQUALIT DOMICIANO...": separador seção Domiciano
      Linha: vazia
      Linha: header Domiciano (PONTO, NaN, NaN, NaN, NaN, COR, TURB, E.COLI, C.T., CRL, PH)
      Linhas: pontos Domiciano
      [linha MÉDIA]
      [linhas especiais]

    Retorna lista de dicts com todos os pontos (Ipameri + Domiciano).
    """
    frames = []

    # Encontra índice da seção DOMICIANO
    domiciano_start = None
    for i, row in df.iterrows():
        val = str(row[0]).upper() if pd.notna(row[0]) else ""
        if "DOMICIANO" in val and "RESULTADOS" in val:
            domiciano_start = i
            break

    # ── IPAMERI: linhas 3 até (domiciano_start ou fim), excluindo especiais ──
    ip_end = domiciano_start if domiciano_start is not None else len(df)
    for i in range(3, ip_end):
        r = df.iloc[i]
        raw_num = r[0]
        raw_pto = r[1]

        # Pular linhas sem número válido
        if pd.isna(raw_num):
            continue
        if _is_especial(raw_num) or _is_especial(raw_pto):
            continue
        try:
            num = int(float(raw_num))
        except (ValueError, TypeError):
            continue

        frames.append({
            "mes_ref":  mes_ref,
            "sistema":  "Ipameri",
            "numero":   num,
            "ponto":    str(raw_pto).strip() if pd.notna(raw_pto) else "",
            "tipo":     "distribuição",
            "fluor":    _fv(r[5]),
            "eba":      _fv(r[6]),
            "cor":      _fv(r[7]),
            "turbidez": _fv(r[8]),
            "ecoli":    _parse_ausente(r[9]),
            "coli_tot": _parse_ausente(r[10]),
            "crl":      _fv(r[11]),
            "ph":       _fv(r[12]),
        })

    # ── DOMICIANO: linhas após o separador + 2 (vazia + header) ──
    if domiciano_start is not None:
        dom_data_start = domiciano_start + 3  # pula: separador, vazia, header
        for i in range(dom_data_start, len(df)):
            r = df.iloc[i]
            raw_num = r[0]
            raw_pto = r[1]

            if pd.isna(raw_num):
                continue
            if _is_especial(raw_num) or _is_especial(raw_pto):
                continue
            try:
                num = int(float(raw_num))
            except (ValueError, TypeError):
                continue

            # Domiciano: PONTO(0), COR(5), TURB(6), ECOLI(7), CT(8), CRL(9), PH(10)
            frames.append({
                "mes_ref":  mes_ref,
                "sistema":  "Domiciano Ribeiro",
                "numero":   num,
                "ponto":    str(raw_pto).strip() if pd.notna(raw_pto) else "",
                "tipo":     "distribuição",
                "fluor":    None,
                "eba":      None,
                "cor":      _fv(r[5]),
                "turbidez": _fv(r[6]),
                "ecoli":    _parse_ausente(r[7]),
                "coli_tot": _parse_ausente(r[8]),
                "crl":      _fv(r[9]),
                "ph":       _fv(r[10]),
            })

    return frames


def etl_qualidade():
    """
    Lê todos os arquivos 'Resultados Qualidade YYYY.xlsx' em Planilhas/.
    Cada arquivo tem abas por mês; cada aba tem seções IPAMERI e DOMICIANO.
    """
    arquivos = sorted(glob.glob(str(PLAN / "Resultados Qualidade *.xlsx")))

    # Fallback: ainda suporta arquivos legados RELATORIO AQUALIT *.xlsx se existirem
    arquivos_legado = sorted(glob.glob(str(PLAN / "RELATORIO AQUALIT*.xlsx")))

    if not arquivos and not arquivos_legado:
        print("Nenhum arquivo de qualidade encontrado.")
        return pd.DataFrame()

    all_frames = []

    # ── Novos arquivos: Resultados Qualidade YYYY.xlsx ──
    for arq in arquivos:
        nome = Path(arq).stem
        # Extrai ano do nome: "Resultados Qualidade 2026" → 2026
        ano_match = re.search(r'(20\d\d)', nome)
        ano = int(ano_match.group(1)) if ano_match else 2026

        xl = pd.ExcelFile(arq)
        for sheet in xl.sheet_names:
            sheet_upper = sheet.strip().upper().replace("Ç", "C").replace("Ã", "A")
            # Normaliza para lookup: MARÇO → MARCO
            sheet_norm = (sheet_upper
                          .replace("Ç", "C")
                          .replace("Ã", "A")
                          .replace("É", "E")
                          .replace("Ê", "E"))
            mes_num = _MESES_PT.get(sheet_upper) or _MESES_PT.get(sheet_norm)
            if mes_num is None:
                continue  # aba não é mês (ex: "Resumo", "Capa")

            df = xl.parse(sheet, header=None)
            if df.empty or len(df) < 4:
                continue

            mes_ref = pd.Timestamp(ano, mes_num, 1)
            pontos = _parse_aba(df, mes_ref)
            all_frames.extend(pontos)
            print(f"  {Path(arq).name} [{sheet}]: {len(pontos)} pontos")

    # ── Arquivos legados: RELATORIO AQUALIT *.xlsx (compatibilidade retroativa) ──
    for arq in arquivos_legado:
        nome = Path(arq).stem
        mes_match = re.search(
            r'(JANEIRO|FEVEREIRO|MAR[ÇC]O|ABRIL|MAIO|JUNHO|JULHO|AGOSTO|SETEMBRO|OUTUBRO|NOVEMBRO|DEZEMBRO)',
            nome.upper()
        )
        if mes_match:
            mes_nome = mes_match.group(1).upper()
            mes_num  = _MESES_PT.get(mes_nome, 1)
        else:
            mes_num = pd.to_datetime(Path(arq).stat().st_mtime, unit="s").month

        ano_match = re.search(r'(202\d)', nome)
        ano = int(ano_match.group(1)) if ano_match else 2026
        mes_ref = pd.Timestamp(ano, mes_num, 1)

        xl = pd.ExcelFile(arq)
        for sheet, sistema in [("IPAMERI", "Ipameri"), ("DOMICIANO", "Domiciano Ribeiro")]:
            if sheet not in xl.sheet_names:
                continue
            df = xl.parse(sheet, header=None)
            for _, r in df.iterrows():
                raw_num = r[0]
                if not isinstance(raw_num, (int, float)) or pd.isna(raw_num):
                    continue
                if str(raw_num).upper() in ("Nº", "MÉDIA", "NÂ°"):
                    continue
                try:
                    num = int(raw_num)
                except Exception:
                    continue
                if sistema == "Ipameri":
                    all_frames.append({
                        "mes_ref":  mes_ref, "sistema": sistema,
                        "numero":   num,
                        "ponto":    str(r[1]).strip() if pd.notna(r[1]) else "",
                        "tipo":     "distribuição",
                        "fluor":    _fv(r[5]), "eba": _fv(r[6]),
                        "cor":      _fv(r[7]), "turbidez": _fv(r[8]),
                        "ecoli":    _parse_ausente(r[9]), "coli_tot": _parse_ausente(r[10]),
                        "crl":      _fv(r[11]), "ph": _fv(r[12]),
                    })
                else:
                    all_frames.append({
                        "mes_ref":  mes_ref, "sistema": sistema,
                        "numero":   num,
                        "ponto":    str(r[1]).strip() if pd.notna(r[1]) else "",
                        "tipo":     "distribuição",
                        "fluor":    None, "eba": None,
                        "cor":      _fv(r[5]), "turbidez": _fv(r[6]),
                        "ecoli":    _parse_ausente(r[7]), "coli_tot": _parse_ausente(r[8]),
                        "crl":      _fv(r[9]), "ph": _fv(r[10]),
                    })

    if not all_frames:
        print("Nenhum ponto extraído.")
        return pd.DataFrame()

    out = pd.DataFrame(all_frames)
    out = out[out["ponto"] != ""].reset_index(drop=True)
    # Remove duplicatas caso arquivo legado e novo contenham o mesmo mês
    out = out.drop_duplicates(subset=["mes_ref", "sistema", "numero"]).reset_index(drop=True)
    out.to_parquet(DATA / "qualidade_agua.parquet", index=False)
    print(f"qualidade_agua: {len(out)} pontos — {sorted(out['mes_ref'].dt.strftime('%m/%Y').unique())}")
    return out


if __name__ == "__main__":
    etl_producao()
    etl_qualidade()
    print("ETL Tratamento concluído.")
