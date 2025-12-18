import streamlit as st
import pandas as pd
import re
import io
import os

# --- CONFIGURAÇÃO DA PÁGINA (DEVE SER A PRIMEIRA LINHA) ---
st.set_page_config(page_title="Classificador Master de SKUs", layout="wide", page_icon="🏭")

# --- CONFIGURAÇÕES GERAIS ---
CAMINHO_DICIONARIO_SISTEMA = "dicionario_regras.xlsx"

INDUSTRY_CONFIG = {
    "ALVOAR / BETANIA": ['Categoria', 'Subcategoria', 'Sabor', 'Gramatura', 'Embalagem', 'Marca', 'Frio Seco', 'Kids', 'Linha', 'Zero Lactose'],
    "AVINE": ['FAMÍLIA DE VENDAS', 'COR', 'TIPO', 'TAMANHO', 'BANDEJA', 'CONCATENADO', 'PERFIL'],
    "FROSTY": ['SUBCATEGORIA', 'SABOR', 'UNIDADE DE MEDIDA', 'Restritivos', 'AÇÚCAR'],
    "MINALBA": ['CATEGORIA', 'SUBCATEGORIA', 'SEGMENTO', 'EMBALAGEM', 'INTERVALO EMBALAGEM', 'TAMANHO EMBALAGEM', 'FORMATO EMBALAGEM', 'MARCA MNB', 'CODIGO MNB', 'Prod Clasif 10'],
    "SÃO GERALDO": ['TIPO', 'CONSUMO', 'SABOR', 'EMBALAGEM', 'SEM ACUCAR', 'GRAMATURA CSG'],
    "M.DIAS BRANCO": ['SubCategoria MDB', 'Gramatura MDB', 'CLASSIFICAÇÃO DO ITEM', 'Marca', 'Familia', 'SubFamilia', 'SubMarca', 'Unidade de Medida']
}

# --- FUNÇÕES DE LEITURA ROBUSTA (CORREÇÃO DE ERROS DE ENCODING) ---
def ler_arquivo_robusto(uploaded_file):
    """
    Tenta ler o arquivo enviado (Excel ou CSV) lidando com diferentes 
    codificações (UTF-8, Latin-1, UTF-16) para evitar erros.
    """
    filename = uploaded_file.name.lower()
    
    # 1. Se for Excel (.xlsx, .xls)
    if filename.endswith(('.xlsx', '.xls')):
        try:
            return pd.read_excel(uploaded_file)
        except Exception as e:
            st.error(f"Erro ao ler Excel: {e}")
            return None

    # 2. Se for CSV, tenta várias codificações
    if filename.endswith('.csv'):
        encodings_para_testar = ['utf-8', 'latin1', 'utf-16', 'cp1252']
        separadores_para_testar = [',', ';', '\t']
        
        # Loop para tentar combinações
        for encoding in encodings_para_testar:
            for sep in separadores_para_testar:
                try:
                    uploaded_file.seek(0) # Reseta o ponteiro do arquivo
                    df = pd.read_csv(uploaded_file, encoding=encoding, sep=sep)
                    
                    # Validação simples: se leu apenas 1 coluna, provavelmente o separador está errado
                    if df.shape[1] > 1:
                        return df
                except Exception:
                    continue
        
        st.error("Não foi possível ler o arquivo CSV. Tente salvá-lo como 'Excel Workbook (.xlsx)'.")
        return None

    st.error("Formato de arquivo não suportado. Use .xlsx ou .csv")
    return None

# --- CARREGAMENTO DO DICIONÁRIO ---
@st.cache_data
def carregar_dicionario_sistema():
    """Carrega o dicionário fixo do repositório para memória"""
    if not os.path.exists(CAMINHO_DICIONARIO_SISTEMA):
        return None, f"Erro: O arquivo '{CAMINHO_DICIONARIO_SISTEMA}' não foi encontrado no repositório."
    
    try:
        # Lê o dicionário (assume que o dicionário interno está sempre correto em .xlsx)
        df = pd.read_excel(CAMINHO_DICIONARIO_SISTEMA)
        return df, None
    except Exception as e:
        return None, f"Erro ao ler o Dicionário de Regras: {e}"

def otimizar_regras(df_dict):
    """Transforma o DataFrame em estrutura de dicionário otimizado para busca"""
    regras_otimizadas = {}
    
    # Validação de colunas obrigatórias
    cols_necessarias = ['Tipo de Regra', 'Valor da Regra', 'Interpretação', 'Grau de Associação']
    if not all(col in df_dict.columns for col in cols_necessarias):
        st.error(f"O Dicionário deve ter as colunas: {cols_necessarias}")
        return {}

    for _, row in df_dict.iterrows():
        tipo_regra = str(row['Tipo de Regra']).strip() # A coluna destino (Ex: SABOR)
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

# --- LÓGICA DE CLASSIFICAÇÃO ---

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

def processar_dataframe(df_sku, regras_otimizadas, industria):
    colunas_alvo = INDUSTRY_CONFIG[industria]
    df_processado = df_sku.copy()
    comparativo_data = []
    
    barra_progresso = st.progress(0)
    status_text = st.empty()
    
    # 1. Garante que as colunas alvo existam no DataFrame
    for col in colunas_alvo:
        if col not in df_processado.columns:
            df_processado[col] = None
    
    # 2. Itera sobre cada coluna que precisa ser classificada
    for i, col_alvo in enumerate(colunas_alvo):
        status_text.text(f"Processando coluna: {col_alvo}...")
        barra_progresso.progress((i + 1) / len(colunas_alvo))
        
        # Verifica se temos regras para essa coluna específica no dicionário
        if col_alvo in regras_otimizadas:
            lista_regras = regras_otimizadas[col_alvo]
            
            # Aplica a classificação
            if 'Nome SKU' not in df_processado.columns:
                st.error("A coluna 'Nome SKU' é obrigatória na planilha de produtos.")
                return df_processado, pd.DataFrame()

            novos_valores = df_processado['Nome SKU'].apply(lambda x: classificar_item(x, lista_regras))
            
            # Lógica de comparação (Antes vs Depois)
            old_values = df_processado[col_alvo]
            
            # Atualiza o DataFrame (combine_first mantém o original se o novo for None)
            # Se quiser forçar a reclassificação sempre, use apenas a atribuição direta onde não for nulo
            df_processado[col_alvo] = novos_valores.combine_first(df_processado[col_alvo])
            
            # Gera dados para o relatório
            for idx, (old, new) in enumerate(zip(old_values, df_processado[col_alvo])):
                # Se mudou o valor e o novo não é nulo
                if str(old) != str(new) and pd.notna(new):
                    sku_id = df_processado.iloc[idx].get('Código Barras SKU', idx)
                    comparativo_data.append({
                        'SKU ID': sku_id,
                        'Descrição': df_processado.iloc[idx]['Nome SKU'],
                        'Coluna Afetada': col_alvo,
                        'Valor Original': old,
                        'Valor Novo': new
                    })
    
    barra_progresso.empty()
    status_text.empty()
    return df_processado, pd.DataFrame(comparativo_data)

# --- INTERFACE PRINCIPAL DO STREAMLIT ---

st.title("🏭 Classificador Inteligente de SKUs")
st.markdown("""
Esta ferramenta classifica automaticamente seus produtos baseando-se em regras de texto (Regex).
""")

# --- SIDEBAR (Barra Lateral) ---
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Carregamento do Dicionário
    df_dict, erro = carregar_dicionario_sistema()
    
    if erro:
        st.error("❌ ERRO NO DICIONÁRIO")
        st.warning(erro)
        st.stop()
    else:
        st.success(f"✅ Dicionário Carregado: {len(df_dict)} regras")
        
    st.divider()
    
    # Seleção da Indústria
    industria_selecionada = st.selectbox("Selecione a Indústria:", list(INDUSTRY_CONFIG.keys()))
    
    st.info(f"Colunas Alvo:\n" + ", ".join(INDUSTRY_CONFIG[industria_selecionada]))

# --- ÁREA PRINCIPAL ---

st.write("### 📂 Upload da Base de Dados")
file_sku = st.file_uploader("Carregue a planilha 'Cadastro SKU' (.xlsx ou .csv)", type=['xlsx', 'csv', 'xls'])

if file_sku:
    # Usa a função robusta para ler o arquivo
    df_sku = ler_arquivo_robusto(file_sku)
    
    if df_sku is not None:
        st.success("Arquivo lido com sucesso!")
        with st.expander("Ver prévia dos dados"):
            st.dataframe(df_sku.head())
        
        # Botão de Ação
        if st.button("🚀 Iniciar Classificação", type="primary"):
            
            # Prepara as regras
            regras_prontas = otimizar_regras(df_dict)
            
            if not regras_prontas:
                st.error("Não há regras válidas carregadas. Verifique o dicionário.")
            else:
                with st.spinner("Classificando SKUs... isso pode levar alguns instantes."):
                    df_final, df_comp = processar_dataframe(df_sku, regras_prontas, industria_selecionada)
                
                st.balloons()
                st.success("✅ Processamento Concluído!")
                
                # --- ÁREA DE DOWNLOADS ---
                col1, col2 = st.columns(2)
                
                # 1. Download Base Classificada
                buffer_final = io.BytesIO()
                with pd.ExcelWriter(buffer_final, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False, sheet_name="Base Classificada")
                
                col1.download_button(
                    label="📥 Baixar Base Classificada (.xlsx)",
                    data=buffer_final.getvalue(),
                    file_name=f"SKU_{industria_selecionada}_Classificado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                # 2. Download Relatório de Alterações
                if not df_comp.empty:
                    buffer_comp = io.BytesIO()
                    with pd.ExcelWriter(buffer_comp, engine='xlsxwriter') as writer:
                        df_comp.to_excel(writer, index=False, sheet_name="Alterações")
                    
                    col2.download_button(
                        label="📊 Baixar Relatório de Mudanças (.xlsx)",
                        data=buffer_comp.getvalue(),
                        file_name="Relatorio_Alteracoes.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    col2.info("ℹ️ Nenhuma alteração foi necessária (nenhuma regra encontrada ou dados já estavam preenchidos).")

    else:
        st.warning("Aguardando um arquivo válido para começar.")

else:
    st.info("👆 Faça o upload da planilha 'Cadastro SKU' acima para começar.")
