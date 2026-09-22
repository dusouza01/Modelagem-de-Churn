"""Project identity and applied machine learning overview."""
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
    st.markdown(f'<div class="topbar"><div class="brand"><img class="brand-mark" src="{_logo_data_uri()}" alt="XP Investimentos"><span>CHURN<span class="brand-light"> ANALISYS</span></span></div><div class="topbar-right"><span class="status-dot"></span> Ambiente local <span class="separator">/</span> Inteligência de retenção</div></div>', unsafe_allow_html=True)
    st.markdown('<section class="hero"><div class="hero-copy"><div class="eyebrow">CIÊNCIA DE DADOS · MACHINE LEARNING APLICADO</div><h1>Entenda os sinais.<br><span class="hero-emphasis">Antecipe a próxima ação.</span></h1><p>Uma aplicação de Machine Learning e Ciência de Dados para estimar risco de churn e apoiar a priorização de clientes, com avaliação histórica, probabilidades calibradas e um dashboard interativo.</p><div class="hero-tags"><span>Python · scikit-learn</span><span>Random Forest calibrado</span><span>Streamlit · Plotly</span></div></div><div class="hero-art" aria-hidden="true"><div class="orbit orbit-one"></div><div class="orbit orbit-two"></div><div class="orbit orbit-three"></div><div class="art-core">↗</div><span class="art-label">DADOS → INSIGHTS → AÇÃO</span></div></section>', unsafe_allow_html=True)


def render_ml_method(metrics):
    with st.container(border=True):
        st.subheader("Como o Machine Learning transforma dados em prioridades")
        st.write("O projeto aplica aprendizado supervisionado para estimar churn: o Random Forest aprende relações entre características dos clientes e o cancelamento registrado em Exited. A análise exploratória revela padrões da carteira; a inferência transforma os dados de cada cliente em uma probabilidade calibrada.")
        left, right = st.columns(2)
        with left:
            st.markdown("#### Treino e teste separados")
            st.write(f"A divisão estratificada reserva {metrics['train_count']:,} registros para treino (80%) e {metrics['test_count']:,} para teste (20%), preservando aproximadamente a proporção de cancelamentos. A semente 42 torna a divisão reproduzível. O teste fica fora do ajuste do modelo e da calibração.")
            st.markdown("#### Pipeline de pré-processamento")
            st.write("ColumnTransformer e OneHotEncoder codificam país e gênero dentro do pipeline do scikit-learn. Dez variáveis alimentam o Random Forest, com 100 árvores e profundidade máxima 10. ID, sobrenome e o alvo Exited não entram como preditores.")
        with right:
            st.markdown("#### Calibração das probabilidades")
            st.write("CalibratedClassifierCV aplica uma transformação sigmoide às estimativas do modelo. A validação cruzada estratificada divide somente o treino em cinco partes: cada previsão usada para calibrar vem de um modelo que não treinou naquele registro. Com ensemble=False, o estimador final é ajustado em todo o treino.")
            st.markdown("#### Inferência e priorização")
            st.write("O modelo salvo estima probabilidades sem novo treinamento. O ranking seleciona os maiores riscos na carteira completa, entre os clientes que atingem o risco mínimo, conforme a capacidade e o público definidos. Os filtros permitem investigar essa seleção sem alterar a prioridade de cada cliente.")
        st.caption("ROC AUC avalia a ordenação do risco; Brier e log loss medem o erro das probabilidades. A curva de confiabilidade compara probabilidades estimadas e frequências observadas. A avaliação é histórica e não mede o efeito de campanhas de retenção.")
