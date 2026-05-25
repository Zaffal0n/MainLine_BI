import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Garante que a pasta dados existe para salvar os gráficos
os.makedirs("dados", exist_ok=True)

# --- FUNÇÃO 1: TRANSPORTE (Dispatched.finance) ---
def criar_clusters_transporte():
    print("Iniciando Machine Learning para a vertical de TRANSPORTES...")
    try:
        # 1. Carregar os dados
        df = pd.read_csv("dados/base_ipc_transporte.csv")

        # 2. Selecionar e Escalar as variáveis
        features = df[['Densidade_Empresas_10k', 'Renda_Media_Domiciliar']]
        scaler = StandardScaler()
        features_escaladas = scaler.fit_transform(features)

        # 3. Aplicar K-Means
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        df['Cluster'] = kmeans.fit_predict(features_escaladas)

        # 4. Nomear Clusters por performance (Média do Score_IPC)
        medias = df.groupby('Cluster')['Score_IPC'].mean().sort_values(ascending=False)
        mapeamento = {
            medias.index[0]: "1. Alta Prioridade (Ouro)",
            medias.index[1]: "2. Média Prioridade (Prata)",
            medias.index[2]: "3. Baixa Prioridade (Bronze)"
        }
        df['Perfil_Mercado'] = df['Cluster'].map(mapeamento)

        # 5. Salvar CSV
        df = df.sort_values(by='Score_IPC', ascending=False)
        df.to_csv("dados/clusters_transporte.csv", index=False)

        # 6. Gerar Gráfico
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df, x='Renda_Media_Domiciliar', y='Densidade_Empresas_10k', 
                        hue='Perfil_Mercado', palette=['gold', 'silver', '#cd7f32'], s=100)
        plt.title('Clusters de Mercado: Dispatched.finance (Transportes)')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.savefig("dados/mapa_clusters_transporte.png")
        plt.close() # Fecha a figura para não sobrepor no próximo gráfico
        
        print("✅ Vertical de Transporte concluída com sucesso.")
    except Exception as e:
        print(f"❌ Erro no Transporte: {e}")

# --- FUNÇÃO 2: CONSTRUÇÃO (Drawn.finance) ---
def criar_clusters_construcao():
    print("Iniciando Machine Learning para a vertical de CONSTRUÇÃO...")
    try:
        # 1. Carregar os dados
        df = pd.read_csv("dados/base_ipc_construcao.csv")

        # 2. Selecionar e Escalar as variáveis
        features = df[['Densidade_Empresas_10k', 'Renda_Media_Domiciliar']]
        scaler = StandardScaler()
        features_escaladas = scaler.fit_transform(features)

        # 3. Aplicar K-Means
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        df['Cluster'] = kmeans.fit_predict(features_escaladas)

        # 4. Nomear Clusters por performance
        medias = df.groupby('Cluster')['Score_IPC'].mean().sort_values(ascending=False)
        mapeamento = {
            medias.index[0]: "1. Alta Prioridade (Ouro)",
            medias.index[1]: "2. Média Prioridade (Prata)",
            medias.index[2]: "3. Baixa Prioridade (Bronze)"
        }
        df['Perfil_Mercado'] = df['Cluster'].map(mapeamento)

        # 5. Salvar CSV
        df = df.sort_values(by='Score_IPC', ascending=False)
        df.to_csv("dados/clusters_construcao.csv", index=False)

        # 6. Gerar Gráfico (Cores diferentes para diferenciar)
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df, x='Renda_Media_Domiciliar', y='Densidade_Empresas_10k', 
                        hue='Perfil_Mercado', palette=['orange', 'gray', '#cd7f32'], s=100)
        plt.title('Clusters de Mercado: Drawn.finance (Construção)')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.savefig("dados/mapa_clusters_construcao.png")
        plt.close()
        
        print("✅ Vertical de Construção concluída com sucesso.")
    except Exception as e:
        print(f"❌ Erro na Construção: {e}")

# --- BLOCO PRINCIPAL ---
if __name__ == "__main__":
    print("=== MAINLINE: PIPELINE DE MODELAGEM E CLUSTERIZAÇÃO ===\n")
    criar_clusters_transporte()
    criar_clusters_construcao()
    print("\n=== TODOS OS MODELOS FORAM PROCESSADOS ===")