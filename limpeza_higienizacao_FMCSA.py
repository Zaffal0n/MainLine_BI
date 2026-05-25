import pandas as pd
import os

# 1. Configuração do Caminho Único
pasta_destino = "dados_FMCSA"

# Criamos a variável única que será usada para ler e sobrescrever
arquivo_alvo = os.path.join(pasta_destino, "fmcsa_leads_limpos.csv")

print(f"Iniciando a higienização direta no ficheiro '{arquivo_alvo}'...")

# 2. Carregar o arquivo original para a memória
try:
    df = pd.read_csv(arquivo_alvo, low_memory=False)
except FileNotFoundError:
    print(f"\n[ERRO] O ficheiro '{arquivo_alvo}' não foi encontrado.")
    print("Certifique-se de que rodou o script de extração antes de iniciar a limpeza.")
    exit()

# --- CORREÇÃO 1: Remover as aspas dos nomes das colunas ---
df.columns = df.columns.str.replace('"', '').str.replace("'", "").str.strip()
print("Cabeçalhos corrigidos com sucesso!")

# --- CORREÇÃO 2: Tratar e separar o phy_zip (ZIP+4 com hífen) ---
df['phy_zip'] = df['phy_zip'].astype(str).str.strip()

# Divide baseado no primeiro hífen
zip_split = df['phy_zip'].str.split('-', n=1, expand=True)

# phy_zip fica só com os 5 dígitos principais
df['phy_zip'] = zip_split[0]

# Cria phy_zip_2 com a extensão de 4 dígitos (se existir)
if zip_split.shape[1] > 1:
    df['phy_zip_2'] = zip_split[1]
else:
    df['phy_zip_2'] = None

# Limpa sujeiras de strings vazias ou 'nan'
df['phy_zip'] = df['phy_zip'].replace(['nan', 'None', ''], None)
df['phy_zip_2'] = df['phy_zip_2'].replace(['nan', 'None', ''], None)

# --- ORGANIZAÇÃO VISUAL: Posicionar phy_zip_2 ao lado de phy_zip ---
colunas_ordenadas = list(df.columns)
if 'phy_zip_2' in colunas_ordenadas:
    colunas_ordenadas.remove('phy_zip_2')
    indice_zip = colunas_ordenadas.index('phy_zip')
    colunas_ordenadas.insert(indice_zip + 1, 'phy_zip_2')
    df = df[colunas_ordenadas]

# 3. A Mágica da Sobrescrição (Overwrite)
print("A guardar alterações no mesmo ficheiro...")
# Ao usar o mesmo 'arquivo_alvo', o Pandas apaga a versão velha e guarda esta limpa
df.to_csv(arquivo_alvo, index=False)

print("\n" + "=" * 60)
print(f"Higienização finalizada! O ficheiro '{arquivo_alvo}' foi SOBRESCRITO com sucesso.")
print(f"Total de registos limpos e prontos para cruzamento: {len(df)}")
print("=" * 60)