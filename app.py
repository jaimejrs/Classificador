import streamlit as st
import pandas as pd
import re
import io
import os
import numpy as np
from PIL import Image
from datetime import datetime

# ==============================================================================
# 1. CONFIGURAÇÃO VISUAL E PÁGINA
# ==============================================================================

# Configuração de caminhos
PASTA_DICIONARIOS = "dicionarios"
CAMINHO_ICONE = "assets/ícone.png"
CAMINHO_LOGO = "assets/logo.png"

icone_img = None
logo_img = None
try:
    if os.path.exists(CAMINHO_ICONE): icone_img = Image.open(CAMINHO_ICONE)
    if os.path.exists(CAMINHO_LOGO): logo_img = Image.open(CAMINHO_LOGO)
except Exception:
    pass

st.set_page_config(
    page_title="Suíte de Dados - Classificador & Extrator",
    page_icon=icone_img, 
    layout="wide"
)

# CSS (Estética Visual - COM TEXTO BRANCO NA TABELA)
st.markdown(
    """
    <style>
        /* Ajuste da Logo na Sidebar */
        [data-testid="stSidebar"] > div:first-child { padding-top: 0rem; }
        [data-testid="stSidebar"] img {
            width: 100% !important;
            max-width: 100% !important;
            margin-top: -20px;
        }

        /* Títulos */
        .stMarkdown h4 {
            margin-top: 1rem;
            margin-bottom: 0.5rem;
            color: #014597; /* Azul Escuro */
        }

        /* Botões de Download */
        div.stDownloadButton > button {
            color: #004BDE !important;
            border-color: #004BDE !important;
            background-color: #FFFFFF !important; 
        }
        div.stDownloadButton > button:hover {
            color: #FFFFFF !important;
            background-color: #004BDE !important;
            border-color: #004BDE !important;
        }

        /* Botões de Ação - Classificar/Processar */
        div.stButton > button {
            color: #FFFFFF !important;
            background-color: #004BDE !important;
            border-color: #004BDE !important;
        }
        div.stButton > button:hover {
            background-color: #003AA6 !important;
            border-color: #003AA6 !important;
            color: #FFFFFF !important;
        }
        div.stButton > button p {
            color: #FFFFFF !important;
        }

        /* Alertas de Alto Contraste */
        [data-testid="stAlert"] {
            background-color: #FFD2D2 !important;
            color: #800000 !important;
            border: 1px solid #FF0000 !important;
        }
        [data-testid="stAlert"] p, [data-testid="stAlert"] li, [data-testid="stAlert"] div {
            color: #800000 !important;
            font-weight: 600 !important;
        }
        
        /* Abas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #014597 !important;
            color: #FFFFFF !important;
        }
        
        /* Badges para Colunas */
        .badge-found {
            background-color: #d4edda;
            color: #155724;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
            margin-right: 5px;
            display: inline-block;
            margin-bottom: 5px;
        }
        .badge-missing {
            background-color: #f8d7da;
            color: #721c24;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
            margin-right: 5px;
            display: inline-block;
            margin-bottom: 5px;
        }
        .badge-info {
            background-color: #e2e3e5;
            color: #383d41;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
            margin-right: 5px;
            display: inline-block;
            margin-bottom: 5px;
        }

        /* --- CORREÇÃO VISUAL DA TABELA (st.table) --- */
        [data-testid="stTable"] {
            display: block;
            overflow-x: auto;
        }
        [data-testid="stTable"] table {
            border-collapse: collapse; 
            width: 100%;
            border: 1px solid #004BDE;
        }
        
        /* Cabeçalho da Tabela */
        [data-testid="stTable"] thead th {
            background-color: #004BDE !important; /* Fundo Azul Escuro */
            color: #FFFFFF !important; /* Texto Branco */
            font-weight: bold;
            text-align: center;
        }
        
        /* Corpo da Tabela */
        [data-testid="stTable"] tbody td {
            background-color: transparent !important; /* Fundo Transparente */
            color: #FFFFFF !important; /* Texto Branco Puro */
            border-bottom: 1px solid #555555; /* Linha cinza escura para separar */
        }
        
        /* Força a cor branca em qualquer elemento interno da célula */
        [data-testid="stTable"] tbody td div, 
        [data-testid="stTable"] tbody td span,
        [data-testid="stTable"] tbody td p {
             color: #FFFFFF !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

if logo_img:
    st.sidebar.image(logo_img, use_column_width=True) 
    st.sidebar.markdown("---") 

# ==============================================================================
# 2. CONFIGURAÇÕES DOS PROJETOS
# ==============================================================================

# Configuração para o CLASSIFICADOR (Hierárquico: Indústria -> Categoria -> Arquivo)
CONFIG_CLASSIFICADOR = {
    "M.DIAS BRANCO": {
        "colunas": [
            'Categoría SKU', 'Familia', 'SubFamilia', 'Marca', 'SubMarca', 
            'Gramatura MDB', 'SubCategoria MDB', 'CLASSIFICAÇÃO DO ITEM', 'Unidade de Medida'
        ],
        "arquivos": {
            "Aveia": "dicionario_mdias_aveia.xlsx",
            "Biscoitos": "dicionario_mdias_biscoitos.xlsx",
            "Granola": "dicionario_mdias_granola.xlsx",
            "Massas Instantâneas": "dicionario_mdias_massa_inst.xlsx",
            "Massas Alimentícias": "dicionario_mdias_massas_alim.xlsx",
            "Pão": "dicionario_mdias_pao.xlsx"
        }
    },
    "ALVOAR / BETANIA": {
        "colunas": [
            'Categoria', 'Subcategoria', 'Sabor', 'Gramatura', 
            'Embalagem', 'Marca', 'Frio Seco', 'Kids', 'Linha', 'Zero Lactose'
        ],
        "arquivos": {
            "Coalhada": "dicionario_alvoar_coalhada.xlsx",
            "Cream Cheese": "dicionario_alvoar_cream_cheese.xlsx",
            "Iogurte": "dicionario_alvoar_iogurte.xlsx",
            "Leite Sabor": "dicionario_alvoar_leite_sabor.xlsx",
            "Queijos": "dicionario_alvoar_queijos.xlsx"
        }
    },
    "FROSTY": {
        "colunas": ['SUBCATEGORIA', 'SABOR', 'UNIDADE DE MEDIDA', 'Restritivos', 'AÇÚCAR'],
        "arquivos": {
             "Sorvete Massa": "dicionario_frosty_sorvete_massa.xlsx",
             "Sorvete Palito": "dicionario_frosty_sorvete_palito.xlsx",
             "Açaí": "dicionario_frosty_acai.xlsx",
             "Polpa de Frutas": "dicionario_frosty_polpa_frutas.xlsx",
             "Gelo Saborizado": "dicionario_frosty_gelo_saborizado.xlsx"
        }
    },
    "AVINE": {
        "colunas": ['FAMÍLIA DE VENDAS', 'COR', 'TIPO', 'TAMANHO', 'BANDEJA', 'CONCATENADO', 'PERFIL'],
        "arquivos": { "Total": "dicionario_avine.xlsx" }
    },
    "MINALBA": {
        "colunas": ['CATEGORIA', 'SUBCATEGORIA', 'SEGMENTO', 'EMBALAGEM', 'INTERVALO EMBALAGEM', 'TAMANHO EMBALAGEM', 'FORMATO EMBALAGEM', 'MARCA MNB', 'CODIGO MNB', 'Prod Clasif 10'],
        "arquivos": { "Total": "dicionario_minalba.xlsx" }
    },
    "SÃO GERALDO (CAJUINA)": {
        "colunas": ['TIPO', 'CONSUMO', 'SABOR', 'EMBALAGEM', 'SEM ACUCAR', 'GRAMATURA CSG'],
        "arquivos": { "Total": "dicionario_cajuina.xlsx" }
    }
}

# Configuração para o EXTRATOR (Plano: Indústria -> Colunas Alvo)
CONFIG_EXTRATOR = {
    "ALVOAR / BETANIA": {
        "sku_origem": "Código Barras SKU",
        "colunas_atributos": [
            'Categoria', 'Subcategoria', 'Sabor', 'Gramatura', 
            'Embalagem', 'Marca', 'Frio Seco', 'Kids', 'Linha', 'Zero Lactose'
        ]
    },
    "AVINE": {
        "sku_origem": "Código Barras SKU",
        "colunas_atributos": [
            'FAMÍLIA DE VENDAS', 'COR', 'TIPO', 'TAMANHO', 
            'BANDEJA', 'CONCATENADO', 'PERFIL'
        ]
    },
    "FROSTY": {
        "sku_origem": "Código Barras SKU",
        "colunas_atributos": [
            'SUBCATEGORIA', 'SABOR', 'UNIDADE DE MEDIDA', 
            'Restritivos', 'AÇÚCAR'
        ]
    },
    "MINALBA": {
        "sku_origem": "Código Barras SKU",
        "colunas_atributos": [
            'CATEGORIA', 'SUBCATEGORIA', 'SEGMENTO', 'EMBALAGEM', 
            'INTERVALO EMBALAGEM', 'TAMANHO EMBALAGEM', 
            'FORMATO EMBALAGEM', 'MARCA MNB', 'CODIGO MNB', 'Prod Clasif 10'
        ]
    },
    "SÃO GERALDO (CAJUINA)": {
        "sku_origem": "Código Barras SKU",
        "colunas_atributos": [
            'TIPO', 'CONSUMO', 'SABOR', 'EMBALAGEM', 
            'SEM ACUCAR', 'GRAMATURA CSG'
        ]
    },
    "M.DIAS BRANCO": {
        "sku_origem": "Código Barras SKU",
        "colunas_atributos": [
            'SubCategoria MDB', 'Gramatura MDB', 'CLASSIFICAÇÃO DO ITEM', 
            'Marca', 'Familia', 'SubFamilia', 'SubMarca', 'Unidade de Medida'
        ]
    }
}

SKU_PADRAO_FINAL = "Código Barras SKU"

# ==============================================================================
# 3. FUNÇÕES UTILITÁRIAS COMUNS
# ==============================================================================

def get_data_atual_str():
    """Retorna data atual formatada para nome de arquivo (dd-mm-yyyy)."""
    return datetime.now().strftime("%d-%m-%Y")

def ler_arquivo_robusto(uploaded_file):
    """Lê Excel ou CSV do usuário detectando encoding."""
    filename = uploaded_file.name.lower()
    
    if filename.endswith(('.xlsx', '.xls')):
        try:
            return pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Erro ao ler Excel: {e}")
            return None

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

def to_excel_bytes(df):
    """Converte DataFrame para bytes Excel para download."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def clean_column_names(df):
    """Limpa nomes das colunas (strip, remove pontos finais)."""
    df.columns = df.columns.astype(str).str.strip().str.strip('.').str.replace(r'\s+', ' ', regex=True)
    return df

def limpar_sku_cientifico(serie):
    """Converte SKUs numéricos/científicos para string limpa."""
    serie_numerica = pd.to_numeric(serie, errors='coerce')
    serie_valida = serie_numerica.dropna()
    return serie_valida.astype(np.int64).astype(str)

# ==============================================================================
# 4. FUNÇÕES ESPECÍFICAS DO CLASSIFICADOR (ABA 1)
# ==============================================================================

def carregar_dicionario_industria(nome_arquivo):
    """Carrega o dicionário buscando dentro da pasta 'dicionarios'."""
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
        
        if tipo_regra not in regras_otimizadas:
            regras_otimizadas[tipo_regra] = []
            
        try:
            regras_otimizadas[tipo_regra].append({
                'pattern': re.compile(regex_pattern, re.IGNORECASE),
                'value': interpretacao,
                'score': int(score)
            })
        except re.error:
            continue
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
        if col not in df_processado.columns:
            df_processado[col] = None
            
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

# ==============================================================================
# 5. FUNÇÕES ESPECÍFICAS DO EXTRATOR (ABA 2)
# ==============================================================================

def processar_arquivos_extrator(files, config_industria):
    lista_dfs = []
    log_erros = []
    debug_missing_cols = {} 
    
    sku_input = config_industria["sku_origem"]
    cols_atributos = config_industria["colunas_atributos"]
    colunas_alvo = [SKU_PADRAO_FINAL] + cols_atributos

    progress_bar = st.progress(0)
    
    for i, file in enumerate(files):
        try:
            df_raw = pd.read_excel(file)
            df_raw = clean_column_names(df_raw)

            if sku_input not in df_raw.columns:
                raise ValueError(f"A coluna chave '{sku_input}' não foi encontrada. Colunas detectadas: {list(df_raw.columns)}")

            df_raw = df_raw.rename(columns={sku_input: SKU_PADRAO_FINAL})

            skus_corrigidos = limpar_sku_cientifico(df_raw[SKU_PADRAO_FINAL])
            df_raw[SKU_PADRAO_FINAL] = skus_corrigidos
            df_raw = df_raw.dropna(subset=[SKU_PADRAO_FINAL])

            colunas_existentes = [c for c in colunas_alvo if c in df_raw.columns]
            colunas_faltantes = [c for c in colunas_alvo if c not in df_raw.columns]
            
            if colunas_faltantes:
                debug_missing_cols[file.name] = {
                    "Faltaram": colunas_faltantes,
                    "Encontradas": list(df_raw.columns) 
                }

            df_selecionado = df_raw[colunas_existentes].copy()
            for col in colunas_faltantes:
                df_selecionado[col] = pd.NA
            
            df_selecionado = df_selecionado[colunas_alvo]
            lista_dfs.append(df_selecionado)
            
        except Exception as e:
            log_erros.append(f"❌ ERRO CRÍTICO no arquivo **{file.name}**: {str(e)}")
        
        progress_bar.progress((i + 1) / len(files))

    if log_erros:
        return None, log_erros, debug_missing_cols

    if not lista_dfs:
        return None, ["Nenhum dado válido extraído."], debug_missing_cols

    df_consolidado = pd.concat(lista_dfs, ignore_index=True)
    df_consolidado = df_consolidado.dropna(subset=[SKU_PADRAO_FINAL])
    df_consolidado = df_consolidado.drop_duplicates()
    
    skus_conflitantes = df_consolidado[df_consolidado.duplicated(subset=[SKU_PADRAO_FINAL], keep=False)]
    
    return df_consolidado, skus_conflitantes, debug_missing_cols

# ==============================================================================
# 7. FUNÇÃO DE ESTATÍSTICAS (NOVA)
# ==============================================================================

def exibir_resumo_estatistico(df, colunas_alvo):
    """Gera dashboards visuais sobre o resultado da classificação."""
    
    st.markdown("### 📊 Estatísticas do Processamento")
    
    total_skus = len(df)
    
    # Métricas Globais
    c1, c2, c3 = st.columns(3)
    c1.metric("Total de SKUs", total_skus)
    
    # Cálculo total de preenchimento
    total_celulas = total_skus * len(colunas_alvo)
    celulas_preenchidas = df[colunas_alvo].notna().sum().sum()
    perc_global = (celulas_preenchidas / total_celulas) * 100 if total_celulas > 0 else 0
    
    c2.metric("Classificações Realizadas", f"{celulas_preenchidas}")
    c3.metric("Cobertura Global", f"{perc_global:.1f}%")
    
    st.divider()
    
    # Detalhamento por Atributo
    st.markdown("#### Detalhamento por Atributo")
    
    for col in colunas_alvo:
        if col in df.columns:
            # Preparação dos dados
            series = df[col].fillna("NÃO CLASSIFICADO")
            counts = series.value_counts()
            
            qtd_preenchidos = df[col].notna().sum()
            qtd_vazios = df[col].isna().sum()
            perc_coluna = (qtd_preenchidos / total_skus) if total_skus > 0 else 0
            
            # Cor do status baseada na completude
            cor_status = "🟢" if perc_coluna == 1.0 else "🟡" if perc_coluna > 0.5 else "🔴"
            
            with st.expander(f"{cor_status} {col} ({qtd_preenchidos} classificados / {qtd_vazios} pendentes)"):
                
                # Barra de Progresso Visual
                st.progress(perc_coluna)
                st.caption(f"**{perc_coluna:.1f}%** dos SKUs possuem {col}.")
                
                col_chart, col_table = st.columns([2, 1])
                
                with col_chart:
                    st.markdown("**Top 10 Valores Encontrados:**")
                    # Filtra apenas o top 10 para o gráfico não ficar gigante
                    chart_data = counts.head(10).sort_values(ascending=True)
                    st.bar_chart(chart_data, color="#004BDE", horizontal=True)
                
                with col_table:
                    st.markdown("**Contagem Completa:**")
                    # Tabela com todos os valores
                    df_counts = counts.reset_index()
                    df_counts.columns = [col, 'Qtd']
                    st.dataframe(df_counts, use_container_width=True, height=300)

# ==============================================================================
# 6. INTERFACE PRINCIPAL
# ==============================================================================

def main():
    st.title("🏭 Central de Dados")
    
    tab_classificador, tab_extrator = st.tabs(["🧩 Classificador Inteligente", "🗃️ Extrator & Fragmentador"])

    # -------------------------------------------------------------------------
    # ABA 1: CLASSIFICADOR (Lógica de Regex)
    # -------------------------------------------------------------------------
    with tab_classificador:
        st.header("Classificação por Dicionários")
        st.caption("Utilize dicionários de regras (Regex) para preencher atributos automaticamente.")

        # --- SESSION STATE ABA 1 ---
        if 'class_concluido' not in st.session_state: st.session_state['class_concluido'] = False
        if 'class_df_final' not in st.session_state: st.session_state['class_df_final'] = None
        if 'class_df_comp' not in st.session_state: st.session_state['class_df_comp'] = None

        col_ind, col_cat = st.columns(2)
        with col_ind:
            ind_class = st.selectbox("1. Indústria:", list(CONFIG_CLASSIFICADOR.keys()), key="sb_ind_class")
        
        config_class = CONFIG_CLASSIFICADOR[ind_class]
        
        with col_cat:
            opcoes_cat = list(config_class['arquivos'].keys())
            cat_class = st.selectbox("2. Categoria:", opcoes_cat, key="sb_cat_class")

        nome_arq_regras = config_class['arquivos'][cat_class]
        
        # Carrega dicionário
        df_dict, erro_dict = carregar_dicionario_industria(nome_arq_regras)
        
        if erro_dict:
            st.error("Erro ao carregar dicionário de regras.")
            st.caption(erro_dict)
        else:
            st.info(f"📚 Dicionário ativo: `{nome_arq_regras}` ({len(df_dict)} regras)")
            
            st.markdown("### 3. Upload da Base")
            file_sku_class = st.file_uploader(f"Base de SKUs ({ind_class} - {cat_class})", type=['xlsx', 'csv', 'xls'], key="up_class")

            # ---------------------------------------------
            #  NOVO: PRÉ-VISUALIZAÇÃO (ABA CLASSIFICADOR)
            # ---------------------------------------------
            if file_sku_class:
                st.divider()
                with st.expander("🔍 Pré-visualização e Diagnóstico (Clique para abrir)", expanded=True):
                    # Ler arquivo para preview
                    df_preview = ler_arquivo_robusto(file_sku_class)
                    file_sku_class.seek(0) # IMPORTANTE: Rebobinar

                    if df_preview is not None:
                        df_preview = clean_column_names(df_preview)
                        cols_found = set(df_preview.columns)
                        
                        st.markdown("##### Diagnóstico de Colunas")
                        # Verifica apenas a coluna mandatória para classificar
                        if 'Nome SKU' in cols_found:
                            st.markdown('<span class="badge-found">✅ Coluna Obrigatória: Nome SKU</span>', unsafe_allow_html=True)
                        else:
                            st.markdown('<span class="badge-missing">❌ Faltando: Nome SKU</span>', unsafe_allow_html=True)
                            st.error("ERRO: O arquivo precisa ter uma coluna chamada 'Nome SKU' para o classificador funcionar.")

                        # Informa as outras colunas encontradas
                        other_cols = cols_found - {'Nome SKU'}
                        if other_cols:
                            html_others = ""
                            for c in list(other_cols)[:5]: 
                                html_others += f'<span class="badge-info">{c}</span>'
                            if len(other_cols) > 5:
                                html_others += f'<span class="badge-info">... e mais {len(other_cols)-5}</span>'
                            
                            st.markdown("**Outras colunas encontradas:**")
                            st.markdown(html_others, unsafe_allow_html=True)

                        st.markdown("##### Amostra de Dados")
                        # USO DE st.table para forçar o CSS de contraste
                        st.table(df_preview.head()) 
                    else:
                        st.error("Erro ao ler o arquivo para pré-visualização.")
                st.divider()

            # Botão de Classificar
            if file_sku_class:
                if st.button("🚀 Classificar", type="primary", key="btn_class"):
                    df_sku = ler_arquivo_robusto(file_sku_class)
                    if df_sku is not None:
                        df_sku.columns = df_sku.columns.str.strip()
                        if 'Nome SKU' not in df_sku.columns:
                            st.error("❌ A planilha deve conter a coluna 'Nome SKU'.")
                        else:
                            regras = otimizar_regras(df_dict)
                            if regras:
                                with st.spinner("Classificando..."):
                                    df_final, df_comp = processar_dataframe_classificador(df_sku, regras, config_class)
                                
                                st.session_state['class_df_final'] = df_final
                                st.session_state['class_df_comp'] = df_comp
                                st.session_state['class_concluido'] = True
                                st.rerun()

            # EXIBIÇÃO PERSISTENTE DOS RESULTADOS
            if st.session_state['class_concluido'] and st.session_state['class_df_final'] is not None:
                st.success("Processamento Concluído!")
                
                # --- ÁREA DE DOWNLOADS ---
                c1, c2 = st.columns(2)
                
                data_hoje = get_data_atual_str()
                nome_base_out = f"Classificados_{ind_class}_{cat_class}".replace(" ", "_").replace("/", "-")
                nome_final_out = f"{nome_base_out}_{data_hoje}.xlsx"
                nome_mudancas_out = f"Mudancas_{data_hoje}.xlsx"

                c1.download_button(
                    "📥 Baixar Classificados", 
                    data=to_excel_bytes(st.session_state['class_df_final']), 
                    file_name=nome_final_out,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                if not st.session_state['class_df_comp'].empty:
                    c2.download_button(
                        "📊 Relatório de Mudanças", 
                        data=to_excel_bytes(st.session_state['class_df_comp']), 
                        file_name=nome_mudancas_out,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    c2.info("Sem alterações.")
                
                # --- NOVO: CHAMADA DAS ESTATÍSTICAS ---
                st.markdown("---")
                exibir_resumo_estatistico(st.session_state['class_df_final'], config_class['colunas'])
                # --------------------------------------

                if st.button("🔄 Limpar Classificador", key="limpar_class"):
                    st.session_state['class_concluido'] = False
                    st.session_state['class_df_final'] = None
                    st.session_state['class_df_comp'] = None
                    st.rerun()

    # -------------------------------------------------------------------------
    # ABA 2: EXTRATOR (Lógica de Fragmentação)
    # -------------------------------------------------------------------------
    with tab_extrator:
        st.header("Extrator de Planilhas")
        st.caption("Consolide arquivos e gere planilhas de atributos separadas.")

        # Session State Específico do Extrator
        if 'ext_arquivos' not in st.session_state: st.session_state['ext_arquivos'] = {}
        if 'ext_concluido' not in st.session_state: st.session_state['ext_concluido'] = False
        if 'ext_erros' not in st.session_state: st.session_state['ext_erros'] = []
        if 'ext_ignorado' not in st.session_state: st.session_state['ext_ignorado'] = []
        if 'ext_conflitos' not in st.session_state: st.session_state['ext_conflitos'] = None
        if 'ext_debug' not in st.session_state: st.session_state['ext_debug'] = {}

        ind_ext = st.selectbox("1. Selecione a Indústria:", list(CONFIG_EXTRATOR.keys()), key="sb_ind_ext")
        config_ext = CONFIG_EXTRATOR[ind_ext]

        st.markdown(f"**Clave:** `{config_ext['sku_origem']}`")
        st.caption("Atributos: " + ", ".join(config_ext['colunas_atributos']))

        files_ext = st.file_uploader("2. Carregue os arquivos Excel:", accept_multiple_files=True, type=["xlsx"], key="up_ext")

        # ---------------------------------------------
        #  PRÉ-VISUALIZAÇÃO (ABA EXTRATOR)
        # ---------------------------------------------
        if files_ext:
            st.divider()
            with st.expander("🔍 Pré-visualização e Diagnóstico de Colunas (Clique para abrir)", expanded=True):
                file_names = [f.name for f in files_ext]
                selected_file_name = st.selectbox("Selecione um arquivo para inspecionar:", file_names)
                
                selected_file = next(f for f in files_ext if f.name == selected_file_name)
                
                # Ler arquivo para preview
                df_preview = ler_arquivo_robusto(selected_file)
                selected_file.seek(0) # IMPORTANTE: Rebobinar
                
                if df_preview is not None:
                    df_preview = clean_column_names(df_preview)
                    
                    colunas_encontradas = set(df_preview.columns)
                    colunas_esperadas = set([config_ext['sku_origem']] + config_ext['colunas_atributos'])
                    
                    cols_ok = colunas_esperadas.intersection(colunas_encontradas)
                    cols_missing = colunas_esperadas - colunas_encontradas
                    
                    st.markdown("##### Diagnóstico de Colunas")
                    
                    html_cols = ""
                    for col in sorted(list(cols_ok)):
                        html_cols += f'<span class="badge-found">✅ {col}</span>'
                    for col in sorted(list(cols_missing)):
                        html_cols += f'<span class="badge-missing">❌ {col}</span>'
                    
                    st.markdown(html_cols, unsafe_allow_html=True)
                    
                    if cols_missing:
                        st.warning(f"Atenção: Este arquivo não possui {len(cols_missing)} colunas esperadas pela configuração.")
                    else:
                        st.success("Todas as colunas esperadas foram encontradas!")

                    st.markdown("##### Amostra de Dados (5 primeiras linhas)")
                    # USO DE st.table para forçar o CSS de contraste
                    st.table(df_preview.head())
                else:
                    st.error("Não foi possível ler este arquivo para pré-visualização.")
            st.divider()

        if files_ext:
            if st.button("🚀 Processar Arquivos", key="btn_ext_proc"):
                # Reset
                st.session_state['ext_arquivos'] = {}
                st.session_state['ext_erros'] = []
                st.session_state['ext_ignorado'] = []
                st.session_state['ext_concluida'] = False
                
                df_final_ext, conflitos_ext, debug_ext = processar_arquivos_extrator(files_ext, config_ext)

                if df_final_ext is None:
                    st.session_state['ext_erros'] = conflitos_ext
                else:
                    st.session_state['ext_conflitos'] = conflitos_ext
                    st.session_state['ext_debug'] = debug_ext
                    st.session_state['ext_concluido'] = True
                    
                    # Gerar arquivos
                    arquivos_out = {}
                    relatorio_skip = []

                    # Mestre com DATA
                    data_hoje = get_data_atual_str()
                    nome_mestre = f"Mestre_Completo_{data_hoje}.xlsx"
                    arquivos_out[nome_mestre] = df_final_ext
                    
                    # Fragmentar
                    for col in config_ext["colunas_atributos"]:
                        if col in df_final_ext.columns:
                            sub_df = df_final_ext[[SKU_PADRAO_FINAL, col]].dropna()
                            if not sub_df.empty:
                                sub_df = sub_df[sub_df[col].astype(str).str.strip() != ""]
                            
                            if not sub_df.empty:
                                total_sub = len(sub_df)
                                nome_base = f"Planilha_{col.replace(' ', '_')}"
                                if total_sub > 9000:
                                    num_partes = int(np.ceil(total_sub / 9000))
                                    partes = np.array_split(sub_df, num_partes)
                                    for idx, parte in enumerate(partes):
                                        arquivos_out[f"{nome_base}_Parte_{idx+1}.xlsx"] = parte
                                else:
                                    arquivos_out[f"{nome_base}.xlsx"] = sub_df
                            else:
                                relatorio_skip.append(f"⚠️ {col}: Vazia (Ignorada).")
                        else:
                            relatorio_skip.append(f"❌ {col}: Não encontrada.")
                    
                    st.session_state['ext_arquivos'] = arquivos_out
                    st.session_state['ext_ignorado'] = relatorio_skip
                    st.rerun()

        # Exibição de Resultados do Extrator
        if st.session_state['ext_erros']:
            st.error("⛔ Erros críticos encontrados:")
            for erro in st.session_state['ext_erros']:
                st.error(erro)

        if st.session_state['ext_concluido']:
            st.markdown("---")
            st.header("3. Resultados")

            if st.session_state['ext_ignorado']:
                with st.expander("⚠️ Relatório de Colunas Vazias/Ignoradas"):
                    for msg in st.session_state['ext_ignorado']: st.text(msg)

            conflitos = st.session_state['ext_conflitos']
            if conflitos is not None and not conflitos.empty:
                st.error(f"🚨 {conflitos[SKU_PADRAO_FINAL].nunique()} SKUs com divergências (Duplicados).")
                st.download_button("📥 Baixar Erros", data=to_excel_bytes(conflitos), file_name="ERROS_DUPLICIDADE.xlsx", key="dl_err_ext")

            st.subheader("Downloads")
            arquivos = st.session_state['ext_arquivos']
            
            # Mestre (Busca dinâmica pelo nome com data)
            mestre_key = next((k for k in arquivos.keys() if "Mestre_Completo" in k), None)
            
            if mestre_key:
                st.download_button(
                    "📦 Baixar Mestre Consolidado", 
                    data=to_excel_bytes(arquivos[mestre_key]), 
                    file_name=mestre_key, 
                    key="dl_mestre"
                )
            
            st.markdown("#### Planilhas Fragmentadas")
            cols_layout = st.columns(2)
            i = 0
            for nome, df_arq in arquivos.items():
                if "Mestre" not in nome:
                    with cols_layout[i % 2]:
                        st.download_button(f"📥 {nome}", data=to_excel_bytes(df_arq), file_name=nome, key=f"dl_{nome}")
                    i += 1
            
            if st.button("🔄 Limpar Extrator"):
                for key in ['ext_arquivos', 'ext_concluido', 'ext_erros', 'ext_ignorado', 'ext_conflitos', 'ext_debug']:
                    del st.session_state[key]
                st.rerun()

if __name__ == "__main__":
    main()
