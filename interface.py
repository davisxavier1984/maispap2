"""
Módulo para interface gráfica da Calculadora PAP.
"""
import streamlit as st
import pandas as pd
from pyUFbr.baseuf import ufbr
from utils import metric_card, format_currency, currency_to_float
from api import consultar_api, load_data_from_json
from components.services_interface import render_services_interface
from calculations import calculate_results

def setup_consulta_parameters():
    """Configura os parâmetros de consulta."""
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
            codigo_ibge_input = st.text_input(
                "Código IBGE do Município",
                placeholder="Digite o código IBGE ou selecione um município",
                help="Digite o código IBGE do município com 7 dígitos"
            )

            if codigo_ibge_input:
                if len(codigo_ibge_input.strip()) != 7:
                    st.warning("O código IBGE deve conter exatamente 7 dígitos")
                codigo_ibge = codigo_ibge_input
            elif municipio_selecionado:
                try:
                    codigo_ibge = str(int(float(ufbr.get_cidade(municipio_selecionado).codigo)))[:-1]
                except AttributeError:
                    st.error("Erro ao obter código IBGE do município")
                    return None, None, None

        if st.button("Consultar"):
            if not (uf_selecionada and municipio_selecionado and competencia):
                st.error("Por favor, preencha todos os campos de consulta.")
                return None, None, None

            dados = consultar_api(codigo_ibge, competencia)
            st.session_state['dados'] = dados

        return uf_selecionada, municipio_selecionado, competencia


def display_info_metrics():
    """Exibe as métricas de informações gerais."""
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
        

def setup_classification_dropdowns():
    """Configura os dropdowns de classificação e vínculo."""
    col_classificacao, col_vinculo = st.columns([1, 1])

    with col_classificacao:
        classificacao = st.selectbox("Considerar Qualidade", 
                              options=['Regular', 'Suficiente', 'Bom', 'Ótimo'], 
                              index=2)

    with col_vinculo:
        vinculo = st.selectbox("Vínculo e Acompanhamento Territorial", 
                        options=['Regular', 'Suficiente', 'Bom', 'Ótimo'], 
                        index=2)
    
    return classificacao, vinculo


def setup_extra_parameters():
    """Configura os parâmetros adicionais."""
    with st.expander("Parâmetros Adicionais", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.session_state['valor_esf_eap'] = st.number_input(
                "Incentivo Financeiro da APS eSF ou eAP", 
                value=st.session_state.get('valor_esf_eap', 0.0), 
                format="%.2f", 
                key="input_esf_eap"
            )
            st.session_state['valor_saude_bucal'] = st.number_input(
                "Incentivo Financeiro para Atenção à Saúde Bucal", 
                value=st.session_state.get('valor_saude_bucal', 0.0), 
                format="%.2f", 
                key="input_saude_bucal"
            )
        with col2:
            st.session_state['valor_acs'] = st.number_input(
                "Total ACS", 
                value=st.session_state.get('valor_acs', 0.0), 
                format="%.2f", 
                key="input_acs"
            )
            st.session_state['valor_estrategicas'] = st.number_input(
                "Ações Estratégicas", 
                value=st.session_state.get('valor_estrategicas', 0.0), 
                format="%.2f", 
                key="input_estrategicas"
            )

        # Cálculos para o total
        total_parametros = (st.session_state['valor_esf_eap'] + 
                           st.session_state['valor_saude_bucal'] + 
                           st.session_state['valor_acs'] + 
                           st.session_state['valor_estrategicas'])

        # Exibindo o total de forma chamativa dentro do expander
        st.markdown(
            f"<p style='text-align: center; font-size: 1.5rem; color: #008080; font-weight: bold'>"
            f"Total Adicional: {format_currency(total_parametros)}</p>", 
            unsafe_allow_html=True
        )


# A função format_currency já está importada de formatting_utils.py no início do arquivo


def setup_interface():
    """Configura a interface principal da aplicação."""
    # Inicializa valores na session_state
    if 'valor_esf_eap' not in st.session_state:
        st.session_state['valor_esf_eap'] = 0.0
    if 'valor_saude_bucal' not in st.session_state:
        st.session_state['valor_saude_bucal'] = 0.0
    if 'valor_acs' not in st.session_state:
        st.session_state['valor_acs'] = 0.0
    if 'valor_estrategicas' not in st.session_state:
        st.session_state['valor_estrategicas'] = 0.0
    if 'calculo_realizado' not in st.session_state:
        st.session_state['calculo_realizado'] = 0.0
    
    # Configuração dos parâmetros de consulta
    uf_selecionada, municipio_selecionado, competencia = setup_consulta_parameters()
    
    # Carrega os dados do data.json se existirem
    st.session_state['dados'] = load_data_from_json()

    # Exibe as métricas se houver dados
    if st.session_state['dados']:
        display_info_metrics()
        
        # Interface de seleção de serviços
        selected_services, edited_values, edited_implantacao_values, edited_implantacao_quantity = render_services_interface()
        
        # Parâmetros adicionais
        setup_extra_parameters()
        
        # Dropdowns de classificação e vínculo
        classificacao, vinculo = setup_classification_dropdowns()
        
        # Botão de calcular
        calcular_button = st.button('Calcular', use_container_width=True)
        
        # Cálculos e exibição dos resultados
        if calcular_button:
            if all(q == 0 for q in selected_services.values()):
                st.error("Por favor, selecione pelo menos um serviço para calcular.")
            else:
                calculate_results(selected_services, edited_values, edited_implantacao_values, 
                                 edited_implantacao_quantity, classificacao, vinculo)
