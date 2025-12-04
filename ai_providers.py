"""
AI Provider abstraction layer.
Supports Anthropic (Claude), OpenAI (GPT), and Google (Gemini).
"""
import os
from typing import Optional
from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai


class AIProvider:
    """Base class for AI providers."""

    def __init__(self, model_name: str, max_tokens: int, temperature: float):
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature

    def generate(self, prompt: str) -> str:
        """Generate text from prompt. Override in subclasses."""
        raise NotImplementedError


class AnthropicProvider(AIProvider):
    """Anthropic (Claude) provider."""

    def __init__(self, model_name: str, max_tokens: int, temperature: float, api_key: str):
        super().__init__(model_name, max_tokens, temperature)
        self.client = Anthropic(api_key=api_key)

    def generate(self, prompt: str) -> str:
        message = self.client.messages.create(
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text


class OpenAIProvider(AIProvider):
    """OpenAI (GPT) provider."""

    def __init__(self, model_name: str, max_tokens: int, temperature: float, api_key: str):
        super().__init__(model_name, max_tokens, temperature)
        self.client = OpenAI(api_key=api_key)

    def generate(self, prompt: str) -> str:
        message = self.client.chat.completions.create(
            model=self.model_name,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.choices[0].message.content


class GeminiProvider(AIProvider):
    """Google (Gemini) provider."""

    def __init__(self, model_name: str, max_tokens: int, temperature: float, api_key: str):
        super().__init__(model_name, max_tokens, temperature)
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model_name)

    def generate(self, prompt: str) -> str:
        response = self.client.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=self.max_tokens,
                temperature=self.temperature,
            )
        )
        return response.text


def get_provider(
    provider_name: str,
    model_name: str,
    max_tokens: int,
    temperature: float,
    api_key: Optional[str] = None
) -> AIProvider:
    """
    Factory function to get the appropriate AI provider.

    Args:
        provider_name: "anthropic", "openai", or "gemini"
        model_name: Model to use
        max_tokens: Maximum tokens in response
        temperature: Temperature for generation
        api_key: API key (if None, will try to get from environment)

    Returns:
        AIProvider instance

    Raises:
        ValueError: If provider is unknown or API key is missing
    """
    # Get API key from environment if not provided
    if api_key is None:
        if provider_name == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
        elif provider_name == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
        elif provider_name == "gemini":
            api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise ValueError(
                f"No API key found for {provider_name}. "
                f"Set {provider_name.upper()}_API_KEY environment variable."
            )

    # Create provider
    if provider_name == "anthropic":
        return AnthropicProvider(model_name, max_tokens, temperature, api_key)
    elif provider_name == "openai":
        return OpenAIProvider(model_name, max_tokens, temperature, api_key)
    elif provider_name == "gemini":
        return GeminiProvider(model_name, max_tokens, temperature, api_key)
    else:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Must be 'anthropic', 'openai', or 'gemini'"
        )
