"""Display measured probability quality without promising calibration gains."""
import plotly.graph_objects as go
import streamlit as st


def render_calibration(metrics):
    st.html('<div class="section-heading"><h2>Confiabilidade das probabilidades</h2><span>03 / CALIBRAÇÃO</span></div>')
    with st.container(border=True):
        st.write("O risco estimado se aproxima da frequência de cancelamento observada?")
        st.caption(
            f"Modelo calibrado avaliado em {metrics['test_count']} clientes de teste. "
            "Esses registros não foram usados para treinar ou calibrar o modelo."
        )
        diagnostics = {"Calibrado": metrics["calibration"]["Calibrado"]}
        values = diagnostics["Calibrado"]
        left, right = st.columns(2)
        left.metric("Brier · modelo calibrado", f"{values['brier']:.4f}".replace(".", ","))
        right.metric("Log loss · modelo calibrado", f"{values['log_loss']:.4f}".replace(".", ","))
        st.caption("Brier mede o erro quadrático das probabilidades; log loss penaliza previsões confiantes e incorretas. Valores menores indicam menor erro nessas métricas.")
        st.caption("O Brier também reflete a capacidade de separar os grupos; use a curva abaixo para avaliar a correspondência entre risco previsto e observado.")
        reliability = values["reliability"]
        fig = go.Figure()
        for name, column, color in [
            ("Churn real · histórico", "observed", "#427A4B"),
            ("Churn estimado · modelo", "predicted", "#C2A000"),
        ]:
            fig.add_scatter(
                x=reliability.interval.astype(str), y=reliability[column] * 100,
                customdata=reliability[["clients", "predicted", "observed"]].assign(
                    predicted=reliability.predicted * 100, observed=reliability.observed * 100,
                ).values,
                name=name, mode="lines+markers", line=dict(color=color, width=3),
                marker=dict(size=7), connectgaps=False,
                hovertemplate="Faixa: %{x}<br>Clientes: %{customdata[0]:.0f}<br>Estimado: %{customdata[1]:.1f}%<br>Real: %{customdata[2]:.1f}%<extra>%{fullData.name}</extra>",
            )
        detail = reliability.copy()
        detail.insert(0, "Modelo", "Calibrado")
        detail[["predicted", "observed"]] *= 100
        fig.update_layout(
            height=380, margin=dict(l=20, r=20, t=10, b=85),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#555B54"), legend=dict(orientation="h", y=-0.25),
            xaxis=dict(title="Faixa de risco estimado (%)", type="category", gridcolor="#ECEEE8"),
            yaxis=dict(title="Taxa de churn / probabilidade média (%)", range=[0, 100], gridcolor="#ECEEE8"),
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.caption("Verde: proporção real de cancelamentos registrados em Exited. Amarelo: média das probabilidades calibradas do modelo. Cada par de pontos considera exatamente os mesmos clientes de teste, agrupados em faixas de risco de 10 pontos percentuais. Quanto mais próximas as linhas, maior a concordância nesse grupo.")
        st.caption("Passe o cursor para consultar as duas medidas e o número de clientes. Grupos pequenos têm maior incerteza; faixas vazias ficam sem pontos e interrompem as linhas. As faixas são diagnósticas e não definem a prioridade de atendimento. O histórico não comprova resultados futuros.")
        with st.expander("Ver faixas e método de calibração"):
            detail = detail.rename(columns={
                "interval": "Faixa", "clients": "Clientes", "predicted": "Estimado (%)", "observed": "Observado (%)",
            })
            st.dataframe(detail, hide_index=True, width="stretch", column_config={
                "Estimado (%)": st.column_config.NumberColumn(format="%.1f%%"),
                "Observado (%)": st.column_config.NumberColumn(format="%.1f%%"),
            })
            st.write(f"Calibração sigmoide com validação cruzada estratificada em cinco partes dos {metrics['train_count']} registros de treino. Cada previsão usada para ajustar a calibração vem de um modelo que não treinou naquele registro. O estimador final usa todo o treino.")
            st.write("O método foi definido antes de observar os resultados do teste. O teste é uma avaliação histórica; não demonstra desempenho em clientes futuros nem impacto de campanhas.")
            st.write("A carteira e a comparação de estratégias usam as probabilidades calibradas. A carteira também contém registros de treino; a avaliação de confiabilidade utiliza exclusivamente o teste.")
