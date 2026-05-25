import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import os
import sys

print("Iniciando Mapeamento de Estados e Clusterização Master...")

# ==========================================
# 1. Carregar o dicionário de Zip Code x Estado (LEITURA LOCAL)
# ==========================================
caminho_mapa = "dados/zipcodes.csv" # Nome atualizado do arquivo

if not os.path.exists(caminho_mapa):
    print(f"\n🔴 ERRO: O arquivo {caminho_mapa} não foi encontrado.")
    print("Por favor, faça o download manual do novo link fornecido no chat e salve-o na pasta 'dados' com o nome 'zipcodes.csv'.")
    sys.exit()

print("Carregando dicionário local de CEPs x Estados...")
# A nova base da Universidade de Washington usa a coluna 'zip_code' em vez de 'zip'
df_map = pd.read_csv(caminho_mapa, usecols=["zip_code", "state"], dtype={"zip_code": str})
df_map = df_map.rename(columns={"zip_code": "Zip_Code", "state": "Estado"})
# Garantir que o zip tenha 5 dígitos (zeros à esquerda)
df_map["Zip_Code"] = df_map["Zip_Code"].str.zfill(5)

# ==========================================
# 2. Carregar o arquivo MASTER de Bolsões
# ==========================================
caminho_master = "dados/bolsoes_ipc_zipcode_master.csv"

if not os.path.exists(caminho_master):
    print(f"\n🔴 ERRO: O arquivo {caminho_master} não foi encontrado na pasta 'dados'.")
    sys.exit()
    
print("🧠 Processando Machine Learning para a base Master...")
df = pd.read_csv(caminho_master, dtype={"Zip_Code": str})

# Adicionar o Estado à tabela principal
df = pd.merge(df, df_map, on="Zip_Code", how="left")
df["Estado"] = df["Estado"].fillna("Desconhecido") # Proteção de segurança para CEPs hiper-novos

# ==========================================
# 3. Machine Learning (K-Means)
# ==========================================
features = df[["Densidade_Empresas_10k", "Renda_Media_Domiciliar"]].copy()

# Normalização (equilibra a escala da Renda com a escala da Densidade)
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# Executar o Algoritmo para encontrar 3 perfis de mercado
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df["Cluster_ID"] = kmeans.fit_predict(features_scaled)

# ==========================================
# 4. Rotulagem Estratégica (Ouro, Prata, Bronze)
# ==========================================
medias_cluster = df.groupby("Cluster_ID")["Score_IPC"].mean().sort_values(ascending=False)

mapa_nomes = {
    medias_cluster.index[0]: "1. Alta Prioridade (Ouro)",
    medias_cluster.index[1]: "2. Média Prioridade (Prata)",
    medias_cluster.index[2]: "3. Baixa Prioridade (Bronze)"
}

df["Cluster_Prioridade"] = df["Cluster_ID"].map(mapa_nomes)

# ==========================================
# 5. Limpeza e Ordenação Visual
# ==========================================
colunas_ordem = [
    "Zip_Code", "Estado", "Setor", "Cluster_Prioridade", "Score_IPC", 
    "Qtd_Empresas", "Populacao_Total_18", "Renda_Media_Domiciliar", "Densidade_Empresas_10k"
]
df = df[colunas_ordem]

# Ordenar do Ouro para o Bronze e pelos escores mais altos
df = df.sort_values(by=["Cluster_Prioridade", "Score_IPC"], ascending=[True, False])

# ==========================================
# 6. Salvar as Bases Finais Dinamicamente
# ==========================================
print("\nSalvando as bases clusterizadas de forma tática...")

df.to_csv("dados/clusters_bolsoes_master.csv", index=False)

for setor in df["Setor"].unique():
    df_fatiado = df[df["Setor"] == setor]
    df_fatiado.to_csv(f"dados/clusters_bolsoes_{setor.lower()}.csv", index=False)