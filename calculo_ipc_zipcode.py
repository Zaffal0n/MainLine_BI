import os
import pandas as pd

def calcular_ipc_e_polos():
    print("Iniciando o Merge de Duas Vias (Bolsões + Polos Industriais)...")
    
    os.makedirs("dados", exist_ok=True)
    
    try:
        # 1. Carregar os dados
        df_empresas = pd.read_csv("dados/base_empresas_zipcode.csv", dtype={"Zip_Code": str})
        df_demo = pd.read_csv("dados/base_demografica_zipcode.csv", dtype={"Zip_Code": str})
        
        # 2. Fazer o Merge (A grande fusão)
        df_completo = pd.merge(df_empresas, df_demo, on="Zip_Code", how="inner")
        
        # ==========================================
        # VIA 1: Polos Industriais Puros 
        # ==========================================
        filtro_polos = (df_completo["Populacao_Total_18"] == 0) & (df_completo["Qtd_Empresas"] >= 5)
        df_polos = df_completo[filtro_polos].copy()
        
        # Limpando a estética dos Polos. 
        df_polos.loc[df_polos["Renda_Media_Domiciliar"] < 0, "Renda_Media_Domiciliar"] = 0
        df_polos = df_polos.sort_values(by=["Setor", "Qtd_Empresas"], ascending=[False, False])
        
        # ==========================================
        # VIA 2: Bolsões Demográficos (O fluxo normal do IPC)
        # ==========================================
        filtro_bolsoes = (df_completo["Populacao_Total_18"] > 0) & (df_completo["Renda_Media_Domiciliar"] > 0)
        df_bolsoes = df_completo[filtro_bolsoes].copy()
        
        # 3. Matemática do IPC (Aplicada APENAS aos Bolsões limpos)
        df_bolsoes["Densidade_Empresas_10k"] = (df_bolsoes["Qtd_Empresas"] / df_bolsoes["Populacao_Total_18"]) * 10000
        df_bolsoes["Score_IPC"] = df_bolsoes["Densidade_Empresas_10k"] * (df_bolsoes["Renda_Media_Domiciliar"] / 10000)
        
        # Limpar números e ordenar pelos "Ouros"
        df_bolsoes = df_bolsoes.round(2)
        df_bolsoes = df_bolsoes.sort_values(by=["Setor", "Score_IPC"], ascending=[True, False])
        
        # 4. Salvar os resultados DINAMICAMENTE
        print("Salvando as bases estratégicas...")
        
        # Salva os arquivos Master
        df_polos.to_csv("dados/polos_industriais_zipcode_master.csv", index=False)
        df_bolsoes.to_csv("dados/bolsoes_ipc_zipcode_master.csv", index=False)
        
        # Fatiar e salvar por setor automaticamente
        for setor in df_bolsoes["Setor"].unique():
            # Bolsoes
            df_b = df_bolsoes[df_bolsoes["Setor"] == setor]
            df_b.to_csv(f"dados/bolsoes_{setor.lower()}_zipcode.csv", index=False)
            # Polos
            df_p = df_polos[df_polos["Setor"] == setor]
            df_p.to_csv(f"dados/polos_{setor.lower()}_zipcode.csv", index=False)

        print("✅ Base de IPC e Polos separada e salva com sucesso!")

    # ====== AQUI ESTÁ A CORREÇÃO (O BLOCO EXCEPT) ======
    except Exception as e:
        print(f"❌ Erro ao calcular o IPC: {e}")

if __name__ == "__main__":
    calcular_ipc_e_polos()