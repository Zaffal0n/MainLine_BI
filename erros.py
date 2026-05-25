import pandas as pd

# Carregar o seu arquivo Master (ajuste o nome se necessário)
df = pd.read_csv("dados/clusters_bolsoes_master.csv", dtype={"Zip_Code": str})

# Filtrar apenas os desconhecidos
desconhecidos = df[df["Estado"] == "Desconhecido"]

print(f"Total de CEPs desconhecidos: {len(desconhecidos)}")
print("Lista dos primeiros CEPs com problema:")
print(desconhecidos[["Zip_Code", "Qtd_Empresas"]].head(10))