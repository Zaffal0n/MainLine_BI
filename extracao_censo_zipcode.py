import os
import requests
import pandas as pd
from dotenv import load_dotenv

# Garante que a nossa pasta do Data Warehouse existe
os.makedirs("dados", exist_ok=True)

# Carrega as chaves de segurança de forma invisível
load_dotenv()
CENSUS_KEY = os.getenv("CENSUS_API_KEY")

def extrair_censo_zipcode():
    print("Iniciando extração demográfica por Zip Code (ZCTA)...")
    
    # URL da American Community Survey (ACS) 5-Year Data
    base_url = "https://api.census.gov/data/2022/acs/acs5"
    
    # Parâmetros: Nome, População 18+ e Renda Média Domiciliar
    parametros = {
        "get": "NAME,B21001_002E,B19013_001E", 
        "for": "zip code tabulation area:*", # Foco total nos CEPs
        "key": CENSUS_KEY
    }
    
    try:
        response = requests.get(base_url, params=parametros)
        
        # Trava de segurança para entender erros da API
        if response.status_code != 200:
            print(f"Erro na API do Censo: {response.text}")
            return
            
        dados_json = response.json()
        
        # O Censo devolve uma lista de listas. Vamos separar o cabeçalho.
        colunas = dados_json[0]
        linhas = dados_json[1:]
        
        # Criando o DataFrame do Pandas
        df = pd.DataFrame(linhas, columns=colunas)
        
        # Limpando e renomeando para a nossa linguagem de negócio
        df = df.rename(columns={
            "NAME": "Nome_ZCTA",
            "B21001_002E": "Populacao_Total_18",
            "B19013_001E": "Renda_Media_Domiciliar",
            "zip code tabulation area": "Zip_Code"
        })
        
        # Convertendo textos para números (erros viram NaN/Nulos)
        df['Populacao_Total_18'] = pd.to_numeric(df['Populacao_Total_18'], errors='coerce')
        df['Renda_Media_Domiciliar'] = pd.to_numeric(df['Renda_Media_Domiciliar'], errors='coerce')
        
        # Removendo CEPs fantasmas (sem população ou sem dados de renda)
        df = df.dropna(subset=['Populacao_Total_18', 'Renda_Media_Domiciliar'])
        
        # Salvando a extração granular na nossa pasta oficial
        caminho_arquivo = "dados/base_demografica_zipcode.csv"
        df.to_csv(caminho_arquivo, index=False)
        
        print(f"✅ Sucesso! Extraídos os dados de {len(df)} Zip Codes americanos.")
        print(f"Arquivo salvo em: {caminho_arquivo}")
        
    except Exception as e:
        print(f"Ocorreu um erro técnico: {e}")

if __name__ == "__main__":
    extrair_censo_zipcode()