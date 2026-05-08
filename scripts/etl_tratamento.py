"""
ETL - Cockpit Tratamento
Lê PRODUÇÃO DE ÁGUA.xlsx (aba TOTAL) e RELATORIO AQUALIT *.xlsx
Exporta:
  data/producao_agua.parquet   — volumes mensais + insumos
  data/qualidade_agua.parquet  — pontos de qualidade por relatório
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

    # Linhas de dados começam na linha 3 (índice 3) — header em linha 1-2
    # Cols: 0=DATA, 2=Ipameri, 4=Domiciano, 6=Total, 8=CAL, 9=CLORO, 10=FLUOR, 11=PAC, 12=NaClO
    rows = []
    for _, r in df.iterrows():
        raw = r[0]
        if not isinstance(raw, (str, pd.Timestamp)) and pd.isna(raw):
            continue
        # Ignora linhas de totais anuais e linhas sem data válida
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

        # Ignora linhas de datas futuras sem volume
        if vol_tot == 0 and vol_ip is None and vol_dom is None:
            continue
        if vol_ip is None and vol_dom is None and vol_tot is None:
            continue

        rows.append({
            "data":       dt,
            "vol_ipameri":    vol_ip   if vol_ip   else 0.0,
            "vol_domiciano":  vol_dom  if vol_dom  else 0.0,
            "vol_total":      vol_tot  if vol_tot  else 0.0,
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


# ─── Qualidade da Água (Aqualit) ───────────────────────────────────────────────

_PADROES = {
    # (min, max) — None = sem limite nesse lado
    # Portaria GM/MS 888/2021
    "fluor":     (0.6,  0.9),
    "cor":       (None, 15.0),
    "turbidez":  (None, 5.0),
    "crl":       (0.2,  2.0),
    "ph":        (6.0,  9.5),
}

def _conforme(param, valor):
    """Retorna True se valor está dentro do padrão."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return None
    lim = _PADROES.get(param)
    if lim is None:
        return None
    lo, hi = lim
    if lo is not None and valor < lo:
        return False
    if hi is not None and valor > hi:
        return False
    return True


def _parse_ausente(v):
    if isinstance(v, str):
        return v.strip().upper()
    return None


def etl_qualidade():
    # Busca todos os relatórios Aqualit na pasta Planilhas
    arquivos = sorted(glob.glob(str(PLAN / "RELATORIO AQUALIT*.xlsx")))
    if not arquivos:
        print("Nenhum relatório Aqualit encontrado.")
        return pd.DataFrame()

    frames = []
    for arq in arquivos:
        nome = Path(arq).stem
        # Extrai mês de referência do nome do arquivo (ex: "MARÇO", "ABRIL")
        # Usa a data de modificação como fallback
        mes_match = re.search(
            r'(JANEIRO|FEVEREIRO|MAR[ÇC]O|ABRIL|MAIO|JUNHO|JULHO|AGOSTO|SETEMBRO|OUTUBRO|NOVEMBRO|DEZEMBRO)',
            nome.upper()
        )
        meses_pt = {
            "JANEIRO":1,"FEVEREIRO":2,"MARÇO":3,"MARCO":3,"MARÇO":3,
            "ABRIL":4,"MAIO":5,"JUNHO":6,"JULHO":7,"AGOSTO":8,
            "SETEMBRO":9,"OUTUBRO":10,"NOVEMBRO":11,"DEZEMBRO":12,
        }
        if mes_match:
            mes_nome = mes_match.group(1).upper().replace("Ç","Ç")
            mes_num  = meses_pt.get(mes_nome, 1)
        else:
            mes_num = pd.to_datetime(Path(arq).stat().st_mtime, unit="s").month

        # Detecta ano no nome; fallback = 2026
        ano_match = re.search(r'(202\d)', nome)
        ano = int(ano_match.group(1)) if ano_match else 2026
        mes_ref = pd.Timestamp(ano, mes_num, 1)

        xl = pd.ExcelFile(arq)

        # ── IPAMERI ──
        if "IPAMERI" in xl.sheet_names:
            df = xl.parse("IPAMERI", header=None)
            # Header está na linha 2 (índice 2)
            # Colunas: 0=Nº, 1=Ponto, 4=FLUOR, 5=EBA, 6=COR, 7=TURB, 8=ECOLI, 9=CT, 10=CRL, 11=PH
            for _, r in df.iterrows():
                raw_num = r[0]
                raw_pto = r[1]
                if not isinstance(raw_num, (int, float)) or pd.isna(raw_num):
                    continue
                if str(raw_num).upper() in ("Nº", "MÉDIA", "NÂ°"):
                    continue
                try:
                    num = int(raw_num)
                except Exception:
                    continue

                def _fv(v):
                    try:
                        return float(v) if pd.notna(v) else None
                    except Exception:
                        return None

                # Header: N°(0), PONTO(1), NaN(2-4), FLUOR(5), EBA(6), COR(7), TURB(8),
                #         E.COLI(9), C.T.(10), CRL(11), PH(12)
                frames.append({
                    "mes_ref":   mes_ref,
                    "sistema":   "Ipameri",
                    "numero":    num,
                    "ponto":     str(raw_pto).strip() if pd.notna(raw_pto) else "",
                    "tipo":      "distribuição",
                    "fluor":     _fv(r[5]),
                    "eba":       _fv(r[6]),
                    "cor":       _fv(r[7]),
                    "turbidez":  _fv(r[8]),
                    "ecoli":     _parse_ausente(r[9]),
                    "coli_tot":  _parse_ausente(r[10]),
                    "crl":       _fv(r[11]),
                    "ph":        _fv(r[12]),
                })

        # ── DOMICIANO ──
        if "DOMICIANO" in xl.sheet_names:
            df = xl.parse("DOMICIANO", header=None)
            # Colunas: 0=PONTO(num), 1=PONTO(nome), 5=COR, 6=TURB, 7=ECOLI, 8=CT, 9=CRL, 10=PH
            for _, r in df.iterrows():
                raw_num = r[0]
                raw_pto = r[1]
                if not isinstance(raw_num, (int, float)) or pd.isna(raw_num):
                    continue
                try:
                    num = int(raw_num)
                except Exception:
                    continue

                def _fv(v):
                    try:
                        return float(v) if pd.notna(v) else None
                    except Exception:
                        return None

                frames.append({
                    "mes_ref":   mes_ref,
                    "sistema":   "Domiciano Ribeiro",
                    "numero":    num,
                    "ponto":     str(raw_pto).strip() if pd.notna(raw_pto) else "",
                    "tipo":      "distribuição",
                    "fluor":     None,
                    "eba":       None,
                    "cor":       _fv(r[5]),
                    "turbidez":  _fv(r[6]),
                    "ecoli":     _parse_ausente(r[7]),
                    "coli_tot":  _parse_ausente(r[8]),
                    "crl":       _fv(r[9]),
                    "ph":        _fv(r[10]),
                })

    if not frames:
        print("Nenhum ponto extraído dos relatórios Aqualit.")
        return pd.DataFrame()

    out = pd.DataFrame(frames)
    out = out[out["ponto"] != ""].reset_index(drop=True)
    out.to_parquet(DATA / "qualidade_agua.parquet", index=False)
    print(f"qualidade_agua: {len(out)} pontos — {out['mes_ref'].unique()}")
    return out


if __name__ == "__main__":
    etl_producao()
    etl_qualidade()
    print("ETL Tratamento concluído.")
