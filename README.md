# MainLine: Engenharia de Dados & Inteligência de Mercado B2B

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Manipulation-150458?logo=pandas)
![Scikit-Learn](https://img.shields.io/badge/Scikit_Learn-Machine_Learning-F7931E?logo=scikit-learn)
![Status](https://img.shields.io/badge/Status-Em_Produ%C3%A7%C3%A3o-brightgreen)

## Visão Geral do Projeto

Este repositório documenta a arquitetura avançada de **Engenharia de Dados e Machine Learning** do projeto **MainLine** — uma plataforma de aconselhamento de capital focada em PMEs americanas (especialmente nas verticais de Transporte e Construção).

**O Desafio de Negócio:** Reduzir o Custo por Negócio Financiado (CPFD) para menos de US$ 450. Em vez de depender de testes A/B caros em Ads, a MainLine utiliza dados espaciais e demográficos para "caçar" frotas e construtoras de alta propensão a crédito antes mesmo de elas pesquisarem por empréstimos.

## Arquitetura do Sistema (Dual Engine)

O pipeline foi desenhado em dois "motores" que operam em paralelo e culminam num cruzamento de alto valor (*Left Join* Espacial).

### Motor 1: Inteligência Demográfica e Machine Learning (O Mapa)
Responsável por consumir APIs do Censo dos EUA e modelar o mercado.
1. **Ingestão (Extract):** Consumo das APIs do US Census Bureau (ACS para Renda/População e CBP para contagem de empresas por setor NAICS).
2. **Transformação de Negócio:** Cálculo do **Score IPC** (Índice de Potencial de Crédito) cruzando densidade empresarial com renda domiciliária.
3. **Machine Learning:** Algoritmo **K-Means** (via Scikit-Learn) que agrupa os CEPs (Zip Codes) em Clusters Estratégicos: Ouro (Alta Prioridade), Prata e Bronze.
4. **Data Cleansing:** Scripts de salvaguarda que tratam CEPs órfãos, imputam condados em falta e garantem que nenhuma "mina de ouro" seja perdida por falha de formatação.

### Motor 2: Pipeline de Ingestão de Leads Governamentais (Os Alvos)
Responsável por puxar empresas reais que se enquadrem no ICP (Ideal Customer Profile).
1. **Extração Cirúrgica (SoQL):** Download automatizado da API da FMCSA (Federal Motor Carrier Safety Administration). O processamento é feito *Server-Side*, baixando apenas empresas ativas, reais (Carriers), com 1 a 50 frotas e e-mail validado.
2. **Higienização:** Limpeza de ruídos governamentais (aspas literais, tratamento do ZIP+4 para Zip Code padrão de 5 dígitos).

### A Fusão (Enriquecimento de Outbound)
O ficheiro da FMCSA é cruzado (`Left Join`) com os Clusters Demográficos gerados pelo Machine Learning. O entregável final é uma lista limpa de PMEs de transporte enriquecida com a tag (Ouro/Prata/Bronze) pronta para injeção em ferramentas automáticas de *Cold Emailing*.

---

## Estrutura de Arquivos e Módulos

### 1. Orquestração e Setup
* `run_all.py`: O "Maestro". Um script subprocess que roda toda a esteira de produção (Fase 1 à Fase 4) em sequência e com travas de segurança.
* `extracao_empresas_cbp.py`: Arquivo de configuração (Single Source of Truth) contendo os códigos NAICS dos setores alvo.

### 2. Motor Demográfico (Censo & ML)
* `ingestao_censo.py`: Validador de chaves de API e variáveis de ambiente.
* `extracao_censo_zipcode.py`: Pipeline de extração de dados populacionais e de renda (ACS).
* `extracao_empresas_zbp.py`: Pipeline de extração de densidade de empresas (CBP).
* `calculo_ipc_zipcode.py`: O coração matemático do projeto. Une as bases e gera o Score IPC.
* `modelagem_clusters.py` & `clusterizacao_zipcode.py`: Pipeline de Machine Learning (K-Means) para ranqueamento e tagueamento geográfico.
* `priorizar_e_mapear_polos.py`: Lógica de decis para separar "Polos Industriais" puros de "Bolsões Residenciais".
* `limpeza_e_sincronizacao.py` & `erros.py`: Auditoria e salvaguarda da base de dados (Data Quality).

### 3. Motor de Ingestão de Leads (Outbound FMCSA)
* `import_FMCSA_db.py`: Ingestão *Streamada* via SODA API (Socrata) aplicando filtros pesados de negócio.
* `limpeza_higienizacao_FMCSA.py`: Tratamento de strings e padronização da chave primária (Zip Code).

---

## Como Executar a Esteira de Produção

1. Clone o repositório e crie seu arquivo `.env` com `CENSUS_API_KEY` e `BLS_API_KEY`.
2. Instale as dependências:
   ```bash
   pip install pandas requests numpy scikit-learn python-dotenv
   ```
3. Rode o pipeline integrado do Motor Demográfico:
   ```bash
   python run_all.py
   ```
4. Baixe e higienize os leads ativos do governo:
   ```bash
   python import_FMCSA_db.py
   python limpeza_higienizacao_FMCSA.py
   ```

---