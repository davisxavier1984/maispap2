"""
Página principal da Calculadora PAP.
Versão refatorada com gerenciadores centralizados.
"""
import streamlit as st
from utils import style_metric_cards
from core.state_manager import StateManager, display_state_debug
from core.config_manager import get_config_manager, debug_config_info

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

# Função para limpar o session_state (refatorada)
def clear_session_state():
    """Limpa todas as variáveis de estado e reseta a aplicação usando StateManager."""
    StateManager.clear_state()
    st.success("🧹 Todos os dados foram limpos com sucesso!")
    st.rerun()

st.title("Calculadora PAP")
style_metric_cards()

# Botão para limpar todos os dados
clear_button_col1, clear_button_col2, clear_button_col3 = st.columns([4, 2, 4])
with clear_button_col2:
    if st.button("🧹 Limpar Dados", use_container_width=True, help="Limpa todos os dados inseridos e resultados calculados"):
        clear_session_state()

# Inicializar o estado da aplicação usando StateManager
state = StateManager.get_state()

# Garantir sincronização com session_state legado
StateManager._sync_to_legacy_session_state()

# Modo debug (ativar com query parameter ?debug=true)
query_params = st.query_params
if query_params.get('debug', 'false').lower() == 'true':
    StateManager.update_state(debug_mode=True)
    debug_config_info()
    display_state_debug()

# Inicializa a interface principal da aplicação
st.markdown("""
## 📊 Bem-vindo à Calculadora PAP

Esta aplicação permite calcular os valores do Programa de Apoio à Atenção Primária (PAP) 
conforme a **Portaria GM/MS Nº 3.493, de 10 de abril de 2024**.

### 🗂️ Como usar o sistema:

1. **📍 Consulta de Dados**: Selecione seu município e competência para obter dados atualizados
2. **🧮 Calculadora de Incentivos**: Configure serviços e parâmetros para calcular incentivos PAP
3. **📈 Projeção Financeira**: Visualize análises detalhadas e projeções de recursos

### 🎯 Navegação:
Use o menu lateral para navegar entre as diferentes funcionalidades do sistema.
""")
