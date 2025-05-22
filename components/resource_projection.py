"""
Módulo para projeção de recursos na Calculadora PAP.
"""
import streamlit as st
import pandas as pd
import numpy as np
from utils import format_currency, currency_to_float

def format_with_nan_check(x, format_str="R$ {:.2f}"):
    """Formata um valor com verificação de NaN."""
    if pd.isna(x) or np.isnan(x) if isinstance(x, float) else False:
        return "-"
    try:
        return format_str.format(x)
    except:
        return str(x)

def calculate_regular_scenario(vinculo_values, quality_values, selected_services, total_fixed_value, 
                              total_implantacao_manutencao_value, total_saude_bucal_value, total_per_capita):
    """Calcula o valor do cenário regular."""
    # Zera os valores para o cenário regular
    valor_vinculo_regular = 0
    valor_qualidade_regular = 0
    valor_emulti_regular = 0

    # Vínculo e Acompanhamento (Regular)
    for service in vinculo_values:
        if service in selected_services:
            valor_vinculo_regular += vinculo_values[service].get('Regular', 0) * selected_services.get(service, 0)

    # Qualidade (Regular)
    for service in quality_values:
        if service in selected_services:
            valor_qualidade_regular += quality_values[service].get('Regular', 0) * selected_services.get(service, 0)

    # eMulti (Regular)
    for service in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
        if selected_services.get(service, 0) > 0:
            valor_emulti_regular += quality_values.get(service, {}).get('Regular', 0) * selected_services.get(service, 0)

    # Calcula o valor total do cenário regular
    valor_cenario_regular = total_fixed_value + valor_vinculo_regular + valor_qualidade_regular + total_implantacao_manutencao_value + total_saude_bucal_value + total_per_capita + valor_emulti_regular

    return valor_cenario_regular

def display_resource_projection(vinculo_values, quality_values, selected_services, total_fixed_value, 
                               total_implantacao_manutencao_value, total_saude_bucal_value, total_per_capita):
    """
    Exibe a projeção de recursos com base nos parâmetros adicionais.
    """
    # Só exibe o RESULTADO do cálculo se o cálculo foi realizado
    if st.session_state['calculo_realizado']:
        # Obtendo o nome do município e UF do st.session_state['dados']
        if st.session_state['dados'] and 'resumosPlanosOrcamentarios' in st.session_state['dados'] and len(st.session_state['dados']['resumosPlanosOrcamentarios']) > 0:
            municipio_selecionado = st.session_state['dados']['resumosPlanosOrcamentarios'][0].get('noMunicipio', 'Não informado')
            uf_selecionada = st.session_state['dados']['resumosPlanosOrcamentarios'][0].get('sgUf', 'Não informado')
        else:
            municipio_selecionado = "Não informado"
            uf_selecionada = "Não informado"

        # CÁLCULO DO CENÁRIO REGULAR
        valor_cenario_regular = calculate_regular_scenario(vinculo_values, quality_values, selected_services, 
                                                          total_fixed_value, total_implantacao_manutencao_value, 
                                                          total_saude_bucal_value, total_per_capita)
        
        # Armazenar o valor do cenário regular na session_state para uso em outras funções
        st.session_state['valor_cenario_regular'] = valor_cenario_regular

        # Cálculos para o texto
        total_parametros = st.session_state['valor_esf_eap'] + st.session_state['valor_saude_bucal'] + st.session_state['valor_acs'] + st.session_state['valor_estrategicas']
        aumento_mensal = total_parametros - valor_cenario_regular  # Diferença entre o total adicional e o cenário regular
        aumento_anual = aumento_mensal * 12
        
        # Armazenar valores importantes na session_state para uso na página de projeção financeira
        st.session_state['aumento_mensal'] = aumento_mensal
        st.session_state['aumento_anual'] = aumento_anual
        st.session_state['municipio_selecionado'] = municipio_selecionado
        st.session_state['uf_selecionada'] = uf_selecionada
        
        # Verificar se é um aumento negativo
        is_negative_increase = aumento_anual < 0
        adjusted_aumento_anual = abs(aumento_anual)
        
        # Inicializar as variáveis de estado para os percentuais se não existirem
        for period in [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]:
            percent = period // 3 * 10  # 10%, 20%, 30%, etc.
            if f'percentual_{period}m' not in st.session_state:
                st.session_state[f'percentual_{period}m'] = int(percent)
            elif isinstance(st.session_state[f'percentual_{period}m'], (list, tuple)):
                # Corrigir caso esteja armazenado como lista
                st.session_state[f'percentual_{period}m'] = int(percent)
            if f'valor_{period}m' not in st.session_state:
                st.session_state[f'valor_{period}m'] = float(adjusted_aumento_anual * (percent / 100))
                
        # Criar dataframe para exibir os parâmetros adicionais
        df_parametros = pd.DataFrame({
            'Parâmetro': [
                "ESF/EAP",
                "Saúde Bucal",
                "ACS",
                "Áreas Estratégicas",
                "Total Adicional"
            ],
            'Valor': [
                st.session_state['valor_esf_eap'],
                st.session_state['valor_saude_bucal'],
                st.session_state['valor_acs'],
                st.session_state['valor_estrategicas'],
                total_parametros
            ]
        })

        def style_table(val):
            if isinstance(val, (int, float)):
                return f'background-color: #008080; color: white; font-weight: bold; text-align: right; font-size: 1.2rem'
            return ''

        # Define uma paleta de cores
        colors = ['#e6ffe6', '#ccffcc', '#b3ffb3', '#99ff99', '#80ff80']

        def highlight_row(row):
            if row.name == len(df_parametros) - 1:  # Última linha (Total Adicional)
                return [f'background-color: #008080; color: white;'] * len(row) # Cor de fundo para o Total
            else:
                return [f'background-color: {colors[row.name % len(colors)]}; color: #2c3e50;'] * len(row) # Cor de fundo para as demais linhas, alternando as cores

        st.dataframe(df_parametros.style.format({'Valor': '{:,.2f}'.format}).map(style_table, subset=['Valor']).apply(highlight_row, axis=1))

        # Texto descritivo com valores calculados
        st.markdown(f"""
            <div style="text-align: justify; color: #2c3e50; font-size: 1.1rem">
                <p>
                    Considerando os valores informados, e subtraindo o valor do cenário <b>REGULAR ({format_currency(valor_cenario_regular)})</b>,
                    espera-se que o <b style="color: #008080">AUMENTO SEJA DE R$ {format_currency(aumento_mensal).replace('R$', '', 1).strip()} MIL MENSAIS</b>,
                    resultando em <b style="color: #008080">APROXIMADAMENTE R$ {format_currency(aumento_anual).replace('R$', '', 1).strip()} MIL ANUAL</b>,
                    comparado com o cenário de pior desempenho. Estes valores são projetados para o município de
                    <b style="color: #008080">{municipio_selecionado} - {uf_selecionada}</b>, levando em conta os parâmetros adicionais fornecidos.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
        # Adicionar uma observação sobre o sinal negativo, se aplicável
        if is_negative_increase:
            st.markdown(f"""
                <div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; margin-top: 10px;">
                    <p style="margin: 0; color: #856404;"><b>Nota:</b> Os valores apresentados representam uma <b>redução</b> em relação ao cenário regular, 
                    por isso o sinal negativo foi removido para facilitar a visualização. Considere estes valores como diminuição de receita.</p>
                </div>
                """, unsafe_allow_html=True)

    else:
        # Se o cálculo ainda não foi realizado, exibe a mensagem
        st.info("Preencha os parâmetros, selecione o município e clique em 'Calcular' para gerar os resultados.")
