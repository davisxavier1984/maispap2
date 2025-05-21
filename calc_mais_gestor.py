import streamlit as st
import requests
import json
import pandas as pd
from pyUFbr.baseuf import ufbr

# Nome do arquivo JSON para armazenar os dados
DATA_FILE = "data.json"

def style_metric_cards(
    background_color: str = "#f5f5f5",
    border_size_px: int = 1,
    border_color: str = "#f39c12",
    border_radius_px: int = 5,
    border_left_color: str = "#003366",
    box_shadow: bool = True,
):
    """Define o estilo dos cartões de métricas."""
    box_shadow_str = (
        "box-shadow: 0 0.15rem 1.75rem 0 rgba(58,59,69,.15) !important;"
        if box_shadow
        else "box-shadow: none !important;"
    )
    st.markdown(
        f"""
        <style>
            .reportview-container .main .block-container{{
                padding-top: 1rem;
            }}
            .card {{
                background-color: {background_color};
                border: {border_size_px}px solid {border_color};
                border-radius: {border_radius_px}px;
                padding: 5px;
                text-align: center;
                margin-bottom: 5px;
                {box_shadow_str}
            }}
            .card-title {{
                font-size: 0.7rem;
                font-weight: bold;
                margin-bottom: 0.2rem;
                color: #2c3e50;
            }}
            .card-value {{
                font-size: 1.5rem;
                color: {border_left_color};
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def metric_card(label, value):
    """Cria um cartão estilizado para exibir uma métrica."""
    st.markdown(
        f"""
        <div class="card">
            <div class="card-title">{label}</div>
            <div class="card-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def consultar_api(codigo_ibge, competencia):
    """Consulta a API de financiamento da saúde e salva os dados em um arquivo JSON com indentação."""
    url = "https://relatorioaps-prd.saude.gov.br/financiamento/pagamento"
    params = {
        "unidadeGeografica": "MUNICIPIO",
        "coUf": codigo_ibge[:2],
        "coMunicipio": codigo_ibge[:6],
        "nuParcelaInicio": competencia,
        "nuParcelaFim": competencia,
        "tipoRelatorio": "COMPLETO"
    }

    try:
        response = requests.get(url, params=params, headers={"Accept": "application/json"})
        response.raise_for_status()
        dados = response.json()

        # Salva os dados em um arquivo JSON com indentação para melhor legibilidade
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

        return dados
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na consulta à API: {e}")
        return None

def main():
    st.set_page_config(page_title="Financiamento da Saúde")
    
    # Centraliza a logo
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.image('logo_colorida_mg.png', width=200)
        
    st.title("🏥 Sistema de Monitoramento de Financiamento da Saúde")
    style_metric_cards()

    with st.expander("🔍 Parâmetros de Consulta", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            estados = ufbr.list_uf
            uf_selecionada = st.selectbox("Selecione um Estado", options=estados)
        with col2:
            competencia = st.text_input("Competência (AAAAMM)", "202501")

        if uf_selecionada:
            municipios = ufbr.list_cidades(uf_selecionada)
            municipio_selecionado = st.selectbox("Selecione um Município", options=municipios)

            if municipio_selecionado:
                try:
                    codigo_ibge_padrao = ufbr.get_cidade(municipio_selecionado).codigo
                    codigo_ibge_padrao = str(int(float(codigo_ibge_padrao)))[:-1]
                    codigo_ibge = st.text_input("Código IBGE (opcional)", value=codigo_ibge_padrao)
                except AttributeError:
                    st.error("Erro ao obter código IBGE do município")
                    return

    if st.button("Consultar"):
        if not (uf_selecionada and municipio_selecionado and competencia):
            st.error("Por favor, preencha todos os campos de consulta.")
            return

        dados = consultar_api(codigo_ibge, competencia)

        if dados:
            # Cabeçalho
            st.subheader("Informações Gerais")
            dados_pagamentos = dados.get("pagamentos", [])
            if dados_pagamentos:
                df = pd.DataFrame(dados_pagamentos)
                populacao = df['qtPopulacao'].iloc[0] if 'qtPopulacao' in df.columns else 0
                ano_referencia = df['nuAnoRefPopulacaoIbge'].iloc[0] if 'nuAnoRefPopulacaoIbge' in df.columns else 0
                ied = df['dsFaixaIndiceEquidadeEsfEap'].iloc[0] if 'dsFaixaIndiceEquidadeEsfEap' in df.columns else "Não informado"

                cols_info = st.columns(3)
                with cols_info[0]:
                    metric_card("População IBGE", f"{populacao:,}".replace(",", "."))
                with cols_info[1]:
                    metric_card("Ano Referência Populacional", ano_referencia)
                with cols_info[2]:
                    metric_card("Índice de Equidade", ied)

        else:
            st.error("Nenhum dado encontrado para os parâmetros informados.")

if __name__ == "__main__":
    main()
    
import pandas as pd

# Data from the OCR text, pre-processed into a dictionary for easier use
data = {
    'eSF': {'quantidade': 1, 'valor': 'R$ 16.000,00'},
    'eAP 30h': {'quantidade': 1, 'valor': 'R$ 9.600,00'},
    'eAP 20h': {'quantidade': 1, 'valor': 'R$ 6.400,00'},
    'eMULTI Ampl.': {'quantidade': 1, 'valor': 'R$ 36.000,00'},
    'eMULTI Compl.': {'quantidade': 1, 'valor': 'R$ 24.000,00'},
    'eMULTI Estrat.': {'quantidade': 1, 'valor': 'R$ 12.000,00'},
    'eSB Comum I': {'quantidade': 1, 'valor': 'R$ 4.014,00'},
    'eSB Comum II': {'quantidade': 1, 'valor': 'R$ 7.064,00'},
    'eSB Quil. Assent. I': {'quantidade': 1, 'valor': 'R$ 6.021,00'},
    'eSB Quil. Assent. II': {'quantidade': 1, 'valor': 'R$ 10.596,00'},
    'eSB 20h': {'quantidade': 1, 'valor': 'R$ 2.007,00'},
    'eSB 30h': {'quantidade': 1, 'valor': 'R$ 3.010,00'},
    'LRPD': {'quantidade': 1, 'valor': 'R$ 11.250,00'},
    'CEO I': {'quantidade': 1, 'valor': 'R$ 8.250,00'},
    'CEO II': {'quantidade': 1, 'valor': 'R$ 11.000,00'},
    'CEO III': {'quantidade': 1, 'valor': 'R$ 19.250,00'},
    'UOM': {'quantidade': 1, 'valor': 'R$ 9.360,00'},
    'SESB': {'quantidade': 1, 'valor': 'R$ 7.200,00'},
    'eCR I': {'quantidade': 1, 'valor': 'R$ 19.900,00'},
    'eCR II': {'quantidade': 1, 'valor': 'R$ 27.300,00'},
    'eCR III': {'quantidade': 1, 'valor': 'R$ 35.200,00'},
    'UBSF': {'quantidade': 0, 'valor': 'Sem cálculo'},
    'eSFR': {'quantidade': 1, 'valor': 'R$ 10.695,00'}gest,
    'eAPP': {'quantidade': 0, 'valor': 'Sem cálculo'},
    'IAF I': {'quantidade': 1, 'valor': 'R$ 1.000,00'},
    'IAF II': {'quantidade': 1, 'valor': 'R$ 1.500,00'},
    'IAF III': {'quantidade': 1, 'valor': 'R$ 2.000,00'},
    'ACS Efetivos': {'quantidade': 1, 'valor': 'R$ 2.824,00'},
    'ACS Contratados': {'quantidade': 1, 'valor': 'R$ 1.550,00'},
    'Mais Médicos': {'quantidade': 1, 'valor': 'R$ 0,00'},
    'ESB MOD I': {'quantidade': 1, 'valor': 'R$ 4.014', 'valor_implantacao': 'R$ 2.453', 'valor_implantacao_novo': 'R$ 4.014'},
    'ESB MOD II': {'quantidade': 1, 'valor': 'R$ 7.064', 'valor_implantacao': 'R$ 3.278', 'valor_implantacao_novo': 'R$ 7.064'},
    'CEO ADESÃO RCPD': {'quantidade': 1, 'valor': 'R$ 6.160', 'valor_implantacao': 'R$ 2.567', 'valor_implantacao_novo': 'R$ 6.160'},
    'CEO COM ESPECIALIDADES': {'quantidade': 1, 'valor': 'R$ 6.160', 'valor_implantacao': 'R$ 2.567', 'valor_implantacao_novo': 'R$ 6.160'},
    'LRPD FAIXA I': {'quantidade': 1, 'valor': 'R$ 12.600', 'valor_implantacao': 'R$ 7.500', 'valor_implantacao_novo': 'R$ 12.600'},
    'LRPD FAIXA II': {'quantidade': 1, 'valor': 'R$ 20.100', 'valor_implantacao': 'R$ 12.000', 'valor_implantacao_novo': 'R$ 20.100'},
    'LRPD FAIXA III': {'quantidade': 1, 'valor': 'R$ 30.000', 'valor_implantacao': 'R$ 18.000', 'valor_implantacao_novo': 'R$ 30.000'},
    'LRPD FAIXA IV': {'quantidade': 1, 'valor': 'R$ 37.500', 'valor_implantacao': 'R$ 22.500', 'valor_implantacao_novo': 'R$ 37.500'},
    'ESB ': {'quantidade': 1, 'valor': 'R$ 7.000', 'valor_implantacao': 'R$ 14.000'},
    'UOM ': {'quantidade': 1, 'valor': 'R$ 3.500', 'valor_implantacao': 'R$ 7.000'},
    'CEO TIPO I ': {'quantidade': 1, 'valor': 'R$ 60.000', 'valor_implantacao': 'R$ 120.000'},
    'CEO TIPO II ': {'quantidade': 1, 'valor': 'R$ 75.000', 'valor_implantacao': 'R$ 150.000'},
    'CEO TIPO III ': {'quantidade': 1, 'valor': 'R$ 120.000', 'valor_implantacao': 'R$ 240.000'},
    'SESB ': {'quantidade': 1, 'valor': 'R$ 24.000', 'valor_implantacao': 'R$ 24.000'},
}

# Categorize the services
updated_categories = {
    'Equipe de Saúde da Família': ['eSF', 'eAP 30h', 'eAP 20h'],
    'Equipe Multiprofissional': ['eMULTI Ampl.', 'eMULTI Compl.', 'eMULTI Estrat.'],
    'Saúde Bucal': [
        'eSB Comum I', 'eSB Comum II', 'eSB Quil. Assent. I', 'eSB Quil. Assent. II', 'eSB 20h', 'eSB 30h','ESB MOD I', 'ESB MOD II','ESB ',
        'CEO I', 'CEO II', 'CEO III','CEO ADESÃO RCPD', 'CEO COM ESPECIALIDADES','CEO TIPO I ', 'CEO TIPO II ', 'CEO TIPO III ',
        'UOM', 'UOM ','SESB', 'SESB ', 
        'LRPD', 'LRPD FAIXA I', 'LRPD FAIXA II', 'LRPD FAIXA III', 'LRPD FAIXA IV'
    ],
    'Equipe de Consultório na Rua': ['eCR I', 'eCR II', 'eCR III'],
    'Unidade Básica de Saúde Fluvial': ['UBSF'],
    'Equipe de Saúde da Família Ribeirinha': ['eSFR'],
    'Equipe de Atenção Primária Prisional': ['eAPP'],
    'Incentivo Atividades Físicas': ['IAF I', 'IAF II', 'IAF III'],
    'Agentes Comunitários de Saúde': ['ACS Efetivos', 'ACS Contratados'],
    'Mais Médicos': ['Mais Médicos'],
}

subcategories = {
    'Equipe de Saúde Bucal': ['eSB Comum I', 'eSB Comum II', 'eSB Quil. Assent. I', 'eSB Quil. Assent. II', 'eSB 20h', 'eSB 30h','ESB MOD I', 'ESB MOD II','ESB '],
    'CEO': ['CEO I', 'CEO II', 'CEO III','CEO ADESÃO RCPD', 'CEO COM ESPECIALIDADES','CEO TIPO I ', 'CEO TIPO II ', 'CEO TIPO III '],
    'Outros': ['UOM', 'UOM ','SESB', 'SESB '],
    'LRPD': ['LRPD', 'LRPD FAIXA I', 'LRPD FAIXA II', 'LRPD FAIXA III', 'LRPD FAIXA IV']
}

def format_currency(value):
    """Formats a number as Brazilian currency."""
    if value == 'Sem cálculo':
        return value
    if isinstance(value, str):
        value = float(value.replace('R$ ', '').replace('.', '').replace(',', '.'))
    return "R$ {:,.2f}".format(value).replace(",", "v").replace(".", ",").replace("v", ".")

def calculate_total(selected_services, values):
    """Calculates the total value for the selected services."""
    results = []
    total_geral = 0

    all_services = {service: quantity for category, services in updated_categories.items() for service, quantity in selected_services.items() if service in services}

    for (service, quantity), value in zip(all_services.items(), values.values()):
        if service in data:
            if value == 'Sem cálculo':
                valor = 0
            else:
                valor = float(value.replace('R$ ', '').replace('.', '').replace(',', '.'))

            total = valor * quantity

            if quantity > 0:
                total_geral += total
                results.append([service, quantity, format_currency(valor), format_currency(total)])

    if total_geral > 0:
        results.append(['Total Geral', '', '', format_currency(total_geral)])
    return results

selected_services = {}
values = {}

# CSS para estilizar os campos de valor unitário
st.markdown("""
<style>
div[data-testid="stText"] {
    background-color: #a7d9ed; /* Cor de fundo azul mais escuro */
    padding: 10px;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

# Use st.expander for each category and create unique keys
for category, services in updated_categories.items():
    with st.expander(category):
        # Check if the category is "Saúde Bucal" and handle subcategories
        if category == 'Saúde Bucal':
            for subcategory, sub_services in subcategories.items():
                st.markdown(f"##### {subcategory}")
                cols = st.columns(4)  # Changed to 4 columns
                col_index = 0
                
                for service in sub_services:
                    unique_key = f"{category}_{subcategory}_{service}"
                    unique_key_value = f"{category}_{subcategory}_{service}_value"

                    with cols[col_index % 4]:  # Mod to 4
                        quantity = st.number_input(f'{service} (Quantidade)', min_value=0, value=0, key=unique_key)
                        initial_value = data[service]['valor']
                        value = st.text_input(f'{service} (Valor Unitário)', value=initial_value, key=unique_key_value)
                        selected_services[service] = quantity
                        values[unique_key_value] = value
                    
                    col_index += 1
                st.divider()
        else:
            # Regular category processing
            cols = st.columns(4)  # Changed to 4 columns
            col_index = 0
            for service in services:
                unique_key = f"{category}_{service}"
                unique_key_value = f"{category}_{service}_value"
                with cols[col_index % 4]:  # Mod to 4
                    quantity = st.number_input(f'{service} (Quantidade)', min_value=0, value=0, key=unique_key)
                    initial_value = data[service]['valor']
                    value = st.text_input(f'{service} (Valor Unitário)', value=initial_value, key=unique_key_value)
                    selected_services[service] = quantity
                    values[unique_key_value] = value
                col_index += 1

if st.button('Calcular'):
    results = calculate_total(selected_services, values)
    results_df = pd.DataFrame(results, columns=['Serviço', 'Quantidade', 'Valor Unitário', 'Valor Total'])
    
    for category, services in updated_categories.items():
        category_df = results_df[results_df['Serviço'].isin(services)]
        if not category_df.empty:
            st.subheader(f"Resultados - {category}")
            st.table(category_df)

    if 'Total Geral' in results_df['Serviço'].values:
        st.subheader("Total Geral")
        st.table(results_df[results_df['Serviço'] == 'Total Geral'])
