import pandas as pd
import pytest

from datawhisperer import DataFrameChatbot, InteractiveResponse


@pytest.fixture
def sample_dataframe():
    return pd.DataFrame(
        {"region": ["North", "South"], "sales": [100, 200], "date": ["2024-01-01", "2024-01-02"]}
    )


@pytest.fixture
def sample_schema():
    return {"region": "Sales region", "sales": "Total sales amount", "date": "Date of sale"}


def test_chatbot_initialization(sample_dataframe, sample_schema, fake_llm_client):
    bot = DataFrameChatbot(
        api_key="fake",
        model="fake-model",
        dataframe=sample_dataframe,
        schema=sample_schema,
        dataframe_name="df",
        llm_client=fake_llm_client,
    )
    assert bot.dataframe_name == "df"


def test_chatbot_response_type(sample_dataframe, sample_schema):
    class FakeClient:
        def chat(self, messages):
            return "print('Total: 300')"

    bot = DataFrameChatbot(
        api_key="irrelevant",
        model="mock-model",
        dataframe=sample_dataframe,
        schema=sample_schema,
        dataframe_name="df",
        llm_client=FakeClient(),  # evita llamadas reales
    )

    response = bot.ask_and_run("What is the total sales?")
    assert isinstance(response, InteractiveResponse)
    assert "Total" in response.text
