"""
Módulo para geração de relatórios de cenários da Calculadora PAP.
"""
import streamlit as st
import pandas as pd
from utils import format_currency, currency_to_float

def gerar_relatorio_cenarios(total_geral, vinculo_values, quality_values, selected_services, total_implantacao_manutencao_value, total_saude_bucal_value, total_per_capita, total_fixed_value):
    """
    Gera um relatório detalhado dos valores para cada cenário de desempenho e constrói um DataFrame
    para o quadro de comparação iterando sobre as linhas das tabelas geradas.

    Args:
        total_geral: Valor total geral calculado (usado como referência para o modelo anterior).
        vinculo_values: Dicionário com os valores de vínculo e acompanhamento por qualidade.
        quality_values: Dicionário com os valores de qualidade por classificação.
        selected_services: Dicionário com os serviços selecionados e suas quantidades.
        total_implantacao_manutencao_value: Valor total de implantação e manutenção.
        total_saude_bucal_value: Valor total de saúde bucal.
        total_per_capita: Valor total per capita.
        total_fixed_value: Valor total fixo.

    Returns:
        pd.DataFrame: DataFrame para o quadro de comparação.
    """

    cenarios = ['Regular', 'Suficiente', 'Bom', 'Ótimo']

    # Valor base (modelo anterior) - Total geral anterior, calculado na PARTE 4
    valor_base = total_geral

    # DataFrame para o quadro de comparação
    dados_comparacao = []

    for cenario in cenarios:
        # Zera os valores para cada cenário
        valor_vinculo = 0
        valor_qualidade = 0
        valor_emulti = 0

        # Vínculo e Acompanhamento
        for service in vinculo_values:
            if service in selected_services:
                valor_vinculo += vinculo_values[service].get(cenario, 0) * selected_services.get(service, 0)

        # Qualidade
        for service in quality_values:
            if service in selected_services:
                valor_qualidade += quality_values[service].get(cenario, 0) * selected_services.get(service, 0)

        # eMulti
        for service in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
            if selected_services.get(service, 0) > 0:
                valor_emulti += quality_values.get(service, {}).get(cenario, 0) * selected_services.get(service, 0)

        # Calcula o valor total do cenário atual
        valor_cenario = total_fixed_value + valor_vinculo + valor_qualidade + total_implantacao_manutencao_value + total_saude_bucal_value + total_per_capita + valor_emulti

        # Diferença e aumento percentual
        diferenca = valor_cenario - valor_base
        aumento_percentual = (diferenca / valor_base) * 100 if valor_base != 0 else 0.00

        # Adiciona dados para o quadro de comparação
        dados_comparacao.append({
            'Valor Total Atual': format_currency(valor_base),
            'Desempenho': cenario.upper(),  # Convertido para maiúsculas
            'Valor Total do Cenário': format_currency(valor_cenario),
            'Diferença Mensal': format_currency(diferenca),
            'Variação %': aumento_percentual
        })

    # Cria DataFrame para o quadro de comparação
    df_comparacao = pd.DataFrame(dados_comparacao)

    return df_comparacao


def display_detailed_report(total_geral, vinculo_values, quality_values, selected_services, total_implantacao_manutencao_value, total_saude_bucal_value, total_per_capita, total_fixed_value):
    """
    Exibe o relatório detalhado por cenário.
    """
    st.subheader("Relatório Detalhado por Cenário")
    cenarios = ['Regular', 'Suficiente', 'Bom', 'Ótimo']
    cores_cenarios = {
        'Regular': '#8B0000',
        'Suficiente': '#FFA500',
        'Bom': '#006400',
        'Ótimo': '#000080'
    }

    # Definindo valor_base
    valor_base = total_geral

    for cenario in cenarios:
        cor_cenario = cores_cenarios.get(cenario)
        st.markdown(f"<h3 style='color:{cor_cenario}'>Cenário: {cenario}</h3>", unsafe_allow_html=True)

        # Zera os valores para cada cenário
        valor_vinculo = 0
        valor_qualidade = 0
        valor_emulti = 0

        # Vínculo e Acompanhamento
        for service in vinculo_values:
            if service in selected_services:
                valor_vinculo += vinculo_values[service].get(cenario, 0) * selected_services.get(service, 0)

        # Qualidade
        for service in quality_values:
            if service in selected_services:
                valor_qualidade += quality_values[service].get(cenario, 0) * selected_services.get(service, 0)

        # eMulti
        for service in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
            if selected_services.get(service, 0) > 0:
                valor_emulti += quality_values.get(service, {}).get(cenario, 0) * selected_services.get(service, 0)

        # Calcula o valor total do cenário atual
        valor_cenario = total_fixed_value + valor_vinculo + valor_qualidade + total_implantacao_manutencao_value + total_saude_bucal_value + total_per_capita + valor_emulti

        # Diferença e aumento percentual
        diferenca = valor_cenario - valor_base
        aumento_percentual = ((valor_cenario - valor_base) / valor_base) * 100 if valor_base != 0 else 0

        # Cria a tabela para o cenário atual
        tabela_dados = []
        tabela_dados.append({
            'Componente': 'Valor Base (Recebia na APS Mensalmente)',
            'Valor': format_currency(valor_base)
        })
        tabela_dados.append({
            'Componente': 'Valor Fixo',
            'Valor': format_currency(total_fixed_value)
        })
        tabela_dados.append({
            'Componente': 'Vínculo e Acompanhamento',
            'Valor': format_currency(valor_vinculo)
        })
        tabela_dados.append({
            'Componente': 'Qualidade',
            'Valor': format_currency(valor_qualidade)
        })
        tabela_dados.append({
            'Componente': 'eMulti',
            'Valor': format_currency(valor_emulti)
        })
        tabela_dados.append({
            'Componente': 'Implantação/Manutenção',
            'Valor': format_currency(total_implantacao_manutencao_value)
        })
        tabela_dados.append({
            'Componente': 'Saúde Bucal',
            'Valor': format_currency(total_saude_bucal_value)
        })
        tabela_dados.append({
            'Componente': 'Per Capita',
            'Valor': format_currency(total_per_capita)
        })
        tabela_dados.append({
            'Componente': f"<span style='font-weight: bold; color: {cor_cenario}'>Total do Cenário ({cenario})</span>",
            'Valor': f"<span style='font-weight: bold; color: {cor_cenario}'>{format_currency(valor_cenario)}</span>"
        })
        tabela_dados.append({
            'Componente': 'Diferença (Aumentou Mensal)',
            'Valor': format_currency(diferenca)
        })
        tabela_dados.append({
            'Componente': 'Aumento Percentual',
            'Valor': f"{aumento_percentual:.0f}%"
        })

        # Cria DataFrame e exibe a tabela
        df = pd.DataFrame(tabela_dados)

        # Formatação condicional e remove índice
        st.markdown(df.style.map(lambda x: f"background-color: {cores_cenarios.get(cenario, '')};" if x == cenario else '', subset=['Componente'])
                  .format({'Valor': '{:}'})
                  .set_table_styles([
                      {'selector': 'th', 'props': [('background-color', cor_cenario), ('color', 'white'), ('text-align', 'center'), ('border', '1px solid black'), ('font-weight', 'bold')]},
                      {'selector': 'td', 'props': [('text-align', 'left'), ('border', '1px solid black')]},
                      {'selector': 'td:nth-child(2)', 'props': [('text-align', 'right')]},
                      {'selector': 'tr:last-child td', 'props': [('font-weight', 'bold')]},
                      {'selector': '', 'props': [('border-collapse', 'collapse'), ('width', '80%'), ('margin', '0 auto')]},
                      {'selector': '.col0', 'props': [('width', '450px')]}
                  ])
                  .hide(axis="index")
                  .to_html(escape=False), unsafe_allow_html=True)
        st.divider()


def display_comparison_chart(df_comparacao):
    """Exibe o quadro de comparação de cenários."""
    st.subheader("Quadro de Comparação de Valores Conforme os Cenários de Qualificação de Desempenho da APS")

    # CSS para a tabela
    st.markdown(
        """
        <style>
        .dataframe {
            width: 100%;
            border-collapse: collapse;
        }
        .dataframe th {
            background-color: #4682B4; /* Azul médio */
            color: white; /* Cabeçalhos em branco */
            text-align: center;
            padding: 8px;
            border: 1px solid black;
            font-weight: bold;
        }
        .dataframe td {
            text-align: center;
            padding: 8px;
            border: 1px solid black;
            font-size: 1.05em;
            color: white; /* Todas as células em branco */
            font-weight: bold; /* Todas as células em negrito */
        }
        .dataframe td:nth-child(1), .dataframe td:nth-child(3), .dataframe td:nth-child(4) {
            font-weight: bold;
        }
        .dataframe td:nth-child(1), .dataframe td:nth-child(4), .dataframe td:nth-child(5) {
            text-align: right; /* Alinha as colunas específicas à direita */
        }
        /* Formatação condicional para a linha inteira baseada no desempenho */
        .optimo {
            background-color: #000080; /* Azul escuro */
        }
        .bom {
            background-color: #006400; /* Verde escuro */
        }
        .suficiente {
            background-color: #FFA500; /* Laranja */
        }
        .regular {
            background-color: #8B0000; /* Vermelho escuro */
        }
        .st-ae { /* Ajusta a altura do header */
            padding-top: 0px !important;
            padding-bottom: 0px !important;
        }
        .st-bf { /* Ajusta a altura das linhas */
            padding-top: 0px !important;
            padding-bottom: 0px !important;
        }
        .st-bb { /* Ajusta a altura das linhas */
            padding-top: 0px !important;
            padding-bottom: 0px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Função para aplicar estilo em toda a linha
    def style_rows(row):
        if row['Desempenho'] == 'ÓTIMO':
            return ['background-color: #000080; color: white'] * len(row)  # Azul escuro
        elif row['Desempenho'] == 'BOM':
            return ['background-color: #006400; color: white'] * len(row)  # Verde escuro
        elif row['Desempenho'] == 'SUFICIENTE':
            return ['background-color: #FFA500; color: white'] * len(row)  # Laranja
        elif row['Desempenho'] == 'REGULAR':
            return ['background-color: #8B0000; color: white'] * len(row)  # Vermelho escuro
        else:
            return [''] * len(row)

    # Função para formatar a Variação %
    def format_variacao_porcentagem(val):
        """Formata a variação percentual com duas casas decimais e símbolo de porcentagem."""
        try:
            if isinstance(val, str):
                # Se for string, tenta converter para float
                num = float(val.replace('%', '').strip())
            elif isinstance(val, (int, float)):
                num = val
            else:
                return val
            return f"{num:.2f}%"
        except ValueError:
            return val  # Retorna o valor original se houver erro na conversão

    # Aplicar estilos ao DataFrame
    styled_df = df_comparacao.style.apply(style_rows, axis=1) \
        .format({'Valor Total Atual': '{:}',
                 'Valor Total do Cenário': '{:}',
                 'Diferença Mensal': '{:}',
                 'Variação %': format_variacao_porcentagem})  # Usando a função de formatação

    st.dataframe(styled_df)
