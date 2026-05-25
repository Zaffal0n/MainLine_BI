import os
from dotenv import load_dotenv
import requests

load_dotenv()

CENSUS_KEY = os.getenv('CENSUS_API_KEY')
BLS_KEY = os.getenv('BLS_API_KEY')

def testar_credenciais():
    if not CENSUS_KEY:
        print("❌ Erro: CENSUS_API_KEY não encontrada.")
        return
    if not BLS_KEY:
        print("❌ Erro: BLS_API_KEY não encontrada.")
        return
    print("✅ Sucesso! Chaves carregadas de forma segura.")

if __name__ == "__main__":
    testar_credenciais()