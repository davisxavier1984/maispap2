"""
Gerenciador centralizado de configurações da Calculadora PAP.
Este módulo implementa o padrão Singleton para garantir carregamento único do config.json.
"""
import json
import streamlit as st
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class ConfigData:
    """Estrutura de dados para as configurações."""
    data: Dict[str, Any] = field(default_factory=dict)
    quality_values: Dict[str, Dict[str, float]] = field(default_factory=dict)
    fixed_component_values: Dict[str, Dict[str, str]] = field(default_factory=dict)
    updated_categories: Dict[str, list] = field(default_factory=dict)
    subcategories: Dict[str, Any] = field(default_factory=dict)
    implantacao_values: Dict[str, str] = field(default_factory=dict)
    
    # Constantes de vínculo (integradas aqui para centralização)
    VINCULO_VALUES: Dict[str, Dict[str, int]] = field(default_factory=lambda: {
        'eSF': {'Ótimo': 8000, 'Bom': 6000, 'Suficiente': 4000, 'Regular': 2000},
        'eAP 30h': {'Ótimo': 4000, 'Bom': 3000, 'Suficiente': 2000, 'Regular': 1000},
        'eAP 20h': {'Ótimo': 3000, 'Bom': 2250, 'Suficiente': 1500, 'Regular': 750},
    })

class ConfigManager:
    """
    Gerenciador centralizado de configurações usando padrão Singleton.
    Garante que o config.json seja carregado apenas uma vez.
    """
    
    _instance: Optional['ConfigManager'] = None
    _config: Optional[ConfigData] = None
    _config_path: Path = Path("config.json")
    
    def __new__(cls) -> 'ConfigManager':
        """Implementa o padrão Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self) -> None:
        """Carrega as configurações do arquivo config.json."""
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                config_dict = json.load(f)
            
            # Validar estrutura básica
            required_keys = ["data", "quality_values", "fixed_component_values"]
            missing_keys = [key for key in required_keys if key not in config_dict]
            
            if missing_keys:
                st.error(f"❌ Chaves obrigatórias faltando em config.json: {missing_keys}")
                self._config = ConfigData()  # Configuração vazia como fallback
                return
            
            # Criar objeto ConfigData com validação
            self._config = ConfigData(
                data=config_dict.get("data", {}),
                quality_values=config_dict.get("quality_values", {}),
                fixed_component_values=config_dict.get("fixed_component_values", {}),
                updated_categories=config_dict.get("updated_categories", {}),
                subcategories=config_dict.get("subcategories", {}),
                implantacao_values=config_dict.get("implantacao_values", {})
            )
            
            # Log de sucesso (opcional, apenas em debug)
            if st.session_state.get('debug_mode', False):
                st.success(f"✅ Configurações carregadas com sucesso ({len(self._config.data)} serviços)")
                
        except FileNotFoundError:
            st.error(f"❌ Arquivo de configuração não encontrado: {self._config_path}")
            self._config = ConfigData()
        except json.JSONDecodeError as e:
            st.error(f"❌ Erro ao decodificar JSON: {e}")
            self._config = ConfigData()
        except Exception as e:
            st.error(f"❌ Erro inesperado ao carregar configurações: {e}")
            self._config = ConfigData()
    
    @property
    def config(self) -> ConfigData:
        """Retorna os dados de configuração."""
        if self._config is None:
            self._load_config()
        return self._config
    
    @property
    def data(self) -> Dict[str, Any]:
        """Retorna os dados de serviços."""
        return self.config.data
    
    @property
    def quality_values(self) -> Dict[str, Dict[str, float]]:
        """Retorna os valores de qualidade."""
        return self.config.quality_values
    
    @property
    def fixed_component_values(self) -> Dict[str, Dict[str, str]]:
        """Retorna os valores do componente fixo."""
        return self.config.fixed_component_values
    
    @property
    def updated_categories(self) -> Dict[str, list]:
        """Retorna as categorias atualizadas."""
        return self.config.updated_categories
    
    @property
    def subcategories(self) -> Dict[str, Any]:
        """Retorna as subcategorias."""
        return self.config.subcategories
    
    @property
    def implantacao_values(self) -> Dict[str, str]:
        """Retorna os valores de implantação."""
        return self.config.implantacao_values
    
    @property
    def vinculo_values(self) -> Dict[str, Dict[str, int]]:
        """Retorna os valores de vínculo e acompanhamento territorial."""
        return self.config.VINCULO_VALUES
    
    def get_service_info(self, service_name: str) -> Dict[str, Any]:
        """
        Retorna informações de um serviço específico.
        
        Args:
            service_name: Nome do serviço
            
        Returns:
            Dict: Informações do serviço ou dicionário vazio
        """
        return self.data.get(service_name, {})
    
    def get_quality_value(self, service: str, classification: str) -> float:
        """
        Retorna o valor de qualidade para um serviço e classificação.
        
        Args:
            service: Nome do serviço
            classification: Classificação da qualidade
            
        Returns:
            float: Valor de qualidade ou 0.0
        """
        service_quality = self.quality_values.get(service, {})
        return service_quality.get(classification, 0.0)
    
    def get_fixed_value(self, service: str, estrato: str) -> str:
        """
        Retorna o valor fixo para um serviço e estrato.
        
        Args:
            service: Nome do serviço
            estrato: Estrato do município
            
        Returns:
            str: Valor formatado como moeda ou "R$ 0,00"
        """
        estrato_values = self.fixed_component_values.get(estrato, {})
        return estrato_values.get(service, "R$ 0,00")
    
    def get_vinculo_value(self, service: str, vinculo_level: str) -> int:
        """
        Retorna o valor de vínculo para um serviço e nível.
        
        Args:
            service: Nome do serviço
            vinculo_level: Nível de vínculo
            
        Returns:
            int: Valor de vínculo ou 0
        """
        service_vinculo = self.vinculo_values.get(service, {})
        return service_vinculo.get(vinculo_level, 0)
    
    def get_implantacao_value(self, service: str) -> str:
        """
        Retorna o valor de implantação para um serviço.
        
        Args:
            service: Nome do serviço
            
        Returns:
            str: Valor formatado como moeda ou "R$ 0,00"
        """
        return self.implantacao_values.get(service, "R$ 0,00")
    
    def is_saude_bucal_service(self, service: str) -> bool:
        """
        Verifica se um serviço pertence à categoria Saúde Bucal.
        
        Args:
            service: Nome do serviço
            
        Returns:
            bool: True se for serviço de saúde bucal
        """
        saude_bucal_services = self.updated_categories.get('Saúde Bucal', [])
        return service in saude_bucal_services
    
    def reload_config(self) -> None:
        """
        Força o recarregamento das configurações.
        Útil para testes ou quando o arquivo config.json é atualizado.
        """
        self._config = None
        self._load_config()
        st.success("🔄 Configurações recarregadas com sucesso!")

# Função de conveniência para obter a instância
def get_config_manager() -> ConfigManager:
    """
    Retorna a instância singleton do ConfigManager.
    
    Returns:
        ConfigManager: Instância do gerenciador de configurações
    """
    return ConfigManager()

# Função para debug/inspeção das configurações
def debug_config_info() -> None:
    """Exibe informações de debug sobre as configurações carregadas."""
    if not st.session_state.get('debug_mode', False):
        return
    
    config = get_config_manager()
    
    with st.expander("🔧 Debug: Informações de Configuração"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Serviços", len(config.data))
            st.metric("Qualidade", len(config.quality_values))
        
        with col2:
            st.metric("Estratos", len(config.fixed_component_values))
            st.metric("Categorias", len(config.updated_categories))
        
        with col3:
            st.metric("Implantação", len(config.implantacao_values))
            st.metric("Subcategorias", len(config.subcategories))
        
        if st.button("🔄 Recarregar Config"):
            config.reload_config()
