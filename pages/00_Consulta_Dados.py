# filepath: /home/davi/Python-Projetos/Alysson/Calculadora/pages/00_Consulta_Dados.py
import streamlit as st
import pandas as pd
from pyUFbr.baseuf import ufbr
from utils import consultar_api, format_currency

def exibir_tabelas(titulo, dados, colunas):
    """Exibe uma tabela formatada com os dados."""
    st.subheader(titulo)
    
    if dados:
        # Filtrar apenas as colunas que existem nos dados
        colunas_existentes = []
        for coluna in colunas:
            if any(coluna in item for item in dados):
                colunas_existentes.append(coluna)
        
        # Criar DataFrame
        df_dados = []
        for item in dados:
            linha = {}
            for coluna in colunas_existentes:
                valor = item.get(coluna, "")
                # Formatar valores monetários
                if coluna.startswith('vl') and isinstance(valor, (int, float)) and valor != 0:
                    linha[coluna] = format_currency(valor)
                else:
                    linha[coluna] = valor
            df_dados.append(linha)
        
        df = pd.DataFrame(df_dados)
        
        # Mapear nomes das colunas para português
        mapeamento_colunas = {
            "sgUf": "UF",
            "coMunicipioIbge": "Código IBGE",
            "noMunicipio": "Município",
            "nuCompCnes": "Competência CNES",
            "nuParcela": "Parcela",
            "dsPlanoOrcamentario": "Plano Orçamentário",
            "dsEsferaAdministrativa": "Esfera Administrativa",
            "vlIntegral": "Valor Integral",
            "vlAjuste": "Valor Ajuste",
            "vlDesconto": "Valor Desconto",
            "vlEfetivoRepasse": "Valor Efetivo Repasse",
            "vlImplantacao": "Valor Implantação",
            "vlAjusteImplantacao": "Ajuste Implantação",
            "vlDescontoImplantacao": "Desconto Implantação",
            "vlTotalImplantacao": "Total Implantação"
        }
        
        # Renomear colunas
        df = df.rename(columns=mapeamento_colunas)
        
        # Exibir DataFrame
        st.dataframe(df, use_container_width=True)
        
        # Mostrar resumo
        st.info(f"📊 Total de registros: {len(df)}")
    else:
        st.warning("Nenhum dado encontrado.")

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

        with st.spinner("Consultando dados da API..."):
            dados = consultar_api(codigo_ibge, competencia)

        if dados:
            # Salvar dados na sessão
            st.session_state['dados'] = dados
            st.session_state['municipio_selecionado'] = municipio_selecionado
            st.session_state['uf_selecionada'] = uf_selecionada
            st.session_state['competencia'] = competencia
            
            st.success(f"✅ Dados carregados com sucesso para {municipio_selecionado} - {uf_selecionada}!")

            # Exibir dados
            resumos = dados.get('resumosPlanosOrcamentarios', [])
            pagamentos = dados.get('pagamentos', [])

            # Colunas para resumos orçamentários
            colunas_resumos = [
                "sgUf", "coMunicipioIbge", "noMunicipio", "nuCompCnes", "nuParcela",
                "dsPlanoOrcamentario", "dsEsferaAdministrativa", "vlIntegral", "vlAjuste",
                "vlDesconto", "vlEfetivoRepasse", "vlImplantacao", "vlAjusteImplantacao",
                "vlDescontoImplantacao", "vlTotalImplantacao"
            ]

            # Colunas para pagamentos
            colunas_pagamentos = [
                "sgUf", "noMunicipio", "coMunicipioIbge", "nuCompCnes", "nuParcela",
                "dsFaixaIndiceEquidadeEsfEap", "dsClassificacaoVinculoEsfEap", 
                "dsClassificacaoQualidadeEsfEap", "qtEsfCredenciado", "qtEsfHomologado"
            ]

            if resumos:
                exibir_tabelas("📋 Resumos dos Planos Orçamentários", resumos, colunas_resumos)
            
            if pagamentos:
                exibir_tabelas("💰 Dados de Pagamentos", pagamentos, colunas_pagamentos)
                
            # Exibir informações importantes extraídas
            if pagamentos:
                st.subheader("ℹ️ Informações Extraídas")
                primeiro_pagamento = pagamentos[0]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("IED", primeiro_pagamento.get('dsFaixaIndiceEquidadeEsfEap', 'N/A'))
                with col2:
                    st.metric("Classificação Vínculo", primeiro_pagamento.get('dsClassificacaoVinculoEsfEap', 'N/A'))
                with col3:
                    st.metric("Classificação Qualidade", primeiro_pagamento.get('dsClassificacaoQualidadeEsfEap', 'N/A'))
                
                # Salvar informações importantes na sessão
                st.session_state['ied'] = primeiro_pagamento.get('dsFaixaIndiceEquidadeEsfEap', '')
                st.session_state['classificacao'] = primeiro_pagamento.get('dsClassificacaoQualidadeEsfEap', 'Bom')
                st.session_state['vinculo'] = primeiro_pagamento.get('dsClassificacaoVinculoEsfEap', 'Bom')
            
        else:
            st.error("❌ Nenhum dado encontrado para os parâmetros informados.")
            st.info("💡 Verifique se o código IBGE e a competência estão corretos.")

if __name__ == "__main__":
    main()
