# SRAG Analytics Agent 🏥

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 📌 Descrição do Problema

A Síndrome Respiratória Aguda Grave (SRAG) é uma condição crítica de saúde pública que exige monitoramento contínuo para detecção de surtos, avaliação da gravidade e gestão de recursos hospitalares. O volume de dados gerados pelos sistemas de notificação (DATASUS) cria um desafio para extração rápida de insights acionáveis por gestores de saúde. O problema central que este projeto resolve é a necessidade de **agilidade na transformação de dados brutos em inteligência epidemiológica**, permitindo o acompanhamento em tempo real de métricas críticas como mortalidade, ocupação de leitos de UTI e cobertura vacinal.

A solução desenvolvida atua como um **Agente de Inteligência Epidemiológica**, automatizando a ingestão de dados, o cálculo de indicadores chave de desempenho (KPIs) e a geração de relatórios contextuais enriquecidos por notícias recentes e análises via LLM (Large Language Model).

---

##  Solução Desenvolvida

A solução é composta por uma arquitetura modular que inclui:

1.  **Pipeline de Dados (ETL)**: Processamento e limpeza de dados brutos do DATASUS, transformando arquivos CSV em um banco de dados SQLite otimizado.
2.  **Cálculo de Métricas Core**: Implementação de lógica de negócio para calcular taxas de crescimento de casos, mortalidade, ocupação de UTI e vacinação.
3.  **Agente de IA (LangChain)**: Um orquestrador inteligente que combina dados internos com buscas na web (notícias recentes) para gerar relatórios analíticos contextualizados.
4.  **Interface Interativa (Streamlit)**: Um dashboard web responsivo para visualização de dados, tendências temporais e acesso aos relatórios gerados pela IA.

###  Arquitetura da Solução
A arquitetura completa da solução pode ser visualizada no diagrama abaixo:
- [ Diagrama de Arquitetura (PDF)](docs/arquitetura_solucao.pdf)

### Funcionalidades Principais
-   **Monitoramento em Tempo Real**: Métricas atualizadas com base nos últimos dados disponíveis.
-   **Análise Preditiva e Contextual**: Insights gerados por IA correlacionando dados internos com notícias externas.
-   **Visualização de Dados**: Gráficos interativos (Plotly) para análise temporal (diária e mensal) e distribuição geográfica.
-   **Relatórios Automatizados**: Geração de documentos executivos com resumo do cenário atual.

---

## Análise Exploratória de Dados (EDA)

A etapa de EDA foi fundamental para garantir a qualidade e confiabilidade das métricas geradas. As análises detalhadas estão disponíveis no diretório `analise/notebooks/`, com destaque para o notebook `01_eda_inicial.ipynb`.

### Principais Análises Realizadas:
-   **Qualidade dos Dados**: Verificação de completude e consistência das colunas críticas (`DT_NOTIFIC`, `EVOLUCAO`, `UTI`, `VACINA`).
-   **Tratamento de Valores Ausentes (Nulls)**:
    -   Campos de evolução (`EVOLUCAO`) e UTI (`UTI`) exigiram tratamento específico para diferenciar "não informado" de "negativo".
    -   Datas inválidas ou futuras foram filtradas.
-   **Análise Univariada e Bivariada**:
    -   Distribuição temporal dos casos (sazonalidade).
    -   Correlação entre idade, comorbidades e óbito.
    -   Impacto da vacinação na gravidade dos casos (internação em UTI e óbito).
-   **Limpeza e Padronização**: Normalização de nomes de colunas e tipos de dados para garantir consistência no banco de dados SQLite.

---

##  Instalação e Configuração

### Pré-requisitos
-   Python 3.10 ou superior
-   Git

### 1. Clonar o Repositório
```bash
git clone https://github.com/seu-usuario/srag-analytics.git
cd srag-analytics
```

### 2. Configurar Ambiente Virtual
Recomendamos o uso de um ambiente virtual para isolar as dependências do projeto.

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependências
O arquivo `requirements.txt` contém todas as bibliotecas necessárias, incluindo `streamlit`, `pandas`, `plotly`, `langchain`, etc.

```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto baseando-se no exemplo:

```bash
cp .env.example .env
```
Edite o arquivo `.env` inserindo suas chaves de API (ex: OpenAI, Anthropic, Tavily) necessárias para o Agente de IA.

---

## Conteinerização (Docker)

A aplicação está totalmente conteinerizada, facilitando o deploy e garantindo consistência entre ambientes de desenvolvimento e produção.

### Construir a Imagem Docker
```bash
docker build -t srag-analytics .
```

### Executar o Container
Este comando inicia a aplicação na porta 8501:

```bash
docker run -p 8501:8501 srag-analytics
```
Acesse o dashboard em: `http://localhost:8501`

---

## Como Executar Localmente

Para iniciar o dashboard Streamlit fora do container:

```bash
streamlit run app.py
```

Para executar apenas o pipeline de dados e geração de relatório via terminal:
```bash
python run_agent.py --output outputs/relatorios/
```

---

## Estrutura do Projeto

```
srag-analytics/
├── .agent/             # Documentação de workflows e regras do agente
├── agent/              # Código fonte do Agente de IA e Ferramentas
│   ├── tools/          # Ferramentas (Database, News Search)
│   ├── metrics.py      # Lógica de cálculo de KPIs
│   └── report_generator.py # Geração de relatórios
├── analise/            # Notebooks de EDA e exploração
├── app.py              # Ponto de entrada do Dashboard Streamlit
├── components/         # Componentes de UI do Streamlit
├── data/               # Dados brutos e banco de dados SQLite
├── Dockerfile          # Configuração do container
├── requirements.txt    # Dependências do projeto
└── utils/              # Funções utilitárias
```

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.
