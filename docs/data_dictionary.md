# Dicionário de Dados - Colunas Essenciais SRAG

## 📊 Visão Geral

**Total de Colunas:** 31 (de 194 originais)  
**Redução:** 84% - Foco em métricas-chave

---

## 🗂️ Categorias de Colunas

### 1. 📅 DATAS (5 colunas)

Essenciais para análise temporal e cálculo de métricas de crescimento.

| Coluna | Descrição | Formato | Uso |
|--------|-----------|---------|-----|
| `DT_NOTIFIC` | Data de notificação do caso | DD/MM/YYYY | Taxa de crescimento mensal |
| `DT_SIN_PRI` | Data dos primeiros sintomas | DD/MM/YYYY | Tempo até notificação |
| `DT_INTERNA` | Data de internação hospitalar | DD/MM/YYYY | Tempo até internação |
| `DT_ENTUTI` | Data de entrada na UTI | DD/MM/YYYY | Taxa de ocupação UTI |
| `DT_EVOLUCA` | Data da evolução (óbito/cura) | DD/MM/YYYY | Taxa de mortalidade |

**Análises Possíveis:**
- Série temporal de casos
- Tempo médio entre sintomas → notificação → internação → UTI
- Sazonalidade e tendências

---

### 2. 🏥 EVOLUÇÃO DO CASO (2 colunas)

Essencial para taxa de mortalidade.

| Coluna | Descrição | Valores | Uso |
|--------|-----------|---------|-----|
| `EVOLUCAO` | Desfecho do caso | 1=Cura<br>2=Óbito<br>3=Óbito por outras causas | **Taxa de mortalidade** |
| `CLASSI_FIN` | Classificação final | 1=SRAG por influenza<br>2=SRAG por outro vírus<br>3=SRAG não especificado<br>4=SRAG por COVID-19<br>5=Síndrome gripal | Estratificação por tipo |

**Análises Possíveis:**
- Taxa de mortalidade geral e por tipo
- Mortalidade por faixa etária
- Mortalidade por região

---

### 3. 🛏️ UTI (2 colunas)

Essencial para taxa de ocupação de UTI.

| Coluna | Descrição | Valores | Uso |
|--------|-----------|---------|-----|
| `UTI` | Internação em UTI | 1=Sim<br>2=Não | **Taxa de ocupação UTI** |
| `SUPORT_VEN` | Suporte ventilatório | 1=Sim, invasivo<br>2=Sim, não invasivo<br>3=Não | Gravidade do caso |

**Análises Possíveis:**
- Taxa de internação em UTI
- Correlação UTI × Mortalidade
- Necessidade de ventilação mecânica

---

### 4. 💉 VACINAÇÃO (5 colunas)

Essencial para taxa de vacinação.

| Coluna | Descrição | Valores | Uso |
|--------|-----------|---------|-----|
| `VACINA` | Vacinação contra influenza | 1=Sim<br>2=Não | **Taxa de vacinação influenza** |
| `DT_UT_DOSE` | Data da última dose (influenza) | DD/MM/YYYY | Tempo desde vacinação |
| `VACINA_COV` | Vacinação contra COVID-19 | 1=Sim<br>2=Não | **Taxa de vacinação COVID** |
| `DOSE_1_COV` | Data 1ª dose COVID | DD/MM/YYYY | Cobertura vacinal |
| `DOSE_2_COV` | Data 2ª dose COVID | DD/MM/YYYY | Esquema completo |

**Análises Possíveis:**
- Taxa de vacinação da população afetada
- Efetividade vacinal (vacinados vs não vacinados)
- Cobertura por região

---

### 5. 👤 CONTEXTO DEMOGRÁFICO (5 colunas)

Essencial para estratificação e análise geográfica.

| Coluna | Descrição | Valores | Uso |
|--------|-----------|---------|-----|
| `NU_IDADE_N` | Idade em anos | 0-120 | Faixas etárias |
| `CS_SEXO` | Sexo | M=Masculino<br>F=Feminino<br>I=Ignorado | Estratificação por sexo |
| `SG_UF_NOT` | UF de notificação | AC, AL, AM, ... | **Análise geográfica** |
| `CO_MUN_NOT` | Código IBGE do município | 6 dígitos | Município específico |
| `ID_MUNICIP` | Nome do município | Texto | Identificação |

**Análises Possíveis:**
- Distribuição por faixa etária
- Diferenças por sexo
- Hotspots geográficos (UF/município)

---

### 6. 🩺 COMORBIDADES (7 colunas)

Fatores de risco para agravamento.

| Coluna | Descrição | Valores | Uso |
|--------|-----------|---------|-----|
| `CARDIOPATI` | Doença cardiovascular | 1=Sim<br>2=Não | Fator de risco |
| `PNEUMOPATI` | Doença respiratória crônica | 1=Sim<br>2=Não | Fator de risco |
| `DIABETES` | Diabetes mellitus | 1=Sim<br>2=Não | Fator de risco |
| `OBESIDADE` | Obesidade | 1=Sim<br>2=Não | Fator de risco |
| `RENAL` | Doença renal crônica | 1=Sim<br>2=Não | Fator de risco |
| `IMUNODEPRE` | Imunodepressão | 1=Sim<br>2=Não | Fator de risco |
| `ASMA` | Asma | 1=Sim<br>2=Não | Fator de risco |

**Análises Possíveis:**
- Número de comorbidades por paciente
- Correlação comorbidades × Mortalidade
- Correlação comorbidades × UTI

---

### 7. 🤒 SINTOMAS PRINCIPAIS (5 colunas)

Caracterização clínica.

| Coluna | Descrição | Valores | Uso |
|--------|-----------|---------|-----|
| `FEBRE` | Febre | 1=Sim<br>2=Não | Sintoma cardinal |
| `TOSSE` | Tosse | 1=Sim<br>2=Não | Sintoma respiratório |
| `DISPNEIA` | Dispneia (falta de ar) | 1=Sim<br>2=Não | Gravidade |
| `SATURACAO` | Saturação O2 < 95% | 1=Sim<br>2=Não | Gravidade |
| `DESC_RESP` | Desconforto respiratório | 1=Sim<br>2=Não | Gravidade |

**Análises Possíveis:**
- Perfil sintomático
- Sintomas × Gravidade (UTI/Óbito)
- Padrões clínicos

---

## 🎯 Mapeamento para Métricas-Chave

### Métrica 1: Taxa de Crescimento de Casos
**Colunas Usadas:** `DT_NOTIFIC`
```python
casos_mensais = df.groupby(df['DT_NOTIFIC'].dt.to_period('M')).size()
taxa_crescimento = casos_mensais.pct_change() * 100
```

### Métrica 2: Taxa de Mortalidade
**Colunas Usadas:** `EVOLUCAO`
```python
obitos = (df['EVOLUCAO'] == 2).sum()
taxa_mortalidade = (obitos / len(df)) * 100
```

### Métrica 3: Taxa de Ocupação de UTI
**Colunas Usadas:** `UTI`
```python
uti_casos = (df['UTI'] == 1).sum()
taxa_uti = (uti_casos / len(df)) * 100
```

### Métrica 4: Taxa de Vacinação
**Colunas Usadas:** `VACINA`, `VACINA_COV`
```python
vacinados_influenza = (df['VACINA'] == 1).sum()
taxa_vacina_flu = (vacinados_influenza / len(df)) * 100

vacinados_covid = (df['VACINA_COV'] == 1).sum()
taxa_vacina_cov = (vacinados_covid / len(df)) * 100
```

---

## 📝 Notas Importantes

### Valores Especiais
- `9` = Ignorado (em muitas colunas categóricas)
- `NaN` / `null` = Dado ausente
- Datas inválidas = `NaN` após conversão

### Qualidade Esperada
- **Datas:** ~10-30% missing (variável por coluna)
- **Evolução:** ~5-15% missing
- **UTI:** ~20-40% missing
- **Vacinação:** ~30-50% missing
- **Comorbidades:** ~20-60% missing (muitos "Ignorado")

### Decisões de Tratamento
1. **Missing em DT_NOTIFIC:** Remover registro (essencial para análise temporal)
2. **Missing em EVOLUCAO:** Remover para cálculo de mortalidade
3. **Missing em UTI:** Considerar como "Não" se não internado
4. **Missing em Vacinação:** Considerar como "Não" (conservador)
5. **Missing em Comorbidades:** Manter como "Ignorado" (não assumir)

---

## ✅ Validação

### Checklist de Qualidade
- [ ] Todas as 31 colunas existem no dataset?
- [ ] Datas convertidas para `datetime`?
- [ ] Valores categóricos mapeados corretamente?
- [ ] Missing values documentados?
- [ ] Outliers em idade identificados?

### Testes Recomendados
```python
# 1. Verificar existência
assert all(col in df.columns for col in colunas_selecionadas)

# 2. Verificar tipos
assert df['DT_NOTIFIC'].dtype == 'datetime64[ns]'
assert df['EVOLUCAO'].dtype in ['int64', 'float64']

# 3. Verificar ranges
assert df['NU_IDADE_N'].between(0, 120).all()
assert df['EVOLUCAO'].isin([1, 2, 3, 9]).all()
```

---

**Versão:** 1.0  
**Data:** 2026-02-10  
**Autor:** Antigravity AI Assistant
