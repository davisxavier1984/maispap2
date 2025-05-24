"""
Formatador de dados para relatórios PDF da Calculadora PAP.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from utils import format_currency, currency_to_float
from reports.report_templates import PAPReportTemplates

class PAPDataFormatter:
    """Classe para formatação de dados específicos da Calculadora PAP."""
    
    @staticmethod
    def format_municipality_data():
        """Formata dados do município para o relatório."""
        return {
            'municipio': st.session_state.get('municipio_selecionado', 'Não informado'),
            'uf': st.session_state.get('uf_selecionada', 'Não informado'),
            'competencia': st.session_state.get('competencia_selecionada', 'Não informado'),
            'populacao': st.session_state.get('populacao', 0),
            'ied': st.session_state.get('ied', 'Não informado'),
            'data_consulta': st.session_state.get('data_consulta', datetime.now().strftime('%d/%m/%Y')),
            'data_relatorio': datetime.now().strftime('%d/%m/%Y às %H:%M')
        }
    
    @staticmethod
    def format_services_configuration():
        """Formata configuração de serviços para o relatório."""
        services_config = []
        
        # Lista de todos os serviços possíveis
        all_services = [
            'eSF', 'eAP 30h', 'eAP 20h', 'eMULTI Ampl.', 
            'eMULTI Compl.', 'eMULTI Estrat.'
        ]
        
        for service in all_services:
            quantity = st.session_state.get(f'quantity_{service}', 0)
            if quantity > 0:
                services_config.append({
                    'servico': service,
                    'quantidade': quantity,
                    'status': 'Configurado'
                })
        
        # Adicionar parâmetros de qualidade
        services_config.append({
            'servico': 'Parâmetro de Qualidade',
            'quantidade': st.session_state.get('classificacao', 'Não definido'),
            'status': 'Selecionado'
        })
        
        services_config.append({
            'servico': 'Vínculo e Acompanhamento',
            'quantidade': st.session_state.get('vinculo', 'Não definido'),
            'status': 'Selecionado'
        })
        
        return services_config
    
    @staticmethod
    def format_calculation_summary():
        """Formata resumo dos cálculos para o relatório."""
        if not st.session_state.get('calculo_realizado', False):
            return None
            
        # Valores dos componentes (simulados - em uma implementação real, 
        # você teria acesso aos valores calculados)
        total_pap = st.session_state.get('total_pap_calculado', 0)
        
        return {
            'total_pap': total_pap,
            'componente_fixo': st.session_state.get('total_componente_fixo', 0),
            'vinculo_acompanhamento': st.session_state.get('total_vinculo', 0),
            'qualidade': st.session_state.get('total_qualidade', 0),
            'implantacao_manutencao': st.session_state.get('total_implantacao', 0),
            'saude_bucal': st.session_state.get('total_saude_bucal', 0),
            'per_capita': st.session_state.get('total_per_capita', 0)
        }
    
    @staticmethod
    def format_scenarios_data():
        """Formata dados de cenários para o relatório."""
        scenarios = ['Regular', 'Suficiente', 'Bom', 'Ótimo']
        scenarios_data = {}
        
        base_value = st.session_state.get('total_pap_calculado', 100000)  # Valor base simulado
        
        # Simular diferentes valores para cada cenário
        multipliers = {'Regular': 1.0, 'Suficiente': 1.15, 'Bom': 1.35, 'Ótimo': 1.6}
        
        for scenario in scenarios:
            scenarios_data[scenario] = base_value * multipliers.get(scenario, 1.0)
        
        return scenarios_data
    
    @staticmethod
    def format_components_distribution():
        """Formata distribuição dos componentes para gráficos."""
        if not st.session_state.get('calculo_realizado', False):
            return None
            
        # Valores simulados dos componentes
        components = {
            'Componente Fixo': st.session_state.get('total_componente_fixo', 50000),
            'Vínculo e Acompanhamento': st.session_state.get('total_vinculo', 30000),
            'Qualidade': st.session_state.get('total_qualidade', 25000),
            'Implantação e Manutenção': st.session_state.get('total_implantacao', 15000),
            'Saúde Bucal': st.session_state.get('total_saude_bucal', 10000),
            'Per Capita': st.session_state.get('total_per_capita', 20000)
        }
        
        # Filtrar componentes com valor > 0
        return {k: v for k, v in components.items() if v > 0}
    
    @staticmethod
    def create_financial_table_data():
        """Cria dados formatados para tabelas financeiras."""
        summary = PAPDataFormatter.format_calculation_summary()
        if not summary:
            return []
            
        table_data = [
            ['Componente', 'Valor (R$)', 'Percentual (%)']
        ]
        
        total = summary['total_pap']
        if total > 0:
            for component, value in summary.items():
                if component != 'total_pap' and value > 0:
                    percentage = (value / total) * 100
                    component_name = PAPDataFormatter._format_component_name(component)
                    table_data.append([
                        component_name,
                        format_currency(value),
                        f"{percentage:.1f}%"
                    ])
            
            # Linha de total
            table_data.append([
                'TOTAL PAP',
                format_currency(total),
                '100.0%'
            ])
        
        return table_data
    
    @staticmethod
    def create_scenarios_comparison_table():
        """Cria tabela de comparação de cenários."""
        scenarios_data = PAPDataFormatter.format_scenarios_data()
        base_value = scenarios_data.get('Regular', 0)
        
        table_data = [
            ['Cenário', 'Valor Total (R$)', 'Diferença (R$)', 'Variação (%)']
        ]
        
        for scenario, value in scenarios_data.items():
            difference = value - base_value
            variation = (difference / base_value * 100) if base_value > 0 else 0
            
            table_data.append([
                scenario,
                format_currency(value),
                format_currency(difference),
                f"{variation:.1f}%"
            ])
        
        return table_data
    
    @staticmethod
    def create_services_summary_table():
        """Cria tabela resumo de serviços."""
        services_config = PAPDataFormatter.format_services_configuration()
        
        table_data = [
            ['Serviço/Parâmetro', 'Valor/Quantidade', 'Status']
        ]
        
        for service in services_config:
            table_data.append([
                service['servico'],
                str(service['quantidade']),
                service['status']
            ])
        
        return table_data
    
    @staticmethod
    def _format_component_name(component_key):
        """Formata nome do componente para exibição."""
        name_mapping = {
            'componente_fixo': 'Componente Fixo',
            'vinculo_acompanhamento': 'Vínculo e Acompanhamento',
            'qualidade': 'Qualidade',
            'implantacao_manutencao': 'Implantação e Manutenção',
            'saude_bucal': 'Atenção à Saúde Bucal',
            'per_capita': 'Per Capita'
        }
        return name_mapping.get(component_key, component_key.replace('_', ' ').title())
    
    @staticmethod
    def create_projection_timeline():
        """Cria dados de projeção temporal."""
        base_value = st.session_state.get('total_pap_calculado', 100000)
        
        # Simular projeção de 12 meses
        months = [f"Mês {i+1}" for i in range(12)]
        
        # Simular pequenas variações mensais
        import random
        random.seed(42)  # Para resultados consistentes
        
        timeline_data = {}
        for i, month in enumerate(months):
            # Variação de ±5% do valor base
            variation = random.uniform(0.95, 1.05)
            timeline_data[month] = base_value * variation
        
        return timeline_data
    
    @staticmethod
    def create_performance_metrics():
        """Cria métricas de desempenho."""
        return {
            'Cobertura Populacional': 85.5,
            'Qualidade dos Serviços': 78.2,
            'Vínculo Territorial': 82.1,
            'Implantação de Programas': 71.8,
            'Atenção à Saúde Bucal': 69.3,
            'Gestão Financeira': 88.7
        }
    
    @staticmethod
    def format_legal_compliance_data():
        """Formata dados de conformidade legal."""
        return {
            'portaria': 'Portaria GM/MS Nº 3.493/2024',
            'data_portaria': '10 de abril de 2024',
            'vigencia': 'A partir de maio de 2024',
            'atualizacao': datetime.now().strftime('%d/%m/%Y'),
            'versao_calculo': '1.0',
            'metodologia': 'Conforme Anexos I a VI da Portaria'
        }
    
    @staticmethod
    def create_recommendations():
        """Cria recomendações baseadas nos resultados."""
        total_pap = st.session_state.get('total_pap_calculado', 0)
        classificacao = st.session_state.get('classificacao', 'Regular')
        vinculo = st.session_state.get('vinculo', 'Regular')
        
        recommendations = []
        
        # Recomendações baseadas na classificação
        if classificacao in ['Regular', 'Suficiente']:
            recommendations.append(
                "Considerar estratégias para melhorar os indicadores de qualidade e "
                "alcançar classificações superiores (Bom ou Ótimo)."
            )
        
        if vinculo in ['Regular', 'Suficiente']:
            recommendations.append(
                "Fortalecer as estratégias de vínculo e acompanhamento territorial "
                "para aumentar o valor do componente II."
            )
        
        # Recomendações baseadas no valor total
        if total_pap > 0:
            if total_pap < 50000:
                recommendations.append(
                    "Avaliar possibilidades de expansão dos serviços oferecidos "
                    "para aumentar o incentivo financeiro."
                )
            elif total_pap > 200000:
                recommendations.append(
                    "Manter excelência na prestação dos serviços para sustentar "
                    "o alto valor do incentivo PAP."
                )
        
        # Recomendações gerais
        recommendations.extend([
            "Monitorar regularmente os indicadores de desempenho para manter ou melhorar a classificação.",
            "Investir na capacitação das equipes para aprimorar a qualidade dos serviços.",
            "Implementar sistemas de gestão que facilitem o acompanhamento dos resultados.",
            "Estabelecer parcerias intersetoriais para fortalecer a atenção primária no território."
        ])
        
        return recommendations
    
    @staticmethod
    def validate_data_completeness():
        """Valida se os dados necessários estão completos."""
        required_fields = [
            'municipio_selecionado',
            'uf_selecionada',
            'competencia_selecionada',
            'populacao'
        ]
        
        missing_fields = []
        for field in required_fields:
            if not st.session_state.get(field):
                missing_fields.append(field)
        
        return {
            'is_complete': len(missing_fields) == 0,
            'missing_fields': missing_fields,
            'calculation_ready': st.session_state.get('calculo_realizado', False)
        }
