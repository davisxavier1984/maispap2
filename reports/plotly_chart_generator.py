"""
Gerador de gráficos Plotly para relatórios PDF da Calculadora PAP.
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import io
import base64
import streamlit as st
from utils import format_currency

class PAPPlotlyChartGenerator:
    """Classe para geração de gráficos Plotly da Calculadora PAP para PDF."""
    
    def __init__(self):
        """Inicializa o gerador de gráficos Plotly."""
        self.colors = {
            'primary': '#4682B4',
            'secondary': '#006400', 
            'warning': '#FFA500',
            'danger': '#8B0000',
            'success': '#228B22',
            'accent': '#9370DB',
            'info': '#2E86AB',
            'light': '#F0F8FF'
        }
        
        # Paleta de cores moderna para gráficos
        self.color_palette = [
            '#4682B4', '#006400', '#FFA500', '#8B0000', 
            '#228B22', '#9370DB', '#2E86AB', '#FF6B35'
        ]
        
    def create_components_pie_chart(self, components_data):
        """Cria gráfico de pizza dos componentes PAP usando Plotly."""
        if not components_data or all(v == 0 for v in components_data.values()):
            return None
            
        try:
            # Filtrar componentes com valores > 0
            filtered_data = {k: v for k, v in components_data.items() if v > 0}
            
            if not filtered_data:
                return None
            
            # Criar DataFrame
            df = pd.DataFrame(list(filtered_data.items()), columns=['Componente', 'Valor'])
            
            # Criar gráfico de pizza
            fig = px.pie(
                df, 
                values='Valor', 
                names='Componente',
                title='Distribuição dos Componentes PAP',
                color_discrete_sequence=self.color_palette,
                hover_data=['Valor']
            )
            
            # Personalizar o gráfico
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                textfont_size=12,
                marker=dict(line=dict(color='#FFFFFF', width=2)),
                hovertemplate='<b>%{label}</b><br>' +
                            'Valor: %{customdata[0]:,.2f}<br>' +
                            'Percentual: %{percent}<br>' +
                            '<extra></extra>',
                customdata=df[['Valor']].values
            )
            
            fig.update_layout(
                title=dict(
                    text='Distribuição dos Componentes PAP',
                    x=0.5,
                    font=dict(size=16, color=self.colors['primary'])
                ),
                font=dict(size=12),
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05
                ),
                width=800,
                height=600,
                margin=dict(l=50, r=150, t=80, b=50)
            )
            
            return self._fig_to_base64(fig)
            
        except Exception as e:
            print(f"Erro ao criar gráfico de pizza: {str(e)}")
            return None
    
    def create_scenarios_comparison_chart(self, scenarios_data):
        """Cria gráfico de comparação de cenários usando Plotly."""
        if not scenarios_data:
            return None
            
        try:
            # Criar DataFrame
            df = pd.DataFrame(list(scenarios_data.items()), columns=['Cenário', 'Valor'])
            
            # Mapear cores por cenário
            color_map = {
                'Regular': self.colors['danger'],
                'Suficiente': self.colors['warning'],
                'Bom': self.colors['secondary'],
                'Ótimo': self.colors['primary']
            }
            
            # Criar gráfico de barras
            fig = px.bar(
                df,
                x='Cenário',
                y='Valor',
                title='Comparação de Valores por Cenário de Desempenho',
                color='Cenário',
                color_discrete_map=color_map,
                text='Valor'
            )
            
            # Personalizar barras
            fig.update_traces(
                texttemplate='%{text:,.0f}',
                textposition='outside',
                textfont_size=11,
                hovertemplate='<b>%{x}</b><br>' +
                            'Valor: R$ %{y:,.2f}<br>' +
                            '<extra></extra>',
                marker=dict(line=dict(color='#FFFFFF', width=1.5))
            )
            
            # Layout
            fig.update_layout(
                title=dict(
                    text='Comparação de Valores por Cenário de Desempenho',
                    x=0.5,
                    font=dict(size=16, color=self.colors['primary'])
                ),
                xaxis_title='Cenários de Desempenho',
                yaxis_title='Valor Total PAP (R$)',
                font=dict(size=12),
                showlegend=False,
                width=900,
                height=600,
                margin=dict(l=80, r=50, t=80, b=80),
                yaxis=dict(tickformat=',.0f'),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            # Grid suave
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
            
            return self._fig_to_base64(fig)
            
        except Exception as e:
            print(f"Erro ao criar gráfico de cenários: {str(e)}")
            return None
    
    def create_services_distribution_chart(self, services_data):
        """Cria gráfico de distribuição de serviços usando Plotly."""
        if not services_data or all(v == 0 for v in services_data.values()):
            return None
            
        try:
            # Filtrar serviços com quantidade > 0
            filtered_services = {k: v for k, v in services_data.items() if v > 0}
            
            if not filtered_services:
                return None
            
            # Criar DataFrame
            df = pd.DataFrame(list(filtered_services.items()), columns=['Serviço', 'Quantidade'])
            
            # Criar gráfico de barras horizontais
            fig = px.bar(
                df,
                x='Quantidade',
                y='Serviço',
                orientation='h',
                title='Distribuição de Serviços Configurados',
                color='Quantidade',
                color_continuous_scale='viridis',
                text='Quantidade'
            )
            
            # Personalizar
            fig.update_traces(
                texttemplate='%{text}',
                textposition='outside',
                textfont_size=12,
                hovertemplate='<b>%{y}</b><br>' +
                            'Quantidade: %{x}<br>' +
                            '<extra></extra>',
                marker=dict(line=dict(color='#FFFFFF', width=1))
            )
            
            fig.update_layout(
                title=dict(
                    text='Distribuição de Serviços Configurados',
                    x=0.5,
                    font=dict(size=16, color=self.colors['primary'])
                ),
                xaxis_title='Quantidade',
                yaxis_title='Tipos de Serviços',
                font=dict(size=12),
                showlegend=False,
                width=900,
                height=500,
                margin=dict(l=150, r=80, t=80, b=50),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            # Grid
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
            fig.update_yaxes(showgrid=False)
            
            return self._fig_to_base64(fig)
            
        except Exception as e:
            print(f"Erro ao criar gráfico de serviços: {str(e)}")
            return None
    
    def create_projection_timeline_chart(self, timeline_data):
        """Cria gráfico de linha temporal de projeções usando Plotly (replicando a interface)."""
        if not timeline_data:
            return None
            
        try:
            # Preparar dados
            periods = list(timeline_data.keys())
            values = list(timeline_data.values())
            
            # Extrair números dos períodos para ordenação
            period_numbers = [int(p.replace(' meses', '')) for p in periods]
            
            # Criar DataFrame ordenado
            df = pd.DataFrame({
                'Período': periods,
                'Período_num': period_numbers,
                'Valor': values
            }).sort_values('Período_num')
            
            # Criar gráfico
            fig = go.Figure()
            
            # Linha principal
            fig.add_trace(go.Scatter(
                x=df['Período_num'],
                y=df['Valor'],
                mode='lines+markers',
                name='Valor Projetado',
                line=dict(color=self.colors['primary'], width=3),
                marker=dict(size=8, color=self.colors['primary']),
                fill='tonexty',
                fillcolor='rgba(31, 119, 180, 0.2)',
                hovertemplate='<b>%{x} meses</b><br>Valor: R$ %{y:,.2f}<extra></extra>'
            ))
            
            # Linha de tendência
            if len(df) > 1:
                z = np.polyfit(df['Período_num'], df['Valor'], 1)
                p = np.poly1d(z)
                trend_values = p(df['Período_num'])
                
                fig.add_trace(go.Scatter(
                    x=df['Período_num'],
                    y=trend_values,
                    mode='lines',
                    name='Tendência',
                    line=dict(color='red', width=2, dash='dash'),
                    hovertemplate='Tendência: R$ %{y:,.2f}<extra></extra>'
                ))
            
            # Layout (replicando exatamente a interface)
            municipio = st.session_state.get('municipio_selecionado', 'Município')
            fig.update_layout(
                title=f'Evolução da Projeção Financeira - {municipio}',
                xaxis_title="Período (meses)",
                yaxis_title="Valor Projetado (R$)",
                font=dict(size=12),
                height=500,
                hovermode='x unified',
                yaxis=dict(tickformat=',.0f'),
                xaxis=dict(
                    tickmode='array', 
                    tickvals=df['Período_num'], 
                    ticktext=[f"{p}m" for p in df['Período_num']]
                ),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            return self._fig_to_base64(fig)
            
        except Exception as e:
            print(f"Erro ao criar gráfico de timeline: {str(e)}")
            return None
    
    def create_projection_bar_chart(self, timeline_data):
        """Cria gráfico de barras de projeções (replicando a interface)."""
        if not timeline_data:
            return None
            
        try:
            import plotly.express as px
            
            # Preparar dados
            periods = list(timeline_data.keys())
            values = list(timeline_data.values())
            period_numbers = [int(p.replace(' meses', '')) for p in periods]
            percentuals = [st.session_state.get(f'percentual_{p}m', 0) for p in period_numbers]
            
            # Criar DataFrame
            chart_data = pd.DataFrame({
                'Período': periods,
                'Período_num': period_numbers,
                'Valor': values,
                'Percentual': percentuals
            })
            
            # Gráfico de barras interativo (replicando exatamente a interface)
            municipio = st.session_state.get('municipio_selecionado', 'Município')
            fig_bar = px.bar(
                chart_data, 
                x='Período', 
                y='Valor',
                title=f'Projeção Financeira por Período - {municipio}',
                labels={'Valor': 'Valor Projetado (R$)', 'Período': 'Período'},
                color='Valor',
                color_continuous_scale='viridis',
                text='Valor'
            )
            
            # Personalizar o gráfico
            fig_bar.update_traces(
                texttemplate='R$ %{text:,.0f}',
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Valor: R$ %{y:,.2f}<br>Percentual: %{customdata}%<extra></extra>',
                customdata=chart_data['Percentual']
            )
            
            fig_bar.update_layout(
                xaxis_title="Período",
                yaxis_title="Valor Projetado (R$)",
                font=dict(size=12),
                showlegend=False,
                height=500,
                yaxis=dict(tickformat=',.0f')
            )
            
            return self._fig_to_base64(fig_bar)
            
        except Exception as e:
            print(f"Erro ao criar gráfico de barras de projeção: {str(e)}")
            return None
    
    def create_projection_pie_chart(self, timeline_data):
        """Cria gráfico de pizza de projeções (replicando a interface)."""
        if not timeline_data:
            return None
            
        try:
            import plotly.express as px
            
            # Preparar dados
            periods = list(timeline_data.keys())
            values = list(timeline_data.values())
            
            # Criar DataFrame
            chart_data = pd.DataFrame({
                'Período': periods,
                'Valor': values
            })
            
            # Gráfico de pizza para distribuição dos valores (replicando a interface)
            municipio = st.session_state.get('municipio_selecionado', 'Município')
            fig_pie = px.pie(
                chart_data, 
                values='Valor', 
                names='Período',
                title=f'Distribuição da Projeção por Período - {municipio}',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}<extra></extra>'
            )
            
            fig_pie.update_layout(
                font=dict(size=12),
                height=500
            )
            
            return self._fig_to_base64(fig_pie)
            
        except Exception as e:
            print(f"Erro ao criar gráfico de pizza de projeção: {str(e)}")
            return None
    
    def create_summary_dashboard(self, summary_data):
        """Cria dashboard resumo com múltiplos gráficos usando Plotly."""
        if not summary_data:
            return None
            
        try:
            # Criar subplots 2x2
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=[
                    'Distribuição dos Componentes',
                    'Cenários de Desempenho', 
                    'Serviços Configurados',
                    'Resumo Financeiro'
                ],
                specs=[
                    [{"type": "pie"}, {"type": "bar"}],
                    [{"type": "bar"}, {"type": "bar"}]
                ],
                vertical_spacing=0.12,
                horizontal_spacing=0.1
            )
            
            # 1. Pizza de componentes
            if 'components' in summary_data:
                components = summary_data['components']
                filtered_comp = {k: v for k, v in components.items() if v > 0}
                if filtered_comp:
                    fig.add_trace(
                        go.Pie(
                            labels=list(filtered_comp.keys()),
                            values=list(filtered_comp.values()),
                            name="Componentes",
                            marker_colors=self.color_palette[:len(filtered_comp)],
                            textinfo='percent',
                            textfont_size=10,
                            showlegend=False
                        ),
                        row=1, col=1
                    )
            
            # 2. Barras de cenários
            if 'scenarios' in summary_data:
                scenarios = summary_data['scenarios']
                if scenarios:
                    scenario_colors = [
                        self.colors['danger'], self.colors['warning'],
                        self.colors['secondary'], self.colors['primary']
                    ]
                    fig.add_trace(
                        go.Bar(
                            x=list(scenarios.keys()),
                            y=list(scenarios.values()),
                            name="Cenários",
                            marker_color=scenario_colors[:len(scenarios)],
                            showlegend=False,
                            text=[f"R$ {v:,.0f}" for v in scenarios.values()],
                            textposition='outside',
                            textfont_size=9
                        ),
                        row=1, col=2
                    )
            
            # 3. Serviços horizontais
            if 'services' in summary_data:
                services = summary_data['services']
                filtered_services = {k: v for k, v in services.items() if v > 0}
                if filtered_services:
                    fig.add_trace(
                        go.Bar(
                            x=list(filtered_services.values()),
                            y=list(filtered_services.keys()),
                            orientation='h',
                            name="Serviços",
                            marker_color=self.colors['secondary'],
                            showlegend=False,
                            text=list(filtered_services.values()),
                            textposition='outside',
                            textfont_size=9
                        ),
                        row=2, col=1
                    )
            
            # 4. Resumo financeiro
            if 'financial' in summary_data:
                financial = summary_data['financial']
                filtered_financial = {k: v for k, v in financial.items() if v > 0}
                if filtered_financial:
                    fig.add_trace(
                        go.Bar(
                            x=list(filtered_financial.keys()),
                            y=list(filtered_financial.values()),
                            name="Financeiro",
                            marker_color=self.color_palette[4:4+len(filtered_financial)],
                            showlegend=False,
                            text=[f"R$ {v:,.0f}" for v in filtered_financial.values()],
                            textposition='outside',
                            textfont_size=8,
                            textangle=45
                        ),
                        row=2, col=2
                    )
            
            # Layout geral
            fig.update_layout(
                title=dict(
                    text='Dashboard Resumo - Calculadora PAP',
                    x=0.5,
                    font=dict(size=18, color=self.colors['primary'])
                ),
                font=dict(size=10),
                width=1200,
                height=800,
                margin=dict(l=50, r=50, t=100, b=50),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            # Formatação específica dos subplots
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(0,0,0,0.1)')
            
            return self._fig_to_base64(fig)
            
        except Exception as e:
            print(f"Erro ao criar dashboard: {str(e)}")
            return None
    
    def _fig_to_base64(self, fig):
        """Converte figura Plotly para base64."""
        try:
            # Método 1: Tentar usar Kaleido (melhor qualidade)
            try:
                img_bytes = fig.to_image(format="png", width=800, height=600, scale=2)
                img_base64 = base64.b64encode(img_bytes).decode()
                return img_base64
            except ImportError:
                print("Kaleido não encontrado. Tentando método alternativo...")
                # Método 2: Fallback usando matplotlib backend
                return self._plotly_to_matplotlib_fallback(fig)
            except Exception as e:
                print(f"Erro do Kaleido: {str(e)}. Tentando método alternativo...")
                return self._plotly_to_matplotlib_fallback(fig)
            
        except Exception as e:
            print(f"Erro geral ao converter figura para base64: {str(e)}")
            return None
    
    def _plotly_to_matplotlib_fallback(self, fig):
        """Fallback: converte dados do Plotly para matplotlib quando Kaleido não está disponível."""
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')
            
            # Extrair dados básicos do gráfico Plotly
            data = fig.data
            if not data:
                return None
            
            # Criar figura matplotlib
            plt.figure(figsize=(10, 8))
            
            # Processar primeiro trace (simplificado)
            trace = data[0]
            
            if trace.type == 'pie':
                # Gráfico de pizza
                plt.pie(trace.values, labels=trace.labels, autopct='%1.1f%%')
                plt.title(fig.layout.title.text if fig.layout.title else 'Gráfico')
                
            elif trace.type == 'bar':
                # Gráfico de barras
                if hasattr(trace, 'orientation') and trace.orientation == 'h':
                    plt.barh(trace.y, trace.x)
                    plt.xlabel('Quantidade')
                    plt.ylabel('Serviços')
                else:
                    plt.bar(trace.x, trace.y)
                    plt.xlabel('Cenários')
                    plt.ylabel('Valores')
                plt.title(fig.layout.title.text if fig.layout.title else 'Gráfico')
                
            elif trace.type == 'scatter':
                # Gráfico de linha
                plt.plot(trace.x, trace.y, marker='o', linewidth=2, markersize=6)
                plt.xlabel('Período')
                plt.ylabel('Valores')
                plt.title(fig.layout.title.text if fig.layout.title else 'Gráfico')
                plt.grid(True, alpha=0.3)
            
            # Ajustar layout
            plt.tight_layout()
            
            # Converter para base64
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return img_base64
            
        except Exception as e:
            print(f"Erro no fallback matplotlib: {str(e)}")
            return None

def generate_plotly_chart_for_pdf(chart_type, data):
    """Função utilitária para gerar gráficos Plotly para PDF."""
    try:
        generator = PAPPlotlyChartGenerator()
        
        if chart_type == 'components_pie':
            return generator.create_components_pie_chart(data)
        elif chart_type == 'scenarios_comparison':
            return generator.create_scenarios_comparison_chart(data)
        elif chart_type == 'services_distribution':
            return generator.create_services_distribution_chart(data)
        elif chart_type == 'projection_timeline':
            return generator.create_projection_timeline_chart(data)
        elif chart_type == 'summary_dashboard':
            return generator.create_summary_dashboard(data)
        else:
            return None
            
    except Exception as e:
        print(f"Erro ao gerar gráfico Plotly {chart_type}: {str(e)}")
        return None
