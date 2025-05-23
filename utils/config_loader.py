import json
import streamlit as st # Importar streamlit para st.error, se necessário

CONFIG_FILE_PATH = "config.json"

def load_config():
    """
    Carrega as configurações do arquivo config.json.

    Retorna:
        dict: Um dicionário contendo as configurações, ou None se ocorrer um erro.
    """
    try:
        with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return config_data
    except FileNotFoundError:
        st.error(f"Erro: O arquivo de configuração {CONFIG_FILE_PATH} não foi encontrado.")
        return None
    except json.JSONDecodeError:
        st.error(f"Erro: O arquivo de configuração {CONFIG_FILE_PATH} contém JSON inválido.")
        return None
    except Exception as e:
        st.error(f"Ocorreu um erro inesperado ao carregar {CONFIG_FILE_PATH}: {e}")
        return None

if __name__ == '__main__':
    # Teste rápido para verificar o carregador de configuração
    config = load_config()
    if config:
        st.success("Configuração carregada com sucesso!")
        # st.json(config) # Descomente para ver a configuração no Streamlit
        print("Configuração carregada:")
        # print(json.dumps(config, indent=4, ensure_ascii=False)) # Print formatado no console
    else:
        st.error("Falha ao carregar a configuração.")

