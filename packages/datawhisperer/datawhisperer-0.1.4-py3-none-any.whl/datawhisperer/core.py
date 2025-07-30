# Copyright 2024 JosueARz
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

"""Main orchestrator: chatbot to interact with a DataFrame using natural language."""

import inspect
from typing import Dict, Optional

import pandas as pd

from datawhisperer.code_executor.executor import run_with_repair
from datawhisperer.core_types import InteractiveResponse
from datawhisperer.llm_client.gemini_client import GeminiClient
from datawhisperer.llm_client.openai_client import OpenAIClient
from datawhisperer.prompt_engine.prompt_cache import (
    hash_schema,
    load_cached_prompt,
    save_cached_prompt,
)
from datawhisperer.prompt_engine.prompt_factory import PromptFactory


class DataFrameChatbot:
    """
    Main chatbot class that uses a language model to generate Python code
    in response to user questions about a given DataFrame.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        dataframe: Optional[pd.DataFrame] = None,
        schema: Optional[Dict[str, str]] = None,
        dataframe_name: Optional[str] = None,
        llm_client=None,
        max_retries: int = 3,
    ) -> None:
        """
        Initializes the chatbot with model credentials and context.

        Args:
            api_key (str): API key for OpenAI or Gemini.
            model (str): Model name.
            dataframe (Optional[pd.DataFrame]): DataFrame to analyze.
            schema (Optional[Dict[str, str]]): Column descriptions.
            dataframe_name (Optional[str]): Name of the DataFrame variable in code.
            llm_client (Optional): Custom LLM client (overrides default).
        """
        self.api_key = api_key
        self.model = model
        self._schema = schema or {}
        self.max_retries = max_retries

        if dataframe_name is None and dataframe is not None:
            frame = inspect.currentframe()
            try:
                outer_frame = frame.f_back
                for var_name, var_val in outer_frame.f_locals.items():
                    if var_val is dataframe:
                        dataframe_name = var_name
                        break
            finally:
                del frame

        if dataframe_name is None:
            raise ValueError("Could not infer the name of the DataFrame. Please provide it manually.")

        self.dataframe_name = dataframe_name
        self.client = llm_client or self._init_llm_client(api_key, model)

        schema_hash = hash_schema(self._schema)
        cached_prompt = load_cached_prompt(schema_hash)

        if cached_prompt is None:
            prompt_factory = PromptFactory(
                api_key=api_key,
                model=model,
                dataframe_name=self.dataframe_name,
                schema=self._schema,
                client=self.client,
            )
            system_prompt = prompt_factory.build_system_prompt()
            save_cached_prompt(schema_hash, system_prompt)
        else:
            system_prompt = cached_prompt

        self._system_prompt = system_prompt
        self._context = {self.dataframe_name: dataframe} if dataframe is not None else {}

    def _init_llm_client(self, api_key: str, model: str):
        """
        Initializes the appropriate LLM client (OpenAI or Gemini).

        Args:
            api_key (str): API key for the LLM provider.
            model (str): Model name.

        Returns:
            OpenAIClient or GeminiClient instance.
        """
        if model.startswith("gemini"):
            return GeminiClient(api_key, model_name=model)
        return OpenAIClient(api_key=api_key, model=model)

    def ask(self, question: str) -> str:
        """
        Sends a natural language question to the LLM and returns the generated code.

        Args:
            question (str): User question in natural language.

        Returns:
            str: Generated Python code from the LLM.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": question},
        ]
        return self.client.chat(messages)

    def ask_and_run(self, question: str, debug: bool = False) -> InteractiveResponse:
        """
        Sends a question and executes the resulting code with automatic repair if needed.

        Args:
            question (str): User question in natural language.
            debug (bool): Whether to enable debug mode.

        Returns:
            InteractiveResponse: Full structured result.
        """
        code = self.ask(question)

        if debug:
            print(f"[DEBUG] Generated code:\n{code}")

        text, table, chart, final_code, success = run_with_repair(
            code=code,
            question=question,
            context=self.context,
            schema=self.schema,
            dataframe_name=self.dataframe_name,
            api_key=self.api_key,
            model=self.model,
            max_retries=self.max_retries  # ← Uso del parámetro de instancia
        )

        return InteractiveResponse(
            text=text,
            value=table if table is not None else chart,
            code=final_code,
            table=table,
            chart=chart,
        )


    # --- Read-only properties ---

    @property
    def schema(self) -> Dict[str, str]:
        """Returns a copy of the schema dictionary."""
        return self._schema.copy()

    @property
    def context(self) -> Dict[str, object]:
        """Returns a copy of the execution context."""
        return self._context.copy()

    @property
    def system_prompt(self) -> str:
        """Returns the generated or cached system prompt."""
        return self._system_prompt
