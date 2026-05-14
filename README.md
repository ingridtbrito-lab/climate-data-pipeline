# Climate Data Pipeline 🌦️

Pipeline de extração, análise e modelagem de dados climáticos brasileiros com Python.

## Sobre o projeto

Este projeto coleta dados climáticos públicos do INMET (Instituto Nacional de Meteorologia),
realiza tratamento, análise exploratória e modelagem estatística dos dados,
com foco em temperatura, precipitação e outros indicadores meteorológicos brasileiros.

## Estrutura

climate-data-pipeline/
│
├── data/               # Dados brutos e processados
├── notebooks/          # Análises em Jupyter Notebook
├── src/                # Scripts Python
├── requirements.txt    # Dependências do projeto
└── README.md

## Tecnologias

- Python 3.14
- Pandas
- Matplotlib / Seaborn
- Scikit-learn
- Jupyter Notebook

## Como executar

```bash
pip install -r requirements.txt
jupyter notebook
```

## Fonte dos dados

INMET — Instituto Nacional de Meteorologia
https://portal.inmet.gov.br/dadoshistoricos