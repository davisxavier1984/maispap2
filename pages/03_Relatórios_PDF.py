"""
Página dedicada para geração de relatórios PDF.
"""
import streamlit as st
from datetime import datetime
import pandas as pd

# Configuração da página
st.set_page_config(
    page_title="Relatórios PDF - Calculadora PAP",
    page_icon="📄",
    layout="wide"
)

def main():
    st.title("📄 Relatórios PDF")
    st.markdown("---")
    
    # Verificar se existem cálculos realizados
    if not st.session_state.get('calculo_realizado', False):
        st.warning("⚠️ **Nenhum cálculo foi realizado ainda**")
        st.info("""
        Para gerar relatórios PDF, você precisa primeiro:
        
        1. Ir para a página **Calculadora PAP**
        2. Configurar os dados do município
        3. Selecionar os serviços
        4. Realizar os cálculos
        
        Após isso, retorne a esta página para gerar os relatórios.
        """)
        
        if st.button("🔙 Ir para Calculadora PAP", use_container_width=True):
            st.switch_page("app.py")
        return
    
    # Informações sobre os dados calculados
    st.subheader("📊 Dados dos Cálculos Realizados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        municipio = st.session_state.get('municipio_selecionado', 'Não informado')
        st.metric("Município", municipio)
        
    with col2:
        uf = st.session_state.get('uf_selecionada', 'Não informado')
        st.metric("UF", uf)
        
    with col3:
        competencia = st.session_state.get('competencia_selecionada', 'Não informado')
        st.metric("Competência", competencia)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        populacao = st.session_state.get('populacao', 0)
        st.metric("População", f"{populacao:,}".replace(',', '.'))
        
    with col2:
        classificacao = st.session_state.get('classificacao', 'Não informado')
        st.metric("Classificação", classificacao)
        
    with col3:
        vinculo = st.session_state.get('vinculo', 'Não informado')
        st.metric("Vínculo", vinculo)
    
    # Total PAP calculado
    total_pap = st.session_state.get('total_pap_calculado', 0)
    if total_pap > 0:
        st.success(f"💰 **Total PAP Calculado:** R$ {total_pap:,.2f}".replace(',', '.'))
    
    st.markdown("---")
    
    # Seção de geração de relatórios
    st.subheader("📋 Geração de Relatórios PDF")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("""
        **O relatório PDF inclui:**
        
        ✅ **Página de Capa** - Identificação completa do relatório  
        ✅ **Dados do Município** - Informações básicas e contextuais  
        ✅ **Fundamentação Legal** - Base legal e metodologia  
        ✅ **Configuração dos Serviços** - Serviços selecionados e quantidades  
        ✅ **Cálculos Detalhados** - Todos os 6 componentes PAP  
        ✅ **Análise de Cenários** - Comparações e projeções  
        ✅ **Gráficos Integrados** - Visualizações profissionais  
        ✅ **Resumo Executivo** - Totais, insights e recomendações  
        """)
    
    with col2:
        st.info("""
        **Especificações:**
        
        📄 Formato: A4  
        📊 Gráficos: Alta qualidade  
        🎨 Design: Profissional  
        ⚡ Tempo: 3-8 segundos  
        💾 Tamanho: 500KB-2MB  
        """)
    
    st.markdown("---")
    
    # Verificação de dependências e geração do relatório
    try:
        # Tentar importar as dependências do sistema de relatórios
        from reports.pdf_generator import generate_pap_report
        from reports.pdf_generator_interface_replica import generate_interface_replica_report
        
        # Mostrar botões de geração se as dependências estão disponíveis
        st.subheader("🚀 Opções de Relatório")
        
        # Criar duas colunas para os tipos de relatório
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📄 Relatório Completo")
            st.write("Relatório detalhado com análises, contexto legal e visualizações completas.")
            
            if st.button("📄 Gerar Relatório Completo", 
                        use_container_width=True, 
                        type="primary",
                        help="Relatório completo com todas as seções e análises"):
                
                with st.spinner("Gerando relatório completo... Por favor, aguarde..."):
                    try:
                        pdf_data = generate_pap_report()
                        
                        if pdf_data and len(pdf_data) > 0:
                            municipio_nome = st.session_state.get('municipio_selecionado', 'municipio').replace(' ', '_')
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            filename = f"relatorio_pap_completo_{municipio_nome}_{timestamp}.pdf"
                            
                            st.success("✅ **Relatório Completo gerado com sucesso!**")
                            
                            col_info1, col_info2 = st.columns(2)
                            with col_info1:
                                st.metric("Tamanho", f"{len(pdf_data)/1024:.1f} KB")
                            with col_info2:
                                st.metric("Páginas", "8-15 páginas")
                            
                            st.download_button(
                                label="⬇️ Baixar Relatório Completo",
                                data=pdf_data,
                                file_name=filename,
                                mime="application/pdf",
                                use_container_width=True,
                                help=f"Baixar: {filename}"
                            )
                            
                        else:
                            st.error("❌ Erro: Relatório vazio")
                            
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar relatório: {str(e)}")
        
        with col2:
            st.markdown("### 📊 Relatório Interface")
            st.write("Replica exatamente os gráficos e tabelas da interface, incluindo todas as tabelas de cenários.")
            
            if st.button("📊 Gerar Relatório Interface", 
                        use_container_width=True, 
                        type="secondary",
                        help="Replica exatamente os gráficos e tabelas da interface"):
                
                with st.spinner("Gerando relatório interface... Por favor, aguarde..."):
                    try:
                        pdf_data = generate_interface_replica_report()
                        
                        if pdf_data and len(pdf_data) > 0:
                            municipio_nome = st.session_state.get('municipio_selecionado', 'municipio').replace(' ', '_')
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            filename = f"relatorio_pap_interface_{municipio_nome}_{timestamp}.pdf"
                            
                            st.success("✅ **Relatório Interface gerado com sucesso!**")
                            
                            col_info1, col_info2 = st.columns(2)
                            with col_info1:
                                st.metric("Tamanho", f"{len(pdf_data)/1024:.1f} KB")
                            with col_info2:
                                st.metric("Páginas", "5-10 páginas")
                            
                            st.download_button(
                                label="⬇️ Baixar Relatório Interface",
                                data=pdf_data,
                                file_name=filename,
                                mime="application/pdf",
                                use_container_width=True,
                                help=f"Baixar: {filename}"
                            )
                            
                            # Destacar o que inclui
                            st.info("""
                            **Este relatório inclui:**
                            ✅ Todas as tabelas de cálculos da interface
                            ✅ Quadro comparativo de cenários (com cores)
                            ✅ Tabelas detalhadas por cenário
                            ✅ Gráficos de projeção (barras, linhas, pizza)
                            ✅ Tabelas de projeção temporal
                            """)
                            
                        else:
                            st.error("❌ Erro: Relatório vazio")
                            
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar relatório interface: {str(e)}")
        
        # Informações comparativas
        st.markdown("---")
        st.subheader("📋 Comparação dos Relatórios")
        
        comparison_data = {
            'Aspecto': [
                'Tabelas de Cálculos',
                'Tabelas de Cenários',
                'Gráficos da Interface',
                'Análise Legal/Contextual',
                'Conclusões e Recomendações',
                'Páginas Típicas',
                'Foco Principal'
            ],
            'Relatório Completo': [
                '✅ Todas',
                '✅ Sim',
                '✅ Modernos',
                '✅ Detalhada',
                '✅ Sim',
                '8-15',
                'Análise completa'
            ],
            'Relatório Interface': [
                '✅ Todas (idênticas)',
                '✅ Todas (com cores)',
                '✅ Idênticos à interface',
                '❌ Não',
                '❌ Não',
                '5-10',
                'Replica interface'
            ]
        }
        
        df_comparison = pd.DataFrame(comparison_data)
        st.table(df_comparison)
    
    except ImportError as e:
        # Caso as dependências não estejam instaladas
        st.warning("📦 **Dependências do Sistema de Relatórios PDF não encontradas**")
        
        st.info("""
        **Para habilitar o gerador de relatórios PDF, instale as dependências:**
        
        ```bash
        pip install reportlab matplotlib pillow
        ```
        
        **Ou instale todas as dependências do projeto:**
        
        ```bash
        pip install -r requirements.txt
        ```
        """)
        
        st.error(f"**Detalhes do erro:** {str(e)}")
        
        # Expandir com instruções detalhadas
        with st.expander("📋 Instruções Detalhadas de Instalação"):
            st.code("""
# PASSO 1: Abra o terminal/prompt de comando

# PASSO 2: Navegue até a pasta do projeto (se necessário)
cd caminho/para/o/projeto

# PASSO 3: Execute um dos comandos abaixo:

# Opção A - Instalar dependências específicas do PDF
pip install reportlab matplotlib pillow

# Opção B - Instalar todas as dependências do projeto  
pip install -r requirements.txt

# PASSO 4: Após a instalação, reinicie a aplicação
streamlit run app.py

# PASSO 5: Retorne a esta página para gerar relatórios
            """, language="bash")
            
            st.success("💡 **Dica:** Após instalar as dependências, atualize esta página para que o sistema de relatórios PDF fique disponível!")
    
    st.markdown("---")
    
    # Seção de histórico (futura implementação)
    with st.expander("📈 Funcionalidades Futuras"):
        st.write("""
        **Próximas atualizações incluirão:**
        
        🔄 **Histórico de Relatórios** - Lista de relatórios gerados anteriormente  
        📊 **Comparativos** - Relatórios comparando diferentes cenários  
        📧 **Envio por Email** - Enviar relatórios diretamente por email  
        🎨 **Templates Personalizados** - Diferentes layouts e estilos  
        📱 **Versão Mobile** - Relatórios otimizados para dispositivos móveis  
        ☁️ **Salvamento em Nuvem** - Armazenar relatórios online  
        """)
    
    # Rodapé com informações
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        📄 Sistema de Relatórios PDF - Calculadora PAP<br>
        Desenvolvido com Streamlit, ReportLab e Matplotlib
    </div>
    """, unsafe_allow_html=True)

main()
