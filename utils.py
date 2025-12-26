import pandas as pd
import re
import io
import os
import numpy as np
import unicodedata
from datetime import datetime
import streamlit as st
from config import PASTA_DICIONARIOS, SKU_PADRAO_FINAL, COL_NOME_SKU

# ==============================================================================
# FUNÇÕES DE CACHE E LÓGICA (BACKEND)
# ==============================================================================

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
    serie_numerica = pd.to_numeric(serie, errors='coerce')
    serie_valida = serie_numerica.dropna()
    return serie_valida.astype(np.int64).astype(str)

def padronizar_texto_extrator(valor):
    """Normaliza texto: Maiúsculo, Sem Acentos, Sem Pontos."""
    if pd.isna(valor): return valor
    texto = str(valor).upper()
    texto_normalizado = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
    texto_final = texto_normalizado.replace('.', '')
    return texto_final.strip()

def ler_arquivo_robusto(uploaded_file):
    filename = uploaded_file.name.lower()
    if filename.endswith(('.xlsx', '.xls')):
        try: return pd.read_excel(uploaded_file)
        except Exception as e: return None

    if filename.endswith('.csv'):
        bytes_iniciais = uploaded_file.read(4)
        uploaded_file.seek(0)
        encoding_detectado = 'utf-8'
        if bytes_iniciais.startswith(b'\xff\xfe'): encoding_detectado = 'utf-16'
        elif bytes_iniciais.startswith(b'\xfe\xff'): encoding_detectado = 'utf-16-be'
        elif bytes_iniciais.startswith(b'\xef\xbb\xbf'): encoding_detectado = 'utf-8-sig'

        try:
            df = pd.read_csv(uploaded_file, encoding=encoding_detectado, sep='\t')
            if df.shape[1] > 1: return df
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=encoding_detectado, sep=';')
            if df.shape[1] > 1: return df
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding=encoding_detectado, sep=',')
            return df
        except Exception:
            try:
                uploaded_file.seek(0)
                return pd.read_csv(uploaded_file, encoding='latin1', sep=';')
            except:
                return None
    return None

# --- CARREGAMENTO DE DICIONÁRIOS COM CACHE ---
@st.cache_data
def carregar_dicionario_industria(nome_arquivo):
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

@st.cache_data
def otimizar_regras(df_dict):
    regras_otimizadas = {}
    cols_necessarias = ['Tipo de Regra', 'Valor da Regra', 'Interpretação', 'Grau de Associação']
    if df_dict is None or not all(col in df_dict.columns for col in cols_necessarias):
        return None
        
    for _, row in df_dict.iterrows():
        tipo_regra = str(row['Tipo de Regra']).strip()
        regex_pattern = str(row['Valor da Regra'])
        interpretacao = row['Interpretação']
        score = row['Grau de Associação'] if pd.notna(row['Grau de Associação']) else 0
        
        if tipo_regra not in regras_otimizadas: regras_otimizadas[tipo_regra] = []
        try:
            regras_otimizadas[tipo_regra].append({
                'pattern': re.compile(regex_pattern, re.IGNORECASE),
                'value': interpretacao,
                'score': int(score)
            })
        except re.error: continue
    return regras_otimizadas

def classificar_item(descricao, regras_lista):
    if pd.isna(descricao): return None
    melhor_match = None
    maior_score = -1
    str_desc = str(descricao)
    for regra in regras_lista:
        if regra['pattern'].search(str_desc):
            if regra['score'] > maior_score:
                maior_score = regra['score']
                melhor_match = regra['value']
    return melhor_match

def processar_dataframe_classificador(df_sku, regras_otimizadas, config_industria):
    colunas_alvo = config_industria['colunas']
    df_processado = df_sku.copy()
    comparativo_data = []
    barra = st.progress(0)
    status = st.empty()
    
    for col in colunas_alvo:
        if col not in df_processado.columns: df_processado[col] = None
            
    for i, col_alvo in enumerate(colunas_alvo):
        status.text(f"Classificando: {col_alvo}...")
        barra.progress((i + 1) / len(colunas_alvo))
        
        if col_alvo in regras_otimizadas:
            lista_regras = regras_otimizadas[col_alvo]
            novos_valores = df_processado['Nome SKU'].apply(lambda x: classificar_item(x, lista_regras))
            old_values = df_processado[col_alvo]
            df_processado[col_alvo] = novos_valores.combine_first(df_processado[col_alvo])
            
            for idx, (old, new) in enumerate(zip(old_values, df_processado[col_alvo])):
                if str(old) != str(new) and pd.notna(new):
                    sku_id = df_processado.iloc[idx].get('Código Barras SKU', idx)
                    comparativo_data.append({
                        'SKU ID': sku_id,
                        'Descrição': df_processado.iloc[idx]['Nome SKU'],
                        'Coluna': col_alvo,
                        'Antes': old,
                        'Depois': new
                    })
    barra.empty()
    status.empty()
    return df_processado, pd.DataFrame(comparativo_data)

def processar_arquivos_extrator(files, config_industria):
    lista_dfs = []
    log_erros = []
    debug_missing_cols = {} 
    sku_input = config_industria["sku_origem"]
    cols_atributos = config_industria["colunas_atributos"]
    # Garante que o Nome SKU esteja no mestre
    colunas_alvo = [SKU_PADRAO_FINAL, COL_NOME_SKU] + cols_atributos

    progress_bar = st.progress(0)
    
    for i, file in enumerate(files):
        try:
            df_raw = ler_arquivo_robusto(file)
            if df_raw is None: raise ValueError("Arquivo ilegível ou formato inválido.")
            df_raw = clean_column_names(df_raw)

            if sku_input not in df_raw.columns:
                raise ValueError(f"Coluna chave '{sku_input}' não encontrada.")

            df_raw = df_raw.rename(columns={sku_input: SKU_PADRAO_FINAL})
            skus_corrigidos = limpar_sku_cientifico(df_raw[SKU_PADRAO_FINAL])
            df_raw[SKU_PADRAO_FINAL] = skus_corrigidos
            df_raw = df_raw.dropna(subset=[SKU_PADRAO_FINAL])

            colunas_existentes = [c for c in colunas_alvo if c in df_raw.columns]
            colunas_faltantes = [c for c in colunas_alvo if c not in df_raw.columns]
            
            if colunas_faltantes:
                debug_missing_cols[file.name] = {"Faltaram": colunas_faltantes, "Encontradas": list(df_raw.columns)}

            df_selecionado = df_raw[colunas_existentes].copy()
            for col in colunas_faltantes: df_selecionado[col] = pd.NA
            
            df_selecionado = df_selecionado[colunas_alvo]
            lista_dfs.append(df_selecionado)
        except Exception as e:
            log_erros.append(f"❌ ERRO no arquivo **{file.name}**: {str(e)}")
        progress_bar.progress((i + 1) / len(files))

    if log_erros: return None, log_erros, debug_missing_cols
    if not lista_dfs: return None, ["Nenhum dado válido extraído."], debug_missing_cols

    df_consolidado = pd.concat(lista_dfs, ignore_index=True)
    df_consolidado = df_consolidado.dropna(subset=[SKU_PADRAO_FINAL])
    df_consolidado = df_consolidado.drop_duplicates()
    
    # Sanitização (Maiúsculo, Sem Acentos, Sem Pontos)
    cols_para_tratar = cols_atributos + [COL_NOME_SKU]
    for col in cols_para_tratar:
        if col in df_consolidado.columns:
            df_consolidado[col] = df_consolidado[col].apply(padronizar_texto_extrator)

    skus_conflitantes = df_consolidado[df_consolidado.duplicated(subset=[SKU_PADRAO_FINAL], keep=False)]
    return df_consolidado, skus_conflitantes, debug_missing_cols

def exibir_resumo_estatistico(df, colunas_alvo):
    st.markdown("### 📊 Estatísticas do Processamento")
    total_skus = len(df)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de SKUs", total_skus)
    
    total_celulas = total_skus * len(colunas_alvo)
    celulas_preenchidas = df[colunas_alvo].notna().sum().sum()
    perc_global = (celulas_preenchidas / total_celulas) * 100 if total_celulas > 0 else 0
    
    c2.metric("Classificações Realizadas", f"{celulas_preenchidas}")
    c3.metric("Cobertura Global", f"{perc_global:.1f}%")
    st.divider()
    
    st.markdown("#### Detalhamento por Atributo")
    for col in colunas_alvo:
        if col in df.columns:
            series = df[col].fillna("NÃO CLASSIFICADO")
            counts = series.value_counts()
            qtd_preenchidos = df[col].notna().sum()
            qtd_vazios = df[col].isna().sum()
            perc_coluna = (qtd_preenchidos / total_skus) if total_skus > 0 else 0
            cor_status = "🟢" if perc_coluna == 1.0 else "🟡" if perc_coluna > 0.5 else "🔴"
            
            with st.expander(f"{cor_status} {col} ({qtd_preenchidos} classificados / {qtd_vazios} pendentes)"):
                st.progress(perc_coluna)
                st.caption(f"**{perc_coluna:.1f}%** dos SKUs possuem {col}.")
                col_chart, col_table = st.columns([2, 1])
                with col_chart:
                    st.markdown("**Top 10 Valores Encontrados:**")
                    chart_data = counts.head(10).sort_values(ascending=True)
                    st.bar_chart(chart_data, color="#004BDE", horizontal=True)
                with col_table:
                    st.markdown("**Contagem Completa:**")
                    df_counts = counts.reset_index()
                    df_counts.columns = [col, 'Qtd']
                    st.dataframe(df_counts, use_container_width=True, height=300)
