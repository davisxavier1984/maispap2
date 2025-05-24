"""
Gerador de gráficos para relatórios PDF da Calculadora PAP.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import io
import base64
from matplotlib import rcParams
import streamlit as st
from utils import format_currency, currency_to_float

# Configurar matplotlib para melhor qualidade nos PDFs
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
rcParams['figure.dpi'] = 300
rcParams['savefig.dpi'] = 300
rcParams['savefig.bbox'] = 'tight'

class PAPChartGenerator:
    """Classe para geração de gráficos da Calculadora PAP."""
    
    def __init__(self):
        """Inicializa o gerador de gráficos."""
        self.colors = {
            'primary': '#4682B4',
            'secondary': '#006400',
            'warning': '#FFA500',
            'danger': '#8B0000',
            'success': '#228B22',
            'light_blue': '#F0F8FF',
            'light_green': '#F0FFF0'
        }
        
    def create_components_pie_chart(self, components_data):
        """Cria gráfico de pizza dos componentes PAP."""
        if not components_data or all(v == 0 for v in components_data.values()):
            return None
            
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Filtrar componentes com valores > 0
        filtered_data = {k: v for k, v in components_data.items() if v > 0}
        
        if not filtered_data:
            return None
            
        labels = list(filtered_data.keys())
        values = list(filtered_data.values())
        
        # Cores para cada componente
        colors = [self.colors['primary'], self.colors['secondary'], 
                 self.colors['warning'], self.colors['danger'], 
                 self.colors['success'], '#9370DB'][:len(labels)]
        
        # Criar gráfico de pizza
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=labels, 
            colors=colors,
            autopct=lambda pct: f'{pct:.1f}%\n{format_currency(pct/100 * sum(values))}',
            startangle=90,
            textprops={'fontsize': 10}
        )
        
        # Ajustar textos
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        ax.set_title('Distribuição dos Componentes PAP', fontsize=14, fontweight='bold', pad=20)
        
        # Adicionar legenda
        ax.legend(wedges, [f'{label}: {format_currency(value)}' for label, value in filtered_data.items()],
                 title="Componentes",
                 loc="center left",
                 bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def create_scenarios_comparison_chart(self, scenarios_data):
        """Cria gráfico de comparação de cenários."""
        if not scenarios_data:
            return None
            
        fig, ax = plt.subplots(figsize=(12, 8))
        
        scenarios = list(scenarios_data.keys())
        values = list(scenarios_data.values())
        
        # Cores para cada cenário
        scenario_colors = {
            'Regular': self.colors['danger'],
            'Suficiente': self.colors['warning'],
            'Bom': self.colors['secondary'],
            'Ótimo': self.colors['primary']
        }
        
        colors = [scenario_colors.get(scenario, self.colors['primary']) for scenario in scenarios]
        
        # Criar gráfico de barras
        bars = ax.bar(scenarios, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
        
        # Adicionar valores nas barras
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
                   format_currency(value),
                   ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        ax.set_title('Comparação de Valores por Cenário de Desempenho', fontsize=14, fontweight='bold')
        ax.set_xlabel('Cenários de Desempenho', fontsize=12)
        ax.set_ylabel('Valor Total PAP (R$)', fontsize=12)
        
        # Formatação do eixo Y
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))
        
        # Rotacionar labels do eixo X se necessário
        plt.xticks(rotation=0)
        
        # Grid suave
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def create_services_distribution_chart(self, services_data):
        """Cria gráfico de distribuição de serviços."""
        if not services_data or all(v == 0 for v in services_data.values()):
            return None
            
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Filtrar serviços com quantidade > 0
        filtered_services = {k: v for k, v in services_data.items() if v > 0}
        
        if not filtered_services:
            return None
            
        services = list(filtered_services.keys())
        quantities = list(filtered_services.values())
        
        # Criar gráfico de barras horizontais
        bars = ax.barh(services, quantities, color=self.colors['secondary'], alpha=0.7)
        
        # Adicionar valores nas barras
        for bar, qty in zip(bars, quantities):
            width = bar.get_width()
            ax.text(width + max(quantities)*0.01, bar.get_y() + bar.get_height()/2,
                   str(qty), ha='left', va='center', fontweight='bold')
        
        ax.set_title('Distribuição de Serviços Configurados', fontsize=14, fontweight='bold')
        ax.set_xlabel('Quantidade', fontsize=12)
        ax.set_ylabel('Tipos de Serviços', fontsize=12)
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--', axis='x')
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def create_projection_timeline_chart(self, timeline_data):
        """Cria gráfico de linha temporal de projeções."""
        if not timeline_data:
            return None
            
        fig, ax = plt.subplots(figsize=(12, 8))
        
        months = list(timeline_data.keys())
        values = list(timeline_data.values())
        
        # Criar gráfico de linha
        line = ax.plot(months, values, marker='o', linewidth=3, 
                      markersize=8, color=self.colors['primary'], 
                      markerfacecolor=self.colors['secondary'],
                      markeredgecolor='white', markeredgewidth=2)
        
        # Adicionar área sob a curva
        ax.fill_between(months, values, alpha=0.2, color=self.colors['primary'])
        
        # Adicionar valores nos pontos
        for i, (month, value) in enumerate(zip(months, values)):
            ax.annotate(format_currency(value), (i, value), 
                       textcoords="offset points", xytext=(0,10), 
                       ha='center', fontweight='bold', fontsize=9)
        
        ax.set_title('Projeção Temporal dos Valores PAP', fontsize=14, fontweight='bold')
        ax.set_xlabel('Período', fontsize=12)
        ax.set_ylabel('Valor PAP (R$)', fontsize=12)
        
        # Formatação do eixo Y
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: format_currency(x)))
        
        # Rotacionar labels do eixo X
        plt.xticks(rotation=45)
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def create_performance_radar_chart(self, performance_data):
        """Cria gráfico radar de desempenho."""
        if not performance_data:
            return None
            
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        categories = list(performance_data.keys())
        values = list(performance_data.values())
        
        # Normalizar valores para escala 0-100
        max_value = max(values) if values else 1
        normalized_values = [v/max_value * 100 for v in values]
        
        # Ângulos para cada categoria
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        
        # Fechar o polígono
        normalized_values += normalized_values[:1]
        angles += angles[:1]
        
        # Plotar
        ax.plot(angles, normalized_values, 'o-', linewidth=2, color=self.colors['primary'])
        ax.fill(angles, normalized_values, alpha=0.25, color=self.colors['primary'])
        
        # Adicionar labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=10)
        
        # Configurar escala radial
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=8)
        
        ax.set_title('Radar de Desempenho dos Componentes', fontsize=14, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig):
        """Converte figura matplotlib para base64."""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        return image_base64
    
    def create_summary_dashboard(self, summary_data):
        """Cria dashboard resumo com múltiplos gráficos."""
        if not summary_data:
            return None
            
        fig = plt.figure(figsize=(16, 12))
        
        # Layout 2x2
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Gráfico 1: Pizza de componentes
        ax1 = fig.add_subplot(gs[0, 0])
        if 'components' in summary_data:
            self._add_pie_subplot(ax1, summary_data['components'], 'Distribuição dos Componentes')
        
        # Gráfico 2: Barras de cenários
        ax2 = fig.add_subplot(gs[0, 1])
        if 'scenarios' in summary_data:
            self._add_bar_subplot(ax2, summary_data['scenarios'], 'Cenários de Desempenho')
        
        # Gráfico 3: Serviços
        ax3 = fig.add_subplot(gs[1, 0])
        if 'services' in summary_data:
            self._add_horizontal_bar_subplot(ax3, summary_data['services'], 'Serviços Configurados')
        
        # Gráfico 4: Resumo financeiro
        ax4 = fig.add_subplot(gs[1, 1])
        if 'financial' in summary_data:
            self._add_financial_summary(ax4, summary_data['financial'])
        
        fig.suptitle('Dashboard Resumo - Calculadora PAP', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        return self._fig_to_base64(fig)
    
    def _add_pie_subplot(self, ax, data, title):
        """Adiciona gráfico de pizza em subplot."""
        filtered_data = {k: v for k, v in data.items() if v > 0}
        if filtered_data:
            ax.pie(filtered_data.values(), labels=filtered_data.keys(), autopct='%1.1f%%', 
                  startangle=90, textprops={'fontsize': 8})
        ax.set_title(title, fontsize=10, fontweight='bold')
    
    def _add_bar_subplot(self, ax, data, title):
        """Adiciona gráfico de barras em subplot."""
        if data:
            bars = ax.bar(data.keys(), data.values(), color=self.colors['secondary'], alpha=0.7)
            for bar, value in zip(bars, data.values()):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       format_currency(value), ha='center', va='bottom', fontsize=8)
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.tick_params(axis='x', rotation=45, labelsize=8)
    
    def _add_horizontal_bar_subplot(self, ax, data, title):
        """Adiciona gráfico de barras horizontais em subplot."""
        filtered_data = {k: v for k, v in data.items() if v > 0}
        if filtered_data:
            ax.barh(list(filtered_data.keys()), list(filtered_data.values()), 
                   color=self.colors['primary'], alpha=0.7)
        ax.set_title(title, fontsize=10, fontweight='bold')
        ax.tick_params(labelsize=8)
    
    def _add_financial_summary(self, ax, data):
        """Adiciona resumo financeiro visual."""
        ax.axis('off')
        
        # Criar boxes com informações financeiras
        y_positions = [0.8, 0.6, 0.4, 0.2]
        colors = [self.colors['primary'], self.colors['secondary'], 
                 self.colors['warning'], self.colors['success']]
        
        for i, (key, value) in enumerate(data.items()):
            if i < len(y_positions):
                # Box colorido
                rect = patches.Rectangle((0.1, y_positions[i]-0.05), 0.8, 0.1, 
                                       linewidth=1, edgecolor='black', 
                                       facecolor=colors[i % len(colors)], alpha=0.3)
                ax.add_patch(rect)
                
                # Texto
                ax.text(0.15, y_positions[i], key, fontsize=10, fontweight='bold', va='center')
                ax.text(0.85, y_positions[i], format_currency(value), 
                       fontsize=10, fontweight='bold', va='center', ha='right')
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_title('Resumo Financeiro', fontsize=10, fontweight='bold')

def generate_chart_for_pdf(chart_type, data):
    """Função utilitária para gerar gráficos para PDF."""
    try:
        generator = PAPChartGenerator()
        
        if chart_type == 'components_pie':
            return generator.create_components_pie_chart(data)
        elif chart_type == 'scenarios_comparison':
            return generator.create_scenarios_comparison_chart(data)
        elif chart_type == 'services_distribution':
            return generator.create_services_distribution_chart(data)
        elif chart_type == 'projection_timeline':
            return generator.create_projection_timeline_chart(data)
        elif chart_type == 'performance_radar':
            return generator.create_performance_radar_chart(data)
        elif chart_type == 'summary_dashboard':
            return generator.create_summary_dashboard(data)
        else:
            return None
            
    except Exception as e:
        st.error(f"Erro ao gerar gráfico {chart_type}: {str(e)}")
        return None
