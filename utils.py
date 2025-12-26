# utils.py
import pandas as pd
import io
import os
import re
import numpy as np
import streamlit as st
from datetime import datetime
from config import PASTA_DICIONARIOS, SKU_PADRAO_FINAL

# --- CACHING PARA PERFORMANCE ---
@st.cache_data(ttl=3600)
def carregar_dicionario_industria(nome_arquivo):
    """Carrega e faz cache do dicionário de regras."""
    caminho_completo = os.path.join(PASTA_DICIONARIOS, nome_arquivo)
    if not os.path.exists(caminho_completo):
        return None, f"⚠️ Arquivo não encontrado: {caminho_completo}"
    try:
        df = pd.read_excel(caminho_completo)
        df = df.dropna(subset=['Valor da Regra'])
        df = df[df['Valor da Regra'].astype(str).str.strip() != '']
        return df, None
    except Exception as e:
        return None, f"Erro ao ler o arquivo {nome_arquivo}: {e}"

@st.cache_data(ttl=3600)
def otimizar_regras(df_dict):
    """Compila e faz cache das Regras de Regex."""
    regras_otimizadas = {}
    if df_dict is None: return None
    
    for _, row in df_dict.iterrows():
        tipo = str(row['Tipo de Regra']).strip()
        pattern = str(row['Valor da Regra'])
        value = row['Interpretação']
        score = int(row['Grau de Associação']) if pd.notna(row['Grau de Associação']) else 0
        
        if tipo not in regras_otimizadas: regras_otimizadas[tipo] = []
        try:
            regras_otimizadas[tipo].append({
                'pattern': re.compile(pattern, re.IGNORECASE),
                'value': value,
                'score': score
            })
        except re.error:
            continue
    return regras_otimizadas

# --- FUNÇÕES DE ARQUIVO E FORMATAÇÃO ---

def get_data_atual_str():
    return datetime.now().strftime("%d-%m-%Y")

def to_excel_bytes(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def clean_column_names(df):
    df.columns = df.columns.astype(str).str.strip().str.strip('.').str.replace(r'\s+', ' ', regex=True)
    return df

def limpar_sku_cientifico(serie):
    return pd.to_numeric(serie, errors='coerce').dropna().astype(np.int64).astype(str)

def ler_arquivo_robusto(uploaded_file):
    # (Mantenha sua função de leitura original aqui, ela é boa)
    filename = uploaded_file.name.lower()
    if filename.endswith(('.xlsx', '.xls')):
        try: return pd.read_excel(uploaded_file)
        except: return None
    # ... adicione o restante da sua lógica CSV aqui ...
    return None

# --- LÓGICA CORE (Sem Caching pois depende do input do usuário) ---

def classificar_item(descricao, regras_lista):
    if pd.isna(descricao): return None
    str_desc = str(descricao)
    melhor_match = None
    maior_score = -1
    
    for regra in regras_lista:
        if regra['pattern'].search(str_desc):
            if regra['score'] > maior_score:
                maior_score = regra['score']
                melhor_match = regra['value']
    return melhor_match

def processar_dataframe_classificador(df_sku, regras_otimizadas, colunas_alvo, progress_callback):
    df_processado = df_sku.copy()
    comparativo_data = []
    
    # Inicializa colunas
    for col in colunas_alvo:
        if col not in df_processado.columns: df_processado[col] = None

    for i, col_alvo in enumerate(colunas_alvo):
        progress_callback(i, len(colunas_alvo), col_alvo) # Callback para atualizar barra no app.py
        
        if col_alvo in regras_otimizadas:
            lista_regras = regras_otimizadas[col_alvo]
            # Aplica a lógica
            old_values = df_processado[col_alvo].copy()
            novos_valores = df_processado['Nome SKU'].apply(lambda x: classificar_item(x, lista_regras))
            df_processado[col_alvo] = novos_valores.combine_first(df_processado[col_alvo])
            
            # Detecta mudanças (Vetorizado é mais rápido que loop)
            mask_changed = (old_values.astype(str) != df_processado[col_alvo].astype(str)) & df_processado[col_alvo].notna()
            if mask_changed.any():
                mudancas = df_processado[mask_changed].copy()
                mudancas['Coluna'] = col_alvo
                mudancas['Antes'] = old_values[mask_changed]
                mudancas['Depois'] = df_processado.loc[mask_changed, col_alvo]
                mudancas['SKU ID'] = mudancas.get('Código Barras SKU', mudancas.index)
                
                comparativo_data.extend(mudancas[['SKU ID', 'Nome SKU', 'Coluna', 'Antes', 'Depois']].rename(columns={'Nome SKU': 'Descrição'}).to_dict('records'))

    return df_processado, pd.DataFrame(comparativo_data)

def processar_extracao(files, config):
    # (Sua lógica de extração original movida para cá)
    # Retorna (df_consolidado, conflitos, debug_missing)
    pass
