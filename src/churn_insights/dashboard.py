from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .model import analyze_data, load_data
from .prioritization import PRIORITY_ORDER, assign_priority
from .presentation import render_header, render_ml_method
from .comparison_view import render_comparison
from .calibration_view import render_calibration
from .import_view import render_import
from .help_text import COUNTRY_HELP, GENDER_HELP, PRIORITY_HELP, CAPACITY_HELP, MINIMUM_RISK_HELP, SCOPE_HELP, SEARCH_HELP

ROOT = Path(__file__).resolve().parents[2]
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
    st.session_state["priority_capacity"] = None
    st.session_state["priority_scope"] = None
    st.session_state["minimum_risk"] = None


def chart_layout(fig, height=300):
    fig.update_layout(height=height, margin=dict(l=12, r=12, t=20, b=12),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Arial, sans-serif", color="#555B54", size=12),
                      legend=dict(orientation="h", y=-0.15, x=0),
                      hoverlabel=dict(bgcolor="#171817", font_color="white"))
    return fig



def main():
    st.set_page_config(page_title="Churn Analisys | Retenção", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")
    st.html(ROOT / "assets" / "css" / "styles.css")
    try:
        with st.spinner("Preparando a análise da carteira…"):
            data, metrics = analyze_data(load_data())
    except (OSError, ValueError, KeyError) as error:
        st.error(f"Não foi possível carregar a base local: {error}")
        st.stop()

    render_header()

    st.html('<div class="section-heading"><h2 id="carteira">Visão da carteira</h2><span>01 / OVERVIEW</span></div>')
    with st.container(border=True):
        columns = st.columns([1.2, 1.2, 1.2, 0.8], vertical_alignment="bottom")
        country = columns[0].selectbox("País", ["Todos"] + sorted(data.Geography.unique()), format_func=lambda x: COUNTRIES.get(x, x), key="country", help=COUNTRY_HELP)
        gender = columns[1].selectbox("Gênero", ["Todos"] + sorted(data.Gender.unique()), format_func=lambda x: GENDERS.get(x, x), key="gender", help=GENDER_HELP)
        risk = columns[2].selectbox("Prioridade", ["Todos"] + PRIORITY_ORDER, key="risk", help=PRIORITY_HELP)
        columns[3].button("Limpar filtros ↺", on_click=reset_filters, width="stretch")

        capacity_col, risk_col, scope_col = st.columns(3)
        priority_capacity = capacity_col.number_input(
            "Capacidade de atendimento da carteira (clientes)", help=CAPACITY_HELP, min_value=1, value=None, step=1,
            placeholder="Informe quantos clientes pode atender", key="priority_capacity",
        )
        minimum_risk_percent = risk_col.number_input(
            "Risco mínimo para prioridade (%)", min_value=0.0, max_value=100.0, value=None, step=1.0,
            placeholder="Defina o percentual mínimo", key="minimum_risk",
            help=MINIMUM_RISK_HELP,
        )
        priority_scope = scope_col.selectbox(
            "Público da prioridade", ["Clientes sem cancelamento", "Todos · demonstração histórica"],
            index=None, placeholder="Escolha o público", key="priority_scope", help=SCOPE_HELP,
        )

    include_exited = None if priority_scope is None else priority_scope == "Todos · demonstração histórica"
    minimum_risk = None if minimum_risk_percent is None else minimum_risk_percent / 100
    planned = priority_capacity is not None and include_exited is not None and minimum_risk is not None
    portfolio = assign_priority(data, priority_capacity, include_exited=include_exited, minimum_risk=minimum_risk)
    if planned:
        eligible_count = int(portfolio.priority.isin(["Prioritário", "Fora da capacidade"]).sum())
        selected = portfolio[portfolio.priority == "Prioritário"]
        st.caption(f"{number(len(selected))} prioritários entre {number(eligible_count)} elegíveis com risco ≥ {percent(minimum_risk_percent)} na carteira completa. País, gênero e busca apenas filtram a exibição; não recalculam a prioridade. Empates de risco são resolvidos pelo ID.")
        if priority_capacity > eligible_count:
            st.info(f"{number(priority_capacity - len(selected))} vagas não utilizadas: somente {number(eligible_count)} clientes do público atingem o risco mínimo. A lista não é completada com clientes abaixo do limite.")
        if not selected.empty:
            boundary = selected.churn_probability.min() * 100
            st.caption(f"Menor risco estimado na seleção: {percent(boundary)}. A seleção respeita o risco mínimo e a capacidade; probabilidades iguais no limite podem ficar fora por desempate.")
    else:
        st.info("Informe a capacidade, o risco mínimo e o público para definir a prioridade. O risco estimado continua disponível para todos os clientes.")
    segment = portfolio
    for column, value in [("Geography", country), ("Gender", gender)]:
        if value != "Todos":
            segment = segment[segment[column] == value]
    filtered = segment if risk == "Todos" else segment[segment.priority == risk]

    if planned:
        segment_eligible = int(segment.priority.isin(["Prioritário", "Fora da capacidade"]).sum())
        segment_priority = int((segment.priority == "Prioritário").sum())
        segment_outside = int((segment.priority == "Fora da capacidade").sum())
        st.caption(f"No recorte de país e gênero: {number(segment_priority)} selecionados para atendimento · {number(segment_outside)} elegíveis fora da capacidade · {number(segment_eligible)} elegíveis no total · {number(int((segment.priority == 'Abaixo do risco mínimo').sum()))} abaixo do risco mínimo.")
        if risk == "Prioritário":
            st.info("O filtro Prioridade está em ‘Prioritário’: somente os clientes selecionados são exibidos. Escolha ‘Todos’ para visualizar também os demais status.")

    total = len(filtered)
    prioritized = filtered[filtered.priority == "Prioritário"]
    churn_rate = filtered.Exited.mean() * 100 if total else 0
    balance = prioritized.Balance.sum()
    active_filters = sum(value != "Todos" for value in (country, gender, risk))
    st.caption(f"{number(total)} de {number(len(data))} clientes · {active_filters} filtro(s) aplicado(s)")

    cards = [
        ("01", "Clientes analisados", number(total), "Clientes no recorte selecionado", ""),
        ("02", "Churn observado", percent(churn_rate), "Cancelamentos registrados na base", ""),
        ("03", "Clientes prioritários", number(len(prioritized)) if planned else "—", "Risco mínimo atendido · dentro da capacidade", "accent"),
        ("04", "Saldo dos prioritários", f"{balance / 1e6:.2f} mi".replace(".", ",") if planned else "—", "Soma de saldos · moeda não informada", ""),
    ]
    for column, (index, label, value, caption, style) in zip(st.columns(4), cards):
        column.markdown(f'<article class="metric-card {style}"><div class="metric-top"><span>{label}</span><span class="metric-index">{index}</span></div><div class="metric-value">{value}</div><div class="metric-caption">{caption}</div></article>', unsafe_allow_html=True)

    st.html('<div class="section-heading"><h2 id="graficos">Insights da carteira: padrões de churn</h2><span>02 / ANÁLISE</span></div>')
    if not total:
        st.info("Nenhum cliente neste recorte. Limpe ou ajuste os filtros para continuar a análise.")
    else:
        left, right = st.columns([1, 1.4])
        with left, st.container(border=True):
            st.subheader("Distribuição do risco estimado")
            st.caption("Machine Learning aplicado: como as probabilidades de churn se distribuem no recorte selecionado.")
            fig = go.Figure(go.Histogram(
                x=filtered.churn_probability * 100, xbins=dict(start=0, end=100, size=10),
                marker_color="#FFD700", hovertemplate="Risco: %{x}%<br>%{y} clientes<extra></extra>",
            ))
            chart_layout(fig)
            fig.update_layout(xaxis=dict(title="Probabilidade de churn (%)", range=[0, 100]),
                              yaxis=dict(title="Clientes", gridcolor="#ECEEE8"), bargap=0.08)
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        with right, st.container(border=True):
            st.subheader("Risco e histórico por país")
            st.caption("Análise exploratória: compare a probabilidade média estimada pelo modelo com o churn registrado em cada país.")
            grouped = filtered.groupby("Geography").agg(risk=("churn_probability", "mean"), churn=("Exited", "mean"), clients=("CustomerId", "size"))
            labels = [COUNTRIES.get(country, country) for country in grouped.index]
            fig = go.Figure()
            for label, column, color in [("Risco estimado", "risk", "#FFD700"), ("Churn observado", "churn", "#242824")]:
                fig.add_bar(name=label, x=labels, y=grouped[column] * 100, marker_color=color,
                            customdata=grouped.clients, hovertemplate="%{x}<br>%{y:.1f}%<br>%{customdata} clientes<extra>%{fullData.name}</extra>")
            chart_layout(fig)
            fig.update_layout(barmode="group", bargap=0.3, yaxis=dict(title="Percentual (%)", gridcolor="#ECEEE8"))
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    if total:
        with st.container(border=True):
            st.subheader("Insights para orientar a investigação")
            st.caption("Leituras calculadas a partir do recorte atual. Os filtros atualizam os resultados; associações históricas não demonstram causalidade.")
            observed = int(filtered.Exited.sum())
            st.write(f"**Churn no recorte.** {number(observed)} de {number(total)} clientes têm cancelamento registrado ({percent(churn_rate)}). A probabilidade média estimada pelo modelo é {percent(filtered.churn_probability.mean() * 100)}. Esses indicadores descrevem medidas diferentes: resultado observado e estimativa de risco.")
            country_summary = filtered.groupby("Geography").agg(clients=("Exited", "size"), rate=("Exited", "mean"))
            if len(country_summary) > 1:
                leaders = country_summary[country_summary.rate == country_summary.rate.max()]
                names = ", ".join(COUNTRIES.get(name, name) for name in leaders.index)
                st.write(f"**Leitura por país.** {names}: maior taxa histórica de churn neste recorte, com {percent(leaders.rate.iloc[0] * 100)}. Compare também o tamanho dos grupos no gráfico; uma taxa maior não explica, sozinha, o motivo do cancelamento.")
            activity = filtered.groupby("IsActiveMember").agg(clients=("Exited", "size"), rate=("Exited", "mean"))
            if 0 in activity.index and 1 in activity.index:
                st.write(f"**Atividade e relacionamento.** Entre {number(activity.loc[0, 'clients'])} clientes inativos, o churn observado é {percent(activity.loc[0, 'rate'] * 100)}; entre {number(activity.loc[1, 'clients'])} ativos, é {percent(activity.loc[1, 'rate'] * 100)}. Use essa diferença para formular hipóteses de investigação sobre o relacionamento.")
            st.caption("A carteira inclui registros de treino. Consulte as métricas do teste separado para avaliar o desempenho do modelo.")

    with st.container(border=True):
        info, accuracy, auc = st.columns([2.5, 1, 1])
        info.markdown('<div class="eyebrow model-label">CIÊNCIA DE DADOS EM AÇÃO</div><h3>Do histórico à probabilidade de churn.</h3>', unsafe_allow_html=True)
        info.caption(f"scikit-learn · Random Forest calibrado · {metrics['features']} variáveis · {number(metrics['test_count'])} clientes na avaliação separada.")
        accuracy.metric("Acurácia no teste · corte de 50%", percent(metrics["accuracy"] * 100))
        auc.metric("ROC AUC no teste", f"{metrics['auc']:.3f}".replace(".", ","))
        with st.expander("Como interpretar esta análise"):
            st.write("O risco é uma probabilidade calibrada. A prioridade exige atingir o risco mínimo informado, pertencer ao público escolhido e estar entre os maiores riscos até a capacidade. O corte de 50% é usado apenas na métrica de acurácia, não na lista de atendimento.")
            st.write("O modelo é treinado em 80% da base; as métricas são calculadas nos 20% separados para teste. A visualização pontua toda a base, incluindo registros de treino, e serve como demonstração, não como validação prospectiva.")
            st.write("Saldo dos prioritários soma Balance dos clientes selecionados. A base não informa moeda; esse saldo não é receita nem valor que uma campanha recuperaria.")

    render_ml_method(metrics)
    render_calibration(metrics)
    render_comparison(metrics["evaluation"], complete_with_active=True)
    render_import()

    st.html('<div class="section-heading"><h2 id="dados">Clientes em foco</h2><span>06 / EXPLORAR</span></div>')
    with st.container(border=True):
        search_col, export_col = st.columns([3, 1], vertical_alignment="bottom")
        search = search_col.text_input("Buscar cliente", placeholder="Digite um sobrenome ou ID…", key="search", help=SEARCH_HELP)
        clients = filtered.sort_values(["churn_probability", "CustomerId"], ascending=[False, True])
        if search.strip():
            query = search.strip()
            clients = clients[clients.Surname.str.contains(query, case=False, regex=False) | clients.CustomerId.astype(str).str.contains(query, regex=False)]
        table = clients[["CustomerId", "Surname", "Geography", "Age", "Balance", "churn_probability", "priority", "Exited"]].copy()
        table["Geography"] = table.Geography.map(COUNTRIES)
        table["churn_probability"] *= 100
        table["Exited"] = table.Exited.map({0: "Não", 1: "Sim"})
        table.columns = ["ID", "Sobrenome", "País", "Idade", "Saldo", "Risco (%)", "Prioridade", "Cancelamento histórico"]
        export_col.download_button("Exportar seleção ↓", table.to_csv(index=False).encode("utf-8-sig"), "clientes_filtrados.csv", "text/csv", width="stretch", disabled=table.empty)
        if table.empty:
            st.info("Nenhum cliente encontrado para esta busca.")
        else:
            st.dataframe(table, hide_index=True, width="stretch", height=350, column_config={"Risco (%)": st.column_config.ProgressColumn("Risco (%)", min_value=0, max_value=100, format="%.1f%%"), "Saldo": st.column_config.NumberColumn(format="%.2f"), "ID": st.column_config.NumberColumn(format="%d")})
        st.caption(f"{number(len(table))} clientes · ordenados do maior para o menor risco estimado")
        if planned and not clients.empty:
            listed_priority = int((clients.priority == "Prioritário").sum())
            st.caption(f"Nesta tabela: {number(listed_priority)} prioritários e {number(len(clients) - listed_priority)} com outros status. A ordenação pode concentrar prioritários nas primeiras linhas; role a tabela para consultar o restante.")

    st.markdown('<footer><span><strong>CHURN ANALISYS</strong> / Inteligência de retenção</span><span>Ciência de Dados · Machine Learning aplicado</span></footer>', unsafe_allow_html=True)
