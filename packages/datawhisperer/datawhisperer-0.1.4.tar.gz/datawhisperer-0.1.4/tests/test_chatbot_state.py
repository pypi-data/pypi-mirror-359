import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import pandas as pd
from datawhisperer import DataFrameChatbot

@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({
        "producto": ["manzana", "pera", "naranja"],
        "precio": [10, 12, 8],
        "stock": [50, 30, 80],
        "categoria": ["fruta de pepita", "fruta de pepita", "fruta cítrica"],
        "origen": ["México", "España", "Brasil"]
    })

@pytest.fixture
def sample_schema():
    return {
        "producto": "nombre del producto",
        "precio": "precio en pesos mexicanos",
        "stock": "cantidad disponible en inventario",
        "categoria": "categoría de la fruta",
        "origen": "país de origen"
    }

@pytest.fixture
def chatbot(sample_dataframe, sample_schema):
    return DataFrameChatbot(
        api_key="*************************************",
        model="gpt-4.1-mini",
        dataframe=sample_dataframe,
        schema=sample_schema
    )

def test_state_immutability(chatbot):
    original_prompt = chatbot.system_prompt
    original_schema = chatbot.schema
    original_context_keys = set(chatbot.context.keys())

    _ = chatbot.ask_and_run("¿Puedes agrupar el stock por categoría y graficarlo?")

    # Verificamos que no cambie el prompt del sistema
    assert chatbot.system_prompt == original_prompt, "El system_prompt fue modificado."

    # Verificamos que el schema no haya sido modificado
    assert chatbot.schema == original_schema, "El schema fue modificado."

    # Verificamos que el context no tenga nuevas claves
    assert set(chatbot.context.keys()) == original_context_keys, "El context fue modificado con nuevas variables."
