# Eleições 2026 — Análise de Dados

Projeto de análise das candidaturas à Presidência da República nas Eleições 2026 utilizando dados públicos disponibilizados pelo Tribunal Superior Eleitoral (TSE).

O objetivo é construir um pipeline reproduzível de dados eleitorais, partindo da ingestão e tratamento dos dados oficiais até análises exploratórias e, em etapas posteriores, técnicas de NLP e Large Language Models (LLMs) aplicadas aos planos de governo.

## Objetivos

O projeto busca explorar diferentes dimensões das candidaturas presidenciais por meio de dados oficiais, incluindo:

- perfil das candidaturas;
- características demográficas e profissionais;
- bens declarados à Justiça Eleitoral;
- dados relacionados às campanhas;
- análise textual dos planos de governo;
- aplicação de NLP, embeddings e LLMs em documentos eleitorais.

O projeto possui caráter exclusivamente analítico e descritivo.

## Fonte dos dados

Os dados são obtidos do Portal de Dados Abertos do Tribunal Superior Eleitoral (TSE).

Nesta etapa são utilizadas principalmente as bases:

- candidatos;
- informações complementares das candidaturas;
- bens declarados pelos candidatos.

Os arquivos originais são obtidos diretamente das fontes oficiais durante o processo de ingestão e não são versionados neste repositório.

## Universo da análise

A análise principal considera somente candidaturas à Presidência cujo campo:

`DS_SITUACAO_JULGAMENTO == "DEFERIDO"`

no snapshot dos dados utilizado.

Registros pendentes, indeferidos ou substituídos são preservados durante o processamento para fins de rastreabilidade, mas não fazem parte do universo analítico principal.

Como os dados eleitorais podem sofrer atualizações, os resultados representam o estado da base oficial no momento de sua coleta.

## Pipeline

O fluxo atual do projeto é:

```text
Portal de Dados Abertos do TSE
            |
            v
        Ingestão
            |
            v
     Dados brutos
            |
            v
 Processamento e validação
            |
            v
   Dados processados
            |
            v
 Análise exploratória (EDA)
            |
            v
      Visualizações
```

As próximas etapas expandirão o pipeline para análise textual dos planos de governo.

## Estrutura do projeto

```text
eleicoes-2026-data-analysis/
|
├── data/
│   ├── raw/
│   └── processed/
|
├── notebooks/
│   └── 01_eda_candidatos.ipynb
|
├── src/
│   ├── ingestion/
│   │   └── tse.py
│   └── processing/
│       ├── candidates.py
│       └── assets.py
|
├── outputs/
│   ├── figures/
│   └── reports/
|
├── README.md
├── requirements.txt
└── .gitignore
```

## Processamento dos dados

### Candidaturas

O pipeline de candidaturas:

1. carrega os dados oficiais do TSE;
2. seleciona os registros referentes ao cargo de Presidente;
3. combina os dados cadastrais com as informações complementares;
4. trata códigos especiais e valores ausentes;
5. valida duplicidades e consistência;
6. identifica candidaturas com registro deferido;
7. gera o dataset utilizado na análise.

Os registros presidenciais completos são mantidos separadamente do dataset analítico para preservar a rastreabilidade do processamento.

### Bens declarados

Os bens declarados são associados às candidaturas por meio do identificador `SQ_CANDIDATO`.

O processamento calcula, entre outras métricas:

- quantidade de bens registrados;
- valor total declarado;
- valor médio dos bens;
- valor mediano;
- maior bem registrado.

A ausência de registros de bens é mantida separada de um valor declarado igual a zero.

Os valores representam bens declarados à Justiça Eleitoral e não devem ser interpretados como uma estimativa independente de patrimônio líquido ou riqueza.

## Análise exploratória

O notebook:

`notebooks/01_eda_candidatos.ipynb`

contém a primeira análise exploratória do projeto.

São avaliados:

- qualidade e completude dos dados;
- idade;
- gênero;
- escolaridade;
- raça/cor autodeclarada;
- ocupação;
- UF de nascimento;
- distribuição dos bens declarados;
- composição dos bens por categoria.

### Alguns resultados do snapshot analisado

O conjunto analítico contém 12 candidaturas com registro deferido.

Entre os resultados observados:

- idade média na data da posse de aproximadamente 59,2 anos;
- mediana de idade de 59 anos;
- 10 das 12 candidaturas possuem ensino superior completo registrado;
- 11 candidaturas possuem registros de bens associados;
- 138 registros individuais de bens foram analisados;
- a distribuição dos valores declarados apresenta forte assimetria;
- o valor mediano declarado é substancialmente inferior ao valor médio.

Esses números descrevem exclusivamente o snapshot utilizado e podem mudar conforme atualizações da base oficial.

## Como executar

### 1. Clonar o repositório

```bash
git clone https://github.com/Juliocesarbs/applied-ai-projects.git
cd applied-ai-projects/eleicoes-2026-data-analysis
```

### 2. Criar o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Executar a ingestão

```bash
python src/ingestion/tse.py
```

### 5. Processar as candidaturas

```bash
python src/processing/candidates.py
```

### 6. Processar os bens

```bash
python src/processing/assets.py
```

### 7. Executar o notebook

```bash
jupyter notebook
```

Abra:

`notebooks/01_eda_candidatos.ipynb`

## Tecnologias

- Python
- Pandas
- Matplotlib
- Requests
- Jupyter Notebook
- Git

## Roadmap

### Concluído

- [x] Estrutura inicial do projeto
- [x] Ingestão de dados oficiais do TSE
- [x] Processamento das candidaturas
- [x] Tratamento da situação de julgamento
- [x] Processamento dos bens declarados
- [x] Validações de qualidade
- [x] Análise exploratória das candidaturas
- [x] Análise inicial dos bens declarados

### Próximas etapas

- [ ] Análise de dados relacionados às campanhas
- [ ] Coleta dos planos de governo
- [ ] Extração e preparação dos documentos
- [ ] Análise textual com NLP
- [ ] TF-IDF e análise de termos
- [ ] Embeddings
- [ ] Clusterização de temas
- [ ] Extração estruturada com LLMs
- [ ] Avaliação das saídas dos modelos
- [ ] Análise comparativa dos temas presentes nos documentos

## Observações

Este projeto utiliza dados públicos oficiais e tem finalidade educacional e analítica.

As análises não representam recomendação, avaliação ou preferência por qualquer candidatura, partido ou proposta política.