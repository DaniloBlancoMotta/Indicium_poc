"""
Configurações centralizadas para análise SRAG
Seguindo padrões de engenharia de software e CRISP-DM
"""

from pathlib import Path
from typing import List, Tuple

# ============================================================
# CAMINHOS
# ============================================================

PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_DATABASE = PROJECT_ROOT / "data" / "database"
OUTPUTS = PROJECT_ROOT / "outputs" / "relatorios"
LOGS = PROJECT_ROOT / "logs"
ANALISE = PROJECT_ROOT / "analise"

# Database Path
DATABASE_PATH = DATA_DATABASE / "srag.db"

# Arquivo principal
DATA_FILE = r"c:\Users\UNIVERSO\OneDrive\Apps\Desktop\Indicium Health\srag-poc\data\raw\INFLUD20-26-06-2025.csv"

# Database Settings
TABLE_NAME = "srag_cases"

# ============================================================
# PARÂMETROS DE CARREGAMENTO
# ============================================================

CHUNK_SIZE = 50000
MAX_CHUNKS = None  # Process all data
ENCODING = 'latin-1'
SEPARATOR = ';'

# ============================================================
# MAPEAMENTO DE COLUNAS (R100)
# ============================================================

COLUMN_MAPPING = {
    # TEMPORAL
    'DT_NOTIFIC': 'dt_notificacao',
    'DT_SIN_PRI': 'dt_sintomas',
    'DT_INTERNA': 'dt_internacao',
    'DT_EVOLUCA': 'dt_evolucao',
    'DT_ENTUTI': 'dt_ent_uti',
        
    # OUTCOME
    'EVOLUCAO': 'evolucao',
    'CLASSI_FIN': 'classificacao_final',
    
    # ICU
    'UTI': 'foi_uti',
    'SUPORT_VEN': 'suporte_ventilatorio',
    
    # VACCINATION
    'VACINA': 'vacina_status',
    'VACINA_COV': 'vacina_covid_status',
    'DOSE_1_COV': 'dose_1_covid',
    'DOSE_2_COV': 'dose_2_covid',
    
    # DEMOGRAPHICS
    'NU_IDADE_N': 'idade',
    'CS_SEXO': 'sexo',
    'SG_UF_NOT': 'uf',
    'ID_MUNICIP': 'municipio',
    'CO_MUN_NOT': 'municipio_cod'
}

# Colunas necessárias para leitura do CSV
COLUNAS_SELECIONADAS = list(COLUMN_MAPPING.keys())

# Colunas de data no CSV original
DATE_COLUMNS_CSV = [
    'DT_NOTIFIC', 'DT_SIN_PRI', 'DT_INTERNA', 'DT_EVOLUCA', 
    'DT_ENTUTI', 'DOSE_1_COV', 'DOSE_2_COV'
]

# ============================================================
# CONFIGURAÇÕES DE VISUALIZAÇÃO
# ============================================================

PLOT_STYLE = 'ggplot'
PLOT_PALETTE = 'husl'
FIGURE_SIZE = (14, 10)
DPI = 100

# Cores para métricas
METRIC_COLORS = {
    'crescimento': '#2E86AB',
    'mortalidade': '#A23B72',
    'uti': '#F18F01',
    'vacinacao': '#06A77D'
}

# ============================================================
# VALIDAÇÃO DE CONFIGURAÇÃO
# ============================================================

def validate_config():
    """Valida se todas as configurações estão corretas"""
    if not Path(DATA_FILE).exists():
        raise FileNotFoundError(f"Arquivo de dados não encontrado: {DATA_FILE}")
    return True
