# Sistema de Relatórios PDF - Calculadora PAP

## Visão Geral

O sistema de relatórios PDF da Calculadora PAP permite gerar documentos completos e profissionais com todos os cálculos, análises e visualizações realizadas pela aplicação.

## Estrutura do Sistema

### Módulos Principais

#### 1. `pdf_generator.py`
- **Função**: Motor principal de geração de PDF
- **Responsabilidades**:
  - Criar estrutura do documento PDF
  - Gerenciar layout e formatação
  - Coordenar inserção de conteúdo
  - Gerar arquivo final

#### 2. `chart_generator.py`
- **Função**: Geração de gráficos para PDF
- **Responsabilidades**:
  - Criar gráficos com matplotlib
  - Converter gráficos para imagens base64
  - Aplicar paleta de cores consistente
  - Otimizar gráficos para impressão

#### 3. `report_templates.py`
- **Função**: Templates e estilos padronizados
- **Responsabilidades**:
  - Definir estilos de texto e tabelas
  - Estabelecer paleta de cores oficial
  - Criar templates reutilizáveis
  - Padronizar layouts

#### 4. `data_formatter.py`
- **Função**: Formatação específica de dados
- **Responsabilidades**:
  - Extrair dados do session_state
  - Formatar valores monetários
  - Criar estruturas de dados para tabelas
  - Validar integridade dos dados

## Como Usar

### 1. Pré-requisitos
- Execute a calculadora e realize os cálculos
- Certifique-se de que as dependências estão instaladas:
  ```bash
  pip install reportlab matplotlib pillow
  ```

### 2. Geração do Relatório
1. Na página de calculadora, após realizar os cálculos
2. Role até a seção "📄 Relatório PDF"
3. Clique em "📄 Gerar Relatório PDF Completo"
4. Aguarde o processamento
5. Clique em "⬇️ Baixar Relatório PDF"

### 3. Conteúdo do Relatório

#### Seções Incluídas:
1. **Página de Capa**
   - Título e identificação
   - Dados do município
   - Data de geração

2. **Informações do Município**
   - Dados básicos
   - População e IED
   - Competência analisada

3. **Fundamentação Legal**
   - Base legal (Portaria 3.493/2024)
   - Componentes do PAP
   - Metodologia aplicada

4. **Configuração dos Serviços**
   - Serviços selecionados
   - Quantidades configuradas
   - Parâmetros de qualidade

5. **Cálculos Detalhados**
   - Todos os componentes PAP
   - Tabelas de valores
   - Subtotais e totais

6. **Análise de Cenários**
   - Comparação de desempenho
   - Projeções financeiras
   - Gráficos comparativos

7. **Resumo Executivo**
   - Total PAP calculado
   - Principais insights
   - Recomendações

## Personalização

### Cores e Estilos
As cores podem ser personalizadas no arquivo `report_templates.py`:

```python
COLORS = {
    'primary': '#4682B4',      # Azul institucional
    'secondary': '#006400',     # Verde saúde
    'warning': '#FFA500',       # Laranja alerta
    'danger': '#8B0000',        # Vermelho crítico
    # ... outras cores
}
```

### Adicionando Novas Seções
Para adicionar uma nova seção ao relatório:

1. Crie o método na classe `PAPReportGenerator`:
```python
def _add_nova_secao(self):
    titulo = Paragraph("NOVA SEÇÃO", self.styles['SubTitle'])
    self.story.append(titulo)
    # ... adicionar conteúdo
```

2. Chame o método em `generate_full_report()`:
```python
self._add_nova_secao()
```

### Novos Tipos de Gráfico
Para adicionar um novo tipo de gráfico:

1. Implemente o método em `PAPChartGenerator`:
```python
def create_novo_grafico(self, data):
    # Implementação do gráfico
    return self._fig_to_base64(fig)
```

2. Adicione ao `generate_chart_for_pdf()`:
```python
elif chart_type == 'novo_grafico':
    return generator.create_novo_grafico(data)
```

## Especificações Técnicas

### Formato do PDF
- **Tamanho**: A4 (210 x 297 mm)
- **Margens**: 2cm (laterais), 3cm (superior), 2.5cm (inferior)
- **Fontes**: Helvetica (padrão), Helvetica-Bold (títulos)
- **Resolução**: 300 DPI para gráficos

### Performance
- **Tempo médio**: 3-8 segundos (dependendo da complexidade)
- **Tamanho típico**: 500KB - 2MB
- **Páginas**: 6-12 páginas (dependendo dos dados)

### Compatibilidade
- **Navegadores**: Todos os principais
- **Dispositivos**: Desktop, tablet, mobile
- **Sistemas**: Windows, macOS, Linux

## Troubleshooting

### Problemas Comuns

#### 1. "Erro ao carregar módulo de relatórios"
**Causa**: Dependências não instaladas
**Solução**: Execute `pip install reportlab matplotlib pillow`

#### 2. "Os cálculos não foram realizados"
**Causa**: Relatório gerado antes dos cálculos
**Solução**: Execute a calculadora primeiro

#### 3. "Erro ao gerar relatório PDF"
**Causa**: Dados incompletos ou corrompidos
**Solução**: Verifique se todos os dados necessários estão preenchidos

#### 4. PDF em branco ou incompleto
**Causa**: Erro na formatação dos dados
**Solução**: Verifique os logs para erros específicos

### Debug e Logs
Para habilitar logs detalhados, adicione no início do arquivo:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Roadmap

### Funcionalidades Futuras
- [ ] Relatórios customizáveis (escolher seções)
- [ ] Templates alternativos de layout
- [ ] Exportação para Excel/CSV
- [ ] Relatórios comparativos entre municípios
- [ ] Gráficos interativos (quando possível)
- [ ] Marca d'água personalizada
- [ ] Assinatura digital

### Melhorias Planejadas
- [ ] Otimização de performance
- [ ] Cache de templates
- [ ] Geração assíncrona
- [ ] Progress bar detalhado
- [ ] Validação avançada de dados

## Suporte

Para problemas ou sugestões relacionadas ao sistema de relatórios:

1. Verifique os logs da aplicação
2. Consulte a seção de troubleshooting
3. Reporte issues específicas com dados de reprodução

## Changelog

### v1.0.0 (2024)
- ✅ Implementação inicial
- ✅ Geração de PDF básico
- ✅ Templates padronizados
- ✅ Gráficos integrados
- ✅ Sistema de formatação de dados
- ✅ Validação de integridade
