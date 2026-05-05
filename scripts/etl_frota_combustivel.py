"""
ETL para extrair e processar dados de Consumo de Frota (Combustível)
Lê arquivos Excel 'RelatorioParametrizado DD-MM-DD A DD-MM-DD.xls'
e exporta em formato Parquet com análise de eficiência e custos
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import glob

# Directories
PLANILHAS_PATH = Path(__file__).parent.parent / "Planilhas"
OUTPUT_PATH = Path(__file__).parent.parent / "data"

def encontrar_arquivo_relatorio():
    """Encontra o arquivo mais recente de RelatorioParametrizado na pasta Planilhas"""
    pattern = str(PLANILHAS_PATH / "RelatorioParametrizado*.xls*")
    arquivos = glob.glob(pattern)

    if not arquivos:
        print(f"[ERRO] Nenhum arquivo RelatorioParametrizado encontrado em {PLANILHAS_PATH}")
        return None

    # Retornar o arquivo mais recente
    arquivo_recente = max(arquivos, key=lambda x: Path(x).stat().st_mtime)
    print(f"[OK] Arquivo encontrado: {Path(arquivo_recente).name}")
    return arquivo_recente

def processar_frota_combustivel(filepath):
    """Processa arquivo de consumo de frota e retorna DataFrames processados"""
    print(f"Processando: {Path(filepath).name}")

    # Ler o arquivo Excel
    try:
        df = pd.read_excel(filepath, sheet_name="RelatorioParametrizado (12)", header=2)
    except Exception as e:
        print(f"  [ERRO] Não foi possível ler o arquivo: {e}")
        return None, None

    # Renomear colunas (evitar problemas de encoding)
    col_names = [
        'Data', 'Matricula', 'Motorista', 'Veiculo', 'Modelo',
        'Quantidade', 'Valor_Unitario', 'Valor_Total', 'Quilometragem', 'Horas',
        'Km_Rodados', 'Horas_Trabalhadas', 'Km_Litros', 'Litros_Horas',
        'Valor_Km_Hora', 'Estabelecimento', 'Cidade', 'UF', 'Valor_por_Litro'
    ]

    if len(df.columns) >= len(col_names):
        df.columns = col_names[:len(df.columns)]

    # Remover linhas vazias e linhas de total
    df = df.dropna(subset=['Matricula'])
    df = df[~df['Matricula'].astype(str).str.contains('TOTAL', case=False, na=False)]

    # Converter tipos de dados
    df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
    df['Matricula'] = pd.to_numeric(df['Matricula'], errors='coerce').astype('Int64')
    df['Quantidade'] = pd.to_numeric(df['Quantidade'], errors='coerce')
    df['Valor_Unitario'] = pd.to_numeric(df['Valor_Unitario'], errors='coerce')
    df['Valor_Total'] = pd.to_numeric(df['Valor_Total'], errors='coerce')
    df['Quilometragem'] = pd.to_numeric(df['Quilometragem'], errors='coerce')
    df['Km_Rodados'] = pd.to_numeric(df['Km_Rodados'], errors='coerce')
    df['Valor_por_Litro'] = pd.to_numeric(df['Valor_por_Litro'], errors='coerce')

    # Limpar strings
    df['Motorista'] = df['Motorista'].str.strip()
    df['Veiculo'] = df['Veiculo'].str.strip()
    df['Modelo'] = df['Modelo'].str.strip()
    df['Estabelecimento'] = df['Estabelecimento'].str.strip()
    df['Cidade'] = df['Cidade'].str.strip()
    df['UF'] = df['UF'].str.strip()

    # Calcular métricas derivadas
    df['Km_Por_Litro'] = np.where(
        df['Quantidade'] > 0,
        df['Km_Rodados'] / df['Quantidade'],
        0
    )

    df['Custo_Por_Km'] = np.where(
        df['Km_Rodados'] > 0,
        df['Valor_Total'] / df['Km_Rodados'],
        0
    )

    df['Mes_Ano'] = df['Data'].dt.strftime('%Y-%m')

    # Selecionar apenas colunas úteis
    colunas_finais = [
        'Data', 'Matricula', 'Motorista', 'Veiculo', 'Modelo',
        'Quantidade', 'Valor_Unitario', 'Valor_Total',
        'Km_Rodados', 'Km_Por_Litro', 'Custo_Por_Km',
        'Estabelecimento', 'Cidade', 'UF', 'Valor_por_Litro',
        'Mes_Ano'
    ]

    df = df[colunas_finais].dropna(subset=['Data', 'Motorista', 'Veiculo', 'Quantidade', 'Valor_Total'])

    # Validar dados
    if df.empty:
        print("  [AVISO] Nenhum registro válido encontrado")
        return None, None

    print(f"  [OK] {len(df)} registros processados")

    # Criar dimensão de veículos
    dim_veiculo = df[['Veiculo', 'Modelo']].drop_duplicates().reset_index(drop=True)
    dim_veiculo.columns = ['Veiculo_ID', 'Modelo']

    return df, dim_veiculo

def main():
    """Processa relatório de frota e exporta Parquets"""
    print("Iniciando ETL de Consumo de Frota Combustível...\n")

    # Encontrar arquivo
    arquivo = encontrar_arquivo_relatorio()
    if not arquivo:
        print("[ERRO] Encerrando ETL")
        return

    # Processar arquivo
    df_frota, dim_veiculo = processar_frota_combustivel(arquivo)

    if df_frota is None or df_frota.empty:
        print("[ERRO] Nenhum dado processado com sucesso")
        return

    # Estatísticas
    print("\n" + "=" * 60)
    print("RESUMO DA EXTRACAO")
    print("=" * 60)
    print(f"Total de registros: {len(df_frota)}")
    print(f"Data minima: {df_frota['Data'].min().strftime('%d/%m/%Y')}")
    print(f"Data maxima: {df_frota['Data'].max().strftime('%d/%m/%Y')}")

    print(f"\nMotorisas unicos: {df_frota['Motorista'].nunique()}")
    print(f"Veiculos unicos: {df_frota['Veiculo'].nunique()}")
    print(f"Modelos unicos: {df_frota['Modelo'].nunique()}")

    print(f"\nTotalizacoes:")
    print(f"  Combustivel consumido: {df_frota['Quantidade'].sum():.2f} L")
    print(f"  Valor gasto: R$ {df_frota['Valor_Total'].sum():.2f}")
    print(f"  Km rodados: {df_frota['Km_Rodados'].sum():.0f}")
    print(f"  Eficiencia media: {(df_frota['Km_Rodados'].sum() / df_frota['Quantidade'].sum()):.2f} km/L")

    print(f"\nTop 5 motoristas (por valor):")
    top_mot = df_frota.groupby('Motorista')['Valor_Total'].sum().nlargest(5)
    for name, valor in top_mot.items():
        print(f"  {name}: R$ {valor:.2f}")

    # Exportar Parquets
    output_frota = OUTPUT_PATH / "frota_combustivel.parquet"
    output_veiculo = OUTPUT_PATH / "dim_veiculo_frota.parquet"

    df_frota.to_parquet(output_frota, index=False)
    dim_veiculo.to_parquet(output_veiculo, index=False)

    print(f"\n[OK] Exportado: {output_frota.name}")
    print(f"[OK] Exportado: {output_veiculo.name}")
    print(f"\nETL concluido com sucesso em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    main()
