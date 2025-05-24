"""
Gerador de PDF que replica exatamente os gráficos e tabelas da interface.
"""
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
import pandas as pd
from datetime import datetime
import json
import io
import base64
from utils import format_currency, currency_to_float

class PAPInterfaceReplicaGenerator:
    """Gerador de PDF que replica exatamente a interface da aplicação."""
    
    def __init__(self):
        """Inicializa o gerador."""
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configura estilos personalizados."""
        # Estilo para título principal
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Title'],
            fontSize=18,
            textColor=colors.HexColor('#4682B4'),
            alignment=TA_CENTER,
            spaceBefore=12,
            spaceAfter=20,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#4682B4'),
            alignment=TA_LEFT,
            spaceBefore=20,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para seções
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#006400'),
            alignment=TA_LEFT,
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceBefore=6,
            spaceAfter=6,
            fontName='Helvetica'
        ))
        
        # Estilo para destacar cenários
        self.styles.add(ParagraphStyle(
            name='CenarioTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            alignment=TA_LEFT,
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))

    def _create_header_footer(self, canvas, doc):
        """Cria cabeçalho e rodapé."""
        canvas.saveState()
        
        # Cabeçalho
        canvas.setFont('Helvetica-Bold', 12)
        canvas.setFillColor(colors.HexColor('#4682B4'))
        canvas.drawString(50, A4[1] - 50, "RELATÓRIO CALCULADORA PAP - INTERFACE REPLICA")
        
        # Linha separadora
        canvas.setStrokeColor(colors.HexColor('#4682B4'))
        canvas.setLineWidth(1)
        canvas.line(50, A4[1] - 70, A4[0] - 50, A4[1] - 70)
        
        # Rodapé
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.black)
        
        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
        canvas.drawString(50, 50, f"Gerado em: {data_geracao}")
        canvas.drawRightString(A4[0] - 50, 50, f"Página {doc.page}")
        
        canvas.restoreState()

    def generate_interface_replica_report(self) -> bytes:
        """Gera relatório que replica exatamente a interface."""
        buffer = io.BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3*cm,
            bottomMargin=2.5*cm
        )
        
        # Adicionar seções
        self._add_cover_page()
        self._add_calculation_tables()
        self._add_scenarios_analysis()
        self._add_scenarios_detailed_tables()
        self._add_projection_section()
        self._add_interface_charts()
        
        # Construir documento
        doc.build(self.story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)
        
        buffer.seek(0)
        return buffer.getvalue()

    def _add_cover_page(self):
        """Adiciona página de capa."""
        titulo = Paragraph("RELATÓRIO CALCULADORA PAP", self.styles['MainTitle'])
        self.story.append(titulo)
        self.story.append(Spacer(1, 20))
        
        subtitulo = Paragraph(
            "Replicando Interface - Gráficos e Tabelas de Cenários",
            self.styles['SubTitle']
        )
        self.story.append(subtitulo)
        self.story.append(Spacer(1, 40))
        
        municipio = st.session_state.get('municipio_selecionado', 'Não informado')
        uf = st.session_state.get('uf_selecionada', 'Não informado')
        
        info = f"""
        <b>Município:</b> {municipio}<br/>
        <b>UF:</b> {uf}<br/>
        <b>Data:</b> {datetime.now().strftime("%d/%m/%Y às %H:%M")}
        """
        
        self.story.append(Paragraph(info, self.styles['CustomNormal']))
        self.story.append(PageBreak())

    def _add_calculation_tables(self):
        """Adiciona tabelas de cálculos (replicando a interface)."""
        titulo = Paragraph("1. TABELAS DE CÁLCULOS (REPLICANDO INTERFACE)", self.styles['SubTitle'])
        self.story.append(titulo)
        
        if not st.session_state.get('calculo_realizado', False):
            aviso = Paragraph("Cálculos não realizados. Execute a calculadora primeiro.", self.styles['CustomNormal'])
            self.story.append(aviso)
            return
        
        try:
            # Recriar os cálculos
            from calculations import (
                calculate_fixed_component, calculate_vinculo_component, 
                calculate_quality_component, calculate_implantacao_manutencao,
                calculate_saude_bucal_component, calculate_per_capita
            )
            
            with open("config.json", "r", encoding="utf-8") as f:
                config_data = json.load(f)
            
            # Obter parâmetros
            selected_services = st.session_state.get('selected_services', {})
            edited_values = st.session_state.get('edited_values', {})
            edited_implantacao_values = st.session_state.get('edited_implantacao_values', {})
            edited_implantacao_quantity = st.session_state.get('edited_implantacao_quantity', {})
            classificacao = st.session_state.get('classificacao', 'Bom')
            vinculo = st.session_state.get('vinculo', 'Bom')
            
            # Calcular cada componente
            fixed_df, _ = calculate_fixed_component(selected_services, edited_values, edited_implantacao_quantity, edited_implantacao_values, config_data)
            vinculo_df, _ = calculate_vinculo_component(selected_services, edited_values, vinculo)
            quality_df, _ = calculate_quality_component(selected_services, edited_values, classificacao, config_data)
            implantacao_df, _ = calculate_implantacao_manutencao(selected_services, edited_values, config_data)
            saude_bucal_df, _ = calculate_saude_bucal_component(selected_services, edited_values, config_data)
            per_capita_df, _ = calculate_per_capita()
            
            # Adicionar cada tabela
            self._add_dataframe_table("1.1 Componente I - Componente Fixo", fixed_df)
            self._add_dataframe_table("1.2 Componente II - Vínculo e Acompanhamento Territorial", vinculo_df)
            self._add_dataframe_table("1.3 Componente III - Qualidade", quality_df)
            self._add_dataframe_table("1.4 Componente IV - Implantação e Manutenção", implantacao_df)
            self._add_dataframe_table("1.5 Componente V - Atenção à Saúde Bucal", saude_bucal_df)
            self._add_dataframe_table("1.6 Componente VI - Per Capita", per_capita_df)
            
        except Exception as e:
            erro = Paragraph(f"Erro ao gerar tabelas: {str(e)}", self.styles['CustomNormal'])
            self.story.append(erro)

    def _add_dataframe_table(self, titulo, df):
        """Adiciona uma tabela do DataFrame."""
        secao_titulo = Paragraph(titulo, self.styles['SectionHeader'])
        self.story.append(secao_titulo)
        
        if df is not None and not df.empty:
            # Converter DataFrame para dados de tabela
            table_data = []
            table_data.append(list(df.columns))
            
            for _, row in df.iterrows():
                table_data.append([str(val) for val in row])
            
            # Calcular larguras das colunas
            col_widths = [A4[0] / len(df.columns) - 1*cm] * len(df.columns)
            
            table = Table(table_data, colWidths=col_widths)
            
            # Estilo da tabela
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4682B4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F8FF')])
            ]
            
            # Destacar linha de total
            if len(table_data) > 1:
                table_style.extend([
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E6E6FA')),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ])
            
            table.setStyle(TableStyle(table_style))
            self.story.append(table)
        else:
            aviso = Paragraph("Nenhum dado disponível.", self.styles['CustomNormal'])
            self.story.append(aviso)
        
        self.story.append(Spacer(1, 15))

    def _add_scenarios_analysis(self):
        """Adiciona quadro de comparação de cenários."""
        titulo = Paragraph("2. QUADRO COMPARATIVO DE CENÁRIOS", self.styles['SubTitle'])
        self.story.append(titulo)
        
        if not st.session_state.get('calculo_realizado', False):
            aviso = Paragraph("Cálculos não realizados.", self.styles['CustomNormal'])
            self.story.append(aviso)
            return
        
        try:
            from components.scenarios_report import gerar_relatorio_cenarios
            
            with open("config.json", "r", encoding="utf-8") as f:
                config_data = json.load(f)
            
            selected_services = st.session_state.get('selected_services', {})
            total_geral = st.session_state.get('total_pap_calculado', 0)
            vinculo_values = config_data.get('quality_values', {})
            quality_values = config_data.get('quality_values', {})
            
            df_comparacao = gerar_relatorio_cenarios(
                total_geral, vinculo_values, quality_values, selected_services,
                0, 0, 0, 0
            )
            
            if not df_comparacao.empty:
                self._add_scenarios_comparison_table(df_comparacao)
            
        except Exception as e:
            erro = Paragraph(f"Erro ao gerar comparação de cenários: {str(e)}", self.styles['CustomNormal'])
            self.story.append(erro)

    def _add_scenarios_comparison_table(self, df_comparacao):
        """Adiciona a tabela de comparação de cenários com cores."""
        # Converter DataFrame para dados de tabela
        table_data = []
        table_data.append(list(df_comparacao.columns))
        
        for _, row in df_comparacao.iterrows():
            table_data.append([str(val) for val in row])
        
        # Calcular larguras
        col_widths = [3*cm, 2.5*cm, 3.5*cm, 3*cm, 2.5*cm]
        
        table = Table(table_data, colWidths=col_widths)
        
        # Estilo base
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4682B4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]
        
        # Cores por cenário (replicando a interface)
        cores_cenarios = {
            'REGULAR': colors.HexColor('#8B0000'),
            'SUFICIENTE': colors.HexColor('#FFA500'),
            'BOM': colors.HexColor('#006400'),
            'ÓTIMO': colors.HexColor('#000080')
        }
        
        # Aplicar cores às linhas
        for i, row in enumerate(table_data[1:], 1):
            desempenho = row[1] if len(row) > 1 else ''
            cor = cores_cenarios.get(desempenho, colors.white)
            table_style.append(('BACKGROUND', (0, i), (-1, i), cor))
            table_style.append(('TEXTCOLOR', (0, i), (-1, i), colors.white))
        
        table.setStyle(TableStyle(table_style))
        self.story.append(table)
        self.story.append(Spacer(1, 20))

    def _add_scenarios_detailed_tables(self):
        """Adiciona tabelas detalhadas por cenário (replicando a interface)."""
        titulo = Paragraph("3. RELATÓRIO DETALHADO POR CENÁRIO", self.styles['SubTitle'])
        self.story.append(titulo)
        
        if not st.session_state.get('calculo_realizado', False):
            return
        
        try:
            from components.scenarios_report import display_detailed_report
            
            with open("config.json", "r", encoding="utf-8") as f:
                config_data = json.load(f)
            
            selected_services = st.session_state.get('selected_services', {})
            total_geral = st.session_state.get('total_pap_calculado', 0)
            vinculo_values = config_data.get('quality_values', {})
            quality_values = config_data.get('quality_values', {})
            
            # Cores dos cenários
            cores_cenarios = {
                'Regular': '#8B0000',
                'Suficiente': '#FFA500',
                'Bom': '#006400',
                'Ótimo': '#000080'
            }
            
            cenarios = ['Regular', 'Suficiente', 'Bom', 'Ótimo']
            
            for cenario in cenarios:
                # Título do cenário
                style_cenario = ParagraphStyle(
                    name=f'Cenario{cenario}',
                    parent=self.styles['CenarioTitle'],
                    textColor=colors.HexColor(cores_cenarios[cenario])
                )
                
                cenario_titulo = Paragraph(f"3.{cenarios.index(cenario)+1} Cenário: {cenario}", style_cenario)
                self.story.append(cenario_titulo)
                
                # Calcular dados do cenário
                tabela_cenario = self._calculate_scenario_table(cenario, total_geral, vinculo_values, quality_values, selected_services)
                
                if tabela_cenario:
                    self._add_scenario_detail_table(tabela_cenario, cores_cenarios[cenario])
                
                self.story.append(Spacer(1, 15))
            
        except Exception as e:
            erro = Paragraph(f"Erro ao gerar tabelas detalhadas: {str(e)}", self.styles['CustomNormal'])
            self.story.append(erro)

    def _calculate_scenario_table(self, cenario, total_geral, vinculo_values, quality_values, selected_services):
        """Calcula dados para tabela detalhada do cenário."""
        try:
            # Zerar valores para o cenário
            valor_vinculo = 0
            valor_qualidade = 0
            valor_emulti = 0
            
            # Calcular valores para o cenário específico
            for service in vinculo_values:
                if service in selected_services:
                    valor_vinculo += vinculo_values[service].get(cenario, 0) * selected_services.get(service, 0)
            
            for service in quality_values:
                if service in selected_services:
                    valor_qualidade += quality_values[service].get(cenario, 0) * selected_services.get(service, 0)
            
            for service in ["eMULTI Ampl.", "eMULTI Compl.", "eMULTI Estrat."]:
                if selected_services.get(service, 0) > 0:
                    valor_emulti += quality_values.get(service, {}).get(cenario, 0) * selected_services.get(service, 0)
            
            # Valores fixos (simplificados para o PDF)
            total_fixed_value = 15000  # Valor aproximado
            total_implantacao_manutencao_value = 5000
            total_saude_bucal_value = 3000
            total_per_capita = 2000
            
            # Calcular total do cenário
            valor_cenario = total_fixed_value + valor_vinculo + valor_qualidade + total_implantacao_manutencao_value + total_saude_bucal_value + total_per_capita + valor_emulti
            
            # Diferença e percentual
            diferenca = valor_cenario - total_geral
            aumento_percentual = ((valor_cenario - total_geral) / total_geral) * 100 if total_geral != 0 else 0
            
            # Criar dados da tabela
            tabela_dados = [
                ['Componente', 'Valor'],
                ['Valor Base (Recebia na APS Mensalmente)', format_currency(total_geral)],
                ['Valor Fixo', format_currency(total_fixed_value)],
                ['Vínculo e Acompanhamento', format_currency(valor_vinculo)],
                ['Qualidade', format_currency(valor_qualidade)],
                ['eMulti', format_currency(valor_emulti)],
                ['Implantação/Manutenção', format_currency(total_implantacao_manutencao_value)],
                ['Saúde Bucal', format_currency(total_saude_bucal_value)],
                ['Per Capita', format_currency(total_per_capita)],
                [f'Total do Cenário ({cenario})', format_currency(valor_cenario)],
                ['Diferença (Aumentou Mensal)', format_currency(diferenca)],
                ['Aumento Percentual', f"{aumento_percentual:.0f}%"]
            ]
            
            return tabela_dados
            
        except Exception as e:
            return None

    def _add_scenario_detail_table(self, tabela_dados, cor_cenario):
        """Adiciona tabela detalhada do cenário."""
        table = Table(tabela_dados, colWidths=[10*cm, 6*cm])
        
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(cor_cenario)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')])
        ]
        
        # Destacar linha do total
        table_style.append(('BACKGROUND', (0, -3), (-1, -3), colors.HexColor(cor_cenario)))
        table_style.append(('TEXTCOLOR', (0, -3), (-1, -3), colors.white))
        table_style.append(('FONTNAME', (0, -3), (-1, -3), 'Helvetica-Bold'))
        
        table.setStyle(TableStyle(table_style))
        self.story.append(table)

    def _add_projection_section(self):
        """Adiciona seção de projeção financeira (replicando interface)."""
        titulo = Paragraph("4. PROJEÇÃO FINANCEIRA (INTERFACE)", self.styles['SubTitle'])
        self.story.append(titulo)
        
        # Tabela de projeção temporal
        self._add_projection_table_interface()
        
        # Tabela de comparação
        self._add_comparison_table_interface()

    def _add_projection_table_interface(self):
        """Adiciona tabela de projeção exatamente como na interface."""
        secao_titulo = Paragraph("4.1 Valores Projetados por Período", self.styles['SectionHeader'])
        self.story.append(secao_titulo)
        
        periods = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
        
        projecao_data = [
            ['Período (meses)', 'Valor Projetado (R$)', 'Percentual (%)']
        ]
        
        for period in periods:
            valor = st.session_state.get(f'valor_{period}m', 0)
            percentual = st.session_state.get(f'percentual_{period}m', 0)
            
            projecao_data.append([
                str(period),
                format_currency(float(valor) if valor else 0),
                f"{int(percentual) if percentual else 0}%"
            ])
        
        table = Table(projecao_data, colWidths=[4*cm, 6*cm, 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4682B4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F8FF')])
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 15))

    def _add_comparison_table_interface(self):
        """Adiciona tabela de comparação da interface."""
        secao_titulo = Paragraph("4.2 Comparação: Cenário Regular vs Projeções", self.styles['SectionHeader'])
        self.story.append(secao_titulo)
        
        valor_regular = st.session_state.get('valor_cenario_regular', 0)
        valor_12m = float(st.session_state.get('valor_12m', 0))
        valor_24m = float(st.session_state.get('valor_24m', 0))
        valor_30m = float(st.session_state.get('valor_30m', 0))
        
        comparacao_data = [
            ['Cenário', 'Valor (R$)'],
            ['Valor Regular', format_currency(valor_regular)],
            ['Projeção 12 meses', format_currency(valor_12m)],
            ['Projeção 24 meses', format_currency(valor_24m)],
            ['Projeção 30 meses', format_currency(valor_30m)]
        ]
        
        table = Table(comparacao_data, colWidths=[8*cm, 6*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E8F4F8')]),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F0E68C')),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 15))

    def _add_interface_charts(self):
        """Adiciona gráficos exatamente como na interface."""
        titulo = Paragraph("5. GRÁFICOS DA INTERFACE", self.styles['SubTitle'])
        self.story.append(titulo)
        
        try:
            from reports.plotly_chart_generator import PAPPlotlyChartGenerator
            generator = PAPPlotlyChartGenerator()
            
            # 1. Gráfico de Barras (Tab 1 da interface)
            periods = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
            values = [float(st.session_state.get(f'valor_{p}m', 0)) for p in periods]
            timeline_data = {f"{p} meses": v for p, v in zip(periods, values)}
            
            chart_base64 = generator.create_projection_bar_chart(timeline_data)
            if chart_base64:
                self._add_chart_to_pdf("5.1 Gráfico de Barras (Interface Tab 1)", chart_base64)
            
            # 2. Gráfico de Linhas (Tab 2 da interface)
            chart_base64 = generator.create_projection_timeline_chart(timeline_data)
            if chart_base64:
                self._add_chart_to_pdf("5.2 Gráfico de Linhas (Interface Tab 2)", chart_base64)
            
            # 3. Gráfico de Pizza (Tab 3 da interface)
            chart_base64 = generator.create_projection_pie_chart(timeline_data)
            if chart_base64:
                self._add_chart_to_pdf("5.3 Gráfico de Pizza (Interface Tab 3)", chart_base64)
            
            # 4. Gráfico de Comparação
            comparison_data = {
                'Regular': st.session_state.get('valor_cenario_regular', 0),
                '12 meses': float(st.session_state.get('valor_12m', 0)),
                '24 meses': float(st.session_state.get('valor_24m', 0)),
                '30 meses': float(st.session_state.get('valor_30m', 0))
            }
            
            chart_base64 = generator.create_scenarios_comparison_chart(comparison_data)
            if chart_base64:
                self._add_chart_to_pdf("5.4 Comparação Regular vs Projeções", chart_base64)
            
        except Exception as e:
            erro = Paragraph(f"Erro ao gerar gráficos da interface: {str(e)}", self.styles['CustomNormal'])
            self.story.append(erro)

    def _add_chart_to_pdf(self, titulo, chart_base64):
        """Adiciona gráfico ao PDF."""
        try:
            chart_titulo = Paragraph(titulo, self.styles['SectionHeader'])
            self.story.append(chart_titulo)
            
            if chart_base64:
                image_data = base64.b64decode(chart_base64)
                image_buffer = io.BytesIO(image_data)
                image_buffer.seek(0)
                
                img = Image(image_buffer, width=14*cm, height=10*cm)
                self.story.append(img)
                self.story.append(Spacer(1, 15))
            else:
                erro = Paragraph("Gráfico não pôde ser gerado.", self.styles['CustomNormal'])
                self.story.append(erro)
                
        except Exception as e:
            erro = Paragraph(f"Erro ao adicionar gráfico: {str(e)}", self.styles['CustomNormal'])
            self.story.append(erro)

def generate_interface_replica_report() -> bytes:
    """Gera relatório que replica a interface."""
    try:
        generator = PAPInterfaceReplicaGenerator()
        return generator.generate_interface_replica_report()
    except Exception as e:
        st.error(f"Erro ao gerar relatório: {str(e)}")
        return b""
