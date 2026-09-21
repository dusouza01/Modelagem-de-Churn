"""Header from the first dashboard version."""
import base64
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
LOGO_PATH = ROOT / "imagens" / "Logotipo_da_XP_Investimentos.jpg"


@st.cache_data
def _logo_data_uri():
    encoded = base64.b64encode(LOGO_PATH.read_bytes()).decode()
    return f"data:image/jpeg;base64,{encoded}"


def render_header():
    st.markdown(
        f'<div class="topbar"><div class="brand"><img class="brand-mark" src="{_logo_data_uri()}" alt="XP Investimentos"><span>Previsão de Churn</span></div>'
        '<div class="topbar-right"><span class="status-dot"></span> Ambiente local <span class="separator">/</span> Inteligência de retenção</div></div>',
        unsafe_allow_html=True,
    )
