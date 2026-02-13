---
description: AI Engineer Method
---

SRAG Analytics Agent - Workflow Rules

## REGRAS GERAIS DO PROJETO

### R001: Estrutura de Diretórios
- DEVE seguir a estrutura modular definida
- DEVE separar análise exploratória (`analise/`) do código de produção (`agent/`)
- DEVE manter dados brutos separados de dados processados
- NÃO DEVE misturar notebooks com código de produção

### R002: Gestão de Dependências
- DEVE usar `requirements.txt` para todas as dependências
- DEVE fixar versões principais (pandas, langchain, etc.)
- DEVE usar ambiente virtual Python (venv)
- DEVE documentar versão mínima do Python (3.10+)

### R003: Configuração e Segurança
- DEVE armazenar API keys em arquivo `.env`
- DEVE incluir `.env.example` com variáveis necessárias
- DEVE adicionar `.env` ao `.gitignore`
- NÃO DEVE commitar credenciais ou API keys

---

## FASE 1: PREPARAÇÃO DE DADOS

### R100: Exploração de Dados
- DEVE realizar exploração em Jupyter Notebooks
- DEVE documentar todas as análises exploratórias
- DEVE identificar e documentar problemas de qualidade
- DEVE estar em `analise/notebooks/`
- NÃO DEVE processar dados diretamente nos notebooks

### R101: Seleção de Colunas
- DEVE selecionar APENAS colunas necessárias para as métricas:
  - Data de notificação/internação (obrigatória)
  - Evolução do caso (obrigatória)
  - Status UTI (obrigatória)
  - Status de vacinação (obrigatória)
  - Data de óbito (se disponível)
  - Campos demográficos (opcional)
- NÃO DEVE carregar todas as ~100 colunas

### R102: Limpeza de Dados
- DEVE converter datas para formato datetime
- DEVE tratar valores ausentes de forma documentada
- DEVE remover registros sem data de notificação
- DEVE filtrar período: últimos 13 meses
- DEVE validar integridade referencial
- DEVE salvar em `data/processed/srag_clean.csv`

### R103: Banco de Dados
- DEVE usar SQLite para armazenamento
- DEVE criar índices em colunas de data
- DEVE normalizar estrutura quando apropriado
- DEVE documentar schema no código
- DEVE salvar em `data/database/srag.db`

---

## FASE 2: DESENVOLVIMENTO CORE

### R200: Cálculo de Métricas
- DEVE implementar em `agent/metrics.py`
- DEVE calcular EXATAMENTE 4 métricas:
  1. Taxa de aumento de casos
  2. Taxa de mortalidade
  3. Taxa de ocupação de UTI
  4. Taxa de vacinação da população

#### R201: Taxa de Aumento de Casos
- DEVE comparar últimos 30 dias vs 30 dias anteriores
- DEVE retornar percentual de variação
- DEVE incluir valores absolutos (casos atuais e anteriores)
- Fórmula: `((casos_30d - casos_30d_ant) / casos_30d_ant) * 100`

#### R202: Taxa de Mortalidade
- DEVE calcular: `(total_óbitos / total_casos) * 100`
- DEVE considerar apenas casos com evolução definida
- DEVE filtrar período relevante
- DEVE tratar casos sem evolução como NaN

#### R203: Taxa de Ocupação de UTI
- DEVE calcular: `(casos_uti / total_casos) * 100`
- DEVE considerar apenas registros com informação de UTI
- DEVE distinguir entre "não informado" e "não foi para UTI"

#### R204: Taxa de Vacinação
- DEVE calcular: `(casos_vacinados / total_casos) * 100`
- DEVE considerar esquema vacinal completo
- DEVE tratar valores ausentes adequadamente
- PODE incluir dose de reforço se disponível

### R210: Geração de Gráficos
- DEVE implementar em `agent/charts.py`
- DEVE gerar EXATAMENTE 2 gráficos obrigatórios

#### R211: Gráfico de Casos Diários
- DEVE mostrar últimos 30 dias
- DEVE usar gráfico de linha (line chart)
- DEVE incluir labels nos eixos
- DEVE salvar como PNG ou retornar base64
- Eixo X: Data (DD/MM)
- Eixo Y: Número de casos

#### R212: Gráfico de Casos Mensais
- DEVE mostrar últimos 12 meses
- DEVE usar gráfico de barras (bar chart)
- DEVE incluir labels nos eixos
- DEVE salvar como PNG ou retornar base64
- Eixo X: Mês/Ano (MM/YYYY)
- Eixo Y: Número de casos

### R220: Validação
- DEVE validar todas as métricas em notebooks antes de produção
- DEVE incluir testes de sanidade (valores entre 0-100 para %)
- DEVE comparar com fontes oficiais quando possível
- DEVE documentar suposições e limitações

---

## FASE 3: DESENVOLVIMENTO DO AGENTE

### R300: Arquitetura do Agente
- DEVE usar LangChain como framework
- DEVE usar Claude (Anthropic) como LLM principal
- DEVE implementar pattern de Tools
- DEVE estar em `agent/agent.py`

### R301: Database Tool
- DEVE implementar em `agent/tools/database_tool.py`
- DEVE fornecer métodos para:
  - Obter todas as 4 métricas
  - Obter dados para gráfico diário
  - Obter dados para gráfico mensal
- DEVE retornar dados estruturados (dict ou dataclass)
- DEVE incluir tratamento de erros
- DEVE logar operações importantes

### R302: News Tool
- DEVE implementar em `agent/tools/news_tool.py`
- DEVE buscar notícias sobre SRAG em tempo real
- DEVE usar NewsAPI ou similar
- DEVE filtrar por:
  - Relevância
  - Data (últimos 7-30 dias)
  - Idioma (português)
- DEVE retornar máximo 5-10 notícias mais relevantes
- DEVE incluir: título, fonte, data, resumo, URL

### R303: System Prompt
- DEVE definir papel do agente claramente
- DEVE instruir sobre uso das tools
- DEVE especificar formato do relatório
- DEVE incluir diretrizes de tom (profissional, objetivo)
- Exemplo:
```
  Você é um analista de dados de saúde especializado em SRAG.
  Sua função é gerar relatórios completos usando dados do banco
  e contexto de notícias recentes. Seja objetivo, preciso e
  forneça insights acionáveis.
```

### R304: Orquestração
- DEVE chamar DatabaseTool primeiro
- DEVE chamar NewsTool em seguida
- DEVE sintetizar informações de ambas as fontes
- DEVE gerar comentários contextualizados
- NÃO DEVE inventar dados ou métricas

---

## FASE 4: GERAÇÃO DE RELATÓRIOS

### R400: Estrutura do Relatório
- DEVE implementar em `agent/report_generator.py`
- DEVE incluir TODAS as seções obrigatórias:

#### R401: Cabeçalho
- Data e hora de geração
- Período de análise
- Fonte dos dados (DATASUS)

#### R402: Resumo Executivo
- Breve overview do cenário atual (2-3 parágrafos)
- Principais destaques
- Gerado pelo agente com base nos dados

#### R403: Métricas-Chave
- DEVE apresentar as 4 métricas em formato visual (cards/tabela)
- DEVE incluir valor atual
- DEVE incluir comparação com período anterior (quando aplicável)
- DEVE usar cores/ícones para indicar tendência

#### R404: Visualizações
- DEVE incluir gráfico de casos diários (30d)
- DEVE incluir gráfico de casos mensais (12m)
- DEVE posicionar após as métricas
- DEVE incluir legendas explicativas

#### R405: Contexto de Notícias
- DEVE listar 3-5 notícias mais relevantes
- DEVE incluir: título, fonte, data
- DEVE adicionar breve comentário do agente relacionando com dados

#### R406: Análise e Insights
- DEVE incluir interpretação das métricas pelo agente
- DEVE correlacionar dados com notícias quando relevante
- DEVE apontar tendências significativas
- DEVE sugerir pontos de atenção

#### R407: Rodapé
- Disclaimers sobre limitações dos dados
- Fontes de informação
- Contato/mais informações

### R410: Formato de Saída
- DEVE gerar em HTML ou Markdown
- DEVE ser responsivo (se HTML)
- DEVE incluir CSS básico para legibilidade
- DEVE permitir exportação para PDF (opcional)
- DEVE salvar em `outputs/relatorios/`
- DEVE usar nomenclatura: `relatorio_srag_YYYYMMDD_HHMMSS.html`

---

## FASE 5: EXECUÇÃO E ENTREGA

### R500: Script Principal
- DEVE implementar em `run_agent.py` na raiz
- DEVE aceitar argumentos opcionais:
  - `--output`: path para salvar relatório
  - `--format`: html ou markdown
  - `--period`: período customizado (opcional)
- DEVE validar configurações antes de executar
- DEVE logar progresso da execução
- DEVE tratar erros graciosamente

### R501: Logging
- DEVE usar módulo `logging` do Python
- DEVE logar em arquivo: `logs/agent.log`
- DEVE incluir níveis: INFO, WARNING, ERROR
- DEVE incluir timestamp em cada log
- DEVE rotacionar logs (opcional)

### R502: Tratamento de Erros
- DEVE capturar exceções em cada módulo
- DEVE fornecer mensagens de erro claras
- DEVE permitir recuperação parcial quando possível
- DEVE logar stack trace completo
- NÃO DEVE expor informações sensíveis em erros

### R503: Performance
- DEVE executar em menos de 30 segundos (meta)
- DEVE otimizar queries SQL com índices
- DEVE cachear resultados quando apropriado
- PODE implementar execução paralela (opcional)

---

## REGRAS DE DOCUMENTAÇÃO

### R600: README.md
- DEVE incluir:
  - Descrição do projeto
  - Requisitos (Python, dependências)
  - Instruções de instalação passo a passo
  - Como executar
  - Estrutura de diretórios
  - Exemplos de uso
  - Limitações conhecidas
  - Licença

### R601: Docstrings
- DEVE usar docstrings em todas as funções públicas
- DEVE seguir formato Google ou NumPy
- DEVE incluir:
  - Descrição da função
  - Parâmetros (tipos e descrição)
  - Retorno (tipo e descrição)
  - Exceções que podem ser lançadas
  - Exemplo de uso (quando relevante)

### R602: Comentários no Código
- DEVE comentar lógica complexa
- DEVE explicar decisões não-óbvias
- NÃO DEVE comentar código autoexplicativo
- DEVE manter comentários atualizados

### R603: Workflow Description
- DEVE manter este documento atualizado
- DEVE refletir implementação real
- DEVE ser versionado junto com código

---

## REGRAS DE QUALIDADE

### R700: Code Style
- DEVE seguir PEP 8
- DEVE usar linter (flake8 ou ruff)
- DEVE usar formatter (black)
- DEVE manter linhas < 100 caracteres
- DEVE usar type hints quando possível

### R701: Nomenclatura
- Funções e variáveis: `snake_case`
- Classes: `PascalCase`
- Constantes: `UPPER_SNAKE_CASE`
- Arquivos: `snake_case.py`
- DEVE usar nomes descritivos

### R702: Modularidade
- DEVE manter funções com responsabilidade única
- DEVE evitar funções > 50 linhas
- DEVE extrair lógica repetida
- DEVE usar classes quando apropriado

### R703: Testabilidade
- DEVE separar lógica de I/O
- DEVE injetar dependências
- PODE incluir testes unitários (opcional para PoC)
- DEVE validar manualmente todas as funcionalidades

---

## REGRAS DE VERSIONAMENTO

### R800: Git
- DEVE usar controle de versão Git
- DEVE fazer commits atômicos e descritivos
- DEVE seguir padrão de mensagens:
```
  tipo(escopo): descrição curta
  
  Descrição detalhada (opcional)
```
  Tipos: feat, fix, docs, refactor, test, chore

### R801: .gitignore
- DEVE ignorar:
  - `venv/`, `.venv/`
  - `__pycache__/`, `*.pyc`
  - `.env`
  - `data/raw/` (arquivos grandes)
  - `*.log`
  - `.DS_Store`
  - `outputs/relatorios/*` (exceto exemplos)

---

## REGRAS DE PRIORIZAÇÃO

### R900: Prioridades para 4 Dias
#### MUST HAVE (Obrigatório)
- 4 métricas calculadas corretamente
- 2 gráficos gerados
- Agente funcionando end-to-end
- Relatório HTML gerado
- README completo

#### SHOULD HAVE (Importante)
- Busca de notícias integrada
- Comentários contextualizados do agente
- Tratamento robusto de erros
- Logging adequado

#### COULD HAVE (Desejável)
- Testes unitários
- Customização de período
- Exportação para PDF
- Dashboard interativo

#### WON'T HAVE (Fora do escopo)
- Interface web
- API REST
- Deploy em produção
- Monitoramento em tempo real
- Machine Learning para previsões

---

## CHECKLIST DE ENTREGA

### DIA 1 - Preparação
- [ ] Estrutura de diretórios criada
- [ ] Ambiente virtual configurado
- [ ] Dependências instaladas
- [ ] Dados explorados em notebook
- [ ] Script de limpeza funcionando
- [ ] Banco SQLite criado e populado

### DIA 2 - Core
- [ ] 4 métricas implementadas
- [ ] Métricas validadas em notebook
- [ ] 2 gráficos implementados
- [ ] Gráficos validados visualmente
- [ ] Módulos metrics.py e charts.py finalizados

### DIA 3 - Agente
- [ ] DatabaseTool implementada
- [ ] NewsTool implementada
- [ ] Agente LangChain configurado
- [ ] System prompt definido
- [ ] Integração testada
- [ ] Template de relatório criado

### DIA 4 - Entrega
- [ ] run_agent.py funcionando
- [ ] Relatório exemplo gerado
- [ ] Todos os erros corrigidos
- [ ] Código documentado
- [ ] README completo
- [ ] Apresentação preparada
- [ ] Repositório limpo e organizado

---

## GLOSSÁRIO

**SRAG**: Síndrome Respiratória Aguda Grave
**PoC**: Proo