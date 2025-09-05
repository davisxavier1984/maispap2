# Sistema de Monitoramento de Financiamento da Saúde - papprefeito
import streamlit as st
import pandas as pd
import json
import os
from pyUFbr.baseuf import ufbr
from utils import consultar_api, format_currency

# Carregar dados de configuração
def carregar_config():
    """Carrega os dados do arquivo config.json"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error("Arquivo config.json não encontrado")
        return None
    except json.JSONDecodeError:
        st.error("Erro ao decodificar arquivo config.json")
        return None

def exibir_tabela_quality_values(quality_values):
    """Exibe uma tabela com os valores de qualidade das equipes"""
    st.subheader("📊 Valores de Qualidade por Tipo de Equipe")
    
    if not quality_values:
        st.warning("Dados de qualidade não disponíveis")
        return
    
    # Criar dados para a tabela
    dados_tabela = []
    for equipe, valores in quality_values.items():
        linha = {
            "Tipo de Equipe": equipe,
            "Ótimo": format_currency(valores.get("Ótimo", 0)),
            "Bom": format_currency(valores.get("Bom", 0)),
            "Suficiente": format_currency(valores.get("Suficiente", 0)),
            "Regular": format_currency(valores.get("Regular", 0))
        }
        dados_tabela.append(linha)
    
    # Criar DataFrame
    df_quality = pd.DataFrame(dados_tabela)
    
    # Exibir tabela
    st.dataframe(df_quality, use_container_width=True)
    
    # Informação adicional
    st.info(f"📋 Total de tipos de equipes com valores de qualidade: {len(dados_tabela)}")

def calcular_valores_municipio(quality_values, classificacao_municipio, municipio_nome, uf_nome):
    """Calcula e exibe valores específicos para o município baseado na classificação de qualidade"""
    st.subheader(f"💰 Valores de Qualidade para {municipio_nome} - {uf_nome}")
    
    if not quality_values or not classificacao_municipio:
        st.warning("Dados insuficientes para calcular valores específicos do município")
        return
    
    # Normalizar classificação (caso venha da API com variações)
    classificacao_normalizada = classificacao_municipio.strip().title()
    
    # Verificar se a classificação existe
    classificacoes_validas = ["Ótimo", "Bom", "Suficiente", "Regular"]
    if classificacao_normalizada not in classificacoes_validas:
        st.warning(f"Classificação '{classificacao_municipio}' não reconhecida. Usando 'Bom' como padrão.")
        classificacao_normalizada = "Bom"
    
    # Exibir classificação atual
    st.info(f"🎯 **Classificação atual**: {classificacao_normalizada}")
    
    # Criar tabela com valores específicos para a classificação
    dados_municipio = []
    valor_total = 0
    
    for equipe, valores in quality_values.items():
        if classificacao_normalizada in valores:
            valor_especifico = valores[classificacao_normalizada]
            valor_total += valor_especifico
            
            linha = {
                "Tipo de Equipe": equipe,
                f"Valor ({classificacao_normalizada})": format_currency(valor_especifico)
            }
            dados_municipio.append(linha)
    
    if dados_municipio:
        # Exibir tabela principal
        df_municipio = pd.DataFrame(dados_municipio)
        st.dataframe(df_municipio, use_container_width=True)
        
        # Exibir métricas importantes
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💵 Valor Total", format_currency(valor_total))
        with col2:
            st.metric("📊 Tipos de Equipes", len(dados_municipio))
        with col3:
            st.metric("⭐ Classificação", classificacao_normalizada)
        
        # Comparação com outras classificações
        if st.expander("📈 Comparação com Outras Classificações"):
            comparacao_dados = []
            for classificacao in classificacoes_validas:
                total_classificacao = 0
                for valores in quality_values.values():
                    if classificacao in valores:
                        total_classificacao += valores[classificacao]
                
                comparacao_dados.append({
                    "Classificação": classificacao,
                    "Valor Total": format_currency(total_classificacao),
                    "Diferença para Atual": format_currency(total_classificacao - valor_total) if classificacao != classificacao_normalizada else "Atual"
                })
            
            df_comparacao = pd.DataFrame(comparacao_dados)
            st.dataframe(df_comparacao, use_container_width=True)
    else:
        st.warning("Nenhum valor encontrado para a classificação atual")

def exibir_valores_reais_municipio(dados):
    """Exibe uma tabela com os valores reais de qualidade das equipes do município"""
    st.subheader("💰 Valores Reais de Qualidade por Equipe")
    
    if not dados or 'pagamentos' not in dados:
        st.warning("Dados de pagamentos não disponíveis")
        return
    
    pagamentos = dados['pagamentos'][0]  # Primeiro registro de pagamentos
    
    # Extrair dados das equipes
    equipes_dados = []
    valor_total_geral = 0
    
    # eSF - Equipes de Saúde da Família
    qt_esf = pagamentos.get('qtEsfHomologado', 0)
    vl_qualidade_esf = pagamentos.get('vlQualidadeEsf', 0)
    if qt_esf > 0:
        vl_unit_esf = vl_qualidade_esf / qt_esf
        equipes_dados.append({
            "Tipo de Equipe": "eSF - Equipes de Saúde da Família",
            "Quantidade": qt_esf,
            "Valor Qualidade/Equipe": format_currency(vl_unit_esf),
            "Valor Total Qualidade": format_currency(vl_qualidade_esf)
        })
        valor_total_geral += vl_qualidade_esf
    
    # eMulti - Equipes Multiprofissionais
    qt_emulti = pagamentos.get('qtEmultiPagas', 0)
    vl_qualidade_emulti = pagamentos.get('vlPagamentoEmultiQualidade', 0)
    if qt_emulti > 0:
        vl_unit_emulti = vl_qualidade_emulti / qt_emulti
        equipes_dados.append({
            "Tipo de Equipe": "eMulti - Equipes Multiprofissionais",
            "Quantidade": qt_emulti,
            "Valor Qualidade/Equipe": format_currency(vl_unit_emulti),
            "Valor Total Qualidade": format_currency(vl_qualidade_emulti)
        })
        valor_total_geral += vl_qualidade_emulti
    
    # eSB - Saúde Bucal
    qt_esb = pagamentos.get('qtSbPagamentoModalidadeI', 0)
    vl_qualidade_esb = pagamentos.get('vlPagamentoEsb40hQualidade', 0)
    if qt_esb > 0:
        vl_unit_esb = vl_qualidade_esb / qt_esb
        equipes_dados.append({
            "Tipo de Equipe": "eSB - Saúde Bucal",
            "Quantidade": qt_esb,
            "Valor Qualidade/Equipe": format_currency(vl_unit_esb),
            "Valor Total Qualidade": format_currency(vl_qualidade_esb)
        })
        valor_total_geral += vl_qualidade_esb
    
    # ACS - Agentes Comunitários de Saúde (se tiver componente qualidade separado)
    qt_acs = pagamentos.get('qtAcsDiretoPgto', 0)
    vl_total_acs = pagamentos.get('vlTotalAcsDireto', 0)
    if qt_acs > 0 and vl_total_acs > 0:
        equipes_dados.append({
            "Tipo de Equipe": "ACS - Agentes Comunitários de Saúde",
            "Quantidade": qt_acs,
            "Valor Qualidade/Equipe": format_currency(vl_total_acs / qt_acs),
            "Valor Total Qualidade": format_currency(vl_total_acs)
        })
        # Note: ACS não tem componente qualidade separado, então não adiciona ao total geral de qualidade
    
    if equipes_dados:
        # Criar DataFrame
        df_equipes = pd.DataFrame(equipes_dados)
        
        # Exibir tabela
        st.dataframe(df_equipes, use_container_width=True)
        
        # Exibir métricas importantes
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💵 Total Geral Qualidade", format_currency(valor_total_geral))
        with col2:
            st.metric("📊 Tipos de Equipes", len([eq for eq in equipes_dados if "ACS" not in eq["Tipo de Equipe"]]))
        with col3:
            # Encontrar maior valor individual por equipe (excluindo ACS)
            valores_individuais = []
            for eq in equipes_dados:
                if "ACS" not in eq["Tipo de Equipe"]:
                    # Extrair valor numérico da string formatada
                    valor_str = eq["Valor Qualidade/Equipe"].replace("R$", "").replace(".", "").replace(",", ".").strip()
                    try:
                        valores_individuais.append(float(valor_str))
                    except:
                        pass
            
            if valores_individuais:
                maior_valor = max(valores_individuais)
                st.metric("⭐ Maior Valor/Equipe", format_currency(maior_valor))
        
        # Informação adicional
        st.info(f"📋 Valores extraídos dos dados reais do município para a competência {pagamentos.get('nuParcela', 'N/A')}")
        
        # Detalhes adicionais em expander
        if st.expander("📈 Detalhes das Classificações"):
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Classificações do Município:**")
                st.write(f"• IED: {pagamentos.get('dsFaixaIndiceEquidadeEsfEap', 'N/A')}")
                st.write(f"• Qualidade eSF/eAP: {pagamentos.get('dsClassificacaoQualidadeEsfEap', 'N/A')}")
                st.write(f"• Vínculo eSF/eAP: {pagamentos.get('dsClassificacaoVinculoEsfEap', 'N/A')}")
                st.write(f"• Qualidade eMulti: {pagamentos.get('dsClassificacaoQualidadeEmulti', 'N/A')}")
            
            with col2:
                st.write("**Informações Complementares:**")
                st.write(f"• População IBGE: {pagamentos.get('qtPopulacao', 'N/A'):,}")
                st.write(f"• Ano Ref. População: {pagamentos.get('nuAnoRefPopulacaoIbge', 'N/A')}")
                st.write(f"• Teto eSF: {pagamentos.get('qtTetoEsf', 'N/A')}")
                st.write(f"• Teto eMulti: {pagamentos.get('qtTetoEmultiAmpliada', 'N/A')}")
    else:
        st.warning("Nenhum dado de equipe encontrado para cálculo dos valores")

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
    
    st.title("🏥 Sistema de Monitoramento de Financiamento da Saúde - papprefeito")
    
    # Carregar configurações
    config_data = carregar_config()

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
            
            # Extrair e salvar população dos dados
            try:
                if 'pagamentos' in dados and dados['pagamentos']:
                    populacao = dados['pagamentos'][0].get('qtPopulacao', 0)
                    if populacao > 0:
                        st.session_state['populacao'] = populacao
            except (KeyError, IndexError, TypeError):
                pass
            
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

            # Focar apenas em vínculo/acompanhamento e qualidade
            if pagamentos:
                # Exibir tabela de classificação de vínculo e acompanhamento para eSF/eAP
                st.subheader("🎯 Classificação de Vínculo e Acompanhamento - eSF/eAP")
                try:
                    from utils import extrair_dados_vinculo_acompanhamento, criar_tabela_vinculo_acompanhamento
                    
                    dados_vinculo = extrair_dados_vinculo_acompanhamento(dados)
                    
                    # Verificar se há dados para exibir
                    tem_dados = dados_vinculo['esf']['tem_equipes'] or dados_vinculo['eap']['tem_equipes']
                    
                    if tem_dados:
                        tabela_vinculo = criar_tabela_vinculo_acompanhamento(dados_vinculo)
                        st.dataframe(tabela_vinculo, use_container_width=True)
                        
                        # Mostrar informações resumidas
                        total_equipes = 0
                        total_vinculo = 0
                        total_qualidade = 0
                        
                        if dados_vinculo['esf']['tem_equipes']:
                            total_equipes += dados_vinculo['esf']['quantidade_equipes']
                            total_vinculo += dados_vinculo['esf']['valor_vinculo']
                            total_qualidade += dados_vinculo['esf']['valor_qualidade']
                            
                        if dados_vinculo['eap']['tem_equipes']:
                            total_equipes += dados_vinculo['eap']['quantidade_equipes']
                            total_vinculo += dados_vinculo['eap']['valor_vinculo']
                            total_qualidade += dados_vinculo['eap']['valor_qualidade']
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Total de Equipes", total_equipes)
                        with col2:
                            st.metric("Total Vínculo", format_currency(total_vinculo))
                        with col3:
                            st.metric("Total Qualidade", format_currency(total_qualidade))
                        with col4:
                            st.metric("Total Geral", format_currency(total_vinculo + total_qualidade))
                            
                    else:
                        st.info("ℹ️ Nenhuma equipe eSF ou eAP encontrada para este município.")
                        
                except ImportError as e:
                    st.error(f"Erro ao importar funções necessárias: {e}")
                except Exception as e:
                    st.error(f"Erro ao gerar tabela de vínculo e acompanhamento: {e}")
                
                # Exibir valores reais de qualidade por equipe
                st.markdown("---")
                exibir_valores_reais_municipio(dados)
                
                # Nova tabela: Valor Total por Classificação (no final da página)
                st.markdown("---")
                st.subheader("📊 Valor Total por Classificação - Cenários Completos")
                try:
                    from utils import criar_tabela_total_por_classificacao
                    
                    tabela_classificacao = criar_tabela_total_por_classificacao(dados)
                    st.dataframe(tabela_classificacao, use_container_width=True)
                    
                    # Destacar a classificação atual
                    primeiro_pagamento = pagamentos[0]
                    classificacao_atual = primeiro_pagamento.get('dsClassificacaoQualidadeEsfEap', 'Não informado')
                    classificacao_emulti = primeiro_pagamento.get('dsClassificacaoQualidadeEmulti', 'Não informado')
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if classificacao_atual != 'Não informado':
                            st.info(f"💡 **Classificação eSF/eAP/eSB**: {classificacao_atual}")
                    with col2:
                        if classificacao_emulti != 'Não informado':
                            st.info(f"💡 **Classificação eMulti**: {classificacao_emulti}")
                            
                except ImportError as e:
                    st.error(f"Erro ao importar função de classificação: {e}")
                except Exception as e:
                    st.error(f"Erro ao gerar tabela por classificação: {e}")
                
                # Salvar informações importantes na sessão (sem exibir)
                primeiro_pagamento = pagamentos[0]
                st.session_state['ied'] = primeiro_pagamento.get('dsFaixaIndiceEquidadeEsfEap', '')
                st.session_state['classificacao'] = primeiro_pagamento.get('dsClassificacaoQualidadeEsfEap', 'Bom')
                st.session_state['vinculo'] = primeiro_pagamento.get('dsClassificacaoVinculoEsfEap', 'Bom')
            
        else:
            st.error("❌ Nenhum dado encontrado para os parâmetros informados.")
            st.info("💡 Verifique se o código IBGE e a competência estão corretos.")

if __name__ == "__main__":
    main()