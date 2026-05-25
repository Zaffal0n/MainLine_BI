import requests
import os

# 1. A sua URL exata (com a query completa e o LIMIT 2000000)
url_fmcsa = (
    "https://data.transportation.gov/resource/az4n-8mr2.csv?$query=SELECT%0A%20%20"
    "%60dot_number%60%2C%0A%20%20%60status_code%60%2C%0A%20%20%60carship%60%2C%0A%20%20"
    "%60power_units%60%2C%0A%20%20%60email_address%60%2C%0A%20%20%60phone%60%2C%0A%20%20"
    "%60cell_phone%60%2C%0A%20%20%60company_officer_1%60%2C%0A%20%20%60legal_name%60%2C%0A%20%20"
    "%60dba_name%60%2C%0A%20%20%60phy_zip%60%2C%0A%20%20%60phy_state%60%2C%0A%20%20"
    "%60phy_city%60%0AWHERE%0A%20%20%60power_units%60%20BETWEEN%20%221%22%20AND%20%2250%22%0A%20%20"
    "AND%20caseless_eq(%60status_code%60%2C%20%22A%22)%0A%20%20AND%20caseless_contains(%60carship%60%2C%20%22C%22)%0A%20%20"
    "AND%20%60email_address%60%20IS%20NOT%20NULL%0A%20%20AND%20(%60phy_country%60%20%3D%20%22US%22)%0ALIMIT%202000000"
)

# 2. O nome do arquivo que será salvo no seu computador
# 1. Defina a pasta
pasta_destino = "dados_FMCSA"
os.makedirs(pasta_destino, exist_ok=True) # Cria a pasta automaticamente

# 2. Defina o caminho completo do arquivo
arquivo_destino = os.path.join(pasta_destino, "fmcsa_leads_limpos.csv")

print("Iniciando a extração do governo americano (Teste de Limite Único)...")
print("Isso pode levar alguns minutos. Por favor, aguarde...")

try:
    # 3. Fazendo a requisição com stream=True para proteger a memória RAM
    with requests.get(url_fmcsa, stream=True) as resposta:
        
        # Verifica se o servidor recusou ou deu timeout (Erro 4xx ou 5xx)
        resposta.raise_for_status()
        
        # 4. Gravando no disco em blocos de 8MB (8192 * 1024 bytes)
        with open(arquivo_destino, 'wb') as arquivo:
            for pedaco in resposta.iter_content(chunk_size=8192 * 1024):
                arquivo.write(pedaco)
                
    print(f"\nSucesso absoluto! O arquivo '{arquivo_destino}' foi baixado e salvo.")

except requests.exceptions.Timeout:
    print("\n[ERRO] O servidor do governo demorou muito para responder (Timeout). Precisaremos usar o script de Paginação.")
except requests.exceptions.RequestException as e:
    print(f"\n[ERRO] Falha na conexão com a API: {e}")