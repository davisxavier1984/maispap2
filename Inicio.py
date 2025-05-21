import streamlit as st
import requests
import json
import pandas as pd
from utils import TRADUCOES, formatar_valor, exibir_tabelas
from pyUFbr.baseuf import ufbr

# Nome do arquivo JSON para armazenar os dados
DATA_FILE = "data.json"

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
        response = requests.get(url, params=params, headers={"Accept": "application/json"})
        response.raise_for_status()
        dados = response.json()

        # Salva os dados em um arquivo JSON com indentação para melhor legibilidade
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

        return dados
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na consulta à API: {e}")
        return None

def main():
    
    st.title("🏥 Sistema de Monitoramento de Financiamento da Saúde")

    with st.expander("🔍 Parâmetros de Consulta", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            estados = ufbr.list_uf
            uf_selecionada = st.selectbox("Selecione um Estado", options=estados)
        with col2:
            competencia = st.text_input("Competência (AAAAMM)", "202501")

        if uf_selecionada:
            municipios = ufbr.list_cidades(uf_selecionada)
            municipio_selecionado = st.selectbox("Selecione um Município", options=municipios)

            if municipio_selecionado:
                try:
                    codigo_ibge = ufbr.get_cidade(municipio_selecionado).codigo
                    codigo_ibge = str(int(float(codigo_ibge)))[:-1]
                except AttributeError:
                    st.error("Erro ao obter código IBGE do município")
                    return

    if st.button("Consultar"):
        if not (uf_selecionada and municipio_selecionado and competencia):
            st.error("Por favor, preencha todos os campos de consulta.")
            return

        dados = consultar_api(codigo_ibge, competencia)

        if dados:
            #st.success("Dados carregados com sucesso e salvos em data.json!")

            resumos = dados.get('resumosPlanosOrcamentarios', [])
            pagamentos = dados.get('pagamentos', [])

            colunas_resumos = ["sgUf", "coMunicipioIbge", "noMunicipio", "nuCompCnes", "nuParcela",
                               "dsPlanoOrcamentario", "dsEsferaAdministrativa", "vlIntegral", "vlAjuste",
                               "vlDesconto", "vlEfetivoRepasse", "vlImplantacao", "vlAjusteImplantacao",
                               "vlDescontoImplantacao", "vlTotalImplantacao"]

            if resumos:
                #st.subheader("Resumos Orçamentários")
                exibir_tabelas("Resumos Orçamentários", resumos, colunas_resumos)
        else:
            st.error("Nenhum dado encontrado para os parâmetros informados.")

if __name__ == "__main__":
    main()