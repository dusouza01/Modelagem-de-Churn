import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report, roc_auc_score, roc_curve
import warnings

warnings.filterwarnings('ignore')

# ==================== CONFIGURAÇÃO DA PÁGINA ====================
st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== PALETA ITAU ====================
COLOR_PRIMARY = '#4C72B0'  # Azul Itau
COLOR_SECONDARY = '#DD8452'  # Laranja Itau
COLOR_TERTIARY = '#55A868'  # Verde Itau
COLOR_BG = '#F8F9FA'  # Background claro
COLOR_TEXT = '#333333'  # Texto escuro
COLOR_BORDER = '#E0E0E0'  # Bordas sutis

PALETA = [COLOR_PRIMARY, COLOR_SECONDARY, COLOR_TERTIARY]

# ==================== CSS CUSTOMIZADO ====================
st.markdown(f"""
    <style>
        /* Global */
        :root {{
            --primary-color: {COLOR_PRIMARY};
            --secondary-color: {COLOR_SECONDARY};
            --tertiary-color: {COLOR_TERTIARY};
        }}

        body, .main {{
            background-color: {COLOR_BG};
            color: {COLOR_TEXT};
        }}

        /* Headers */
        h1 {{
            color: {COLOR_PRIMARY};
            font-weight: 700;
            font-size: 2.2em;
            margin-bottom: 0.5em;
            border-bottom: 3px solid {COLOR_PRIMARY};
            padding-bottom: 0.5em;
        }}

        h2 {{
            color: {COLOR_PRIMARY};
            font-weight: 600;
            font-size: 1.6em;
            margin-top: 1.5em;
            margin-bottom: 0.8em;
        }}

        h3 {{
            color: {COLOR_PRIMARY};
            font-weight: 500;
            font-size: 1.2em;
        }}

        /* Métrica Cards */
        .metric-card {{
            background-color: white;
            padding: 24px;
            border-radius: 8px;
            border-left: 5px solid {COLOR_PRIMARY};
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
            transition: all 0.3s ease;
        }}

        .metric-card:hover {{
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
            transform: translateY(-2px);
        }}

        /* Sidebar */
        .css-1d391kg {{
            background-color: white;
        }}

        /* Info/Success/Warning boxes */
        .stAlert {{
            border-radius: 8px;
            border: 1px solid {COLOR_BORDER};
            padding: 16px;
        }}

        .stSuccess {{
            border-left: 4px solid {COLOR_TERTIARY};
        }}

        .stInfo {{
            border-left: 4px solid {COLOR_PRIMARY};
        }}

        .stWarning {{
            border-left: 4px solid {COLOR_SECONDARY};
        }}

        /* Dataframe styling */
        .dataframe {{
            border-collapse: collapse;
            width: 100%;
        }}

        .dataframe thead tr {{
            background-color: {COLOR_PRIMARY};
            color: white;
            font-weight: 600;
        }}

        .dataframe tbody tr:nth-child(odd) {{
            background-color: {COLOR_BG};
        }}

        .dataframe tbody tr:hover {{
            background-color: #F0F0F0;
        }}

        /* Buttons */
        .stButton > button {{
            background-color: {COLOR_PRIMARY};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 24px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}

        .stButton > button:hover {{
            background-color: {COLOR_SECONDARY};
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}

        /* Divider */
        hr {{
            border: 0;
            height: 2px;
            background: linear-gradient(to right, {COLOR_PRIMARY}, {COLOR_SECONDARY}, {COLOR_TERTIARY});
            margin: 2em 0;
        }}

        /* Selectbox/Multiselect */
        .stMultiSelect > div {{
            border-radius: 6px;
            border: 2px solid {COLOR_BORDER};
        }}

        .stSelectbox > div {{
            border-radius: 6px;
        }}

        /* Spinner */
        .stSpinner > div {{
            border-color: {COLOR_PRIMARY};
        }}
    </style>
""", unsafe_allow_html=True)


# ==================== FUNÇÕES DE CARREGAMENTO ====================
@st.cache_data
def load_data():
    """Carrega e prepara dados do CSV"""
    df = pd.read_csv('Churn_Modelling.csv')
    df = df.drop(columns=['RowNumber'])
    return df


@st.cache_data
def prepare_model_data(df):
    """Adiciona feature engineering ao dataframe"""
    df_model = df.copy()

    # Criar faixas etárias
    bins = [18, 31, 41, 51, 61, float('inf')]
    labels = ['18-30', '31-40', '41-50', '51-60', '61+']
    df_model['AgeGroup'] = pd.cut(df_model['Age'], bins=bins, labels=labels, right=False)

    return df_model


@st.cache_data
def train_models(df):
    """Treina modelos de ML"""
    df_model = df.copy()

    # Preparar dados
    X = df_model.drop(columns=['CustomerId', 'Surname', 'Exited', 'AgeGroup'])
    y = df_model['Exited']

    # Codificar variáveis categóricas
    le_dict = {}
    for col in ['Geography', 'Gender']:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col])
        le_dict[col] = le

    # Dividir dados
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Escalar features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Treinar modelos
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    }

    results = {}
    for name, model in models.items():
        if name == 'Logistic Regression':
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]

        results[name] = {
            'model': model,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba,
            'scaler': scaler if name == 'Logistic Regression' else None,
            'le_dict': le_dict,
            'X_test': X_test_scaled if name == 'Logistic Regression' else X_test,
            'y_test': y_test,
            'X_train': X_train_scaled if name == 'Logistic Regression' else X_train
        }

    return results, X.columns


def calculate_metrics(y_true, y_pred, y_pred_proba):
    """Calcula métricas de performance"""
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

    return {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred),
        'recall': recall_score(y_true, y_pred),
        'f1': f1_score(y_true, y_pred),
        'auc': roc_auc_score(y_true, y_pred_proba)
    }


# ==================== CARREGAMENTO INICIAL ====================
df = load_data()
df = prepare_model_data(df)

# ==================== SIDEBAR ====================
with st.sidebar:
    st.markdown(
        f"<div style='text-align: center; padding: 20px 0;'><h2 style='margin: 0; border: none; color: {COLOR_PRIMARY};'>Customer Churn Prediction</h2></div>",
        unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 0.9em;'>Identificação de Clientes em Risco</p>",
                unsafe_allow_html=True)
    st.markdown("---")

pages = {
    "Visão Geral": "overview",
    "Exploração de Dados": "exploration",
    "Perfil do Cliente": "profile",
    "Fatores de Churn": "factors",
    "Modelo Preditivo": "model",
    "Clientes em Risco": "high_risk",
    "Impacto Financeiro": "impact",
    "Recomendações": "recommendations",
    "Tecnologias": "tech"
}

selected_page = st.sidebar.radio("Navegação", list(pages.keys()), label_visibility="collapsed")
page_key = pages[selected_page]

st.sidebar.markdown("---")
st.sidebar.markdown(
    f"<p style='text-align: center; font-size: 0.8em; color: #999;'>Desenvolvido com Python, Streamlit e Scikit-learn</p>",
    unsafe_allow_html=True)

# ==================== PAGE: OVERVIEW ====================
if page_key == "overview":
    st.title("Visão Geral")
    st.markdown("### Identificação antecipada de clientes com maior risco de cancelamento")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### O Problema
        Clientes estão cancelando suas contas, resultando em perda de receita e redução da base.

        ### O Objetivo
        Identificar antecipadamente quais clientes apresentam maior risco de cancelamento para priorizar ações de retenção.

        ### A Abordagem
        1. **Análise Exploratória** - Entender quem são os clientes que cancelam
        2. **Descoberta de Padrões** - Identificar características comuns
        3. **Modelagem Preditiva** - Treinar modelos para estimar risco individual
        4. **Priorização** - Identificar clientes com maior risco
        5. **Ação** - Direcionar recursos para retenção
        """)

    with col2:
        st.markdown("""
        ### Resultado Esperado
        Uma ferramenta que permite:
        - Identificar clientes em risco de forma automática
        - Entender razões por trás do cancelamento
        - Priorizar ações de retenção por impacto
        - Monitorar efetividade das estratégias

        ### Impacto de Negócio
        Maior retenção de clientes significa aumento de receita recorrente e redução de churn.
        """)

    st.markdown("---")
    st.markdown("### Indicadores Principais")

    total_customers = len(df)
    churned_customers = (df['Exited'] == 1).sum()
    retained_customers = (df['Exited'] == 0).sum()
    churn_rate = (churned_customers / total_customers) * 100
    avg_salary = df['EstimatedSalary'].mean()
    revenue_at_risk = df[df['Exited'] == 1]['EstimatedSalary'].sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total de Clientes", f"{total_customers:,}")

    with col2:
        st.metric("Clientes que Saíram", f"{churned_customers:,}", delta=f"{churn_rate:.1f}%")

    with col3:
        st.metric("Clientes Retidos", f"{retained_customers:,}", delta=f"{100 - churn_rate:.1f}%")

    with col4:
        st.metric("Salário Médio", f"R$ {avg_salary:,.0f}")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure(data=[
            go.Pie(
                labels=['Permaneceu', 'Saiu'],
                values=[retained_customers, churned_customers],
                marker=dict(colors=[COLOR_PRIMARY, COLOR_SECONDARY]),
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Clientes: %{value}<br>Percentual: %{percent}<extra></extra>'
            )
        ])
        fig.update_layout(
            title="Distribuição de Clientes",
            height=400,
            showlegend=True,
            template="plotly_white",
            font=dict(family="Arial, sans-serif", size=11)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.metric("Receita em Risco", f"R$ {revenue_at_risk / 1e6:.1f}M",
                  delta=f"{(revenue_at_risk / df['EstimatedSalary'].sum()) * 100:.1f}% da receita total")
        st.info("A receita em risco representa o salário estimado dos clientes que cancelaram.")

# ==================== PAGE: EXPLORATION ====================
elif page_key == "exploration":
    st.title("Exploração de Dados")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Registros", f"{len(df):,}")
    with col2:
        st.metric("Total de Variáveis", f"{df.shape[1]}")
    with col3:
        st.metric("Dados Ausentes", f"{df.isnull().sum().sum()}")
    with col4:
        st.metric("Duplicatas", "0")

    st.markdown("---")
    st.markdown("### Descrição das Variáveis")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **Identificação**
        - CustomerId: ID único
        - Surname: Sobrenome

        **Geográfico**
        - Geography: País

        **Demográfico**
        - Gender: Gênero
        - Age: Idade
        - AgeGroup: Faixa etária
        """)

    with col2:
        st.markdown("""
        **Financeiro**
        - CreditScore: Score de crédito
        - Balance: Saldo em conta
        - EstimatedSalary: Salário estimado

        **Comportamental**
        - Tenure: Tempo de relacionamento
        - NumOfProducts: Número de produtos
        - HasCrCard: Possui cartão de crédito
        - IsActiveMember: Membro ativo
        """)

    with col3:
        st.markdown("""
        **Alvo**
        - Exited: Status de churn
          - 0 = Permaneceu
          - 1 = Saiu

        **Resumo**
        - Total: 10.000 clientes
        - Sem valores ausentes
        - Pronto para análise
        """)

    st.markdown("---")
    st.markdown("### Distribuição do Churn")

    col1, col2 = st.columns(2)

    with col1:
        churn_dist = df['Exited'].value_counts()
        fig = go.Figure(data=[
            go.Bar(x=['Permaneceu', 'Saiu'],
                   y=[churn_dist[0], churn_dist[1]],
                   marker=dict(color=[COLOR_PRIMARY, COLOR_SECONDARY]))
        ])
        fig.update_layout(
            title="Contagem de Clientes por Status",
            xaxis_title="Status",
            yaxis_title="Número de Clientes",
            height=400,
            showlegend=False,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.success(f"Taxa de churn: {(churn_dist[1] / len(df) * 100):.1f}% - Aproximadamente 1 em 5 clientes cancelam")

    with col2:
        age_dist = df['Age'].describe()
        fig = go.Figure(data=[
            go.Histogram(x=df['Age'], nbinsx=30, marker=dict(color=COLOR_PRIMARY))
        ])
        fig.update_layout(
            title="Distribuição da Idade dos Clientes",
            xaxis_title="Idade",
            yaxis_title="Frequência",
            height=400,
            showlegend=False,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.info(f"Idade média: {age_dist['mean']:.1f} anos (variação: {age_dist['min']:.0f} a {age_dist['max']:.0f})")

    st.markdown("---")
    st.markdown("### Distribuição Geográfica")

    col1, col2 = st.columns(2)

    with col1:
        geo_churn = df.groupby('Geography')['Exited'].agg(['count', 'sum'])
        geo_churn['churn_rate'] = (geo_churn['sum'] / geo_churn['count'] * 100).round(1)

        fig = go.Figure(data=[
            go.Bar(x=geo_churn.index,
                   y=geo_churn['count'],
                   marker=dict(color=COLOR_PRIMARY))
        ])
        fig.update_layout(
            title="Clientes por País",
            xaxis_title="País",
            yaxis_title="Número de Clientes",
            height=400,
            showlegend=False,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure(data=[
            go.Bar(x=geo_churn.index,
                   y=geo_churn['churn_rate'],
                   marker=dict(color=COLOR_SECONDARY))
        ])
        fig.update_layout(
            title="Taxa de Churn por País",
            xaxis_title="País",
            yaxis_title="Taxa de Churn (%)",
            height=400,
            showlegend=False,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.warning(f"Alemanha apresenta maior taxa de churn: {geo_churn.loc['Germany', 'churn_rate']:.1f}%")

# ==================== PAGE: PROFILE ====================
elif page_key == "profile":
    st.title("Perfil do Cliente")

    st.markdown("### Filtros Interativos")

    col1, col2, col3 = st.columns(3)

    with col1:
        selected_geography = st.multiselect(
            "País",
            options=df['Geography'].unique(),
            default=df['Geography'].unique()
        )

    with col2:
        selected_gender = st.multiselect(
            "Gênero",
            options=df['Gender'].unique(),
            default=df['Gender'].unique()
        )

    with col3:
        selected_age_group = st.multiselect(
            "Faixa Etária",
            options=sorted(df['AgeGroup'].dropna().unique()),
            default=sorted(df['AgeGroup'].dropna().unique())
        )

    # Filtrar dados
    df_filtered = df[
        (df['Geography'].isin(selected_geography)) &
        (df['Gender'].isin(selected_gender)) &
        (df['AgeGroup'].isin(selected_age_group))
        ]

    st.markdown("---")
    st.markdown(f"### Perfil dos {len(df_filtered):,} Clientes Filtrados")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total", f"{len(df_filtered):,}")

    with col2:
        st.metric("Idade Média", f"{df_filtered['Age'].mean():.1f} anos")

    with col3:
        st.metric("Saldo Médio", f"R$ {df_filtered['Balance'].mean():,.0f}")

    with col4:
        st.metric("Tempo Médio", f"{df_filtered['Tenure'].mean():.1f} anos")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure(data=[
            go.Box(y=df_filtered['Age'], marker=dict(color=COLOR_PRIMARY))
        ])
        fig.update_layout(
            title="Distribuição de Idade",
            yaxis_title="Idade",
            height=400,
            showlegend=False,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        tenure_dist = df_filtered['Tenure'].value_counts().sort_index()
        fig = go.Figure(data=[
            go.Bar(x=tenure_dist.index, y=tenure_dist.values, marker=dict(color=COLOR_SECONDARY))
        ])
        fig.update_layout(
            title="Distribuição de Tempo de Relacionamento",
            xaxis_title="Tenure (Anos)",
            yaxis_title="Número de Clientes",
            height=400,
            showlegend=False,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        products_churn = df_filtered.groupby('NumOfProducts')['Exited'].agg(['count', 'sum'])
        products_churn['churn_rate'] = (products_churn['sum'] / products_churn['count'] * 100)

        fig = go.Figure(data=[
            go.Bar(x=products_churn.index,
                   y=products_churn['count'],
                   marker=dict(color=COLOR_PRIMARY))
        ])
        fig.update_layout(
            title="Clientes por Número de Produtos",
            xaxis_title="Número de Produtos",
            yaxis_title="Quantidade",
            height=400,
            showlegend=False,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        active_status = df_filtered['IsActiveMember'].map({0: 'Inativo', 1: 'Ativo'}).value_counts()
        fig = go.Figure(data=[
            go.Pie(labels=active_status.index, values=active_status.values,
                   marker=dict(colors=[COLOR_SECONDARY, COLOR_TERTIARY]))
        ])
        fig.update_layout(
            title="Status de Atividade",
            height=400,
            showlegend=True,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE: FACTORS ====================
elif page_key == "factors":
    st.title("Fatores Associados ao Churn")
    st.markdown("### Análise: O que os clientes que cancelaram têm em comum?")

    st.markdown("---")
    st.markdown("### Taxa de Churn por Gênero")

    col1, col2 = st.columns(2)

    with col1:
        gender_churn = df.groupby('Gender')['Exited'].agg(['count', 'sum'])
        gender_churn['churn_rate'] = (gender_churn['sum'] / gender_churn['count'] * 100)

        fig = go.Figure(data=[
            go.Bar(x=gender_churn.index,
                   y=gender_churn['churn_rate'],
                   marker=dict(color=[COLOR_SECONDARY, COLOR_PRIMARY]))
        ])
        fig.update_layout(
            title="Taxa de Churn por Gênero",
            xaxis_title="Gênero",
            yaxis_title="Taxa de Churn (%)",
            height=400,
            showlegend=False,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"""
        **Mulheres:** {gender_churn.loc['Female', 'churn_rate']:.1f}% de taxa de churn

        **Homens:** {gender_churn.loc['Male', 'churn_rate']:.1f}% de taxa de churn

        Mulheres apresentam taxa de churn **{gender_churn.loc['Female', 'churn_rate'] / gender_churn.loc['Male', 'churn_rate']:.1f}x maior** que homens.
        """)

    st.markdown("---")
    st.markdown("### Taxa de Churn por Faixa Etária")

    col1, col2 = st.columns(2)

    with col1:
        age_group_churn = df.groupby('AgeGroup')['Exited'].agg(['count', 'sum'])
        age_group_churn['churn_rate'] = (age_group_churn['sum'] / age_group_churn['count'] * 100)

        fig = go.Figure(data=[
            go.Bar(x=age_group_churn.index,
                   y=age_group_churn['churn_rate'],
                   marker=dict(color=COLOR_SECONDARY))
        ])
        fig.update_layout(
            title="Taxa de Churn por Faixa Etária",
            xaxis_title="Faixa Etária",
            yaxis_title="Taxa de Churn (%)",
            height=400,
            showlegend=False,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"""
        Clientes mais velhos apresentam maior risco:

        - **51-60 anos:** {age_group_churn.loc['51-60', 'churn_rate']:.1f}%
        - **61+ anos:** {age_group_churn.loc['61+', 'churn_rate']:.1f}%
        - **41-50 anos:** {age_group_churn.loc['41-50', 'churn_rate']:.1f}%

        Clientes acima de 51 anos têm **{age_group_churn.loc['61+', 'churn_rate'] / age_group_churn.loc['18-30', 'churn_rate']:.1f}x maior** taxa de churn.
        """)

    st.markdown("---")
    st.markdown("### Taxa de Churn por Número de Produtos")

    col1, col2 = st.columns(2)

    with col1:
        products_churn = df.groupby('NumOfProducts')['Exited'].agg(['count', 'sum'])
        products_churn['churn_rate'] = (products_churn['sum'] / products_churn['count'] * 100)

        fig = go.Figure(data=[
            go.Bar(x=products_churn.index,
                   y=products_churn['churn_rate'],
                   marker=dict(color=COLOR_TERTIARY))
        ])
        fig.update_layout(
            title="Taxa de Churn por Número de Produtos",
            xaxis_title="Número de Produtos",
            yaxis_title="Taxa de Churn (%)",
            height=400,
            showlegend=False,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"""
        - **1 Produto:** {products_churn.loc[1, 'churn_rate']:.1f}%
        - **2 Produtos:** {products_churn.loc[2, 'churn_rate']:.1f}%
        - **3+ Produtos:** {products_churn.loc[[3, 4], 'churn_rate'].mean():.1f}%

        Clientes com um único produto têm **{products_churn.loc[1, 'churn_rate'] / products_churn.loc[2, 'churn_rate']:.1f}x maior** taxa de churn.
        """)

    st.markdown("---")
    st.markdown("### Taxa de Churn por Status de Atividade")

    col1, col2 = st.columns(2)

    with col1:
        active_churn = df.groupby('IsActiveMember')['Exited'].agg(['count', 'sum'])
        active_churn['churn_rate'] = (active_churn['sum'] / active_churn['count'] * 100)
        active_churn.index = ['Inativo', 'Ativo']

        fig = go.Figure(data=[
            go.Bar(x=active_churn.index,
                   y=active_churn['churn_rate'],
                   marker=dict(color=[COLOR_SECONDARY, COLOR_TERTIARY]))
        ])
        fig.update_layout(
            title="Taxa de Churn por Atividade",
            xaxis_title="Status",
            yaxis_title="Taxa de Churn (%)",
            height=400,
            showlegend=False,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown(f"""
        - **Inativos:** {active_churn.loc['Inativo', 'churn_rate']:.1f}%
        - **Ativos:** {active_churn.loc['Ativo', 'churn_rate']:.1f}%

        Clientes inativos têm **{active_churn.loc['Inativo', 'churn_rate'] / active_churn.loc['Ativo', 'churn_rate']:.1f}x maior** taxa de churn.

        Falta de atividade é um sinal forte de risco.
        """)

    st.markdown("---")
    st.markdown("### Churn ao Longo do Tempo")

    tenure_churn = df.groupby('Tenure')['Exited'].agg(['count', 'sum'])
    tenure_churn['churn_rate'] = (tenure_churn['sum'] / tenure_churn['count'] * 100)

    fig = go.Figure(data=[
        go.Scatter(x=tenure_churn.index,
                   y=tenure_churn['churn_rate'],
                   mode='lines+markers',
                   line=dict(color=COLOR_PRIMARY, width=3),
                   marker=dict(size=8))
    ])
    fig.update_layout(
        title="Taxa de Churn ao Longo do Tempo",
        xaxis_title="Tenure (Anos)",
        yaxis_title="Taxa de Churn (%)",
        height=450,
        showlegend=False,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        - **Clientes novos (0-1 ano):** {tenure_churn.loc[[0, 1], 'churn_rate'].mean():.1f}%
        - **Clientes antigos (8-10 anos):** {tenure_churn.loc[[8, 9, 10], 'churn_rate'].mean():.1f}%

        Taxa de churn é maior nos primeiros anos.
        """)

    with col2:
        st.info(
            "Clientes novos requerem maior atenção. Um programa de onboarding robusto reduz significativamente o churn inicial.")

# ==================== PAGE: MODEL ====================
elif page_key == "model":
    st.title("Modelo Preditivo de Churn")

    st.markdown(
        "Após entender os padrões, treinamos modelos de Machine Learning capazes de estimar a probabilidade de cancelamento.")

    st.markdown("---")

    # Treinar modelos
    with st.spinner("Treinando modelos..."):
        results, feature_names = train_models(df)

    st.markdown("### Comparação de Modelos")

    metrics_data = []
    for model_name, result in results.items():
        metrics = calculate_metrics(result['y_test'], result['y_pred'], result['y_pred_proba'])
        metrics_data.append({
            'Modelo': model_name,
            'Acurácia': f"{metrics['accuracy']:.3f}",
            'Precisão': f"{metrics['precision']:.3f}",
            'Recall': f"{metrics['recall']:.3f}",
            'F1-Score': f"{metrics['f1']:.3f}",
            'AUC-ROC': f"{metrics['auc']:.3f}"
        })

    metrics_df = pd.DataFrame(metrics_data)
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### Curva ROC")

    fig = go.Figure()

    for model_name, result in results.items():
        fpr, tpr, _ = roc_curve(result['y_test'], result['y_pred_proba'])
        auc = roc_auc_score(result['y_test'], result['y_pred_proba'])

        fig.add_trace(go.Scatter(
            x=fpr, y=tpr,
            mode='lines',
            name=f"{model_name} (AUC={auc:.3f})",
            line=dict(width=2)
        ))

    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1],
        mode='lines',
        name='Baseline',
        line=dict(dash='dash', color='gray', width=1)
    ))

    fig.update_layout(
        title="Curva ROC - Comparação de Modelos",
        xaxis_title="Taxa de Falsos Positivos",
        yaxis_title="Taxa de Verdadeiros Positivos",
        height=500,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### Matriz de Confusão - Random Forest")

    rf_result = results['Random Forest']
    cm = confusion_matrix(rf_result['y_test'], rf_result['y_pred'])

    fig = go.Figure(data=go.Heatmap(
        z=cm,
        x=['Previsto: Não Churn', 'Previsto: Churn'],
        y=['Real: Não Churn', 'Real: Churn'],
        text=cm,
        texttemplate='%{text}',
        colorscale='Blues'
    ))

    fig.update_layout(
        title="Matriz de Confusão",
        height=400,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### Importância das Features")

    rf_model = results['Random Forest']['model']
    importances = rf_model.feature_importances_
    feature_importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importância': importances
    }).sort_values('Importância', ascending=True).tail(10)

    fig = go.Figure(data=[
        go.Bar(y=feature_importance_df['Feature'],
               x=feature_importance_df['Importância'],
               orientation='h',
               marker=dict(color=COLOR_PRIMARY))
    ])
    fig.update_layout(
        title="Top 10 Features Mais Importantes",
        xaxis_title="Importância",
        yaxis_title="Feature",
        height=400,
        showlegend=False,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### Explicação das Métricas")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Acurácia**
        Porcentagem de previsões corretas.

        **Precisão**
        Entre os clientes previstos como "churn", quantos realmente cancelam?
        """)

    with col2:
        st.markdown("""
        **Recall**
        Entre os clientes que realmente cancelam, quantos conseguimos identificar?

        **AUC-ROC**
        Capacidade geral de distinguir clientes que vão cancelar.
        """)

# ==================== PAGE: HIGH RISK ====================
elif page_key == "high_risk":
    st.title("Clientes em Risco")

    st.markdown("### Identificação: Quais clientes devemos abordar primeiro?")

    # Usar melhor modelo
    results, _ = train_models(df)
    best_model_name = 'Random Forest'
    best_result = results[best_model_name]

    # Adicionar probabilidades ao dataframe original
    df_copy = df.copy()

    # Preparar dados para previsão
    X = df_copy.drop(columns=['CustomerId', 'Surname', 'Exited', 'AgeGroup'])
    for col in ['Geography', 'Gender']:
        le = best_result['le_dict'][col]
        X[col] = le.transform(X[col])

    # Fazer previsões
    y_pred_proba = best_result['model'].predict_proba(X)[:, 1]
    df_copy['Probabilidade_Churn'] = y_pred_proba


    # Classificar risco
    def classify_risk(prob):
        if prob < 0.33:
            return 'Baixo'
        elif prob < 0.67:
            return 'Médio'
        else:
            return 'Alto'


    df_copy['Classificacao_Risco'] = df_copy['Probabilidade_Churn'].apply(classify_risk)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    risk_counts = df_copy['Classificacao_Risco'].value_counts()

    with col1:
        low_risk = risk_counts.get('Baixo', 0)
        st.metric("Baixo Risco", f"{low_risk:,}", delta=f"{low_risk / len(df_copy) * 100:.1f}%")

    with col2:
        med_risk = risk_counts.get('Médio', 0)
        st.metric("Médio Risco", f"{med_risk:,}", delta=f"{med_risk / len(df_copy) * 100:.1f}%")

    with col3:
        high_risk = risk_counts.get('Alto', 0)
        st.metric("Alto Risco", f"{high_risk:,}", delta=f"{high_risk / len(df_copy) * 100:.1f}%")

    st.markdown("---")
    st.markdown("### Top Clientes em Maior Risco")

    top_n = st.selectbox("Mostrar top", [10, 20, 50, 100], index=0)

    top_risk = df_copy.nlargest(top_n, 'Probabilidade_Churn')[
        ['CustomerId', 'Gender', 'Age', 'Geography', 'Tenure', 'Balance',
         'NumOfProducts', 'IsActiveMember', 'Probabilidade_Churn', 'Classificacao_Risco']
    ].copy()

    top_risk['Probabilidade_Churn'] = (top_risk['Probabilidade_Churn'] * 100).round(1).astype(str) + '%'
    top_risk['Age'] = top_risk['Age'].astype(int)
    top_risk['Tenure'] = top_risk['Tenure'].astype(int)
    top_risk['Balance'] = top_risk['Balance'].apply(lambda x: f"R$ {x:,.0f}")
    top_risk['IsActiveMember'] = top_risk['IsActiveMember'].map({0: 'Não', 1: 'Sim'})
    top_risk = top_risk.rename(columns={
        'Probabilidade_Churn': 'Prob. Churn',
        'Classificacao_Risco': 'Risco'
    })

    st.dataframe(top_risk, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### Distribuição de Risco")

    fig = go.Figure(data=[
        go.Pie(labels=['Baixo', 'Médio', 'Alto'],
               values=[risk_counts.get('Baixo', 0),
                       risk_counts.get('Médio', 0),
                       risk_counts.get('Alto', 0)],
               marker=dict(colors=[COLOR_TERTIARY, '#FFC107', COLOR_SECONDARY]))
    ])
    fig.update_layout(
        title="Distribuição de Clientes por Classificação de Risco",
        height=400,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE: IMPACT ====================
elif page_key == "impact":
    st.title("Impacto Financeiro")

    st.markdown("### Quantificação: Quanto dinheiro pode estar em risco?")

    # Preparar dados
    results, _ = train_models(df)
    best_model_name = 'Random Forest'
    best_result = results[best_model_name]

    df_copy = df.copy()
    X = df_copy.drop(columns=['CustomerId', 'Surname', 'Exited', 'AgeGroup'])
    for col in ['Geography', 'Gender']:
        le = best_result['le_dict'][col]
        X[col] = le.transform(X[col])

    y_pred_proba = best_result['model'].predict_proba(X)[:, 1]
    df_copy['Probabilidade_Churn'] = y_pred_proba


    def classify_risk(prob):
        if prob < 0.33:
            return 'baixo'
        elif prob < 0.67:
            return 'medio'
        else:
            return 'alto'


    df_copy['Risco'] = df_copy['Probabilidade_Churn'].apply(classify_risk)

    st.markdown("---")

    # Calcular métricas
    alto_risco = df_copy[df_copy['Risco'] == 'alto']
    receita_em_risco = alto_risco['EstimatedSalary'].sum()
    clientes_alto_risco = len(alto_risco)
    pct_base = (clientes_alto_risco / len(df_copy)) * 100

    st.markdown("### Análise de Receita em Risco")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Clientes em Alto Risco", f"{clientes_alto_risco:,}")

    with col2:
        st.metric("Percentual da Base", f"{pct_base:.1f}%")

    with col3:
        st.metric("Receita em Risco", f"R$ {receita_em_risco / 1e6:.1f}M")

    with col4:
        st.metric("Média por Cliente", f"R$ {alto_risco['EstimatedSalary'].mean():,.0f}")

    st.markdown("---")
    st.markdown("### Cenário de Retenção")

    col1, col2 = st.columns([1, 2])

    with col1:
        retention_rate = st.slider(
            "Taxa de Retenção Estimada (%)",
            min_value=0,
            max_value=100,
            value=25,
            step=5,
            label_visibility="collapsed"
        )

    with col2:
        valor_recuperado = receita_em_risco * (retention_rate / 100)
        clientes_recuperados = int(clientes_alto_risco * (retention_rate / 100))

        st.metric(
            f"Valor Preservado ({retention_rate}%)",
            f"R$ {valor_recuperado / 1e6:.2f}M",
            delta=f"{clientes_recuperados} clientes"
        )

    st.markdown("---")
    st.markdown("### Impacto por Taxa de Retenção")

    retention_scenarios = []
    for rate in range(0, 101, 10):
        retention_scenarios.append({
            'Taxa': f"{rate}%",
            'Clientes': int(clientes_alto_risco * (rate / 100)),
            'Receita (R$ M)': receita_em_risco * (rate / 100) / 1e6
        })

    scenario_df = pd.DataFrame(retention_scenarios)

    fig = go.Figure(data=[
        go.Bar(x=scenario_df['Taxa'],
               y=scenario_df['Receita (R$ M)'],
               marker=dict(color=COLOR_PRIMARY))
    ])
    fig.update_layout(
        title="Receita Preservada por Taxa de Retenção",
        xaxis_title="Taxa de Retenção",
        yaxis_title="Receita (R$ Milhões)",
        height=400,
        showlegend=False,
        template="plotly_white"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### Segmentação por Características")

    col1, col2 = st.columns(2)

    with col1:
        gender_risk = alto_risco.groupby('Gender')['EstimatedSalary'].sum()
        fig = go.Figure(data=[
            go.Bar(x=gender_risk.index, y=gender_risk.values / 1e6,
                   marker=dict(color=[COLOR_SECONDARY, COLOR_PRIMARY]))
        ])
        fig.update_layout(
            title="Receita em Risco por Gênero",
            xaxis_title="Gênero",
            yaxis_title="Receita (R$ M)",
            height=400,
            showlegend=False,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        geo_risk = alto_risco.groupby('Geography')['EstimatedSalary'].sum()
        fig = go.Figure(data=[
            go.Bar(x=geo_risk.index, y=geo_risk.values / 1e6,
                   marker=dict(color=[COLOR_PRIMARY, COLOR_SECONDARY, COLOR_TERTIARY]))
        ])
        fig.update_layout(
            title="Receita em Risco por País",
            xaxis_title="País",
            yaxis_title="Receita (R$ M)",
            height=400,
            showlegend=False,
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)

# ==================== PAGE: RECOMMENDATIONS ====================
elif page_key == "recommendations":
    st.title("Recomendações de Negócio")

    st.markdown("### O que a empresa deveria fazer com base nos dados?")

    st.markdown("---")
    st.markdown("### 1. Priorizar Clientes em Alto Risco")

    st.markdown("""
    **Ação:** Direcionar campanhas de retenção para clientes com probabilidade de churn > 67%.

    **Por quê:** Nosso modelo identifica clientes em alto risco, representando receita significativa em risco.

    **Como:** Listar clientes automaticamente, priorizar contato por likelihood de churn, preparar ofertas personalizadas.
    """)

    st.markdown("---")
    st.markdown("### 2. Estratégias Segmentadas de Retenção")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **Mulheres**

        - Atendimento personalizado
        - Investigar satisfação
        - Propostas customizadas
        - Acompanhamento contínuo
        """)

    with col2:
        st.markdown("""
        **Clientes 51+**

        - Simplificar produtos
        - Suporte premium
        - Atendimento dedicado
        - Benefícios específicos
        """)

    with col3:
        st.markdown("""
        **Clientes 1 Produto**

        - Cross-sell de produtos
        - Bundles com desconto
        - Demonstrar valor
        - Educação contínua
        """)

    st.markdown("---")
    st.markdown("### 3. Programa de Ativação")

    st.markdown("""
    Clientes inativos têm 26% taxa de churn vs 7% dos ativos.

    **Ação:** Detectar inatividade cedo, criar campanhas de re-engajamento, oferecer benefícios por atividade.
    """)

    st.markdown("---")
    st.markdown("### 4. Programa de Onboarding")

    st.markdown("""
    Clientes no primeiro ano têm maior taxa de churn.

    **Ação:** Melhorar experiência de onboarding, contato pessoal, treinamento, check-ins semanais.
    """)

    st.markdown("---")
    st.markdown("### 5. Monitoramento Contínuo")

    st.markdown("""
    - Atualizar modelo mensalmente
    - Rastrear precisão das previsões
    - Medir ROI das campanhas
    - A/B testar estratégias
    - Refinar segmentação
    """)

    st.markdown("---")
    st.markdown("### Métricas de Sucesso")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Curto Prazo (1-3 meses)**
        - % de clientes em alto risco contatados
        - Taxa de resposta às campanhas
        - Conversão de ofertas
        """)

    with col2:
        st.markdown("""
        **Longo Prazo (6-12 meses)**
        - Redução geral de churn
        - Aumento de lifetime value
        - ROI das campanhas
        - Satisfação do cliente
        """)

# ==================== PAGE: TECH ====================
elif page_key == "tech":
    st.title("Tecnologias")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### Bibliotecas Python

        **Pandas** - Manipulação e análise de dados

        **NumPy** - Operações numéricas

        **Scikit-learn** - Machine Learning

        **Plotly** - Visualizações interativas
        """)

    with col2:
        st.markdown("""
        ### Framework Web

        **Streamlit** - Aplicação web em Python

        ### Modelos Utilizados

        **Logistic Regression** - Baseline rápido

        **Random Forest** - Melhor performance
        """)

    st.markdown("---")
    st.markdown("### Pipeline de ML")

    st.markdown("""
    1. Preparação dos dados
    2. Codificação de categorias
    3. Separação treino/teste
    4. Normalização de features
    5. Treinamento de modelos
    6. Avaliação com métricas
    7. Predição em novos dados
    """)

    st.markdown("---")
    st.markdown("### Instruções de Execução")

    st.code("""
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar aplicação
streamlit run app.py

# 3. Acessar no navegador
# http://localhost:8501
    """, language="bash")

    st.markdown("---")
    st.markdown("### Estrutura de Arquivos")

    st.code("""
projeto-churn/
├── app.py
├── Churn_Modelling.csv
├── requirements.txt
└── README.md
    """, language="text")

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px 0;'>
    <p style='color: #888; font-size: 0.9em;'>Customer Churn Prediction | Análise de Clientes em Risco</p>
    <p style='color: #999; font-size: 0.8em;'>Desenvolvido com Python, Streamlit e Scikit-learn</p>
</div>
""", unsafe_allow_html=True)