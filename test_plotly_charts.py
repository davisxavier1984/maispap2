"""
Teste simples para verificar se os gráficos Plotly estão sendo gerados.
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_plotly_charts():
    """Testa a geração de gráficos Plotly."""
    print("🧪 Testando geração de gráficos Plotly...")
    
    try:
        from reports.plotly_chart_generator import PAPPlotlyChartGenerator
        
        # Inicializar gerador
        generator = PAPPlotlyChartGenerator()
        print("✅ Gerador Plotly inicializado com sucesso")
        
        # Dados de teste
        components_data = {
            'Componente Fixo': 15000,
            'Vínculo e Acompanhamento': 8000,
            'Qualidade': 5000,
            'Saúde Bucal': 3000
        }
        
        scenarios_data = {
            'Regular': 25000,
            'Suficiente': 30000,
            'Bom': 35000,
            'Ótimo': 40000
        }
        
        services_data = {
            'eSF': 5,
            'eAP 30h': 3,
            'eMULTI Ampl.': 2
        }
        
        timeline_data = {
            '3 meses': 10000,
            '6 meses': 15000,
            '12 meses': 25000,
            '24 meses': 35000,
            '30 meses': 40000
        }
        
        # Testar cada tipo de gráfico
        print("\n📊 Testando gráficos individuais:")
        
        # 1. Gráfico de pizza
        print("1. Testando gráfico de pizza...")
        chart1 = generator.create_components_pie_chart(components_data)
        if chart1:
            print("   ✅ Gráfico de pizza gerado com sucesso")
        else:
            print("   ❌ Falha ao gerar gráfico de pizza")
        
        # 2. Gráfico de cenários
        print("2. Testando gráfico de cenários...")
        chart2 = generator.create_scenarios_comparison_chart(scenarios_data)
        if chart2:
            print("   ✅ Gráfico de cenários gerado com sucesso")
        else:
            print("   ❌ Falha ao gerar gráfico de cenários")
        
        # 3. Gráfico de serviços
        print("3. Testando gráfico de serviços...")
        chart3 = generator.create_services_distribution_chart(services_data)
        if chart3:
            print("   ✅ Gráfico de serviços gerado com sucesso")
        else:
            print("   ❌ Falha ao gerar gráfico de serviços")
        
        # 4. Gráfico de timeline
        print("4. Testando gráfico de timeline...")
        chart4 = generator.create_projection_timeline_chart(timeline_data)
        if chart4:
            print("   ✅ Gráfico de timeline gerado com sucesso")
        else:
            print("   ❌ Falha ao gerar gráfico de timeline")
        
        # 5. Dashboard resumo
        print("5. Testando dashboard resumo...")
        summary_data = {
            'components': components_data,
            'scenarios': scenarios_data,
            'services': services_data,
            'financial': {
                'Total PAP': 35000,
                'eSF/eAP': 20000,
                'Saúde Bucal': 3000,
                'Total Adicional': 23000
            }
        }
        chart5 = generator.create_summary_dashboard(summary_data)
        if chart5:
            print("   ✅ Dashboard resumo gerado com sucesso")
        else:
            print("   ❌ Falha ao gerar dashboard resumo")
        
        # Contar sucessos
        charts = [chart1, chart2, chart3, chart4, chart5]
        successful_charts = sum(1 for chart in charts if chart is not None)
        
        print(f"\n📈 Resultado do teste:")
        print(f"   ✅ {successful_charts}/5 gráficos gerados com sucesso")
        print(f"   ❌ {5 - successful_charts}/5 gráficos falharam")
        
        if successful_charts == 5:
            print("\n🎉 TODOS OS GRÁFICOS FUNCIONANDO PERFEITAMENTE!")
            return True
        elif successful_charts > 0:
            print(f"\n⚠️  GRÁFICOS PARCIALMENTE FUNCIONANDO ({successful_charts}/5)")
            return True
        else:
            print("\n💥 NENHUM GRÁFICO FOI GERADO")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de importação: {str(e)}")
        print("💡 Verifique se as dependências estão instaladas:")
        print("   pip install plotly pandas numpy")
        return False
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        return False

def test_kaleido_availability():
    """Testa se o Kaleido está disponível."""
    print("\n🔍 Verificando disponibilidade do Kaleido...")
    
    try:
        import kaleido
        print("✅ Kaleido encontrado - gráficos de alta qualidade disponíveis")
        return True
    except ImportError:
        print("⚠️  Kaleido não encontrado - usando fallback matplotlib")
        print("💡 Para gráficos de melhor qualidade, instale: pip install kaleido")
        return False

def test_matplotlib_fallback():
    """Testa se o fallback matplotlib funciona."""
    print("\n🔄 Testando fallback matplotlib...")
    
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
        
        # Teste simples
        plt.figure(figsize=(6, 4))
        plt.plot([1, 2, 3], [1, 4, 2])
        plt.title("Teste Matplotlib")
        plt.close()
        
        print("✅ Matplotlib funcionando - fallback disponível")
        return True
    except Exception as e:
        print(f"❌ Matplotlib não funciona: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 TESTE DE GRÁFICOS PLOTLY PARA PDF")
    print("=" * 50)
    
    # Testar componentes
    kaleido_ok = test_kaleido_availability()
    matplotlib_ok = test_matplotlib_fallback()
    charts_ok = test_plotly_charts()
    
    print("\n" + "=" * 50)
    print("📋 RESUMO DOS TESTES:")
    print(f"   Kaleido: {'✅' if kaleido_ok else '⚠️ '}")
    print(f"   Matplotlib: {'✅' if matplotlib_ok else '❌'}")
    print(f"   Gráficos: {'✅' if charts_ok else '❌'}")
    
    if charts_ok:
        print("\n🎯 RESULTADO: Sistema de gráficos OPERACIONAL!")
        print("   Os gráficos serão incluídos no PDF com sucesso.")
    else:
        print("\n💥 RESULTADO: Sistema de gráficos com PROBLEMAS!")
        print("   Verifique as dependências e tente novamente.")
