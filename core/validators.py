"""
Sistema de validação de dados da Calculadora PAP.

Este módulo contém classes e funções para validação de dados de entrada.
"""

from typing import Dict, List, Tuple, Any
import streamlit as st
from .models import ServiceSelection, MunicipioData, ValidationResult


class DataValidator:
    """Validador de dados da aplicação."""
    
    # Limites razoáveis para validação
    MAX_SERVICE_QUANTITY = 1000
    MAX_SERVICE_VALUE = 1000000  # 1 milhão
    MIN_POPULATION = 1
    MAX_POPULATION = 20000000  # 20 milhões
    
    @staticmethod
    def validate_municipio_data(municipio_data: MunicipioData) -> ValidationResult:
        """Valida os dados do município."""
        result = ValidationResult(is_valid=True)
        
        if not municipio_data.uf:
            result.add_error("uf", "UF é obrigatória")
        
        if not municipio_data.municipio:
            result.add_error("municipio", "Município é obrigatório")
        
        if not municipio_data.competencia:
            result.add_error("competencia", "Competência é obrigatória")
        
        if municipio_data.ied is not None:
            if not isinstance(municipio_data.ied, (int, float, str)):
                result.add_error("ied", "IED deve ser um número ou string", municipio_data.ied)
        
        if municipio_data.populacao is not None:
            if municipio_data.populacao < DataValidator.MIN_POPULATION:
                result.add_error("populacao", f"População deve ser maior que {DataValidator.MIN_POPULATION}", municipio_data.populacao)
            elif municipio_data.populacao > DataValidator.MAX_POPULATION:
                result.add_error("populacao", f"População deve ser menor que {DataValidator.MAX_POPULATION:,}", municipio_data.populacao)
        
        return result
    
    @staticmethod
    def validate_service_selection(service_selection: ServiceSelection) -> ValidationResult:
        """Valida a seleção de serviços."""
        result = ValidationResult(is_valid=True)
        
        if not service_selection.services:
            result.add_error("services", "Nenhum serviço selecionado")
            return result
        
        if not service_selection.has_services():
            result.add_error("services", "Selecione pelo menos um serviço com quantidade maior que zero")
        
        # Validar quantidades de serviços
        for service, quantity in service_selection.services.items():
            if quantity < 0:
                result.add_error("services", f"Quantidade inválida para {service}: {quantity}", quantity)
            elif quantity > DataValidator.MAX_SERVICE_QUANTITY:
                result.add_error("services", f"Quantidade muito alta para {service}: {quantity}", quantity)
        
        # Validar valores editados
        for service, value in service_selection.edited_values.items():
            if value < 0:
                result.add_error("edited_values", f"Valor inválido para {service}: R$ {value:,.2f}", value)
            elif value > DataValidator.MAX_SERVICE_VALUE:
                result.add_error("edited_values", f"Valor muito alto para {service}: R$ {value:,.2f}", value)
        
        # Validar valores de implantação
        for service, value in service_selection.edited_implantacao_values.items():
            if value < 0:
                result.add_error("implantacao_values", f"Valor de implantação inválido para {service}: R$ {value:,.2f}", value)
            elif value > DataValidator.MAX_SERVICE_VALUE:
                result.add_error("implantacao_values", f"Valor de implantação muito alto para {service}: R$ {value:,.2f}", value)
        
        # Validar quantidades de implantação
        for service, quantity in service_selection.edited_implantacao_quantity.items():
            if quantity < 0:
                result.add_error("implantacao_quantity", f"Quantidade de implantação inválida para {service}: {quantity}", quantity)
            elif quantity > DataValidator.MAX_SERVICE_QUANTITY:
                result.add_error("implantacao_quantity", f"Quantidade de implantação muito alta para {service}: {quantity}", quantity)
        
        return result
    
    @staticmethod
    def validate_calculation_inputs(classificacao: str, vinculo: str) -> ValidationResult:
        """Valida os parâmetros de entrada para cálculos."""
        result = ValidationResult(is_valid=True)
        
        valid_classifications = ['Regular', 'Suficiente', 'Bom', 'Ótimo']
        
        if classificacao not in valid_classifications:
            result.add_error("classificacao", f"Classificação inválida: {classificacao}. Deve ser uma de: {valid_classifications}", classificacao)
        
        if vinculo not in valid_classifications:
            result.add_error("vinculo", f"Vínculo inválido: {vinculo}. Deve ser uma de: {valid_classifications}", vinculo)
        
        return result
    
    @staticmethod
    def validate_additional_values(additional_values: Dict[str, float]) -> ValidationResult:
        """Valida valores adicionais (parâmetros extras)."""
        result = ValidationResult(is_valid=True)
        
        for param_name, value in additional_values.items():
            if not isinstance(value, (int, float)):
                result.add_error("additional_values", f"Valor inválido para {param_name}: deve ser numérico", value)
            elif value < 0:
                result.add_error("additional_values", f"Valor negativo para {param_name}: {value}", value)
            elif value > DataValidator.MAX_SERVICE_VALUE:
                result.add_error("additional_values", f"Valor muito alto para {param_name}: R$ {value:,.2f}", value)
        
        return result
    
    @staticmethod
    def display_validation_errors(errors: List, error_type: str = "Erros de Validação"):
        """Exibe erros de validação na interface do Streamlit."""
        if errors:
            with st.expander(f"⚠️ {error_type}", expanded=True):
                for error in errors:
                    if hasattr(error, 'message'):
                        st.error(f"**{error.field}**: {error.message}")
                    else:
                        st.error(str(error))
    
    @staticmethod
    def validate_all_inputs(municipio_data: MunicipioData, 
                          service_selection: ServiceSelection,
                          classificacao: str,
                          vinculo: str,
                          additional_values: Dict[str, float] = None) -> ValidationResult:
        """Valida todas as entradas de uma vez."""
        result = ValidationResult(is_valid=True)
        
        # Validar dados do município
        municipio_result = DataValidator.validate_municipio_data(municipio_data)
        if municipio_result.has_errors():
            result.errors.extend(municipio_result.errors)
            result.is_valid = False
        
        # Validar seleção de serviços
        service_result = DataValidator.validate_service_selection(service_selection)
        if service_result.has_errors():
            result.errors.extend(service_result.errors)
            result.is_valid = False
        
        # Validar parâmetros de cálculo
        calc_result = DataValidator.validate_calculation_inputs(classificacao, vinculo)
        if calc_result.has_errors():
            result.errors.extend(calc_result.errors)
            result.is_valid = False
        
        # Validar valores adicionais se fornecidos
        if additional_values:
            additional_result = DataValidator.validate_additional_values(additional_values)
            if additional_result.has_errors():
                result.errors.extend(additional_result.errors)
                result.is_valid = False
        
        return result


class BusinessRuleValidator:
    """Validador de regras de negócio específicas do PAP."""
    
    @staticmethod
    def validate_service_combinations(service_selection: ServiceSelection) -> ValidationResult:
        """Valida combinações específicas de serviços."""
        result = ValidationResult(is_valid=True)
        
        # Exemplo: Verificar se há eSF sem eAP (regra hipotética)
        esf_count = service_selection.services.get('eSF', 0)
        eap_30h_count = service_selection.services.get('eAP 30h', 0)
        eap_20h_count = service_selection.services.get('eAP 20h', 0)
        
        total_eap = eap_30h_count + eap_20h_count
        
        # Regra: Se há eSF, deve haver pelo menos uma eAP
        if esf_count > 0 and total_eap == 0:
            result.add_error("business_rule", "Se há Equipes de Saúde da Família (eSF), deve haver pelo menos uma Equipe de Atenção Primária (eAP)")
        
        # Regra: Não pode haver mais eAP que eSF
        if total_eap > esf_count and esf_count > 0:
            result.add_error("business_rule", f"Número de eAP ({total_eap}) não pode ser maior que eSF ({esf_count})")
        
        return result
    
    @staticmethod
    def validate_population_service_ratio(municipio_data: MunicipioData, service_selection: ServiceSelection) -> ValidationResult:
        """Valida a proporção de serviços em relação à população."""
        result = ValidationResult(is_valid=True)
        
        if not municipio_data.populacao:
            return result
        
        population = municipio_data.populacao
        esf_count = service_selection.services.get('eSF', 0)
        
        # Regra: Uma eSF deve atender entre 2.000 e 3.500 pessoas
        if esf_count > 0:
            pessoas_por_esf = population / esf_count
            
            if pessoas_por_esf < 2000:
                result.add_error("population_ratio", f"Muitas eSF para a população. Cada eSF atende {pessoas_por_esf:.0f} pessoas (mínimo recomendado: 2.000)")
            elif pessoas_por_esf > 3500:
                result.add_error("population_ratio", f"Poucas eSF para a população. Cada eSF atende {pessoas_por_esf:.0f} pessoas (máximo recomendado: 3.500)")
        
        return result
