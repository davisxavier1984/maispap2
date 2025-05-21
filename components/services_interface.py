"""
Módulo que controla a interface para seleção de serviços na Calculadora PAP.
"""
import streamlit as st
import json

def format_currency(value: float | str) -> str:
    """Formata um número como moeda brasileira (R$)."""
    if value == 'Sem cálculo':
        return value

    # Converte a string para float, se necessário
    if isinstance(value, str):
        try:
            # Remove "R$" e espaços, e substitui vírgulas por pontos
            value = value.replace('R\\$', '').strip().replace('.', '').replace(',', '.')
            value = float(value)
        except ValueError:
            return "Valor inválido"

    # Formata o valor como moeda, usando f-string
    return f"R$ {value:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")

def get_estrato(ied: str | None = None) -> str:
    """
    Retorna o estrato com base no IED (dsFaixaIndiceEquidadeEsfEap).
    Se o IED for inválido ou ausente, exibe um erro e interrompe o cálculo.
    """
    if ied is not None and isinstance(ied, str) and ied.startswith("ESTRATO "):
        try:
            return ied[-1]
        except IndexError:
            st.error(f"Erro ao extrair estrato do IED: {ied}.")
            st.stop()

    st.error("IED (dsFaixaIndiceEquidadeEsfEap) ausente ou inválido. Não é possível determinar o estrato.")
    st.stop()

def render_services_interface():
    """Renderiza a interface para seleção de serviços."""
    # Carregando dados do config.json
    with open("config.json", "r", encoding="utf-8") as f:
        config_data = json.load(f)

    # Extrai valores do config.json
    data = config_data["data"]
    updated_categories = config_data["updated_categories"]
    subcategories = config_data["subcategories"]
    quality_values = config_data["quality_values"]
    fixed_component_values = config_data["fixed_component_values"]
    service_to_plan = config_data["service_to_plan"]
    implantacao_values = config_data["implantacao_values"]

    # CSS para estilizar os campos
    st.markdown(
        """
        <style>
        div[data-testid="stVerticalBlock"] > div:first-child {
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 5px;
        }
        
        div[data-testid="stVerticalBlock"] > div:nth-child(2) {
            padding: 10px;
            border-radius: 5px;
            text-align: center;
            margin-bottom: 5px;
        }
        
        div[data-testid="stVerticalBlock"] > div:last-child {
            padding: 10px;
            border-radius: 5px;
            text-align: right;
            margin-bottom: 5px;
        }
        
        .result-value {
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    selected_services = {}
    edited_values = {}  # Dicionário para armazenar valores editados
    # Dicionário para armazenar valores de implantação editados
    edited_implantacao_values = {}
    # Dicionário para armazenar quantidades de implantação editadas
    edited_implantacao_quantity = {}

    # Use st.expander for each category and create unique keys
    for category, services in updated_categories.items():
        with st.expander(category):
            if category == 'Saúde Bucal':
                for subcategory, sub_services in subcategories.items():
                    st.markdown(f"##### {subcategory}")
                    for service in sub_services:
                        # --- Campos normais ---
                        unique_key = f"{category}_{subcategory}_{service}"
                        unique_key_value = f"{category}_{subcategory}_{service}_value"
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            quantity = st.number_input(f'{service} (Quantidade)', min_value=0, value=0, key=unique_key)
                            selected_services[service] = quantity

                        with col2:
                            # Buscar valor do data.json (resumosPlanosOrcamentarios)
                            initial_value = "R$ 0,00"

                            # Buscar valor do config.json
                            if service in data and data[service]['valor'] != 'Sem cálculo':
                                initial_value = data[service]['valor']

                            value = st.text_input(f"Valor {service}", value=initial_value, key=unique_key_value)
                            # Armazenar valor editado, se houver
                            if value != initial_value:
                                try:
                                    edited_values[service] = float(
                                        value.replace('R$ ', '').replace('.', '').replace(',', '.'))
                                except ValueError:
                                    st.error(f"Valor inválido para {service}. Insira um número válido.")
                                    edited_values[service] = 0.0
                            else:
                                if service in edited_values:
                                    del edited_values[service]

                        with col3:
                            if value != 'Sem cálculo':
                                try:
                                    total_value = float(
                                        value.replace('R$ ', '').replace('.', '').replace(',', '.')) * quantity
                                except ValueError:
                                    total_value = 0
                            else:
                                total_value = 0
                            st.text_input(f"Subtotal {service}", value=format_currency(total_value), key=f"{unique_key}_total",
                                          disabled=True)
            else:
                for service in services:
                    # --- Campos normais ---
                    unique_key = f"{category}_{service}"
                    unique_key_value = f"{category}_{service}_value"
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        quantity = st.number_input(f'{service} (Quantidade)', min_value=0, value=0, key=unique_key)
                        selected_services[service] = quantity

                    with col2:
                        # Buscar valor do data.json (resumosPlanosOrcamentarios) ou do fixed_component_values se for eSF, eAP 30h ou eAP 20h
                        initial_value = "R$ 0,00"
                        if service in ["eSF", "eAP 30h", "eAP 20h"]:
                            populacao = st.session_state.get('populacao', 0)
                            estrato = get_estrato(st.session_state.get('ied', None))
                            if estrato in fixed_component_values:
                                initial_value = fixed_component_values[estrato][service]
                        else:
                            # Buscar valor do config.json
                            if service in data and data[service]['valor'] != 'Sem cálculo':
                                initial_value = data[service]['valor']

                        value = st.text_input(f"Valor {service}", value=initial_value, key=unique_key_value)
                        # Armazenar valor editado, se houver
                        if value != initial_value:
                            try:
                                edited_values[service] = float(
                                    value.replace('R$ ', '').replace('.', '').replace(',', '.'))
                            except ValueError:
                                st.error(f"Valor inválido para {service}. Insira um número válido.")
                                edited_values[service] = 0.0
                        else:
                            if service in edited_values:
                                del edited_values[service]

                    with col3:
                        if value != 'Sem cálculo':
                            try:
                                total_value = float(
                                    value.replace('R$ ', '').replace('.', '').replace(',', '.')) * quantity
                            except ValueError:
                                total_value = 0
                        else:
                            total_value = 0
                        st.text_input(f"Subtotal {service}", value=format_currency(total_value), key=f"{unique_key}_total",
                                      disabled=True)

                    # --- Campos de implantação (eSF, eAP e eMulti) ---
                    if service in ["eSF", "eAP 30h", "eAP 20h", "eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
                        if 'implantacao_campos' not in st.session_state:
                            st.session_state['implantacao_campos'] = {}
                        if category not in st.session_state['implantacao_campos']:
                            # Agora é um dicionário para armazenar as chaves únicas
                            st.session_state['implantacao_campos'][category] = {}

                        # Chaves únicas para os campos de implantação
                        key_q = f"{category}_{service}_implantacao_q_quantidade"
                        key_v = f"{category}_{service}_implantacao_valor"
                        key_s = f"{category}_{service}_implantacao_subtotal"

                        # Armazenar as chaves no dicionário
                        st.session_state['implantacao_campos'][category][key_q] = ''
                        st.session_state['implantacao_campos'][category][key_v] = ''
                        st.session_state['implantacao_campos'][category][key_s] = ''

            # Divisor e campos de implantação após os campos normais
            # A lógica agora só é executada se a categoria tiver campos de implantação
            if 'implantacao_campos' in st.session_state and category in st.session_state['implantacao_campos']:
                st.divider()
                st.markdown(f"###### Implantação")

                for key_q in list(st.session_state['implantacao_campos'][category].keys()):
                    if key_q.endswith('_quantidade'):
                        service = key_q.split('_')[1] # Obter o nome do serviço a partir da chave
                        key_v = key_q.replace('_q_quantidade', '_valor')
                        key_s = key_q.replace('_q_quantidade', '_subtotal')

                        # --- Campos de implantação (eSF, eAP e eMulti) ---
                        col1_imp, col2_imp, col3_imp = st.columns(3)

                        with col1_imp:
                            # Quantidade de implantação
                            quantity_implantacao = st.number_input(f'{service} (Quantidade)', min_value=0, value=0,
                                                                  key=key_q)
                            edited_implantacao_quantity[service] = quantity_implantacao

                        with col2_imp:
                            # Valor de implantação
                            # Buscar valor do implantacao_values, tratando eMulti
                            initial_implantacao_value = "R$ 0,00"
                            if service in implantacao_values:
                                initial_implantacao_value = implantacao_values[service]
                            elif service == "eMULTI Ampl.":
                                initial_implantacao_value = implantacao_values["eMulti Ampliada"]
                            elif service == "eMULTI Compl.":
                                initial_implantacao_value = implantacao_values["eMulti Complementar"]
                            elif service == "eMULTI Estrat.":
                                initial_implantacao_value = implantacao_values["eMulti Estratégica"]

                            implantacao_value = st.text_input(f"Valor", value=initial_implantacao_value,
                                                              key=key_v)
                            # Armazenar valor de implantação editado, se houver
                            if implantacao_value != initial_implantacao_value:
                                try:
                                    edited_implantacao_values[service] = float(
                                        implantacao_value.replace('R$ ', '').replace('.', '').replace(',', '.'))
                                except ValueError:
                                    st.error(
                                        f"Valor de implantação inválido para {service}. Insira um número válido.")
                                    edited_implantacao_values[service] = 0.0
                            else:
                                if service in edited_implantacao_values:
                                    del edited_implantacao_values[service]

                        with col3_imp:
                            if implantacao_value != 'Sem cálculo':
                                try:
                                    total_implantacao = float(
                                        implantacao_value.replace('R$ ', '').replace('.', '').replace(',',
                                                                                                    '.')) * quantity_implantacao
                                except ValueError:
                                    total_implantacao = 0
                            else:
                                total_implantacao = 0
                            st.text_input(f"Subtotal", value=format_currency(total_implantacao),
                                          key=key_s, disabled=True)

    return selected_services, edited_values, edited_implantacao_values, edited_implantacao_quantity
