import streamlit as st
import pandas as pd
import datetime
from pyUFbr.baseuf import ufbr
import time

if 'counter' not in st.session_state:
    st.session_state.counter = 0
    st.session_state.fns = 'INCENTIVO FINANCEIRO DA APS - COMPONENTE PER CAPITA DE BASE POPULACIONAL'
st.session_state.counter += 1

def formatar_numero(num):
    # Formatação do número para duas casas decimais com ponto como separador de milhar
    num_formatado = "{:,.2f}".format(num)

    # Substituindo ponto por vírgula e vírgula por ponto
    num_formatado = num_formatado.replace(",", "x").replace(".", ",").replace("x", ".")

    # Adicionando o símbolo de Real (R$) na frente
    num_formatado = "R$ " + num_formatado

    return num_formatado

def importar_município():
    equipes_cnes = pd.read_csv('Anexo VI Portaria 3493.csv', delimiter=';')
    equipes_cnes['IBGE'] = equipes_cnes['IBGE'].fillna(0).astype(int).astype(str).str.zfill(6)
    equipes_cnes = equipes_cnes[equipes_cnes['IBGE'] == codigo_ibge]
    pop2021 = pd.read_csv('estimativa_pop_2021_ibge.csv', delimiter=';')
    pop2021['IBGE'] = pop2021['IBGE'].fillna(0).astype(int).astype(str).str[:-1].str.zfill(6)
    pop2021 = pop2021[pop2021['IBGE'] == codigo_ibge]
    pop2021 = pop2021['POP2021'].item()
    pop2021_formatado = '{:,.0f}'.format(pop2021)
    equipes_cnes['População 2021'] = pop2021_formatado
    
    st.dataframe(equipes_cnes, hide_index=True)
    ied = equipes_cnes['Índice de Equidade e Dimensionamento (IED)'].item()
    pop = equipes_cnes['Número de habitantes segundo o IBGE 2022'].item()
    pop = pop.replace('.', '')
    pop = float(pop)
    pop = int(pop)
    if pop < pop2021:
        pop = pop2021
        st.toast('Utilizando a população de 2021!', icon="⚠️")
        st.session_state.fns = 'INCENTIVO FINANCEIRO DA APS - MANUTENÇÃO DE PAGAMENTO DE VALOR NOMINAL COM BASE EM EXERCÍCIO ANTERIOR'
    else:
        st.session_state.fns = 'INCENTIVO FINANCEIRO DA APS - COMPONENTE PER CAPITA DE BASE POPULACIONAL'
    ied = int(ied) - 1
    st.session_state._pop = pop
    st.session_state.ied = ied
    progress_text = "Preenchendo população e estrato..."
    my_bar = st.progress(0, text=progress_text)
    for percent_complete in range(100):
        time.sleep(0.01)
        my_bar.progress(percent_complete + 1, text=progress_text)
    time.sleep(1)
    my_bar.empty()
    
    return pop, ied

# Definindo as tabelas de valores

# =========== COMPONENTE FIXO ==================

data = {
    'estrato': [1, 2, 3, 4],
    'eSF': [18000.00, 16000.00, 14000.00, 12000.00],
    'eAP 30h': [10800.00, 9600.00, 8400.00, 7200.00],
    'eAP 20h': [7200.00, 6400.00, 5600.00, 4800.00]
}

componente_fixo = pd.DataFrame(data)

# =========== COMPONENTE IMPLANTAÇÃO ==================

data = {
    'TIPO DE EQUIPE': ['eSF', 'eAP 30h', 'eAP 20h', 'eSB 40h', 'eMulti Ampliada', 'eMulti Complementar', 'eMulti Estratégica'],
    'VALOR POR IMPLANTAÇÃO': ['R$ 30.000,00', 'R$ 16.800,00', 'R$ 10.800,00', 'R$ 14.000,00', 'R$ 36.000,00', 'R$ 24.000,00', 'R$ 12.000,00']
}

valor_implantacao = pd.DataFrame(data)

# =========== COMPONENTE VINCULO E ACOMP - PARAMETRO CADASTROS ==================

data = {
    'Porte Populacional (habitantes)': ['1- Até 20 mil', '2- Acima de 20 mil até 50 mil', '3- Acima de 50 mil até 100 mil', '4- Acima de 100 mil'],
    'eSF Min': [2000, 2500, 2750, 3000],
    'eSF Max': [3000, 3750, 4125, 4500],
    'eAP 30h Min': [1500, 1875, 2063, 2250],
    'eAP 30h Max': [2250, 2813, 3095, 3375],
    'eAP 20h Min': [1000, 1250, 1375, 1500],
    'eAP 20h Max': [1500, 1875, 2063, 2250]
}

param_vinc_e_acomp = pd.DataFrame(data)

# =========== COMPONENTE IMPLANTAÇÃO - CLASSIFICAÇÃO ==================

data = {
    'Ótimo': [8000.00, 4000.00, 3000.00],
    'Bom': [6000.00, 3000.00, 2250.00],
    'Suficiente': [4000.00, 2000.00, 1500.00],
    'Regular': [2000.00, 1000.00, 750.00]
}

index = ['eSF_40h', 'eAP_30h', 'eAP_20h']

classif_vinc_e_acomp = pd.DataFrame(data, index=index)

# =========== COMPONENTE QUALIDADE ==================

data = {
    'Equipe': ['eSF', 'eAP', 'eAP', 'eMulti', 'eMulti', 'eMulti', 'eSB', 'eSB', 'eSB', 'eSB'],
    'Modalidade': ['40h', '30h', '20h', 'Ampliada', 'Complementar', 'Estratégica', 'I- Comum', 'II- Comum', 'I- Quil/Assent', 'II- Quil/Assent'],
    'Ótimo': [8000.00, 4000.00, 3000.00, 9000.00, 6000.00, 3000.00, 2449.00, 3267.00, 3673.50, 4900.50],
    'Bom': [6000.00, 3000.00, 2250.00, 6750.00, 4500.00, 2250.00, 1836.75, 2450.25, 2755.13, 3675.38],
    'Suficiente': [4000.00, 2000.00, 1500.00, 4500.00, 3000.00, 1500.00, 1224.50, 1633.50, 1836.75, 2450.25],
    'Regular': [2000.00, 1000.00, 750.00, 2250.00, 1500.00, 750.00, 612.25, 816.75, 918.38, 1225.13]
}

qualidade = pd.DataFrame(data)

# Concatenação das colunas 'Equipe' e 'Modalidade'
qualidade['Equipe'] = qualidade['Equipe'] + ' ' + qualidade['Modalidade']

# Remoção da coluna 'Modalidade'
qualidade = qualidade.drop('Modalidade', axis=1)

valor_lrpd = 11250
valor_atividade_física = 1000
mes = datetime.datetime.now().month - 1
porte = 1


# Interface:

st.set_page_config(page_title='Novo Financiamento da APS - S Consultoria')
st.markdown(
    """
    <style>
    .reportview-container {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def definir_porte(valor,):
    if valor <= 20000:
        return "1- Até 20 mil", 1
    elif valor <= 50000:
        return "2- Acima de 20 mil até 50 mil", 2
    elif valor <= 100000:
        return "3- Acima de 50 mil até 100 mil", 3
    else:
        return "4- Acima de 100 mil", 4

esf40h = eap30h = eap20h = emulti_a = emulti_c = emulti_e = esb_I_c = esb_II_c = esb_I_qa = esb_II_qa = esb_20h = esb_30h = lrpd = ceo_I = ceo_II = ceo_III = uom = cnr1 = cnr2 = cnr3 = iaf = acs = med_res = enf_res = cd_res = 0
variaveis = [emulti_a, emulti_c, emulti_e, esb_I_c, esb_II_c, esb_I_qa, esb_II_qa, esb_20h, esb_30h, lrpd, ceo_I, ceo_II, ceo_III, uom, cnr1, cnr2, cnr3, iaf, acs, med_res, enf_res, cd_res]

st.title('Novo Financiamento da APS')
st.write('[PORTARIA GM/MS Nº 3.493, DE 10 DE ABRIL DE 2024](https://www.in.gov.br/en/web/dou/-/portaria-gm/ms-n-3.493-de-10-de-abril-de-2024-553573811)')
st.write('[Portal FNS](https://consultafns.saude.gov.br/#/detalhada)')
st.write('Calcule os valores do Novo Financiamento da APS do seu município!')

if st.session_state.counter == 1:
    #ied = pop = 0
    st.session_state._pop = 0
    st.session_state.ied = 0

pop = st.session_state._pop
ied = st.session_state.ied

with st.expander("Consultar Anexo VI Portaria 3493"):
    uf = st.selectbox('UF: ', ufbr.list_uf)
    mun = st.selectbox('Município: ', ufbr.list_cidades(uf))
    codigo_ibge = ufbr.get_cidade(mun)
    codigo_ibge = str(codigo_ibge[0])
    codigo_ibge = codigo_ibge[:6]
    if st.button('Consultar', type='secondary'):
        pop, ied = importar_município()
    

with st.form(key='form_equipes'):
    st.subheader('Preencha os dados do seu município:')
    st.caption(':red[**OBS. IBGE:**] Houve aumento da população em 2022: Informe IBGE :blue[2022]. Se houve redução, informe IBGE :blue[2021].')
    população = st.number_input('População:', value=pop, help="Compare a população do eGestor com a do FNS, se em 2022 houve diminuição, use a que for maior.")
    if população > 0:
        porte, valor = definir_porte(valor = população)
        if população > 0:
            porte, valor = definir_porte(valor = população)
    estrato = st.selectbox('Estrato (IED):', ('1', '2', '3', '4'), help="Anexo VI da PORTARIA GM/MS Nº 3.493, DE 10 DE ABRIL DE 2024 (Link acima)", index=ied) 
    mes_atual = st.selectbox('Parcela (mês):' , ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12'), index=mes, help='Mesma parcela do FNS')
    st.subheader('Informe os serviços existentes:')
    st.caption('em caso de dúvida, consulte o [e-Gestor](https://egestorab.saude.gov.br/gestaoaps/relFinanciamentoParcela.xhtml)')
    
    with st.expander("ESF/eAP"):
        esf40h = st.number_input('Quantidade de equipes ESF (40h):', value=0)
        eap30h = st.number_input('Quantidade de equipes eAP (30h):', value=0)
        eap20h = st.number_input('Quantidade de equipes eAP (20h):', value=0)

    with st.expander("eMulti"):
        emulti_a = st.number_input('Quantidade de equipes eMulti Ampliada:', value=0)
        emulti_c = st.number_input('Quantidade de equipes eMulti Complementar:', value=0)
        emulti_e = st.number_input('Quantidade de equipes eMulti Estratégica:', value=0)

    with st.expander("Saúde Bucal"):
        esb_I_c = st.number_input('Quantidade de equipes de Saúde Bucal Modalidade I Comum:', value=0)
        esb_II_c = st.number_input('Quantidade de equipes de Saúde Bucal Modalidade II Comum:', value=0)
        esb_I_qa = st.number_input('Quantidade de equipes de Saúde Bucal Modalidade I Quilombola/Assentado:', value=0)
        esb_II_qa = st.number_input('Quantidade de equipes de Saúde Bucal Modalidade II Quilombola/Assentado:', value=0)
        esb_20h = st.number_input('Quantidade de equipes de Saúde Bucal 20h:', value=0)
        esb_30h = st.number_input('Quantidade de equipes de Saúde Bucal 30h:', value=0)
        lrpd = st.number_input('Quantidade de LRPD:', value=0)
        valor_lrpd = st.number_input('Valor de custeio do LRPD:', value=11250)
        ceo_I = st.number_input('Quantidade de CEO tipo I:', value=0)
        ceo_II = st.number_input('Quantidade de CEO tipo II:', value=0)
        ceo_III = st.number_input('Quantidade de CEO tipo III:', value=0)
        uom = st.number_input('Quantidade de UOM:', value=0)
    st.divider()
    with st.expander("Consultório na Rua"):
        cnr1 = st.number_input('Consultório na Rua I:', value=0)
        cnr2 = st.number_input('Consultório na Rua II:', value=0)
        cnr3 = st.number_input('Consultório na Rua III:', value=0)

    with st.expander("Atividade Física"):
        iaf = st.number_input('Quantidade de Estabelecimentos Pagos com Incentivo Atividade Física:', value=0)
        valor_atividade_física = st.number_input('Valor de custeio Atividade Física:', value=1000)

    with st.expander("Residência"):
        med_res = st.number_input('Médico(s) Residentes:', value=0)
        enf_res = st.number_input('Enfermeiro(s) Residentes:', value=0)
        cd_res = st.number_input('Cirurgiões-Dentistas residentes:', value=0)

    with st.expander("ACS - Vínculo Indireto"):
        acs = st.number_input('Quantidade de ACS (Vínculo indireto):', value=0)
    calcular = st.form_submit_button('Calcular')
if calcular:
    
    st.header('Resultado:')
    st.divider()

    # Componente I
    valor_componente_fixo = componente_fixo.loc[componente_fixo['estrato'] == int(estrato)]    
    valor_componente_fixo = valor_componente_fixo['eSF'] * esf40h + valor_componente_fixo['eAP 30h'] * eap30h + valor_componente_fixo['eAP 20h'] * eap20h
    valor_componente_fixo = valor_componente_fixo.item()

    # Componente II
    param_vinc_e_acomp = param_vinc_e_acomp.loc[param_vinc_e_acomp['Porte Populacional (habitantes)'] == porte]
    classif_vinc_e_acomp = classif_vinc_e_acomp[['Bom']]
    variaveis_esf = [esf40h, eap30h, eap20h]
    valor_vinc_e_acomp = classif_vinc_e_acomp.multiply(variaveis_esf, axis=0)
    valor_vinc_e_acomp = valor_vinc_e_acomp.sum(axis=0)
    soma_vinc_e_acomp = valor_vinc_e_acomp.item()

    # Componente III
    qualidade_bom = qualidade[['Bom']]
    variaveis_qualidade = [esf40h, eap30h, eap20h, emulti_a, emulti_c, emulti_e, esb_I_c, esb_II_c, esb_I_qa, esb_II_qa]
    qualidade_bom = qualidade_bom.multiply(variaveis_qualidade, axis=0)
    # Separando os valores de Qualidade por Área
    qualidade_esf = qualidade_bom.iloc[0:3].sum().sum().astype(float)
    qualidade_emulti = qualidade_bom.iloc[3:6].sum().sum().astype(float)
    qualidade_esb = qualidade_bom.iloc[6:10].sum().sum().astype(float)
    # Calculando o valor do Componente Qualidade (sem Saúde Bucal)
    soma_qualidade = qualidade_esf + qualidade_emulti
    #Exibição da tabela de Qualidade por Equipe
    st.write('**Componente Qualidade por tipo de equipe:**')
    qualidade_separado = {
        'Qualidade ESF': [qualidade_esf],
        'Qualidade eMulti': [qualidade_emulti],
        'Qualidade ESB': [qualidade_esb]
    }
    qualidade_separado = pd.DataFrame(qualidade_separado)
    qualidade_separado = qualidade_separado.map(formatar_numero)
    qualidade_separado = st.dataframe(qualidade_separado, hide_index=True)

    # Componente IV
    # =========== RELAÇÃO DAS EQUIPES PARA CUSTEIO ==================
    data = {
        'Equipe': ['eMulti Ampliada', 'eMulti Complementar', 'eMulti Estratégica', 'eSB I- Comum', 'eSB II- Comum', 'eSB I- Quil/Assent', 'eSB II- Quil/Assent', 'eSB 20h', 'eSB 30h', 'LRPD', 'CEO I', 'CEO_II', 'CEO_III', 'UOM', "Consultório na Rua I", "Consultório na Rua II", "Consultório na Rua III","Incentivo Ativ. Física","ACS", "Médicos Residentes", "Enfermeiros Residentes", "Cirurgiões-Dentistas Residentes"],
        'Valor Unit.': [36000.00, 24000.00, 12000.00, 4014.00, 7064.00, 6021.00, 10596.00, 2007.00, 3010.00, valor_lrpd, 28864.94, 36343.21, 0, 0, 19900, 27300, 35200, valor_atividade_física, 1550, 4500, 1500, 1500]
    }
    custeio = pd.DataFrame(data)
    tam_custeio = len(custeio)
    custeio_outros = custeio.iloc[14:tam_custeio,:]
    st.write('**Valor de custeio (Outras equipes):**')
    # =========== VARIÁVEIS DOS OUTROS SERVIÇOS ================
    var_custeio_outros = [cnr1, cnr2, cnr3, iaf, acs, med_res, enf_res, cd_res]
    # ==========================================================
    custeio_outros = custeio_outros.multiply(var_custeio_outros, axis=0)
    custeio_outros_filtrado = custeio_outros[custeio_outros['Valor Unit.'] != 0]
    custeio_outros_filtrado['Valor Unit.'] = custeio_outros_filtrado['Valor Unit.'].map(formatar_numero)
    custeio_outros_filtrado = st.dataframe(custeio_outros_filtrado, hide_index=True)
    total_custeio_outros = sum(custeio_outros['Valor Unit.'])
        
    # Componente V
    variaveis_sb = [esb_I_c, esb_II_c, esb_I_qa, esb_II_qa, esb_20h, esb_30h, lrpd, ceo_I, ceo_II, ceo_III, uom]
    custeio_sb = custeio.iloc[3:14,:]
    soma_custeio_sb = custeio_sb.multiply(variaveis_sb, axis=0)
    soma_custeio_sb = soma_custeio_sb.sum(axis=0)
    soma_custeio_sb = soma_custeio_sb['Valor Unit.']
    soma_custeio_sb_qualidade = soma_custeio_sb + qualidade_esb

    # Componente VI
    mes_atual = datetime.datetime.now().month
    comp_per_capita = 5.95 * população / 12 * mes_atual

    #====================================Criando o DataFrame da Portaria
    st.write('**_NOMENCLATURA PORTARIA GM/MS Nº 3.493, DE 10 DE ABRIL DE 2024:_**')
    df_portaria = pd.DataFrame({
        'Componente': ['I- Componente Fixo', 
                    'II- Componente Vínculo e Acompanhamento', 
                    'III- Componente Qualidade', 
                    'IV- Componente para implantação e manutenção...', 
                    'V- Componente para Atenção à Saúde Bucal', 
                    'VI- Componente per capita de base populacional para ações no âmbito da APS'],
        'Valor': [valor_componente_fixo, soma_vinc_e_acomp, soma_qualidade, total_custeio_outros, soma_custeio_sb_qualidade, comp_per_capita]
    })

    # Total
    valor_total = sum(df_portaria['Valor'])
    valor_total_formatado = formatar_numero(valor_total)
   
    df_portaria['Valor'] = df_portaria['Valor'].map(formatar_numero)
    st.dataframe(df_portaria, hide_index=True)
   
    st.markdown(f"**Total:** <span style='color:green;'>**{valor_total_formatado}**</span>", unsafe_allow_html=True)

    
    #=lor:green;'>**{valor_total_1_formatado}**</span>", unsafe_allow_html=True)====================================Criando o DataFrame do FNS
    st.divider()
    st.write('**_NOMENCLATURA DO FNS:_**')


    valor_fns_1 = valor_componente_fixo + soma_vinc_e_acomp + soma_qualidade
    valor_fns_2 = total_custeio_outros
    valor_fns_3 = comp_per_capita
    valor_fns_4 = soma_custeio_sb_qualidade

    df_fns = pd.DataFrame({'Componente': ['INCENTIVO FINANCEIRO DA APS - EQUIPES DE SAÚDE DA FAMÍLIA/ESF E EQUIPES DE ATENÇÃO PRIMÁRIA/EAP', 
                    'INCENTIVO FINANCEIRO DA APS - DEMAIS PROGRAMAS SERVIÇOS E EQUIPES DA APS', 
                    st.session_state.fns, 
                    'INCENTIVO FINANCEIRO PARA ATENÇÃO À SAÚDE BUCAL'], 
                    'Valor': [valor_fns_1, valor_fns_2, valor_fns_3, valor_fns_4]
    })

    df_fns['Valor'] = df_fns['Valor'].map(formatar_numero)
    st.dataframe(df_fns, hide_index=True)

    # Total
    st.markdown(f"**Total:** <span style='color:green;'>**{valor_total_formatado}**</span>", unsafe_allow_html=True)