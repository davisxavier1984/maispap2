# Calculadora PAP

## Estrutura do Projeto

O projeto foi refatorado para melhorar a organização e manutenção do código, dividindo-o em módulos menores e componentes reutilizáveis:

### Arquivos Principais
- `app.py`: Arquivo principal que inicia a aplicação
- `api.py`: Funções para comunicação com a API de financiamento da saúde
- `calculations.py`: Funções para os cálculos dos componentes do PAP
- `interface.py`: Funções para construção da interface gráfica principal
- `utils.py`: Funções utilitárias gerais

### Componentes Modulares
- `components/services_interface.py`: Interface para seleção de serviços
- `components/scenarios_analysis.py`: Análise de cenários da Calculadora PAP
- `components/scenarios_report.py`: Geração de relatórios de cenários
- `components/resource_projection.py`: Projeções de recursos e cálculos adicionais

## Como Executar

Para executar a aplicação, use o comando:

```bash
streamlit run app.py
```

## Arquivos de Configuração

- `config.json`: Contém as configurações e valores de referência para cálculos
- `data.json`: Armazena os dados consultados da API

## Responsabilidades de cada Módulo

### app.py
- Ponto de entrada da aplicação
- Configura a página inicial do Streamlit
- Inicializa a interface principal

### api.py
- Funções para consulta à API de financiamento da saúde
- Carregamento e salvamento de dados JSON

### calculations.py
- Cálculos dos componentes do PAP
- Formatação dos resultados
- Orquestração dos componentes adicionais
- Geração das tabelas de resultados

### interface.py
- Configuração da interface principal
- Controle do fluxo da aplicação
- Coordenação entre entrada de dados e exibição de resultados

### components/services_interface.py
- Interface para seleção de serviços
- Gestão de valores e quantidades por serviço
- Interface de implantação

### components/scenarios_analysis.py
- Geração de texto de análise dos cenários
- Comparação entre diferentes níveis de desempenho

### components/scenarios_report.py
- Geração de relatórios detalhados por cenário
- Quadros de comparação entre cenários
- Tabelas com formatação condicional

### components/resource_projection.py
- Projeções de aumento de recursos
- Cálculo do cenário regular
- Visualizações comparativas de recursos
