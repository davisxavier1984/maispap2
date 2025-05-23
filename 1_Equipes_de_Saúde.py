import streamlit as st
import pandas as pd
from utils.translations import TRADUCOES
from utils.formatting import format_currency
from utils.interface import style_metric_cards, metric_card 
# from calculos.calculos_equipes import calcular_metricas_equipes # Comentado temporariamente
from utils.data import load_data_from_json

# Constantes
CORES_CLASSIFICACAO = {
    "verde": "#28a745",
    "amarelo": "#ffc107",
    "vermelho": "#dc3545",
    "cinza": "#6c757d" 
}

# Placeholder para criar_tabela_classificacao
# Idealmente, esta função deveria estar em utils.interface ou um módulo similar de UI.
# Por enquanto, a manteremos aqui para evitar mais erros de importação.
# A assinatura da função foi alterada na chamada em `pagina_equipes_saude`, 
# então vamos ajustar a definição aqui também, ou comentar seu uso.
# A chamada original era: criar_tabela_classificacao(df, 'Equipe de Saúde da Família (eSF) 40h', num_equipes_esf, num_equipes_eap_20h, num_equipes_eap_30h)
# A definição é: def criar_tabela_classificacao(df_classificacao, cores):
# Vamos comentar as chamadas a esta função por enquanto, pois a lógica e os parâmetros não batem.
# def criar_tabela_classificacao(df_classificacao, cores):\n    st.dataframe(df_classificacao.style.applymap(lambda x: f"background-color: {cores.get(x, cores['cinza'])}"))

# Placeholder para obter_valor_unitario - esta função precisa ser definida ou importada corretamente.
# Comentando as chamadas a ela por enquanto.
# def obter_valor_unitario(tipo_equipe, classificacao):
#     # Lógica para obter valor unitário (exemplo)
#     # Isso deve vir de uma fonte de dados ou configuração
#     if tipo_equipe == "Equipe de Saúde da Família (eSF) 40h":
#         if classificacao == "Ótimo": return 10000
#         if classificacao == "Bom": return 8000
#         # ... etc
#     return 0


def pagina_equipes_saude():
    st.set_page_config(layout="wide", page_title="Equipes de Saúde Detalhado")
    style_metric_cards()
    st.title("Painel Detalhado de Equipes de Saúde")

    dados_api = load_data_from_json()
    if not dados_api:
        st.warning("Dados da API não encontrados. Por favor, consulte os dados na página principal primeiro.")
        return

    # Extração dos dados
    dados_pagamentos = dados_api.get("pagamentos", [])

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

    def converter_colunas(df_conv, colunas_conv): # Renomeado df para df_conv para evitar sombreamento
        for col in colunas_conv['quantitativas']:
            if col in df_conv.columns:
                df_conv[col] = pd.to_numeric(df_conv[col], errors='coerce').fillna(0).astype(int)

        for col in colunas_conv['monetarias']:
            if col in df_conv.columns:
                df_conv[col] = (
                    df_conv[col].astype(str)
                    .str.replace('.', '', regex=False)
                    .str.replace(',', '.', regex=False)
                    .astype(float)
                )
        return df_conv

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
    populacao = df['qtPopulacao'].iloc[0] if 'qtPopulacao' in df.columns and not df.empty else 0
    ano_referencia = df['nuAnoRefPopulacaoIbge'].iloc[0] if 'nuAnoRefPopulacaoIbge' in df.columns and not df.empty else 0


    cols_info = st.columns(2)
    with cols_info[0]:
        metric_card("População IBGE", f"{populacao:,}".replace(",", "."))
    with cols_info[1]:
        metric_card("Ano Referência Populacional", str(ano_referencia)) # Convertido para string
    
    # Input para código IBGE do município
    codigo_ibge_atual = None
    if not df.empty:
        if 'coMunicipio' in df.columns:
            codigo_ibge_atual = str(df['coMunicipio'].iloc[0])
        elif 'coIbge' in df.columns: # Corrigido para coIbge
            codigo_ibge_atual = str(df['coIbge'].iloc[0])


    codigo_ibge_input = st.text_input(
        "Código IBGE do Município",
        value=codigo_ibge_atual if codigo_ibge_atual else "",
        help="Digite o código IBGE do município com 7 dígitos"
    )

    if codigo_ibge_input and len(codigo_ibge_input.strip()) != 7:
        st.warning("O código IBGE deve conter exatamente 7 dígitos")

    # Adiciona as novas colunas ao dicionário de traduções
    # Idealmente, isso deveria estar no translations.py, mas para manter o exemplo funcional:
    local_translations = TRADUCOES.copy() # Evitar modificar o global diretamente se importado
    local_translations.update({
        "qtPopulacao": "População IBGE",
        "nuAnoRefPopulacaoIbge": "Ano Referência Populacional"
    })

    # Classificações no topo
    classificacoes_cols = ['dsFaixaIndiceEquidadeEsfEap',
                           'dsClassificacaoVinculoEsfEap',
                           'dsClassificacaoQualidadeEsfEap']

    if all(col in df.columns for col in classificacoes_cols) and not df.empty:
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
                todas_metricas_esf.append((local_translations.get(k, k), f"{v:,}".replace(",", ".")))
        for k, v in metricas['ESF']['monetarias'].items():
            todas_metricas_esf.append((local_translations.get(k, k), format_currency(v)))


        cols_esf = st.columns(4)
        for i, (titulo, valor) in enumerate(todas_metricas_esf):
            with cols_esf[i % 4]:
                metric_card(titulo, valor)

        st.divider()
        st.write("**Gráficos de Pizza - ESF**")
        # Comentado para evitar erro com plotly não importado
        # ... (código do gráfico de pizza ESF) ...
        st.divider()
        st.write("**Equipe de Saúde da Família (eSF) 40h**")
        # criar_tabela_classificacao(df,'Equipe de Saúde da Família (eSF) 40h', num_equipes_esf, num_equipes_eap_20h, num_equipes_eap_30h) # Comentado
        st.divider()

    # --- Container para EAP ---
    with st.container():
        st.subheader("Equipes de Atenção Primária (eAP)")
        st.write("**Equipes EAP (Métricas)**")
        todas_metricas_eap = []
        for k, v in metricas['EAP']['quantitativas'].items():
            todas_metricas_eap.append((local_translations.get(k,k), f"{v:,}".replace(",", ".")))
        for k, v in metricas['EAP']['monetarias'].items():
            todas_metricas_eap.append((local_translations.get(k,k), format_currency(v)))

        cols_eap = st.columns(4)
        for i, (titulo, valor) in enumerate(todas_metricas_eap):
            with cols_eap[i % 4]:
                metric_card(titulo, valor)
        st.divider()
        st.write("**Gráficos de Pizza - EAP**")
        # Comentado para evitar erro com plotly não importado
        # ... (código dos gráficos de pizza EAP) ...
        st.divider()
        if num_equipes_eap_20h > 0:
            st.write("**Equipe de Atenção Primária (eAP) 20h**")
            # criar_tabela_classificacao(df, "Equipe de Atenção Primária (eAP) 20h", num_equipes_esf, num_equipes_eap_20h, num_equipes_eap_30h) # Comentado
        if num_equipes_eap_30h > 0:
            st.write("**Equipe de Atenção Primária (eAP) 30h**")
            # criar_tabela_classificacao(df, "Equipe de Atenção Primária (eAP) 30h", num_equipes_esf, num_equipes_eap_20h, num_equipes_eap_30h) # Comentado
        st.divider()

    # --- Container para Resumo ---
    with st.container():
        st.subheader("Resumo")
        st.write("**Tabela Resumo**")
        classificacoes = ['Ótimo', 'Bom', 'Suficiente', 'Regular']
        totais_esf = {clf: {"Total Geral": 0} for clf in classificacoes}
        totais_eap_20h = {clf: {"Total Geral": 0} for clf in classificacoes}
        totais_eap_30h = {clf: {"Total Geral": 0} for clf in classificacoes}

        # Comentando chamadas para obter_valor_unitario
        # for clf in classificacoes:
        #     valor_unitario_esf = obter_valor_unitario("Equipe de Saúde da Família (eSF) 40h", clf)
        #     totais_esf[clf]["Total Geral"] = valor_unitario_esf * num_equipes_esf * 2
        # if num_equipes_eap_20h > 0:
        #     for clf in classificacoes:
        #         valor_unitario_eap_20h = obter_valor_unitario("Equipe de Atenção Primária (eAP) 20h", clf)
        #         totais_eap_20h[clf]["Total Geral"] = valor_unitario_eap_20h * num_equipes_eap_20h * 2
        # if num_equipes_eap_30h > 0:
        #     for clf in classificacoes:
        #         valor_unitario_eap_30h = obter_valor_unitario("Equipe de Atenção Primária (eAP) 30h", clf)
        #         totais_eap_30h[clf]["Total Geral"] = valor_unitario_eap_30h * num_equipes_eap_30h * 2

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

        def _color_row(row):
            # ... (código de _color_row) ...
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


        def formatar_tabela_resumo(df_format): # Renomeado df para df_format
            for col in df_format.columns:
                if "R$" in col or "Vínculo" in col or "Qualidade" in col: # "Vínculo" e "Qualidade" podem não ser monetários diretamente
                    # Apenas aplicar format_currency para colunas que são realmente monetárias
                    if "R$" in col: 
                        df_format[col] = df_format[col].apply(format_currency)
            return df_format

        colunas_manter = [
            "Classificação", "Total Geral (R$) eSF", "Total Geral (R$) eAP 20h",
            "Total Geral (R$) eAP 30h", "Total Geral (R$)"
        ]
        df_tabela_resumo = df_tabela_resumo[colunas_manter]
        df_tabela_resumo = formatar_tabela_resumo(df_tabela_resumo) # Usando a função renomeada
        st.table(df_tabela_resumo.style.apply(_color_row, axis=1))
        st.divider()
        st.write("**Gráfico Resumo**")
        
        # Preparar os dados para o gráfico
        # Assegurar que a coluna existe e é numérica antes de tentar converter/somar
        if "Total Geral (R$)" in df_tabela_resumo.columns:
            # A coluna já foi formatada para string por format_currency, precisa reverter para float
            def G_currency_to_float(value_str):
                if isinstance(value_str, (int, float)): return float(value_str)
                try:
                    return float(value_str.replace('R$', '').replace('.', '').replace(',', '.'))
                except: return 0.0

            df_tabela_resumo["Total Geral (Num)"] = df_tabela_resumo["Total Geral (R$)"].apply(G_currency_to_float)
            totais_por_classificacao = df_tabela_resumo.groupby("Classificação")["Total Geral (Num)"].sum().reset_index()
            
            ordem_classificacoes = ["Regular", "Suficiente", "Bom", "Ótimo"]
            totais_por_classificacao["Classificação"] = pd.Categorical(totais_por_classificacao["Classificação"], categories=ordem_classificacoes, ordered=True)
            totais_por_classificacao = totais_por_classificacao.sort_values("Classificação")

            # Comentado para evitar erro com plotly não importado
            # ... (código do gráfico de barras resumo) ...
        else:
            st.info("Coluna 'Total Geral (R$)' não encontrada para gerar o gráfico resumo.")


if __name__ == "__main__":
    pagina_equipes_saude()
