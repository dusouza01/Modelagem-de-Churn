"""Run with .venv/Scripts/python.exe tests/test_app.py."""
from pathlib import Path

from streamlit.testing.v1 import AppTest


app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=90).run()
assert not app.exception, app.exception
assert len(app.dataframe[0].value) == 10000
app.selectbox(key="country").set_value("Germany").run()
assert not app.exception, app.exception
assert set(app.dataframe[0].value["País"]) == {"Alemanha"}
app.selectbox(key="risk").set_value("Alto").run()
assert not app.exception, app.exception
assert (app.dataframe[0].value["Risco (%)"] >= 67).all()
app.text_input(key="search").set_value("no-matching-client-123456789").run()
assert not app.exception, app.exception
assert len(app.dataframe) == 0
assert any("Nenhum cliente" in item.value for item in app.info)
app.button[0].click().run()
assert not app.exception, app.exception
assert len(app.dataframe[0].value) == 10000
assert app.text_input(key="search").value == ""
print("PASS: initial render, country/risk filters, empty search and reset.")
