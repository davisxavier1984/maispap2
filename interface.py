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
            uf_selecionada = st.selectbox(
                "Selecione um Estado", 
                options=estados, 
                index=estados.index(st.session_state.get('uf_selecionada', "Não informado")) if st.session_state.get('uf_selecionada', "Não informado") in estados else 0,
                key="uf_selectbox"
            )
            st.session_state['uf_selecionada'] = uf_selecionada
        with col2:
            competencia = st.text_input(
                "Competência (AAAAMM)", 
                value=st.session_state.get('competencia', "202501"),
                key="competencia_input"
            )
            st.session_state['competencia'] = competencia

        if uf_selecionada:
            municipios = ufbr.list_cidades(uf_selecionada)
            municipio_selecionado = st.selectbox(
                "Selecione um Município", 
                options=municipios,
                index=municipios.index(st.session_state.get('municipio_selecionado', "Não informado")) if st.session_state.get('municipio_selecionado', "Não informado") in municipios else 0,
                key="municipio_selectbox"
            )
            st.session_state['municipio_selecionado'] = municipio_selecionado
            
            codigo_ibge_input = st.text_input(
                "Código IBGE do Município",
                value=st.session_state.get('codigo_ibge', ""),
                placeholder="Digite o código IBGE ou selecione um município",
                help="Digite o código IBGE do município com 7 dígitos",
                key="codigo_ibge_input"
            )
            
            st.session_state['codigo_ibge'] = codigo_ibge_input

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
            
            # Extrair e salvar população dos dados
            if dados:
                try:
                    if 'pagamentos' in dados and dados['pagamentos']:
                        populacao = dados['pagamentos'][0].get('qtPopulacao', 0)
                        if populacao > 0:
                            st.session_state['populacao'] = populacao
                            
                            # Também sincronizar com o StateManager
                            try:
                                from core.state_manager import StateManager
                                StateManager.set_dados_municipio(dados, municipio_selecionado, uf_selecionada, competencia)
                            except ImportError:
                                pass  # Se não conseguir importar, apenas continue
                except (KeyError, IndexError, TypeError):
                    pass

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
        opcoes = ['Regular', 'Suficiente', 'Bom', 'Ótimo']
        index_padrao = opcoes.index(st.session_state.get('classificacao', 'Bom')) if st.session_state.get('classificacao', 'Bom') in opcoes else 2
        classificacao = st.selectbox(
            "Considerar Qualidade", 
            options=opcoes, 
            index=index_padrao,
            key="classificacao_dropdown"
        )
        st.session_state['classificacao'] = classificacao

    with col_vinculo:
        opcoes = ['Regular', 'Suficiente', 'Bom', 'Ótimo']
        index_padrao = opcoes.index(st.session_state.get('vinculo', 'Bom')) if st.session_state.get('vinculo', 'Bom') in opcoes else 2
        vinculo = st.selectbox(
            "Vínculo e Acompanhamento Territorial", 
            options=opcoes, 
            index=index_padrao,
            key="vinculo_dropdown"
        )
        st.session_state['vinculo'] = vinculo
    
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
    # Garantir que o StateManager inicializou o estado
    from core.state_manager import StateManager
    StateManager.get_state()  # Isso garante a inicialização
    
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
            # Usar os valores armazenados na session_state
            services = st.session_state.get('selected_services', {})
            
            if all(q == 0 for q in services.values()):
                st.error("Por favor, selecione pelo menos um serviço para calcular.")
            else:
                # Utilizar os valores da session_state
                calculate_results(
                    st.session_state.get('selected_services', {}), 
                    st.session_state.get('edited_values', {}), 
                    st.session_state.get('edited_implantacao_values', {}), 
                    st.session_state.get('edited_implantacao_quantity', {}), 
                    st.session_state.get('classificacao', 'Bom'), 
                    st.session_state.get('vinculo', 'Bom')
                )
