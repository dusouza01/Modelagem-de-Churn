"""Display measured probability quality without promising calibration gains."""
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from .uncertainty import observed_intervals


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
        reliability = observed_intervals(values["reliability"])
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.72, 0.28], vertical_spacing=0.12)
        for name, column, color in [
            ("Taxa de cancelamento observada", "observed", "#427A4B"),
            ("Probabilidade média estimada", "predicted", "#C2A000"),
        ]:
            fig.add_scatter(
                x=reliability.interval.astype(str), y=reliability[column] * 100,
                customdata=reliability[["clients", "predicted", "observed", "lower", "upper"]].assign(
                    predicted=reliability.predicted * 100, observed=reliability.observed * 100,
                    lower=reliability.lower * 100, upper=reliability.upper * 100,
                ).values,
                name=name, mode="lines+markers", line=dict(color=color, width=3),
                marker=dict(size=7), connectgaps=False,
                error_y=dict(type="data", symmetric=False,
                             array=(reliability.upper - reliability.observed) * 100,
                             arrayminus=(reliability.observed - reliability.lower) * 100,
                             color=color, thickness=1.5, width=5) if column == "observed" else None,
                hovertemplate="Faixa: %{x}<br>Clientes: %{customdata[0]:.0f}<br>Estimado: %{customdata[1]:.1f}%<br>Observado: %{customdata[2]:.1f}%<br>IC 95% observado: %{customdata[3]:.1f}% a %{customdata[4]:.1f}%<extra>%{fullData.name}</extra>",
                row=1, col=1,
            )
        fig.add_trace(go.Bar(
            x=reliability.interval.astype(str), y=reliability.clients,
            name="Clientes por faixa", showlegend=False, marker_color="#A9B8A5",
            text=[f"{n:,}".replace(",", ".") for n in reliability.clients],
            textposition="outside", cliponaxis=False,
            hovertemplate="Faixa: %{x}<br>Clientes de teste: %{y}<extra></extra>",
        ), row=2, col=1)
        detail = reliability.copy()
        detail.insert(0, "Modelo", "Calibrado")
        detail[["predicted", "observed", "lower", "upper"]] *= 100
        fig.update_layout(
            height=550, margin=dict(l=20, r=20, t=25, b=100),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#555B54"), legend=dict(orientation="h", y=-0.22),
        )
        fig.update_xaxes(type="category", categoryorder="array",
                         categoryarray=reliability.interval.astype(str).tolist())
        fig.update_xaxes(title="Faixa de risco estimado (%)", row=2, col=1)
        fig.update_yaxes(title="Taxa / probabilidade (%)", range=[0, 100], gridcolor="#ECEEE8", row=1, col=1)
        fig.update_yaxes(title="Clientes", range=[0, max(1, reliability.clients.max()) * 1.3],
                         gridcolor="#ECEEE8", row=2, col=1)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.caption("Verde: taxa de cancelamento observada em Exited. Amarelo: média das probabilidades calibradas. Cada par compara os mesmos clientes de teste. Verde acima do amarelo indica subestimação; abaixo, superestimação. A proximidade indica concordância naquela faixa, não acerto individual.")
        st.caption("As barras inferiores mostram quantos clientes sustentam cada comparação. As hastes verdes representam o intervalo de confiança de 95% de Wilson para a taxa observada. Grupos menores tendem a ter maior incerteza; o intervalo também depende da taxa. Faixas vazias não têm estimativa nem intervalo e interrompem as linhas.")
        with st.expander("Como interpretar os intervalos de confiança?"):
            st.write("A taxa observada é exata para os clientes desta amostra. O intervalo expressa a incerteza ao estimar a taxa de uma população comparável, supondo observações independentes. Em repetições da amostragem, o método busca cobrir a taxa populacional em aproximadamente 95% dos intervalos construídos.")
            st.write("Se a linha amarela estiver dentro da haste verde, a previsão média é compatível com esse intervalo; isso não comprova calibração perfeita. Fora dele, há um sinal de discrepância que merece investigação. Os intervalos são individuais por faixa, sem correção para múltiplas comparações, e não constituem um teste global de calibração.")
            st.write("O intervalo não mede a incerteza de cada cliente nem a variabilidade de retreinar o modelo. As faixas são diagnósticas e não definem a prioridade de atendimento. Mudanças no perfil dos clientes ou no período podem alterar os resultados; o histórico não garante desempenho futuro.")
        with st.expander("Ver faixas e método de calibração"):
            detail = detail.rename(columns={
                "interval": "Faixa", "clients": "Clientes", "predicted": "Estimado (%)", "observed": "Observado (%)",
                "lower": "IC 95% · inferior (%)", "upper": "IC 95% · superior (%)",
            })
            st.dataframe(detail, hide_index=True, width="stretch", column_config={
                "Estimado (%)": st.column_config.NumberColumn(format="%.1f%%"),
                "Observado (%)": st.column_config.NumberColumn(format="%.1f%%"),
                "IC 95% · inferior (%)": st.column_config.NumberColumn(format="%.1f%%"),
                "IC 95% · superior (%)": st.column_config.NumberColumn(format="%.1f%%"),
            })
            st.write(f"Calibração sigmoide com validação cruzada estratificada em cinco partes dos {metrics['train_count']} registros de treino. Cada previsão usada para ajustar a calibração vem de um modelo que não treinou naquele registro. O estimador final usa todo o treino.")
            st.write("O método foi definido antes de observar os resultados do teste. O teste é uma avaliação histórica; não demonstra desempenho em clientes futuros nem impacto de campanhas.")
            st.write("A carteira e a comparação de estratégias usam as probabilidades calibradas. A carteira também contém registros de treino; a avaliação de confiabilidade utiliza exclusivamente o teste.")
