import streamlit as st
import pandas as pd
import json
#import plotly.graph_objects as go
from utils import TRADUCOES, formatar_valor, style_metric_cards, metric_card, criar_tabela_classificacao, CORES_CLASSIFICACAO

DATA_FILE = "data.json"

VALORES_POR_TIPO_E_CLASSIFICACAO = {
    "Equipe de Saúde da Família (eSF) 40h": {
        "Ótimo": 8000,
        "Bom": 6000,
        "Suficiente": 4000,
        "Regular": 2000
    },
    "Equipe de Atenção Primária (eAP) 30h": {
        "Ótimo": 4000,
        "Bom": 3000,
        "Suficiente": 2000,
        "Regular": 1000
    },
    "Equipe de Atenção Primária (eAP) 20h": {
        "Ótimo": 3000,
        "Bom": 2250,
        "Suficiente": 1500,
        "Regular": 750
    }
}

def obter_valor_unitario(tipo_equipe, classificacao):
    return VALORES_POR_TIPO_E_CLASSIFICACAO[tipo_equipe][classificacao]

def main():
    st.title("Equipes de Saúde da Família (eSF) e Equipes de Atenção Primária (eAP)")
    style_metric_cards()

    try:
        with open(DATA_FILE, 'r') as f:
            dados = json.load(f)
    except FileNotFoundError:
        st.error("Arquivo data.json não encontrado.")
        return

    if not dados:
        st.error("Dados inválidos no arquivo.")
        return

    dados_pagamentos = dados.get("pagamentos", [])

    if not dados_pagamentos:
        st.error("Nenhum dado encontrado para pagamentos.")
        return

    df = pd.DataFrame(dados_pagamentos)

    # Conversão de tipos
    colunas_esf = {
        'quantitativas': [
            'qtEsfCredenciado', 'qtEsfHomologado', 'qtEsfTotalPgto',
            'qtEsf100pcPgto', 'qtEsf75pcPgto', 'qtEsf50pcPgto', 'qtEsf25pcPgto'
        ],
        'monetarias': [
            'vlFixoEsf', 'vlVinculoEsf', 'vlQualidadeEsf',
            'vlPagamentoEsf', 'vlPagamentoImplantacaoEsf'
        ]
    }

    colunas_eap = {
        'quantitativas': [
            'qtEapCredenciadas', 'qtEapHomologado', 'qtEapTotalPgto',
            'qtEap20hCompletas', 'qtEap20hIncompletas', 'qtEap30hCompletas', 'qtEap30hIncompletas'
        ],
        'monetarias': [
            'vlFixoEap', 'vlVinculoEap', 'vlQualidadeEap',
            'vlTotalEap', 'vlPagamentoEap', 'vlPagamentoImplantacaoEap'
        ]
    }

    def converter_colunas(df, colunas):
        for col in colunas['quantitativas']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        for col in colunas['monetarias']:
            if col in df.columns:
                df[col] = (
                    df[col].astype(str)
                    .str.replace('.', '', regex=False)
                    .str.replace(',', '.', regex=False)
                    .astype(float)
                )
        return df

    df = converter_colunas(df, colunas_esf)
    df = converter_colunas(df, colunas_eap)

    # Converte as colunas de população e ano de referência
    if 'qtPopulacao' in df.columns:
        df['qtPopulacao'] = pd.to_numeric(df['qtPopulacao'], errors='coerce').fillna(0).astype(int)
    if 'nuAnoRefPopulacaoIbge' in df.columns:
        df['nuAnoRefPopulacaoIbge'] = pd.to_numeric(df['nuAnoRefPopulacaoIbge'], errors='coerce').fillna(0).astype(int)

    # Cálculo de métricas
    metricas = {
        'ESF': {
            'quantitativas': {col: df[col].sum() for col in colunas_esf['quantitativas'] if col in df.columns},
            'monetarias': {col: df[col].sum() for col in colunas_esf['monetarias'] if col in df.columns}
        },
        'EAP': {
            'quantitativas': {col: df[col].sum() for col in colunas_eap['quantitativas'] if col in df.columns},
            'monetarias': {col: df[col].sum() for col in colunas_eap['monetarias'] if col in df.columns}
        }
    }

    # Número de equipes para cálculo das tabelas
    num_equipes_esf = metricas['ESF']['quantitativas'].get('qtEsfTotalPgto', 0)
    num_equipes_eap_20h = metricas['EAP']['quantitativas'].get('qtEap20hCompletas', 0)
    num_equipes_eap_30h = metricas['EAP']['quantitativas'].get('qtEap30hCompletas', 0)

    # 1 - CARDS
    # População e ano de referência em cards
    st.subheader("Informações Gerais")
    populacao = df['qtPopulacao'].iloc[0] if 'qtPopulacao' in df.columns else 0
    ano_referencia = df['nuAnoRefPopulacaoIbge'].iloc[0] if 'nuAnoRefPopulacaoIbge' in df.columns else 0

    cols_info = st.columns(2)
    with cols_info[0]:
        metric_card("População IBGE", f"{populacao:,}".replace(",", "."))
    with cols_info[1]:
        metric_card("Ano Referência Populacional", ano_referencia)
    
    # Input para código IBGE do município
    codigo_ibge_atual = None
    if 'coMunicipio' in df.columns:
        codigo_ibge_atual = str(df['coMunicipio'].iloc[0])
    elif 'coIbge' in df.columns:
        codigo_ibge_atual = str(df['coIbge'].iloc[0])

    codigo_ibge_input = st.text_input(
        "Código IBGE do Município",
        value=codigo_ibge_atual if codigo_ibge_atual else "",
        help="Digite o código IBGE do município com 7 dígitos"
    )

    if codigo_ibge_input and len(codigo_ibge_input.strip()) != 7:
        st.warning("O código IBGE deve conter exatamente 7 dígitos")

    # Adiciona as novas colunas ao dicionário de traduções
    TRADUCOES.update({
        "qtPopulacao": "População IBGE",
        "nuAnoRefPopulacaoIbge": "Ano Referência Populacional"
    })

    # Classificações no topo
    classificacoes_cols = ['dsFaixaIndiceEquidadeEsfEap',
                           'dsClassificacaoVinculoEsfEap',
                           'dsClassificacaoQualidadeEsfEap']

    if all(col in df.columns for col in classificacoes_cols):
        st.subheader("Classificações")
        cols = st.columns(3)
        with cols[0]:
            metric_card("Índice de Equidade", df['dsFaixaIndiceEquidadeEsfEap'].iloc[0])
        with cols[1]:
            metric_card("Classificação de Vínculo", df['dsClassificacaoVinculoEsfEap'].iloc[0])
        with cols[2]:
            metric_card("Classificação de Qualidade", df['dsClassificacaoQualidadeEsfEap'].iloc[0])

    st.divider()

    # --- Container para ESF ---
    with st.container():
        st.subheader("Equipes de Saúde da Família (eSF)")

        # Exibir métricas de ESF
        st.write("**Equipes ESF (Métricas)**")
        todas_metricas_esf = []
        for k, v in metricas['ESF']['quantitativas'].items():
            if k not in ['qtEsf100pcPgto', 'qtEsf75pcPgto', 'qtEsf50pcPgto', 'qtEsf25pcPgto']:
                todas_metricas_esf.append((TRADUCOES[k], f"{v:,}".replace(",", ".")))
        for k, v in metricas['ESF']['monetarias'].items():
            todas_metricas_esf.append((TRADUCOES[k], formatar_valor(v)))

        cols_esf = st.columns(4)
        for i, (titulo, valor) in enumerate(todas_metricas_esf):
            with cols_esf[i % 4]:
                metric_card(titulo, valor)

        st.divider()

        # 2 - GRÁFICOS DE PIZZA
        st.write("**Gráficos de Pizza - ESF**")
        # Gráfico de Pizza para ESF (Pagamentos)
        
        labels = ['ESF 100% Pagas', 'ESF 75% Pagas', 'ESF 50% Pagas', 'ESF 25% Pagas']
        values = [
            metricas['ESF']['quantitativas'].get('qtEsf100pcPgto', 0),
            metricas['ESF']['quantitativas'].get('qtEsf75pcPgto', 0),
            metricas['ESF']['quantitativas'].get('qtEsf50pcPgto', 0),
            metricas['ESF']['quantitativas'].get('qtEsf25pcPgto', 0)
        ]

        #fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
        # fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=14,
        #                 marker=dict(colors=['#2ca02c', '#ff7f0e', '#d62728', '#9467bd'], line=dict(color='#FFFFFF', width=2)))
        # fig.update_layout(title_text='Distribuição de Pagamentos das ESF', title_x=0.5,
        #                 title_font=dict(size=18),
        #                 font=dict(size=16))
        # st.plotly_chart(fig)

        # st.divider()

        # 3 - TABELAS
        # --- Tabela eSF ---
        st.write("**Equipe de Saúde da Família (eSF) 40h**")
        criar_tabela_classificacao(df,'Equipe de Saúde da Família (eSF) 40h', num_equipes_esf, num_equipes_eap_20h, num_equipes_eap_30h)

        # 4 - GRÁFICOS DE COLUNA - Não há para eSF

        st.divider()

    # --- Container para EAP ---
    with st.container():
        st.subheader("Equipes de Atenção Primária (eAP)")

        # Exibir métricas de EAP
        st.write("**Equipes EAP (Métricas)**")
        todas_metricas_eap = []
        for k, v in metricas['EAP']['quantitativas'].items():
            todas_metricas_eap.append((TRADUCOES[k], f"{v:,}".replace(",", ".")))

        for k, v in metricas['EAP']['monetarias'].items():
            todas_metricas_eap.append((TRADUCOES[k], formatar_valor(v)))

        cols_eap = st.columns(4)
        for i, (titulo, valor) in enumerate(todas_metricas_eap):
            with cols_eap[i % 4]:
                metric_card(titulo, valor)

        st.divider()

        # 2 - GRÁFICOS DE PIZZA
        st.write("**Gráficos de Pizza - EAP**")
        # Gráficos de Pizza para EAP
        # EAP 20h
        # if metricas['EAP']['quantitativas'].get('qtEap20hCompletas', 0) > 0 or metricas['EAP']['quantitativas'].get('qtEap20hIncompletas', 0) > 0:
        #     st.write("**EAP 20h**")
        #     labels_eap_20h = ['Completas', 'Incompletas']
        #     values_eap_20h = [
        #         metricas['EAP']['quantitativas'].get('qtEap20hCompletas', 0),
        #         metricas['EAP']['quantitativas'].get('qtEap20hIncompletas', 0)
        #     ]
        #     fig_eap_20h = go.Figure(data=[go.Pie(labels=labels_eap_20h, values=values_eap_20h, hole=.3)])
        #     fig_eap_20h.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=14,
        #                             marker=dict(colors=['#2ca02c', '#d62728'], line=dict(color='#FFFFFF', width=2)))
        #     fig_eap_20h.update_layout(title_text='Distribuição EAP 20h', title_x=0.5, showlegend=True,
        #                             title_font=dict(size=18),
        #                             font=dict(size=16))
        #     st.plotly_chart(fig_eap_20h)

        # EAP 30h
        # if metricas['EAP']['quantitativas'].get('qtEap30hCompletas', 0) > 0 or metricas['EAP']['quantitativas'].get('qtEap30hIncompletas', 0) > 0:
        #     st.write("**EAP 30h**")
        #     labels_eap_30h = ['Completas', 'Incompletas']
        #     values_eap_30h = [
        #         metricas['EAP']['quantitativas'].get('qtEap30hCompletas', 0),
        #         metricas['EAP']['quantitativas'].get('qtEap30hIncompletas', 0)
        #     ]
        #     fig_eap_30h = go.Figure(data=[go.Pie(labels=labels_eap_30h, values=values_eap_30h, hole=.3)])
        #     fig_eap_30h.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=14,
        #                             marker=dict(colors=['#2ca02c', '#d62728'], line=dict(color='#FFFFFF', width=2)))
        #     fig_eap_30h.update_layout(title_text='Distribuição EAP 30h', title_x=0.5, showlegend=True,
        #                             title_font=dict(size=18),
        #                             font=dict(size=16))
        #     st.plotly_chart(fig_eap_30h)

        st.divider()

        # 3 - TABELAS
        # --- Tabela eAP 20h ---
        if num_equipes_eap_20h > 0:
            st.write("**Equipe de Atenção Primária (eAP) 20h**")
            criar_tabela_classificacao(df, "Equipe de Atenção Primária (eAP) 20h", num_equipes_esf, num_equipes_eap_20h, num_equipes_eap_30h)

        # --- Tabela eAP 30h ---
        if num_equipes_eap_30h > 0:
            st.write("**Equipe de Atenção Primária (eAP) 30h**")
            criar_tabela_classificacao(df, "Equipe de Atenção Primária (eAP) 30h", num_equipes_esf, num_equipes_eap_20h, num_equipes_eap_30h)

        # 4 - GRÁFICOS DE COLUNA - Não há para eAP

        st.divider()

    # --- Container para Resumo ---
    with st.container():
        st.subheader("Resumo")

        # 1 - CARDS - Não há cards específicos para o resumo

        # 2 - GRÁFICOS DE PIZZA - Não há gráficos de pizza para o resumo

        # 3 - TABELAS
        # --- Tabela Resumo ---
        st.write("**Tabela Resumo**")
        classificacoes = ['Ótimo', 'Bom', 'Suficiente', 'Regular']

        # Dicionários para armazenar os totais por classificação
        totais_esf = {clf: {"Total Geral": 0} for clf in classificacoes}
        totais_eap_20h = {clf: {"Total Geral": 0} for clf in classificacoes}
        totais_eap_30h = {clf: {"Total Geral": 0} for clf in classificacoes}

        # Calcular totais para eSF
        for clf in classificacoes:
            valor_unitario_esf = obter_valor_unitario("Equipe de Saúde da Família (eSF) 40h", clf)
            totais_esf[clf]["Total Geral"] = valor_unitario_esf * num_equipes_esf * 2

        # Calcular totais para eAP 20h
        if num_equipes_eap_20h > 0:
            for clf in classificacoes:
                valor_unitario_eap_20h = obter_valor_unitario("Equipe de Atenção Primária (eAP) 20h", clf)
                totais_eap_20h[clf]["Total Geral"] = valor_unitario_eap_20h * num_equipes_eap_20h * 2

        # Calcular totais para eAP 30h
        if num_equipes_eap_30h > 0:
            for clf in classificacoes:
                valor_unitario_eap_30h = obter_valor_unitario("Equipe de Atenção Primária (eAP) 30h", clf)
                totais_eap_30h[clf]["Total Geral"] = valor_unitario_eap_30h * num_equipes_eap_30h * 2

        # Construir a tabela resumo
        tabela_data_resumo = []
        for clf in classificacoes:
            tabela_data_resumo.append({
                "Classificação": clf,
                "Total Geral (R$) eSF": totais_esf[clf]["Total Geral"],
                "Total Geral (R$) eAP 20h": totais_eap_20h[clf]["Total Geral"],
                "Total Geral (R$) eAP 30h": totais_eap_30h[clf]["Total Geral"],
                "Total Geral (R$)": totais_esf[clf]["Total Geral"] + totais_eap_20h[clf]["Total Geral"] + totais_eap_30h[clf]["Total Geral"]
            })

        df_tabela_resumo = pd.DataFrame(tabela_data_resumo)

        # Aplicar estilo para as cores das linhas
        def _color_row(row):
            if row['Classificação'] == 'Ótimo':
                return ['background-color: #90caf9'] * len(row)
            elif row['Classificação'] == 'Bom':
                return ['background-color: #90ee90'] * len(row)
            elif row['Classificação'] == 'Suficiente':
                return ['background-color: #fff59d'] * len(row)
            elif row['Classificação'] == 'Regular':
                return ['background-color: #f28b82'] * len(row)
            else:
                return [''] * len(row)

        # Formatar valores monetários nas tabelas
        def formatar_tabela(df):
            for col in df.columns:
                if "R$" in col or "Vínculo" in col or "Qualidade" in col:
                    df[col] = df[col].apply(formatar_valor)
            return df

        # Colunas para manter na tabela resumo
        colunas_manter = [
            "Classificação",
            "Total Geral (R$) eSF",
            "Total Geral (R$) eAP 20h",
            "Total Geral (R$) eAP 30h",
            "Total Geral (R$)"
        ]

        # Filtrar o DataFrame para manter apenas as colunas desejadas
        df_tabela_resumo = df_tabela_resumo[colunas_manter]

        df_tabela_resumo = formatar_tabela(df_tabela_resumo)
        st.table(df_tabela_resumo.style.apply(_color_row, axis=1))

        st.divider()

        # 4 - GRÁFICOS DE COLUNA
        # --- Gráfico Resumo ---
        st.write("**Gráfico Resumo**")
        # Preparar os dados para o gráfico
        totais_por_classificacao = df_tabela_resumo.groupby("Classificação")["Total Geral (R$)"].sum().reset_index()

        # Definir a ordem desejada das classificações
        ordem_classificacoes = ["Regular", "Suficiente", "Bom", "Ótimo"]

        # Reordenar os dados de acordo com a ordem definida
        totais_por_classificacao["Classificação"] = pd.Categorical(totais_por_classificacao["Classificação"], categories=ordem_classificacoes, ordered=True)
        totais_por_classificacao = totais_por_classificacao.sort_values("Classificação")

        # Converter a coluna "Total Geral (R$)" para float
        totais_por_classificacao["Total Geral (R$)"] = totais_por_classificacao["Total Geral (R$)"].str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).astype(float)

        # Normalizar os valores para exibição no gráfico
        soma_totais = totais_por_classificacao["Total Geral (R$)"].sum()
        totais_por_classificacao["Proporcao"] = totais_por_classificacao["Total Geral (R$)"] / soma_totais

        # dados_grafico_resumo = [
        #     go.Bar(
        #         name='Total Geral (R$)',
        #         x=totais_por_classificacao["Classificação"],
        #         y=totais_por_classificacao["Proporcao"],  # Usar a proporção para a altura da barra
        #         marker_color=[CORES_CLASSIFICACAO.get(clf, '#7f7f7f') for clf in totais_por_classificacao["Classificação"]],
        #         text=totais_por_classificacao["Total Geral (R$)"].apply(lambda x: formatar_valor(x)), # Formatar o valor original
        #         textposition='inside',
        #     )
        # ]

        # Criar o gráfico de barras com Plotly
        # fig_resumo = go.Figure(data=dados_grafico_resumo)

        # # Configurar o layout do gráfico
        # fig_resumo.update_layout(
        #     title="Gráfico Resumo por Classificação",
        #     xaxis_title="Classificação",
        #     yaxis_title="Valor (%)",
        #     yaxis_tickformat=',.2%',
        #     barmode='group',
        #     width=700,
        #     showlegend=False,
        #     plot_bgcolor='rgba(0,0,0,0)',
        #     title_font=dict(size=18),
        #     font=dict(size=16)
        # )

        # # Inverter a ordem do eixo x para corresponder à imagem
        # fig_resumo.update_xaxes(autorange="reversed", tickfont=dict(size=14))

        # # Ajustar o limite superior do eixo Y para evitar cortes
        # fig_resumo.update_yaxes(showticklabels=False, showgrid=False, range=[0, totais_por_classificacao["Proporcao"].max() * 1.10], tickfont=dict(size=14))

        # # Exibir gráfico no Streamlit
        # st.plotly_chart(fig_resumo)

if __name__ == "__main__":
    main()
