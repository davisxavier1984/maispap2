"""
Funções para manipulação de dados na Calculadora PAP.
"""
import streamlit as st
import requests
import json
import pandas as pd

# Nome do arquivo JSON para armazenar os dados
DATA_FILE = "data.json"

def get_estrato(ied: str | None = None) -> str:
    """
    Retorna o estrato com base no IED (dsFaixaIndiceEquidadeEsfEap).
    Se o IED for inválido ou ausente, exibe um erro e interrompe o cálculo.
    """
    if ied is not None and isinstance(ied, str) and ied.startswith("ESTRATO "):
        try:
            return ied[-1]
        except IndexError:
            st.error(f"Erro ao extrair estrato do IED: {ied}.")
            st.stop()

    st.error("IED (dsFaixaIndiceEquidadeEsfEap) ausente ou inválido. Não é possível determinar o estrato.")
    st.stop()

def load_data_from_json():
    """Carrega os dados do arquivo data.json. Retorna um dicionário vazio se o arquivo não existir."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Selecione UF e Município e clique em Consultar.")
        return {}

def consultar_api(codigo_ibge, competencia):
    """Consulta a API de financiamento da saúde e salva os dados em um arquivo JSON com indentação."""
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
        response = requests.get(url, params=params, headers={"Accept": "application/json"}, verify=False)
        response.raise_for_status()
        dados = response.json()

        # Salva os dados em um arquivo JSON com indentação para melhor legibilidade
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

        return dados
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na consulta à API: {e}")
        return None
