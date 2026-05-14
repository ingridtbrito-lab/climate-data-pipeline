import os
import pandas as pd
import numpy as np

# Mapeamento de estados para regiões do Brasil
REGIOES = {
    'Norte': ['AC', 'AM', 'AP', 'PA', 'RO', 'RR', 'TO'],
    'Nordeste': ['AL', 'BA', 'CE', 'MA', 'PB', 'PE', 'PI', 'RN', 'SE'],
    'Centro-Oeste': ['DF', 'GO', 'MS', 'MT'],
    'Sudeste': ['ES', 'MG', 'RJ', 'SP'],
    'Sul': ['PR', 'RS', 'SC']
}

# Inverte o dicionário para busca rápida: estado -> região
ESTADO_REGIAO = {
    estado: regiao
    for regiao, estados in REGIOES.items()
    for estado in estados
}


def padronizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Padroniza os nomes das colunas removendo espaços e caracteres especiais.
    """
    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.replace(' ', '_')
        .str.replace('(', '')
        .str.replace(')', '')
        .str.replace('/', '_')
        .str.normalize('NFKD')
        .str.encode('ascii', errors='ignore')
        .str.decode('ascii')
    )
    return df


def converter_datas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte colunas de data e hora para datetime.
    """
    possiveis_datas = ['DATA', 'DATA_MEDICAO', 'DT_MEDICAO']
    for col in possiveis_datas:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
            df = df.rename(columns={col: 'DATA'})
            break

    if 'DATA' in df.columns:
        df['ANO'] = df['DATA'].dt.year
        df['MES'] = df['DATA'].dt.month
        df['MES_NOME'] = df['DATA'].dt.strftime('%B')
    return df


def tratar_valores_ausentes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove ou preenche valores ausentes nas colunas numéricas principais.
    """
    colunas_numericas = df.select_dtypes(include=[np.number]).columns
    total_antes = len(df)

    # Remove linhas onde todas as colunas numéricas são nulas
    df = df.dropna(subset=colunas_numericas, how='all')

    total_depois = len(df)
    removidos = total_antes - total_depois
    if removidos > 0:
        print(f"Removidos {removidos:,} registros completamente vazios.")

    return df


def extrair_estado(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tenta extrair o estado da estação a partir das colunas disponíveis.
    """
    possiveis = ['UF', 'ESTADO', 'SG_ESTADO', 'UF_ESTACAO']
    for col in possiveis:
        if col in df.columns:
            df['ESTADO'] = df[col].str.strip().str.upper()
            break

    if 'ESTADO' in df.columns:
        df['REGIAO'] = df['ESTADO'].map(ESTADO_REGIAO)

    return df


def identificar_colunas_clima(df: pd.DataFrame) -> dict:
    """
    Identifica automaticamente quais colunas contêm temperatura e precipitação.
    """
    colunas = df.columns.tolist()
    resultado = {}

    for col in colunas:
        if any(t in col for t in ['TEMP_MAX', 'TEMPERATURA_MAXIMA', 'TEM_MAX']):
            resultado['temp_max'] = col
        elif any(t in col for t in ['TEMP_MIN', 'TEMPERATURA_MINIMA', 'TEM_MIN']):
            resultado['temp_min'] = col
        elif any(t in col for t in ['TEMP_MED', 'TEMPERATURA_MEDIA', 'TEM_MED']):
            resultado['temp_med'] = col
        elif any(t in col for t in ['PRECIPITACAO', 'CHUVA', 'PRECIP', 'PREC']):
            resultado['precipitacao'] = col

    print(f"Colunas climáticas identificadas: {resultado}")
    return resultado


def processar(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline completo de processamento. Aplica todas as transformações em sequência.
    """
    print(f"Iniciando processamento: {len(df):,} registros")

    df = padronizar_colunas(df)
    df = converter_datas(df)
    df = tratar_valores_ausentes(df)
    df = extrair_estado(df)

    colunas_clima = identificar_colunas_clima(df)

    # Renomeia para nomes padronizados
    rename_map = {v: k.upper() for k, v in colunas_clima.items()}
    df = df.rename(columns=rename_map)

    print(f"Processamento concluído: {len(df):,} registros")
    return df, colunas_clima


if __name__ == "__main__":
    # Teste rápido com dados fictícios
    dados_teste = {
        'Data': ['01/01/2023', '02/01/2023', '03/01/2023'],
        'Temp Max (C)': [35.2, 36.1, None],
        'Temp Min (C)': [22.1, 21.5, 20.8],
        'Precipitacao (mm)': [0.0, 12.4, 5.2],
        'UF': ['SP', 'RJ', 'MG']
    }
    df_teste = pd.DataFrame(dados_teste)
    df_processado, cols = processar(df_teste)
    print(df_processado)