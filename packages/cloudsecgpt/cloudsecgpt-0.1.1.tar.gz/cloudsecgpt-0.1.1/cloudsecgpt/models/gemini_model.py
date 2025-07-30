import os
import sys
from typing import Any, Dict, List

import google.generativeai as genai

from cloudsecgpt.utils.cache import make_cache_path
from cloudsecgpt.utils.console import console


class GeminiModel:
    """
    Google Gemini client with on-disk caching.
    Uses the Google Generative AI Python SDK.
    """

    def __init__(self, model_name: str, namespace: str):
        try:
            # Configure the API key
            api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise RuntimeError(
                    "GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set"
                )

            genai.configure(api_key=api_key)

            # Initialize the model
            self.model = genai.GenerativeModel(model_name)
            self.model_name = model_name
            self.namespace = namespace
        except Exception as e:
            console.log(f"[red]GeminiModel error: {e}[/red]")
            sys.exit(1)

    def call(self, messages: List[Dict[str, Any]]) -> str:
        """
        Send 'messages' to the Gemini API and return the response text.
        Caches results to avoid duplicate calls.
        """
        try:
            prompt_str = str(messages)
            cache_path = make_cache_path(
                namespace=self.namespace,
                provider="gemini",
                model=self.model_name,
                prompt=prompt_str,
            )
            # Return cached response if available
            if cache_path.exists():
                return cache_path.read_text()

            try:
                # Convert OpenAI-style messages to Gemini format
                gemini_messages = self._convert_messages(messages)

                # Generate content
                response = self.model.generate_content(gemini_messages)

                # Extract the text response
                if response.text:
                    text = response.text
                else:
                    console.log("[red]Gemini returned empty response[/red]")
                    text = ""

            except Exception as e:
                console.log(f"[red]Gemini API error: {e}[/red]")
                return ""

            cache_path.write_text(text)
            return text
        except Exception as e:
            console.log(f"[red]GeminiModel error: {e}[/red]")
            sys.exit(1)

    def _convert_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert OpenAI-style messages to Gemini format.
        Gemini uses 'role' and 'parts' structure.
        """
        gemini_messages = []

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            # Map OpenAI roles to Gemini roles
            if role == "system":
                # Gemini doesn't have a system role, so we'll prepend to user messages
                # For now, we'll treat system messages as user messages
                role = "user"
            elif role == "assistant":
                role = "model"
            elif role == "user":
                role = "user"

            gemini_messages.append({"role": role, "parts": [{"text": content}]})

        return gemini_messages
