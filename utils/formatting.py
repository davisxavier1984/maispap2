"""
Funções de formatação para valores monetários na Calculadora PAP.
"""
import streamlit as st

def currency_to_float(value):
    """
    Converte uma string de moeda brasileira (R$) para um número float.
    
    Args:
        value: Valor a converter, pode ser string ou número
        
    Returns:
        float: Valor numérico convertido
    """
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

def format_currency(value):
    """
    Formata um número como moeda brasileira (R$).
    
    Args:
        value: Número ou string a ser formatada
        
    Returns:
        str: Valor formatado como moeda brasileira
    """
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

def calcular_potencial_aumento(total_geral, valor_cenario_regular, valor_parametros_adicionais):
    """
    Calcula o potencial de aumento com base no valor total e no cenário regular.
    
    Args:
        total_geral (float): Valor total calculado pelo sistema
        valor_cenario_regular (float): Valor do cenário regular (pior desempenho)
        valor_parametros_adicionais (float): Soma dos valores de parâmetros adicionais
        
    Returns:
        float: Valor do potencial de aumento
    """
    # Calcula a diferença entre o total + parâmetros adicionais e o cenário regular
    aumento_mensal = valor_parametros_adicionais - valor_cenario_regular if valor_cenario_regular > 0 else 0
    
    # Retorna o potencial de aumento
    return aumento_mensal
