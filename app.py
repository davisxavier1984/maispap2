"""
Arquivo principal da aplicação Calculadora PAP.
"""
import streamlit as st
from interface import setup_interface
from utils import style_metric_cards

def main():
    """Função principal que inicia a aplicação."""
    st.set_page_config(page_title="Calculadora PAP")

    # Layout do cabeçalho
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        st.image('logo_colorida_mg.png', width=200)

    st.title("Calculadora PAP")
    style_metric_cards()

    # Inicializa a interface principal da aplicação
    setup_interface()

if __name__ == "__main__":
    main()
