# Copyright 2024 JosueARz
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

"""Minimal client for interacting with the OpenAI API."""

from typing import Dict, List
from openai import OpenAI


class OpenAIClient:
    """
    Client for sending chat-style requests to the OpenAI API using the official OpenAI SDK.
    """

    def __init__(self, api_key: str, model: str = "gpt-4.1-mini") -> None:
        """
        Initializes the client with the provided API key and model.

        Args:
            api_key (str): OpenAI API key.
            model (str): Model to use (default: "gpt-4.1-mini").
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
        """
        Sends a list of chat-formatted messages and returns the model's response.

        Args:
            messages (List[Dict[str, str]]): List of messages like
                [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
            temperature (float): Degree of randomness in the response.

        Returns:
            str: Text content of the model's reply.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
