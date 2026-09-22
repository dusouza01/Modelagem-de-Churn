"""Display measured probability quality without promising calibration gains."""
import pandas as pd
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
        fig = go.Figure()
        fig.add_scatter(x=[0, 100], y=[0, 100], mode="lines", name="Correspondência ideal",
                        line=dict(color="#B5BDAE", dash="dash"), hoverinfo="skip")
        tables = []
        for (label, values), color in zip(diagnostics.items(), ("#C2A000",)):
            reliability = values["reliability"]
            populated = reliability[reliability.clients > 0]
            fig.add_scatter(
                x=populated.predicted * 100, y=populated.observed * 100,
                customdata=populated[["clients", "interval"]].astype(str).values,
                name=label, mode="lines+markers", line=dict(color=color, width=2),
                hovertemplate="Estimado: %{x:.1f}%<br>Observado: %{y:.1f}%<br>%{customdata[0]} clientes · %{customdata[1]}<extra>%{fullData.name}</extra>",
            )
            detail = reliability.copy()
            detail.insert(0, "Modelo", label)
            detail[["predicted", "observed"]] *= 100
            tables.append(detail)
        fig.update_layout(
            height=340, margin=dict(l=20, r=20, t=10, b=20),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#555B54"), legend=dict(orientation="h", y=-0.25),
            xaxis=dict(title="Probabilidade média estimada (%)", range=[0, 100], gridcolor="#ECEEE8"),
            yaxis=dict(title="Cancelamentos observados (%)", range=[0, 100], gridcolor="#ECEEE8"),
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.caption("Cada ponto resume uma faixa de 10 pontos percentuais. Passe o cursor para consultar a quantidade de clientes. Faixas com poucos registros têm maior incerteza; faixas vazias não aparecem na curva. Essas faixas servem apenas ao diagnóstico, não à decisão de prioridade.")
        with st.expander("Ver faixas e método de calibração"):
            detail = pd.concat(tables, ignore_index=True).rename(columns={
                "interval": "Faixa", "clients": "Clientes", "predicted": "Estimado (%)", "observed": "Observado (%)",
            })
            st.dataframe(detail, hide_index=True, width="stretch", column_config={
                "Estimado (%)": st.column_config.NumberColumn(format="%.1f%%"),
                "Observado (%)": st.column_config.NumberColumn(format="%.1f%%"),
            })
            st.write(f"Calibração sigmoide com validação cruzada estratificada em cinco partes dos {metrics['train_count']} registros de treino. Cada previsão usada para ajustar a calibração vem de um modelo que não treinou naquele registro. O estimador final usa todo o treino.")
            st.write("O método foi definido antes de observar os resultados do teste. O teste é uma avaliação histórica; não demonstra desempenho em clientes futuros nem impacto de campanhas.")
            st.write("A carteira e a comparação de estratégias usam as probabilidades calibradas. A carteira também contém registros de treino; a avaliação de confiabilidade utiliza exclusivamente o teste.")
