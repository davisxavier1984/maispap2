"""
Funções úteis para a interface da Calculadora PAP.
"""
import streamlit as st

def style_metric_cards(
    background_color: str = "#f5f5f5",
    border_size_px: int = 1,
    border_color: str = "#f39c12",
    border_radius_px: int = 5,
    border_left_color: str = "#003366",
    box_shadow: bool = True,
):
    """
    Define o estilo dos cartões de métricas.
    
    Args:
        background_color: Cor de fundo do cartão
        border_size_px: Tamanho da borda em pixels
        border_color: Cor da borda
        border_radius_px: Raio da borda em pixels
        border_left_color: Cor da borda esquerda
        box_shadow: Se deve aplicar sombra ou não
    """
    box_shadow_str = (
        "box-shadow: 0 0.15rem 1.75rem 0 rgba(58,59,69,.15) !important;"
        if box_shadow
        else "box-shadow: none !important;"
    )
    st.markdown(
        f"""
        <style>
            .reportview-container .main .block-container{{
                padding-top: 1rem;
            }}
            .card {{
                background-color: {background_color};
                border: {border_size_px}px solid {border_color};
                border-radius: {border_radius_px}px;
                padding: 5px;
                text-align: center;
                margin-bottom: 5px;
                {box_shadow_str}
            }}
            .card-title {{
                font-size: 0.7rem;
                font-weight: bold;
                margin-bottom: 0.2rem;
                color: #2c3e50;
            }}
            .card-value {{
                font-size: 1.5rem;
                color: {border_left_color};
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

def metric_card(title, value, delta=None, icon=None, color="blue", help=None):
    """
    Exibe um card de métrica estilizado.
    
    Args:
        title: Título do card
        value: Valor principal a ser exibido
        delta: Opcional, valor de delta/diferença
        icon: Opcional, ícone para exibir
        color: Cor do card (blue, green, red, yellow)
        help: Texto de ajuda
    """
    colors = {
        "blue": "#1E88E5",
        "green": "#4CAF50",
        "red": "#E53935",
        "yellow": "#FDD835",
    }
    
    style = f"""
    <style>
        div.metric-card {{
            background-color: white;
            border-radius: 8px;
            padding: 15px 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 10px;
            border-left: 5px solid {colors.get(color, colors["blue"])};
        }}
        div.metric-card h3 {{
            margin: 0;
            color: #555;
            font-size: 0.9rem;
            font-weight: 400;
        }}
        div.metric-card p.value {{
            margin: 10px 0 5px 0;
            color: #333;
            font-size: 1.5rem;
            font-weight: 700;
        }}
        div.metric-card p.delta {{
            margin: 0;
            font-size: 0.8rem;
        }}
        div.metric-card p.delta.positive {{
            color: #4CAF50;
        }}
        div.metric-card p.delta.negative {{
            color: #E53935;
        }}
        
        div.metric-card .icon {{
            float: right;
            margin-top: -40px;
            font-size: 1.8rem;
            opacity: 0.6;
        }}
    </style>
    """
    
    delta_html = ""
    if delta:
        delta_class = "positive" if "+" in str(delta) else "negative"
        delta_html = f'<p class="delta {delta_class}">{delta}</p>'
    
    icon_html = f'<div class="icon">{icon}</div>' if icon else ""
    
    help_attr = f'title="{help}"' if help else ""
    
    metric_html = f"""
    {style}
    <div class="metric-card" {help_attr}>
        <h3>{title}</h3>
        <p class="value">{value}</p>
        {delta_html}
        {icon_html}
    </div>
    """
    
    st.markdown(metric_html, unsafe_allow_html=True)
