#!/usr/bin/env python3
"""
Teste para a funcionalidade de tabela de vínculo e acompanhamento.
"""
import json
import sys
import pandas as pd

# Adicionar o diretório raiz ao path
sys.path.append('.')

def teste_funcoes():
    """Testa as novas funções com os dados de cache existentes."""
    
    print("Testando funcoes de vinculo e acompanhamento...")
    
    try:
        # Carregar dados do cache
        with open('data_cache.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
        print("OK - Dados carregados com sucesso")
        
        # Importar e testar as funções
        from utils.data import extrair_dados_vinculo_acompanhamento, criar_tabela_vinculo_acompanhamento
        
        # Testar extração de dados
        dados_vinculo = extrair_dados_vinculo_acompanhamento(dados)
        print("OK - Funcao de extracao executada")
        
        print("\nDados extraidos:")
        print(f"eSF - Tem equipes: {dados_vinculo['esf']['tem_equipes']}")
        if dados_vinculo['esf']['tem_equipes']:
            print(f"eSF - Quantidade: {dados_vinculo['esf']['quantidade_equipes']}")
            print(f"eSF - Classificacao Vinculo: {dados_vinculo['esf']['classificacao_vinculo']}")
            print(f"eSF - Classificacao Qualidade: {dados_vinculo['esf']['classificacao_qualidade']}")
            print(f"eSF - Valor Vinculo: R$ {dados_vinculo['esf']['valor_vinculo']:,.2f}")
            print(f"eSF - Valor Qualidade: R$ {dados_vinculo['esf']['valor_qualidade']:,.2f}")
        
        print(f"\neAP - Tem equipes: {dados_vinculo['eap']['tem_equipes']}")
        if dados_vinculo['eap']['tem_equipes']:
            print(f"eAP - Quantidade: {dados_vinculo['eap']['quantidade_equipes']}")
            print(f"eAP - Classificacao Vinculo: {dados_vinculo['eap']['classificacao_vinculo']}")
            print(f"eAP - Classificacao Qualidade: {dados_vinculo['eap']['classificacao_qualidade']}")
            print(f"eAP - Valor Vinculo: R$ {dados_vinculo['eap']['valor_vinculo']:,.2f}")
            print(f"eAP - Valor Qualidade: R$ {dados_vinculo['eap']['valor_qualidade']:,.2f}")
        
        # Testar criação da tabela
        tabela = criar_tabela_vinculo_acompanhamento(dados_vinculo)
        print("OK - Funcao de criacao de tabela executada")
        
        print("\nTabela gerada:")
        if not tabela.empty:
            print(tabela.to_string(index=False))
        else:
            print("Tabela vazia - nenhuma equipe eSF ou eAP encontrada")
            
        print("\nTeste concluido com sucesso!")
        
    except FileNotFoundError:
        print("ERRO - Arquivo data_cache.json nao encontrado")
    except json.JSONDecodeError:
        print("ERRO - Erro ao decodificar data_cache.json")
    except ImportError as e:
        print(f"ERRO - Erro ao importar funcoes: {e}")
    except Exception as e:
        print(f"ERRO - Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    teste_funcoes()