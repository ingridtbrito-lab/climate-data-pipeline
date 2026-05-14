import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', '2023')


def extrair_metadados_estacao(filepath: str) -> dict:
    """
    Lê as primeiras 8 linhas do arquivo CSV do INMET
    e extrai metadados da estação (nome, UF, lat, lon, altitude).
    """
    metadados = {}
    try:
        with open(filepath, encoding='latin-1') as f:
            linhas = [next(f).strip() for _ in range(8)]

        for linha in linhas:
            if ':;' in linha:
                chave, _, valor = linha.partition(':;')
                chave = chave.strip().upper()
                valor = valor.strip()

                if 'ESTACAO' in chave:
                    metadados['ESTACAO'] = valor
                elif chave == 'UF':
                    metadados['UF'] = valor
                elif 'LATITUDE' in chave:
                    metadados['LATITUDE'] = valor.replace(',', '.')
                elif 'LONGITUDE' in chave:
                    metadados['LONGITUDE'] = valor.replace(',', '.')
                elif 'ALTITUDE' in chave:
                    metadados['ALTITUDE'] = valor.replace(',', '.')

        metadados['ARQUIVO'] = os.path.basename(filepath)
    except Exception as e:
        print(f"Erro em {filepath}: {e}")

    return metadados


def carregar_todas_estacoes() -> pd.DataFrame:
    """
    Percorre todos os arquivos CSV e retorna um DataFrame
    com os metadados de cada estação.
    """
    arquivos = [
        os.path.join(DATA_DIR, f)
        for f in os.listdir(DATA_DIR)
        if f.endswith('.CSV') or f.endswith('.csv')
    ]

    print(f"Lendo metadados de {len(arquivos)} estações...")
    registros = [extrair_metadados_estacao(f) for f in arquivos]
    df = pd.DataFrame(registros)

    # Converte coordenadas para float
    for col in ['LATITUDE', 'LONGITUDE', 'ALTITUDE']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna(subset=['LATITUDE', 'LONGITUDE'])
    print(f"Estações com coordenadas válidas: {len(df)}")
    return df


if __name__ == "__main__":
    df = carregar_todas_estacoes()
    print(df.head())
    print(df.columns.tolist())