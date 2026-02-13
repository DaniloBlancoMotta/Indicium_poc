# SRAG Analytics Agent (PoC)


Sistema inteligente para monitoramento e análise de Síndrome Respiratória Aguda Grave (SRAG) utilizando dados do DATASUS e Inteligência Artificial.

---

##  Descrição do Problema e Contexto

A Síndrome Respiratória Aguda Grave (SRAG) representa um desafio contínuo para a saúde pública, exigindo monitoramento constante e respostas ágeis. Os dados epidemiológicos, embora disponíveis publicamente através do DATASUS (sistema SIVEP-Gripe), apresentam desafios significativos:

1.  **Volume e Complexidade**: Milhares de registros diários com dezenas de variáveis clínicas e demográficas.
2.  **Necessidade de Agilidade**: A identificação de surtos e tendências precisa ser feita em tempo hábil para orientar políticas públicas.
3.  **Processamento Manual**: A análise tradicional depende de processos manuais de limpeza e estruturação de dados, propensos a erros e lentidão.
4.  **Desconexão de Contexto**: Dados isolados sem o contexto de notícias e eventos atuais podem levar a interpretações incompletas.

Este projeto propõe uma **solução automatizada** que ingere dados brutos, calcula métricas epidemiológicas críticas e utiliza um **Agente de IA** para gerar relatórios analíticos contextualizados, integrando dados quantitativos com notícias recentes, permitindo uma tomada de decisão mais informada e rápida.

---

##  Funcionalidades

- **Processamento de Dados**: Pipeline automatizado que transforma CSV bruto do DATASUS em um banco de dados SQLite otimizado.
- **Métricas Chave**: Cálculo preciso de:
  - Taxa de Crescimento de Casos (Mensal)
  - Taxa de Mortalidade
  - Taxa de Ocupação de UTI
  - Status de Vacinação
- **Inteligência Artificial**: Agente autônomo baseado em **Llama 3 (via Groq)** que gera insights e correlações em linguagem natural.
- **Relatórios**: Geração automática de DOIS relatórios distintos (Dataset e Notícias) em formatos **HTML e PDF**.
- **Busca de Notícias**: Monitoramento ativo de portais oficiais (Gov.br, Saúde SP) e imprensa (DuckDuckGo) para contexto atualizado.

## 🛠️ Arquitetura

O projeto segue uma arquitetura modular focada em Clean Code e escalabilidade:

```text
srag-poc/
├── agent/               # Núcleo do Agente Inteligente
│   ├── tools/           # Ferramentas (Banco de Dados, Busca Web)
│   ├── agent.py         # Orquestrador LangChain
│   ├── loader.py        # Pipeline de Dados (ETL)
│   ├── metrics.py       # Motor de Cálculo (Regras de Negócio)
│   └── chart.py         # Visualização de Dados
├── data/                # Armazenamento de Dados
│   ├── raw/             # CSVs Originais
│   ├── processed/       # CSVs Limpos
│   └── database/        # Banco SQLite (srag.db)
├── outputs/             # Relatórios Gerados
├── run_agent.py         # Ponto de Entrada (Entrypoint)
└── requirements.txt     # Dependências
```

## Pré-requisitos

- Python 3.10 ou superior
- Uma chave de API da [Groq](https://console.groq.com/) (Gratuita para teste)
- Dados do DATASUS (Arquivo INFLUD*.csv na pasta `data/raw`)

##  Como Executar

1. **Clone e Instale as Dependências**:
   Recomendamos o uso de um ambiente virtual para isolar as dependências do projeto.
   ```bash
   git clone <repo-url>
   cd srag-poc
   
   # Criar ambiente virtual
   python -m venv .venv
   
   # Ativar ambiente virtual
   # Windows:
   .venv\Scripts\activate
   # Linux/Mac:
   source .venv/bin/activate

   pip install -r requirements.txt
   ```

2. **Configure o Ambiente**:
   Copie o arquivo de exemplo e adicione sua chave API:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env e adicione: GROQ_API_KEY=sua_chave_aqui
   ```

3. **Execute o Agente**:
   ```bash
   python run_agent.py
   ```

4. **Resultado**:
   O sistema irá processar os dados e gerar relatórios na pasta `outputs/relatorios/`:
   - `relatorio_dataset_YYYYMMDD_HHMMSS.pdf` (Análise de Dados)
   - `relatorio_news_YYYYMMDD_HHMMSS.pdf` (Contexto de Notícias)

5. **Interface Gráfica (Dashboard)**:
   Para visualizar os dados em um painel interativo:
   ```bash
   streamlit run app.py
   ```

##  Docker

Para executar a aplicação em um container Docker, siga os passos abaixo:

1. **Construir a Imagem**:
   ```bash
   docker build -t srag-agent .
   ```

2. **Executar o Container**:
   ```bash
   docker run -p 8501:8501 --env-file .env srag-agent
   ```
   Isso iniciará a aplicação e disponibilizará o dashboard na porta 8501.

##  Decisões Técnicas

- **SQLite**: Escolhido para armazenamento local eficiente e suporte a SQL completo sem overhead de servidor.
- **LangChain + Groq**: Combinação para alta performance de inferência (Llama 3 70B) com abstração robusta de ferramentas.
- **Pandas**: Motor de processamento em memória para limpeza e transformação inicial dos dados brutos.
- **xhtml2pdf**: Geração de relatórios PDF a partir de templates HTML/CSS.
- **Tavily API e DuckDuckGo & Scraping**: Coleta de notícias em tempo real sem custos de API proprietária.

## ⚠️ Limitações Conhecidas (PoC)

- O desempenho da geração de PDF pode variar com base na complexidade do HTML.
- O filtro temporal do dataset considera a data mais recente no histórico (2020-2021) para simular cada cenário "em tempo real".

##  Licença

Este projeto é uma Prova de Conceito (PoC) desenvolvida para fins de demonstração técnica.
