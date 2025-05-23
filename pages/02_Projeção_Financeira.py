"""
Página de projeção financeira detalhada.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import format_currency

# Configuração da página
st.set_page_config(
    page_title="Projeção Financeira | Calculadora PAP",
    page_icon="📊",
    layout="wide"
)

# Função para formatar valores com verificação de NaN
def format_with_nan_check(x, format_str="R$ {:.2f}"):
    """Formata um valor com verificação de NaN."""
    if pd.isna(x) or np.isnan(x) if isinstance(x, float) else False:
        return "-"
    try:
        return format_str.format(x)
    except:
        return str(x)

# Título da página
st.title("Projeção Financeira Detalhada")

# Verificar se o cálculo foi realizado
if not st.session_state.get('calculo_realizado', False):
    st.warning("É necessário realizar o cálculo na página principal primeiro.")
    st.stop()

# Recuperar o valor do aumento anual e outros dados relevantes
valor_cenario_regular = st.session_state.get('valor_cenario_regular', 0)
aumento_mensal = st.session_state.get('aumento_mensal', 0)
aumento_anual = st.session_state.get('aumento_anual', 0)
municipio_selecionado = st.session_state.get('municipio_selecionado', "Não informado")
uf_selecionada = st.session_state.get('uf_selecionada', "Não informado")

# Verificar se é um aumento negativo
is_negative_increase = aumento_anual < 0
adjusted_aumento_anual = abs(aumento_anual)

# Cabeçalho com informações resumidas
st.markdown(f"""
<div style="background-color: #e1f5fe; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
    <h3 style="color: #01579b; margin-top: 0;">Detalhes da Projeção</h3>
    <p style="margin-bottom: 5px;"><b>Município:</b> {municipio_selecionado} - {uf_selecionada}</p>
    <p style="margin-bottom: 5px;"><b>Valor Regular:</b> {format_currency(valor_cenario_regular)}</p>
    <p style="margin-bottom: 5px;"><b>{'Aumento' if not is_negative_increase else 'Redução'} Mensal:</b> {format_currency(abs(aumento_mensal))}</p>
    <p style="margin-bottom: 0;"><b>{'Aumento' if not is_negative_increase else 'Redução'} Anual:</b> {format_currency(abs(aumento_anual))}</p>
</div>
""", unsafe_allow_html=True)

# Explicação sobre a projeção
st.markdown("""
<div style="background-color: #f1f8ff; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
    <p style="margin: 0; color: #0366d6;">
        <b>Sobre a Projeção:</b> Os valores abaixo representam a projeção financeira em diferentes períodos, 
        calculados como percentuais do valor anual projetado. Você pode ajustar os percentuais e depois recalcular 
        os valores, ou editar diretamente os valores projetados para cada período.
    </p>
</div>
""", unsafe_allow_html=True)

# Interface para edição de percentuais
st.subheader("Editar Percentuais Padrão")
st.markdown("Defina os percentuais padrão para cada período e clique em 'Recalcular' para atualizar os valores.")

# Lista de períodos
periods = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]

# Inicializar as variáveis de estado para os percentuais se não existirem
for period in periods:
    percent = period // 3 * 10  # 10%, 20%, 30%, etc.
    if f'percentual_{period}m' not in st.session_state:
        st.session_state[f'percentual_{period}m'] = percent
    elif isinstance(st.session_state[f'percentual_{period}m'], (list, tuple)):
        # Corrigir caso esteja armazenado como lista
        st.session_state[f'percentual_{period}m'] = int(percent)
    if f'valor_{period}m' not in st.session_state:
        st.session_state[f'valor_{period}m'] = adjusted_aumento_anual * (percent / 100)

# Organizando a interface em colunas para melhor visualização
cols = st.columns(5)

# Cria sliders para percentuais em 2 linhas de 5 colunas
for i, period in enumerate(periods[:5]):
    with cols[i]:
        # Garantir que o valor seja um inteiro
        value = st.session_state.get(f'percentual_{period}m', period // 3 * 10)
        if isinstance(value, (list, tuple)):
            value = period // 3 * 10  # valor padrão se for lista
        st.session_state[f'percentual_{period}m'] = st.slider(
            f"{period} meses", 
            min_value=0, 
            max_value=100, 
            value=int(value),
            step=5,
            key=f"slider_{period}m"
        )

cols = st.columns(5)
for i, period in enumerate(periods[5:]):
    with cols[i]:
        # Garantir que o valor seja um inteiro
        value = st.session_state.get(f'percentual_{period}m', period // 3 * 10)
        if isinstance(value, (list, tuple)):
            value = period // 3 * 10  # valor padrão se for lista
        st.session_state[f'percentual_{period}m'] = st.slider(
            f"{period} meses", 
            min_value=0, 
            max_value=100, 
            value=int(value),
            step=5,
            key=f"slider_{period}m"
        )

# Função para atualizar os valores quando os percentuais são alterados
def update_projection():
    for period in periods:
        percent_value = st.session_state[f'percentual_{period}m']
        # Converter para inteiro se for lista ou tuple
        if isinstance(percent_value, (list, tuple)):
            percent_value = int(period // 3 * 10)  # valor padrão
        # Garantir que é um número
        try:
            percent_value = float(percent_value)
        except (ValueError, TypeError):
            percent_value = period // 3 * 10  # valor padrão
            
        st.session_state[f'percentual_{period}m'] = int(percent_value)  # Garantir que é inteiro
        st.session_state[f'valor_{period}m'] = adjusted_aumento_anual * (percent_value / 100)
    return True

# Botão para recalcular os valores com base nos percentuais
if st.button("Recalcular Valores com Percentuais", key="recalcular_projecao"):
    if update_projection():
        st.success("Valores recalculados com sucesso!")

# Exibir tabela de valores projetados
st.subheader("Valores Projetados por Período")

# Criar DataFrame para edição de valores
df_projecao = pd.DataFrame({
    'Período (meses)': periods,
    'Valor Projetado': [float(st.session_state.get(f'valor_{p}m', 0)) for p in periods],
    'Percentual (%)': [int(st.session_state.get(f'percentual_{p}m', 0)) if isinstance(st.session_state.get(f'percentual_{p}m', 0), (int, float)) else 0 for p in periods]
})

# Exibir valores em uma interface editável
edited_df = st.data_editor(
    df_projecao,
    key="edit_projecao",
    column_config={
        "Período (meses)": st.column_config.NumberColumn(
            "Período (meses)",
            help="Período de tempo em meses",
            disabled=True,
            width="medium"
        ),
        "Valor Projetado": st.column_config.NumberColumn(
            "Valor Projetado (R$)",
            help="Valor projetado para o período",
            format="R$ %.2f",
            min_value=0.0,
            step=100.0,
            width="large"
        ),
        "Percentual (%)": st.column_config.NumberColumn(
            "Percentual (%)",
            help="Percentual do valor anual",
            format="%d%%",
            min_value=0,
            max_value=100,
            step=5,
            width="medium"
        )
    },
    hide_index=True,
    use_container_width=True
)

# Atualizar valores no session_state a partir da tabela editada
if edited_df is not None:
    for i, period in enumerate(periods):
        valor_projetado = edited_df.iloc[i]['Valor Projetado']
        percentual = edited_df.iloc[i]['Percentual (%)']
        
        # Garantir que os valores são numéricos
        try:
            st.session_state[f'valor_{period}m'] = float(valor_projetado)
        except (ValueError, TypeError):
            # Manter o valor anterior se houver erro
            pass
            
        # Garantir que o percentual é um inteiro
        try:
            percentual_value = int(percentual)
            st.session_state[f'percentual_{period}m'] = percentual_value
        except (ValueError, TypeError):
            # Manter o valor anterior se houver erro
            pass

# Visualização gráfica dos dados com Plotly
st.subheader("📊 Visualização Gráfica Interativa")

# Preparar dados para os gráficos
chart_data = pd.DataFrame({
    'Período': [f"{p} meses" for p in periods],
    'Período_num': periods,
    'Valor': [float(st.session_state.get(f'valor_{p}m', 0)) for p in periods],
    'Percentual': [int(st.session_state.get(f'percentual_{p}m', 0)) for p in periods]
})

# Criar abas para diferentes visualizações
tab1, tab2, tab3 = st.tabs(["📊 Gráfico de Barras", "📈 Gráfico de Linhas", "🥧 Gráfico de Pizza"])

with tab1:
    # Gráfico de barras interativo
    fig_bar = px.bar(
        chart_data, 
        x='Período', 
        y='Valor',
        title=f'Projeção Financeira por Período - {municipio_selecionado}',
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
    
    st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    # Gráfico de linhas com área
    fig_line = go.Figure()
    
    # Adicionar linha
    fig_line.add_trace(go.Scatter(
        x=chart_data['Período_num'],
        y=chart_data['Valor'],
        mode='lines+markers',
        name='Valor Projetado',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=8, color='#1f77b4'),
        fill='tonexty',
        fillcolor='rgba(31, 119, 180, 0.2)',
        hovertemplate='<b>%{x} meses</b><br>Valor: R$ %{y:,.2f}<extra></extra>'
    ))
    
    # Adicionar linha de tendência
    z = np.polyfit(chart_data['Período_num'], chart_data['Valor'], 1)
    p = np.poly1d(z)
    fig_line.add_trace(go.Scatter(
        x=chart_data['Período_num'],
        y=p(chart_data['Período_num']),
        mode='lines',
        name='Tendência',
        line=dict(color='red', width=2, dash='dash'),
        hovertemplate='Tendência: R$ %{y:,.2f}<extra></extra>'
    ))
    
    fig_line.update_layout(
        title=f'Evolução da Projeção Financeira - {municipio_selecionado}',
        xaxis_title="Período (meses)",
        yaxis_title="Valor Projetado (R$)",
        font=dict(size=12),
        height=500,
        hovermode='x unified',
        yaxis=dict(tickformat=',.0f'),
        xaxis=dict(tickmode='array', tickvals=periods, ticktext=[f"{p}m" for p in periods])
    )
    
    st.plotly_chart(fig_line, use_container_width=True)

with tab3:
    # Gráfico de pizza para distribuição dos valores
    fig_pie = px.pie(
        chart_data, 
        values='Valor', 
        names='Período',
        title=f'Distribuição da Projeção por Período - {municipio_selecionado}',
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
    
    st.plotly_chart(fig_pie, use_container_width=True)

# Gráfico adicional: Comparação com valor regular
st.subheader("📊 Comparação com Cenário Regular")

# Dados para comparação
comparison_data = pd.DataFrame({
    'Cenário': ['Valor Regular', 'Projeção 12 meses', 'Projeção 24 meses', 'Projeção 30 meses'],
    'Valor': [
        valor_cenario_regular,
        float(st.session_state.get('valor_12m', 0)),
        float(st.session_state.get('valor_24m', 0)),
        float(st.session_state.get('valor_30m', 0))
    ],
    'Tipo': ['Regular', 'Projeção', 'Projeção', 'Projeção']
})

fig_comparison = px.bar(
    comparison_data,
    x='Cenário',
    y='Valor',
    color='Tipo',
    title='Comparação: Cenário Regular vs Projeções',
    labels={'Valor': 'Valor (R$)', 'Cenário': 'Cenário'},
    color_discrete_map={'Regular': '#ff7f0e', 'Projeção': '#1f77b4'},
    text='Valor'
)

fig_comparison.update_traces(
    texttemplate='R$ %{text:,.0f}',
    textposition='outside'
)

fig_comparison.update_layout(
    xaxis_title="Cenários",
    yaxis_title="Valor (R$)",
    font=dict(size=12),
    height=400,
    yaxis=dict(tickformat=',.0f')
)

st.plotly_chart(fig_comparison, use_container_width=True)

# Resumo dos valores em tabela estilizada
st.subheader("Resumo da Projeção Financeira")

# Criar DataFrame para o resumo
df_resumo = pd.DataFrame({
    'Período (meses)': periods,
    'Valor Projetado': [float(st.session_state.get(f'valor_{p}m', 0)) for p in periods],
    'Percentual (%)': [int(st.session_state.get(f'percentual_{p}m', 0)) if isinstance(st.session_state.get(f'percentual_{p}m', 0), (int, float)) else 0 for p in periods]
})

# Função para estilizar a tabela de resumo
def highlight_resumo(row):
    color = f'background-color: {"#e1f5fe" if row.name % 2 == 0 else "#b3e5fc"}'
    return [color] * len(row)

def style_resumo_value(val):
    if isinstance(val, (int, float)):
        color = "#006064" if val > 0 else "#000"
        return f'color: {color}; font-weight: bold; text-align: right;'
    return ''

# Aplicar estilo à tabela de resumo
styled_resumo = df_resumo.style.format({
    'Valor Projetado': lambda x: format_with_nan_check(x),
    'Percentual (%)': '{:.0f}%'.format
}).map(style_resumo_value, subset=['Valor Projetado', 'Percentual (%)']).apply(highlight_resumo, axis=1)

# Exibir tabela de resumo com estilo melhorado
st.dataframe(
    styled_resumo,
    use_container_width=True,
    height=400
)

# Adicionar uma observação sobre o sinal negativo, se aplicável
if is_negative_increase:
    st.markdown(f"""
        <div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; margin-top: 10px;">
            <p style="margin: 0; color: #856404;"><b>Nota:</b> Os valores apresentados representam uma <b>redução</b> em relação ao cenário regular, 
            por isso o sinal negativo foi removido para facilitar a visualização. Considere estes valores como diminuição de receita.</p>
        </div>
        """, unsafe_allow_html=True)

# Explicação sobre como usar os resultados
st.markdown("""
### Como Utilizar Estes Resultados

Esta projeção financeira pode ser usada para:

1. **Planejamento Orçamentário**: Prepare seu orçamento com base nos valores esperados em diferentes períodos.
2. **Avaliação de Investimentos**: Determine quando recursos estarão disponíveis para novos investimentos.
3. **Apresentações**: Use estes dados em apresentações para gestores e tomadores de decisão.

Você pode exportar estes resultados usando o botão de download abaixo.
""")

# Preparar dados para download
csv = df_resumo.to_csv(index=False).encode('utf-8')

# Botão para download dos dados
st.download_button(
    label="Baixar Projeção como CSV",
    data=csv,
    file_name=f'projecao_financeira_{municipio_selecionado.replace(" ", "_")}_{uf_selecionada}.csv',
    mime='text/csv',
)
