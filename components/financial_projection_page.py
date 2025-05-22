"""
Módulo para a página de projeção financeira detalhada na Calculadora PAP.

NOTA: Este arquivo é considerado LEGADO e não é mais usado ativamente.
A funcionalidade foi migrada para o sistema de múltiplas páginas do Streamlit em:
/pages/01_Projeção_Financeira.py
"""
import streamlit as st
import pandas as pd
from utils import format_currency
from components.resource_projection import format_with_nan_check

def display_financial_projection_page():
    """Exibe a página de projeção financeira detalhada."""
    
    # Botão para voltar à página principal
    if st.button("← Voltar para Calculadora", key="btn_voltar"):
        st.session_state['page'] = 'main'
        st.experimental_rerun()
    
    st.title("Projeção Financeira em Parcelas")
    
    # Verificar se o cálculo foi realizado
    if not st.session_state.get('calculo_realizado', False):
        st.warning("É necessário realizar o cálculo na página principal primeiro.")
        st.stop()
    
    # Verificar se existe um aumento anual calculado
    if 'valor_cenario_regular' not in st.session_state:
        st.error("Por favor, realize o cálculo na página principal para gerar a projeção.")
        st.stop()
    
    # Recuperar o valor do aumento anual e outros dados relevantes
    total_parametros = st.session_state.get('valor_esf_eap', 0) + st.session_state.get('valor_saude_bucal', 0) + \
                       st.session_state.get('valor_acs', 0) + st.session_state.get('valor_estrategicas', 0)
    
    valor_cenario_regular = st.session_state.get('valor_cenario_regular', 0)
    aumento_mensal = total_parametros - valor_cenario_regular
    aumento_anual = aumento_mensal * 12
    
    # Obter informações do município
    if st.session_state.get('dados', {}) and 'resumosPlanosOrcamentarios' in st.session_state['dados'] and \
       len(st.session_state['dados']['resumosPlanosOrcamentarios']) > 0:
        municipio_selecionado = st.session_state['dados']['resumosPlanosOrcamentarios'][0].get('noMunicipio', 'Não informado')
        uf_selecionada = st.session_state['dados']['resumosPlanosOrcamentarios'][0].get('sgUf', 'Não informado')
    else:
        municipio_selecionado = "Não informado"
        uf_selecionada = "Não informado"
    
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
    
    # Organizando a interface em colunas para melhor visualização
    cols = st.columns(5)
    
    # Cria sliders para percentuais em 2 linhas de 5 colunas
    periods = [3, 6, 9, 12, 15, 18, 21, 24, 27, 30]
    
    for i, period in enumerate(periods[:5]):
        with cols[i]:
            st.session_state[f'percentual_{period}m'] = st.slider(
                f"{period} meses", 
                min_value=0, 
                max_value=100, 
                value=st.session_state.get(f'percentual_{period}m', period // 3 * 10),
                step=5,
                key=f"slider_{period}m"
            )
    
    cols = st.columns(5)
    for i, period in enumerate(periods[5:]):
        with cols[i]:
            st.session_state[f'percentual_{period}m'] = st.slider(
                f"{period} meses", 
                min_value=0, 
                max_value=100, 
                value=st.session_state.get(f'percentual_{period}m', period // 3 * 10),
                step=5,
                key=f"slider_{period}m"
            )
    
    # Função para atualizar os valores quando os percentuais são alterados
    def update_projection():
        for period in periods:
            st.session_state[f'valor_{period}m'] = adjusted_aumento_anual * (st.session_state[f'percentual_{period}m'] / 100)
        return True
    
    # Botão para recalcular os valores com base nos percentuais
    if st.button("Recalcular Valores com Percentuais", key="recalcular_projecao"):
        if update_projection():
            st.success("Valores recalculados com sucesso!")
    
    # Exibir tabela de valores projetados
    st.subheader("Valores Projetados por Período")
    
    # Inicializar ou atualizar valores calculados
    for period in periods:
        if f'valor_{period}m' not in st.session_state:
            st.session_state[f'valor_{period}m'] = adjusted_aumento_anual * (st.session_state[f'percentual_{period}m'] / 100)
    
    # Criar DataFrame para edição de valores
    df_projecao = pd.DataFrame({
        'Período (meses)': periods,
        'Valor Projetado': [st.session_state.get(f'valor_{p}m', 0) for p in periods],
        'Percentual (%)': [st.session_state.get(f'percentual_{p}m', 0) for p in periods]
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
            st.session_state[f'valor_{period}m'] = edited_df.iloc[i]['Valor Projetado']
            st.session_state[f'percentual_{period}m'] = edited_df.iloc[i]['Percentual (%)']
    
    # Visualização gráfica dos dados
    st.subheader("Visualização Gráfica")
    
    # Gráfico de barras para valores projetados
    st.bar_chart(
        pd.DataFrame({
            'Valor': [st.session_state.get(f'valor_{p}m', 0) for p in periods]
        }),
        y='Valor',
        use_container_width=True
    )
    
    # Resumo dos valores em tabela estilizada
    st.subheader("Resumo da Projeção Financeira")
    
    # Criar DataFrame para o resumo
    df_resumo = pd.DataFrame({
        'Período (meses)': periods,
        'Valor Projetado': [st.session_state.get(f'valor_{p}m', 0) for p in periods],
        'Percentual (%)': [st.session_state.get(f'percentual_{p}m', 0) for p in periods]
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
