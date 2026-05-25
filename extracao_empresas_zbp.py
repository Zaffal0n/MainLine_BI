import os
import requests
import pandas as pd
from dotenv import load_dotenv
from extracao_empresas_cbp import setores

# Garantir que a pasta de dados existe
os.makedirs("dados", exist_ok=True)

# Carregar as chaves de segurança
load_dotenv()
CENSUS_KEY = os.getenv("CENSUS_API_KEY")

def extrair_empresas_zbp():
    print("A iniciar a extração de empresas por Zip Code (via API unificada CBP)...")
    
    # CORREÇÃO 1: A URL agora aponta para a base unificada CBP
    base_url = "https://api.census.gov/data/2021/cbp"
    
    dfs = [] # Lista para guardar as tabelas temporárias
    
    for nome_setor, codigo_naics in setores.items():
        print(f"A extrair dados para o setor: {nome_setor} (NAICS {codigo_naics})...")
        
        # CORREÇÃO 2: A variável de pesquisa manteve a taxonomia de 2017
        parametros = {
            "get": "ESTAB", 
            "for": "zip code:*",
            "NAICS2017": codigo_naics,
            "key": CENSUS_KEY
        }
        
        try:
            response = requests.get(base_url, params=parametros)
            
            if response.status_code != 200:
                print(f"Erro na API para {nome_setor}: {response.text}")
                continue
                
            dados_json = response.json()
            
            # Separar o cabeçalho das linhas de dados
            colunas = dados_json[0]
            linhas = dados_json[1:]
            
            # Criar o DataFrame
            df_setor = pd.DataFrame(linhas, columns=colunas)
            
            # Limpeza e Padronização (Cobrindo possíveis variações no nome da coluna de CEP)
            df_setor = df_setor.rename(columns={
                "ESTAB": "Qtd_Empresas",
                "zip code": "Zip_Code",
                "zipcode": "Zip_Code"
            })
            
            # Tipagem correta dos dados
            df_setor["Qtd_Empresas"] = pd.to_numeric(df_setor["Qtd_Empresas"], errors="coerce")
            df_setor["Setor"] = nome_setor
            
            # Isolar apenas as colunas que nos interessam
            df_setor = df_setor[["Zip_Code", "Setor", "Qtd_Empresas"]]
            
            # Adicionar à nossa lista de tabelas
            dfs.append(df_setor)
            
        except Exception as e:
            print(f"Erro técnico ao extrair {nome_setor}: {e}")
            
    # Juntar os dois setores numa única tabela (Concat)
    if dfs:
        df_final = pd.concat(dfs, ignore_index=True)
        
        # Remover CEPs que não têm nenhuma empresa destas verticais (filtramos o ruído)
        df_final = df_final[df_final["Qtd_Empresas"] > 0]
        
        # Guardar na nossa pasta oficial
        caminho_arquivo = "dados/base_empresas_zipcode.csv"
        df_final.to_csv(caminho_arquivo, index=False)
        
        print(f"\n✅ Sucesso! Extraídas {len(df_final)} zonas geográficas com PMEs ativas.")
        print(f"Arquivo guardado em: {caminho_arquivo}")

if __name__ == "__main__":
    extrair_empresas_zbp()