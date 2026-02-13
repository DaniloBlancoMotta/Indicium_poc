---
description: DATA INGESTION & PROCESSING 
---

# DATA INGESTION & PROCESSING AGENT

## MISSION
Transform raw DATASUS SRAG CSV data into a clean, indexed SQLite database optimized for metric calculations and chart generation.

---

## CRITICAL REQUIREMENTS

### INPUT
- File: `data/raw/SRAG_*.csv`
- Format: CSV with `;` delimiter
- Encoding: `latin-1` or `cp1252`
- Size: ~165,000 rows, ~100 columns

### OUTPUT
- Database: `data/database/srag.db`
- Table: `srag_cases`
- Metrics support: 4 KPIs + 2 charts
- Query performance: < 2 seconds per metric

---

## SCHEMA DESIGN

### Table: srag_cases
```sql
CREATE TABLE srag_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- TEMPORAL (Critical for all queries)
    dt_notificacao DATE NOT NULL,        -- Notification/admission date
    dt_obito DATE,                       -- Death date (if applicable)
    ano INTEGER NOT NULL,                -- Year (indexed)
    mes INTEGER NOT NULL,                -- Month (indexed)
    semana_epi INTEGER,                  -- Epidemiological week
    
    -- OUTCOME (For mortality rate)
    evolucao INTEGER,                    -- 1=Cure, 2=Death, 3=Death other causes
    teve_obito BOOLEAN,                  -- Computed: TRUE if died
    
    -- ICU (For ICU occupancy rate)
    foi_uti INTEGER,                     -- 1=Yes, 2=No, 9=Ignored
    teve_uti BOOLEAN,                    -- Computed: TRUE if ICU
    
    -- VACCINATION (For vaccination rate)
    vacina_status INTEGER,               -- Varies by dataset
    esta_vacinado BOOLEAN,               -- Computed: TRUE if vaccinated
    doses_vacina INTEGER,                -- Number of doses (if available)
    
    -- DEMOGRAPHICS (Optional context)
    idade INTEGER,
    sexo INTEGER,                        -- 1=M, 2=F
    uf_sigla VARCHAR(2),
    municipio_cod VARCHAR(10),
    
    -- METADATA
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CRITICAL INDEXES
CREATE INDEX idx_dt_notificacao ON srag_cases(dt_notificacao);
CREATE INDEX idx_ano_mes ON srag_cases(ano, mes);
CREATE INDEX idx_evolucao ON srag_cases(evolucao);
CREATE INDEX idx_teve_obito ON srag_cases(teve_obito);
CREATE INDEX idx_teve_uti ON srag_cases(teve_uti);
CREATE INDEX idx_esta_vacinado ON srag_cases(esta_vacinado);
```

---

## DATA MAPPING RULES

### R100: Column Identification
Map DATASUS columns to schema (names vary by year):
```python
COLUMN_MAPPING = {
    # TEMPORAL
    'date': ['DT_NOTIFIC', 'DT_INTERNA', 'DT_SIN_PRI'],
    'death_date': ['DT_EVOLUCA', 'DT_OBITO'],
    
    # OUTCOME
    'evolution': ['EVOLUCAO', 'CLASSI_FIN'],
    
    # ICU
    'icu': ['UTI', 'SUPORT_VEN'],
    
    # VACCINATION
    'vaccine': ['VACINA', 'VACINA_COV', 'DOSE_1_COV', 'DOSE_2_COV'],
    
    # DEMOGRAPHICS
    'age': ['NU_IDADE_N', 'IDADE'],
    'sex': ['CS_SEXO', 'SEXO'],
    'state': ['SG_UF_NOT', 'SG_UF'],
}
```

### R101: Date Cleaning
```python
def clean_date(date_str):
    """
    RULES:
    - Format: DD/MM/YYYY (DATASUS standard)
    - Invalid dates → NULL
    - Future dates → NULL (data quality issue)
    - Before 2020 → NULL (SRAG relevance)
    """
    if pd.isna(date_str):
        return None
    
    try:
        dt = pd.to_datetime(date_str, format='%d/%m/%Y', errors='coerce')
        
        # Validation
        if dt > datetime.now():
            return None  # Future date = invalid
        if dt.year < 2020:
            return None  # Too old for SRAG context
            
        return dt
    except:
        return None
```

### R102: Outcome Classification
```python
def classify_outcome(evolucao_value):
    """
    RULES (DATASUS codes):
    1 = Cura/Alta → teve_obito = FALSE
    2 = Óbito pelo agravo → teve_obito = TRUE
    3 = Óbito por outras causas → teve_obito = TRUE
    9, NULL = Ignorado → teve_obito = NULL
    """
    if pd.isna(evolucao_value):
        return None
    
    evolucao_map = {
        1: False,  # Cure
        2: True,   # Death by disease
        3: True,   # Death other causes
        9: None    # Unknown
    }
    
    return evolucao_map.get(int(evolucao_value), None)
```

### R103: ICU Classification
```python
def classify_icu(uti_value):
    """
    RULES (DATASUS codes):
    1 = Sim → teve_uti = TRUE
    2 = Não → teve_uti = FALSE
    9, NULL = Ignorado → teve_uti = NULL
    """
    if pd.isna(uti_value):
        return None
    
    icu_map = {
        1: True,   # Yes
        2: False,  # No
        9: None    # Unknown
    }
    
    return icu_map.get(int(uti_value), None)
```

### R104: Vaccination Classification
```python
def classify_vaccination(row):
    """
    RULES (complex - varies by dataset):
    
    Option 1: VACINA column exists
    - 1 = Sim → TRUE
    - 2 = Não → FALSE
    - 9 = Ignorado → NULL
    
    Option 2: DOSE columns exist (COVID)
    - If DOSE_1_COV == 1 OR DOSE_2_COV == 1 → TRUE
    - Else → FALSE
    
    Priority: Check DOSE columns first (more reliable)
    """
    # Try COVID dose columns first
    if 'DOSE_1_COV' in row:
        if row['DOSE_1_COV'] == 1 or row.get('DOSE_2_COV') == 1:
            doses = 0
            if row.get('DOSE_1_COV') == 1: doses += 1
            if row.get('DOSE_2_COV') == 1: doses += 1
            if row.get('DOSE_REF') == 1: doses += 1
            return True, doses
    
    # Fallback to generic VACINA column
    if 'VACINA' in row:
        vacina = row['VACINA']
        if vacina == 1:
            return True, None  # Vaccinated, doses unknown
        elif vacina == 2:
            return False, 0
    
    return None, None  # Unknown
```

---

## DATA QUALITY RULES

### R200: Required Fields
```python
MUST_HAVE = ['dt_notificacao']  # Absolute minimum

# Drop rows if:
df = df[df['dt_notificacao'].notna()]  # No date = useless
```

### R201: Temporal Filtering
```python
# Keep only last 13 months (for 12-month chart + current month)
cutoff_date = datetime.now() - timedelta(days=395)
df = df[df['dt_notificacao'] >= cutoff_date]
```

### R202: Deduplication
```python
# Remove duplicates (can happen in DATASUS)
# Keep last notification (most recent data)
df = df.sort_values('dt_notificacao').drop_duplicates(
    subset=['NU_NOTIFIC'],  # Notification number (if exists)
    keep='last'
)
```

### R203: Value Validation
```python
# Age validation
df.loc[df['idade'] > 120, 'idade'] = None
df.loc[df['idade'] < 0, 'idade'] = None

# Sex validation (1 or 2 only)
df.loc[~df['sexo'].isin([1, 2]), 'sexo'] = None
```

---

## PROCESSING PIPELINE

### Step 1: Load Raw Data
```python
import pandas as pd
import sqlite3
from pathlib import Path

def load_raw_csv(filepath):
    """Load with proper encoding and delimiter"""
    return pd.read_csv(
        filepath,
        sep=';',
        encoding='latin-1',
        low_memory=False,
        parse_dates=False  # Manual parsing for control
    )
```

### Step 2: Column Selection & Mapping
```python
def select_columns(df):
    """Keep only necessary columns"""
    
    # Identify available columns from mapping
    cols_to_keep = []
    
    for target, candidates in COLUMN_MAPPING.items():
        for col in candidates:
            if col in df.columns:
                cols_to_keep.append(col)
                break  # Take first match
    
    return df[cols_to_keep]
```

### Step 3: Transform & Clean
```python
def transform_data(df):
    """Apply all cleaning rules"""
    
    # Dates
    df['dt_notificacao'] = df['DT_NOTIFIC'].apply(clean_date)
    df['dt_obito'] = df['DT_OBITO'].apply(clean_date) if 'DT_OBITO' in df else None
    
    # Computed fields
    df['ano'] = df['dt_notificacao'].dt.year
    df['mes'] = df['dt_notificacao'].dt.month
    df['semana_epi'] = df['dt_notificacao'].dt.isocalendar().week
    
    # Outcomes
    df['teve_obito'] = df['EVOLUCAO'].apply(classify_outcome)
    df['teve_uti'] = df['UTI'].apply(classify_icu)
    
    # Vaccination (complex)
    vaccine_result = df.apply(classify_vaccination, axis=1)
    df['esta_vacinado'] = vaccine_result.apply(lambda x: x[0])
    df['doses_vacina'] = vaccine_result.apply(lambda x: x[1])
    
    return df
```

### Step 4: Load to SQLite
```python
def load_to_sqlite(df, db_path='data/database/srag.db'):
    """Create database and load data"""
    
    # Create directory
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Connect
    conn = sqlite3.connect(db_path)
    
    # Load data
    df.to_sql('srag_cases', conn, if_exists='replace', index=False)
    
    # Create indexes
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX idx_dt_notificacao ON srag_cases(dt_notificacao)")
    cursor.execute("CREATE INDEX idx_ano_mes ON srag_cases(ano, mes)")
    cursor.execute("CREATE INDEX idx_teve_obito ON srag_cases(teve_obito)")
    cursor.execute("CREATE INDEX idx_teve_uti ON srag_cases(teve_uti)")
    cursor.execute("CREATE INDEX idx_esta_vacinado ON srag_cases(esta_vacinado)")
    
    conn.commit()
    conn.close()
    
    print(f"✓ Loaded {len(df)} records to {db_path}")
```

---

## VALIDATION QUERIES

### V1: Record Counts
```sql
SELECT 
    COUNT(*) as total_records,
    COUNT(DISTINCT ano) as years,
    MIN(dt_notificacao) as earliest,
    MAX(dt_notificacao) as latest
FROM srag_cases;
```

### V2: Data Quality Check
```sql
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN teve_obito IS NOT NULL THEN 1 ELSE 0 END) as with_outcome,
    SUM(CASE WHEN teve_uti IS NOT NULL THEN 1 ELSE 0 END) as with_icu_info,
    SUM(CASE WHEN esta_vacinado IS NOT NULL THEN 1 ELSE 0 END) as with_vaccine_info
FROM srag_cases;
```

### V3: Temporal Distribution
```sql
SELECT ano, mes, COUNT(*) as casos
FROM srag_cases
GROUP BY ano, mes
ORDER BY ano DESC, mes DESC
LIMIT 13;
```

---

## SUCCESS CRITERIA

- [ ] Database created with proper schema
- [ ] All 4 metrics calculable from data
- [ ] 13+ months of data available (for charts)
- [ ] Indexes improve query speed
- [ ] <5% NULL rate in critical fields (outcome, ICU, vaccine)
- [ ] Data validated against DATASUS totals

---

## EXECUTION
```bash
python scripts/setup_database.py
```

Expected runtime: 2-5 minutes for 165k records.