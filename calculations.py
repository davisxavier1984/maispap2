"""
Módulo para cálculos da Calculadora PAP.
"""
import streamlit as st
import pandas as pd
import json
# Importando as funções utilitárias do pacote utils
from utils import currency_to_float, format_currency

# Importações de componentes após as funções utilitárias
from components.scenarios_analysis import display_scenarios_analysis
from components.scenarios_report import gerar_relatorio_cenarios, display_comparison_chart, display_detailed_report
from components.resource_projection import display_resource_projection

# Constantes para valores de vínculo e acompanhamento territorial
VINCULO_VALUES = {
    'eSF': {'Ótimo': 8000, 'Bom': 6000, 'Suficiente': 4000, 'Regular': 2000},
    'eAP 30h': {'Ótimo': 4000, 'Bom': 3000, 'Suficiente': 2000, 'Regular': 1000},
    'eAP 20h': {'Ótimo': 3000, 'Bom': 2250, 'Suficiente': 1500, 'Regular': 750},
}

# Carregando os valores de qualidade do config.json
try:
    with open("config.json", "r", encoding="utf-8") as f:
        CONFIG_DATA = json.load(f)
        QUALITY_VALUES = CONFIG_DATA.get("quality_values", {})
except (FileNotFoundError, json.JSONDecodeError) as e:
    st.error(f"Erro ao carregar config.json: {e}")
    QUALITY_VALUES = {}

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

def calculate_fixed_component(selected_services, edited_values, edited_implantacao_quantity, edited_implantacao_values, config_data):
    """Calcula o componente fixo."""
    fixed_component_values = config_data["fixed_component_values"]
    implantacao_values = config_data["implantacao_values"]
    data = config_data["data"]
    
    fixed_table = []
    
    # Construindo a tabela do componente fixo
    for service in ["eSF", "eAP 30h", "eAP 20h", "eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
        quantity = selected_services.get(service, 0)
        if quantity > 0:
            # Buscar valor do config.json ou fixed_component_values
            if service in ["eSF", "eAP 30h", "eAP 20h"]:
                # Obter o IED da session_state
                ied = st.session_state.get('ied', None)
                estrato = get_estrato(ied)

                if estrato in fixed_component_values:
                    valor = currency_to_float(fixed_component_values[estrato][service])
                else:
                    valor = 0
            elif service in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
                try:
                    valor = currency_to_float(data[service]['valor'])
                except (ValueError, KeyError):
                    st.error(f"Valor inválido para {service} no config.json.")
                    valor = 0
            else:
                valor = 0

            # Verifica se o valor foi editado
            if service in edited_values:
                valor = edited_values[service]

            total_value = valor * quantity
            fixed_table.append([service, format_currency(valor), quantity, format_currency(total_value)])
    
    # Adicionar linhas para implantação de eSF, eAP, eMulti
    for service in ["eSF", "eAP 30h", "eAP 20h", "eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
        if selected_services.get(service, 0) > 0:
            if service in edited_implantacao_values:
                valor_implantacao = edited_implantacao_values[service]
            else:
                if service in implantacao_values:
                    valor_implantacao = currency_to_float(implantacao_values.get(service, "R$ 0,00"))
                elif service == "eMULTI Ampl.":
                    valor_implantacao = currency_to_float(implantacao_values.get("eMulti Ampliada", "R$ 0,00"))
                elif service == "eMULTI Compl.":
                    valor_implantacao = currency_to_float(implantacao_values.get("eMulti Complementar", "R$ 0,00"))
                elif service == "eMULTI Estrat.":
                    valor_implantacao = currency_to_float(implantacao_values.get("eMulti Estratégica", "R$ 0,00"))
                else:
                    valor_implantacao = 0

            if service in edited_implantacao_quantity:
                quantity_implantacao = edited_implantacao_quantity[service]
            else:
                quantity_implantacao = 0

            total_implantacao = valor_implantacao * quantity_implantacao
            fixed_table.append([f"{service} (Implantação)", format_currency(valor_implantacao), quantity_implantacao, format_currency(total_implantacao)])
    
    fixed_df = pd.DataFrame(fixed_table, columns=['Serviço', 'Valor Unitário', 'Quantidade', 'Valor Total'])
    
    # Calcular o total
    total_fixed_value = sum(
        currency_to_float(val)
        for val in fixed_df['Valor Total']
    )
    
    # Adicionar linha de total à tabela
    total_fixed_row = pd.DataFrame({
        'Serviço': ['Total'],
        'Valor Unitário': [''],
        'Quantidade': [''],
        'Valor Total': [format_currency(total_fixed_value)]
    })
    fixed_df = pd.concat([fixed_df, total_fixed_row], ignore_index=True)
    
    return fixed_df, total_fixed_value

def calculate_vinculo_component(selected_services, edited_values, vinculo):
    """Calcula o componente de vínculo e acompanhamento territorial."""
    # Utilizando a constante global VINCULO_VALUES diretamente
    vinculo_table = []
    
    # Construindo a tabela de vínculo e acompanhamento
    for service, quality_levels in VINCULO_VALUES.items():
        if vinculo in quality_levels:
            quantity = selected_services.get(service, 0)
            if quantity > 0:
                # Verificar se o valor foi editado
                if service in edited_values:
                    value = edited_values[service]
                else:
                    value = quality_levels[vinculo]
                total_value = value * quantity
                vinculo_table.append([service, vinculo, format_currency(value), quantity, format_currency(total_value)])
    
    vinculo_df = pd.DataFrame(vinculo_table, columns=['Serviço', 'Qualidade', 'Valor Unitário', 'Quantidade', 'Valor Total'])
    
    # Calcular o total
    total_vinculo_value = sum(
        currency_to_float(val)
        for val in vinculo_df['Valor Total']
    )
    
    # Adicionar linha de total à tabela
    total_vinculo_row = pd.DataFrame({
        'Serviço': ['Total'],
        'Qualidade': [''],
        'Valor Unitário': [''],
        'Quantidade': [''],
        'Valor Total': [format_currency(total_vinculo_value)]
    })
    vinculo_df = pd.concat([vinculo_df, total_vinculo_row], ignore_index=True)
    
    return vinculo_df, total_vinculo_value

def calculate_quality_component(selected_services, edited_values, classificacao, config_data):
    """Calcula o componente de qualidade."""
    # Utilizando a constante global QUALITY_VALUES para consistência
    # Mas permitindo fallback para config_data caso necessário
    quality_values = QUALITY_VALUES if QUALITY_VALUES else config_data.get("quality_values", {})
    
    quality_table = []
    
    # Construindo a tabela de qualidade
    for service, quality_levels in quality_values.items():
        if classificacao in quality_levels:
            quantity = selected_services.get(service, 0)
            if quantity > 0:
                # Verificar se o valor foi editado
                if service in edited_values:
                    value = edited_values[service]
                else:
                    value = quality_levels[classificacao]
                    
                total_value = value * quantity
                quality_table.append([service, classificacao, format_currency(value), quantity, format_currency(total_value)])
    
    quality_df = pd.DataFrame(quality_table, columns=['Serviço', 'Qualidade', 'Valor Unitário', 'Quantidade', 'Valor Total'])
    
    # Calcular o total
    total_quality_value = sum(
        currency_to_float(val)
        for val in quality_df['Valor Total']
    )
    
    # Adicionar linha de total à tabela
    total_quality_row = pd.DataFrame({
        'Serviço': ['Total'],
        'Qualidade': [''],
        'Valor Unitário': [''],
        'Quantidade': [''],
        'Valor Total': [format_currency(total_quality_value)]
    })
    quality_df = pd.concat([quality_df, total_quality_row], ignore_index=True)
    
    return quality_df, total_quality_value

def calculate_implantacao_manutencao(selected_services, edited_values, config_data):
    """Calcula o componente para implantação e manutenção de programas."""
    data = config_data["data"]
    updated_categories = config_data["updated_categories"]
    
    implantacao_manutencao_table = []
    
    # Todos os serviços que não estão em quality_values, têm valor em data e não são da Saúde Bucal
    implantacao_manutencao_services = [
        service for service in data
        if service not in config_data["quality_values"]
        and data[service]['valor'] != 'Sem cálculo'
        and service not in updated_categories.get('Saúde Bucal', [])
    ]
    
    for service in implantacao_manutencao_services:
        quantity = selected_services.get(service, 0)
        if quantity > 0:
            # Buscar valor unitário de config.json
            try:
                valor = currency_to_float(data[service]['valor'])
            except (ValueError, KeyError):
                st.error(f"Valor inválido para {service} no config.json.")
                valor = 0

            # Verifica se o valor foi editado
            if service in edited_values:
                valor = edited_values[service]

            total = valor * quantity
            implantacao_manutencao_table.append([service, quantity, format_currency(valor), format_currency(total)])
    
    implantacao_manutencao_df = pd.DataFrame(implantacao_manutencao_table, columns=['Serviço', 'Quantidade', 'Valor Unitário', 'Valor Total'])
    
    # Calcular o total
    total_implantacao_manutencao_value = sum(
        currency_to_float(val)
        for val in implantacao_manutencao_df['Valor Total']
    )
    
    # Adicionar linha de total à tabela
    total_implantacao_manutencao_row = pd.DataFrame({
        'Serviço': ['Subtotal'],
        'Quantidade': [''],
        'Valor Unitário': [''],
        'Valor Total': [format_currency(total_implantacao_manutencao_value)]
    })
    implantacao_manutencao_df = pd.concat([implantacao_manutencao_df, total_implantacao_manutencao_row], ignore_index=True)
    
    return implantacao_manutencao_df, total_implantacao_manutencao_value

def calculate_saude_bucal_component(selected_services, edited_values, config_data):
    """Calcula o componente para atenção à saúde bucal."""
    data = config_data["data"]
    updated_categories = config_data["updated_categories"]
    
    saude_bucal_table = []
    
    # Adiciona as linhas de serviços da Saúde Bucal
    saude_bucal_services = updated_categories.get('Saúde Bucal', [])
    
    for service in saude_bucal_services:
        quantity = selected_services.get(service, 0)
        if quantity > 0:
            try:
                # Usar somente os valores de data[service]['valor'], nunca quality_values
                valor = currency_to_float(data[service]['valor'])
            except (ValueError, KeyError) as e:
                st.error(f"Erro ao obter valor para {service}: {e}")
                valor = 0
            
            # Verifica se o valor foi editado pelo usuário
            if service in edited_values:
                valor = edited_values[service]
            
            total = valor * quantity
            saude_bucal_table.append([service, quantity, format_currency(valor), format_currency(total)])
    
    saude_bucal_df = pd.DataFrame(saude_bucal_table, columns=['Serviço', 'Quantidade', 'Valor Unitário', 'Valor Total'])
    
    # Preencher valores vazios na coluna 'Quantidade' com 0
    saude_bucal_df['Quantidade'] = saude_bucal_df['Quantidade'].replace('', 0)
    
    # Calcular o total
    total_saude_bucal_value = sum(
        currency_to_float(val)
        for val in saude_bucal_df['Valor Total'].tolist()
    )
    
    # Adicionar linha de total à tabela
    total_saude_bucal_row = pd.DataFrame({
        'Serviço': ['Subtotal'],
        'Quantidade': [''],
        'Valor Unitário': [''],
        'Valor Total': [format_currency(total_saude_bucal_value)]
    })
    saude_bucal_df = pd.concat([saude_bucal_df, total_saude_bucal_row], ignore_index=True)
    
    return saude_bucal_df, total_saude_bucal_value

def calculate_per_capita():
    """Calcula o componente per capita."""
    populacao = st.session_state.get('populacao', 0)
    valor_per_capita = 5.95
    total_per_capita = (valor_per_capita * populacao) / 12
    
    per_capita_df = pd.DataFrame({
        'Descrição': ['Valor per capita', 'População', 'Total Per Capita (Mensal)'],
        'Valor': [format_currency(valor_per_capita), populacao, format_currency(total_per_capita)]
    })
    
    return per_capita_df, total_per_capita

def calculate_results(selected_services, edited_values, edited_implantacao_values, edited_implantacao_quantity, classificacao, vinculo):
    """Calcula e exibe os resultados."""
    # Utilizar os dados já carregados globalmente para evitar múltiplas leituras do mesmo arquivo
    try:
        config_data = CONFIG_DATA.copy() if CONFIG_DATA else {}
        
        # Se CONFIG_DATA estiver vazio, tentar carregar novamente
        if not config_data:
            st.warning("Tentando carregar config.json novamente...")
            with open("config.json", "r", encoding="utf-8") as f:
                config_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, AttributeError) as e:
        st.error(f"Erro ao carregar config.json: {e}")
        config_data = {"quality_values": {}, "data": {}, "updated_categories": {}, "fixed_component_values": {}, "implantacao_values": {}}
    
    st.header('Valores PAP')
    
    # COMPONENTE 01 - COMPONENTE FIXO
    st.subheader("Componente I - Componente Fixo")
    fixed_df, total_fixed_value = calculate_fixed_component(
        selected_services, edited_values, edited_implantacao_quantity, edited_implantacao_values, config_data
    )
    st.table(fixed_df)
    
    # COMPONENTE 02 - VÍNCULO E ACOMPANHAMENTO TERRITORIAL
    st.subheader("Componente II - Vínculo e Acompanhamento Territorial")
    vinculo_df, total_vinculo_value = calculate_vinculo_component(selected_services, edited_values, vinculo)
    st.table(vinculo_df)
    
    # COMPONENTE 03 - QUALIDADE
    st.subheader("Componente III - Qualidade")
    quality_df, total_quality_value = calculate_quality_component(selected_services, edited_values, classificacao, config_data)
    st.table(quality_df)
    
    # IV - COMPONENTE PARA IMPLANTAÇÃO E MANUTENÇÃO DE PROGRAMAS
    st.subheader("IV - Componente para Implantação e Manutenção de Programas, Serviços, Profissionais e Outras Composições de Equipes")
    implantacao_manutencao_df, total_implantacao_manutencao_value = calculate_implantacao_manutencao(selected_services, edited_values, config_data)
    st.table(implantacao_manutencao_df)
    
    # V - COMPONENTE PARA ATENÇÃO À SAÚDE BUCAL
    st.subheader("V - Componente para Atenção à Saúde Bucal")
    saude_bucal_df, total_saude_bucal_value = calculate_saude_bucal_component(selected_services, edited_values, config_data)
    st.table(saude_bucal_df)
    
    # COMPONENTE PER CAPITA
    st.subheader("VI - Componente Per Capita (Cálculo Simplificado)")
    per_capita_df, total_per_capita = calculate_per_capita()
    st.table(per_capita_df)
    
    # CÁLCULO DO TOTAL GERAL
    total_geral = (total_fixed_value + total_vinculo_value + total_quality_value + 
                  total_implantacao_manutencao_value + total_saude_bucal_value + total_per_capita)
    
    # CÁLCULO DO INCENTIVO FINANCEIRO DA APS - ESF E EAP
    total_incentivo_aps = total_fixed_value + total_quality_value + total_vinculo_value
    
    # Adicionando implantações ao cálculo do incentivo financeiro da APS
    for service in ["eSF", "eAP 30h", "eAP 20h"]:
        if service in selected_services:
            quantity_implantacao = edited_implantacao_quantity.get(service, 0)
            if quantity_implantacao > 0:
                valor_implantacao = edited_implantacao_values.get(service, 0)
                if valor_implantacao == 0:  # Se não foi editado, tenta pegar do config.json
                    try:
                        implantacao_values = config_data.get("implantacao_values", {})
                        valor_implantacao_str = implantacao_values.get(service, "R$ 0,00")
                        valor_implantacao = currency_to_float(valor_implantacao_str)
                    except (ValueError, KeyError):
                        valor_implantacao = 0
                total_incentivo_aps += valor_implantacao * quantity_implantacao
    
    # CÁLCULO DO INCENTIVO FINANCEIRO DA APS - EMULTI
    total_incentivo_emulti = 0
    for service in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
        quantity = selected_services.get(service, 0)
        if quantity > 0:
            try:
                # Valor de custeio mensal
                valor = currency_to_float(config_data["data"][service]['valor'])
                if service in edited_values:
                    valor = edited_values[service]
                    
                # Valor de qualidade
                valor_qualidade = 0
                if service in config_data["quality_values"]:
                    valor_qualidade = config_data["quality_values"][service].get(classificacao, 0)
                
                # Valor de implantação
                quantity_implantacao = edited_implantacao_quantity.get(service, 0)
                valor_implantacao = 0
                if quantity_implantacao > 0:
                    if service in edited_implantacao_values:
                        valor_implantacao = edited_implantacao_values[service]
                    else:
                        implantacao_key = ""
                        if service == "eMULTI Ampl.":
                            implantacao_key = "eMulti Ampliada"
                        elif service == "eMULTI Compl.":
                            implantacao_key = "eMulti Complementar"
                        elif service == "eMULTI Estrat.":
                            implantacao_key = "eMulti Estratégica"
                        
                        if implantacao_key:
                            try:
                                valor_implantacao_str = config_data["implantacao_values"].get(implantacao_key, "R$ 0,00")
                                valor_implantacao = currency_to_float(valor_implantacao_str)
                            except (ValueError, KeyError):
                                valor_implantacao = 0

                # Soma tudo
                total_incentivo_emulti += valor * quantity  # Custeio mensal
                total_incentivo_emulti += valor_qualidade * quantity  # Qualidade
                total_incentivo_emulti += valor_implantacao * quantity_implantacao  # Implantação
                
            except (KeyError, ValueError) as e:
                st.warning(f"Erro no cálculo para {service}: {e}")
    
    # Exibir resumo final
    st.subheader("Resumo do Cálculo PAP")
    resumo_df = pd.DataFrame({
        'Componente': [
            'Incentivo Financeiro da APS - eSF ou eAP', 
            'Incentivo Financeiro da APS - eMulti',
            'Incentivo Financeiro para Atenção à Saúde Bucal',
            'Componente Per Capita',
            'Componente para Implantação e Manutenção',
            'Total Adicional',
            'TOTAL PAP'
        ],
        'Valor': [
            format_currency(total_incentivo_aps),
            format_currency(total_incentivo_emulti),
            format_currency(total_saude_bucal_value),
            format_currency(total_per_capita),
            format_currency(total_implantacao_manutencao_value),
            format_currency(st.session_state.get('valor_esf_eap', 0.0) + st.session_state.get('valor_saude_bucal', 0.0) +
                           st.session_state.get('valor_acs', 0.0) + st.session_state.get('valor_estrategicas', 0.0)),
            format_currency(total_geral + st.session_state.get('valor_esf_eap', 0.0) + st.session_state.get('valor_saude_bucal', 0.0) + 
                          st.session_state.get('valor_acs', 0.0) + st.session_state.get('valor_estrategicas', 0.0))
        ]
    })
    
    # Estilizar o dataframe para destacar o total
    st.table(resumo_df.style.apply(lambda x: ['font-weight: bold' if i == len(resumo_df)-1 else '' for i in range(len(resumo_df))], axis=0))
    
    # Marcar que o cálculo foi realizado
    st.session_state['calculo_realizado'] = True
    
    # Exibir análise de cenários
    display_scenarios_analysis(total_incentivo_aps, total_incentivo_emulti, total_geral, VINCULO_VALUES, QUALITY_VALUES, 
                              selected_services, total_fixed_value, total_implantacao_manutencao_value, 
                              total_saude_bucal_value, total_per_capita)
    
    # Gerar e exibir quadro de comparação
    df_comparacao = gerar_relatorio_cenarios(total_geral, VINCULO_VALUES, QUALITY_VALUES, selected_services, 
                                            total_implantacao_manutencao_value, total_saude_bucal_value, 
                                            total_per_capita, total_fixed_value)
    display_comparison_chart(df_comparacao)
    
    # Exibir relatório detalhado por cenário
    display_detailed_report(total_geral, VINCULO_VALUES, QUALITY_VALUES, selected_services,
                           total_implantacao_manutencao_value, total_saude_bucal_value, 
                           total_per_capita, total_fixed_value)
    
    # Exibir projeção de recursos
    display_resource_projection(VINCULO_VALUES, QUALITY_VALUES, selected_services, 
                               total_fixed_value, total_implantacao_manutencao_value,
                               total_saude_bucal_value, total_per_capita)
