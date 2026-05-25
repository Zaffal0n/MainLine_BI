import pandas as pd
import os
import sys

def processar_polos_completo():
    print("Iniciando Mapeamento de Estados e Priorização dos Polos...")

# 1. Carregar o dicionário de Estados (Local)
    caminho_mapa = "dados/zipcodes.csv"
    
    if not os.path.exists(caminho_mapa):
        print(f"🔴 ERRO: O arquivo {caminho_mapa} não foi encontrado.")
        return
    
    # A leitura do CSV (garantindo que não há vírgulas sobrando fora do lugar)
    df_map = pd.read_csv(caminho_mapa, usecols=["zip_code", "state"], dtype={"zip_code": str})
    df_map = df_map.rename(columns={"zip_code": "Zip_Code", "state": "Estado"})
    df_map["Zip_Code"] = df_map["Zip_Code"].str.zfill(5)

    # 2. Arquivos para processar dinamicamente
    import glob
    # Pega todos os arquivos de polos gerados automaticamente
    arquivos_polos = glob.glob("dados/polos_*_zipcode.csv")

    lista_dfs_processados = []

    # Como arquivos_polos agora é uma lista (e não um dicionário), rodamos o ciclo assim:
    for caminho in arquivos_polos:
        if "master" in caminho:
            continue # Ignora o master antigo para não criar duplicatas
            
        print(f"🛰️ Processando base de Polos: {caminho}...")
        df = pd.read_csv(caminho, dtype={"Zip_Code": str})
        
        if df.empty:
            continue

        # A. Adicionar o Estado (Cruzamento local)
        df = pd.merge(df, df_map, on="Zip_Code", how="left")
        df["Estado"] = df["Estado"].fillna("Desconhecido")

        # B. Criar o Ranking de Prioridade (Ouro/Prata/Bronze)
        try:
            df['Cluster_Prioridade'] = pd.qcut(df['Qtd_Empresas'].rank(method='first'), 
                                              q=[0, 0.7, 0.9, 1.0], 
                                              labels=['3. Baixa Prioridade (Bronze)', '2. Média Prioridade (Prata)', '1. Alta Prioridade (Ouro)'])
        except:
            df['Cluster_Prioridade'] = '2 - Prata'

        # C. Reorganizar colunas e Salvar o arquivo Setorial
        colunas_finais = ["Zip_Code", "Estado", "Setor", "Cluster_Prioridade", "Qtd_Empresas", "Populacao_Total_18", "Renda_Media_Domiciliar"]
        colunas_existentes = [c for c in colunas_finais if c in df.columns]
        df = df[colunas_existentes]

        df = df.sort_values(by=["Cluster_Prioridade", "Qtd_Empresas"], ascending=[True, False])
        df.to_csv(caminho, index=False)
        lista_dfs_processados.append(df)
        print(f"✅ Polos do setor atualizados e salvos!")

    # D. Recriar o Arquivo Master com os Polos novos consolidados
    if lista_dfs_processados:
        df_master = pd.concat(lista_dfs_processados, ignore_index=True)
        df_master.to_csv("dados/polos_industriais_zipcode_master.csv", index=False)
        print("✅ Arquivo Master de Polos recriado com sucesso!")

if __name__ == "__main__":
    processar_polos_completo()