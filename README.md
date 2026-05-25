# MainLine: Engenharia de Dados & Inteligência de Mercado para Outbound B2B

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data_Manipulation-150458?logo=pandas)
![Status](https://img.shields.io/badge/Status-Fase_1_Conclu%C3%ADda-brightgreen)

## Visão Geral do Projeto

Este repositório documenta a arquitetura e os scripts de Engenharia de Dados (Data Engineering) do projeto **MainLine** — uma plataforma de aconselhamento financeiro focada em PMEs (Pequenas e Médias Empresas) americanas, especialmente nas verticais de **Transporte e Construção**.

O objetivo técnico principal deste repositório é construir uma pipeline ETL (Extract, Transform, Load) robusta para **reduzir o Custo por Negócio Financiado (CPFD) para menos de US$ 450**, substituindo o gasto massivo em anúncios cegos por uma estratégia cirúrgica de *Cold Emailing* orientada a dados.

A nossa infraestrutura cruza ativamente bases de dados de censos demográficos (bolsões industriais) com registos governamentais em tempo real para mapear leads altamente propensos a necessitar de linhas de crédito.

---

## O Desafio de Negócio (O "Porquê")

Nos EUA, mais de 33 milhões de pequenos negócios (transportadoras, empreiteiros) são rejeitados sistematicamente pelos grandes bancos, caindo nas mãos de corretores de empréstimos predatórios (MCAs). A MainLine atua como um conselheiro honesto, gratuito para a PME. 

O desafio é encontrar exatamente as frotas e empresas de construção que:
1. São pequenas/médias (não possuem acesso a crédito *Enterprise*).
2. Têm a documentação ativa.
3. Estão sediadas em áreas demográficas de rápida expansão (o que gera alta procura por crédito).

Este projeto é o "motor" que filtra milhões de registos inúteis e entrega ao marketing apenas a "mina de ouro".

---

## Arquitetura da Pipeline (ETL)

A fase inicial (atual) deste repositório foca-se na **Vertical de Transporte (Dispatched.finance)**. 

### 1. Ingestão e Filtragem em Origem (Extract)
Consumimos os dados da **API da FMCSA (Federal Motor Carrier Safety Administration)** americana utilizando a biblioteca `requests` e a Socrata Query Language (SoQL).
* Em vez de baixar um *dump* de 3GB, otimizamos o processamento executando o filtro (ICP) diretamente nos servidores do governo:
  * Apenas com **Status Ativo** (`A`).
  * Apenas **Transportadoras Reais** (`CARRIER` = `C`), excluindo corretores.
  * Métrica rigorosa de frota: **Entre 1 e 50 camiões/cavalos mecânicos** (`POWER_UNITS`).
  * Descarte obrigatório de empresas **sem e-mail** registado.

### 2. Higienização Técnica (Transform - Passo 1)
O ficheiro CSV filtrado é processado em memória utilizando o `pandas`.
* Limpeza de aspas literais dos cabeçalhos vindos da API.
* **Harmonização de Chave (O Zip Code):** Remoção de rotas postais estendidas (ZIP+4, ex: `90210-1234`), isolando estritamente os 5 primeiros dígitos e aplicando preenchimento com zeros à esquerda (`.zfill(5)`) para garantir que as chaves coincidam perfeitamente nas fases seguintes.

### 3. O Cruzamento de Inteligência Geográfica (Transform - Passo 2 / LEFT JOIN)
A verdadeira vantagem competitiva do projeto acontece aqui. O script cruza os leads limpos da FMCSA com o nosso **Master Lookup de Demografia de Transporte**.
* **Base Demográfica:** Uma tabela de inteligência que agrupa Zip Codes americanos em *Clusters de Prioridade* (Ouro, Prata e Bronze) com base em métricas censitárias e dados macroeconómicos.
* **Operação:** Realizamos um *Left Join*. 
  * Se o Zip Code da empresa coincidir com um Polo/Bolsão Ouro/Prata/Bronze, ela herda esse rótulo estratégico.
  * Se a empresa estiver fora das áreas mapeadas ativas, ela não é descartada, sendo inteligentemente categorizada como **"Desconhecida"** (gerando um lead de descoberta para campanhas de baixo custo).

### 4. Estruturação do Entregável (Load)
O output final do processo é o ficheiro `fmcsa_leads_clusters.csv`. Um arquivo levíssimo contendo o Identificador do Governo (DOT), contactos completos e validados, tamanho exato da frota e a sua **Prioridade de Cluster**, pronto a ser injetado em ferramentas de *Cold Email Outreach*.

---

## Tecnologias e Ferramentas

* **Python 3.10+**: Linguagem base da orquestração.
* **Pandas**: Para limpeza, *joins* relacionais e manipulação em lote dos CSVs.
* **Requests / Socrata API**: Para consumo eficiente, paginação e *streaming* de dados governamentais massivos.
* **NumPy**: Para manipulação algébrica das chaves.
* **SO (Built-in)**: Para gestão estrutural do sistema de ficheiros (`dados/`, `dados_FMCSA/`).

---

## Estrutura de Ficheiros

```text
/MainLine_Project
│
├── dados/                                   # Bases de dados estratégicas da empresa
│   ├── clusters_bolsoes_transporte.csv      # Base com Score IPC e Clusters Demográficos
│   └── polos_transporte_zipcode.csv         # Polos industriais mapeados
│
├── dados_FMCSA/                             # Zona de tratamento (Landing Zone e Curated)
│   ├── fmcsa_leads_limpos.csv               # Output cru da API Governamental
│   └── fmcsa_leads_clusters.csv             # Ouro: Output Final (O Lead Enriquecido)
│
├── 01_import_fmcsa_api.py                   # Script de consumo automatizado via SODA API
├── 02_limpeza_zip_codes.py                  # Script de Data Cleansing (Hifen e Aspas)
├── 03_left_join_clusters.py                 # O Motor de Inteligência Geográfica
│
├── MainLine_Contexto_Negocio.md             # Regras de Negócio e Tom de Marca
└── README.md                                # Esta documentação
```

---

## Como Executar o Pipeline Localmente

1. Clone o repositório.
2. Crie as pastas `/dados` e `/dados_FMCSA` se elas não existirem no root.
3. Garanta que tem as bases de dados demográficos originais dentro da pasta `/dados`.
4. Instale as dependências: `pip install pandas requests numpy`.
5. Execute o pipeline em sequência lógica:
   ```bash
   # Baixa os leads do governo
   python 01_import_fmcsa_api.py
   
   # Formata e higieniza os dados (Opcional se integrados no mesmo script)
   python 02_limpeza_zip_codes.py
   
   # Faz o Left Join e gera o ficheiro com o Ouro/Prata/Bronze
   python 03_left_join_clusters.py
   ```

---
