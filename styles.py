import streamlit as st

def aplicar_css_personalizado():
    """Aplica o CSS global da aplicação."""
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
