# MainLine — Projeto de Inteligência de Mercado e Análise Demográfica

**Status:** Planejamento (Dia Zero)
**Objetivo:** Otimizar a alocação de marketing e reduzir o Custo por Negócio Financiado (CPFD) através de modelagem demográfica espacial.

---

## 1. Escopo e Justificativa

Para atingir a meta de escalabilidade mantendo o CPFD estritamente abaixo de US$ 450, a aquisição de clientes não pode depender de testes cegos em plataformas de Ads. 

Este projeto visa mapear a densidade de Pequenas e Médias Empresas (PMEs) e cruzar esses dados com indicadores socioeconômicos. Iniciaremos o escopo pelas duas verticais da Fase 1:
* **Transporte / Logística (Dispatched.finance)**
* **Construção (Drawn.finance)**

A análise permitirá identificar "bolsões" demográficos com alta concentração do público-alvo e alta propensão à necessidade de crédito (ex: áreas com expansão demográfica acelerada demandam mais empreiteiras).

---

## 2. Stack Tecnológica

A arquitetura foi desenhada para garantir pipelines de dados (ETL) robustos e interfaces de visualização estatística altamente interativas:

* **Ingestão e Processamento (ETL):** Python. 
    * *Bibliotecas:* `pandas`, `geopandas` (para tratamento de dados espaciais), `requests` (para consumo das APIs governamentais).
* **Armazenamento (Data Warehouse):** PostgreSQL com extensão PostGIS (ideal para queries geoespaciais) ou Google BigQuery.
* **Modelagem e Inferência Estatística:** R. Utilização de pacotes de estatística espacial para criar clusters demográficos e calcular a propensão a crédito por região.
* **Interface Visual (Dashboard Interativo):** R usando o pacote Shiny. O Shiny permitirá que a equipe de negócios interaja com os dados de forma dinâmica (ex: ajustando pesos de variáveis demográficas e visualizando o recálculo do mapa de calor em tempo real).

---

## 3. Fontes de Dados

* **US Census Bureau (API):** Dados da *American Community Survey (ACS)* para extração de variáveis demográficas (crescimento populacional, renda, mobilidade).
* **Bureau of Labor Statistics / Census Business Builder:** Dados baseados em códigos NAICS para identificar a densidade de registros de empresas de transporte (ex: NAICS 484) e construção (ex: NAICS 23).

---

## 4. Roadmap de Implementação

### Fase 1: Ingestão e Pipelines ETL (Semanas 1-2)
* Configurar credenciais de acesso às APIs do governo americano.
* Desenvolver scripts em Python para extração de dados brutos.
* Estruturar o pipeline de ETL para limpar, normalizar e unificar as bases de dados empresariais e demográficas na mesma granularidade geográfica (ex: Zip Code ou County).
* *Entregável:* Data warehouse populado com a base histórica inicial.

### Fase 2: Inferência Estatística e Modelagem (Semanas 3-4)
* Desenvolver o **Índice de Propensão a Crédito (IPC)**, aplicando probabilidade e estatística inferencial para ponderar variáveis como densidade de frotas versus acesso a polos bancários tradicionais.
* Aplicar algoritmos de clusterização para segmentar o território americano em zonas de prioridade de aquisição.
* *Entregável:* Tabela final com escores de prioridade por código postal.

### Fase 3: Desenvolvimento da Interface Visual (Semanas 5-6)
* Construir a aplicação web em R (Shiny) consumindo a base de dados modelada.
* Implementar filtros reativos por setor (Construção vs. Transporte).
* Criar funcionalidade de exportação de listas de Zip Codes otimizados para subida direta no Meta Ads e Google Ads.
* *Entregável:* Dashboard Shiny em produção para uso da equipe de performance.

### Fase 4: Feedback Loop e Otimização Contínua (Ongoing)
* Integrar os dados de Custo de Aquisição (CAC) real gerados pelas campanhas de marketing de volta ao pipeline de dados.
* Recalibrar o modelo estatístico periodicamente para garantir que a indicação de prioridade geográfica maximize a conversão e mantenha o unit economics saudável.

---
*Fim do documento.*