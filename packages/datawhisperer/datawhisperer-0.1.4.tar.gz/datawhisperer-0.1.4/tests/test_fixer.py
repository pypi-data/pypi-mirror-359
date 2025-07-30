import pytest

from datawhisperer.code_executor.fixer import CodeFixer
from datawhisperer.llm_client.gemini_client import GeminiClient
from datawhisperer.llm_client.openai_client import OpenAIClient


class FakeClient:
    def chat(self, messages):
        user_prompt = messages[0]["content"]
        assert "Question:" in user_prompt
        assert "Code (which failed to execute):" in user_prompt
        assert "The code failed with the following error:" in user_prompt
        assert "Return only the corrected Python code" in user_prompt
        return "# Código corregido\nprint('OK')"


@pytest.fixture
def fixer_with_fake_client(monkeypatch):
    fixer = CodeFixer(api_key="fake-key", model="gpt-4")
    fixer.client = FakeClient()  # 🧪 inyectamos fake client para evitar conexión real
    return fixer


def test_fix_code_returns_expected_code(fixer_with_fake_client):
    code_with_error = "print('mal código'"
    error_message = "SyntaxError: unexpected EOF while parsing"
    schema = {"ventas": "Total de ventas"}
    dataframe_name = "df"

    fixed_code = fixer_with_fake_client.fix_code(
        question="¿Cuántas ventas hay?",
        code=code_with_error,
        error=error_message,
        schema=schema,
        dataframe_name=dataframe_name,
    )

    assert "print('OK')" in fixed_code


def test_fixer_initializes_openai_client():
    fixer = CodeFixer(api_key="fake", model="gpt-4")
    assert isinstance(fixer.client, OpenAIClient)


def test_fixer_initializes_gemini_client():
    fixer = CodeFixer(api_key="fake", model="gemini-1.5-pro")
    assert isinstance(fixer.client, GeminiClient)
