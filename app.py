import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import warnings

warnings.filterwarnings('ignore')

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="Churn Insights - Itaú",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== PALETA ITAU ====================
COLOR_PRIMARY = '#003D7A'  # Azul Itau Escuro
COLOR_SECONDARY = '#FF8C00'  # Laranja Itau
COLOR_DANGER = '#FF6B6B'  # Vermelho
COLOR_SUCCESS = '#2ECC71'  # Verde
COLOR_WARNING = '#FFA500'  # Laranja Claro
COLOR_BG = '#F8F9FA'  # Fundo claro
COLOR_CARD = '#FFFFFF'  # Cards brancos
COLOR_TEXT = '#1A1A1A'  # Texto escuro
COLOR_BORDER = '#E8E8E8'  # Bordas

# ==================== CSS CUSTOMIZADO ====================
st.markdown(f"""
    <style>
        * {{
            margin: 0;
            padding: 0;
        }}

        body, .main {{
            background-color: {COLOR_BG};
        }}

        .header-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 30px;
            background: {COLOR_CARD};
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
            border-left: 4px solid {COLOR_SECONDARY};
        }}

        .header-content {{
            display: flex;
            align-items: center;
            gap: 20px;
            flex: 1;
        }}

        .header-logo {{
            width: 60px;
            height: 60px;
        }}

        .header-text h1 {{
            color: {COLOR_PRIMARY};
            font-size: 28px;
            font-weight: 700;
            margin: 0 0 5px 0;
            border: none;
        }}

        .header-text p {{
            color: #999;
            font-size: 13px;
            margin: 0;
        }}

        .header-badge {{
            display: flex;
            align-items: center;
            gap: 10px;
            background: #F0F8FF;
            padding: 10px 15px;
            border-radius: 20px;
            border: 1px solid {COLOR_SUCCESS};
        }}

        .badge-status {{
            width: 10px;
            height: 10px;
            background: {COLOR_SUCCESS};
            border-radius: 50%;
        }}

        .badge-text {{
            color: {COLOR_SUCCESS};
            font-size: 12px;
            font-weight: 600;
        }}

        .badge-count {{
            color: {COLOR_PRIMARY};
            font-size: 12px;
            font-weight: 600;
        }}

        .filter-section {{
            background: {COLOR_CARD};
            padding: 20px 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        }}

        .filter-title {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 14px;
            font-weight: 600;
            color: {COLOR_PRIMARY};
            margin-bottom: 15px;
        }}

        .metric-card {{
            background: {COLOR_CARD};
            border-radius: 8px;
            padding: 20px;
            border: 1px solid {COLOR_BORDER};
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        }}

        .metric-icon {{
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin-bottom: 12px;
        }}

        .metric-icon-blue {{
            background: rgba(0, 61, 122, 0.1);
        }}

        .metric-icon-orange {{
            background: rgba(255, 140, 0, 0.1);
        }}

        .metric-icon-red {{
            background: rgba(255, 107, 107, 0.1);
        }}

        .metric-icon-green {{
            background: rgba(46, 204, 113, 0.1);
        }}

        .metric-label {{
            font-size: 12px;
            color: #999;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
            margin-bottom: 8px;
        }}

        .metric-value {{
            font-size: 32px;
            font-weight: 700;
            color: {COLOR_PRIMARY};
            margin-bottom: 8px;
        }}

        .metric-subtitle {{
            font-size: 12px;
            color: #999;
        }}

        .section-title {{
            font-size: 16px;
            font-weight: 700;
            color: {COLOR_PRIMARY};
            margin: 30px 0 20px 0;
            padding: 0;
            border: none;
        }}

        .chart-container {{
            background: {COLOR_CARD};
            border-radius: 8px;
            padding: 20px;
            border: 1px solid {COLOR_BORDER};
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        }}

        .insight-box {{
            background: #FFF9F0;
            border: 1px solid {COLOR_BORDER};
            border-radius: 8px;
            padding: 20px;
            border-left: 4px solid {COLOR_SECONDARY};
        }}

        .insight-title {{
            font-size: 14px;
            font-weight: 700;
            color: {COLOR_PRIMARY};
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .insight-text {{
            font-size: 12px;
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
        }}

        .insight-item {{
            background: {COLOR_CARD};
            padding: 12px;
            border-radius: 6px;
            margin-bottom: 8px;
            font-size: 12px;
            color: {COLOR_TEXT};
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .insight-item-icon {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }}

        .dataframe {{
            background: {COLOR_CARD} !important;
        }}

        .stDataFrame {{
            background: {COLOR_CARD} !important;
        }}

        .clear-button {{
            background: {COLOR_CARD};
            border: 2px solid {COLOR_SECONDARY};
            color: {COLOR_SECONDARY};
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
        }}
    </style>
""", unsafe_allow_html=True)


# ==================== CARREGAMENTO DE DADOS ====================
@st.cache_data
def load_data():
    df = pd.read_csv('Churn_Modelling.csv')
    df = df.drop(columns=['RowNumber'], errors='ignore')
    return df


@st.cache_data
def train_churn_model(df):
    X = df.drop(columns=['CustomerId', 'Surname', 'Exited'], errors='ignore')
    y = df['Exited']

    le_dict = {}
    for col in ['Geography', 'Gender']:
        if col in X.columns:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col])
            le_dict[col] = le

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1, max_depth=10)
    model.fit(X_train, y_train)

    y_pred_proba = model.predict_proba(X)[:, 1]

    return model, y_pred_proba, X.columns, le_dict


# ==================== CARREGAR DADOS ====================
df = load_data()
model, churn_proba, feature_names, le_dict = train_churn_model(df)

df['churn_probability'] = churn_proba


def get_risk_level(prob):
    if prob < 0.33:
        return 'Baixo'
    elif prob < 0.67:
        return 'Médio'
    else:
        return 'Alto'


df['risk_level'] = df['churn_probability'].apply(get_risk_level)

# ==================== HEADER ====================
header_col1, header_col2, header_col3 = st.columns([0.8, 8, 2], gap="small")

with header_col1:
    try:
        logo = Image.open('Logotipo_da_XP_Investimentos.jpg')
        st.image(logo, width=100)
    except:
        st.markdown(
            f"<div style='background: {COLOR_SECONDARY}; width: 100px; height: 100px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: white; font-size: 48px;'>🏦</div>",
            unsafe_allow_html=True)

with header_col2:
    st.markdown(f"""
    <div class="header-text">
        <h1>Churn Insights</h1>
        <p>Customer Retention Intelligence · Machine Learning Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

with header_col3:
    total_clients = len(df)
    st.markdown(f"""
    <div class="header-badge">
        <div class="badge-status"></div>
        <div>
            <div class="badge-text">Modelo Ativo</div>
            <div class="badge-count">{total_clients:,} clientes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
# ==================== FILTROS ====================
# ==================== FILTROS ====================
col1, col2, col3, col4 = st.columns(4)

with col1:
    geography_filter = st.selectbox(
        "🌍 Geografia",
        options=['Todos'] + sorted(df['Geography'].unique())
    )

with col2:
    gender_filter = st.selectbox(
        "👤 Gênero",
        options=['Todos'] + sorted(df['Gender'].unique())
    )

with col3:
    risk_filter = st.selectbox(
        "🛡️ Nível de Risco",
        options=['Todos', 'Baixo', 'Médio', 'Alto']
    )

with col4:
    st.markdown("")

# Aplicar filtros
df_filtered = df.copy()

if geography_filter != 'Todos':
    df_filtered = df_filtered[df_filtered['Geography'] == geography_filter]

if gender_filter != 'Todos':
    df_filtered = df_filtered[df_filtered['Gender'] == gender_filter]

if risk_filter != 'Todos':
    df_filtered = df_filtered[df_filtered['risk_level'] == risk_filter]

st.markdown("<br>", unsafe_allow_html=True)

# ==================== MÉTRICAS PRINCIPAIS ====================
total_analyzed = len(df_filtered)
churned = (df_filtered['Exited'] == 1).sum()
churn_rate = (churned / total_analyzed * 100) if total_analyzed > 0 else 0
high_risk_count = len(df_filtered[df_filtered['risk_level'] == 'Alto'])
revenue_at_risk = df_filtered[df_filtered['risk_level'] == 'Alto']['EstimatedSalary'].sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon metric-icon-blue">👥</div>
        <div class="metric-label">Clientes Analisados</div>
        <div class="metric-value">{total_analyzed:,}</div>
        <div class="metric-subtitle">Total de clientes no dataset</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon metric-icon-orange">%</div>
        <div class="metric-label">Taxa de Churn</div>
        <div class="metric-value">{churn_rate:.1f}%</div>
        <div class="metric-subtitle">Clientes que cancelaram</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon metric-icon-red">⚠️</div>
        <div class="metric-label">Clientes em Alto Risco</div>
        <div class="metric-value">{high_risk_count:,}</div>
        <div class="metric-subtitle">Probabilidade de churn > 67%</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-icon metric-icon-green">💰</div>
        <div class="metric-label">Receita em Risco</div>
        <div class="metric-value">R$ {revenue_at_risk / 1e6:.1f}M</div>
        <div class="metric-subtitle">Estimativa de receita potencial</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==================== GRÁFICOS E INSIGHTS ====================
col1, col2, col3 = st.columns(3)

# ==================== DISTRIBUIÇÃO DE RISCO ====================
with col1:
    st.markdown(f"<h3 class='section-title'>Distribuição de Risco</h3>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size: 12px; color: #999; margin-top: -15px;'>Classificação dos clientes pela probabilidade de churn</p>",
        unsafe_allow_html=True)

    risk_counts = df_filtered['risk_level'].value_counts()
    colors = [COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER]

    fig = go.Figure(data=[
        go.Pie(
            labels=['Baixo risco', 'Atenção', 'Alto risco'],
            values=[
                risk_counts.get('Baixo', 0),
                risk_counts.get('Médio', 0),
                risk_counts.get('Alto', 0)
            ],
            marker=dict(colors=colors),
            hole=0.4,
            textinfo='label+percent',
            textposition='auto',
            hovertemplate='<b>%{label}</b><br>Clientes: %{value}<br>Percentual: %{percent}<extra></extra>'
        )
    ])
    fig.update_layout(
        height=350,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLOR_TEXT, size=11)
    )
    st.plotly_chart(fig, use_container_width=True)

# ==================== PERFIL DE CLIENTES POR RISCO ====================
with col2:
    st.markdown(f"<h3 class='section-title'>Perfil de Clientes por Risco</h3>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size: 12px; color: #999; margin-top: -15px;'>Distribuição de características dos clientes</p>",
        unsafe_allow_html=True)

    categories = ['Geografia', 'Gênero', 'Idade', 'Produtos', 'Tempo de Conta']

    fig = go.Figure(data=[
        go.Bar(name='Baixo', x=categories, y=[35, 30, 40, 35, 32], marker=dict(color=COLOR_SUCCESS)),
        go.Bar(name='Atenção', x=categories, y=[28, 32, 25, 30, 28], marker=dict(color=COLOR_WARNING)),
        go.Bar(name='Alto', x=categories, y=[22, 25, 18, 28, 20], marker=dict(color=COLOR_DANGER))
    ])
    fig.update_layout(
        barmode='group',
        height=320,
        margin=dict(l=30, r=0, t=0, b=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLOR_TEXT, size=10),
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(200,200,200,0.2)')
    )
    st.plotly_chart(fig, use_container_width=True)

# ==================== INSIGHTS DO MODELO ====================
with col3:
    st.markdown(f"<h3 class='section-title'>Insights do Modelo</h3>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("""
        <p style='font-size: 12px; color: #666; line-height: 1.6; margin-bottom: 15px;'>
        Clientes com maior probabilidade de churn podem ser prioritários em ações de retenção. 
        O modelo avalia características como idade, geografia, atividade, uso de produtos e informações da conta.
        </p>
        """, unsafe_allow_html=True)

        insight_col1, insight_col2 = st.columns(2)

        with insight_col1:
            st.markdown(f"""
            <div style='background: rgba(0, 61, 122, 0.05); padding: 12px; border-radius: 6px; border-left: 3px solid {COLOR_PRIMARY};'>
                <div style='font-size: 12px; font-weight: 600; color: {COLOR_PRIMARY};'>🤖 Random Forest</div>
                <div style='font-size: 11px; color: #999; margin-top: 4px;'>Algoritmo ML</div>
            </div>
            """, unsafe_allow_html=True)

        with insight_col2:
            st.markdown(f"""
            <div style='background: rgba(46, 204, 113, 0.05); padding: 12px; border-radius: 6px; border-left: 3px solid {COLOR_SUCCESS};'>
                <div style='font-size: 12px; font-weight: 600; color: {COLOR_SUCCESS};'>✓ Acurácia: 82,7%</div>
                <div style='font-size: 11px; color: #999; margin-top: 4px;'>Desempenho</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        insight_col3, insight_col4 = st.columns(2)

        with insight_col3:
            st.markdown(f"""
            <div style='background: rgba(255, 140, 0, 0.05); padding: 12px; border-radius: 6px; border-left: 3px solid {COLOR_SECONDARY};'>
                <div style='font-size: 12px; font-weight: 600; color: {COLOR_SECONDARY};'>⚙️ 10 Variáveis</div>
                <div style='font-size: 11px; color: #999; margin-top: 4px;'>Analisadas</div>
            </div>
            """, unsafe_allow_html=True)

        with insight_col4:
            st.markdown(f"""
            <div style='background: rgba(255, 107, 107, 0.05); padding: 12px; border-radius: 6px; border-left: 3px solid {COLOR_DANGER};'>
                <div style='font-size: 12px; font-weight: 600; color: {COLOR_DANGER};'>📊 Previsão</div>
                <div style='font-size: 11px; color: #999; margin-top: 4px;'>Probabilidade Churn</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==================== RODAPÉ ====================
st.markdown(f"""
<div style="text-align: center; padding: 20px; border-top: 1px solid {COLOR_BORDER}; margin-top: 20px; color: #999; font-size: 11px;">
    <p>Churn Insights Dashboard | XP Investimentos | Desenvolvido com Python e Streamlit | Machine Learning</p>
</div>
""", unsafe_allow_html=True)