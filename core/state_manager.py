"""
Gerenciador centralizado de estado da aplicação Calculadora PAP.
Este módulo gerencia o session_state de forma organizada e tipo-segura.
"""
import streamlit as st
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class AppState:
    """Estado centralizado da aplicação."""
    # Dados do município
    municipio_selecionado: str = "Não informado"
    uf_selecionada: str = "Não informado"
    competencia: str = "202501"
    populacao: int = 0
    
    # Dados da API
    dados: Dict[str, Any] = field(default_factory=dict)
    ied: Optional[str] = None
    
    # Parâmetros de cálculo
    classificacao: str = "Bom"
    vinculo: str = "Bom"
    
    # Seleções de serviços
    selected_services: Dict[str, int] = field(default_factory=dict)
    edited_values: Dict[str, float] = field(default_factory=dict)
    edited_implantacao_values: Dict[str, float] = field(default_factory=dict)
    edited_implantacao_quantity: Dict[str, int] = field(default_factory=dict)
    
    # Resultados de cálculos
    calculo_realizado: bool = False
    valor_cenario_regular: float = 0.0
    valor_esf_eap: float = 0.0
    valor_saude_bucal: float = 0.0
    valor_acs: float = 0.0
    valor_estrategicas: float = 0.0
    aumento_mensal: float = 0.0
    aumento_anual: float = 0.0
    
    # Metadados
    ultima_atualizacao: Optional[str] = None
    debug_mode: bool = False

class StateManager:
    """Gerenciador centralizado do estado da aplicação."""
    
    STATE_KEY = 'app_state'
    
    @classmethod
    def get_state(cls) -> AppState:
        """
        Retorna o estado atual da aplicação.
        
        Returns:
            AppState: Estado atual ou estado padrão se não existir
        """
        if cls.STATE_KEY not in st.session_state:
            cls._initialize_state()
        
        return st.session_state[cls.STATE_KEY]
    
    @classmethod
    def _initialize_state(cls) -> None:
        """Inicializa o estado com valores padrão."""
        st.session_state[cls.STATE_KEY] = AppState()
        cls._migrate_legacy_state()
        cls._ensure_legacy_keys()
    
    @classmethod
    def _ensure_legacy_keys(cls) -> None:
        """
        Garante que todas as chaves legadas estejam inicializadas no session_state.
        Previne erros de KeyError em módulos que acessam diretamente o session_state.
        """
        state = cls.get_state()
        
        # Chaves essenciais que devem sempre existir no session_state
        essential_keys = {
            'municipio_selecionado': state.municipio_selecionado,
            'uf_selecionada': state.uf_selecionada,
            'competencia': state.competencia,
            'populacao': state.populacao,
            'dados': state.dados,
            'ied': state.ied,
            'classificacao': state.classificacao,
            'vinculo': state.vinculo,
            'selected_services': state.selected_services,
            'edited_values': state.edited_values,
            'edited_implantacao_values': state.edited_implantacao_values,
            'edited_implantacao_quantity': state.edited_implantacao_quantity,
            'calculo_realizado': state.calculo_realizado,
            'valor_cenario_regular': state.valor_cenario_regular,
            'valor_esf_eap': state.valor_esf_eap,
            'valor_saude_bucal': state.valor_saude_bucal,
            'valor_acs': state.valor_acs,
            'valor_estrategicas': state.valor_estrategicas,
            'aumento_mensal': state.aumento_mensal,
            'aumento_anual': state.aumento_anual,
            'debug_mode': state.debug_mode
        }
        
        # Garantir que todas as chaves existam no session_state
        for key, default_value in essential_keys.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    @classmethod
    def _migrate_legacy_state(cls) -> None:
        """
        Migra valores do session_state legado para o novo formato.
        Mantém compatibilidade com código existente.
        """
        state = st.session_state[cls.STATE_KEY]
        
        # Mapeamento de chaves legadas para o novo estado
        legacy_mappings = {
            'municipio_selecionado': 'municipio_selecionado',
            'uf_selecionada': 'uf_selecionada',
            'competencia': 'competencia',
            'populacao': 'populacao',
            'dados': 'dados',
            'ied': 'ied',
            'classificacao': 'classificacao',
            'vinculo': 'vinculo',
            'selected_services': 'selected_services',
            'edited_values': 'edited_values',
            'edited_implantacao_values': 'edited_implantacao_values',
            'edited_implantacao_quantity': 'edited_implantacao_quantity',
            'calculo_realizado': 'calculo_realizado',
            'valor_cenario_regular': 'valor_cenario_regular',
            'valor_esf_eap': 'valor_esf_eap',
            'valor_saude_bucal': 'valor_saude_bucal',
            'valor_acs': 'valor_acs',
            'valor_estrategicas': 'valor_estrategicas',
            'aumento_mensal': 'aumento_mensal',
            'aumento_anual': 'aumento_anual',
            'debug_mode': 'debug_mode'
        }
        
        # Migrar valores existentes
        migrated_count = 0
        for legacy_key, state_attr in legacy_mappings.items():
            if legacy_key in st.session_state:
                setattr(state, state_attr, st.session_state[legacy_key])
                migrated_count += 1
        
        # Log da migração se em modo debug
        if migrated_count > 0 and state.debug_mode:
            st.info(f"🔄 Migrados {migrated_count} valores do estado legado")
    
    @classmethod
    def update_state(cls, **kwargs) -> None:
        """
        Atualiza o estado com novos valores.
        
        Args:
            **kwargs: Pares chave-valor para atualizar o estado
        """
        state = cls.get_state()
        
        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)
            else:
                if state.debug_mode:
                    st.warning(f"⚠️ Tentativa de atualizar chave inexistente: {key}")
        
        # Atualizar timestamp
        state.ultima_atualizacao = datetime.now().isoformat()
        
        # Sincronizar com session_state legado para compatibilidade
        cls._sync_to_legacy_session_state()
    
    @classmethod
    def _sync_to_legacy_session_state(cls) -> None:
        """Sincroniza o estado novo com as chaves legadas do session_state."""
        state = cls.get_state()
        
        # Sincronizar apenas valores alterados
        legacy_sync = {
            'municipio_selecionado': state.municipio_selecionado,
            'uf_selecionada': state.uf_selecionada,
            'competencia': state.competencia,
            'populacao': state.populacao,
            'dados': state.dados,
            'ied': state.ied,
            'classificacao': state.classificacao,
            'vinculo': state.vinculo,
            'selected_services': state.selected_services,
            'edited_values': state.edited_values,
            'edited_implantacao_values': state.edited_implantacao_values,
            'edited_implantacao_quantity': state.edited_implantacao_quantity,
            'calculo_realizado': state.calculo_realizado,
            'valor_cenario_regular': state.valor_cenario_regular,
            'valor_esf_eap': state.valor_esf_eap,
            'valor_saude_bucal': state.valor_saude_bucal,
            'valor_acs': state.valor_acs,
            'valor_estrategicas': state.valor_estrategicas,
            'aumento_mensal': state.aumento_mensal,
            'aumento_anual': state.aumento_anual,
            'debug_mode': state.debug_mode
        }
        
        for key, value in legacy_sync.items():
            st.session_state[key] = value
    
    @classmethod
    def clear_state(cls) -> None:
        """Limpa todo o estado da aplicação."""
        # Limpar estado novo
        if cls.STATE_KEY in st.session_state:
            del st.session_state[cls.STATE_KEY]
        
        # Limpar chaves legadas importantes
        legacy_keys = [
            'dados', 'valor_cenario_regular', 'valor_esf_eap', 'valor_saude_bucal',
            'valor_acs', 'valor_estrategicas', 'calculo_realizado', 'aumento_mensal',
            'aumento_anual', 'municipio_selecionado', 'uf_selecionada', 'competencia',
            'selected_services', 'edited_values', 'edited_implantacao_values',
            'edited_implantacao_quantity', 'classificacao', 'vinculo', 'ied', 'populacao'
        ]
        
        for key in legacy_keys:
            if key in st.session_state:
                del st.session_state[key]
        
        # Reinicializar estado limpo
        cls._initialize_state()
    
    @classmethod
    def get_municipio_info(cls) -> Dict[str, str]:
        """
        Retorna informações básicas do município selecionado.
        
        Returns:
            Dict: Informações do município
        """
        state = cls.get_state()
        return {
            'municipio': state.municipio_selecionado,
            'uf': state.uf_selecionada,
            'competencia': state.competencia,
            'ied': state.ied or "N/A"
        }
    
    @classmethod
    def has_dados(cls) -> bool:
        """
        Verifica se há dados carregados.
        
        Returns:
            bool: True se há dados carregados
        """
        state = cls.get_state()
        return bool(state.dados)
    
    @classmethod
    def has_calculo_realizado(cls) -> bool:
        """
        Verifica se algum cálculo foi realizado.
        
        Returns:
            bool: True se cálculo foi realizado
        """
        state = cls.get_state()
        return state.calculo_realizado
    
    @classmethod
    def get_total_services_selected(cls) -> int:
        """
        Retorna o total de serviços selecionados.
        
        Returns:
            int: Número total de serviços selecionados
        """
        state = cls.get_state()
        return sum(state.selected_services.values())
    
    @classmethod
    def get_municipio_data(cls) -> Optional['MunicipioData']:
        """
        Retorna os dados do município como MunicipioData.
        
        Returns:
            MunicipioData: Dados do município ou None se não definido
        """
        from .models import MunicipioData
        state = cls.get_state()
        
        if not (state.municipio_selecionado and state.uf_selecionada):
            return None
        
        return MunicipioData(
            uf=state.uf_selecionada,
            municipio=state.municipio_selecionado,
            competencia=state.competencia or "",
            ied=state.ied,
            populacao=state.populacao
        )
    
    @classmethod
    def set_dados_municipio(cls, dados: Dict[str, Any], municipio: str, uf: str, competencia: str) -> None:
        """
        Define os dados do município de forma organizada.
        
        Args:
            dados: Dados da API
            municipio: Nome do município
            uf: Estado
            competencia: Competência
        """
        # Extrair IED e população dos dados se disponível
        ied = None
        populacao = 0
        
        if dados and 'pagamentos' in dados:
            pagamentos = dados['pagamentos']
            if pagamentos:
                primeiro_pagamento = pagamentos[0]
                ied = primeiro_pagamento.get('dsFaixaIndiceEquidadeEsfEap')
                populacao = primeiro_pagamento.get('qtPopulacao', 0)
        
        cls.update_state(
            dados=dados,
            municipio_selecionado=municipio,
            uf_selecionada=uf,
            competencia=competencia,
            ied=ied,
            populacao=populacao
        )
    
    @classmethod
    def export_state_for_debug(cls) -> Dict[str, Any]:
        """
        Exporta o estado atual para debug.
        
        Returns:
            Dict: Estado serializado
        """
        state = cls.get_state()
        return {
            'municipio': state.municipio_selecionado,
            'uf': state.uf_selecionada,
            'competencia': state.competencia,
            'ied': state.ied,
            'total_services': cls.get_total_services_selected(),
            'calculo_realizado': state.calculo_realizado,
            'ultima_atualizacao': state.ultima_atualizacao,
            'has_dados': cls.has_dados()
        }
    
    @classmethod
    def force_population_sync(cls) -> None:
        """
        Força a sincronização da população entre o core e session_state.
        Útil para garantir que a população está disponível para cálculos legados.
        """
        state = cls.get_state()
        
        # Se temos população no core mas não no session_state, sincronizar
        if state.populacao > 0 and st.session_state.get('populacao', 0) == 0:
            st.session_state['populacao'] = state.populacao
        
        # Se temos população no session_state mas não no core, sincronizar
        elif st.session_state.get('populacao', 0) > 0 and state.populacao == 0:
            cls.update_state(populacao=st.session_state['populacao'])
        
        # Se temos dados mas população não foi extraída, tentar extrair
        elif state.populacao == 0 and state.dados:
            try:
                if 'pagamentos' in state.dados and state.dados['pagamentos']:
                    populacao = state.dados['pagamentos'][0].get('qtPopulacao', 0)
                    if populacao > 0:
                        cls.update_state(populacao=populacao)
            except (KeyError, IndexError, TypeError):
                pass
    
# Funções de conveniência para compatibilidade com código existente
def get_state() -> AppState:
    """Função de conveniência para obter o estado."""
    return StateManager.get_state()

def update_state(**kwargs) -> None:
    """Função de conveniência para atualizar o estado."""
    StateManager.update_state(**kwargs)

def clear_all_state() -> None:
    """Função de conveniência para limpar o estado."""
    StateManager.clear_state()

def display_state_debug() -> None:
    """Exibe informações de debug do estado."""
    if not st.session_state.get('debug_mode', False):
        return
    
    with st.expander("🔍 Debug: Estado da Aplicação"):
        state_info = StateManager.export_state_for_debug()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.json(state_info)
        
        with col2:
            if st.button("🧹 Limpar Estado"):
                StateManager.clear_state()
                st.rerun()
            
            if st.button("🔄 Sincronizar Estado"):
                StateManager._sync_to_legacy_session_state()
                st.success("Estado sincronizado!")
