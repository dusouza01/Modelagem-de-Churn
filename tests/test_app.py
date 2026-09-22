"""Run with .venv/Scripts/python.exe tests/test_app.py."""
from pathlib import Path

from streamlit.testing.v1 import AppTest


def client_table(app):
    return next((item.value for item in app.dataframe if "ID" in item.value.columns), None)


def comparison_table(app):
    return next(item.value for item in app.dataframe if "Estratégia" in item.value.columns)


app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=90).run()
assert not app.exception, app.exception
assert len(client_table(app)) == 10000
assert app.number_input(key="priority_capacity").value is None
assert app.number_input(key="minimum_risk").value is None
assert app.selectbox(key="priority_scope").value is None
assert set(client_table(app)["Prioridade"]) == {"Não definido"}
assert client_table(app)["Risco (%)"].between(0, 100).all()
app.selectbox(key="country").set_value("Germany").run()
assert not app.exception, app.exception
assert set(client_table(app)["País"]) == {"Alemanha"}
app.number_input(key="priority_capacity").set_value(50).run()
assert set(client_table(app)["Prioridade"]) == {"Não definido"}, "No scope must mean no automatic selection."
app.selectbox(key="priority_scope").set_value("Clientes sem cancelamento").run()
assert set(client_table(app)["Prioridade"]) == {"Não definido"}
app.number_input(key="minimum_risk").set_value(0.0).run()
app.selectbox(key="country").set_value("Todos").run()
app.selectbox(key="risk").set_value("Prioritário").run()
assert not app.exception, app.exception
assert len(client_table(app)) == 50
assert set(client_table(app)["Cancelamento histórico"]) == {"Não"}
app.selectbox(key="priority_scope").set_value("Todos · demonstração histórica").run()
assert not app.exception, app.exception
assert len(client_table(app)) == 50
# A filter must preserve the global priority of each client, including when
# capacity is larger than the displayed segment (the reported regression).
app.selectbox(key="risk").set_value("Todos").run()
app.number_input(key="priority_capacity").set_value(3000).run()
global_table = client_table(app).copy().set_index("ID")
assert (global_table.Prioridade == "Prioritário").sum() == 3000
app.selectbox(key="country").set_value("Germany").run()
app.selectbox(key="gender").set_value("Female").run()
segment_table = client_table(app).copy().set_index("ID")
assert 0 < len(segment_table) < 3000
assert segment_table.Prioridade.equals(global_table.loc[segment_table.index, "Prioridade"])
assert "Fora da capacidade" in set(segment_table.Prioridade)
assert "Prioritário" in set(segment_table.Prioridade)
# Switching to the contactable scope must also keep a stable global selection.
app.selectbox(key="priority_scope").set_value("Clientes sem cancelamento").run()
contact_segment = client_table(app).copy().set_index("ID")
app.selectbox(key="country").set_value("Todos").run()
app.selectbox(key="gender").set_value("Todos").run()
contact_global = client_table(app).copy().set_index("ID")
assert contact_segment.Prioridade.equals(contact_global.loc[contact_segment.index, "Prioridade"])
assert (contact_global.Prioridade == "Prioritário").sum() == 3000
assert set(contact_global.loc[contact_global.Prioridade == "Prioritário", "Cancelamento histórico"]) == {"Não"}
print("PASS: portfolio filters preserve global priorities in both scopes, even when capacity exceeds the displayed segment.")
app.number_input(key="minimum_risk").set_value(90.0).run()
threshold_table = client_table(app)
assert (threshold_table.loc[threshold_table.Prioridade == "Prioritário", "Risco (%)"] >= 90).all()
assert (threshold_table.Prioridade == "Prioritário").sum() < 3000
assert "Abaixo do risco mínimo" in set(threshold_table.Prioridade)
app.number_input(key="minimum_risk").set_value(100.0).run()
assert not (client_table(app).Prioridade == "Prioritário").any()
app.text_input(key="search").set_value("no-matching-client-123456789").run()
assert not app.exception, app.exception
assert client_table(app) is None
assert any("Nenhum cliente" in item.value for item in app.info)
app.button[0].click().run()
assert not app.exception, app.exception
assert len(client_table(app)) == 10000
assert app.text_input(key="search").value == ""
assert app.number_input(key="priority_capacity").value is None
assert app.number_input(key="minimum_risk").value is None
assert app.selectbox(key="priority_scope").value is None
print("PASS: calibrated probabilities, explicit scope/capacity, priority ranking, filters, empty search and reset.")

reliability = next(item.value for item in app.dataframe if "Estimado (%)" in item.value.columns)
assert reliability.groupby("Modelo").Clientes.sum().tolist() == [2000]
assert set(reliability.Modelo) == {"Calibrado"}
assert app.number_input(key="comparison_capacity").value is None
app.number_input(key="comparison_capacity").set_value(50).run()
assert not app.exception, app.exception
comparison = comparison_table(app).copy()
assert comparison["Estratégia"].tolist() == ["Modelo", "Aleatória", "Inativos primeiro"]
assert comparison["Clientes selecionados"].tolist() == [50, 50, 50]
app.selectbox(key="country").set_value("Germany").run()
assert not app.exception, app.exception
assert comparison.equals(comparison_table(app)), "Portfolio filters must not change the test population."
app.number_input(key="comparison_capacity").set_value(3000).run()
assert not app.exception, app.exception
full_test = comparison_table(app)
assert full_test["Clientes selecionados"].tolist() == [2000, 2000, 2000]
assert full_test["Cancelamentos identificados"].max() - full_test["Cancelamentos identificados"].min() < 1e-9
assert all(abs(value - 100) < 1e-9 for value in full_test["Cancelamentos da base identificados (%)"])
print("PASS: calibration sample accounting, comparison population isolation and capacity cap.")
