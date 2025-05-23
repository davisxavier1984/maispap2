"""
Testes unitários para a Calculadora PAP.

Este módulo contém testes para as classes principais do sistema.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Adicionar o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.models import MunicipioData, ServiceSelection, CalculationResults, ConfigManager
from core.calculations import PAPCalculator
from core.validators import DataValidator, BusinessRuleValidator


class TestMunicipioData(unittest.TestCase):
    """Testes para a classe MunicipioData."""
    
    def test_municipio_data_creation(self):
        """Testa a criação de dados do município."""
        municipio = MunicipioData(
            uf="MG",
            municipio="Belo Horizonte",
            competencia="2024-01",
            ied=0.5,
            populacao=2500000
        )
        
        self.assertEqual(municipio.uf, "MG")
        self.assertEqual(municipio.municipio, "Belo Horizonte")
        self.assertEqual(municipio.ied, 0.5)
        self.assertEqual(municipio.populacao, 2500000)
    
    def test_ied_validation(self):
        """Testa validação do IED."""
        with self.assertRaises(ValueError):
            MunicipioData(
                uf="MG",
                municipio="Test",
                competencia="2024-01",
                ied=1.5  # IED inválido > 1
            )
        
        with self.assertRaises(ValueError):
            MunicipioData(
                uf="MG",
                municipio="Test",
                competencia="2024-01",
                ied=-0.1  # IED inválido < 0
            )


class TestServiceSelection(unittest.TestCase):
    """Testes para a classe ServiceSelection."""
    
    def test_service_selection_creation(self):
        """Testa criação da seleção de serviços."""
        selection = ServiceSelection(
            services={'eSF': 5, 'eAP 30h': 2},
            edited_values={'eSF': 18000.0}
        )
        
        self.assertEqual(selection.services['eSF'], 5)
        self.assertEqual(selection.edited_values['eSF'], 18000.0)
    
    def test_total_services(self):
        """Testa cálculo do total de serviços."""
        selection = ServiceSelection(
            services={'eSF': 5, 'eAP 30h': 2, 'eMULTI Ampl.': 1}
        )
        
        self.assertEqual(selection.get_total_services(), 8)
        self.assertTrue(selection.has_services())
    
    def test_empty_services(self):
        """Testa seleção vazia."""
        selection = ServiceSelection()
        
        self.assertEqual(selection.get_total_services(), 0)
        self.assertFalse(selection.has_services())


class TestCalculationResults(unittest.TestCase):
    """Testes para a classe CalculationResults."""
    
    def test_total_geral_calculation(self):
        """Testa cálculo do total geral."""
        results = CalculationResults(
            total_fixed_value=10000.0,
            total_quality_value=5000.0,
            total_vinculo_value=3000.0,
            total_implantacao_value=2000.0,
            total_saude_bucal_value=1500.0,
            total_per_capita=500.0
        )
        
        total = results.calculate_total_geral()
        expected_total = 10000.0 + 5000.0 + 3000.0 + 2000.0 + 1500.0 + 500.0
        
        self.assertEqual(total, expected_total)
        self.assertEqual(results.total_geral, expected_total)


class TestPAPCalculator(unittest.TestCase):
    """Testes para a classe PAPCalculator."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.calculator = PAPCalculator()
        self.sample_selection = ServiceSelection(
            services={'eSF': 5, 'eAP 30h': 2},
            edited_values={},
            edited_implantacao_values={},
            edited_implantacao_quantity={}
        )
    
    @patch('core.models.ConfigManager')
    def test_calculate_per_capita_component(self, mock_config):
        """Testa cálculo do componente per capita."""
        populacao = 10000
        result = self.calculator.calculate_per_capita_component(populacao)
        
        expected = (5.95 * populacao) / 12
        self.assertEqual(result, expected)
    
    def test_get_estrato_valid(self):
        """Testa extração de estrato válido."""
        ied = "ESTRATO 3"
        estrato = self.calculator._get_estrato(ied)
        self.assertEqual(estrato, "3")
    
    def test_get_estrato_invalid(self):
        """Testa extração de estrato inválido."""
        with self.assertRaises(ValueError):
            self.calculator._get_estrato("INVALID")
        
        with self.assertRaises(ValueError):
            self.calculator._get_estrato(None)
    
    def test_parse_currency_string(self):
        """Testa conversão de string de moeda."""
        test_cases = [
            ("R$ 1.500,00", 1500.0),
            ("R$ 10.000,50", 10000.5),
            ("R$ 0,00", 0.0),
            ("1500", 1500.0)
        ]
        
        for input_str, expected in test_cases:
            result = self.calculator._parse_currency_string(input_str)
            self.assertEqual(result, expected)


class TestDataValidator(unittest.TestCase):
    """Testes para a classe DataValidator."""
    
    def test_validate_municipio_data_valid(self):
        """Testa validação de dados válidos do município."""
        municipio = MunicipioData(
            uf="MG",
            municipio="Belo Horizonte",
            competencia="2024-01",
            ied=0.5,
            populacao=2500000
        )
        
        result = DataValidator.validate_municipio_data(municipio)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_validate_municipio_data_invalid(self):
        """Testa validação de dados inválidos do município."""
        municipio = MunicipioData(
            uf="",  # UF vazia
            municipio="",  # Município vazio
            competencia="2024-01",
            populacao=-1000  # População negativa
        )
        
        result = DataValidator.validate_municipio_data(municipio)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_validate_service_selection_valid(self):
        """Testa validação de seleção válida de serviços."""
        selection = ServiceSelection(
            services={'eSF': 5, 'eAP 30h': 2},
            edited_values={'eSF': 18000.0}
        )
        
        result = DataValidator.validate_service_selection(selection)
        self.assertTrue(result.is_valid)
    
    def test_validate_service_selection_invalid(self):
        """Testa validação de seleção inválida de serviços."""
        selection = ServiceSelection(
            services={'eSF': -1},  # Quantidade negativa
            edited_values={'eAP 30h': -5000.0}  # Valor negativo
        )
        
        result = DataValidator.validate_service_selection(selection)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_validate_calculation_inputs(self):
        """Testa validação de parâmetros de cálculo."""
        # Teste válido
        result = DataValidator.validate_calculation_inputs("Bom", "Ótimo")
        self.assertTrue(result.is_valid)
        
        # Teste inválido
        result = DataValidator.validate_calculation_inputs("Inválido", "Ótimo")
        self.assertFalse(result.is_valid)


class TestBusinessRuleValidator(unittest.TestCase):
    """Testes para validação de regras de negócio."""
    
    def test_validate_service_combinations_valid(self):
        """Testa combinação válida de serviços."""
        selection = ServiceSelection(
            services={'eSF': 5, 'eAP 30h': 3}
        )
        
        result = BusinessRuleValidator.validate_service_combinations(selection)
        self.assertTrue(result.is_valid)
    
    def test_validate_service_combinations_invalid(self):
        """Testa combinação inválida de serviços."""
        selection = ServiceSelection(
            services={'eSF': 2, 'eAP 30h': 5}  # Mais eAP que eSF
        )
        
        result = BusinessRuleValidator.validate_service_combinations(selection)
        self.assertFalse(result.is_valid)
    
    def test_validate_population_service_ratio(self):
        """Testa proporção população/serviços."""
        municipio = MunicipioData(
            uf="MG",
            municipio="Test",
            competencia="2024-01",
            populacao=10000
        )
        
        selection = ServiceSelection(
            services={'eSF': 3}  # 10000/3 = ~3333 pessoas por eSF (válido)
        )
        
        result = BusinessRuleValidator.validate_population_service_ratio(municipio, selection)
        self.assertTrue(result.is_valid)
        
        # Teste com muitas eSF
        selection = ServiceSelection(
            services={'eSF': 10}  # 10000/10 = 1000 pessoas por eSF (inválido)
        )
        
        result = BusinessRuleValidator.validate_population_service_ratio(municipio, selection)
        self.assertFalse(result.is_valid)


if __name__ == '__main__':
    # Executar todos os testes
    unittest.main(verbosity=2)
