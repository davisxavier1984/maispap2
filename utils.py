"""
Módulo de compatibilidade com o código antigo.
Este arquivo agora apenas importa funcionalidades do pacote utils.
"""

# Importando funções do pacote utils
from utils import (
    # Funções de formatação
    currency_to_float, 
    format_currency,
    
    # Funções de interface
    metric_card,
    style_metric_cards,
    
    # Funções de dados
    get_estrato,
    load_data_from_json,
    consultar_api,
    DATA_FILE
)

# Este módulo não deve mais conter implementações.
# Todas as funções foram movidas para o pacote utils/
# Este arquivo é mantido apenas por compatibilidade com código existente.