import os

# --- CAMINHOS ---
PASTA_DICIONARIOS = "dicionarios"
CAMINHO_ICONE = "assets/ícone.png"
CAMINHO_LOGO = "assets/logo.png"

# --- CONSTANTES DE DADOS ---
SKU_PADRAO_FINAL = "Código Barras SKU"
COL_NOME_SKU = "Nome SKU"

# --- CONFIGURAÇÃO DO CLASSIFICADOR ---
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

# --- CONFIGURAÇÃO DO EXTRATOR ---
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
