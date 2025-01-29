import streamlit as st
import pandas as pd

# Updated data from the image, pre-processed into a dictionary for easier use
data = {
    'ESB MOD I': {'quantidade': 1, 'valor': 'R$ 4.014', 'valor_implantacao': 'R$ 2.453', 'valor_implantacao_novo': 'R$ 4.014'},
    'ESB MOD II': {'quantidade': 1, 'valor': 'R$ 7.064', 'valor_implantacao': 'R$ 3.278', 'valor_implantacao_novo': 'R$ 7.064'},
    'UOM': {'quantidade': 1, 'valor': 'R$ 9.360', 'valor_implantacao': 'R$ 4.680', 'valor_implantacao_novo': 'R$ 9.360'},
    'CEO TIPO I': {'quantidade': 1, 'valor': 'R$ 23.760', 'valor_implantacao': 'R$ 8.250', 'valor_implantacao_novo': 'R$ 23.760'},
    'CEO TIPO II': {'quantidade': 1, 'valor': 'R$ 31.680', 'valor_implantacao': 'R$ 11.000', 'valor_implantacao_novo': 'R$ 31.680'},
    'CEO TIPO III': {'quantidade': 1, 'valor': 'R$ 55.440', 'valor_implantacao': 'R$ 19.250', 'valor_implantacao_novo': 'R$ 55.440'},
    'CEO ADESÃO RCPD': {'quantidade': 1, 'valor': 'R$ 6.160', 'valor_implantacao': 'R$ 2.567', 'valor_implantacao_novo': 'R$ 6.160'},
    'CEO COM ESPECIALIDADES': {'quantidade': 1, 'valor': 'R$ 6.160', 'valor_implantacao': 'R$ 2.567', 'valor_implantacao_novo': 'R$ 6.160'},
    'SESB': {'quantidade': 1, 'valor': 'R$ 9.000', 'valor_implantacao': 'R$ 9.000', 'valor_implantacao_novo': 'R$ 9.000'},
    'LRPD FAIXA I': {'quantidade': 1, 'valor': 'R$ 12.600', 'valor_implantacao': 'R$ 7.500', 'valor_implantacao_novo': 'R$ 12.600'},
    'LRPD FAIXA II': {'quantidade': 1, 'valor': 'R$ 20.100', 'valor_implantacao': 'R$ 12.000', 'valor_implantacao_novo': 'R$ 20.100'},
    'LRPD FAIXA III': {'quantidade': 1, 'valor': 'R$ 30.000', 'valor_implantacao': 'R$ 18.000', 'valor_implantacao_novo': 'R$ 30.000'},
    'LRPD FAIXA IV': {'quantidade': 1, 'valor': 'R$ 37.500', 'valor_implantacao': 'R$ 22.500', 'valor_implantacao_novo': 'R$ 37.500'},
    'ESB': {'quantidade': 1, 'valor': 'R$ 7.000', 'valor_implantacao': 'R$ 14.000'},
    'UOM ': {'quantidade': 1, 'valor': 'R$ 3.500', 'valor_implantacao': 'R$ 7.000'},
    'CEO TIPO I ': {'quantidade': 1, 'valor': 'R$ 60.000', 'valor_implantacao': 'R$ 120.000'},
    'CEO TIPO II ': {'quantidade': 1, 'valor': 'R$ 75.000', 'valor_implantacao': 'R$ 150.000'},
    'CEO TIPO III ': {'quantidade': 1, 'valor': 'R$ 120.000', 'valor_implantacao': 'R$ 240.000'},
    'SESB ': {'quantidade': 1, 'valor': 'R$ 24.000', 'valor_implantacao': 'R$ 24.000'},
}

# Categorize the services
categories = {
    'Estratégia': ['ESB MOD I', 'ESB MOD II', 'UOM', 'CEO TIPO I', 'CEO TIPO II', 'CEO TIPO III', 'CEO ADESÃO RCPD', 'CEO COM ESPECIALIDADES', 'SESB', 'LRPD FAIXA I', 'LRPD FAIXA II', 'LRPD FAIXA III', 'LRPD FAIXA IV'],
    'Custeio e Implantação': ['ESB', 'UOM ', 'CEO TIPO I ', 'CEO TIPO II ', 'CEO TIPO III ', 'SESB ']
}

def format_currency(value):
    """Formats a number as Brazilian currency."""
    return "R$ {:,.2f}".format(value).replace(",", "v").replace(".", ",").replace("v", ".")

def calculate_total(selected_services):
    """Calculates the total value for the selected services."""
    results = []
    total_geral = 0
    for service, quantity in selected_services.items():
        if service in data:
            if 'valor' in data[service]:
                valor = float(data[service]['valor'].replace('R$ ', '').replace('.', '').replace(',', '.'))
                total = valor * quantity
                total_geral += total
                results.append([service, quantity, format_currency(valor), format_currency(total)])

    
    results.append(['Total Geral', '', '', format_currency(total_geral)])
    return results

st.title('Calculadora de Serviços de Saúde')

selected_services = {}
for category, services in categories.items():
    st.subheader(category)
    for service in services:
        quantity = st.number_input(f'{service}', min_value=0, value=0, key=service)
        selected_services[service] = quantity

if st.button('Calcular'):
    results = calculate_total(selected_services)
    results_df = pd.DataFrame(results, columns=['Serviço', 'Quantidade', 'Valor Unitário', 'Valor Total'])
    
    # Display results by category
    for category, services in categories.items():
        st.subheader(f"Resultados - {category}")
        category_df = results_df[results_df['Serviço'].isin(services)]
        if not category_df.empty:
            st.table(category_df)

    # Display the total at the end
    st.subheader("Total Geral")
    st.table(results_df[results_df['Serviço'] == 'Total Geral'])