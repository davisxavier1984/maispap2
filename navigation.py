"""
Módulo para gerenciar a navegação entre páginas da Calculadora PAP.

NOTA: Este arquivo é considerado LEGADO e não é mais usado ativamente.
A funcionalidade foi migrada para o sistema de múltiplas páginas nativo do Streamlit,
utilizando a pasta /pages/ para as páginas adicionais.
"""
import streamlit as st
from components.financial_projection_page import display_financial_projection_page

def setup_navigation():
    """Configura a navegação entre páginas da aplicação."""
    # Inicializa a variável de estado 'page' se não existir
    if 'page' not in st.session_state:
        st.session_state['page'] = 'main'
    
    # Navegação para as diferentes páginas
    if st.session_state['page'] == 'main':
        # A página principal é gerenciada pelo arquivo interface.py
        pass
    elif st.session_state['page'] == 'projecao_detalhada':
        # Página de projeção financeira detalhada
        display_financial_projection_page()
