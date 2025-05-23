"""
Funções para manipulação de dados na Calculadora PAP.
Versão refatorada que utiliza o APIClient consolidado.
"""
import streamlit as st
from typing import Optional, Dict, Any
from .api_client import APIClient, load_data_from_json as load_cache_data, consultar_api as api_consultar

# Nome do arquivo JSON legado para compatibilidade
DATA_FILE = "data.json"

def get_estrato(ied: Optional[str] = None) -> str:
    """
    Retorna o estrato com base no IED (dsFaixaIndiceEquidadeEsfEap).
    Se o IED for inválido ou ausente, exibe um erro e interrompe o cálculo.
    
    Args:
        ied: String do IED no formato "ESTRATO X"
        
    Returns:
        str: Último caractere do IED (número do estrato)
        
    Raises:
        st.stop(): Para a execução se IED for inválido
    """
    if ied is not None and isinstance(ied, str) and ied.startswith("ESTRATO "):
        try:
            estrato = ied[-1]
            if estrato.isdigit():
                return estrato
            else:
                st.error(f"Estrato inválido extraído do IED: {ied}. Esperado dígito, encontrado: {estrato}")
                st.stop()
        except IndexError:
            st.error(f"Erro ao extrair estrato do IED: {ied}. Formato inválido.")
            st.stop()

    st.error("⚠️ IED (dsFaixaIndiceEquidadeEsfEap) ausente ou inválido. Não é possível determinar o estrato.")
    st.info("💡 **Dica**: Certifique-se de que os dados foram carregados corretamente na página 'Consulta Dados'.")
    st.stop()

def load_data_from_json() -> Dict[str, Any]:
    """
    Carrega os dados do arquivo de cache. 
    Mantém compatibilidade com data.json e data_cache.json.
    
    Returns:
        Dict: Dados carregados do cache ou dicionário vazio
    """
    # Primeiro tenta carregar do cache moderno
    dados = load_cache_data()
    
    if dados:
        return dados
    
    # Fallback para o arquivo legado data.json
    try:
        import json
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            dados_legado = json.load(f)
            st.info("📁 Dados carregados do arquivo legado data.json")
            return dados_legado
    except FileNotFoundError:
        st.warning("⚠️ Nenhum arquivo de dados encontrado. Selecione UF e Município na página 'Consulta Dados'.")
        return {}
    except json.JSONDecodeError:
        st.error("❌ Erro ao decodificar arquivo de dados. Arquivo pode estar corrompido.")
        return {}

def consultar_api(codigo_ibge: str, competencia: str) -> Optional[Dict[str, Any]]:
    """
    Consulta a API de financiamento da saúde.
    Interface compatível que utiliza o APIClient robusto.
    
    Args:
        codigo_ibge: Código IBGE do município
        competencia: Competência no formato AAAAMM
        
    Returns:
        Dict ou None: Dados da API ou None em caso de erro
    """
    return api_consultar(codigo_ibge, competencia)

def validar_dados_municipio(dados: Dict[str, Any]) -> bool:
    """
    Valida se os dados do município estão completos e válidos.
    
    Args:
        dados: Dicionário com dados da API
        
    Returns:
        bool: True se dados são válidos
    """
    if not isinstance(dados, dict):
        return False
    
    # Verificar estruturas essenciais
    required_keys = ['resumosPlanosOrcamentarios', 'pagamentos']
    if not any(key in dados for key in required_keys):
        return False
    
    # Validar pagamentos se existir
    pagamentos = dados.get('pagamentos', [])
    if pagamentos and isinstance(pagamentos, list):
        primeiro_pagamento = pagamentos[0]
        required_payment_fields = ['dsFaixaIndiceEquidadeEsfEap', 'qtEsfCredenciado']
        return all(field in primeiro_pagamento for field in required_payment_fields)
    
    return True

def extrair_informacoes_municipio(dados: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrai informações essenciais do município dos dados da API.
    
    Args:
        dados: Dados completos da API
        
    Returns:
        Dict: Informações estruturadas do município
    """
    info = {
        'ied': None,
        'total_equipes': 0,
        'classificacao_vinculo': None,
        'classificacao_qualidade': None,
        'populacao': 0
    }
    
    try:
        pagamentos = dados.get('pagamentos', [])
        if pagamentos:
            primeiro_pagamento = pagamentos[0]
            info.update({
                'ied': primeiro_pagamento.get('dsFaixaIndiceEquidadeEsfEap'),
                'total_equipes': primeiro_pagamento.get('qtEsfCredenciado', 0),
                'classificacao_vinculo': primeiro_pagamento.get('dsClassificacaoVinculoEsfEap'),
                'classificacao_qualidade': primeiro_pagamento.get('dsClassificacaoQualidadeEsfEap')
            })
        
        # Tentar extrair população de outras fontes se disponível
        resumos = dados.get('resumosPlanosOrcamentarios', [])
        # Aqui poderia ser implementada lógica para extrair população dos resumos
        
    except (KeyError, IndexError, TypeError) as e:
        st.warning(f"⚠️ Erro ao extrair informações do município: {e}")
    
    return info
