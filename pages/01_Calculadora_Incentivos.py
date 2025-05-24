"""
Página da Calculadora de Incentivos PAP.
"""
import streamlit as st
import json
from components.services_interface import render_services_interface
from calculations import calculate_results
from utils import format_currency, load_data_from_json

# Configuração da página
st.set_page_config(
    page_title="Calculadora de Incentivos | PAP",
    page_icon="🧮",
    layout="wide"
)

def main():
    st.title("🧮 Calculadora de Incentivos PAP")
    
    # Verificar se os dados foram carregados
    if not st.session_state.get('dados'):
        st.warning("⚠️ É necessário consultar os dados do município primeiro.")
        st.info("👉 Vá para a página **Consulta Dados** e selecione seu município.")
        
        # Opção de carregar dados do arquivo local
        st.subheader("🔄 Ou carregue dados salvos")
        if st.button("Carregar dados do arquivo local (data.json)"):
            dados_locais = load_data_from_json()
            if dados_locais:
                st.session_state['dados'] = dados_locais
                st.success("✅ Dados carregados do arquivo local!")
                st.rerun()
            else:
                st.error("❌ Nenhum dado encontrado no arquivo local.")
        return
    
    # Exibir informações do município
    municipio = st.session_state.get('municipio_selecionado', 'Não informado')
    uf = st.session_state.get('uf_selecionada', 'Não informado')
    competencia = st.session_state.get('competencia', 'Não informado')
    
    st.info(f"📍 **Município**: {municipio} - {uf} | **Competência**: {competencia}")
    
    # Carregar configuração
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            config_data = json.load(f)
    except FileNotFoundError:
        st.error("❌ Arquivo config.json não encontrado.")
        return
    except json.JSONDecodeError:
        st.error("❌ Erro ao ler o arquivo config.json.")
        return
    
    # Verificar dados de pagamentos para obter IED
    dados_pagamentos = st.session_state['dados'].get("pagamentos", [])
    if dados_pagamentos:
        primeiro_pagamento = dados_pagamentos[0]
        ied = primeiro_pagamento.get('dsFaixaIndiceEquidadeEsfEap', '')
        st.session_state['ied'] = ied
        
        # Exibir métricas
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏥 IED", ied if ied else "N/A")
        with col2:
            st.metric("🔗 Vínculo", primeiro_pagamento.get('dsClassificacaoVinculoEsfEap', 'N/A'))
        with col3:
            st.metric("⭐ Qualidade", primeiro_pagamento.get('dsClassificacaoQualidadeEsfEap', 'N/A'))
        with col4:
            st.metric("👥 Equipes", primeiro_pagamento.get('qtEsfCredenciado', 0))
    else:
        st.warning("⚠️ Dados de pagamentos não encontrados.")
        return
    
    # Interface para seleção de serviços
    st.subheader("🏥 Seleção de Serviços")
    
    # Renderizar interface de serviços
    selected_services, edited_values, edited_implantacao_values, edited_implantacao_quantity = render_services_interface()
    
    # Parâmetros de qualidade e vínculo
    st.subheader("⚙️ Parâmetros de Cálculo")
    col_class, col_vinc = st.columns(2)
    
    with col_class:
        classificacao = st.selectbox(
            "Considerar Qualidade", 
            options=['Regular', 'Suficiente', 'Bom', 'Ótimo'], 
            index=2,
            help="Nível de qualidade para cálculo dos incentivos"
        )
    
    with col_vinc:
        vinculo = st.selectbox(
            "Vínculo e Acompanhamento Territorial", 
            options=['Regular', 'Suficiente', 'Bom', 'Ótimo'], 
            index=2,
            help="Nível de vínculo para cálculo dos incentivos"
        )
    
    # Parâmetros Adicionais
    st.subheader("📋 Parâmetros Adicionais")
    with st.expander("Valores Adicionais para o Cálculo", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            valor_esf_eap = st.number_input(
                "Incentivo Financeiro da APS eSF ou eAP", 
                value=st.session_state.get('valor_esf_eap', 0.0), 
                format="%.2f",
                help="Valor adicional para incentivo financeiro eSF ou eAP",
                key="input_esf_eap"
            )
            st.session_state['valor_esf_eap'] = valor_esf_eap
            
            valor_saude_bucal = st.number_input(
                "Incentivo Financeiro para Atenção à Saúde Bucal", 
                value=st.session_state.get('valor_saude_bucal', 0.0), 
                format="%.2f",
                help="Valor adicional para atenção à saúde bucal",
                key="input_saude_bucal"
            )
            st.session_state['valor_saude_bucal'] = valor_saude_bucal
        
        with col2:
            valor_acs = st.number_input(
                "Total ACS", 
                value=st.session_state.get('valor_acs', 0.0), 
                format="%.2f",
                help="Valor total para Agentes Comunitários de Saúde",
                key="input_acs"
            )
            st.session_state['valor_acs'] = valor_acs
            
            valor_estrategicas = st.number_input(
                "Ações Estratégicas", 
                value=st.session_state.get('valor_estrategicas', 0.0), 
                format="%.2f",
                help="Valor para ações estratégicas",
                key="input_estrategicas"
            )
            st.session_state['valor_estrategicas'] = valor_estrategicas
        
        # Calcular e exibir o total adicional
        total_adicional = valor_esf_eap + valor_saude_bucal + valor_acs + valor_estrategicas
        
        if total_adicional > 0:
            st.markdown("---")
            st.markdown(
                f"<div style='text-align: center; padding: 10px; background-color: #f0f2f6; border-radius: 5px;'>"
                f"<h4 style='color: #1f77b4; margin: 0;'>💰 Total Adicional: R$ {total_adicional:,.2f}</h4>"
                f"</div>", 
                unsafe_allow_html=True
            )
    
    # Botão de cálculo
    st.markdown("---")
    calcular_col1, calcular_col2, calcular_col3 = st.columns([1, 2, 1])
    with calcular_col2:
        calcular_button = st.button(
            "🧮 Calcular Incentivos PAP", 
            use_container_width=True,
            type="primary"
        )
    
    # Realizar cálculos
    if calcular_button:
        # Verificar se pelo menos um serviço foi selecionado
        if not any(selected_services.values()):
            st.error("❌ Por favor, selecione pelo menos um serviço para calcular.")
            return
        
        # Atualizar session_state com parâmetros
        st.session_state['selected_services'] = selected_services
        st.session_state['edited_values'] = edited_values
        st.session_state['edited_implantacao_values'] = edited_implantacao_values
        st.session_state['edited_implantacao_quantity'] = edited_implantacao_quantity
        st.session_state['classificacao'] = classificacao
        st.session_state['vinculo'] = vinculo
        st.session_state['calculo_realizado'] = True
        
        # Executar cálculos
        try:
            calculate_results(
                selected_services, 
                edited_values, 
                edited_implantacao_values, 
                edited_implantacao_quantity, 
                classificacao, 
                vinculo
            )
            
            st.success("✅ Cálculo realizado com sucesso!")
            st.info("💡 **Dica**: Vá para a página **Projeção Financeira** para ver análises detalhadas.")
            
        except Exception as e:
            st.error(f"❌ Erro durante o cálculo: {str(e)}")

if __name__ == "__main__":
    main()
