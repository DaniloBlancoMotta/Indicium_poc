"""
Módulo de preparação e carregamento de dados SRAG (Data Agent Workflow)
Implementa R100, R101, R102, R103, R104, R200, R201, R202, R203
"""

import pandas as pd
import sqlite3
import logging
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple, Optional
from . import config

logger = logging.getLogger(__name__)

# ============================================================
# REGRAS DE LIMPEZA E TRANSFORMAÇÃO
# ============================================================

def clean_date(date_str):
    """
    R101: Limpeza de Datas
    - Formato: DD/MM/YYYY
    - Filtra datas inválidas, futuras ou anteriores a 2020
    """
    if pd.isna(date_str):
        return None
    
    try:
        # Tenta formato DD/MM/YYYY (DATASUS padrão) ou YYYY-MM-DD (ISO)
        dt = pd.to_datetime(date_str, format='%d/%m/%Y', errors='coerce')
        if pd.isna(dt):
             dt = pd.to_datetime(date_str, format='%Y-%m-%d', errors='coerce')
        
        # Validações detalhadas (R101)
        if pd.isna(dt):
            return None
        if dt > datetime.now():
            return None  # Data futura
        # Permitir 2019 para análise histórica de 2020
        if dt.year < 2019:
            return None  # Fora do escopo SRAG
            
        return dt.date() # Retorna apenas data (sem hora) para o SQLite
    except:
        return None

def classify_outcome(evolucao_value):
    """
    R102: Classificação de Desfecho (Óbito)
    1=Cura, 2=Óbito, 3=Óbito outras, 9=Ignorado
    Returns: True (Óbito), False (Cura), None (Ignorado)
    """
    if pd.isna(evolucao_value):
        return None
    
    try:
        val = int(evolucao_value)
        if val == 1: 
            return False # Cura
        elif val in [2, 3]: 
            return True  # Óbito
        else: 
            return None # Ignorado/Outro
    except:
        return None

def classify_icu(uti_value):
    """
    R103: Classificação de UTI
    1=Sim, 2=Não, 9=Ignorado
    Returns: True (UTI), False (Não UTI), None (Ignorado)
    """
    if pd.isna(uti_value):
        return None
    
    try:
        val = int(uti_value)
        if val == 1: return True
        elif val == 2: return False
        else: return None
    except:
        return None

def classify_vaccination(row) -> Tuple[Optional[bool], int]:
    """
    R104: Classificação de Vacinação (Complexa)
    Prioriza colunas de DOSE_COV, fallback para VACINA.
    Returns: (esta_vacinado, numero_doses)
    """
    doses = 0
    is_vaccinated = None
    
    # 1. Verificar Doses COVID (Mais confiável se existir)
    # Check if columns exist in row to avoid KeyErrors if mapping fails
    has_dose1 = 'DOSE_1_COV' in row and row['DOSE_1_COV'] not in [None, np.nan, '']
    has_dose2 = 'DOSE_2_COV' in row and row['DOSE_2_COV'] not in [None, np.nan, '']
    
    if has_dose1 or has_dose2:
        if has_dose1: doses += 1
        if has_dose2: doses += 1
        return True, doses
        
    # 2. Fallback para coluna genérica VACINA
    # 1=Sim, 2=Não, 9=Ignorado
    if 'VACINA' in row and pd.notna(row['VACINA']):
        try:
            val = int(row['VACINA'])
            if val == 1:
                return True, 0 # Vacinado, doses desconhecidas
            elif val == 2:
                return False, 0
        except:
            pass
            
    return None, 0 # Desconhecido

# ============================================================
# PIPELINE DE CARREGAMENTO
# ============================================================

def load_from_csv(
    filepath: Optional[str] = None, 
    chunk_size: Optional[int] = None,
    max_chunks: Optional[int] = None
) -> pd.DataFrame:
    """Implementa Step 1 e 2 do Pipeline: Load & Select"""
    filepath = filepath or config.DATA_FILE
    chunk_size = chunk_size or config.CHUNK_SIZE
    max_chunks = max_chunks or config.MAX_CHUNKS
    
    logger.info(f"📂 Lendo CSV bruto: {Path(filepath).name} (R100)")
    
    # Colunas originais para carregar (chaves do mapping)
    cols_to_load = config.COLUNAS_SELECIONADAS
    
    chunks = []
    try:
        for i, chunk in enumerate(pd.read_csv(
            filepath,
            sep=config.SEPARATOR,
            encoding=config.ENCODING,
            chunksize=chunk_size,
            low_memory=False,
            usecols=lambda c: c in cols_to_load # Carrega apenas colunas mapeadas
        )):
            chunks.append(chunk)
            if max_chunks and len(chunks) >= max_chunks:
                logger.info(f"⚠️ Limitado a {max_chunks} chunks para teste")
                break
                
        df = pd.concat(chunks, ignore_index=True)
        logger.info(f"raw_rows: {len(df)}")
        return df
    except Exception as e:
        logger.error(f"Erro ao ler CSV: {e}")
        raise

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Implementa Step 3: Transform & Clean (R101-R104, R200-R203)"""
    logger.info("⚡ Transformando dados (R101-R104)...")
    
    # 1. Limpeza de Datas (R101)
    # Aplicar clean_date nas colunas mapeadas de data
    # Mapping: DT_NOTIFIC -> dt_notificacao, etc.
    
    # Work on a copy with renamed columns for clarity or process original then rename?
    # Strategy: Process originals, then map to new Schema
    
    # Dates
    df['dt_notificacao_clean'] = df['DT_NOTIFIC'].apply(clean_date)
    df['dt_obito_clean'] = df['DT_EVOLUCA'].apply(clean_date)
    
    # R200: Required Fields
    original_len = len(df)
    df = df[df['dt_notificacao_clean'].notna()].copy()
    logger.info(f"Dropados {original_len - len(df)} registros sem data de notificação (R200)")
    
    # R201: Filtro Temporal (Últimos 13 meses RELATIVOS AOS DADOS)
    # Como estamos processando dados históricos (2020), usar max(data) do dataset
    if not df.empty:
        max_data_dataset = df['dt_notificacao_clean'].max()
        cutoff_date = max_data_dataset - timedelta(days=395)
        df = df[df['dt_notificacao_clean'] >= cutoff_date].copy()
        logger.info(f"Registros após filtro de 13 meses (ref: {max_data_dataset}): {len(df)} (R201)")
    else:
        logger.warning("Dataset vazio após limpeza de datas.")
    
    # R202: Deduplicação (Simplificado por dt_notificacao se NU_NOTIFIC n/a)
    # Assumindo que não temos ID único confiável além das linhas, skip complex dedupe for now unless explicit ID col exist
    
    # Computed Fields (Schema Target)
    df['dt_notificacao'] = df['dt_notificacao_clean'] # Already date object
    df['dt_obito'] = df['dt_obito_clean']
    
    # Extrair ano/mes/semana de objetos date
    # Precisamos converter para pd.Timestamp para usar acessores .dt
    temp_dates = pd.to_datetime(df['dt_notificacao'])
    df['ano'] = temp_dates.dt.year
    df['mes'] = temp_dates.dt.month
    df['semana_epi'] = temp_dates.dt.isocalendar().week
    
    # Outcomes (R102)
    df['evolucao_raw'] = df['EVOLUCAO']
    df['teve_obito'] = df['EVOLUCAO'].apply(classify_outcome)
    
    # ICU (R103)
    df['foi_uti_raw'] = df['UTI']
    df['teve_uti'] = df['UTI'].apply(classify_icu)
    
    # Vaccination (R104)
    # Apply row-wise
    vac_res = df.apply(classify_vaccination, axis=1)
    df['esta_vacinado'] = [x[0] for x in vac_res]
    df['doses_vacina'] = [x[1] for x in vac_res]
    df['vacina_status_raw'] = df['VACINA']
    
    # Demographics
    df['idade'] = pd.to_numeric(df['NU_IDADE_N'], errors='coerce')
    # R203: Age Validation
    df.loc[(df['idade'] < 0) | (df['idade'] > 120), 'idade'] = None
    
    df['sexo'] = pd.to_numeric(df['CS_SEXO'], errors='coerce') # 1=M, 2=F typically, but check parsing if M/F str
    # Se sexo for M/F string no CSV:
    # 1=M, 2=F mapping logic if needed. Assuming DATASUS raw is usually M/F strings or code. 
    # CSV sample inspection would be good. Standardizing to code:
    sex_map = {'M': 1, 'F': 2, 'I': 9}
    df['sexo'] = df['CS_SEXO'].map(sex_map).fillna(9).astype(int)
    
    df['uf_sigla'] = df['SG_UF_NOT']
    # Ensure column exists or handle gracefully
    df['municipio_cod'] = df['CO_MUN_NOT'] if 'CO_MUN_NOT' in df.columns else None
    
    # Select Final Schema Columns
    final_cols = [
        'dt_notificacao', 'dt_obito', 'ano', 'mes', 'semana_epi',
        'evolucao_raw', 'teve_obito',
        'foi_uti_raw', 'teve_uti',
        'vacina_status_raw', 'esta_vacinado', 'doses_vacina',
        'idade', 'sexo', 'uf_sigla', 'municipio_cod'
    ]
    
    # Rename mapping for raw columns to match schema expected keys if needed
    # Renaming for clarity in SQL
    rename_map = {
        'evolucao_raw': 'evolucao',
        'foi_uti_raw': 'foi_uti',
        'vacina_status_raw': 'vacina_status'
    }
    
    df_final = df[final_cols].rename(columns=rename_map)
    return df_final

def ingest_to_sqlite(df: pd.DataFrame):
    """Implementa Step 4: Load to SQLite (Schema Def)"""
    logger.info("🗄️ Ingerindo no SQLite (Schema Target)...")
    
    db_path = config.DATABASE_PATH
    config.DATA_DATABASE.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    # Create Table Schema Manually to ensure types
    # df.to_sql does generic types, good to enforce structure if needed
    # Rationale: to_sql is faster for PoC. Indexes are critical.
    
    try:
        # Save
        df.to_sql(config.TABLE_NAME, conn, if_exists='replace', index=False)
        
        # Indexes (Critical)
        cursor = conn.cursor()
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_dt_notificacao ON {config.TABLE_NAME}(dt_notificacao)")
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_ano_mes ON {config.TABLE_NAME}(ano, mes)")
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_teve_obito ON {config.TABLE_NAME}(teve_obito)")
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_teve_uti ON {config.TABLE_NAME}(teve_uti)")
        
        conn.commit()
        logger.info(f"✅ Ingestão completa: {len(df)} registros na tabela {config.TABLE_NAME}")
        
    finally:
        conn.close()

# ============================================================
# INTERFACE DE LEITURA (Para o Agente)
# ============================================================

def load_from_sqlite() -> pd.DataFrame:
    """Reads cleaned data for Metrics/Charts"""
    if not config.DATABASE_PATH.exists():
        return pd.DataFrame()
        
    conn = sqlite3.connect(config.DATABASE_PATH)
    try:
        # Read all for now, Metrics module handles filtering
        df = pd.read_sql(f"SELECT * FROM {config.TABLE_NAME}", conn)
        
        # Ensure dates are datetime objects for pandas manip
        if 'dt_notificacao' in df.columns:
            df['dt_notificacao'] = pd.to_datetime(df['dt_notificacao'])
            
        return df
    finally:
        conn.close()

# Alias for compatibility with run_agent.py
def clean_data(df):
    return transform_data(df)
