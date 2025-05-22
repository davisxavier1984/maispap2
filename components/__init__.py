"""
Pacote de componentes da Calculadora PAP.
"""
from components.resource_projection import display_resource_projection
from components.scenarios_analysis import display_scenarios_analysis
from components.scenarios_report import gerar_relatorio_cenarios, display_detailed_report
from components.services_interface import render_services_interface
# A importação abaixo foi removida pois o arquivo é considerado legado.
# O componente foi substituído pelo sistema de páginas do Streamlit em /pages/01_Projeção_Financeira.py
# from components.financial_projection_page import display_financial_projection_page
