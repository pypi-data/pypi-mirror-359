import pytest

from datawhisperer.prompt_engine.prompt_factory import PromptFactory


class FakeClient:
    def chat(self, messages):
        assert isinstance(messages, list)
        assert any("DataFrame named" in m["content"] for m in messages)
        return "# Código simulado por el prompt"


@pytest.fixture
def example_schema():
    return {"ventas": "Total de ventas", "fecha": "Fecha de la operación"}


def test_prompt_factory_builds_prompt_correctly(example_schema):
    factory = PromptFactory(
        api_key="dummy-key",
        model="gpt-4",
        dataframe_name="df",
        schema=example_schema,
        client=FakeClient(),
    )

    system_prompt = factory.build_system_prompt()
    assert "# Código simulado por el prompt" in system_prompt
