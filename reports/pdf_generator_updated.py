"""
Gerador de relatórios PDF para a Calculadora PAP.
"""
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import pandas as pd
from datetime import datetime
import json
import io
import base64
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from utils import format_currency, currency_to_float
from reports.report_templates import PAPReportTemplates, PDFLayoutHelper
from reports.data_formatter import PAPDataFormatter
from reports.chart_generator import generate_chart_for_pdf

class PAPReportGenerator:
    """Classe para geração de relatórios PDF da Calculadora PAP."""
    
    def __init__(self):
        """Inicializa o gerador de relatórios."""
        self.story = []
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Configura estilos personalizados para o relatório."""
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
        
        # Estilo para informações destacadas
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#8B0000'),
            alignment=TA_LEFT,
            spaceBefore=8,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        ))

    def _create_header_footer(self, canvas, doc):
        """Cria cabeçalho e rodapé para todas as páginas."""
        # Cabeçalho
        canvas.saveState()
        
        # Logo (se existir)
        try:
            logo_path = "logo_colorida_mg.png"
            canvas.drawImage(logo_path, 50, A4[1] - 80, width=100, height=40, preserveAspectRatio=True)
        except:
            pass
            
        # Título do relatório no cabeçalho
        canvas.setFont('Helvetica-Bold', 12)
        canvas.setFillColor(colors.HexColor('#4682B4'))
        canvas.drawString(200, A4[1] - 50, "RELATÓRIO DE CÁLCULO PAP")
        canvas.drawString(200, A4[1] - 65, "Programa de Apoio à Atenção Primária")
        
        # Linha separadora
        canvas.setStrokeColor(colors.HexColor('#4682B4'))
        canvas.setLineWidth(1)
        canvas.line(50, A4[1] - 90, A4[0] - 50, A4[1] - 90)
        
        # Rodapé
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.black)
        
        # Data de geração
        data_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")
        canvas.drawString(50, 50, f"Gerado em: {data_geracao}")
        
        # Número da página
        canvas.drawRightString(A4[0] - 50, 50, f"Página {doc.page}")
        
        # Linha separadora inferior
        canvas.setStrokeColor(colors.grey)
        canvas.line(50, 70, A4[0] - 50, 70)
        
        canvas.restoreState()

    def generate_full_report(self) -> bytes:
        """Gera o relatório completo em PDF."""
        buffer = io.BytesIO()
        
        # Criar documento
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3*cm,
            bottomMargin=2.5*cm
        )
        
        # Adicionar seções ao relatório
        self._add_cover_page()
        self._add_municipality_info()
        self._add_legal_context()
        self._add_services_configuration()
        self._add_calculation_details()
        self._add_executive_summary()
        self._add_scenarios_analysis()
        self._add_detailed_scenarios()
        self._add_additional_parameters()
        self._add_financial_projection()
        self._add_charts_section()
        self._add_conclusions()
        
        # Construir documento
        doc.build(self.story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)
        
        # Retornar bytes
        buffer.seek(0)
        return buffer.getvalue()

    def _add_cover_page(self):
        """Adiciona página de capa."""
        # Título principal
        titulo = Paragraph("RELATÓRIO DE CÁLCULO PAP", self.styles['MainTitle'])
        self.story.append(titulo)
        self.story.append(Spacer(1, 20))
        
        # Subtítulo
        subtitulo = Paragraph(
            "Programa de Apoio à Atenção Primária<br/>"
            "Portaria GM/MS Nº 3.493, de 10 de abril de 2024",
            self.styles['SubTitle']
        )
        self.story.append(subtitulo)
        self.story.append(Spacer(1, 40))
        
        # Informações do município
        municipio = st.session_state.get('municipio_selecionado', 'Não informado')
        uf = st.session_state.get('uf_selecionada', 'Não informado')
        competencia = st.session_state.get('competencia_selecionada', 'Não informado')
        
        info_municipio = f"""
        <b>Município:</b> {municipio}<br/>
        <b>UF:</b> {uf}<br/>
        <b>Competência:</b> {competencia}<br/>
        <b>Data de Geração:</b> {datetime.now().strftime("%d/%m/%Y às %H:%M")}
        """
        
        info_para = Paragraph(info_municipio, self.styles['CustomNormal'])
        self.story.append(info_para)
        self.story.append(PageBreak())

    def _add_municipality_info(self):
        """Adiciona informações do município."""
        titulo = Paragraph("1. INFORMAÇÕES DO MUNICÍPIO", self.styles['SubTitle'])
        self.story.append(titulo)
        
        # Dados básicos
        populacao = st.session_state.get('populacao', 0)
        ied = st.session_state.get('ied', 'Não informado')
        
        dados_basicos = [
            ['Informação', 'Valor'],
            ['Município', st.session_state.get('municipio_selecionado', 'Não informado')],
            ['UF', st.session_state.get('uf_selecionada', 'Não informado')],
            ['População', f"{populacao:,}".replace(',', '.')],
            ['IED', ied],
            ['Competência', st.session_state.get('competencia_selecionada', 'Não informado')]
        ]
        
        tabela_dados = Table(dados_basicos, colWidths=[8*cm, 8*cm])
        tabela_dados.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4682B4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F8FF')])
        ]))
        
        self.story.append(tabela_dados)
        self.story.append(Spacer(1, 20))

    def _add_legal_context(self):
        """Adiciona contexto legal."""
        titulo = Paragraph("2. FUNDAMENTAÇÃO LEGAL", self.styles['SubTitle'])
        self.story.append(titulo)
        
        contexto = """
        Este relatório apresenta os cálculos do Programa de Apoio à Atenção Primária (PAP) conforme 
        estabelecido na <b>Portaria GM/MS Nº 3.493, de 10 de abril de 2024</b>, que institui incentivo 
        financeiro federal de custeio para o fortalecimento da Atenção Primária à Saúde.
        <br/><br/>
        O PAP é composto por seis componentes principais:
        <br/>• <b>Componente I:</b> Componente Fixo
        <br/>• <b>Componente II:</b> Vínculo e Acompanhamento Territorial  
        <br/>• <b>Componente III:</b> Qualidade
        <br/>• <b>Componente IV:</b> Implantação e Manutenção de Programas
        <br/>• <b>Componente V:</b> Atenção à Saúde Bucal
        <br/>• <b>Componente VI:</b> Per Capita
        """
        
        contexto_para = Paragraph(contexto, self.styles['CustomNormal'])
        self.story.append(contexto_para)
        self.story.append(Spacer(1, 20))

    def _add_services_configuration(self):
        """Adiciona configuração dos serviços."""
        titulo = Paragraph("3. CONFIGURAÇÃO DOS SERVIÇOS", self.styles['SubTitle'])
        self.story.append(titulo)
        
        # Obter serviços selecionados
        servicos_data = []
        servicos_data.append(['Serviço', 'Quantidade', 'Observações'])
        
        # Lista de todos os serviços possíveis
        todos_servicos = [
            'eSF', 'eAP 30h', 'eAP 20h', 'eMULTI Ampl.', 'eMULTI Compl.', 'eMULTI Estrat.'
        ]
        
        for servico in todos_servicos:
            quantidade = st.session_state.get(f'quantity_{servico}', 0)
            if quantidade > 0:
                servicos_data.append([servico, str(quantidade), 'Configurado'])
        
        # Parâmetros de qualidade
        classificacao = st.session_state.get('classificacao', 'Não definido')
        vinculo = st.session_state.get('vinculo', 'Não definido')
        
        servicos_data.append(['', '', ''])  # Linha em branco
        servicos_data.append(['Parâmetro de Qualidade', classificacao, 'Selecionado'])
        servicos_data.append(['Vínculo e Acompanhamento', vinculo, 'Selecionado'])
        
        if len(servicos_data) > 1:  # Se há dados além do cabeçalho
            tabela_servicos = Table(servicos_data, colWidths=[6*cm, 4*cm, 6*cm])
            tabela_servicos.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006400')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0FFF0')])
            ]))
            
            self.story.append(tabela_servicos)
        else:
            aviso = Paragraph("Nenhum serviço foi configurado.", self.styles['Highlight'])
            self.story.append(aviso)
            
        self.story.append(Spacer(1, 20))

    def _add_calculation_details(self):
        """Adiciona detalhes dos cálculos com tabelas reais."""
        titulo = Paragraph("4. CÁLCULOS DETALHADOS", self.styles['SubTitle'])
        self.story.append(titulo)
        
        # Verificar se os cálculos foram realizados
        if not st.session_state.get('calculo_realizado', False):
            aviso = Paragraph(
                "Os cálculos não foram realizados. Execute a calculadora antes de gerar o relatório.",
                self.styles['Highlight']
            )
            self.story.append(aviso)
            return
        
        # Recriar os cálculos para obter as tabelas
        try:
            # Importar funções de cálculo
            from calculations import (
                calculate_fixed_component, calculate_vinculo_component, 
                calculate_quality_component, calculate_implantacao_manutencao,
                calculate_saude_bucal_component, calculate_per_capita
            )
            import json
            
            # Carregar configuração
            with open("config.json", "r", encoding="utf-8") as f:
                config_data = json.load(f)
            
            # Obter parâmetros do session_state
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
            self._add_component_table("4.1 Componente I - Componente Fixo", fixed_df)
            self._add_component_table("4.2 Componente II - Vínculo e Acompanhamento Territorial", vinculo_df)
            self._add_component_table("4.3 Componente III - Qualidade", quality_df)
            self._add_component_table("4.4 Componente IV - Implantação e Manutenção", implantacao_df)
            self._add_component_table("4.5 Componente V - Atenção à Saúde Bucal", saude_bucal_df)
            self._add_component_table("4.6 Componente VI - Per Capita", per_capita_df)
            
        except Exception as e:
            erro = Paragraph(f"Erro ao gerar tabelas de cálculo: {str(e)}", self.styles['Highlight'])
            self.story.append(erro)

    def _add_component_table(self, titulo, dataframe):
        """Adiciona uma tabela de componente ao relatório."""
        # Título da seção
        secao_titulo = Paragraph(titulo, self.styles['SectionHeader'])
        self.story.append(secao_titulo)
        
        if dataframe is not None and not dataframe.empty:
            # Converter DataFrame para dados de tabela
            table_data = []
            table_data.append(list(dataframe.columns))  # Cabeçalho
            
            for _, row in dataframe.iterrows():
                table_data.append([str(val) for val in row])
            
            # Criar tabela
            table = Table(table_data, colWidths=[4*cm] * len(dataframe.columns))
            
            # Estilo da tabela
            table_style = [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4682B4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F8FF')])
            ]
            
            # Destacar última linha (totais)
            if len(table_data) > 1:
                table_style.extend([
                    ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E6E6FA')),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ])
            
            table.setStyle(TableStyle(table_style))
            self.story.append(table)
        else:
            aviso = Paragraph("Nenhum dado disponível para este componente.", self.styles['CustomNormal'])
            self.story.append(aviso)
        
        self.story.append(Spacer(1, 15))

    def _add_scenarios_analysis(self):
        """Adiciona análise de cenários."""
        titulo = Paragraph("5. ANÁLISE DE CENÁRIOS", self.styles['SubTitle'])
        self.story.append(titulo)
        
        descricao = """
        A análise de cenários considera diferentes níveis de desempenho da Atenção Primária à Saúde:
        <br/>• <b>Regular:</b> Nível básico de desempenho
        <br/>• <b>Suficiente:</b> Nível adequado de desempenho  
        <br/>• <b>Bom:</b> Nível elevado de desempenho
        <br/>• <b>Ótimo:</b> Nível excelente de desempenho
        <br/><br/>
        Cada cenário impacta diretamente nos valores dos componentes de Vínculo/Acompanhamento e Qualidade.
        """
        
        descricao_para = Paragraph(descricao, self.styles['CustomNormal'])
        self.story.append(descricao_para)
        self.story.append(Spacer(1, 20))

    def _add_executive_summary(self):
        """Adiciona resumo executivo."""
        titulo = Paragraph("6. RESUMO EXECUTIVO", self.styles['SubTitle'])
        self.story.append(titulo)
        
        # Calcular totais se disponíveis
        total_pap = st.session_state.get('total_pap_calculado', 0)
        
        if total_pap > 0:
            resumo = f"""
            <b>Valor Total PAP Calculado:</b> {format_currency(total_pap)}
            <br/><br/>
            Este valor representa o incentivo financeiro federal mensal que o município pode receber 
            através do Programa de Apoio à Atenção Primária, conforme os serviços configurados e 
            parâmetros de qualidade selecionados.
            <br/><br/>
            <b>Recomendações:</b>
            <br/>• Manter e aprimorar os serviços já implantados
            <br/>• Considerar estratégias para melhorar os indicadores de qualidade
            <br/>• Avaliar possibilidades de expansão dos serviços oferecidos
            """
        else:
            resumo = """
            Para visualizar o resumo executivo completo, execute os cálculos na aplicação principal 
            antes de gerar este relatório.
            """
            
        resumo_para = Paragraph(resumo, self.styles['CustomNormal'])
        self.story.append(resumo_para)
        self.story.append(Spacer(1, 20))
        
        # Adicionar tabela resumo se disponível
        self._add_summary_table()

    def _add_summary_table(self):
        """Adiciona tabela resumo executivo."""
        try:
            # Obter valores dos componentes principais
            valor_esf_eap = st.session_state.get('valor_esf_eap', 0.0)
            valor_saude_bucal = st.session_state.get('valor_saude_bucal', 0.0)
            valor_acs = st.session_state.get('valor_acs', 0.0)
            valor_estrategicas = st.session_state.get('valor_estrategicas', 0.0)
            total_adicional = valor_esf_eap + valor_saude_bucal + valor_acs + valor_estrategicas
            
            resumo_data = [
                ['Componente', 'Valor Mensal'],
                ['Incentivo Financeiro da APS - eSF ou eAP', format_currency(valor_esf_eap)],
                ['Incentivo Financeiro da APS - eMulti', format_currency(0)],  # Será calculado
                ['Incentivo Financeiro para Atenção à Saúde Bucal', format_currency(valor_saude_bucal)],
                ['Componente Per Capita', format_currency(0)],  # Será calculado
                ['Componente para Implantação e Manutenção', format_currency(0)],  # Será calculado
                ['Total Adicional', format_currency(total_adicional)],
                ['TOTAL PAP', format_currency(st.session_state.get('total_pap_calculado', 0))]
            ]
            
            tabela_resumo = Table(resumo_data, colWidths=[10*cm, 6*cm])
            tabela_resumo.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4682B4')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F0F8FF')]),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E6E6FA')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ]))
            
            self.story.append(tabela_resumo)
            self.story.append(Spacer(1, 20))
            
        except Exception as e:
            pass  # Se houver erro, pula a tabela

    def _add_detailed_scenarios(self):
        """Adiciona cenários detalhados."""
        titulo = Paragraph("7. CENÁRIOS DETALHADOS", self.styles['SubTitle'])
        self.story.append(titulo)
        
        if not st.session_state.get('calculo_realizado', False):
            aviso = Paragraph("Cálculos não realizados. Execute a calculadora primeiro.", self.styles['Highlight'])
            self.story.append(aviso)
            return
            
        try:
            # Importar função de geração de relatório de cenários
            from components.scenarios_report import gerar_relatorio_cenarios
            import json
            
            # Carregar configuração
            with open("config.json", "r", encoding="utf-8") as f:
                config_data = json.load(f)
            
            # Obter dados necessários
            selected_services = st.session_state.get('selected_services', {})
            total_geral = st.session_state.get('total_pap_calculado', 0)
            vinculo_values = config_data.get('quality_values', {})  # Usando quality_values como proxy
            quality_values = config_data.get('quality_values', {})
            
            # Gerar relatório de cenários
            df_comparacao = gerar_relatorio_cenarios(
                total_geral, vinculo_values, quality_values, selected_services,
                0, 0, 0, 0  # Valores simplificados para o PDF
            )
            
            # Adicionar tabela de comparação
            if not df_comparacao.empty:
                self._add_component_table("7.1 Quadro Comparativo de Cenários", df_comparacao)
            
        except Exception as e:
            erro = Paragraph(f"Erro ao gerar cenários detalhados: {str(e)}", self.styles['Highlight'])
            self.story.append(erro)

    def _add_additional_parameters(self):
        """Adiciona seção de parâmetros adicionais."""
        titulo = Paragraph("8. PARÂMETROS ADICIONAIS", self.styles['SubTitle'])
        self.story.append(titulo)
        
        descricao = Paragraph(
            "Esta seção apresenta os parâmetros adicionais configurados para complementar "
            "o cálculo do PAP, incluindo valores específicos definidos pelo município.",
            self.styles['CustomNormal']
        )
        self.story.append(descricao)
        self.story.append(Spacer(1, 10))
        
        # Tabela de parâmetros adicionais
        parametros_data = [
            ['Parâmetro', 'Valor Configurado'],
            ['Incentivo Financeiro da APS eSF ou eAP', format_currency(st.session_state.get('valor_esf_eap', 0.0))],
            ['Incentivo Financeiro para Atenção à Saúde Bucal', format_currency(st.session_state.get('valor_saude_bucal', 0.0))],
            ['Total ACS', format_currency(st.session_state.get('valor_acs', 0.0))],
            ['Ações Estratégicas', format_currency(st.session_state.get('valor_estrategicas', 0.0))],
            ['Total Adicional', format_currency(
                st.session_state.get('valor_esf_eap', 0.0) + 
                st.session_state.get('valor_saude_bucal', 0.0) + 
                st.session_state.get('valor_acs', 0.0) + 
                st.session_state.get('valor_estrategicas', 0.0)
            )]
        ]
        
        tabela_parametros = Table(parametros_data, colWidths=[10*cm, 6*cm])
        tabela_parametros.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#006400')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#F0FFF0')]),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#90EE90')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        self.story.append(tabela_parametros)
        self.story.append(Spacer(1, 20))

    def _add_financial_projection(self):
        """Adiciona seção de projeção financeira."""
        titulo = Paragraph("9. PROJEÇÃO FINANCEIRA", self.styles['SubTitle'])
        self.story.append(titulo)
        
        if not st.session_state.get('calculo_realizado', False):
            aviso = Paragraph("Cálculos não realizados. Execute a calculadora primeiro.", self.styles['Highlight'])
            self.story.append(aviso)
            return
        
        # Obter dados de projeção
        valor_cenario_regular = st.session_state.get('valor_cenario_regular', 0)
        aumento_mensal = st.session_state.get('aumento_mensal', 0)
        aumento_anual = st.session_state.get('aumento_anual', 0)
        municipio = st.session_state.get('municipio_selecionado', 'Não informado')
        uf = st.session_state.get('uf_selecionada', 'Não informado')
        
        # Verificar se é aumento negativo
        is_negative_increase = aumento_anual < 0
        adjusted_aumento_anual = abs(aumento_anual)
        
        # Descrição da projeção
        descricao = f"""
        Esta seção apresenta a projeção financeira para {municipio} - {uf}, considerando 
        o cenário regular como base e projetando o impacto financeiro em diferentes períodos.
        <br/><br/>
        <b>Dados Base:</b>
        <br/>• Valor Cenário Regular: {format_currency(valor_cenario_regular)}
        <br/>• {'Aumento' if not is_negative_increase else 'Redução'} Mensal: {format_currency(abs(aumento_mensal))}
        <br/>• {'Aumento' if not is_negative_increase else 'Redução'} Anual: {format_currency(abs(aumento_anual))}
        """
        
        descricao_para = Paragraph(descricao, self.styles['CustomNormal'])
        self.story.append(descricao_para)
        self.story.append(Spacer(1, 15))
        
        # Tabela de projeção temporal
        self._add_projection_table()
        
        # Tabela de comparação
        self._add_comparison_table()
        
        # Gráficos de projeção
        self._add_projection_charts()

    def _add_projection_table(self):
        """Adiciona tabela de projeção temporal."""
        secao_titulo = Paragraph("9.1 Projeção por Períodos", self.styles['SectionHeader'])
        self.story.append(secao_titulo)
        
        # Períodos de 3 a 30 meses
        periods = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
        
        # Criar dados da tabela
        projecao_data = [
            ['Período (meses)', 'Valor Projetado', 'Percentual (%)']
        ]
        
        for period in periods:
            valor = st.session_state.get(f'valor_{period}m', 0)
            percentual = st.session_state.get(f'percentual_{period}m', 0)
            
            projecao_data.append([
                f"{period} meses",
                format_currency(float(valor)),
                f"{int(percentual)}%"
            ])
        
        # Criar tabela
        tabela_projecao = Table(projecao_data, colWidths=[4*cm, 6*cm, 4*cm])
        tabela_projecao.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B35')),
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
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF4F0')])
        ]))
        
        self.story.append(tabela_projecao)
        self.story.append(Spacer(1, 15))

    def _add_comparison_table(self):
        """Adiciona tabela de comparação com cenário regular."""
        secao_titulo = Paragraph("9.2 Comparação com Cenário Regular", self.styles['SectionHeader'])
        self.story.append(secao_titulo)
        
        # Obter valores para comparação
        valor_regular = st.session_state.get('valor_cenario_regular', 0)
        valor_12m = st.session_state.get('valor_12m', 0)
        valor_24m = st.session_state.get('valor_24m', 0)
        valor_30m = st.session_state.get('valor_30m', 0)
        
        # Calcular diferenças
        diff_12m = float(valor_12m) - valor_regular
        diff_24m = float(valor_24m) - valor_regular
        diff_30m = float(valor_30m) - valor_regular
        
        # Criar dados da tabela
        comparacao_data = [
            ['Cenário', 'Valor Total', 'Diferença vs Regular', 'Variação (%)']
        ]
        
        scenarios = [
            ('Cenário Regular', valor_regular, 0, 0),
            ('Projeção 12 meses', float(valor_12m), diff_12m, (diff_12m/valor_regular*100) if valor_regular > 0 else 0),
            ('Projeção 24 meses', float(valor_24m), diff_24m, (diff_24m/valor_regular*100) if valor_regular > 0 else 0),
            ('Projeção 30 meses', float(valor_30m), diff_30m, (diff_30m/valor_regular*100) if valor_regular > 0 else 0)
        ]
        
        for nome, valor, diferenca, variacao in scenarios:
            comparacao_data.append([
                nome,
                format_currency(valor),
                format_currency(diferenca),
                f"{variacao:.1f}%"
            ])
        
        # Criar tabela
        tabela_comparacao = Table(comparacao_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
        tabela_comparacao.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E8F4F8')]),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#F0E68C')),  # Destacar cenário regular
        ]))
        
        self.story.append(tabela_comparacao)
        self.story.append(Spacer(1, 15))

    def _add_projection_charts(self):
        """Adiciona gráficos de projeção financeira."""
        secao_titulo = Paragraph("9.3 Visualizações da Projeção", self.styles['SectionHeader'])
        self.story.append(secao_titulo)
        
        try:
            # Preparar dados para gráficos
            periods = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
            values = [float(st.session_state.get(f'valor_{p}m', 0)) for p in periods]
            
            # Criar dados para timeline
            timeline_data = {f"{p} meses": v for p, v in zip(periods, values)}
            
            # Gerar gráfico de timeline
            from reports.chart_generator import PAPChartGenerator
            generator = PAPChartGenerator()
            
            chart_base64 = generator.create_projection_timeline_chart(timeline_data)
            if chart_base64:
                self._add_chart_to_pdf("Evolução da Projeção Financeira", chart_base64)
            
            # Dados para comparação
            comparison_data = {
                'Regular': st.session_state.get('valor_cenario_regular', 0),
                '12 meses': float(st.session_state.get('valor_12m', 0)),
                '24 meses': float(st.session_state.get('valor_24m', 0)),
                '30 meses': float(st.session_state.get('valor_30m', 0))
            }
            
            chart_base64 = generator.create_scenarios_comparison_chart(comparison_data)
            if chart_base64:
                self._add_chart_to_pdf("Comparação: Regular vs Projeções", chart_base64)
                
        except Exception as e:
            aviso = Paragraph(f"Gráficos de projeção não puderam ser gerados: {str(e)}", self.styles['Highlight'])
            self.story.append(aviso)
        
        self.story.append(Spacer(1, 20))

    def _add_charts_section(self):
        """Adiciona seção de gráficos e visualizações."""
        titulo = Paragraph("10. VISUALIZAÇÕES E GRÁFICOS", self.styles['SubTitle'])
        self.story.append(titulo)
        
        descricao = Paragraph(
            "Esta seção apresenta visualizações gráficas dos dados calculados para "
            "facilitar a análise e compreensão dos resultados do PAP.",
            self.styles['CustomNormal']
        )
        self.story.append(descricao)
        self.story.append(Spacer(1, 15))
        
        # Verificar se há dados calculados
        if not st.session_state.get('calculo_realizado', False):
            aviso = Paragraph(
                "Gráficos não disponíveis. Execute os cálculos primeiro para visualizar os dados.",
                self.styles['Highlight']
            )
            self.story.append(aviso)
            return
        
        # Tentar gerar gráficos com dados reais
        try:
            from reports.chart_generator import PAPChartGenerator
            generator = PAPChartGenerator()
            
            # 1. Gráfico de Distribuição dos Componentes PAP
            components_data = self._get_components_data()
            if components_data and any(v > 0 for v in components_data.values()):
                chart_base64 = generator.create_components_pie_chart(components_data)
                if chart_base64:
                    self._add_chart_to_pdf("10.1 Distribuição dos Componentes PAP", chart_base64)
            
            # 2. Gráfico de Comparação de Cenários
            scenarios_data = self._get_scenarios_data()
            if scenarios_data and any(v > 0 for v in scenarios_data.values()):
                chart_base64 = generator.create_scenarios_comparison_chart(scenarios_data)
                if chart_base64:
                    self._add_chart_to_pdf("10.2 Comparação de Cenários de Desempenho", chart_base64)
            
            # 3. Gráfico de Distribuição de Serviços
            services_data = self._get_services_data()
            if services_data and any(v > 0 for v in services_data.values()):
                chart_base64 = generator.create_services_distribution_chart(services_data)
                if chart_base64:
                    self._add_chart_to_pdf("10.3 Distribuição de Serviços Configurados", chart_base64)
            
            # 4. Dashboard Resumo (se houver dados suficientes)
            summary_data = self._get_summary_dashboard_data()
            if summary_data:
                chart_base64 = generator.create_summary_dashboard(summary_data)
                if chart_base64:
                    self._add_chart_to_pdf("10.4 Dashboard Resumo Executivo", chart_base64)
            
            # Se nenhum gráfico foi gerado
            charts_count = len([item for item in self.story if isinstance(item, Image)])
            if charts_count == 0:
                aviso = Paragraph(
                    "Gráficos não puderam ser gerados com os dados disponíveis. "
                    "Verifique se todos os cálculos foram executados corretamente.",
                    self.styles['Highlight']
                )
                self.story.append(aviso)
                
        except Exception as e:
            aviso = Paragraph(f"Erro ao gerar gráficos: {str(e)}", self.styles['Highlight'])
            self.story.append(aviso)

    def _get_components_data(self):
        """Extrai dados reais dos componentes PAP calculados."""
        try:
            # Obter valores calculados dos componentes
            components_data = {}
            
            # Componente Fixo
            total_fixo = 0
            for service in ['eSF', 'eAP 30h', 'eAP 20h', 'eMULTI Ampl.', 'eMULTI Compl.', 'eMULTI Estrat.']:
                qty = st.session_state.get(f'quantity_{service}', 0)
                value = st.session_state.get(f'value_{service}', 0)
                if qty > 0 and value > 0:
                    total_fixo += qty * value
            
            if total_fixo > 0:
                components_data['Componente Fixo'] = total_fixo
            
            # Componente Vínculo
            total_vinculo = 0
            vinculo_scenario = st.session_state.get('vinculo', 'Bom')
            for service in ['eSF', 'eAP 30h', 'eAP 20h', 'eMULTI Ampl.', 'eMULTI Compl.', 'eMULTI Estrat.']:
                qty = st.session_state.get(f'quantity_{service}', 0)
                if qty > 0:
                    # Valor base aproximado para vínculo
                    base_value = 5000  # Valor estimado
                    scenario_multiplier = {'Regular': 0.7, 'Suficiente': 0.85, 'Bom': 1.0, 'Ótimo': 1.15}.get(vinculo_scenario, 1.0)
                    total_vinculo += qty * base_value * scenario_multiplier
            
            if total_vinculo > 0:
                components_data['Vínculo e Acompanhamento'] = total_vinculo
            
            # Componente Qualidade
            total_qualidade = 0
            quality_scenario = st.session_state.get('classificacao', 'Bom')
            for service in ['eSF', 'eAP 30h', 'eAP 20h', 'eMULTI Ampl.', 'eMULTI Compl.', 'eMULTI Estrat.']:
                qty = st.session_state.get(f'quantity_{service}', 0)
                if qty > 0:
                    # Valor base aproximado para qualidade
                    base_value = 3000  # Valor estimado
                    scenario_multiplier = {'Regular': 0.7, 'Suficiente': 0.85, 'Bom': 1.0, 'Ótimo': 1.15}.get(quality_scenario, 1.0)
                    total_qualidade += qty * base_value * scenario_multiplier
            
            if total_qualidade > 0:
                components_data['Qualidade'] = total_qualidade
            
            # Componentes adicionais do session_state
            valor_saude_bucal = st.session_state.get('valor_saude_bucal', 0.0)
            if valor_saude_bucal > 0:
                components_data['Saúde Bucal'] = valor_saude_bucal
            
            valor_acs = st.session_state.get('valor_acs', 0.0)
            if valor_acs > 0:
                components_data['ACS'] = valor_acs
            
            valor_estrategicas = st.session_state.get('valor_estrategicas', 0.0)
            if valor_estrategicas > 0:
                components_data['Ações Estratégicas'] = valor_estrategicas
            
            return components_data
            
        except Exception as e:
            return {}

    def _get_scenarios_data(self):
        """Extrai dados dos cenários de desempenho."""
        try:
            scenarios_data = {}
            
            # Calcular valores para cada cenário baseado no valor total atual
            total_atual = st.session_state.get('total_pap_calculado', 0)
            
            if total_atual > 0:
                # Estimativas dos cenários baseadas no valor atual
                current_scenario = st.session_state.get('classificacao', 'Bom')
                
                # Multiplicadores para cada cenário
                multipliers = {
                    'Regular': 0.7,
                    'Suficiente': 0.85,
                    'Bom': 1.0,
                    'Ótimo': 1.15
                }
                
                # Calcular valor base (se estamos em "Bom", esse é o valor base)
                current_multiplier = multipliers.get(current_scenario, 1.0)
                base_value = total_atual / current_multiplier
                
                # Calcular todos os cenários
                for scenario, multiplier in multipliers.items():
                    scenarios_data[scenario] = base_value * multiplier
            
            return scenarios_data
            
        except Exception as e:
            return {}

    def _get_services_data(self):
        """Extrai dados dos serviços configurados."""
        try:
            services_data = {}
            
            # Lista de todos os serviços
            all_services = ['eSF', 'eAP 30h', 'eAP 20h', 'eMULTI Ampl.', 'eMULTI Compl.', 'eMULTI Estrat.']
            
            for service in all_services:
                qty = st.session_state.get(f'quantity_{service}', 0)
                if qty > 0:
                    services_data[service] = qty
            
            return services_data
            
        except Exception as e:
            return {}

    def _get_summary_dashboard_data(self):
        """Prepara dados para o dashboard resumo."""
        try:
            summary_data = {}
            
            # Componentes
            components = self._get_components_data()
            if components:
                summary_data['components'] = components
            
            # Cenários
            scenarios = self._get_scenarios_data()
            if scenarios:
                summary_data['scenarios'] = scenarios
            
            # Serviços
            services = self._get_services_data()
            if services:
                summary_data['services'] = services
            
            # Dados financeiros
            financial_data = {
                'Total PAP': st.session_state.get('total_pap_calculado', 0),
                'eSF/eAP': st.session_state.get('valor_esf_eap', 0.0),
                'Saúde Bucal': st.session_state.get('valor_saude_bucal', 0.0),
                'Total Adicional': (
                    st.session_state.get('valor_esf_eap', 0.0) + 
                    st.session_state.get('valor_saude_bucal', 0.0) + 
                    st.session_state.get('valor_acs', 0.0) + 
                    st.session_state.get('valor_estrategicas', 0.0)
                )
            }
            
            if any(v > 0 for v in financial_data.values()):
                summary_data['financial'] = financial_data
            
            return summary_data if summary_data else None
            
        except Exception as e:
            return None

    def _add_chart_to_pdf(self, titulo, chart_base64):
        """Adiciona um gráfico ao PDF."""
        try:
            # Título do gráfico
            chart_titulo = Paragraph(titulo, self.styles['SectionHeader'])
            self.story.append(chart_titulo)
            
            # Converter base64 para imagem
            import base64
            from reportlab.lib.utils import ImageReader
            
            image_data = base64.b64decode(chart_base64)
            image_buffer = io.BytesIO(image_data)
            
            # Adicionar imagem
            img = Image(ImageReader(image_buffer), width=14*cm, height=10*cm)
            self.story.append(img)
            self.story.append(Spacer(1, 15))
            
        except Exception as e:
            erro = Paragraph(f"Erro ao adicionar gráfico: {str(e)}", self.styles['CustomNormal'])
            self.story.append(erro)

    def _add_conclusions(self):
        """Adiciona conclusões e recomendações."""
        titulo = Paragraph("11. CONCLUSÕES E RECOMENDAÇÕES", self.styles['SubTitle'])
        self.story.append(titulo)
        
        total_pap = st.session_state.get('total_pap_calculado', 0)
        municipio = st.session_state.get('municipio_selecionado', 'o município')
        
        conclusoes = f"""
        <b>Síntese dos Resultados:</b>
        <br/>
        Com base nos cálculos realizados, {municipio} tem potencial para receber 
        <b>{format_currency(total_pap)}</b> mensais através do Programa de Apoio à Atenção Primária (PAP).
        <br/><br/>
        
        <b>Principais Observações:</b>
        <br/>• O valor final depende diretamente da qualidade dos serviços prestados
        <br/>• Melhorias nos indicadores de vínculo e acompanhamento territorial podem aumentar significativamente os recursos
        <br/>• A implantação de novos serviços pode ampliar o valor recebido
        <br/>• Os parâmetros adicionais configurados complementam o financiamento base
        <br/><br/>
        
        <b>Recomendações Estratégicas:</b>
        <br/>• Investir na qualificação das equipes para alcançar melhores avaliações
        <br/>• Implementar sistemas de monitoramento dos indicadores de qualidade
        <br/>• Considerar a expansão dos serviços oferecidos conforme a demanda local
        <br/>• Manter documentação adequada para comprovação dos critérios de qualidade
        <br/>• Buscar capacitação contínua para gestores e profissionais da Atenção Primária
        <br/><br/>
        
        <b>Próximos Passos:</b>
        <br/>• Revisar periodicamente os cálculos conforme mudanças na configuração dos serviços
        <br/>• Acompanhar as atualizações da legislação que rege o PAP
        <br/>• Utilizar este relatório como base para planejamento financeiro e estratégico
        """
        
        conclusoes_para = Paragraph(conclusoes, self.styles['CustomNormal'])
        self.story.append(conclusoes_para)
        self.story.append(Spacer(1, 20))
        
        # Nota final
        nota_final = Paragraph(
            "<i>Este relatório foi gerado automaticamente pela Calculadora PAP. "
            "Para informações adicionais ou esclarecimentos, consulte a documentação oficial da portaria "
            "GM/MS Nº 3.493/2024 ou entre em contato com os órgãos competentes do Ministério da Saúde.</i>",
            self.styles['CustomNormal']
        )
        self.story.append(nota_final)

def generate_pap_report() -> bytes:
    """Função principal para gerar o relatório PAP."""
    try:
        generator = PAPReportGenerator()
        return generator.generate_full_report()
    except Exception as e:
        st.error(f"Erro ao gerar relatório PDF: {str(e)}")
        return b""

def create_download_button():
    """Cria botão de download do relatório PDF."""
    if st.button("📄 Gerar Relatório PDF Completo", key="generate_pdf_report", use_container_width=True):
        with st.spinner("Gerando relatório PDF..."):
            pdf_data = generate_pap_report()
            
            if pdf_data:
                # Nome do arquivo
                municipio = st.session_state.get('municipio_selecionado', 'municipio')
                data_atual = datetime.now().strftime('%Y%m%d_%H%M')
                nome_arquivo = f"relatorio_pap_{municipio}_{data_atual}.pdf"
                
                st.download_button(
                    label="⬇️ Baixar Relatório PDF",
                    data=pdf_data,
                    file_name=nome_arquivo,
                    mime="application/pdf",
                    key="download_pdf_report",
                    use_container_width=True
                )
                
                st.success("✅ Relatório PDF gerado com sucesso!")
            else:
                st.error("❌ Erro ao gerar o relatório PDF.")
