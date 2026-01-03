import streamlit as st

def apply_custom_styles():
    """Aplica toda a estilização CSS customizada à aplicação."""
    st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .main {
        background-color: #0e1117;
        color: #fafafa;
    }
    h1, h2, h3 {
        color: #00e676; /* Verde Neon */
        font-family: 'Inter', sans-serif;
    }
    .stButton>button {
        background: linear-gradient(45deg, #00e676, #00b359);
        color: #0d1117;
        font-weight: 700;
        font-size: 14px;
        border-radius: 20px;
        border: none;
        padding: 0.4rem 1.2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease-in-out;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        width: auto;
        min-width: 120px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 230, 118, 0.4);
        color: #000;
    }
    .stButton>button:active {
        transform: translateY(1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    .metric-card {
        background-color: #1f2937;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00e676;
    }
    
    /* Otimização de Espaço e Fontes para Configuração */
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 14px;
    }
    label[data-testid="stWidgetLabel"] p {
        font-size: 12px !important;
        font-weight: 600;
        margin-bottom: -0.5rem;
    }
    div[data-testid="stNumberInput"] input {
        font-size: 13px;
        height: 2.2rem;
        min-height: 2.2rem;
    }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        font-size: 13px;
        min-height: 2.2rem;
        height: 2.2rem;
    }
    div[data-testid="stSlider"] label {
        font-size: 12px;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 14px;
    }
    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 2rem !important;
    }

    /* Estilização para st.segmented_control transformando em Abas Modernas (Tab Highlight) */
    div[data-testid="stSegmentedControl"] {
        background-color: #1f2937;
        padding: 4px;
        border-radius: 12px;
        gap: 6px;
        border: 1px solid #374151;
        width: fit-content;
        display: flex;
        flex-wrap: nowrap;
        overflow-x: auto; /* Fallback para telas muito pequenas */
    }
    div[data-testid="stSegmentedControl"] button {
        background-color: transparent !important;
        border: none !important;
        color: #9ca3af !important;
        font-weight: 500 !important;
        padding: 6px 20px !important;
        border-radius: 8px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        min-width: 140px; /* Garante que o texto não quebre/fique incompleto */
        white-space: nowrap;
    }
    div[data-testid="stSegmentedControl"] button[data-active="true"] {
        background-color: #00e676 !important;
        color: #0d1117 !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(0, 230, 118, 0.3) !important;
    }
    div[data-testid="stSegmentedControl"] button:hover:not([data-active="true"]) {
        color: #00e676 !important;
        background-color: rgba(0, 230, 118, 0.1) !important;
    }
    
    /* Estilo para transformar botão de popover em texto clicável na tabela */
    .popover-as-text button {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
        color: #00e676 !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-size: 14px !important;
        text-decoration: underline rgba(0, 230, 118, 0.3) !important;
        box-shadow: none !important;
        min-height: 0 !important;
        height: auto !important;
    }
    .popover-as-text button:hover {
        color: #00ff80 !important;
        text-decoration: underline !important;
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)
