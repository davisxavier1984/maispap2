"""
Utilitários para formatação de valores na Calculadora PAP.
"""
import streamlit as st

def currency_to_float(value: str) -> float:
    """Converte uma string de moeda brasileira (R$) para um número float."""
    if value == 'Sem cálculo' or not value:
        return 0.0
        
    if isinstance(value, str):
        try:
            # Remove "R$" e espaços, e substitui vírgulas por pontos
            cleaned_value = value.replace('R$', '').strip().replace('.', '').replace(',', '.')
            return float(cleaned_value)
        except ValueError:
            st.warning(f"Valor inválido para conversão: {value}")
            return 0.0
    
    # Se já for um número, retorna diretamente
    return float(value)

def format_currency(value: float | str) -> str:
    """Formata um número como moeda brasileira (R$)."""
    if value == 'Sem cálculo':
        return value

    # Converte a string para float, se necessário
    if isinstance(value, str):
        try:
            value = currency_to_float(value)
        except ValueError:
            return "Valor inválido"

    # Formata o valor como moeda, usando f-string
    return f"R$ {value:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")
