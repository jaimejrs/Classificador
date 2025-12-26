import streamlit as st
import os
import numpy as np
from PIL import Image

# Importação dos Módulos Locais
import config
import styles
import utils

# ==============================================================================
# CONFIGURAÇÃO INICIAL E ASSETS
# ==============================================================================
icone_img = None
logo_img = None

if os.path.exists("assets/ícone.png"):
    icone_img = Image.open("assets/ícone.png")
elif os.path.exists("assets/icone.png"):
    icone_img = Image.open("assets/icone.png")
else:
    print("AVISO: Arquivo de ícone não encontrado na pasta assets/")

# Tenta carregar a logo
if os.path.exists(config.CAMINHO_LOGO):
    logo_img = Image.open(config.CAMINHO_LOGO)

st.set_page_config(
    page_title="Suíte de Dados - Classificador & Extrator",
    page_icon=icone_img, # Se for None, o Streamlit usa o ícone padrão
    layout="wide"
)
# APLICA O CSS DO MÓDULO styles.py
styles.aplicar_css_personalizado()

def main():
    if logo_img:
        st.sidebar.image(logo_img, use_column_width=True)
    st.sidebar.markdown("---") 
    
    st.title("Classificador de Prods")
    
    tab_classificador, tab_extrator = st.tabs(["Classificador", "Extrator & Fragmentador"])

    # -------------------------------------------------------------------------
    # ABA 1: CLASSIFICADOR
    # -------------------------------------------------------------------------
    with tab_classificador:
        st.header("Classificação por Dicionários")
        st.caption("Utilize dicionários de regras (Regex) para preencher atributos automaticamente.")

        if 'class_concluido' not in st.session_state: st.session_state['class_concluido'] = False
        if 'class_df_final' not in st.session_state: st.session_state['class_df_final'] = None
        if 'class_df_comp' not in st.session_state: st.session_state['class_df_comp'] = None

        col_ind, col_cat = st.columns(2)
        with col_ind:
            ind_class = st.selectbox("1. Indústria:", list(config.CONFIG_CLASSIFICADOR.keys()), key="sb_ind_class")
        
        config_class = config.CONFIG_CLASSIFICADOR[ind_class]
        
        with col_cat:
            opcoes_cat = list(config_class['arquivos'].keys())
            cat_class = st.selectbox("2. Categoria:", opcoes_cat, key="sb_cat_class")

        nome_arq_regras = config_class['arquivos'][cat_class]
        
        # Carrega dicionário (usando Cache do utils)
        df_dict, erro_dict = utils.carregar_dicionario_industria(nome_arq_regras)
        
        if erro_dict:
            st.error("Erro ao carregar dicionário de regras.")
            st.caption(erro_dict)
        else:
            st.info(f"📚 Dicionário ativo: `{nome_arq_regras}` ({len(df_dict)} regras)")
            
            st.markdown("### 3. Upload da Base")
            file_sku_class = st.file_uploader(f"Base de SKUs ({ind_class} - {cat_class})", type=['xlsx', 'csv', 'xls'], key="up_class")

            if file_sku_class:
                st.divider()
                with st.expander("🔍 Pré-visualização e Diagnóstico (Clique para abrir)", expanded=True):
                    df_preview = utils.ler_arquivo_robusto(file_sku_class)
                    file_sku_class.seek(0)

                    if df_preview is not None:
                        df_preview = utils.clean_column_names(df_preview)
                        cols_found = set(df_preview.columns)
                        
                        st.markdown("##### Diagnóstico de Colunas")
                        if 'Nome SKU' in cols_found:
                            st.markdown('<span class="badge-found">✅ Coluna Obrigatória: Nome SKU</span>', unsafe_allow_html=True)
                        else:
                            st.markdown('<span class="badge-missing">❌ Faltando: Nome SKU</span>', unsafe_allow_html=True)
                            st.error("ERRO: O arquivo precisa ter uma coluna chamada 'Nome SKU'.")

                        other_cols = cols_found - {'Nome SKU'}
                        if other_cols:
                            html_others = ""
                            for c in list(other_cols)[:5]: html_others += f'<span class="badge-info">{c}</span>'
                            if len(other_cols) > 5: html_others += f'<span class="badge-info">... e mais {len(other_cols)-5}</span>'
                            st.markdown("**Outras colunas encontradas:**")
                            st.markdown(html_others, unsafe_allow_html=True)

                        st.markdown("##### Amostra de Dados")
                        st.table(df_preview.head()) 
                    else:
                        st.error("Erro ao ler o arquivo para pré-visualização.")
                st.divider()

            if file_sku_class:
                if st.button("🚀 Classificar", type="primary", key="btn_class"):
                    df_sku = utils.ler_arquivo_robusto(file_sku_class)
                    if df_sku is not None:
                        df_sku.columns = df_sku.columns.str.strip()
                        if 'Nome SKU' not in df_sku.columns:
                            st.error("❌ A planilha deve conter a coluna 'Nome SKU'.")
                        else:
                            regras = utils.otimizar_regras(df_dict)
                            if regras:
                                with st.spinner("Classificando..."):
                                    df_final, df_comp = utils.processar_dataframe_classificador(df_sku, regras, config_class)
                                
                                st.session_state['class_df_final'] = df_final
                                st.session_state['class_df_comp'] = df_comp
                                st.session_state['class_concluido'] = True
                                st.rerun()

            if st.session_state['class_concluido'] and st.session_state['class_df_final'] is not None:
                st.success("Processamento Concluído!")
                c1, c2 = st.columns(2)
                
                data_hoje = utils.get_data_atual_str()
                nome_base_out = f"Classificados_{ind_class}_{cat_class}".replace(" ", "_").replace("/", "-")
                nome_final_out = f"{nome_base_out}_{data_hoje}.xlsx"
                nome_mudancas_out = f"Mudancas_{data_hoje}.xlsx"

                c1.download_button(
                    "📥 Baixar Classificados", 
                    data=utils.to_excel_bytes(st.session_state['class_df_final']), 
                    file_name=nome_final_out,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
                if not st.session_state['class_df_comp'].empty:
                    c2.download_button(
                        "📊 Relatório de Mudanças", 
                        data=utils.to_excel_bytes(st.session_state['class_df_comp']), 
                        file_name=nome_mudancas_out,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    c2.info("Sem alterações.")
                
                st.markdown("---")
                utils.exibir_resumo_estatistico(st.session_state['class_df_final'], config_class['colunas'])

                if st.button("🔄 Limpar Classificador", key="limpar_class"):
                    st.session_state['class_concluido'] = False
                    st.session_state['class_df_final'] = None
                    st.session_state['class_df_comp'] = None
                    st.rerun()

    # -------------------------------------------------------------------------
    # ABA 2: EXTRATOR
    # -------------------------------------------------------------------------
    with tab_extrator:
        st.header("Extrator de Planilhas")
        st.caption("Consolide arquivos e gere planilhas de atributos separadas.")

        if 'ext_arquivos' not in st.session_state: st.session_state['ext_arquivos'] = {}
        if 'ext_concluido' not in st.session_state: st.session_state['ext_concluido'] = False
        if 'ext_erros' not in st.session_state: st.session_state['ext_erros'] = []
        if 'ext_ignorado' not in st.session_state: st.session_state['ext_ignorado'] = []
        if 'ext_conflitos' not in st.session_state: st.session_state['ext_conflitos'] = None

        ind_ext = st.selectbox("1. Selecione a Indústria:", list(config.CONFIG_EXTRATOR.keys()), key="sb_ind_ext")
        config_ext = config.CONFIG_EXTRATOR[ind_ext]

        st.markdown(f"**Clave:** `{config_ext['sku_origem']}`")
        st.caption("Atributos: " + ", ".join(config_ext['colunas_atributos']))

        files_ext = st.file_uploader("2. Carregue os arquivos Excel:", accept_multiple_files=True, type=["xlsx"], key="up_ext")

        if files_ext:
            st.divider()
            with st.expander("🔍 Pré-visualização e Diagnóstico de Colunas (Clique para abrir)", expanded=True):
                file_names = [f.name for f in files_ext]
                selected_file_name = st.selectbox("Selecione um arquivo para inspecionar:", file_names)
                selected_file = next(f for f in files_ext if f.name == selected_file_name)
                
                df_preview = utils.ler_arquivo_robusto(selected_file)
                selected_file.seek(0)
                
                if df_preview is not None:
                    df_preview = utils.clean_column_names(df_preview)
                    colunas_encontradas = set(df_preview.columns)
                    colunas_esperadas = set([config_ext['sku_origem']] + config_ext['colunas_atributos'])
                    
                    cols_ok = colunas_esperadas.intersection(colunas_encontradas)
                    cols_missing = colunas_esperadas - colunas_encontradas
                    
                    st.markdown("##### Diagnóstico de Colunas")
                    html_cols = ""
                    for col in sorted(list(cols_ok)): html_cols += f'<span class="badge-found">✅ {col}</span>'
                    for col in sorted(list(cols_missing)): html_cols += f'<span class="badge-missing">❌ {col}</span>'
                    st.markdown(html_cols, unsafe_allow_html=True)
                    
                    if cols_missing:
                        st.warning(f"Atenção: Este arquivo não possui {len(cols_missing)} colunas esperadas.")
                    else:
                        st.success("Todas as colunas esperadas foram encontradas!")

                    st.markdown("##### Amostra de Dados")
                    st.table(df_preview.head())
                else:
                    st.error("Não foi possível ler este arquivo.")
            st.divider()

        if files_ext:
            if st.button("🚀 Processar Arquivos", key="btn_ext_proc"):
                st.session_state['ext_arquivos'] = {}
                st.session_state['ext_erros'] = []
                st.session_state['ext_ignorado'] = []
                st.session_state['ext_concluida'] = False
                
                df_final_ext, conflitos_ext, debug_ext = utils.processar_arquivos_extrator(files_ext, config_ext)

                if df_final_ext is None:
                    st.session_state['ext_erros'] = conflitos_ext
                else:
                    st.session_state['ext_conflitos'] = conflitos_ext
                    st.session_state['ext_concluido'] = True
                    
                    arquivos_out = {}
                    relatorio_skip = []

                    data_hoje = utils.get_data_atual_str()
                    nome_mestre = f"Mestre_Completo_{data_hoje}.xlsx"
                    arquivos_out[nome_mestre] = df_final_ext
                    
                    for col in config_ext["colunas_atributos"]:
                        if col in df_final_ext.columns:
                            cols_fragmento = [config.SKU_PADRAO_FINAL, config.COL_NOME_SKU, col]
                            cols_fragmento = [c for c in cols_fragmento if c in df_final_ext.columns]
                            
                            sub_df = df_final_ext[cols_fragmento].dropna(subset=[col])
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

        if st.session_state['ext_erros']:
            st.error("⛔ Erros críticos encontrados:")
            for erro in st.session_state['ext_erros']: st.error(erro)

        if st.session_state['ext_concluido']:
            st.markdown("---")
            st.header("3. Resultados")

            if st.session_state['ext_ignorado']:
                with st.expander("⚠️ Relatório de Colunas Vazias/Ignoradas"):
                    for msg in st.session_state['ext_ignorado']: st.text(msg)

            conflitos = st.session_state['ext_conflitos']
            if conflitos is not None and not conflitos.empty:
                st.error(f"🚨 {conflitos[config.SKU_PADRAO_FINAL].nunique()} SKUs com divergências.")
                st.download_button("📥 Baixar Erros", data=utils.to_excel_bytes(conflitos), file_name="ERROS_DUPLICIDADE.xlsx", key="dl_err_ext")

            st.subheader("Downloads")
            arquivos = st.session_state['ext_arquivos']
            mestre_key = next((k for k in arquivos.keys() if "Mestre_Completo" in k), None)
            
            if mestre_key:
                st.download_button("📦 Baixar Mestre Consolidado", data=utils.to_excel_bytes(arquivos[mestre_key]), file_name=mestre_key, key="dl_mestre")
            
            st.markdown("#### Planilhas Fragmentadas")
            cols_layout = st.columns(2)
            i = 0
            for nome, df_arq in arquivos.items():
                if "Mestre" not in nome:
                    with cols_layout[i % 2]:
                        st.download_button(f"📥 {nome}", data=utils.to_excel_bytes(df_arq), file_name=nome, key=f"dl_{nome}")
                    i += 1
            
            if st.button("🔄 Limpar Extrator"):
                for key in ['ext_arquivos', 'ext_concluido', 'ext_erros', 'ext_ignorado', 'ext_conflitos']:
                    del st.session_state[key]
                st.rerun()

if __name__ == "__main__":
    main()


