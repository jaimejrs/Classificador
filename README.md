# Suíte de Dados | Classificador & Extrator

> **Versão:** 2.0.0  
> **Stack:** Python, Streamlit, Pandas, Regex  
> **Status:** Produção  
> **Foco:** Governança de Cadastros, Padronização de SKUs e Automação do Processo.

---

## 🌐 Acesso Rápido (Web)

Para utilização imediata da ferramenta, sem a necessidade de instalações ou uso de terminal, acesse o ambiente de produção em nuvem:

### [🔗 CLIQUE AQUI PARA ACESSAR O SISTEMA](https://classificadorscanntech.streamlit.app/)
*(https://classificadorscanntech.streamlit.app/)*

---

## 🎯 Visão Geral

A **Suíte de Dados** é uma solução desenvolvida para automatizar e elevar a qualidade do cadastro de produtos (SKUs). Atuando como um hub central de processamento, a ferramenta elimina a subjetividade humana na classificação de itens e acelera a consolidação de dados dispersos.

O sistema opera sob dois pilares fundamentais:
1.  **Classificação:** Uso de expressões regulares (Regex) para inferir atributos técnicos a partir de descrições não estruturadas.
2.  **Padronização de Dados:** Agrupamento, formatação, padronização e fragmentação automática de grandes volumes de dados para o envio no clasificaciones.scanntech.com.

---

## 🚀 Funcionalidades Principais

### 1. 🧩 Classificador Inteligente (Auditoria & Categorização)
Este módulo não serve apenas para novos cadastros. Ele atua como um **motor de validação** para bases que já estão cadastradas.

* **Classificação de Novos Itens:** Recebe uma lista de descrições e preenche automaticamente colunas como *Sabor*, *Gramatura*, *Subcategoria*, *Marca*, entre outros.
* **Auditoria de Base :** Utilize o classificador para processar itens já cadastrados. O sistema confrontará a classificação atual com as regras de negócio vigentes, destacando inconsistências (Ex: Um item "Zero Açúcar" classificado erroneamente como "Regular").
* **Relatório de Mudanças:** Gera automaticamente um "De/Para" evidenciando quais atributos foram alterados ou enriquecidos pelo algoritmo.

### 2. 🗃️ Extrator & Fragmentador (ETL)
Focado na produtividade, este módulo reduz problemáticas envolvendo a metodologia de envio de arquivos para o clasificaciones.

* **Consolidação:** Unifica múltiplos arquivos Excel de diferentes fontes em um único Mestre.
* **Padronização:** Converte todo o texto para **CAIXA ALTA**, remove acentos e caracteres especiais indesejados.
* **Fragmentação:** Divide o arquivo mestre em planilhas menores baseadas em atributos (ex: uma planilha só para *Sabor*, outra só para *Embalagem*), facilitando a importação em massa via templates.

---

## 📚 Manual de Utilização (Interface)

### Pré-requisitos dos Arquivos
Para garantir a integridade do processamento, seus arquivos de entrada devem seguir padrões mínimos:
* **Formatos aceitos:** `.xlsx`, `.xls`, `.csv`.
* **Para o Classificador:** O arquivo deve conter obrigatoriamente uma coluna nomeada **`Nome SKU`** contendo a descrição do produto.
* **Para o Extrator:** O arquivo deve conter a coluna chave configurada para a indústria ( `Código Barras SKU`).

### Fluxo de Trabalho

#### Módulo Classificador
1.  Acesse o link da aplicação.
2.  Na aba **"🧩 Classificador Inteligente"**, selecione a **Indústria** e a **Categoria** (carrega o Dicionário de Regras).
3.  Faça o upload da planilha.
4.  Após a validação automática das colunas, clique em **🚀 Classificar**.
5.  Faça o download do arquivo processado e do relatório de auditoria.

#### Módulo Extrator
1.  Na aba **"🗃️ Extrator & Fragmentador"**, selecione a **Indústria**.
2.  Faça o upload de um ou múltiplos arquivos (Lotes).
3.  Clique em **🚀 Processar Arquivos**.
4.  O sistema gerará o **Arquivo Mestre Consolidado** e os **Fragmentos por Atributo** para download imediato.

---

## 🧠 Governança de Dicionários

A inteligência da ferramenta reside nos arquivos localizados na pasta `/dicionarios`. Estes arquivos Excel contêm as regras de Regex que determinam a lógica de negócio.

**⚠️ Nota Importante sobre Manutenção:**
O mercado é dinâmico e novos produtos com nomenclaturas inéditas surgem constantemente.
* **Sintoma:** Se você notar que determinados produtos não estão sendo classificados corretamente ou "NÃO ESTÃO SENDO CLASSIFICADOS".
* **Ação:** Isso indica a necessidade de refinar o dicionário.
* **Como fazer:** O responsável pode atualizar o arquivo `.xlsx` correspondente, adicionando a nova regra de texto (Regex) na coluna `Valor da Regra` e definindo sua prioridade na coluna `Grau de Associação`.
* **Após Fazer:** Deve enviar o arquivo atualizado para o responsável pela manutenção da aplicação/código. Para pequenos ajustes o problema pode ser informado diretamente.
* **Aviso 1:** A aplicação preza pela segurança dos dados da indústria e da scanntech, não havendo possibilidade de uso malicioso das informações publicas por terceiros.
* **Aviso 2:** As informações disponíveis ao público por meio desse repositório são informações genéricas, não há disponibilidade de dados sensíveis ou informações privadas.
* **Aviso 3:** A ferramenta deve ser utilizada como um suporte, as etapas de validação e conferência devem ser respeitadas para o máximo aproveitamento. Apesar da facilitação promovida por essa ferramenta a análise humana é indispensável para a entrega de dados de qualidade para o cliente.

> *Quanto maior o "Grau de Associação", maior a prioridade daquela regra sobre as demais.*

---

<div align="center">
    <p>Desenvolvido para excelência em Gestão de Dados - A entrega de dados de qualidade promove a confiança do cliente e remove barreiras para o letramento em dados em contextos mais conservadores.</p>
</div>
