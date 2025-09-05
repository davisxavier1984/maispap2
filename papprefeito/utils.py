"""
Módulo de utilidades para o sistema papprefeito.
Combina as funcionalidades necessárias de formatação e API.
"""

# Importações de formatação
from formatting import (
    format_currency,
    parse_currency,
    currency_to_float,
    format_percentage,
    format_number,
    validate_numeric_input
)

# Importações de API
from api_client import (
    consultar_api,
    load_data_from_json,
    DATA_FILE
)

# Lista de funções exportadas
__all__ = [
    # Funções de formatação
    "format_currency",
    "parse_currency", 
    "currency_to_float",
    "format_percentage",
    "format_number",
    "validate_numeric_input",
    
    # Funções de API
    "consultar_api",
    "load_data_from_json",
    "DATA_FILE"
]