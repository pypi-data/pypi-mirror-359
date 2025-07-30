# Copyright 2024 JosueARz
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

from typing import Dict

from datawhisperer.llm_client.gemini_client import GeminiClient
from datawhisperer.llm_client.openai_client import OpenAIClient


class CodeFixer:
    """
    Uses an LLM (OpenAI or Gemini) to fix Python code that failed to execute,
    based on the error message and the provided schema.
    """

    def __init__(self, api_key: str, model: str = "gpt-4.1-mini"):
        """
        Initializes the fixer with the appropriate LLM client.

        Args:
            api_key (str): API key for the LLM service.
            model (str): LLM model identifier. If it starts with 'gemini', uses GeminiClient.
        """
        if model.startswith("gemini"):
            self.client = GeminiClient(api_key=api_key, model_name=model)
        else:
            self.client = OpenAIClient(api_key=api_key, model=model)

    def fix_code(
        self,
        question: str,
        code: str,
        error: str,
        schema: Dict[str, str],
        dataframe_name: str,
    ) -> str:
        """
        Generates a corrected version of the failed code using the selected LLM.

        Args:
            question (str): User's original natural language question.
            code (str): Python code that failed to execute.
            error (str): Error message produced during execution.
            schema (Dict[str, str]): Dictionary mapping column names to descriptions.
            dataframe_name (str): Name of the DataFrame variable in the code.

        Returns:
            str: Corrected Python code (no explanations or comments).
        """
        schema_description = "\n".join(f"- {column}: {description}" for column, description in schema.items())

        prompt = f"""
                You previously generated the following Python code to answer a user's question:

                Question:
                {question}

                Code (which failed to execute):
                ```python
                {code.strip()}
                The code failed with the following error:
                {error}

                Note that the DataFrame is named {dataframe_name} and its schema is:
                {schema_description}

                Fix the code based on the schema above. Do not reference non-existent columns.
                Return only the corrected Python code — no explanations or comments.
                """
        
        messages = [{"role": "user", "content": prompt}]
        return self.client.chat(messages)

