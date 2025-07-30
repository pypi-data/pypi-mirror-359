# Copyright 2024 JosueARz
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0

"""Minimal client for interacting with Google's Gemini API."""

from typing import Any, Dict, List, Optional

import google.generativeai as genai
from google.generativeai.types import GenerationConfig


class GeminiClient:
    """
    Client for sending chat-style requests to Google's Gemini API.

    Attributes:
        default_model_name (str): Default Gemini model to use.
    """

    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash-latest") -> None:
        """
        Initializes the Gemini client.

        Args:
            api_key (str): Google Generative AI API key.
            model_name (str): Gemini model name (default: "gemini-1.5-flash-latest").
        """
        genai.configure(api_key=api_key)
        self.default_model_name = model_name

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
        """
        Sends chat-formatted messages to the Gemini API and returns the response.

        The input format should match OpenAI-style chat logs:
            - "system": system prompt.
            - "user": user message.
            - "assistant": previous model reply (mapped to "model" for Gemini).

        Args:
            messages (List[Dict[str, str]]): List of chat messages.
            temperature (float): Controls randomness (range depends on the model).

        Returns:
            str: Text content from the Gemini model's response.
        """
        system_instruction: Optional[str] = None
        chat_history: List[Dict[str, Any]] = []

        for message in messages:
            role = message.get("role")
            content = message.get("content")

            if not role or not content:
                print(f"Warning: Skipping invalid message: {message}")
                continue

            if role == "system":
                if system_instruction is None:
                    system_instruction = content
                else:
                    system_instruction += "\n" + content
            elif role == "user":
                chat_history.append({"role": "user", "parts": [{"text": content}]})
            elif role == "assistant":
                chat_history.append({"role": "model", "parts": [{"text": content}]})
            else:
                print(f"Warning: Unrecognized role '{role}' ignored.")

        if not chat_history and not system_instruction:
            return "Error: No valid messages or system instructions provided."

        if not chat_history and system_instruction:
            return (
                "Error: A system instruction was provided, but no user message to respond to. "
                "At least one user message is required."
            )

        try:
            model = genai.GenerativeModel(
                model_name=self.default_model_name,
                system_instruction=system_instruction,
            )
            config = GenerationConfig(temperature=temperature)

            response = model.generate_content(
                contents=chat_history,
                generation_config=config,
            )

            if response.candidates:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    return candidate.content.parts[0].text.strip()

                reason_val = getattr(candidate.finish_reason, "value", candidate.finish_reason)
                reason_name = getattr(candidate.finish_reason, "name", "UNKNOWN")

                if reason_val not in [None, 1]:
                    return f"Generation stopped. Reason: {reason_name} (Value: {reason_val})."

            if response.prompt_feedback and response.prompt_feedback.block_reason:
                block_reason = getattr(response.prompt_feedback.block_reason, "name", "UNKNOWN")
                return f"Response blocked by the API. Reason: {block_reason}"

            if hasattr(response, "text") and response.text:
                return response.text.strip()

            return "Error: Gemini response is empty or in an unexpected format."

        except genai.types.generation_types.BlockedPromptException as e:
            print(f"Gemini Error: Blocked prompt. Details: {e}")
            return f"Error: Prompt was blocked by the API. Details: {e}"

        except genai.types.generation_types.StopCandidateException as e:
            print(f"Gemini Error: All candidates stopped. Details: {e}")
            if e.response.candidates and e.response.candidates[0].finish_reason:
                reason_name = getattr(e.response.candidates[0].finish_reason, "name", "UNKNOWN")
                return f"Generation stopped (StopCandidateException). Reason: {reason_name}"
            return f"Error: All candidates were stopped. {e}"

        except Exception as e:
            print(f"Unexpected Gemini error: {type(e).__name__} - {e}")
            return f"Unexpected Gemini error: {type(e).__name__} - {str(e)}"
