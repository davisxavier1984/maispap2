"""
Módulo para análise de cenários da Calculadora PAP.
"""
import streamlit as st
import pandas as pd
from utils import format_currency, currency_to_float

def gerar_analise_cenarios(total_incentivo_aps, total_incentivo_emulti, total_geral, vinculo_values, quality_values, selected_services, total_fixed_value, total_implantacao_manutencao_value, total_saude_bucal_value, total_per_capita):
    """
    Gera o texto de análise dos cenários com base nos valores calculados.

    Args:
        total_incentivo_aps: Valor total do incentivo financeiro da APS para eSF e eAP.
        total_incentivo_emulti: Valor total do incentivo financeiro da APS para eMulti.
        total_geral: Valor total geral calculado.
        vinculo_values: Dicionário com os valores de vínculo e acompanhamento por qualidade.
        quality_values: Dicionário com os valores de qualidade por classificação.
        selected_services: Dicionário com os serviços selecionados e suas quantidades.
        total_fixed_value: Valor total do componente fixo.
        total_implantacao_manutencao_value: Valor total de implantação e manutenção.
        total_saude_bucal_value: Valor total de saúde bucal.
        total_per_capita: Valor total per capita.

    Returns:
        str: Texto de análise dos cenários.
    """

    # Valores no modelo anterior (hipotético - você precisará ajustar com base em dados reais)
    # Neste exemplo, estou considerando que o modelo anterior seria apenas o valor fixo + per capita
    valor_modelo_anterior = total_fixed_value + total_per_capita

    # Cenário de pior desempenho (Regular)
    pior_desempenho_vinculo = sum(vinculo_values[service]['Regular'] * selected_services.get(service, 0) for service in vinculo_values if service in selected_services)
    pior_desempenpenho_qualidade = sum(quality_values[service]['Regular'] * selected_services.get(service, 0) for service in quality_values if service in selected_services)

    # Cenário eMulti Regular
    pior_desempenho_emulti = 0
    for service in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
        if selected_services.get(service, 0) > 0:
            if service in quality_values:
                valor_qualidade = quality_values[service]['Regular']
            else:
                valor_qualidade = 0

            pior_desempenho_emulti += valor_qualidade * selected_services.get(service, 0)

    valor_pior_desempenho = total_fixed_value + pior_desempenho_vinculo + pior_desempenpenho_qualidade + total_implantacao_manutencao_value + total_saude_bucal_value + total_per_capita + pior_desempenho_emulti

    # Cenário de melhor desempenho (Ótimo)
    melhor_desempenho_vinculo = sum(vinculo_values[service]['Ótimo'] * selected_services.get(service, 0) for service in vinculo_values if service in selected_services)
    melhor_desempenho_qualidade = sum(quality_values[service]['Ótimo'] * selected_services.get(service, 0) for service in quality_values if service in selected_services)

    # Cenário eMulti Ótimo
    melhor_desempenho_emulti = 0
    for service in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
        if selected_services.get(service, 0) > 0:
            if service in quality_values:
                valor_qualidade = quality_values[service]['Ótimo']
            else:
                valor_qualidade = 0

            melhor_desempenho_emulti += valor_qualidade * selected_services.get(service, 0)

    valor_melhor_desempenho = total_fixed_value + melhor_desempenho_vinculo + melhor_desempenho_qualidade + total_implantacao_manutencao_value + total_saude_bucal_value + total_per_capita + melhor_desempenho_emulti

    # Diferença entre os cenários
    diferenca = valor_melhor_desempenho - valor_pior_desempenho

    # Porcentagem de aumento
    porcentagem_aumento = ((valor_melhor_desempenho - valor_pior_desempenho) / valor_pior_desempenho) * 100 if valor_pior_desempenho != 0 else 0

    # Texto da análise
    texto_analise = f"""
    <div style="text-align: justify; color: #2c3e50; font-size: 1.1rem">
        <p>
            <b style="font-size: 1.3rem; color: #008080">ANÁLISE DOS CENÁRIOS</b><br>
            O quadro abaixo contém de forma consolidada mensalmente (a cada mês) uma comparação dos valores recebidos no modelo anterior e no cofinanciamento federal da APS. Nele, recomenda-se observar, especialmente se conforme o desempenho, o município tem <span style="color: #008000; font-weight: bold">aumento</span> ou <span style="color: #8B0000; font-weight: bold">redução</span> de repasses federais na APS. Valores negativos (com sinal de <span style="font-weight: bold">menos-</span>) representam diminuição do valor em relação ao modelo de financiamento anterior. No cenário de pior desempenho, <span style="color: #8B0000; font-weight: bold">"REGULAR"</span>, o município recebe o valor de <span style="color: #8B0000; font-weight: bold">{format_currency(valor_pior_desempenho)}</span> e no cenário de melhor desempenho, <span style="color: #008000; font-weight: bold">"ÓTIMO"</span>, o município recebe o valor de <span style="color: #008000; font-weight: bold">{format_currency(valor_melhor_desempenho)}</span>. A diferença de <span style="background-color: #FFFFE0; font-weight: bold">{format_currency(diferenca)}</span> <span style="font-weight: bold">MENSAL</span> está relacionada aos componentes de <span style="font-weight: bold">vínculo e acompanhamento e qualidade</span> que são os valores variáveis do cofinanciamento federal na APS. <span style="color: #008000; font-weight: bold">AUMENTO DE MAIS DE {porcentagem_aumento:.2f}%</span>, EQUIVALENTE A QUASE <span style="color: #008000; font-weight: bold">{format_currency(diferenca * 12)}</span> SOMENTE NESTE ITEM.
        </p>
    </div>
    """

    return texto_analise


def display_scenarios_analysis(total_incentivo_aps, total_incentivo_emulti, total_geral, vinculo_values, quality_values, selected_services, total_fixed_value, total_implantacao_manutencao_value, total_saude_bucal_value, total_per_capita):
    """
    Exibe a análise de cenários na interface.
    """
    # Gerando a análise dos cenários
    texto_analise = gerar_analise_cenarios(total_incentivo_aps, total_incentivo_emulti, total_geral, vinculo_values, 
                                          quality_values, selected_services, total_fixed_value, total_implantacao_manutencao_value, 
                                          total_saude_bucal_value, total_per_capita)

    # Exibindo a análise dos cenários
    st.markdown(texto_analise, unsafe_allow_html=True)
