import streamlit as st
import pandas as pd
import re
import io
import os

# --- CONFIGURAÇÃO ---
# Nome exato do arquivo que você vai colocar no GitHub junto com o código
CAMINHO_DICIONARIO_SISTEMA = "dicionario_regras.xlsx"

INDUSTRY_CONFIG = {
    "ALVOAR / BETANIA": ['Categoria', 'Subcategoria', 'Sabor', 'Gramatura', 'Embalagem', 'Marca', 'Frio Seco', 'Kids', 'Linha', 'Zero Lactose'],
    "AVINE": ['FAMÍLIA DE VENDAS', 'COR', 'TIPO', 'TAMANHO', 'BANDEJA', 'CONCATENADO', 'PERFIL'],
    "FROSTY": ['SUBCATEGORIA', 'SABOR', 'UNIDADE DE MEDIDA', 'Restritivos', 'AÇÚCAR'],
    "MINALBA": ['CATEGORIA', 'SUBCATEGORIA', 'SEGMENTO', 'EMBALAGEM', 'INTERVALO EMBALAGEM', 'TAMANHO EMBALAGEM', 'FORMATO EMBALAGEM', 'MARCA MNB', 'CODIGO MNB', 'Prod Clasif 10'],
    "SÃO GERALDO": ['TIPO', 'CONSUMO', 'SABOR', 'EMBALAGEM', 'SEM ACUCAR', 'GRAMATURA CSG'],
    "M.DIAS BRANCO": ['SubCategoria MDB', 'Gramatura MDB', 'CLASSIFICAÇÃO DO ITEM', 'Marca', 'Familia', 'SubFamilia', 'SubMarca', 'Unidade de Medida']
}

# --- FUNÇÕES DE CARREGAMENTO (CACHED) ---

@st.cache_data
def carregar_dicionario_sistema():
    """Carrega o dicionário fixo do repositório para memória"""
    if not os.path.exists(CAMINHO_DICIONARIO_SISTEMA):
        return None, f"Erro: O arquivo '{CAMINHO_DICIONARIO_SISTEMA}' não foi encontrado no repositório."
    
    try:
        df = pd.read_excel(CAMINHO_DICIONARIO_SISTEMA)
        return df, None
    except Exception as e:
        return None, f"Erro ao ler o Excel: {e}"

def otimizar_regras(df_dict):
    """Transforma o DataFrame em estrutura de dicionário otimizado para busca"""
    regras_otimizadas = {}
    
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

# --- FUNÇÕES DE LÓGICA ---

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
    
    # Garante colunas
    for col in colunas_alvo:
        if col not in df_processado.columns:
            df_processado[col] = None
    
    for i, col_alvo in enumerate(colunas_alvo):
        barra_progresso.progress((i + 1) / len(colunas_alvo))
        
        if col_alvo in regras_otimizadas:
            lista_regras = regras_otimizadas[col_alvo]
            novos_valores = df_processado['Nome SKU'].apply(lambda x: classificar_item(x, lista_regras))
            
            old_values = df_processado[col_alvo]
            df_processado[col_alvo] = novos_valores.combine_first(df_processado[col_alvo])
            
            for idx, (old, new) in enumerate(zip(old_values, df_processado[col_alvo])):
                if str(old) != str(new):
                    comparativo_data.append({
                        'SKU ID': df_processado.iloc[idx].get('Código Barras SKU', idx),
                        'Descrição': df_processado.iloc[idx]['Nome SKU'],
                        'Coluna Afetada': col_alvo,
                        'Valor Original': old,
                        'Valor Novo': new
                    })
    
    barra_progresso.empty()
    return df_processado, pd.DataFrame(comparativo_data)

# --- INTERFACE ---

st.set_page_config(page_title="Classificador Master", layout="wide")
st.title("🏭 Classificador Inteligente de SKUs")

# Carregamento Automático do Dicionário
with st.sidebar:
    st.header("Status do Sistema")
    df_dict, erro = carregar_dicionario_sistema()
    
    if erro:
        st.error(erro)
        st.stop()
    else:
        st.success(f"✅ Dicionário Carregado ({len(df_dict)} regras)")
        
    st.divider()
    industria_selecionada = st.selectbox("Selecione a Indústria:", list(INDUSTRY_CONFIG.keys()))
    st.info(f"Classificando colunas: {', '.join(INDUSTRY_CONFIG[industria_selecionada])}")

# Área Principal
st.write("### 1. Upload da Base de SKUs")
file_sku = st.file_uploader("Carregue a planilha 'Cadastro SKU' (.xlsx ou .csv)", type=['xlsx', 'csv'])

if file_sku:
    try:
        # Leitura da Base SKU
        if file_sku.name.endswith('.csv'):
            df_sku = pd.read_csv(file_sku)
        else:
            df_sku = pd.read_excel(file_sku)
            
        st.dataframe(df_sku.head())
        
        if st.button("🚀 Iniciar Classificação"):
            # Otimiza regras apenas no momento do clique (usando o dict carregado)
            regras_prontas = otimizar_regras(df_dict)
            
            with st.spinner("Processando regras..."):
                df_final, df_comp = processar_dataframe(df_sku, regras_prontas, industria_selecionada)
            
            st.success("Concluído!")
            
            col1, col2 = st.columns(2)
            
            # Download Base Final
            buffer_final = io.BytesIO()
            with pd.ExcelWriter(buffer_final, engine='xlsxwriter') as writer:
                df_final.to_excel(writer, index=False)
            
            col1.download_button(
                "📥 Baixar Base Classificada",
                data=buffer_final.getvalue(),
                file_name=f"SKU_Classificado_{industria_selecionada}.xlsx",
                mime="application/vnd.ms-excel"
            )
            
            # Download Comparativo
            if not df_comp.empty:
                buffer_comp = io.BytesIO()
                with pd.ExcelWriter(buffer_comp, engine='xlsxwriter') as writer:
                    df_comp.to_excel(writer, index=False)
                
                col2.download_button(
                    "📊 Baixar Relatório de Mudanças",
                    data=buffer_comp.getvalue(),
                    file_name="Relatorio_Alteracoes.xlsx",
                    mime="application/vnd.ms-excel"
                )
            else:
                col2.info("Nenhuma alteração detectada.")
                
    except Exception as e:
        st.error(f"Erro crítico: {e}")
