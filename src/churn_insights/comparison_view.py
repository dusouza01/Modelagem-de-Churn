"""Presentation of the historical capacity comparison."""
import plotly.graph_objects as go
import streamlit as st

from .comparison import compare_strategies
from .comparison_export import comparison_csv
from .model import get_model
from .help_text import comparison_capacity_help


def render_comparison(test_data, *, complete_with_active):
    st.html('<div class="section-heading"><h2>Comparação de estratégias</h2><span>04 / VALIDAR</span></div>')
    with st.container(border=True):
        st.write("Com a mesma capacidade de atendimento, quantos cancelamentos históricos cada estratégia identifica?")
        st.caption(
            f"Avaliação nos {len(test_data):,} clientes separados para teste. "
            "Esta comparação usa o conjunto de teste completo; os filtros e a busca da carteira não alteram esta base."
        )
        capacity = st.number_input(
            "Capacidade de atendimento (clientes)", min_value=1, value=None, step=1,
            placeholder="Digite a quantidade de clientes", key="comparison_capacity",
            help=comparison_capacity_help(len(test_data), int(test_data.Exited.sum()), complete_with_active),
        )
        if capacity is None:
            st.info("Informe a capacidade para calcular a comparação. Nenhuma quantidade foi predefinida.")
            return
        if test_data.empty:
            st.info("Não há clientes de teste disponíveis para comparar.")
            return
        if capacity > len(test_data):
            st.info(f"A capacidade informada excede a base. A seleção fica limitada aos {len(test_data)} clientes disponíveis.")

        results = compare_strategies(
            test_data, capacity, include_inactivity=True,
            complete_with_active=complete_with_active,
        )
        table = results.rename(columns={
            "strategy": "Estratégia", "result_type": "Tipo de resultado",
            "selected": "Clientes selecionados", "captured": "Cancelamentos identificados",
            "precision": "Taxa histórica na seleção (%)",
            "predicted_rate": "Probabilidade média estimada (%)",
            "probability_gap_pp": "Estimado − histórico (p.p.)",
            "recall": "Cancelamentos da base identificados (%)",
        })[["Estratégia", "Tipo de resultado", "Clientes selecionados", "Cancelamentos identificados",
             "Probabilidade média estimada (%)", "Taxa histórica na seleção (%)", "Estimado − histórico (p.p.)", "Cancelamentos da base identificados (%)"]].copy()
        for column in ("Probabilidade média estimada (%)", "Taxa histórica na seleção (%)", "Cancelamentos da base identificados (%)"):
            table[column] *= 100

        st.subheader("Risco estimado × cancelamento histórico")
        st.caption("Para os clientes selecionados por cada estratégia, compare a probabilidade média prevista com a proporção de cancelamentos registrados. As duas barras usam a mesma escala de 0 a 100%.")
        labels = ["Modelo · seleção definida", "Aleatória · média esperada", "Inativos primeiro · média esperada"]
        fig = go.Figure()
        for name, values, color in [
            ("Probabilidade estimada", results.predicted_rate * 100, "#195AB4"),
            ("Taxa histórica", results.precision * 100, "#05132A"),
        ]:
            fig.add_bar(y=labels, x=values, name=name, orientation="h", marker_color=color,
                        text=[f"{value:.1f}%".replace(".", ",") for value in values],
                        textposition="auto", customdata=results.selected,
                        hovertemplate="%{y}<br>%{x:.1f}%<br>%{customdata} clientes selecionados<extra>%{fullData.name}</extra>")
        fig.update_layout(height=350, barmode="group", bargap=0.3,
                          margin=dict(l=16, r=24, t=12, b=70),
                          paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font=dict(color="#4A5568"), legend=dict(orientation="h", y=-0.25),
                          xaxis=dict(title="Percentual entre os selecionados (%)", range=[0,100], gridcolor="#E6EAF1"),
                          yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.caption("Valor real significa resultado histórico (Exited), não uma probabilidade individual conhecida. Para as estratégias com sorteio, ambos os percentuais representam médias esperadas sobre as seleções possíveis, não um sorteio realizado.")

        st.subheader("Quantos cancelamentos a seleção identifica?")
        cancellations = int(test_data.Exited.sum())
        st.caption(f"O teste contém {cancellations} cancelamentos. As barras mostram quantos entram na seleção; os percentuais indicam a cobertura desse total.")
        coverage_labels = [f"{row.captured:.2f} · {row.recall * 100:.1f}% do total".replace(".", ",")
                           if cancellations else f"{row.captured:.2f} · cobertura indisponível".replace(".", ",")
                           for row in results.itertuples()]
        capture_fig = go.Figure(go.Bar(y=labels, x=results.captured, orientation="h",
                                     marker_color="#307AE0", text=coverage_labels, textposition="auto",
                                     customdata=results.result_type,
                                     hovertemplate="%{y}<br>%{x:.2f} cancelamentos identificados<br>%{customdata}<extra></extra>"))
        capture_fig.update_layout(height=270, margin=dict(l=16, r=24, t=12, b=40),
                                  paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                  font=dict(color="#4A5568"), yaxis=dict(autorange="reversed"),
                                  xaxis=dict(title="Cancelamentos identificados (clientes)",
                                             range=[0, max(1, cancellations)], gridcolor="#E6EAF1"))
        st.plotly_chart(capture_fig, width="stretch", config={"displayModeBar": False})
        st.caption("Maior cobertura significa encontrar mais cancelamentos históricos dentro da capacidade. Isso não mede cancelamentos evitados. A proximidade entre as barras do primeiro gráfico é um diagnóstico agregado; consulte também a curva de calibração.")
        st.dataframe(table, hide_index=True, width="stretch", column_config={
            "Cancelamentos identificados": st.column_config.NumberColumn(format="%.2f"),
            "Taxa histórica na seleção (%)": st.column_config.NumberColumn(format="%.1f%%"),
            "Probabilidade média estimada (%)": st.column_config.NumberColumn(format="%.1f%%"),
            "Estimado − histórico (p.p.)": st.column_config.NumberColumn(format="%.2f"),
            "Cancelamentos da base identificados (%)": st.column_config.NumberColumn(format="%.1f%%"),
        })
        cancellations = int(test_data.Exited.sum())
        st.caption(
            f"A base de teste contém {cancellations} cancelamentos registrados. "
            "No modelo, a contagem é observada; nas regras com sorteio, é uma média esperada e pode ser fracionária. "
            "Cancelamentos identificados não representam cancelamentos evitados."
        )
        if results.selected.nunique() > 1:
            st.info("As estratégias selecionaram quantidades diferentes. Compare também os percentuais e a capacidade efetivamente utilizada.")
        _, metadata = get_model()
        st.download_button(
            "Exportar relatório completo ↓",
            comparison_csv(test_data, capacity, metadata, complete_with_active=complete_with_active),
            f"churn_analisys_comparacao_capacidade_{capacity}_{metadata['version']}.csv",
            "text/csv", key="comparison_download",
        )
        st.caption("CSV para planilhas: UTF-8, separador ponto e vírgula e vírgula decimal. Uma linha por estratégia, com capacidade, métricas, comparação com sorteio, regras e versão do modelo. O risco mínimo da carteira não é aplicado nesta avaliação.")
        with st.expander("O que contém o relatório exportado"):
            st.write("As colunas seguem a ordem: estratégia → capacidade → base avaliada → resultados → comparação com sorteio → método e rastreabilidade. Valores numéricos têm até seis casas decimais; percentuais vão de 0 a 100.")
            st.write("Precisão é a proporção de cancelamentos entre os selecionados. Cobertura é a proporção dos cancelamentos da base identificada pela seleção. Lift divide a precisão pela taxa de churn da base: 1 significa a mesma concentração esperada de um sorteio; acima de 1, maior concentração; abaixo de 1, menor concentração.")
            st.write("As diferenças usam um sorteio com a mesma quantidade efetivamente selecionada por cada estratégia. A diferença de precisão é medida em pontos percentuais. Valores negativos são mantidos. Se o denominador for zero, a métrica fica vazia, sem substituir ausência de informação por zero.")
        with st.expander("Como a comparação é calculada"):
            st.write("Modelo: seleciona os maiores riscos calibrados. Empates são resolvidos pelo ID do cliente. O cancelamento real não participa da ordenação.")
            st.write("Aleatória: todos os clientes têm a mesma chance, sem repetição. A média esperada é a quantidade selecionada multiplicada pela proporção de cancelamentos da base de teste.")
            completion = "Se faltarem inativos, as vagas restantes são preenchidas por sorteio entre os ativos." if complete_with_active else "Se faltarem inativos, a lista fica menor e não é completada com ativos."
            st.write("Inativos primeiro: usa IsActiveMember = 0. Quando é necessário desempatar, considera sorteio uniforme entre os inativos. " + completion)
            st.write("A porcentagem na seleção divide os cancelamentos identificados pela quantidade selecionada. A cobertura divide pelos cancelamentos de toda a base de teste. Percentuais sem denominador ficam indisponíveis.")
            st.write("A probabilidade média é a soma das probabilidades calibradas dividida pelo tamanho da seleção. Nas regras aleatórias, calculamos essa média por grupo, ponderada pelas quantidades selecionadas. A diferença estimado − histórico usa pontos percentuais: positiva indica estimativa média acima da taxa histórica; negativa, abaixo.")
            st.write("Exited é consultado somente para avaliar os resultados. A avaliação é histórica e não estima o efeito de uma campanha de retenção.")
