"""
Modelos de dados da Calculadora PAP.

Este módulo contém as classes de dados e estruturas utilizadas pelo sistema.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
import json
from pathlib import Path


@dataclass
class MunicipioData:
    """Dados do município selecionado."""
    uf: str
    municipio: str
    competencia: str
    ied: Optional[float] = None
    total_geral: Optional[float] = None
    populacao: Optional[int] = None
    
    def __post_init__(self):
        """Validações após inicialização."""
        if self.ied is not None and (self.ied < 0 or self.ied > 1):
            raise ValueError(f"IED deve estar entre 0 e 1, recebido: {self.ied}")


@dataclass
class ServiceSelection:
    """Seleção de serviços e quantidades."""
    services: Dict[str, int] = field(default_factory=dict)
    edited_values: Dict[str, float] = field(default_factory=dict)
    edited_implantacao_values: Dict[str, float] = field(default_factory=dict)
    edited_implantacao_quantity: Dict[str, int] = field(default_factory=dict)
    
    def get_total_services(self) -> int:
        """Retorna o total de serviços selecionados."""
        return sum(self.services.values())
    
    def has_services(self) -> bool:
        """Verifica se há pelo menos um serviço selecionado."""
        return self.get_total_services() > 0


@dataclass
class CalculationResults:
    """Resultados dos cálculos do PAP."""
    total_fixed_value: float = 0.0
    total_vinculo_value: float = 0.0
    total_quality_value: float = 0.0
    total_core_implantacao_value: float = 0.0 # NOVO: Implantação de eSF, eAP, eMulti
    total_outros_programas_value: float = 0.0 # RENOMEADO: Antigo total_implantacao_value
    total_saude_bucal_value: float = 0.0
    total_per_capita: float = 0.0
    total_geral: float = 0.0
    
    # Tabelas detalhadas
    fixed_table: List[List] = field(default_factory=list)
    quality_table: List[List] = field(default_factory=list)
    vinculo_table: List[List] = field(default_factory=list)
    core_implantacao_table: List[List] = field(default_factory=list) # NOVO: Tabela para implantação de eSF, eAP, eMulti
    outros_programas_table: List[List] = field(default_factory=list) # RENOMEADO: Antigo implantacao_table
    # Adicionar as tabelas que faltavam
    saude_bucal_table: List[List] = field(default_factory=list)
    per_capita_table: List[List] = field(default_factory=list)
    
    # Subtotais para resumo
    total_incentivo_aps_esf_eap: float = 0.0
    total_incentivo_aps_emulti: float = 0.0
    
    def calculate_total_geral(self) -> float:
        """Calcula o total geral automaticamente."""
        self.total_geral = (
            self.total_fixed_value + 
            self.total_quality_value + 
            self.total_vinculo_value + 
            self.total_core_implantacao_value + # ATUALIZADO
            self.total_outros_programas_value + # ATUALIZADO
            self.total_saude_bucal_value + 
            self.total_per_capita
        )
        return self.total_geral


class ConfigManager:
    """Gerenciador de configurações do sistema."""
    
    _instance = None
    _config = None
    
    VINCULO_VALUES = {
        'eSF': {'Ótimo': 8000, 'Bom': 6000, 'Suficiente': 4000, 'Regular': 2000},
        'eAP 30h': {'Ótimo': 4000, 'Bom': 3000, 'Suficiente': 2000, 'Regular': 1000},
        'eAP 20h': {'Ótimo': 3000, 'Bom': 2250, 'Suficiente': 1500, 'Regular': 750},
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._load_config()
        return cls._instance
    
    @classmethod
    def _load_config(cls):
        """Carrega as configurações do arquivo config.json."""
        config_path = Path(__file__).parent.parent / "config.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cls._config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Erro ao decodificar JSON: {e}")
    
    @property
    def data(self) -> Dict:
        """Retorna os dados de serviços."""
        return self._config.get("data", {})
    
    @property
    def quality_values(self) -> Dict:
        """Retorna os valores de qualidade."""
        return self._config.get("quality_values", {})
    
    @property
    def fixed_component_values(self) -> Dict:
        """Retorna os valores do componente fixo."""
        return self._config.get("fixed_component_values", {})
    
    @property
    def updated_categories(self) -> Dict:
        """Retorna as categorias atualizadas."""
        return self._config.get("updated_categories", {})
    
    @property
    def subcategories(self) -> Dict:
        """Retorna as subcategorias."""
        return self._config.get("subcategories", {})
    
    @property
    def implantacao_values(self) -> Dict:
        """Retorna os valores de implantação."""
        return self._config.get("implantacao_values", {})
    
    def get_service_info(self, service_name: str) -> Dict:
        """Retorna informações de um serviço específico."""
        return self.data.get(service_name, {})
    
    def get_quality_value(self, service: str, classification: str) -> float:
        """Retorna o valor de qualidade para um serviço e classificação."""
        service_quality = self.quality_values.get(service, {})
        return service_quality.get(classification, 0.0)
    
    def get_fixed_value(self, service: str, estrato: str) -> str:
        """Retorna o valor fixo para um serviço e estrato."""
        estrato_values = self.fixed_component_values.get(estrato, {})
        return estrato_values.get(service, "R$ 0,00")
    
    def get_vinculo_values(self) -> Dict:
        """Retorna os valores de vínculo e acompanhamento territorial."""
        return self.VINCULO_VALUES


@dataclass
class ValidationError:
    """Representa um erro de validação."""
    field: str
    message: str
    value: Optional[any] = None


@dataclass
class ValidationResult:
    """Resultado de uma validação."""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    
    def add_error(self, field: str, message: str, value=None):
        """Adiciona um erro de validação."""
        self.errors.append(ValidationError(field, message, value))
        self.is_valid = False
    
    def has_errors(self) -> bool:
        """Verifica se há erros."""
        return len(self.errors) > 0
