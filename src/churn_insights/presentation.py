"""Header and hero from the first dashboard version."""
import streamlit as st


def render_header():
    st.markdown('<div class="topbar"><div class="brand"><span class="brand-mark">ci<span>˙</span></span><span>CHURN<span class="brand-light"> INSIGHTS</span></span></div><div class="topbar-right"><span class="status-dot"></span> Ambiente local <span class="separator">/</span> Inteligência de retenção</div></div>', unsafe_allow_html=True)
    st.markdown('<section class="hero"><div class="hero-copy"><div class="eyebrow">INTELIGÊNCIA QUE APROXIMA</div><h1>Entenda os sinais.<br><span class="hero-emphasis">Antecipe a próxima ação.</span></h1><p>Uma visão clara da sua carteira para transformar dados<br class="desktop-break"> em melhores decisões de retenção.</p><div class="hero-tags"><span>● Random Forest</span><span>Base de demonstração</span></div></div><div class="hero-art" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="orbit orbit-three"></div><div class="art-core">↗</div><span class="art-label">DADOS → INSIGHTS → AÇÃO</span></div></section>', unsafe_allow_html=True)
