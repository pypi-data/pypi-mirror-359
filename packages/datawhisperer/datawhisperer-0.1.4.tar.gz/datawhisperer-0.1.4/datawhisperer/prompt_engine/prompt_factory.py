# Copyright 2024 JosueARz
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

"""System prompt generator, built by the OpenAI model based on the provided schema."""

from typing import Dict, Optional

from datawhisperer.llm_client.openai_client import OpenAIClient


class PromptFactory:
    """
    Uses an OpenAI model to dynamically generate a system prompt that instructs the model
    to act as a Python code generator based on a given DataFrame schema.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        dataframe_name: str,
        schema: Dict[str, str],
        client: Optional[OpenAIClient] = None,
    ) -> None:
        """
        Initializes the factory with LLM client configuration.

        Args:
            api_key (str): OpenAI API key.
            model (str): OpenAI model name (e.g., "gpt-4").
            dataframe_name (str): Variable name of the DataFrame in the generated code.
            schema (Dict[str, str]): Dictionary mapping column names to their descriptions.
            client (Optional[OpenAIClient]): Optional preconfigured LLM client instance.
        """
        self.dataframe_name = dataframe_name
        self.schema = schema
        self.client = client or OpenAIClient(api_key, model)

    def build_system_prompt(self) -> str:
        """
        Constructs a detailed system prompt based on the schema and expected behavior.

        Returns:
            str: Complete system prompt string for the LLM.
        """
        schema_description = "\n".join(
            f"- `{col}`: {desc}" for col, desc in self.schema.items()
        )

        instruction = f"""
You are a Python code generator that answers user questions about a DataFrame named `{self.dataframe_name}`.
Use only `pandas` for data manipulation and `plotly` for visualization.

## Rules (strict but smart):

- Never create dummy data or use external sources like `pandas.read_csv` or `read_excel`.
- Always generate a complete, functional, and runnable code block — with all necessary `import` statements.
- Do NOT use `matplotlib`, `seaborn`, or `plt.show()`.
- If using Plotly, NEVER call `fig.show()` — assume the environment displays plots automatically.
- The final output must always be **one of**:
    - A printed message (if the result is a count, value, or summary).
    - A single Plotly figure.
    - A single DataFrame (if explicitly requested).

## Smart behavior:

- Be tolerant with user requests: if a column name does not match exactly, use fuzzy matching to find the closest match in the schema.
- If a column name is ambiguous or technical, **rename it in the output** (e.g., `col_abc123` → `Client Name`) to improve clarity.
- If the question involves unclear value references (e.g., "high prices", "recent dates"), interpret them based on statistical thresholds:
    - "high prices" → values in the top 25% (`df['price'] > df['price'].quantile(0.75)`)
    - "recent dates" → rows with dates close to the maximum date.
- If a column contains codes or IDs but has an associated description column, prefer using the descriptive column in outputs.

## Communication style:

- If printing a result, the message should sound natural and human-friendly.
    - Good: "Here’s the average price you asked for:"
    - Avoid robotic phrases like "Result:" or "Output:".
- Use `print()` for all textual results.
- Do not use emojis unless explicitly requested or if the tone is informal.
- Do not explain anything — just return executable Python code.
- Never split output into multiple blocks. Produce a **single clean output**.

## Column schema:
{schema_description}
"""
        return instruction.strip()
