"""
Arquivo principal da aplicação Calculadora PAP.

NOTA: Este arquivo é considerado LEGADO e não é mais usado ativamente.
A aplicação agora é iniciada através do arquivo Home.py, que utiliza
o sistema de múltiplas páginas nativo do Streamlit, com as páginas adicionais
localizadas na pasta /pages/.
"""
import streamlit as st
from interface import setup_interface
from utils import style_metric_cards
from navigation import setup_navigation

def main():
    """Função principal que inicia a aplicação."""
    st.set_page_config(page_title="Calculadora PAP")

    # Layout do cabeçalho
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.image('logo_colorida_mg.png', width=200)

    # Título e estilo apenas na página principal
    if st.session_state.get('page', 'main') == 'main':
        st.title("Calculadora PAP")
    
    style_metric_cards()

    # Configuração da navegação entre páginas
    setup_navigation()
    
    # Inicializa a interface principal da aplicação 
    # (só será executada se estivermos na página principal)
    if st.session_state.get('page', 'main') == 'main':
        setup_interface()

if __name__ == "__main__":
    main()
