import os
import requests
import zipfile
import pandas as pd
from io import BytesIO

# Pasta onde os dados serão salvos
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)


def download_inmet_data(year: int) -> str:
    """
    Baixa dados históricos do INMET para um ano específico.
    Retorna o caminho do arquivo salvo.
    """
    url = f"https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip"
    print(f"Baixando dados de {year}...")

    response = requests.get(url, timeout=60)

    if response.status_code != 200:
        raise Exception(f"Erro ao baixar dados de {year}: status {response.status_code}")

    zip_path = os.path.join(DATA_DIR, f"{year}.zip")
    with open(zip_path, 'wb') as f:
        f.write(response.content)

    print(f"Arquivo salvo em: {zip_path}")
    return zip_path


def extract_zip(zip_path: str) -> str:
    """
    Extrai o zip do INMET e retorna a pasta de destino.
    """
    year = os.path.basename(zip_path).replace('.zip', '')
    extract_dir = os.path.join(DATA_DIR, year)
    os.makedirs(extract_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(extract_dir)

    print(f"Extraído em: {extract_dir}")
    return extract_dir


def load_station_file(filepath: str) -> pd.DataFrame:
    """
    Lê um arquivo CSV de estação do INMET e retorna um DataFrame limpo.
    """
    try:
        df = pd.read_csv(
            filepath,
            sep=';',
            encoding='latin-1',
            skiprows=8,
            decimal=',',
            na_values=['-9999', '']
        )
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"Erro ao ler {filepath}: {e}")
        return pd.DataFrame()


def load_all_stations(extract_dir: str) -> pd.DataFrame:
    """
    Lê todos os arquivos CSV de uma pasta e concatena num único DataFrame.
    """
    all_files = [
        os.path.join(extract_dir, f)
        for f in os.listdir(extract_dir)
        if f.endswith('.CSV') or f.endswith('.csv')
    ]

    print(f"{len(all_files)} arquivos encontrados.")
    frames = [load_station_file(f) for f in all_files]
    frames = [df for df in frames if not df.empty]

    if not frames:
        raise Exception("Nenhum arquivo válido encontrado.")

    combined = pd.concat(frames, ignore_index=True)
    print(f"Total de registros carregados: {len(combined):,}")
    return combined


if __name__ == "__main__":
    year = 2023
    zip_path = download_inmet_data(year)
    extract_dir = extract_zip(zip_path)
    df = load_all_stations(extract_dir)
    print(df.head())
    print(df.shape)