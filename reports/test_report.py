"""
Arquivo de teste para demonstrar o sistema de relatórios PDF.
"""
import streamlit as st
from datetime import datetime
from reports.pdf_generator import generate_pap_report
from reports.data_formatter import PAPDataFormatter
from reports.chart_generator import generate_chart_for_pdf

def test_report_generation():
    """Testa a geração de relatório com dados simulados."""
    
    # Simular dados mínimos necessários
    st.session_state.update({
        'municipio_selecionado': 'Belo Horizonte',
        'uf_selecionada': 'MG',
        'competencia_selecionada': '2024-05',
        'populacao': 2500000,
        'ied': 'ESTRATO 1',
        'classificacao': 'Bom',
        'vinculo': 'Ótimo',
        'calculo_realizado': True,
        'total_pap_calculado': 150000.00,
        'quantity_eSF': 5,
        'quantity_eAP 30h': 3,
        'quantity_eMULTI Ampl.': 2
    })
    
    # Testar formatação de dados
    municipality_data = PAPDataFormatter.format_municipality_data()
    print("✅ Dados do município formatados:")
    for key, value in municipality_data.items():
        print(f"   {key}: {value}")
    
    # Testar configuração de serviços
    services_config = PAPDataFormatter.format_services_configuration()
    print("\n✅ Configuração de serviços:")
    for service in services_config:
        print(f"   {service['servico']}: {service['quantidade']} ({service['status']})")
    
    # Testar validação de dados
    validation = PAPDataFormatter.validate_data_completeness()
    print(f"\n✅ Validação de dados: {'Completo' if validation['is_complete'] else 'Incompleto'}")
    print(f"   Cálculo realizado: {'Sim' if validation['calculation_ready'] else 'Não'}")
    
    # Testar geração de gráfico
    scenarios_data = {'Regular': 100000, 'Suficiente': 115000, 'Bom': 135000, 'Ótimo': 160000}
    chart_base64 = generate_chart_for_pdf('scenarios_comparison', scenarios_data)
    if chart_base64:
        print("✅ Gráfico de cenários gerado com sucesso")
    else:
        print("❌ Erro na geração do gráfico")
    
    # Testar geração do PDF
    try:
        pdf_data = generate_pap_report()
        if pdf_data and len(pdf_data) > 0:
            print(f"✅ PDF gerado com sucesso ({len(pdf_data)} bytes)")
            return True
        else:
            print("❌ PDF vazio ou erro na geração")
            return False
    except Exception as e:
        print(f"❌ Erro na geração do PDF: {str(e)}")
        return False

def create_test_interface():
    """Cria interface de teste no Streamlit."""
    st.title("🧪 Teste do Sistema de Relatórios PDF")
    
    st.info("Este é um ambiente de teste para o sistema de relatórios PDF da Calculadora PAP.")
    
    # Seção de configuração de teste
    st.subheader("1. Configuração dos Dados de Teste")
    
    col1, col2 = st.columns(2)
    
    with col1:
        municipio_teste = st.text_input("Município", value="Belo Horizonte")
        uf_teste = st.selectbox("UF", ["MG", "SP", "RJ", "RS", "PR"], index=0)
        populacao_teste = st.number_input("População", value=2500000, min_value=1000)
    
    with col2:
        competencia_teste = st.text_input("Competência", value="2024-05")
        classificacao_teste = st.selectbox("Classificação", ["Regular", "Suficiente", "Bom", "Ótimo"], index=2)
        vinculo_teste = st.selectbox("Vínculo", ["Regular", "Suficiente", "Bom", "Ótimo"], index=3)
    
    # Configurar serviços de teste
    st.subheader("2. Configuração dos Serviços")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        esf_qty = st.number_input("Quantidade eSF", value=5, min_value=0)
        eap30_qty = st.number_input("Quantidade eAP 30h", value=3, min_value=0)
    
    with col2:
        eap20_qty = st.number_input("Quantidade eAP 20h", value=2, min_value=0)
        emulti_ampl_qty = st.number_input("Quantidade eMULTI Ampl.", value=2, min_value=0)
    
    with col3:
        emulti_compl_qty = st.number_input("Quantidade eMULTI Compl.", value=1, min_value=0)
        emulti_estrat_qty = st.number_input("Quantidade eMULTI Estrat.", value=1, min_value=0)
    
    # Botão para aplicar configurações
    if st.button("🔧 Aplicar Configurações de Teste", use_container_width=True):
        st.session_state.update({
            'municipio_selecionado': municipio_teste,
            'uf_selecionada': uf_teste,
            'competencia_selecionada': competencia_teste,
            'populacao': populacao_teste,
            'ied': 'ESTRATO 1',
            'classificacao': classificacao_teste,
            'vinculo': vinculo_teste,
            'calculo_realizado': True,
            'total_pap_calculado': 150000.00,
            'quantity_eSF': esf_qty,
            'quantity_eAP 30h': eap30_qty,
            'quantity_eAP 20h': eap20_qty,
            'quantity_eMULTI Ampl.': emulti_ampl_qty,
            'quantity_eMULTI Compl.': emulti_compl_qty,
            'quantity_eMULTI Estrat.': emulti_estrat_qty
        })
        st.success("✅ Configurações aplicadas com sucesso!")
    
    st.divider()
    
    # Seção de teste dos componentes
    st.subheader("3. Teste dos Componentes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧪 Testar Formatação de Dados", use_container_width=True):
            with st.spinner("Testando formatação..."):
                try:
                    municipality_data = PAPDataFormatter.format_municipality_data()
                    services_config = PAPDataFormatter.format_services_configuration()
                    validation = PAPDataFormatter.validate_data_completeness()
                    
                    st.success("✅ Formatação testada com sucesso!")
                    
                    with st.expander("📊 Dados Formatados"):
                        st.json(municipality_data)
                        st.write("Serviços configurados:", len(services_config))
                        st.write("Dados completos:", validation['is_complete'])
                        
                except Exception as e:
                    st.error(f"❌ Erro na formatação: {str(e)}")
    
    with col2:
        if st.button("📈 Testar Geração de Gráficos", use_container_width=True):
            with st.spinner("Gerando gráficos..."):
                try:
                    scenarios_data = {'Regular': 100000, 'Suficiente': 115000, 'Bom': 135000, 'Ótimo': 160000}
                    chart = generate_chart_for_pdf('scenarios_comparison', scenarios_data)
                    
                    if chart:
                        st.success("✅ Gráfico gerado com sucesso!")
                        st.info(f"Tamanho do gráfico: {len(chart)} caracteres base64")
                    else:
                        st.error("❌ Erro na geração do gráfico")
                        
                except Exception as e:
                    st.error(f"❌ Erro na geração: {str(e)}")
    
    st.divider()
    
    # Seção de teste completo
    st.subheader("4. Teste Completo do Sistema")
    
    if st.button("📄 Gerar Relatório PDF de Teste", use_container_width=True, type="primary"):
        with st.spinner("Gerando relatório PDF de teste..."):
            try:
                pdf_data = generate_pap_report()
                
                if pdf_data and len(pdf_data) > 0:
                    st.success(f"✅ Relatório PDF gerado com sucesso! ({len(pdf_data)} bytes)")
                    
                    # Botão de download
                    filename = f"teste_relatorio_pap_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                    st.download_button(
                        label="⬇️ Baixar Relatório de Teste",
                        data=pdf_data,
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                    # Estatísticas do arquivo
                    st.info(f"""
                    **Estatísticas do Arquivo:**
                    - Tamanho: {len(pdf_data):,} bytes ({len(pdf_data)/1024:.1f} KB)
                    - Nome: {filename}
                    - Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}
                    """)
                    
                else:
                    st.error("❌ Erro: PDF vazio ou não gerado")
                    
            except Exception as e:
                st.error(f"❌ Erro na geração do PDF: {str(e)}")
                st.exception(e)
    
    # Informações sobre o teste
    st.divider()
    st.subheader("ℹ️ Informações do Teste")
    
    st.info("""
    **O que este teste verifica:**
    
    1. **Formatação de Dados**: Extração e formatação dos dados do session_state
    2. **Geração de Gráficos**: Criação de visualizações matplotlib para PDF
    3. **Geração de PDF**: Criação do documento completo com todas as seções
    4. **Integridade**: Verificação se o arquivo final está correto
    
    **Para usar em produção:**
    - Execute a calculadora principal
    - Realize os cálculos completos
    - Use o botão "📄 Gerar Relatório PDF Completo" na página de resultados
    """)

if __name__ == "__main__":
    # Este código só executa se o arquivo for chamado diretamente
    create_test_interface()
