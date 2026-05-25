import pandas as pd
import os
import numpy as np

# 1. Configuração dos caminhos das pastas e arquivos
pasta_fmcsa = "dados_FMCSA"
pasta_dados = "dados"

# Ficheiros de entrada
arquivo_fmcsa = os.path.join(pasta_fmcsa, "fmcsa_leads_limpos.csv")
arquivo_bolsoes = os.path.join(pasta_dados, "clusters_bolsoes_transporte.csv")
arquivo_polos = os.path.join(pasta_dados, "polos_transporte_zipcode.csv")

# Ficheiro de saída
arquivo_saida = os.path.join(pasta_fmcsa, "fmcsa_leads_clusters.csv")

print("Iniciando a fase de Inteligência Geográfica (Left Join)...")

# 2. Carregamento dos dados
try:
    df_fmcsa = pd.read_csv(arquivo_fmcsa, low_memory=False)
    df_bolsoes = pd.read_csv(arquivo_bolsoes, low_memory=False)
    df_polos = pd.read_csv(arquivo_polos, low_memory=False)
except FileNotFoundError as e:
    print(f"\n[ERRO] Ficheiro não encontrado: {e}")
    print("Certifique-se de que as pastas 'dados' e 'dados_FMCSA' e os ficheiros existem.")
    exit()

# 3. Função inteligente para limpar e padronizar Zip Codes (5 dígitos)
def padronizar_zip(valor):
    if pd.isna(valor):
        return ""
    # Converte para string e limpa espaços
    txt = str(valor).strip()
    # Se o Pandas leu como número decimal (ex: 12345.0), tira o .0
    if txt.endswith('.0'):
        txt = txt[:-2]
    # Ignora valores nulos em texto
    if txt.lower() in ['nan', 'none', '']:
        return ""
    # Preenche com zeros à esquerda para ter exatamente 5 dígitos
    return txt.zfill(5)

# 4. Aplicar a padronização em todas as tabelas
print("A padronizar e limpar todos os Zip Codes (preenchendo zeros à esquerda)...")
df_fmcsa['phy_zip'] = df_fmcsa['phy_zip'].apply(padronizar_zip)
df_bolsoes['Zip_Code'] = df_bolsoes['Zip_Code'].apply(padronizar_zip)
df_polos['Zip_Code'] = df_polos['Zip_Code'].apply(padronizar_zip)

# 5. Criar a "Super Tabela de Consulta" (Master Lookup)
# Pegamos só as colunas que importam de cada base e juntamos tudo numa só
lookup_bolsoes = df_bolsoes[['Zip_Code', 'Cluster_Prioridade']].copy()
lookup_polos = df_polos[['Zip_Code', 'Cluster_Prioridade']].copy()

# Concatenamos e removemos duplicados (caso um ZIP esteja nas duas tabelas)
df_lookup_master = pd.concat([lookup_bolsoes, lookup_polos]).drop_duplicates(subset=['Zip_Code'])

# 6. O GRANDE CRUZAMENTO (Left Join)
print("A cruzar a base governamental com a sua base demográfica...")
df_final = pd.merge(
    df_fmcsa, 
    df_lookup_master, 
    how='left', 
    left_on='phy_zip', 
    right_on='Zip_Code'
)

# 7. Regra de Negócio: Tratamento dos não identificados
# Onde a coluna 'Cluster_Prioridade' ficou vazia (NaN) após o cruzamento, marcamos como Desconhecida
df_final['Cluster_Prioridade'] = df_final['Cluster_Prioridade'].fillna('Desconhecida')

# Limpeza: Podemos remover a coluna duplicada 'Zip_Code' (já que temos a 'phy_zip')
if 'Zip_Code' in df_final.columns:
    df_final = df_final.drop(columns=['Zip_Code'])

# 8. Exportação do ficheiro enriquecido
print("A gravar o ficheiro final...")
df_final.to_csv(arquivo_saida, index=False)

# Validações Finais e Resumo
total_linhas = len(df_final)
total_mapeadas = len(df_final[df_final['Cluster_Prioridade'] != 'Desconhecida'])
total_desconhecidas = len(df_final[df_final['Cluster_Prioridade'] == 'Desconhecida'])

print("\n" + "=" * 60)
print(f"Cruzamento concluído com sucesso! Ficheiro salvo em: '{arquivo_saida}'")
print(f"Total de Leads Processados: {total_linhas}")
print(f"✅ Leads com Cluster Mapeado (Bolsões/Polos): {total_mapeadas}")
print(f"⚠️ Leads Desconhecidos (Fora da base): {total_desconhecidas}")
print("=" * 60)