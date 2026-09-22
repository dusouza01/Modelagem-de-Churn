"""CSV import and model provenance controls, isolated from the reference dashboard."""
import streamlit as st

from .importing import analyze_import
from .help_text import PURPOSE_HELP, CSV_HELP
from .model import get_model
from .validation import DataValidationError, FEATURES, IDENTITY


def render_import():
    bundle, metadata = get_model()
    st.html('<div class="section-heading"><h2>Importar e validar clientes</h2><span>05 / APLICAR</span></div>')
    with st.container(border=True):
        st.caption(f"Modelo ativo: {metadata['version']} · treinado em {metadata['created_at_utc']}")
        with st.expander("Rastreabilidade do modelo e contrato do arquivo"):
            st.write("O modelo salvo é usado somente para previsão. Para gerar uma nova versão com a base local, execute treinar.bat.")
            st.write("CSV UTF-8, separado por vírgulas, com ponto decimal. Limites técnicos: 10 MiB e 100.000 linhas. Não são preenchidos valores ausentes nem removidas linhas inválidas automaticamente.")
            st.write("Colunas obrigatórias: " + ", ".join(IDENTITY + FEATURES) + ". Exited (0 ou 1) também é obrigatória na avaliação histórica.")
            st.write("IDs devem ser únicos; campos numéricos devem ser finitos e não negativos. Idade, tempo de relacionamento, quantidade de produtos e score devem ser inteiros. HasCrCard e IsActiveMember aceitam 0 ou 1.")
            st.write("Categorias aceitas pelo modelo: " + "; ".join(f"{name}: {', '.join(values)}" for name, values in bundle["categories"].items()))
            st.caption("Colunas extras não entram no modelo. As regras validam o contrato técnico; não certificam a origem nem a qualidade de negócio dos dados.")
            st.json({**metadata, "calibration": {"Calibrado": metadata["calibration"]["Calibrado"]}}, expanded=False)
        purpose = st.selectbox("Finalidade da importação", ["Prever risco de clientes", "Avaliar resultados históricos"], index=None,
                               placeholder="Escolha a finalidade antes de enviar", key="import_purpose", help=PURPOSE_HELP)
        if purpose is None:
            st.info("Escolha se deseja prever riscos ou avaliar cancelamentos já observados.")
            return
        historical = purpose == "Avaliar resultados históricos"
        header = IDENTITY + FEATURES + (["Exited"] if historical else [])
        st.download_button("Baixar cabeçalho CSV", (",".join(header) + "\n").encode("utf-8-sig"),
                           "estrutura_clientes.csv", "text/csv", key="schema_download")
        st.caption("O modelo de arquivo contém somente o cabeçalho. Preencha com seus dados; nenhum cliente de exemplo foi inventado.")
        upload = st.file_uploader("Arquivo CSV", type=["csv"], max_upload_size=10,
                                  key="historical_upload" if historical else "prediction_upload",
                                  help=CSV_HELP + "\n\n**Categorias aceitas:** " + "; ".join(f"{name}: {', '.join(values)}" for name, values in bundle["categories"].items()))
        if upload is None:
            return
        try:
            predictions, metrics, overlap = analyze_import(upload.getvalue(), bundle, historical=historical)
        except DataValidationError as error:
            st.error("Arquivo não aceito. Corrija os problemas abaixo e envie novamente.")
            for issue in str(error).splitlines():
                st.write(issue)
            return
        st.success(f"{len(predictions):,} clientes validados e pontuados com o modelo {metadata['version']}.")
        st.caption("A importação não altera a carteira de referência, a comparação de estratégias ou o modelo. O arquivo não é salvo em disco pela aplicação.")
        if overlap:
            st.warning(f"{overlap:,} IDs já pertencem à base usada no desenvolvimento do modelo. As previsões estão disponíveis, mas métricas desta importação ficam desabilitadas para evitar apresentá-las como validação independente.")
        if not historical and "Exited" in predictions:
            st.caption("Exited foi validada, mas não participa da previsão. Para medir desempenho, use a finalidade de avaliação histórica.")
        if metrics is not None:
            columns = st.columns(3)
            columns[0].metric("Brier · arquivo importado", f"{metrics['brier']:.4f}")
            columns[1].metric("Log loss · arquivo importado", f"{metrics['log_loss']:.4f}")
            columns[2].metric("ROC AUC · arquivo importado", "Indisponível" if metrics["auc"] is None else f"{metrics['auc']:.3f}")
            if metrics["auc"] is None:
                st.info("ROC AUC exige exemplos das duas classes; o arquivo contém apenas uma.")
            st.caption("A ausência de IDs conhecidos é uma verificação de sobreposição, não uma garantia de independência ou de desempenho futuro. A origem e o período dos dados precisam ser verificados por quem os fornece.")
        result = predictions.sort_values(["churn_probability", "CustomerId"], ascending=[False, True]).copy()
        result = result.rename(columns={"churn_probability": "Risco (%)"})
        result["Risco (%)"] *= 100
        result["Modelo"] = metadata["version"]
        st.dataframe(result, hide_index=True, width="stretch", height=300)
        st.download_button("Exportar previsões importadas", result.to_csv(index=False).encode("utf-8-sig"),
                           "previsoes_importadas.csv", "text/csv", key="import_download")
