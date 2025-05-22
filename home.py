"""
Página principal da Calculadora PAP.
"""
import streamlit as st
from interface import setup_interface
from utils import style_metric_cards

# Configuração da página
st.set_page_config(
    page_title="Calculadora PAP",
    page_icon="💰",
    layout="wide"
)

# Layout do cabeçalho
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image('logo_colorida_mg.png', width=200)

# Função para limpar o session_state
def clear_session_state():
    """Limpa todas as variáveis de estado e reseta a aplicação."""
    # Lista de chaves a serem resetadas para seus valores padrão
    keys_to_reset = {
        'dados': {},
        'valor_cenario_regular': 0.0,
        'valor_esf_eap': 0.0,
        'valor_saude_bucal': 0.0,
        'valor_acs': 0.0,
        'valor_estrategicas': 0.0,
        'calculo_realizado': False,
        'aumento_mensal': 0.0,
        'aumento_anual': 0.0,
        'municipio_selecionado': "Não informado",
        'uf_selecionada': "Não informado",
        'competencia': "202501",
        'selected_services': {},
        'edited_values': {},
        'edited_implantacao_values': {},
        'edited_implantacao_quantity': {},
        'classificacao': "Bom",
        'vinculo': "Bom",
        'ied': None,
        'populacao': 0
    }
    
    # Resetar cada chave para seu valor padrão
    for key, default_value in keys_to_reset.items():
        if key in st.session_state:
            st.session_state[key] = default_value
            
    # Recarregar a página para mostrar os valores resetados
    st.rerun()

st.title("Calculadora PAP")
style_metric_cards()

# Botão para limpar todos os dados
clear_button_col1, clear_button_col2, clear_button_col3 = st.columns([4, 2, 4])
with clear_button_col2:
    if st.button("🧹 Limpar Dados", use_container_width=True, help="Limpa todos os dados inseridos e resultados calculados"):
        clear_session_state()

# Inicializar variáveis de estado para armazenar dados entre páginas
if 'dados' not in st.session_state:
    st.session_state['dados'] = {}
if 'valor_cenario_regular' not in st.session_state:
    st.session_state['valor_cenario_regular'] = 0.0
if 'valor_esf_eap' not in st.session_state:
    st.session_state['valor_esf_eap'] = 0.0
if 'valor_saude_bucal' not in st.session_state:
    st.session_state['valor_saude_bucal'] = 0.0
if 'valor_acs' not in st.session_state:
    st.session_state['valor_acs'] = 0.0
if 'valor_estrategicas' not in st.session_state:
    st.session_state['valor_estrategicas'] = 0.0
if 'calculo_realizado' not in st.session_state:
    st.session_state['calculo_realizado'] = False
if 'aumento_mensal' not in st.session_state:
    st.session_state['aumento_mensal'] = 0.0
if 'aumento_anual' not in st.session_state:
    st.session_state['aumento_anual'] = 0.0
if 'municipio_selecionado' not in st.session_state:
    st.session_state['municipio_selecionado'] = "Não informado"
if 'uf_selecionada' not in st.session_state:
    st.session_state['uf_selecionada'] = "Não informado"
if 'competencia' not in st.session_state:
    st.session_state['competencia'] = "202501"
if 'selected_services' not in st.session_state:
    st.session_state['selected_services'] = {}
if 'edited_values' not in st.session_state:
    st.session_state['edited_values'] = {}
if 'edited_implantacao_values' not in st.session_state:
    st.session_state['edited_implantacao_values'] = {}
if 'edited_implantacao_quantity' not in st.session_state:
    st.session_state['edited_implantacao_quantity'] = {}
if 'classificacao' not in st.session_state:
    st.session_state['classificacao'] = "Bom"
if 'vinculo' not in st.session_state:
    st.session_state['vinculo'] = "Bom"

# Inicializa a interface principal da aplicação
setup_interface()

# Adicionar informação sobre páginas adicionais
if st.session_state['calculo_realizado']:
    st.success("Cálculo realizado com sucesso!")
