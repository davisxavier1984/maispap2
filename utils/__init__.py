"""
Pacote de utilidades para a Calculadora PAP.
Este módulo contém funções utilitárias usadas em vários lugares do aplicativo.
"""

# Importações de funções de formatação
from utils.formatting import currency_to_float, format_currency

# Importações de funções de interface
from utils.interface import metric_card, style_metric_cards

# Importações de funções de dados
from utils.data import get_estrato, load_data_from_json, consultar_api, DATA_FILE

# Lista de funções e constantes exportadas
__all__ = [
    # Funções de formatação
    "currency_to_float", 
    "format_currency", 
    
    # Funções de interface
    "metric_card",
    "style_metric_cards",
    
    # Funções de dados
    "get_estrato",
    "load_data_from_json",
    "consultar_api",
    "DATA_FILE"
]
