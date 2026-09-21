from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .model import RISK_ORDER, analyze_data, load_data
from .presentation import render_header

ROOT = Path(__file__).resolve().parents[2]
COLORS = {"Baixo": "#242824", "Médio": "#FFD700", "Alto": "#EE7564"}
COUNTRIES = {"France": "França", "Germany": "Alemanha", "Spain": "Espanha", "Todos": "Todos os países"}
GENDERS = {"Female": "Feminino", "Male": "Masculino", "Todos": "Todos os gêneros"}


def number(value):
    return f"{value:,.0f}".replace(",", ".")


def percent(value):
    return f"{value:.1f}%".replace(".", ",")


def reset_filters():
    for key in ("country", "gender", "risk"):
        st.session_state[key] = "Todos"
    st.session_state["search"] = ""


def chart_layout(fig, height=300):
    fig.update_layout(height=height, margin=dict(l=12, r=12, t=20, b=12),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Arial, sans-serif", color="#555B54", size=12),
                      legend=dict(orientation="h", y=-0.15, x=0),
                      hoverlabel=dict(bgcolor="#171817", font_color="white"))
    return fig



def main():
    st.set_page_config(page_title="Previsão de Churn | Retenção", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")
    st.html(ROOT / "assets" / "css" / "styles.css")
    try:
        with st.spinner("Preparando a análise da carteira…"):
            data, metrics = analyze_data(load_data())
    except (FileNotFoundError, ValueError, KeyError) as error:
        st.error(f"Não foi possível carregar a base local: {error}")
        st.stop()

    render_header()

    st.html('<div class="section-heading"><h2 id="carteira">Visão da carteira</h2><span>01 / OVERVIEW</span></div>')
    with st.container(border=True):
        columns = st.columns([1.2, 1.2, 1.2, 0.8], vertical_alignment="bottom")
        country = columns[0].selectbox("País", ["Todos"] + sorted(data.Geography.unique()), format_func=lambda x: COUNTRIES.get(x, x), key="country")
        gender = columns[1].selectbox("Gênero", ["Todos"] + sorted(data.Gender.unique()), format_func=lambda x: GENDERS.get(x, x), key="gender")
        risk = columns[2].selectbox("Nível de risco", ["Todos"] + RISK_ORDER, key="risk")
        columns[3].button("Limpar filtros ↺", on_click=reset_filters, width="stretch")

    filtered = data.copy()
    for column, value in [("Geography", country), ("Gender", gender), ("risk_level", risk)]:
        if value != "Todos":
            filtered = filtered[filtered[column] == value]

    total = len(filtered)
    high_risk = filtered[filtered.risk_level == "Alto"]
    churn_rate = filtered.Exited.mean() * 100 if total else 0
    balance = high_risk.Balance.sum()
    active_filters = sum(value != "Todos" for value in (country, gender, risk))
    st.caption(f"{number(total)} de {number(len(data))} clientes · {active_filters} filtro(s) aplicado(s)")

    cards = [
        ("01", "Clientes analisados", number(total), "Clientes no recorte selecionado", ""),
        ("02", "Churn observado", percent(churn_rate), "Cancelamentos registrados na base", ""),
        ("03", "Alto risco estimado", number(len(high_risk)), "Probabilidade igual ou superior a 67%", "accent"),
        ("04", "Saldo em alto risco", f"{balance / 1e6:.2f} mi".replace(".", ","), "Soma de saldos · moeda não informada", ""),
    ]
    for column, (index, label, value, caption, style) in zip(st.columns(4), cards):
        column.markdown(f'<article class="metric-card {style}"><div class="metric-top"><span>{label}</span><span class="metric-index">{index}</span></div><div class="metric-value">{value}</div><div class="metric-caption">{caption}</div></article>', unsafe_allow_html=True)

    st.html('<div class="section-heading"><h2 id="graficos">O que os dados revelam</h2><span>02 / ANÁLISE</span></div>')
    if not total:
        st.info("Nenhum cliente neste recorte. Limpe ou ajuste os filtros para continuar a análise.")
    else:
        left, right = st.columns([1, 1.4])
        with left, st.container(border=True):
            st.subheader("Distribuição de risco")
            st.caption("Como os clientes se distribuem na carteira selecionada")
            counts = filtered.risk_level.value_counts().reindex(RISK_ORDER, fill_value=0)
            fig = go.Figure(go.Pie(labels=RISK_ORDER, values=counts, hole=0.76, sort=False,
                                  marker=dict(colors=list(COLORS.values()), line=dict(color="white", width=5)),
                                  textinfo="none", hovertemplate="%{label}: %{value} clientes (%{percent})<extra></extra>"))
            fig.update_layout(annotations=[dict(text=f"<b>{number(total)}</b><br>clientes", x=0.5, y=0.5, showarrow=False, font_size=23)])
            st.plotly_chart(chart_layout(fig), width="stretch", config={"displayModeBar": False})
        with right, st.container(border=True):
            st.subheader("Risco por país")
            st.caption("Volume de clientes por geografia · dados do recorte atual")
            grouped = pd.crosstab(filtered.Geography, filtered.risk_level).reindex(columns=RISK_ORDER, fill_value=0)
            fig = go.Figure()
            for level in RISK_ORDER:
                fig.add_bar(name=level, x=[COUNTRIES.get(x, x) for x in grouped.index], y=grouped[level], marker_color=COLORS[level], hovertemplate="%{x}<br>%{y} clientes<extra>%{fullData.name}</extra>")
            chart_layout(fig)
            fig.update_layout(barmode="stack", bargap=0.55, yaxis=dict(gridcolor="#ECEEE8", zeroline=False, title="Clientes"), xaxis=dict(showgrid=False))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with st.container(border=True):
        info, accuracy, auc = st.columns([2.5, 1, 1])
        info.markdown('<div class="eyebrow model-label">POR TRÁS DOS INSIGHTS</div><h3>Um modelo. Mais contexto.</h3>', unsafe_allow_html=True)
        info.caption(f"Random Forest · {metrics['features']} variáveis · {number(metrics['test_count'])} clientes na avaliação separada.")
        accuracy.metric("Acurácia no teste", percent(metrics["accuracy"] * 100))
        auc.metric("ROC AUC no teste", f"{metrics['auc']:.3f}".replace(".", ","))
        with st.expander("Como interpretar esta análise"):
            st.write("Risco baixo: menos de 33%. Médio: de 33% a menos de 67%. Alto: a partir de 67%. O churn observado vem do histórico; o risco é uma estimativa do modelo.")
            st.write("O modelo é treinado em 80% da base; as métricas são calculadas nos 20% separados para teste. A visualização pontua toda a base, incluindo registros de treino, e serve como demonstração, não como validação prospectiva.")
            st.write("Saldo em alto risco soma Balance dos clientes classificados como alto risco. A base não informa moeda; salário estimado não é receita da instituição.")

    st.html('<div class="section-heading"><h2 id="dados">Clientes em foco</h2><span>03 / EXPLORAR</span></div>')
    with st.container(border=True):
        search_col, export_col = st.columns([3, 1], vertical_alignment="bottom")
        search = search_col.text_input("Buscar cliente", placeholder="Digite um sobrenome ou ID…", key="search")
        clients = filtered.sort_values("churn_probability", ascending=False)
        if search.strip():
            query = search.strip()
            clients = clients[clients.Surname.str.contains(query, case=False, regex=False) | clients.CustomerId.astype(str).str.contains(query, regex=False)]
        table = clients[["CustomerId", "Surname", "Geography", "Age", "Balance", "churn_probability", "risk_level"]].copy()
        table["Geography"] = table.Geography.map(COUNTRIES)
        table["churn_probability"] *= 100
        table.columns = ["ID", "Sobrenome", "País", "Idade", "Saldo", "Risco (%)", "Nível"]
        export_col.download_button("Exportar seleção ↓", table.to_csv(index=False).encode("utf-8-sig"), "clientes_filtrados.csv", "text/csv", width="stretch", disabled=table.empty)
        if table.empty:
            st.info("Nenhum cliente encontrado para esta busca.")
        else:
            st.dataframe(table, hide_index=True, width="stretch", height=350, column_config={"Risco (%)": st.column_config.ProgressColumn("Risco (%)", min_value=0, max_value=100, format="%.1f%%"), "Saldo": st.column_config.NumberColumn(format="%.2f"), "ID": st.column_config.NumberColumn(format="%d")})
        st.caption(f"{number(len(table))} clientes · ordenados do maior para o menor risco estimado")

    st.markdown('<footer><span><strong>PREVISÃO DE CHURN</strong> / Inteligência de retenção</span><span>Projeto demonstrativo · Python + Streamlit</span></footer>', unsafe_allow_html=True)
