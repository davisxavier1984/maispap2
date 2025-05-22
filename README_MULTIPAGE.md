# Documentação do Sistema Multi-Página da Calculadora PAP

## Visão Geral

Este documento descreve a implementação do sistema multi-página na Calculadora PAP, utilizando o sistema nativo de páginas do Streamlit.

## Estrutura de Arquivos

A aplicação segue a estrutura padrão de multi-página do Streamlit:

- `app.py` - Página principal da aplicação, ponto de entrada
- `/pages/` - Diretório contendo páginas adicionais
  - `01_Projeção_Financeira.py` - Página de projeção financeira detalhada
- `/components/` - Diretório com componentes reutilizáveis
  - `resource_projection.py` - Componente para cálculo e exibição da projeção de recursos
  - `scenarios_report.py` - Componente para geração de relatórios de cenários
  - outros componentes...

## Compartilhamento de Estado

O compartilhamento de dados entre páginas é feito através do `st.session_state`, que permite que variáveis sejam acessadas em qualquer página da aplicação.

Principais variáveis de estado:

- `st.session_state['dados']` - Dados do município selecionado
- `st.session_state['valor_cenario_regular']` - Valor do cenário regular calculado
- `st.session_state['aumento_mensal']` - Aumento mensal projetado
- `st.session_state['aumento_anual']` - Aumento anual projetado
- `st.session_state['calculo_realizado']` - Flag indicando se o cálculo foi realizado
- `st.session_state['percentual_XXm']` e `st.session_state['valor_XXm']` - Percentuais e valores para períodos de XX meses (3, 6, 9, 12, 15, 18, 21, 24, 27, 30)

## Navegação entre Páginas

A navegação entre páginas é gerenciada pelo sistema nativo do Streamlit, através do menu lateral gerado automaticamente.

## Arquivos Legados

Os seguintes arquivos são considerados legados e não são mais utilizados ativamente:

- `app.py` - Antigo ponto de entrada da aplicação
- `navigation.py` - Sistema de navegação antigo
- `components/financial_projection_page.py` - Implementação antiga da página de projeção financeira

Estes foram substituídos pelo sistema de páginas nativo do Streamlit.

## Melhorias Realizadas

1. Remoção de código duplicado no arquivo `resource_projection.py` para inicialização de variáveis de estado.
2. Documentação dos arquivos legados com avisos claros.
3. Simplificação da estrutura do projeto para seguir o padrão multi-página do Streamlit.

## Execução da Aplicação

Para executar a aplicação, use:

```bash
streamlit run app.py
```

## Problemas Conhecidos

- [Descrever aqui problemas conhecidos, se houver]

## Futuras Melhorias

- [Descrever aqui possíveis melhorias futuras, se houver]
