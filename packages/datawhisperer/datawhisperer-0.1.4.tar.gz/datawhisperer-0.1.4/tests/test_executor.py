import pandas as pd
import plotly.graph_objects as go
import pytest

from datawhisperer.code_executor.executor import (
    detect_last_dataframe,
    detect_last_plotly_chart,
    run_user_code,
    run_with_repair,
    sanitize_code,
)


@pytest.mark.parametrize(
    "input_code, expected",
    [
        ("```python\nprint('Hello')\n```", "print('Hello')"),
        ("```print('Hola')```", "print('Hola')"),
        ("print('Hello')", "print('Hello')"),
        ("fig.show()", ""),
        ("plt.show()", ""),
        ("print('Start')\nfig.show()\nprint('End')", "print('Start')\n\nprint('End')"),
    ],
)
def test_sanitize_code(input_code, expected):
    assert sanitize_code(input_code) == expected


def test_run_user_code_success():
    code = """
df2 = df[df['sales'] > 100]
print("Filtrado completado")
"""
    context = {
        "df": pd.DataFrame(
            {
                "region": ["North", "South", "East"],
                "sales": [100, 200, 300],
                "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            }
        )
    }

    output_text, table_result, chart_result, final_code, success = run_user_code(
        code, context, dataframe_name="df"
    )

    assert success is True
    assert "Filtrado completado" in output_text
    assert isinstance(table_result, pd.DataFrame)
    assert len(table_result) == 2
    assert chart_result is None


def test_run_user_code_with_plotly_chart():
    code = """
import plotly.graph_objects as go

fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
"""
    context = {}

    output_text, table_result, chart_result, final_code, success = run_user_code(
        code, context, dataframe_name="df"
    )

    assert success is True
    assert chart_result is not None
    assert hasattr(chart_result, "to_plotly_json")  # asegura que es una figura válida
    assert output_text == ""  # no hay prints
    assert table_result is None


def test_run_user_code_with_error():
    code = """
# Esto fallará porque 'ventas' no es una columna válida
df2 = df[df['ventas'] > 100]
"""
    context = {
        "df": pd.DataFrame(
            {
                "region": ["North", "South"],
                "sales": [100, 200],
                "date": ["2024-01-01", "2024-01-02"],
            }
        )
    }

    output_text, table_result, chart_result, final_code, success = run_user_code(
        code, context, dataframe_name="df"
    )

    assert success is False
    assert "Execution error" in output_text or "KeyError" in output_text
    assert table_result is None
    assert chart_result is None


def test_detect_last_dataframe():
    original_df = pd.DataFrame({"a": [1, 2, 3]})
    other_df = pd.DataFrame({"b": [4, 5, 6]})

    context = {
        "df": original_df,
        "temp": "valor",
        "df_aux": other_df,
    }

    result = detect_last_dataframe(context, dataframe_name="df")
    assert result is other_df


def test_detect_last_dataframe_none():
    df = pd.DataFrame({"x": [1, 2]})
    context = {"df": df}

    result = detect_last_dataframe(context, dataframe_name="df")
    assert result is None


def test_detect_last_plotly_chart():
    chart1 = go.Figure()
    chart2 = go.Figure()

    context = {
        "value": 123,
        "chart1": chart1,
        "chart2": chart2,
    }

    result = detect_last_plotly_chart(context)
    assert result is chart2  # Último gráfico


def test_detect_last_plotly_chart_none():
    context = {"value": 123, "df": pd.DataFrame({"a": [1, 2]})}

    result = detect_last_plotly_chart(context)
    assert result is None


def test_run_with_repair_success_after_fix(monkeypatch):
    class FakeFixer:
        def fix_code(self, question, code, error, schema, dataframe_name):
            return "print('Código reparado')"

    # Monkeypatch el CodeFixer por el fake
    monkeypatch.setattr("datawhisperer.code_executor.executor.CodeFixer", lambda *_: FakeFixer())

    broken_code = "x ==="  # Código inválido a propósito
    question = "¿Qué hace este código?"
    context = {}
    schema = {"x": "una columna"}
    dataframe_name = "df"
    api_key = "irrelevant"
    model = "irrelevant"

    output, table, chart, final_code, success = run_with_repair(
        broken_code, question, context, schema, dataframe_name, api_key, model
    )

    assert success is True
    assert "Código reparado" in output
    assert table is None
    assert chart is None
