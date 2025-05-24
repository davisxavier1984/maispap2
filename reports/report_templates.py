"""
Templates e layouts para relatórios PDF da Calculadora PAP.
"""
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import TableStyle

class PAPReportTemplates:
    """Classe com templates padronizados para relatórios PAP."""
    
    # Paleta de cores oficial
    COLORS = {
        'primary': colors.HexColor('#4682B4'),      # Azul institucional
        'secondary': colors.HexColor('#006400'),     # Verde saúde
        'warning': colors.HexColor('#FFA500'),       # Laranja alerta
        'danger': colors.HexColor('#8B0000'),        # Vermelho crítico
        'success': colors.HexColor('#228B22'),       # Verde sucesso
        'light_blue': colors.HexColor('#F0F8FF'),    # Azul claro
        'light_green': colors.HexColor('#F0FFF0'),   # Verde claro
        'light_gray': colors.HexColor('#F5F5F5'),    # Cinza claro
        'dark_gray': colors.HexColor('#696969'),     # Cinza escuro
    }
    
    @classmethod
    def get_title_style(cls):
        """Retorna estilo para títulos principais."""
        return ParagraphStyle(
            name='TitleStyle',
            fontSize=18,
            textColor=cls.COLORS['primary'],
            alignment=TA_CENTER,
            spaceBefore=20,
            spaceAfter=25,
            fontName='Helvetica-Bold'
        )
    
    @classmethod
    def get_subtitle_style(cls):
        """Retorna estilo para subtítulos."""
        return ParagraphStyle(
            name='SubtitleStyle',
            fontSize=14,
            textColor=cls.COLORS['primary'],
            alignment=TA_LEFT,
            spaceBefore=18,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
    
    @classmethod
    def get_section_header_style(cls):
        """Retorna estilo para cabeçalhos de seção."""
        return ParagraphStyle(
            name='SectionHeaderStyle',
            fontSize=12,
            textColor=cls.COLORS['secondary'],
            alignment=TA_LEFT,
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
    
    @classmethod
    def get_normal_style(cls):
        """Retorna estilo para texto normal."""
        return ParagraphStyle(
            name='NormalStyle',
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceBefore=6,
            spaceAfter=6,
            fontName='Helvetica',
            leading=12
        )
    
    @classmethod
    def get_highlight_style(cls):
        """Retorna estilo para texto destacado."""
        return ParagraphStyle(
            name='HighlightStyle',
            fontSize=11,
            textColor=cls.COLORS['danger'],
            alignment=TA_LEFT,
            spaceBefore=8,
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
    
    @classmethod
    def get_info_box_style(cls):
        """Retorna estilo para caixas de informação."""
        return ParagraphStyle(
            name='InfoBoxStyle',
            fontSize=10,
            textColor=cls.COLORS['dark_gray'],
            alignment=TA_LEFT,
            spaceBefore=8,
            spaceAfter=8,
            fontName='Helvetica',
            leftIndent=10,
            rightIndent=10,
            borderWidth=1,
            borderColor=cls.COLORS['light_gray']
        )
    
    @classmethod
    def get_standard_table_style(cls):
        """Retorna estilo padrão para tabelas."""
        return TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), cls.COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Corpo da tabela
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, cls.COLORS['light_blue']]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ])
    
    @classmethod
    def get_financial_table_style(cls):
        """Retorna estilo específico para tabelas financeiras."""
        return TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), cls.COLORS['secondary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Corpo da tabela
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, cls.COLORS['light_green']]),
            
            # Alinhamento de valores monetários à direita
            ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
            ('ALIGN', (-2, 1), (-2, -1), 'RIGHT'),
            
            # Padding
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ])
    
    @classmethod
    def get_summary_table_style(cls):
        """Retorna estilo para tabelas de resumo."""
        return TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), cls.COLORS['warning']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
            
            # Corpo da tabela
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            
            # Linha de total (última linha)
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('BACKGROUND', (0, -1), (-1, -1), cls.COLORS['light_gray']),
            ('TEXTCOLOR', (0, -1), (-1, -1), cls.COLORS['danger']),
            
            # Bordas e alinhamento
            ('GRID', (0, 0), (-1, -1), 1.5, colors.black),
            ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ])
    
    @classmethod
    def get_comparison_table_style(cls):
        """Retorna estilo para tabelas de comparação de cenários."""
        return TableStyle([
            # Cabeçalho
            ('BACKGROUND', (0, 0), (-1, 0), cls.COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Corpo da tabela
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            # Alinhamento específico por coluna
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),    # Primeira coluna à esquerda
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'), # Demais colunas centralizadas
            ('ALIGN', (-1, 1), (-1, -1), 'RIGHT'), # Última coluna à direita
            
            # Cores alternadas nas linhas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, cls.COLORS['light_blue']]),
            
            # Padding
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ])
    
    @classmethod
    def get_scenario_colors(cls):
        """Retorna cores específicas para cada cenário."""
        return {
            'Regular': cls.COLORS['danger'],
            'Suficiente': cls.COLORS['warning'],
            'Bom': cls.COLORS['secondary'],
            'Ótimo': cls.COLORS['primary']
        }
    
    @classmethod
    def get_component_colors(cls):
        """Retorna cores específicas para cada componente PAP."""
        return {
            'Componente Fixo': cls.COLORS['primary'],
            'Vínculo e Acompanhamento': cls.COLORS['secondary'],
            'Qualidade': cls.COLORS['success'],
            'Implantação e Manutenção': cls.COLORS['warning'],
            'Saúde Bucal': cls.COLORS['danger'],
            'Per Capita': colors.HexColor('#9370DB')
        }
    
    @classmethod
    def create_legal_text_template(cls):
        """Retorna template para texto legal padronizado."""
        return """
        <b>Fundamentação Legal:</b><br/>
        Este relatório foi elaborado com base na <b>Portaria GM/MS Nº 3.493, de 10 de abril de 2024</b>, 
        que institui incentivo financeiro federal de custeio para o fortalecimento da Atenção Primária à Saúde.
        <br/><br/>
        <b>Metodologia:</b><br/>
        Os cálculos seguem rigorosamente os critérios estabelecidos na portaria, considerando:
        <br/>• Estratificação por Índice de Equidade (IED)
        <br/>• Parâmetros de qualidade e desempenho
        <br/>• Tipologia e quantidade de serviços
        <br/>• População cadastrada e coberta
        <br/><br/>
        <b>Validade:</b><br/>
        Os valores apresentados são válidos para a competência informada e podem sofrer alterações 
        conforme atualizações nos dados oficiais ou modificações na legislação vigente.
        """
    
    @classmethod
    def create_disclaimer_template(cls):
        """Retorna template para disclaimer padronizado."""
        return """
        <i><b>Importante:</b> Este relatório foi gerado automaticamente pela Calculadora PAP 
        e tem caráter informativo. Para fins oficiais, consulte sempre as fontes primárias 
        e a legislação vigente. Os valores aqui apresentados são estimativas baseadas nos 
        parâmetros informados e podem não refletir exatamente os valores reais a serem 
        repassados pelo Ministério da Saúde.</i>
        """
    
    @classmethod
    def create_contact_info_template(cls):
        """Retorna template para informações de contato."""
        return """
        <b>Suporte e Informações:</b><br/>
        Para esclarecimentos sobre os cálculos ou uso da aplicação:<br/>
        • Consulte a documentação oficial da Portaria GM/MS Nº 3.493/2024<br/>
        • Acesse o portal oficial do Ministério da Saúde<br/>
        • Entre em contato com a Secretaria de Atenção Primária à Saúde (SAPS)
        """

class PDFLayoutHelper:
    """Classe auxiliar para layout de PDFs."""
    
    @staticmethod
    def create_two_column_data(left_data, right_data):
        """Cria dados para layout de duas colunas."""
        max_len = max(len(left_data), len(right_data))
        
        # Preencher listas menores com strings vazias
        left_data.extend([''] * (max_len - len(left_data)))
        right_data.extend([''] * (max_len - len(right_data)))
        
        return list(zip(left_data, right_data))
    
    @staticmethod
    def format_large_number(number):
        """Formata números grandes com separadores."""
        return f"{number:,.0f}".replace(',', '.')
    
    @staticmethod
    def create_progress_bar_data(percentage, width=20):
        """Cria dados para barra de progresso em texto."""
        filled = int(width * percentage / 100)
        empty = width - filled
        return '█' * filled + '░' * empty + f' {percentage:.1f}%'
    
    @staticmethod
    def calculate_table_widths(num_columns, page_width=18):
        """Calcula larguras automáticas para colunas da tabela."""
        base_width = page_width / num_columns
        return [base_width] * num_columns
    
    @staticmethod
    def split_long_text(text, max_length=50):
        """Divide texto longo em múltiplas linhas."""
        if len(text) <= max_length:
            return text
        
        words = text.split(' ')
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_length:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return '<br/>'.join(lines)
