"""
Interface principal de cálculos da Calculadora PAP.

Este módulo contém a interface refatorada para os cálculos do PAP.
"""

import streamlit as st
import pandas as pd
from typing import Dict, Optional
from .state_manager import StateManager
from .calculations import PAPCalculator
from .models import ServiceSelection, MunicipioData, ConfigManager
from .validators import DataValidator, BusinessRuleValidator
from utils.formatting import format_currency


class CalculationInterface:
    """Interface principal para cálculos do PAP."""
    
    def __init__(self):
        self.state_manager = StateManager()
        self.calculator = PAPCalculator()
        self.config = ConfigManager()
        
    def render_calculation_section(self):
        """Renderiza a seção completa de cálculos."""
        # Inicializar estado
        self.state_manager.initialize_state()
        
        # Verificar pré-requisitos
        if not self._validate_prerequisites():
            return
        
        # Renderizar interface de seleção de serviços
        self._render_service_selection()
        
        # Renderizar parâmetros adicionais
        self._render_additional_parameters()
        
        # Renderizar controles de cálculo
        self._render_calculation_controls()
        
        # Renderizar resultados se disponíveis
        if self.state_manager.get_state_value('calculo_realizado', False):
            self._render_results()
    
    def _validate_prerequisites(self) -> bool:
        """Valida se os pré-requisitos estão atendidos."""
        municipio_data = self.state_manager.get_municipio_data()
        
        if not municipio_data:
            st.warning("📍 **Selecione um município primeiro**")
            st.info("Use a página anterior para selecionar UF, município e consultar os dados.")
            return False
        
        # Exibir informações do município selecionado
        with st.expander("ℹ️ Informações do Município", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("UF", municipio_data.uf)
            with col2:
                st.metric("Município", municipio_data.municipio)
            with col3:
                st.metric("População", f"{municipio_data.populacao:,}" if municipio_data.populacao else "N/A")
        
        return True
    
    def _render_service_selection(self):
        """Renderiza a interface de seleção de serviços."""
        st.header("📋 Seleção de Serviços")
        
        # Obter seleção atual ou criar nova
        current_selection = self.state_manager.get_service_selection()
        if not current_selection:
            current_selection = ServiceSelection()
        
        selected_services = {}
        edited_values = {}
        edited_implantacao_values = {}
        edited_implantacao_quantity = {}
        
        # Renderizar por categoria
        for category, services in self.config.updated_categories.items():
            with st.expander(f"📂 {category}"):
                if category == 'Saúde Bucal':
                    self._render_saude_bucal_services(
                        selected_services, edited_values, 
                        edited_implantacao_values, edited_implantacao_quantity
                    )
                else:
                    self._render_category_services(
                        category, services, selected_services, edited_values,
                        edited_implantacao_values, edited_implantacao_quantity
                    )
        
        # Atualizar seleção no estado
        updated_selection = ServiceSelection(
            services=selected_services,
            edited_values=edited_values,
            edited_implantacao_values=edited_implantacao_values,
            edited_implantacao_quantity=edited_implantacao_quantity
        )
        
        self.state_manager.set_service_selection(updated_selection)
        
        # Mostrar resumo dos serviços selecionados
        self._render_service_summary(updated_selection)
    
    def _render_saude_bucal_services(self, selected_services, edited_values, 
                                   edited_implantacao_values, edited_implantacao_quantity):
        """Renderiza serviços de saúde bucal por subcategoria."""
        for subcategory, sub_services in self.config.subcategories.items():
            st.markdown(f"##### {subcategory}")
            
            for service in sub_services:
                self._render_service_row(
                    service, f"SB_{subcategory}", selected_services, edited_values,
                    edited_implantacao_values, edited_implantacao_quantity
                )
    
    def _render_category_services(self, category, services, selected_services, edited_values,
                                edited_implantacao_values, edited_implantacao_quantity):
        """Renderiza serviços de uma categoria normal."""
        for service in services:
            self._render_service_row(
                service, category, selected_services, edited_values,
                edited_implantacao_values, edited_implantacao_quantity
            )
            
            # Renderizar campos de implantação para serviços específicos
            if service in ["eSF", "eAP 30h", "eAP 20h", "eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
                self._render_implantacao_row(
                    service, category, edited_implantacao_values, edited_implantacao_quantity
                )
    
    def _render_service_row(self, service, category, selected_services, edited_values,
                          edited_implantacao_values, edited_implantacao_quantity):
        """Renderiza uma linha de serviço."""
        unique_key = f"{category}_{service}"
        unique_key_value = f"{category}_{service}_value"
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            quantity = st.number_input(
                f'{service} (Quantidade)', 
                min_value=0, 
                value=0, 
                key=unique_key
            )
            selected_services[service] = quantity
        
        with col2:
            initial_value = self._get_initial_service_value(service)
            value = st.text_input(
                f"Valor {service}", 
                value=initial_value, 
                key=unique_key_value
            )
            
            # Processar valor editado
            if value != initial_value:
                try:
                    edited_values[service] = float(
                        value.replace('R$ ', '').replace('.', '').replace(',', '.')
                    )
                except ValueError:
                    st.error(f"Valor inválido para {service}")
                    edited_values[service] = 0.0
        
        with col3:
            total_value = self._calculate_service_total(value, quantity)
            st.text_input(
                f"Subtotal {service}", 
                value=format_currency(total_value), 
                key=f"{unique_key}_total",
                disabled=True
            )
    
    def _render_implantacao_row(self, service, category, edited_implantacao_values, edited_implantacao_quantity):
        """Renderiza linha de implantação para um serviço."""
        key_q = f"{category}_{service}_implantacao_quantidade"
        key_v = f"{category}_{service}_implantacao_valor"
        key_s = f"{category}_{service}_implantacao_subtotal"
        
        st.markdown(f"###### Implantação - {service}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            quantity_implantacao = st.number_input(
                f'Quantidade Implantação', 
                min_value=0, 
                value=0,
                key=key_q
            )
            edited_implantacao_quantity[service] = quantity_implantacao
        
        with col2:
            initial_implantacao_value = self._get_initial_implantacao_value(service)
            implantacao_value = st.text_input(
                f"Valor Implantação", 
                value=initial_implantacao_value,
                key=key_v
            )
            
            if implantacao_value != initial_implantacao_value:
                try:
                    edited_implantacao_values[service] = float(
                        implantacao_value.replace('R$ ', '').replace('.', '').replace(',', '.')
                    )
                except ValueError:
                    st.error(f"Valor de implantação inválido para {service}")
                    edited_implantacao_values[service] = 0.0
        
        with col3:
            total_implantacao = self._calculate_service_total(implantacao_value, quantity_implantacao)
            st.text_input(
                f"Subtotal Implantação", 
                value=format_currency(total_implantacao),
                key=key_s, 
                disabled=True
            )
    
    def _get_initial_service_value(self, service: str) -> str:
        """Obtém o valor inicial de um serviço."""
        if service in ["eSF", "eAP 30h", "eAP 20h"]:
            municipio_data = self.state_manager.get_municipio_data()
            if municipio_data and municipio_data.ied:
                try:
                    estrato = str(municipio_data.ied)[-1] if isinstance(municipio_data.ied, str) else "1"
                    return self.config.get_fixed_value(service, estrato)
                except:
                    return "R$ 0,00"
        
        service_info = self.config.get_service_info(service)
        if service_info and service_info.get('valor') != 'Sem cálculo':
            return service_info['valor']
        
        return "R$ 0,00"
    
    def _get_initial_implantacao_value(self, service: str) -> str:
        """Obtém o valor inicial de implantação de um serviço."""
        implantacao_values = self.config._config.get("implantacao_values", {})
        
        # Mapeamento para eMulti
        mapping = {
            "eMULTI Ampl.": "eMulti Ampliada",
            "eMULTI Compl.": "eMulti Complementar",
            "eMULTI Estrat.": "eMulti Estratégica"
        }
        
        if service in implantacao_values:
            return implantacao_values[service]
        elif service in mapping and mapping[service] in implantacao_values:
            return implantacao_values[mapping[service]]
        
        return "R$ 0,00"
    
    def _calculate_service_total(self, value_str: str, quantity: int) -> float:
        """Calcula o total de um serviço."""
        if value_str == 'Sem cálculo':
            return 0.0
        
        try:
            value = float(value_str.replace('R$ ', '').replace('.', '').replace(',', '.'))
            return value * quantity
        except ValueError:
            return 0.0
    
    def _render_service_summary(self, service_selection: ServiceSelection):
        """Renderiza resumo dos serviços selecionados."""
        if service_selection.has_services():
            with st.expander("📊 Resumo dos Serviços Selecionados", expanded=False):
                total_services = service_selection.get_total_services()
                st.metric("Total de Serviços", total_services)
                
                # Listar serviços selecionados
                selected = [f"{service}: {qty}" for service, qty in service_selection.services.items() if qty > 0]
                if selected:
                    st.write("**Serviços selecionados:**")
                    for item in selected:
                        st.write(f"• {item}")
    
    def _render_additional_parameters(self):
        """Renderiza parâmetros adicionais."""
        with st.expander("🔧 Parâmetros Adicionais", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                valor_esf_eap = st.number_input(
                    "Incentivo Financeiro da APS eSF ou eAP", 
                    value=self.state_manager.get_state_value('valor_esf_eap', 0.0), 
                    format="%.2f"
                )
                self.state_manager.set_state_value('valor_esf_eap', valor_esf_eap)
                
                valor_saude_bucal = st.number_input(
                    "Incentivo Financeiro para Atenção à Saúde Bucal", 
                    value=self.state_manager.get_state_value('valor_saude_bucal', 0.0), 
                    format="%.2f"
                )
                self.state_manager.set_state_value('valor_saude_bucal', valor_saude_bucal)
            
            with col2:
                valor_acs = st.number_input(
                    "Total ACS", 
                    value=self.state_manager.get_state_value('valor_acs', 0.0), 
                    format="%.2f"
                )
                self.state_manager.set_state_value('valor_acs', valor_acs)
                
                valor_estrategicas = st.number_input(
                    "Ações Estratégicas", 
                    value=self.state_manager.get_state_value('valor_estrategicas', 0.0), 
                    format="%.2f"
                )
                self.state_manager.set_state_value('valor_estrategicas', valor_estrategicas)
            
            # Total adicional
            total_adicional = valor_esf_eap + valor_saude_bucal + valor_acs + valor_estrategicas
            st.markdown(
                f"<p style='text-align: center; font-size: 1.5rem; color: #008080; font-weight: bold'>"
                f"Total Adicional: {format_currency(total_adicional)}</p>", 
                unsafe_allow_html=True
            )
    
    def _render_calculation_controls(self):
        """Renderiza controles de cálculo."""
        st.header("🧮 Configurações de Cálculo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            classificacao = st.selectbox(
                "Considerar Qualidade", 
                options=['Regular', 'Suficiente', 'Bom', 'Ótimo'], 
                index=2
            )
        
        with col2:
            vinculo = st.selectbox(
                "Vínculo e Acompanhamento Territorial", 
                options=['Regular', 'Suficiente', 'Bom', 'Ótimo'], 
                index=2
            )
        
        self.state_manager.set_classification_settings(classificacao, vinculo)
        
        # Botão de cálculo
        if st.button('🚀 Calcular PAP', use_container_width=True, type="primary"):
            self._perform_calculation()
    
    def _perform_calculation(self):
        """Executa os cálculos do PAP."""
        municipio_data = self.state_manager.get_municipio_data()
        service_selection = self.state_manager.get_service_selection()
        classificacao, vinculo = self.state_manager.get_classification_settings()
        
        # Validar entradas
        additional_values = {
            'valor_esf_eap': self.state_manager.get_state_value('valor_esf_eap', 0.0),
            'valor_saude_bucal': self.state_manager.get_state_value('valor_saude_bucal', 0.0),
            'valor_acs': self.state_manager.get_state_value('valor_acs', 0.0),
            'valor_estrategicas': self.state_manager.get_state_value('valor_estrategicas', 0.0)
        }
        
        validation_result = DataValidator.validate_all_inputs(
            municipio_data, service_selection, classificacao, vinculo, additional_values
        )
        
        if not validation_result.is_valid:
            DataValidator.display_validation_errors(validation_result.errors)
            return
        
        # Validações de regras de negócio
        business_validation = BusinessRuleValidator.validate_service_combinations(service_selection)
        if not business_validation.is_valid:
            DataValidator.display_validation_errors(business_validation.errors, "Avisos de Regras de Negócio")
        
        # Executar cálculos
        try:
            results = self.calculator.calculate_all_components(
                service_selection=service_selection,
                classificacao=classificacao,
                vinculo=vinculo,
                ied=str(municipio_data.ied),
                populacao=municipio_data.populacao or 0,
                additional_values=additional_values
            )
            
            self.state_manager.set_calculation_results(results)
            st.success("✅ Cálculo realizado com sucesso!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Erro no cálculo: {str(e)}")
    
    def _render_results(self):
        """Renderiza os resultados dos cálculos."""
        results = self.state_manager.get_calculation_results()
        if not results:
            return
        
        st.header("📊 Resultados do Cálculo PAP")
        
        # Métricas principais
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Componente Fixo", format_currency(results.total_fixed_value))
        with col2:
            st.metric("Componente Qualidade", format_currency(results.total_quality_value))
        with col3:
            st.metric("Componente Vínculo", format_currency(results.total_vinculo_value))
        with col4:
            st.metric("Total Geral", format_currency(results.total_geral))
        
        # Tabelas detalhadas
        self._render_detailed_tables(results)
    
    def _render_detailed_tables(self, results):
        """Renderiza tabelas detalhadas dos resultados."""
        tab1, tab2, tab3, tab4 = st.tabs(["Componente Fixo", "Qualidade", "Vínculo", "Outros"])
        
        with tab1:
            if results.fixed_table:
                df = pd.DataFrame(results.fixed_table, columns=['Serviço', 'Valor Unitário', 'Quantidade', 'Valor Total'])
                
                # Adicionar linha de total
                total_row = pd.DataFrame({
                    'Serviço': ['Total'],
                    'Valor Unitário': [''],
                    'Quantidade': [''],
                    'Valor Total': [format_currency(results.total_fixed_value)]
                })
                df = pd.concat([df, total_row], ignore_index=True)
                st.table(df)
        
        with tab2:
            if results.quality_table:
                df = pd.DataFrame(results.quality_table, columns=['Serviço', 'Qualidade', 'Valor Unitário', 'Quantidade', 'Valor Total'])
                
                total_row = pd.DataFrame({
                    'Serviço': ['Total'],
                    'Qualidade': [''],
                    'Valor Unitário': [''],
                    'Quantidade': [''],
                    'Valor Total': [format_currency(results.total_quality_value)]
                })
                df = pd.concat([df, total_row], ignore_index=True)
                st.table(df)
        
        with tab3:
            if results.vinculo_table:
                df = pd.DataFrame(results.vinculo_table, columns=['Serviço', 'Qualidade', 'Valor Unitário', 'Quantidade', 'Valor Total'])
                
                total_row = pd.DataFrame({
                    'Serviço': ['Total'],
                    'Qualidade': [''],
                    'Valor Unitário': [''],
                    'Quantidade': [''],
                    'Valor Total': [format_currency(results.total_vinculo_value)]
                })
                df = pd.concat([df, total_row], ignore_index=True)
                st.table(df)
        
        with tab4:
            st.subheader("Componente Per Capita")
            municipio_data = self.state_manager.get_municipio_data()
            per_capita_df = pd.DataFrame({
                'Descrição': ['Valor per capita', 'População', 'Total Per Capita (Mensal)'],
                'Valor': ['R$ 5,95', municipio_data.populacao or 0, format_currency(results.total_per_capita)]
            })
            st.table(per_capita_df)
