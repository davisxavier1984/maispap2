#=============================================== PARTE 1 ===============================================
import streamlit as st
import requests
import json
import pandas as pd
from pyUFbr.baseuf import ufbr
from requests.exceptions import RequestException

# Nome do arquivo JSON para armazenar os dados
DATA_FILE = "data.json"

# Função para carregar os dados do data.json
def load_data_from_json():
    """Carrega os dados do arquivo data.json. Retorna um dicionário vazio se o arquivo não existir."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Selecione UF e Município e clique em Consultar.")
        return {}

def style_metric_cards(
    background_color: str = "#f5f5f5",
    border_size_px: int = 1,
    border_color: str = "#f39c12",
    border_radius_px: int = 5,
    border_left_color: str = "#003366",
    box_shadow: bool = True,
) -> None:
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

def metric_card(label: str, value: str | int | float) -> None:
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

def consultar_api(codigo_ibge: str, competencia: str) -> dict | None:
    """Consulta a API de financiamento da saúde e salva os dados em um arquivo JSON com indentação."""

    st.session_state['competencia'] = competencia

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
        # Remover verify=False e tratar o erro de certificado se ocorrer
        response = requests.get(url, params=params, headers={"Accept": "application/json"}, verify=False)
        response.raise_for_status()
        dados = response.json()

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

        return dados
    except RequestException as e:
        st.error(f"Erro na consulta à API: {e}")
        # Aqui você pode adicionar um tratamento mais específico, como:
        # if isinstance(e, requests.exceptions.SSLError):
        #     st.error("Erro de certificado SSL. Verifique a configuração do servidor.")
        return None

def main():
    st.set_page_config(page_title="Financiamento da Saúde")

    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.image('logo_colorida_mg.png', width=200)

    st.title("Calculadora PAP")
    style_metric_cards()

    with st.expander("🔍 Parâmetros de Consulta", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            estados = ufbr.list_uf
            uf_selecionada = st.selectbox("Selecione um Estado", options=estados)
        with col2:
            competencia = st.text_input("Competência (AAAAMM)", st.session_state.get('competencia', "202501"))

        if uf_selecionada:
            municipios = ufbr.list_cidades(uf_selecionada)
            municipio_selecionado = st.selectbox("Selecione um Município", options=municipios)

            if municipio_selecionado:
                try:
                    codigo_ibge = str(int(float(ufbr.get_cidade(municipio_selecionado).codigo)))[:-1]
                except AttributeError:
                    st.error("Erro ao obter código IBGE do município")
                    return

    if st.button("Consultar"):
        if not (uf_selecionada and municipio_selecionado and competencia):
            st.error("Por favor, preencha todos os campos de consulta.")
            return

        dados = consultar_api(codigo_ibge, competencia)
        st.session_state['dados'] = dados

    # Carrega os dados do data.json se existirem
    st.session_state['dados'] = load_data_from_json()

    if st.session_state['dados']:
        st.subheader("Informações Gerais")
        dados_pagamentos = st.session_state['dados'].get("pagamentos", [])
        if dados_pagamentos:
            df = pd.DataFrame(dados_pagamentos)
            populacao = df['qtPopulacao'].iloc[0] if 'qtPopulacao' in df.columns else 0
            ano_referencia = df['nuAnoRefPopulacaoIbge'].iloc[0] if 'nuAnoRefPopulacaoIbge' in df.columns else 0
            ied = df['dsFaixaIndiceEquidadeEsfEap'].iloc[0] if 'dsFaixaIndiceEquidadeEsfEap' in df.columns else "Não informado"

            st.session_state['ied'] = ied
            st.session_state['populacao'] = populacao

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
    
    
    
    
    
    
    #=============================================== PARTE 2 ===============================================

# Inicializa os valores no session_state, se não existirem, antes do botão Calcular e antes da PARTE 3
if 'valor_esf_eap' not in st.session_state:
    st.session_state['valor_esf_eap'] = 0.0
if 'valor_saude_bucal' not in st.session_state:
    st.session_state['valor_saude_bucal'] = 0.0
if 'valor_acs' not in st.session_state:
    st.session_state['valor_acs'] = 0.0
if 'valor_estrategicas' not in st.session_state:
    st.session_state['valor_estrategicas'] = 0.0
if 'ied' not in st.session_state:
    st.session_state['ied'] = 0.0
if 'calculo_realizado' not in st.session_state:
    st.session_state['calculo_realizado'] = False  # Inicializado como False

# Carrega a configuração do config.json
with open("config.json", "r", encoding="utf-8") as f:
    config_data = json.load(f)

# Carrega os dados da API do data.json (atualizado pela parte1.py)
# api_data = load_data_from_json() # Já foi carregado na Parte 1

# Mantenha os dados de config.json separados
data = config_data["data"]
updated_categories = config_data["updated_categories"]
subcategories = config_data["subcategories"]
quality_values = config_data["quality_values"]
fixed_component_values = config_data["fixed_component_values"]
service_to_plan = config_data["service_to_plan"] # Carregando service_to_plan
implantacao_values = config_data["implantacao_values"] # Carregando implantacao_values

# CSS para estilizar os campos (pode ser movido para um arquivo .css separado)
CSS = """
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
"""

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

# Aplicar CSS
st.markdown(CSS, unsafe_allow_html=True)









#=============================================== PARTE 3 ===============================================

# Carregando dados do config.json (data.json já foi carregado na Parte 1)
with open("config.json", "r", encoding="utf-8") as f:
    config_data = json.load(f)

# Já carregado na Parte 2
# data = config_data["data"]
# updated_categories = config_data["updated_categories"]
# subcategories = config_data["subcategories"]
# quality_values = config_data["quality_values"]
# fixed_component_values = config_data["fixed_component_values"]
# service_to_plan = config_data["service_to_plan"]
# implantacao_values = config_data["implantacao_values"]

selected_services: dict[str, int] = {}
edited_values: dict[str, float] = {}  # Dicionário para armazenar valores editados
# Dicionário para armazenar valores de implantação editados
edited_implantacao_values: dict[str, float] = {}
# Dicionário para armazenar quantidades de implantação editadas
edited_implantacao_quantity: dict[str, int] = {}

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

                        # *** Buscar valor do config.json ***
                        if service in data and data[service]['valor'] != 'Sem cálculo':
                            initial_value = data[service]['valor']
                        # *** Fim da modificação ***

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
                        estrato = get_estrato(st.session_state.ied)
                        if estrato in fixed_component_values:
                            initial_value = fixed_component_values[estrato][service]
                    else:
                        # *** Buscar valor do config.json ***
                        if service in data and data[service]['valor'] != 'Sem cálculo':
                            initial_value = data[service]['valor']
                        # *** Fim da modificação ***

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
                        # *** Buscar valor do implantacao_values, tratando eMulti ***
                        initial_implantacao_value = "R$ 0,00"
                        if service in implantacao_values:
                            initial_implantacao_value = implantacao_values[service]
                        elif service == "eMULTI Ampl.":
                            initial_implantacao_value = implantacao_values["eMulti Ampliada"]
                        elif service == "eMULTI Compl.":
                            initial_implantacao_value = implantacao_values["eMulti Complementar"]
                        elif service == "eMULTI Estrat.":
                            initial_implantacao_value = implantacao_values["eMulti Estratégica"]
                        # *** Fim da modificação ***

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

#========================================================= ENTRADA DA PARTE 8 ==========================

# Interface para inserção dos valores com st.number_input DENTRO de um st.expander
with st.expander("Parâmetros Adicionais", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        st.session_state['valor_esf_eap'] = st.number_input("Incentivo Financeiro da APS eSF ou eAP", value=float(st.session_state['valor_esf_eap']), format="%.2f", key="input_esf_eap")
        st.session_state['valor_saude_bucal'] = st.number_input("Incentivo Financeiro para Atenção à Saúde Bucal", value=float(st.session_state['valor_saude_bucal']), format="%.2f", key="input_saude_bucal")
    with col2:
        st.session_state['valor_acs'] = st.number_input("Total ACS", value=float(st.session_state['valor_acs']), format="%.2f", key="input_acs")
        st.session_state['valor_estrategicas'] = st.number_input("Ações Estratégicas", value=float(st.session_state['valor_estrategicas']), format="%.2f", key="input_estrategicas")

    # Cálculos para o total
    total_parametros = st.session_state['valor_esf_eap'] + st.session_state['valor_saude_bucal'] + st.session_state['valor_acs'] + st.session_state['valor_estrategicas']

    # Exibindo o total de forma chamativa dentro do expander
    st.markdown(f"<p style='text-align: center; font-size: 1.5rem; color: #008080; font-weight: bold'>Total Adicional: {format_currency(total_parametros)}</p>", unsafe_allow_html=True)

#========================================================= ENTRADA DA PARTE 8 ==========================

# Nova linha para os dropdowns e botão
col_classificacao, col_vinculo = st.columns([1, 1])

with col_classificacao:
    Classificacao = st.selectbox("Considerar Qualidade", options=['Regular', 'Suficiente', 'Bom', 'Ótimo'], index=2)

with col_vinculo:
    Vinculo = st.selectbox("Vínculo e Acompanhamento Territorial", options=['Regular', 'Suficiente', 'Bom', 'Ótimo'], index=2)

calcular_button = st.button('Calcular', use_container_width=True)








#=============================================== PARTE 4 ===============================================

# Carregando dados do config.json (data.json e api_data já foram carregados anteriormente)
with open("config.json", "r", encoding="utf-8") as f:
    config_data = json.load(f)

# Já carregado nas Partes 2 e 3
# data = config_data["data"]
# updated_categories = config_data["updated_categories"]
# subcategories = config_data["subcategories"]
# quality_values = config_data["quality_values"]
# fixed_component_values = config_data["fixed_component_values"]
# service_to_plan = config_data["service_to_plan"]
# implantacao_values = config_data["implantacao_values"]

if calcular_button:
    # Só prossegue com os cálculos se houver dados carregados
    if st.session_state['dados']:
        if all(q == 0 for q in selected_services.values()):
            st.error("Por favor, selecione pelo menos um serviço para calcular.")
        else:
            st.header('Valores PAP')

            # COMPONENTE 01 - COMPONENTE FIXO
            st.subheader("Componente I - Componente Fixo")
            fixed_table: list[list[str | int | float]] = []

            # Construindo a tabela do componente fixo
            for service in ["eSF", "eAP 30h", "eAP 20h", "eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:  # Incluindo eMulti aqui
                quantity = selected_services.get(service, 0)
                if quantity > 0:
                    # Buscar valor do config.json ou fixed_component_values
                    if service in ["eSF", "eAP 30h", "eAP 20h"]:
                        # Obter o IED da session_state - foi definido na PARTE 1
                        ied = st.session_state.get('ied', None)

                        # Passar SOMENTE o IED para a função get_estrato
                        estrato = get_estrato(ied) # A função get_estrato (PARTE 2) agora lida com IED ausente/inválido

                        if estrato in fixed_component_values:
                            valor = float(fixed_component_values[estrato][service].replace('R$ ', '').replace('.', '').replace(',', '.'))
                        else:
                            valor = 0 # Teoricamente, o código nunca deve chegar aqui, pois get_estrato vai interromper a execução
                    elif service in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:  # Tratamento para eMulti
                        try:
                            valor = float(data[service]['valor'].replace('R$ ', '').replace('.', '').replace(',', '.'))
                        except (ValueError, KeyError):
                            st.error(f"Valor inválido para {service} no config.json.")
                            valor = 0
                    else:
                        valor = 0

                    # Verifica se o valor foi editado
                    if service in edited_values:
                        valor = edited_values[service]

                    total_value = valor * quantity
                    fixed_table.append([service, format_currency(valor), quantity, format_currency(total_value)])

            # Adicionar linhas para implantação de eSF, eAP, eMulti (agrupadas após os serviços)
            for service in ["eSF", "eAP 30h", "eAP 20h", "eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
                if selected_services.get(service, 0) > 0:
                    if service in edited_implantacao_values:
                        valor_implantacao = edited_implantacao_values[service]
                    else:
                        if service in implantacao_values:
                            valor_implantacao = float(implantacao_values.get(service, "R$ 0,00").replace('R$ ', '').replace('.', '').replace(',', '.'))
                        elif service == "eMULTI Ampl.":
                            valor_implantacao = float(implantacao_values.get("eMulti Ampliada", "R$ 0,00").replace('R$ ', '').replace('.', '').replace(',', '.'))
                        elif service == "eMULTI Compl.":
                            valor_implantacao = float(implantacao_values.get("eMulti Complementar", "R$ 0,00").replace('R$ ', '').replace('.', '').replace(',', '.'))
                        elif service == "eMULTI Estrat.":
                            valor_implantacao = float(implantacao_values.get("eMulti Estratégica", "R$ 0,00").replace('R$ ', '').replace('.', '').replace(',', '.'))
                        else:
                            valor_implantacao = 0

                    if service in edited_implantacao_quantity:
                        quantity_implantacao = edited_implantacao_quantity[service]
                    else:
                        quantity_implantacao = 0

                    total_implantacao = valor_implantacao * quantity_implantacao
                    fixed_table.append([f"{service} (Implantação)", format_currency(valor_implantacao), quantity_implantacao, format_currency(total_implantacao)])

            fixed_df = pd.DataFrame(fixed_table, columns=['Serviço', 'Valor Unitário', 'Quantidade', 'Valor Total'])

            # Adicionar linha de total à tabela do componente fixo
            total_fixed_value = sum(
                float(str(val).replace('R$ ', '').replace('.', '').replace(',', '.'))
                for val in fixed_df['Valor Total']
            )
            total_fixed_row = pd.DataFrame({
                'Serviço': ['Total'],
                'Valor Unitário': [''],
                'Quantidade': [0],  # CORREÇÃO: Usar 0 para quantidade total
                'Valor Total': [format_currency(total_fixed_value)]
            })
            fixed_df = pd.concat([fixed_df, total_fixed_row], ignore_index=True)

            st.table(fixed_df)

            # COMPONENTE 02 - VÍNCULO E ACOMPANHAMENTO TERRITORIAL.
            st.subheader("Componente II - Vínculo e Acompanhamento Territorial")
            vinculo_table: list[list[str | int | float]] = []

            # Valores do componente de vínculo e acompanhamento
            vinculo_values: dict[str, dict[str, float]] = {
                'eSF': {'Ótimo': 8000, 'Bom': 6000, 'Suficiente': 4000, 'Regular': 2000},
                'eAP 30h': {'Ótimo': 4000, 'Bom': 3000, 'Suficiente': 2000, 'Regular': 1000},
                'eAP 20h': {'Ótimo': 3000, 'Bom': 2250, 'Suficiente': 1500, 'Regular': 750},
            }

            # Construindo a tabela de vínculo e acompanhamento
            for service, quality_levels in vinculo_values.items():
                if Vinculo in quality_levels:
                    quantity = selected_services.get(service, 0)
                    if quantity > 0:
                        if service in edited_values:
                            value = edited_values[service]
                        else:
                            value = quality_levels[Vinculo]
                        total_value = value * quantity
                        vinculo_table.append([service, Vinculo, format_currency(value), quantity, format_currency(total_value)])

            vinculo_df = pd.DataFrame(vinculo_table, columns=['Serviço', 'Qualidade', 'Valor Unitário', 'Quantidade', 'Valor Total'])

            # Adicionar linha de total à tabela de vínculo e acompanhamento
            total_vinculo_value = sum(
                float(str(val).replace('R$ ', '').replace('.', '').replace(',', '.'))
                for val in vinculo_df['Valor Total']
            )
            total_vinculo_row = pd.DataFrame({
                'Serviço': ['Total'],
                'Qualidade': [''],
                'Valor Unitário': [''],
                'Quantidade': [0],  # CORREÇÃO: Usar 0 para quantidade total
                'Valor Total': [format_currency(total_vinculo_value)]
            })
            vinculo_df = pd.concat([vinculo_df, total_vinculo_row], ignore_index=True)

            st.table(vinculo_df)

            # COMPONENTE 03 - QUALIDADE
            st.subheader("Componente III - Qualidade")
            quality_table: list[list[str | int | float]] = []

            # Construindo a tabela de qualidade
            for service, quality_levels in quality_values.items():
                if Classificacao in quality_levels:
                    quantity = selected_services.get(service, 0)
                    if quantity > 0:
                        if service in edited_values:
                            value = edited_values[service]
                        else:
                            value = quality_levels[Classificacao]
                        total_value = value * quantity
                        quality_table.append([service, Classificacao, format_currency(value), quantity, format_currency(total_value)])

            quality_df = pd.DataFrame(quality_table, columns=['Serviço', 'Qualidade', 'Valor Unitário', 'Quantidade', 'Valor Total'])

            total_quality_value = sum(
                float(str(val).replace('R$ ', '').replace('.', '').replace(',', '.'))
                for val in quality_df['Valor Total']
            )
            total_quality_row = pd.DataFrame({
                'Serviço': ['Total'],
                'Qualidade': [''],
                'Valor Unitário': [''],
                'Quantidade': [0],  # CORREÇÃO: Usar 0 para quantidade total
                'Valor Total': [format_currency(total_quality_value)]
            })
            quality_df = pd.concat([quality_df, total_quality_row], ignore_index=True)

            st.table(quality_df)

            # IV - COMPONENTE PARA IMPLANTAÇÃO E MANUTENÇÃO DE PROGRAMAS, SERVIÇOS, PROFISSIONAIS E OUTRAS COMPOSIÇÕES DE EQUIPES QUE ATUAM NA APS
            st.subheader("IV - Componente para Implantação e Manutenção de Programas, Serviços, Profissionais e Outras Composições de Equipes")
            implantacao_manutencao_table: list[list[str | int | float]] = []

            # Todos os serviços que não estão em quality_values, têm valor em data e *não* são da Saúde Bucal
            implantacao_manutencao_services = [
                service for service in data
                if service not in quality_values
                and data[service]['valor'] != 'Sem cálculo'
                and service not in updated_categories.get('Saúde Bucal', []) # Removendo serviços da Saúde Bucal
            ]

            for service in implantacao_manutencao_services:
                quantity = selected_services.get(service, 0)
                if quantity > 0:
                    # Buscar valor unitário de config.json
                    try:
                        valor = float(data[service]['valor'].replace('R$ ', '').replace('.', '').replace(',', '.'))
                    except (ValueError, KeyError):
                        st.error(f"Valor inválido para {service} no config.json.")
                        valor = 0

                    # Verifica se o valor foi editado
                    if service in edited_values:
                        valor = edited_values[service]

                    total = valor * quantity
                    implantacao_manutencao_table.append([service, quantity, format_currency(valor), format_currency(total)])

            implantacao_manutencao_df = pd.DataFrame(implantacao_manutencao_table, columns=['Serviço', 'Quantidade', 'Valor Unitário', 'Valor Total'])

            total_implantacao_manutencao_value = sum(
                float(str(val).replace('R$ ', '').replace('.', '').replace(',', '.'))
                for val in implantacao_manutencao_df['Valor Total']
            )
            total_implantacao_manutencao_row = pd.DataFrame({
                'Serviço': ['Subtotal'],
                'Quantidade': [0],  # CORREÇÃO: Usar 0 para quantidade total
                'Valor Unitário': [''],
                'Valor Total': [format_currency(total_implantacao_manutencao_value)]
            })
            implantacao_manutencao_df = pd.concat([implantacao_manutencao_df, total_implantacao_manutencao_row], ignore_index=True)

            st.table(implantacao_manutencao_df)

            # V - COMPONENTE PARA ATENÇÃO À SAÚDE BUCAL
            st.subheader("V - Componente para Atenção à Saúde Bucal")
            saude_bucal_table: list[list[str | int | float]] = []

            # Adiciona as linhas de serviços da Saúde Bucal
            saude_bucal_services = updated_categories.get('Saúde Bucal', [])

            for service in saude_bucal_services:
                quantity = selected_services.get(service, 0)
                if quantity > 0:
                    # Buscar valor unitário de config.json (CORREÇÃO AQUI - quality_values só deve ser usado no componente III)
                    try:
                        valor = float(data[service]['valor'].replace('R$ ', '').replace('.', '').replace(',', '.'))
                    except (ValueError, KeyError):
                        st.error(f"Valor inválido para {service} no config.json.")
                        valor = 0

                    # Verifica se o valor foi editado
                    if service in edited_values:
                        valor = edited_values[service]  # Sobrescreve o valor padrão se foi editado

                    total = valor * quantity
                    saude_bucal_table.append([service, quantity, format_currency(valor), format_currency(total)])

            saude_bucal_df = pd.DataFrame(saude_bucal_table, columns=['Serviço', 'Quantidade', 'Valor Unitário', 'Valor Total'])

            # Preencher valores vazios na coluna 'Quantidade' com 0 e garantir tipo int
            saude_bucal_df['Quantidade'] = saude_bucal_df['Quantidade'].fillna(0).astype(int)

            total_saude_bucal_value = sum(
                float(str(val).replace('R$ ', '').replace('.', '').replace(',', '.'))
                for val in saude_bucal_df['Valor Total'].tolist()
            )

            total_saude_bucal_row = pd.DataFrame({
                'Serviço': ['Subtotal'],
                'Quantidade': [0],  # CORREÇÃO: Usar 0 para quantidade total
                'Valor Unitário': [''],
                'Valor Total': [format_currency(total_saude_bucal_value)]
            })
            saude_bucal_df = pd.concat([saude_bucal_df, total_saude_bucal_row], ignore_index=True)

            st.table(saude_bucal_df)

            # COMPONENTE PER CAPITA (CÁLCULO SIMPLIFICADO)
            st.subheader("VI - Componente Per Capita (Cálculo Simplificado)")
            populacao = st.session_state.get('populacao', 0)
            valor_per_capita = 5.95
            total_per_capita = (valor_per_capita * populacao) / 12

            per_capita_df = pd.DataFrame({
                'Descrição': ['Valor per capita', 'População', 'Total Per Capita (Mensal)'],
                'Valor': [format_currency(valor_per_capita), populacao, format_currency(total_per_capita)]
            })
            st.table(per_capita_df)

            # CÁLCULO DO TOTAL GERAL
            total_geral = total_fixed_value + total_vinculo_value + total_quality_value + total_implantacao_manutencao_value + total_saude_bucal_value + total_per_capita
            
            # CÁLCULO DO INCENTIVO FINANCEIRO DA APS - ESF E EAP
            total_incentivo_aps = total_fixed_value + total_quality_value + total_vinculo_value
            
            # Adicionar linhas de implantação ao total do incentivo financeiro da APS
            for service in ["eSF", "eAP 30h", "eAP 20h"]:
                if service in implantacao_values and selected_services.get(service, 0) > 0:
                    if service in edited_implantacao_values:
                        valor_implantacao = edited_implantacao_values[service]
                    else:
                        valor_implantacao = float(implantacao_values.get(service, "R$ 0,00").replace('R$ ', '').replace('.', '').replace(',', '.'))

                    if service in edited_implantacao_quantity:
                        quantity_implantacao = edited_implantacao_quantity[service]
                    else:
                        quantity_implantacao = 0

                    total_incentivo_aps += valor_implantacao * quantity_implantacao

            # CÁLCULO DO INCENTIVO FINANCEIRO DA APS - EMULTI
            total_incentivo_emulti = 0
            for service in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
                if selected_services.get(service, 0) > 0:
                    # Custeio mensal
                    if service in edited_values:
                        valor_custeio = edited_values[service]
                    else:
                        try:
                            valor_custeio = float(data[service]['valor'].replace('R$ ', '').replace('.', '').replace(',', '.'))
                        except (ValueError, KeyError):
                            valor_custeio = 0

                    # Qualidade
                    if service in quality_values:
                        if service in edited_values:
                            valor_qualidade = edited_values[service]
                        else:
                            valor_qualidade = quality_values[service][Classificacao]
                    else:
                        valor_qualidade = 0

                    # Implantação
                    if service in edited_implantacao_values:
                        valor_implantacao = edited_implantacao_values[service]
                    else:
                        if service == "eMULTI Ampl.":
                            valor_implantacao = float(implantacao_values.get("eMulti Ampliada", "R$ 0,00").replace('R$ ', '').replace('.', '').replace(',', '.'))
                        elif service == "eMULTI Compl.":
                            valor_implantacao = float(implantacao_values.get("eMulti Complementar", "R$ 0,00").replace('R$ ', '').replace('.', '').replace(',', '.'))
                        elif service == "eMULTI Estrat.":
                            valor_implantacao = float(implantacao_values.get("eMulti Estratégica", "R$ 0,00").replace('R$ ', '').replace('.', '').replace(',', '.'))
                        else:
                            valor_implantacao = 0
                    
                    if service in edited_implantacao_quantity:
                        quantity_implantacao = edited_implantacao_quantity[service]
                    else:
                        quantity_implantacao = 0

                    total_incentivo_emulti += (valor_custeio + valor_qualidade + (valor_implantacao * quantity_implantacao)) * selected_services.get(service, 0)

            # TABELA FINAL COM TOOLTIPS
            tabela_final_data = [
                {
                    "Ação Detalhada": "Incentivo financeiro da APS – equipes de Saúde da Família - eSF e equipes de Atenção Primária - eAP",
                    "Valor": format_currency(total_incentivo_aps),
                    "Descrição": "Consiste no somatório dos componentes fixo, qualidade e vínculo e acompanhamento territorial, bem como incentivo de implantação para equipes implantadas a partir da parcela 05/2024 (CNES março)."
                },
                {
                    "Ação Detalhada": "Incentivo financeiro da APS – equipes Multiprofissionais - eMulti",
                    "Valor": format_currency(total_incentivo_emulti),
                    "Descrição": "Consiste no somatório dos componentes de custeio mensal e ao componente de qualidade das equipes Multiprofissionais (eMulti), bem como incentivo de implantação para equipes implantadas a partir da parcela 05/2024 (CNES março)."
                },
                {
                    "Ação Detalhada": "Incentivo financeiro da APS – Demais programas, serviços e equipes da Atenção Primária à Saúde",
                    "Valor": format_currency(total_implantacao_manutencao_value),
                    "Descrição": "Consiste no custeio de programas, serviços, profissionais e outras composições de equipe que atuam na APS, quais sejam: I - das equipes de Consultório na Rua - eCR; II - das Unidades Básicas de Saúde Fluvial - UBSF; III - das equipes de Saúde da Família Ribeirinha - eSFR; IV - das equipes de Atenção Primária Prisional - eAPP; V - para o ente federativo responsável pela gestão das ações de atenção integral à saúde dos adolescentes em situação de privação de liberdade; VI - do incentivo aos municípios com equipes de saúde integradas a programas de residência uniprofissional ou multiprofissional na Atenção Primária à Saúde; VII - do Programa Saúde na Escola - PSE; VIII - do incentivo financeiro federal de custeio para implementação de ações de atividade física no âmbito da APS - IAF; IX - dos profissionais microscopistas; X - da Estratégia de Agentes Comunitários de Saúde - ACS; e XI - de outros programas, serviços, profissionais e composições de equipe que venham a ser instituídos por meio de ato normativo específico do Ministério da Saúde."
                },
                {
                    "Ação Detalhada": "Incentivo financeiro da APS – Componente per capita de base populacional",
                    "Valor": format_currency(total_per_capita),
                    "Descrição": "Consiste no repasse de recursos aos entes federativos, com base em critério populacional de acordo com Censo 2022 para municípios com estabilidade ou ganho populacional, de acordo com o valor per capita de 5,95 conforme Portaria 3732/024 - Anexo I."
                },
                {
                    "Ação Detalhada": "Incentivo financeiro da APS – Manutenção de pagamento de valor nominal com base em exercício anterior",
                    "Valor": "R$ 0,00",  # Valor não calculado, pois não há uma lógica definida no código atual
                    "Descrição": "Consiste no repasse de recursos aos entes subnacionais que tiveram perda populacional no Censo 2022, com a manutenção do valor nominal repassado no ano anterior, conforme Portaria nº 3732/2024 - Anexo II."
                },
                {
                    "Ação Detalhada": "Incentivo Compensatório de Transição",
                    "Valor": "R$ 0,00",  # Valor não calculado, pois não há uma lógica definida no código atual
                    "Descrição": "Consiste no repasse do incentivo compensatório de transição aos entes federativos que apresentaram redução dos valores dos componentes recebidos no âmbito da Atenção Primária à Saúde (APS) em comparação com os valores nominais recebidos nas últimas doze parcelas anteriores a vigência da nova metodologia de cofinanciamento. Os entes federativos farão jus, até saírem da situação de perda, a um valor adicional mensal de compensação, correspondente ao valor da redução acrescido de 10%, desde que seja mantido o quantitativo equivalente de eSF e eAP."
                },
                {
                    "Ação Detalhada": "Incentivo financeiro da APS – Atenção à Saúde Bucal",
                    "Valor": format_currency(total_saude_bucal_value),
                    "Descrição": "Consiste no somatório do custeio mensal, e qualidade das Equipes de Saúde Bucal, à implantação das Unidades Odontológicas Móveis (UOM), ao custeio e ao componente de qualidade de Centros de Especialidades Odontológicas (CEO), ao custeio de Laboratórios Regionais de Prótese Dentária (LRPD), à implantação, ao custeio e ao componente de qualidade de Serviços de Especialidades em Saúde Bucal (Sesb)."
                },
                {
                    "Ação Detalhada": "Agentes Comunitários de Saúde",
                    "Valor": "R$ 0,00",  # Valor não calculado, pois não há uma lógica definida no código atual
                    "Descrição": "Consiste no custeio mensal aos Agentes Comunitários de Saúde"
                },
            ]

            tabela_final_df = pd.DataFrame(tabela_final_data)

            # Aqui estava o erro, a coluna já havia sido removida anteriormente
            # tabela_final_df_sem_descricao = tabela_final_df.drop(columns=["Descrição"])

            # Adicionar CSS para os tooltips, largura da coluna e alinhamento à direita
            st.markdown(
                """
                <style>
                .tooltip {
                  position: relative;
                  display: inline-block;
                  border-bottom: 1px dotted black;
                }

                .tooltip .tooltiptext {
                  visibility: hidden;
                  width: 300px;
                  background-color: black;
                  color: #fff;
                  text-align: center;
                  border-radius: 6px;
                  padding: 5px 0;
                  position: absolute;
                  z-index: 1;
                  top: 150%;
                  left: 50%;
                  margin-left: -150px;
                }

                .tooltip .tooltiptext::after {
                  content: "";
                  position: absolute;
                  bottom: 100%;
                  left: 50%;
                  margin-left: -5px;
                  border-width: 5px;
                  border-style: solid;
                  border-color: transparent transparent black transparent;
                }

                .tooltip:hover .tooltiptext {
                  visibility: visible;
                }

                /* Estilo para a tabela */
                table {
                    width: 80%; /* Ajuste a largura da tabela conforme necessário */
                    margin: 0 auto; /* Centraliza a tabela */
                    border-collapse: collapse;
                }

                th, td {
                    text-align: left;
                    padding: 8px;
                    border: 1px solid #ddd; /* Adiciona bordas às células */
                }

                th:nth-child(2), td:nth-child(2) {
                    width: 30%; /* Ajuste a largura da coluna Valor */
                    text-align: right; /* Alinha os valores à direita */
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            # Função para gerar a tabela HTML com tooltips
            def generate_html_table_with_tooltips(df, tooltip_column):
                html = "<table>"
                html += "<thead><tr>"
                for col in df.columns:
                    html += f"<th>{col}</th>"
                html += "</tr></thead>"
                html += "<tbody>"
                for index, row in df.iterrows():
                    html += "<tr>"
                    for col in df.columns:
                        if col == "Ação Detalhada":
                            html += f"<td><div class='tooltip'>{row[col]}<span class='tooltiptext'>{tooltip_column.iloc[index]}</span></div></td>"
                        else:
                            html += f"<td>{row[col]}</td>"
                    html += "</tr>"
                html += "</tbody></table>"
                return html

            # Gerar a tabela HTML com tooltips
            html_table = generate_html_table_with_tooltips(tabela_final_df.drop(columns=["Descrição"]), tabela_final_df["Descrição"])

            # EXIBIÇÃO DA TABELA FINAL COM TOOLTIPS
            st.subheader("Resumo dos Incentivos Financeiros da APS")
            st.markdown(html_table, unsafe_allow_html=True)

            # Destaque para o valor total geral
            st.markdown(f"<h3 style='text-align: center; color: blue;'>Total Geral: {format_currency(total_geral)}</h3>", unsafe_allow_html=True)

    else:
        st.error("Não há dados para calcular. Realize uma consulta na API primeiro.")
        
        
        
        
        
        
        
        
        #=============================================== PARTE 7 ===============================================

def gerar_relatorio_cenarios(total_geral, vinculo_values, quality_values, selected_services, total_implantacao_manutencao_value, total_saude_bucal_value, total_per_capita, total_fixed_value):
    """
    Gera um relatório detalhado dos valores para cada cenário de desempenho e constrói um DataFrame
    para o quadro de comparação (PARTE 6) iterando sobre as linhas das tabelas geradas.

    **A exibição dos quadros do relatório detalhado foi movida para fora desta função,
    para que a PARTE 7 apenas gere o DataFrame e a PARTE 6 exiba a tabela.**

    Args:
        total_geral: Valor total geral calculado (usado como referência para o modelo anterior).
        vinculo_values: Dicionário com os valores de vínculo e acompanhamento por qualidade.
        quality_values: Dicionário com os valores de qualidade por classificação.
        selected_services: Dicionário com os serviços selecionados e suas quantidades.
        total_implantacao_manutencao_value: Valor total de implantação e manutenção.
        total_saude_bucal_value: Valor total de saúde bucal.
        total_per_capita: Valor total per capita.
        total_fixed_value: Valor total fixo.

    Returns:
        pd.DataFrame: DataFrame para o quadro de comparação (PARTE 6).
    """

    cenarios = ['Regular', 'Suficiente', 'Bom', 'Ótimo']

    # Valor base (modelo anterior) - Total geral anterior, calculado na PARTE 4
    valor_base = total_geral

    # DataFrame para o quadro de comparação (PARTE 6)
    dados_comparacao = []

    for cenario in cenarios:
        # Zera os valores para cada cenário
        valor_vinculo = 0
        valor_qualidade = 0
        valor_emulti = 0

        # Vínculo e Acompanhamento
        for service in vinculo_values:
            if service in selected_services:
                valor_vinculo += vinculo_values[service].get(cenario, 0) * selected_services.get(service, 0)

        # Qualidade
        for service in quality_values:
            if service in selected_services:
                valor_qualidade += quality_values[service].get(cenario, 0) * selected_services.get(service, 0)

        # eMulti
        for service in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
            if selected_services.get(service, 0) > 0:
                valor_emulti += quality_values.get(service, {}).get(cenario, 0) * selected_services.get(service, 0)

        # Calcula o valor total do cenário atual
        valor_cenario = total_fixed_value + valor_vinculo + valor_qualidade + total_implantacao_manutencao_value + total_saude_bucal_value + total_per_capita + valor_emulti

        # Diferença e aumento percentual
        diferenca = valor_cenario - valor_base
        aumento_percentual = (diferenca / valor_base) * 100 if valor_base != 0 else 0.00

        # Adiciona dados para o quadro de comparação (PARTE 6)
        dados_comparacao.append({
            'Valor Total Atual': format_currency(valor_base),
            'Desempenho': cenario.upper(),  # Convertido para maiúsculas
            'Valor Total do Cenário': format_currency(valor_cenario),
            'Diferença Mensal': format_currency(diferenca),
            'Variação %': aumento_percentual
        })

    # Cria DataFrame para o quadro de comparação (PARTE 6)
    df_comparacao = pd.DataFrame(dados_comparacao)

    return df_comparacao

# Chamando a função e exibindo o resultado
if calcular_button:
    if st.session_state['dados']:
        # ... (Todos os cálculos das partes anteriores permanecem inalterados)

        # Gerando o DataFrame para a PARTE 6
        df_comparacao = gerar_relatorio_cenarios(total_geral, vinculo_values, quality_values, selected_services, total_implantacao_manutencao_value, total_saude_bucal_value, total_per_capita, total_fixed_value)

        # Exibindo o Relatório Detalhado por Cenário (Quadros) - (Código novo)
        st.subheader("Relatório Detalhado por Cenário")
        cenarios = ['Regular', 'Suficiente', 'Bom', 'Ótimo']
        cores_cenarios = {
            'Regular': '#8B0000',
            'Suficiente': '#FFA500',
            'Bom': '#006400',
            'Ótimo': '#000080'
        }

        # Definindo valor_base (CORREÇÃO AQUI)
        valor_base = total_geral

        for cenario in cenarios:
            cor_cenario = cores_cenarios.get(cenario)
            st.markdown(f"<h3 style='color:{cor_cenario}'>Cenário: {cenario}</h3>", unsafe_allow_html=True)

            # Zera os valores para cada cenário
            valor_vinculo = 0
            valor_qualidade = 0
            valor_emulti = 0

            # Vínculo e Acompanhamento
            for service in vinculo_values:
                if service in selected_services:
                    valor_vinculo += vinculo_values[service].get(cenario, 0) * selected_services.get(service, 0)

            # Qualidade
            for service in quality_values:
                if service in selected_services:
                    valor_qualidade += quality_values[service].get(cenario, 0) * selected_services.get(service, 0)

            # eMulti
            for service in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
                if selected_services.get(service, 0) > 0:
                    valor_emulti += quality_values.get(service, {}).get(cenario, 0) * selected_services.get(service, 0)

            # Calcula o valor total do cenário atual
            valor_cenario = total_fixed_value + valor_vinculo + valor_qualidade + total_implantacao_manutencao_value + total_saude_bucal_value + total_per_capita + valor_emulti

            # Diferença e aumento percentual
            diferenca = valor_cenario - valor_base
            aumento_percentual = ((valor_cenario - valor_base) / valor_base) * 100 if valor_base != 0 else 0

            # Cria a tabela para o cenário atual
            tabela_dados = []
            tabela_dados.append({
                'Componente': 'Valor Base (Recebia na APS Mensalmente)',
                'Valor': format_currency(valor_base)
            })
            tabela_dados.append({
                'Componente': 'Valor Fixo',
                'Valor': format_currency(total_fixed_value)
            })
            tabela_dados.append({
                'Componente': 'Vínculo e Acompanhamento',
                'Valor': format_currency(valor_vinculo)
            })
            tabela_dados.append({
                'Componente': 'Qualidade',
                'Valor': format_currency(valor_qualidade)
            })
            tabela_dados.append({
                'Componente': 'eMulti',
                'Valor': format_currency(valor_emulti)
            })
            tabela_dados.append({
                'Componente': 'Implantação/Manutenção',
                'Valor': format_currency(total_implantacao_manutencao_value)
            })
            tabela_dados.append({
                'Componente': 'Saúde Bucal',
                'Valor': format_currency(total_saude_bucal_value)
            })
            tabela_dados.append({
                'Componente': 'Per Capita',
                'Valor': format_currency(total_per_capita)
            })
            tabela_dados.append({
                'Componente': f"<span style='font-weight: bold; color: {cor_cenario}'>Total do Cenário ({cenario})</span>",
                'Valor': f"<span style='font-weight: bold; color: {cor_cenario}'>{format_currency(valor_cenario)}</span>"
            })
            tabela_dados.append({
                'Componente': 'Diferença (Aumentou Mensal)',
                'Valor': format_currency(diferenca)
            })
            tabela_dados.append({
                'Componente': 'Aumento Percentual',
                'Valor': f"{aumento_percentual:.0f}%"
            })

            # Cria DataFrame e exibe a tabela
            df = pd.DataFrame(tabela_dados)

            # Formatação condicional e remove índice
            st.markdown(df.style.map(lambda x: f"background-color: {cores_cenarios.get(cenario, '')};" if x == cenario else '', subset=['Componente'])
                      .format({'Valor': '{:}'})
                      .set_table_styles([
                          {'selector': 'th', 'props': [('background-color', cor_cenario), ('color', 'white'), ('text-align', 'center'), ('border', '1px solid black'), ('font-weight', 'bold')]},
                          {'selector': 'td', 'props': [('text-align', 'left'), ('border', '1px solid black')]},
                          {'selector': 'td:nth-child(2)', 'props': [('text-align', 'right')]},
                          {'selector': 'tr:last-child td', 'props': [('font-weight', 'bold')]},
                          {'selector': '', 'props': [('border-collapse', 'collapse'), ('width', '80%'), ('margin', '0 auto')]},
                          {'selector': '.col0', 'props': [('width', '450px')]}
                      ])
                      .hide(axis="index")
                      .to_html(escape=False), unsafe_allow_html=True)
            st.divider()

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        #=============================================== PARTE 5 ===============================================

def gerar_analise_cenarios(total_incentivo_aps, total_incentivo_emulti, total_geral, vinculo_values, quality_values, selected_services, total_fixed_value, total_implantacao_manutencao_value, total_saude_bucal_value, total_per_capita):
    """
    Gera o texto de análise dos cenários com base nos valores calculados.

    Args:
        total_incentivo_aps: Valor total do incentivo financeiro da APS para eSF e eAP.
        total_incentivo_emulti: Valor total do incentivo financeiro da APS para eMulti.
        total_geral: Valor total geral calculado.
        vinculo_values: Dicionário com os valores de vínculo e acompanhamento por qualidade.
        quality_values: Dicionário com os valores de qualidade por classificação.
        selected_services: Dicionário com os serviços selecionados e suas quantidades.
        total_fixed_value: Valor total do componente fixo.
        total_implantacao_manutencao_value: Valor total de implantação e manutenção.
        total_saude_bucal_value: Valor total de saúde bucal.
        total_per_capita: Valor total per capita.

    Returns:
        str: Texto de análise dos cenários.
    """

    # Valores no modelo anterior (hipotético - você precisará ajustar com base em dados reais)
    # Neste exemplo, estou considerando que o modelo anterior seria apenas o valor fixo + per capita
    valor_modelo_anterior = total_fixed_value + total_per_capita

    # Cenário de pior desempenho (Regular)
    pior_desempenho_vinculo = sum(vinculo_values[service]['Regular'] * selected_services.get(service, 0) for service in vinculo_values if service in selected_services)
    pior_desempenho_qualidade = sum(quality_values[service]['Regular'] * selected_services.get(service, 0) for service in quality_values if service in selected_services)

    # Cenário eMulti Regular
    pior_desempenho_emulti = 0
    for service in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
        if selected_services.get(service, 0) > 0:
            if service in quality_values:
                valor_qualidade = quality_values[service]['Regular']
            else:
                valor_qualidade = 0

            pior_desempenho_emulti += valor_qualidade * selected_services.get(service, 0)

    valor_pior_desempenho = total_fixed_value + pior_desempenho_vinculo + pior_desempenho_qualidade + total_implantacao_manutencao_value + total_saude_bucal_value + total_per_capita + pior_desempenho_emulti

    # Cenário de melhor desempenho (Ótimo)
    melhor_desempenho_vinculo = sum(vinculo_values[service]['Ótimo'] * selected_services.get(service, 0) for service in vinculo_values if service in selected_services)
    melhor_desempenho_qualidade = sum(quality_values[service]['Ótimo'] * selected_services.get(service, 0) for service in quality_values if service in selected_services)

    # Cenário eMulti Ótimo
    melhor_desempenho_emulti = 0
    for service in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
        if selected_services.get(service, 0) > 0:
            if service in quality_values:
                valor_qualidade = quality_values[service]['Ótimo']
            else:
                valor_qualidade = 0

            melhor_desempenho_emulti += valor_qualidade * selected_services.get(service, 0)

    valor_melhor_desempenho = total_fixed_value + melhor_desempenho_vinculo + melhor_desempenho_qualidade + total_implantacao_manutencao_value + total_saude_bucal_value + total_per_capita + melhor_desempenho_emulti

    # Diferença entre os cenários
    diferenca = valor_melhor_desempenho - valor_pior_desempenho

    # Porcentagem de aumento
    porcentagem_aumento = ((valor_melhor_desempenho - valor_pior_desempenho) / valor_pior_desempenho) * 100 if valor_pior_desempenho != 0 else 0

    # Texto da análise
    texto_analise = f"""
    <div style="text-align: justify; color: #2c3e50; font-size: 1.1rem">
        <p>
            <b style="font-size: 1.3rem; color: #008080">ANÁLISE DOS CENÁRIOS</b><br>
            O quadro abaixo contém de forma consolidada mensalmente (a cada mês) uma comparação dos valores recebidos no modelo anterior e no cofinanciamento federal da APS. Nele, recomenda-se observar, especialmente se conforme o desempenho, o município tem <span style="color: #008000; font-weight: bold">aumento</span> ou <span style="color: #8B0000; font-weight: bold">redução</span> de repasses federais na APS. Valores negativos (com sinal de <span style="font-weight: bold">menos-</span>) representam diminuição do valor em relação ao modelo de financiamento anterior. No cenário de pior desempenho, <span style="color: #8B0000; font-weight: bold">“REGULAR”</span>, o município recebe o valor de <span style="color: #8B0000; font-weight: bold">{format_currency(valor_pior_desempenho)}</span> e no cenário de melhor desempenho, <span style="color: #008000; font-weight: bold">“ÓTIMO”</span>, o município recebe o valor de <span style="color: #008000; font-weight: bold">{format_currency(valor_melhor_desempenho)}</span>. A diferença de <span style="background-color: #FFFFE0; font-weight: bold">{format_currency(diferenca)}</span> <span style="font-weight: bold">MENSAL</span> está relacionada aos componentes de <span style="font-weight: bold">vínculo e acompanhamento e qualidade</span> que são os valores variáveis do cofinanciamento federal na APS. <span style="color: #008000; font-weight: bold">AUMENTO DE MAIS DE {porcentagem_aumento:.2f}%</span>, EQUIVALENTE A QUASE <span style="color: #008000; font-weight: bold">{format_currency(diferenca * 12)}</span> SOMENTE NESTE ITEM.
        </p>
    </div>
    """

    return texto_analise

# Chamando a função e exibindo o resultado
if calcular_button:
    if st.session_state['dados']:
        # ... (Todos os cálculos das partes anteriores permanecem inalterados)

        # Gerando a análise dos cenários
        texto_analise = gerar_analise_cenarios(total_incentivo_aps, total_incentivo_emulti, total_geral, vinculo_values, quality_values, selected_services, total_fixed_value, total_implantacao_manutencao_value, total_saude_bucal_value, total_per_capita)

        # Exibindo a análise dos cenários

        st.markdown(texto_analise, unsafe_allow_html=True)

    else:
        st.error("Não há dados para calcular. Realize uma consulta na API primeiro.")

#=============================================== PARTE 6 ===============================================

# Chamando a função e exibindo o resultado (modificado para usar o DataFrame da PARTE 7)
if calcular_button:
    if st.session_state['dados']:
        # ... (Todos os cálculos das partes anteriores permanecem inalterados)
        
        from __main__ import gerar_relatorio_cenarios

        # Gerando o relatório de cenários (PARTE 7) e obtendo o DataFrame para o quadro de comparação
        df_comparacao = gerar_relatorio_cenarios(total_geral, vinculo_values, quality_values, selected_services, total_implantacao_manutencao_value, total_saude_bucal_value, total_per_capita, total_fixed_value)

        # Exibindo o quadro de comparação
        st.subheader("Quadro de Comparação de Valores Conforme os Cenários de Qualificação de Desempenho da APS")

        # CSS para a tabela (MODIFICADO PARA LETRAS BRANCAS EM NEGRITO)
        st.markdown(
            """
            <style>
            .dataframe {
                width: 100%;
                border-collapse: collapse;
            }
            .dataframe th {
                background-color: #4682B4; /* Azul médio */
                color: white; /* Cabeçalhos em branco */
                text-align: center;
                padding: 8px;
                border: 1px solid black;
                font-weight: bold;
            }
            .dataframe td {
                text-align: center;
                padding: 8px;
                border: 1px solid black;
                font-size: 1.05em;
                color: white; /* Todas as células em branco */
                font-weight: bold; /* Todas as células em negrito */
            }
            .dataframe td:nth-child(1), .dataframe td:nth-child(3), .dataframe td:nth-child(4) {
                font-weight: bold;
            }
            .dataframe td:nth-child(1), .dataframe td:nth-child(4), .dataframe td:nth-child(5) {
                text-align: right; /* Alinha as colunas específicas à direita */
            }
            /* Formatação condicional para a linha inteira baseada no desempenho */
            .optimo {
                background-color: #000080; /* Azul escuro */
            }
            .bom {
                background-color: #006400; /* Verde escuro */
            }
            .suficiente {
                background-color: #FFA500; /* Laranja */
            }
            .regular {
                background-color: #8B0000; /* Vermelho escuro */
            }
            .st-ae { /* Ajusta a altura do header */
                padding-top: 0px !important;
                padding-bottom: 0px !important;
            }
            .st-bf { /* Ajusta a altura das linhas */
                padding-top: 0px !important;
                padding-bottom: 0px !important;
            }
            .st-bb { /* Ajusta a altura das linhas */
                padding-top: 0px !important;
                padding-bottom: 0px !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Função para aplicar estilo em toda a linha (MANTIDA INALTERADA)
        def style_rows(row):
            if row['Desempenho'] == 'ÓTIMO':
                return ['background-color: #000080; color: white'] * len(row)  # Azul escuro
            elif row['Desempenho'] == 'BOM':
                return ['background-color: #006400; color: white'] * len(row)  # Verde escuro
            elif row['Desempenho'] == 'SUFICIENTE':
                return ['background-color: #FFA500; color: white'] * len(row)  # Laranja
            elif row['Desempenho'] == 'REGULAR':
                return ['background-color: #8B0000; color: white'] * len(row)  # Vermelho escuro
            else:
                return [''] * len(row)

        # Função para formatar a Variação %
        def format_variacao_porcentagem(val):
            """Formata a variação percentual com duas casas decimais e símbolo de porcentagem."""
            try:
                if isinstance(val, str):
                    # Se for string, tenta converter para float
                    num = float(val.replace('%', '').strip())
                elif isinstance(val, (int, float)):
                    num = val
                else:
                    return val
                return f"{num:.2f}%"
            except ValueError:
                return val  # Retorna o valor original se houver erro na conversão

        # Aplicar estilos ao DataFrame (MODIFICADO PARA TRATAR ERROS DE FORMATAÇÃO)
        styled_df = df_comparacao.style.apply(style_rows, axis=1) \
            .format({'Valor Total Atual': '{:}',
                     'Valor Total do Cenário': '{:}',
                     'Diferença Mensal': '{:}',
                     'Variação %': format_variacao_porcentagem}) # Usando a função de formatação

        st.dataframe(styled_df)


#=============================================== PARTE 8 ===============================================

        # ... (Inicialização das variáveis em st.session_state, expander com inputs - tudo permanece igual)

        # Só exibe o RESULTADO do cálculo se o botão "Calcular" já tiver sido pressionado
        if calcular_button:
            # Indica que o cálculo foi realizado
            st.session_state['calculo_realizado'] = True
        if st.session_state['calculo_realizado']:
            # Obtendo o nome do município e UF do st.session_state['dados']
            if st.session_state['dados'] and 'resumosPlanosOrcamentarios' in st.session_state['dados'] and len(st.session_state['dados']['resumosPlanosOrcamentarios']) > 0:
                municipio_selecionado = st.session_state['dados']['resumosPlanosOrcamentarios'][0].get('noMunicipio', 'Não informado')
                uf_selecionada = st.session_state['dados']['resumosPlanosOrcamentarios'][0].get('sgUf', 'Não informado')
            else:
                municipio_selecionado = "Não informado"
                uf_selecionada = "Não informado"

            # CÁLCULO DO CENÁRIO REGULAR (NECESSÁRIO PARA A NOVA LÓGICA)
            valor_cenario_regular = 0
            if st.session_state['dados']:
                # Zera os valores para o cenário regular
                valor_vinculo_regular = 0
                valor_qualidade_regular = 0
                valor_emulti_regular = 0

                # Vínculo e Acompanhamento (Regular)
                for service in vinculo_values:
                    if service in selected_services:
                        valor_vinculo_regular += vinculo_values[service].get('Regular', 0) * selected_services.get(service, 0)

                # Qualidade (Regular)
                for service in quality_values:
                    if service in selected_services:
                        valor_qualidade_regular += quality_values[service].get('Regular', 0) * selected_services.get(service, 0)

                # eMulti (Regular)
                for service in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
                    if selected_services.get(service, 0) > 0:
                        valor_emulti_regular += quality_values.get(service, {}).get('Regular', 0) * selected_services.get(service, 0)

                # Calcula o valor total do cenário regular
                valor_cenario_regular = total_fixed_value + valor_vinculo_regular + valor_qualidade_regular + total_implantacao_manutencao_value + total_saude_bucal_value + total_per_capita + valor_emulti_regular

            # Cálculos para o texto (NOVA LÓGICA)
            total_parametros = st.session_state['valor_esf_eap'] + st.session_state['valor_saude_bucal'] + st.session_state['valor_acs'] + st.session_state['valor_estrategicas']
            aumento_mensal = total_parametros - valor_cenario_regular  # Diferença entre o total adicional e o cenário regular
            aumento_anual = aumento_mensal * 12

            # Exibindo os valores inseridos em uma tabela chamativa
            st.subheader("Projeção de Aumento de Recursos")
            df_parametros = pd.DataFrame({
                'Parâmetro': ["Incentivo Financeiro da APS eSF ou eAP", "Incentivo Financeiro para Atenção à Saúde Bucal", "Total ACS", "Ações Estratégicas", "Total Adicional"],
                'Valor': [float(st.session_state['valor_esf_eap']),  # Convertido para float
                          float(st.session_state['valor_saude_bucal']),  # Convertido para float
                          float(st.session_state['valor_acs']),  # Convertido para float
                          float(st.session_state['valor_estrategicas']),  # Convertido para float
                          float(total_parametros)]  # Convertido para float
            })

            def style_table(val):
                if isinstance(val, (int, float)):
                    return f'background-color: #008080; color: white; font-weight: bold; text-align: right; font-size: 1.2rem'
                return ''

            # Define uma paleta de cores
            colors = ['#e6ffe6', '#ccffcc', '#b3ffb3', '#99ff99', '#80ff80']

            def highlight_row(row):
                if row.name == len(df_parametros) - 1:  # Última linha (Total Adicional)
                    return [f'background-color: #008080; color: white;'] * len(row) # Cor de fundo para o Total
                else:
                    return [f'background-color: {colors[row.name % len(colors)]}; color: #2c3e50;'] * len(row) # Cor de fundo para as demais linhas, alternando as cores

            st.dataframe(df_parametros.style.format({'Valor': '{:,.2f}'.format}).map(style_table, subset=['Valor']).apply(highlight_row, axis=1))

            # Texto descritivo com valores calculados (COM A NOVA LÓGICA)
            st.markdown(f"""
                <div style="text-align: justify; color: #2c3e50; font-size: 1.1rem">
                    <p>
                        Considerando os valores informados, e subtraindo o valor do cenário <b>REGULAR ({format_currency(valor_cenario_regular)})</b>,
                        espera-se que o <b style="color: #008080">AUMENTO SEJA DE R$ {format_currency(aumento_mensal).replace('R$', '', 1).strip()} MIL MENSAIS</b>,
                        resultando em <b style="color: #008080">APROXIMADAMENTE R$ {format_currency(aumento_anual).replace('R$', '', 1).strip()} MIL ANUAL</b>,
                        comparado com o cenário de pior desempenho. Estes valores são projetados para o município de
                        <b style="color: #008080">{municipio_selecionado} - {uf_selecionada}</b>, levando em conta os parâmetros adicionais fornecidos.
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Se o botão ainda não foi clicado, exibe a mensagem
            st.info("Preencha os parâmetros, selecione o município e clique em 'Calcular' para gerar os resultados.")

    else:
        st.error("Não há dados para calcular. Realize uma consulta na API primeiro.")
        