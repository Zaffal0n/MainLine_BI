import pandas as pd
import os
import glob

# A Bomba Nuclear da Limpeza de Strings
def limpar_zipcode(coluna):
    return coluna.astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.zfill(5)

def limpeza_final_dados():
    print("🧹 Iniciando Preenchimento Focado em Cidades e Condados...")
    
    frames_resgate = []
    
    # 1. PLANO A: Kaggle (Forte em Condados e Estados)
    caminho_kaggle = "dados/us_zip_fips_county.csv"
    if os.path.exists(caminho_kaggle):
        df_k = pd.read_csv(caminho_kaggle, dtype={"Zip Code": str}, encoding='latin1', low_memory=False)
        df_k["Zip_Code"] = limpar_zipcode(df_k["Zip Code"])
        
        df_k = df_k.rename(columns={
            "State Abrv": "Ref_Estado",
            "County Name": "Ref_county"
        })
        
        frames_resgate.append(df_k[["Zip_Code", "Ref_Estado", "Ref_county"]])

    # 2. PLANO B: Zipcodes original (Forte em Cidades)
    caminho_mapa = "dados/zipcodes.csv"
    if os.path.exists(caminho_mapa):
        df_m = pd.read_csv(caminho_mapa, dtype=str, low_memory=False)
        
        # Identifica a coluna correta de Zip Code
        col_zip = "zip_code" if "zip_code" in df_m.columns else "zipcode"
        if col_zip in df_m.columns:
            df_m["Zip_Code"] = limpar_zipcode(df_m[col_zip])
        
        # Renomeia as colunas para o nosso padrão de resgate
        df_m = df_m.rename(columns={
            "state": "Ref_Estado",
            "city": "Ref_city",
            "county": "Ref_county"
        })
        
        # Pega apenas as colunas que realmente existem no arquivo para não dar erro
        cols_existentes = ["Zip_Code"] + [c for c in ["Ref_Estado", "Ref_city", "Ref_county"] if c in df_m.columns]
        frames_resgate.append(df_m[cols_existentes])

    # 3. Criar o SUPER DICIONÁRIO
    if frames_resgate:
        df_resgate = pd.concat(frames_resgate, ignore_index=True)
        # O pulo do gato: Agrupa por Zip Code e pega a primeira informação válida que encontrar (juntando o melhor dos 2 ficheiros!)
        df_resgate = df_resgate.groupby("Zip_Code", as_index=False).first()
    else:
        df_resgate = None

    # 4. Varrer TODOS os ficheiros CSV da pasta dados
    arquivos = glob.glob("dados/*.csv")
    
    for f in arquivos:
        if any(x in f for x in ["zipcodes.csv", "us_zip_fips_county.csv"]):
            continue
            
        try:
            # Lemos apenas o Zip_Code como string para não quebrar a matemática
            df = pd.read_csv(f, dtype={"Zip_Code": str}, low_memory=False) 
            
            if "Zip_Code" in df.columns:
                print(f"🛰️ Reparando e Preenchendo: {os.path.basename(f)}")
                
                # --- GARANTIA ---
                # Garante que as colunas de cidade e condado existam ANTES de tirar a Foto Inicial
                colunas_alvo = ["Estado", "county", "city"]
                for col in colunas_alvo:
                    if col not in df.columns:
                        df[col] = "Desconhecido"
                
                # A Foto Inicial (O Molde Fixo)
                colunas_originais = df.columns.tolist()
                
                df["Zip_Code"] = limpar_zipcode(df["Zip_Code"])
                
                # O Grande Cruzamento
                if df_resgate is not None:
                    df = pd.merge(df, df_resgate, on="Zip_Code", how="left")
                    
                    mapeamentos = {
                        "Estado": "Ref_Estado",
                        "county": "Ref_county",
                        "city": "Ref_city"
                    }
                    
                    for col_alvo, col_ref in mapeamentos.items():
                        if col_alvo in df.columns and col_ref in df.columns:
                            df[col_alvo] = df[col_alvo].astype(object)
                            # Se estiver vazio ou "Desconhecido", injetamos o dado real!
                            mask = (df[col_alvo] == "Desconhecido") | (df[col_alvo].isna()) | (df[col_alvo] == "") | (df[col_alvo].astype(str).str.strip() == "")
                            df.loc[mask, col_alvo] = df.loc[mask, col_ref]
                
                # --- GUILHOTINA ---
                if "Estado" in df.columns:
                    df = df[df["Estado"] != "Desconhecido"]
                    df = df.dropna(subset=["Estado"])
                
                # --- PREENCHIMENTO SEGURO ---
                for col in colunas_alvo:
                    if col in df.columns:
                        df[col] = df[col].fillna("Desconhecido")
                        
                # --- A MÁGICA UNIVERSAL PARA O 'COUNTY' ---
                if "county" in df.columns:
                    # Remove "County" do final, ignorando espaços
                    df["county"] = df["county"].astype(str).str.replace(r'(?i)\s*county\s*$', '', regex=True).str.strip()
                    df.loc[df["county"] == "", "county"] = "Desconhecido"
                
                # Retorna ao molde original e salva (Adeus latitude e longitude forçadas!)
                df = df[colunas_originais]
                df.to_csv(f, index=False)
                
        except Exception as e:
            print(f"⚠️ Erro ao processar {os.path.basename(f)}: {e}")

    print("\n✅ Reparo concluído com sucesso!")

if __name__ == "__main__":
    limpeza_final_dados()