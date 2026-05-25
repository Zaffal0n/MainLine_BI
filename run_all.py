import sys
import subprocess

# A ordem exata da sua Esteira de Produção
scripts = [
    "extracao_censo_zipcode.py",       # Fase 1: Extract Demografia
    "extracao_empresas_zbp.py",        # Fase 1: Extract Empresas
    "calculo_ipc_zipcode.py",          # Fase 2: Transform & Cálculo do IPC
    "clusterizacao_zipcode.py",        # Fase 3: IA & Clusterização de Bolsões
    "priorizar_e_mapear_polos.py",     # Fase 3: Ranqueamento de Polos B2B
    "limpeza_e_sincronizacao.py"       # Fase 4: Garantia de Qualidade
]

print("=== INICIANDO A ESTEIRA DE PRODUÇÃO DA MAINLINE ===")

for script in scripts:
    print(f"\n🚀 RODANDO: {script}...")
    
    # Usando o subprocess e o sys.executable garante que ele use EXATAMENTE
    # o mesmo Python (e o mesmo ambiente virtual) que você usa no terminal
    resultado = subprocess.run([sys.executable, script])
    
    # Trava de segurança: Verifica se deu erro
    if resultado.returncode != 0:
        print(f"\n❌ ERRO CRÍTICO: O script '{script}' falhou ou foi interrompido.")
        print("O pipeline foi pausado para evitar dados corrompidos.")
        break

else:
    # Se o loop terminar sem nenhum 'break', exibe a mensagem de sucesso
    print("\n=======================================================")
    print("✅ PIPELINE COMPLETO EXECUTADO COM SUCESSO!")
    print("Todos os dados do Data Warehouse foram atualizados.")
    print("=======================================================")