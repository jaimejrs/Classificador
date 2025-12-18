import streamlit as st
import pandas as pd
import re
import io
import os

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Classificador Multi-Indústria", layout="wide", page_icon="🏭")

# --- CONFIGURAÇÃO DE PASTAS ---
PASTA_DICIONARIOS = "dicionarios"

# --- CONFIGURAÇÃO DAS INDÚSTRIAS ---
INDUSTRY_CONFIG = {
    "FROSTY": {
        "arquivo": "dicionario_frosty.xlsx",
        "colunas": ['SUBCATEGORIA', 'SABOR', 'UNIDADE DE MEDIDA', 'Restritivos', 'AÇÚCAR']
    },
    "ALVOAR / BETANIA": {
        "arquivo": "dicionario_alvoar.xlsx",
        "colunas": ['Categoria', 'Subcategoria', 'Sabor', 'Gramatura', 'Embalagem', 'Marca', 'Frio Seco', 'Kids', 'Linha', 'Zero Lactose']
    },
    "AVINE": {
        "arquivo": "dicionario_avine.xlsx",
        "colunas": ['FAMÍLIA DE VENDAS', 'COR', 'TIPO', 'TAMANHO', 'BANDEJA', 'CONCATENADO', 'PERFIL']
    },
    "MINALBA": {
        "arquivo": "dicionario_minalba.xlsx",
        "colunas": ['CATEGORIA', 'SUBCATEGORIA', 'SEGMENTO', 'EMBALAGEM', 'INTERVALO EMBALAGEM', 'TAMANHO EMBALAGEM', 'FORMATO EMBALAGEM', 'MARCA MNB', 'CODIGO MNB', 'Prod Clasif 10']
    },
    "SÃO GERALDO": {
        "arquivo": "dicionario_sao_geraldo.xlsx",
        "colunas": ['TIPO', 'CONSUMO', 'SABOR', 'EMBALAGEM', 'SEM ACUCAR', 'GRAMATURA CSG']
    },
    "M.DIAS BRANCO": {
        "arquivo": "dicionario_mdias.xlsx",
        "colunas": ['SubCategoria MDB', 'Gramatura MDB', 'CLASSIFICAÇÃO DO ITEM', 'Marca', 'Familia', 'SubFamilia', 'SubMarca', 'Unidade de Medida']
    }
}

# --- FUNÇÃO DE LEITURA BLINDADA (PARA O UPLOAD DO USUÁRIO) ---
def ler_arquivo_robusto(uploaded_file):
    """Lê Excel ou CSV do usuário detectando encoding"""
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

# --- CARREGAMENTO DO DICIONÁRIO (AGORA NA PASTA CORRETA) ---
def carregar_dicionario_industria(nome_arquivo):
    """Carrega o dicionário buscando dentro da pasta 'dicionarios'"""
    
    # Monta o caminho completo: dicionarios/arquivo.xlsx
    caminho_completo = os.path.join(PASTA_DICIONARIOS, nome_arquivo)
    
    if not os.path.exists(caminho_completo):
        return None, f"⚠️ Arquivo não encontrado: {caminho_completo}"
    
    try:
        df = pd.read_excel(caminho_completo)
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

# --- PROCESSAMENTO PRINCIPAL ---
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

def processar_dataframe(df_sku, regras_otimizadas, config_industria):
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

# --- INTERFACE ---
st.title("🏭 Classificador Multi-Indústria")

with st.sidebar:
    st.header("1. Selecione a Indústria")
    opcao_industria = st.selectbox("Indústria:", list(INDUSTRY_CONFIG.keys()))
    
    config = INDUSTRY_CONFIG[opcao_industria]
    nome_arquivo_regras = config['arquivo']
    
    # Verifica status
    df_dict, erro_dict = carregar_dicionario_industria(nome_arquivo_regras)
    
    status_container = st.container()
    if erro_dict:
        status_container.error(f"❌ Arquivo não encontrado na pasta 'dicionarios'")
        st.caption(f"Esperado: `dicionarios/{nome_arquivo_regras}`")
        df_dict = None
    else:
        status_container.success(f"✅ Regras carregadas: {len(df_dict)}")

st.write("### 2. Upload da Base de SKUs")
file_sku = st.file_uploader("Carregue a planilha 'Cadastro SKU'", type=['xlsx', 'csv', 'xls'])

if file_sku and df_dict is not None:
    df_sku = ler_arquivo_robusto(file_sku)
    
    if df_sku is not None:
        if 'Nome SKU' not in df_sku.columns:
            st.error("❌ A planilha deve conter a coluna 'Nome SKU'.")
        else:
            st.success("Base carregada com sucesso!")
            with st.expander("Ver dados brutos"):
                st.dataframe(df_sku.head())
            
            if st.button("🚀 Classificar Agora", type="primary"):
                regras_prontas = otimizar_regras(df_dict)
                
                if regras_prontas:
                    with st.spinner(f"Processando regras para {opcao_industria}..."):
                        df_final, df_comp = processar_dataframe(df_sku, regras_prontas, config)
                    
                    st.success("Processamento concluído!")
                    
                    col1, col2 = st.columns(2)
                    
                    buffer_final = io.BytesIO()
                    with pd.ExcelWriter(buffer_final, engine='xlsxwriter') as writer:
                        df_final.to_excel(writer, index=False)
                        
                    col1.download_button("📥 Baixar Classificados (.xlsx)", 
                                       data=buffer_final.getvalue(), 
                                       file_name=f"Classificados_{opcao_industria}.xlsx",
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    
                    if not df_comp.empty:
                        buffer_comp = io.BytesIO()
                        with pd.ExcelWriter(buffer_comp, engine='xlsxwriter') as writer:
                            df_comp.to_excel(writer, index=False)
                        col2.download_button("📊 Baixar Relatório de Mudanças", 
                                           data=buffer_comp.getvalue(), 
                                           file_name="Relatorio_Mudancas.xlsx",
                                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                    else:
                        col2.info("Nenhuma alteração realizada.")
                else:
                    st.error("O arquivo de regras está vazio ou inválido.")
