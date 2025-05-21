"""
Módulo para comunicação com a API de financiamento da saúde.
"""
import streamlit as st
import requests
import json
from requests.exceptions import RequestException

# Nome do arquivo JSON para armazenar os dados
DATA_FILE = "data.json"

def load_data_from_json():
    """Carrega os dados do arquivo data.json. Retorna um dicionário vazio se o arquivo não existir."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Selecione UF e Município e clique em Consultar.")
        return {}

def consultar_api(codigo_ibge: str, competencia: str) -> dict | None:
    """Consulta a API de financiamento da saúde e salva os dados em um arquivo JSON com indentação."""

    st.session_state['competencia'] = competencia

    url = "https://relatorioaps-prd.saude.gov.br/financiamento/pagamento"
    params = {
        "unidadeGeografica": "MUNICIPIO",
        "coUf": codigo_ibge[:2],
        "coMunicipio": codigo_ibge[:6],
        "nuParcelaInicio": competencia,
        "nuParcelaFim": competencia,
        "tipoRelatorio": "COMPLETO"
    }
    
    try:
        # Remover verify=False e tratar o erro de certificado se ocorrer
        response = requests.get(url, params=params, headers={"Accept": "application/json"}, verify=False)
        response.raise_for_status()
        dados = response.json()

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

        return dados
    except RequestException as e:
        st.error(f"Erro na consulta à API: {e}")
        # Aqui você pode adicionar um tratamento mais específico, como:
        # if isinstance(e, requests.exceptions.SSLError):
        #     st.error("Erro de certificado SSL. Verifique a configuração do servidor.")
        return None
