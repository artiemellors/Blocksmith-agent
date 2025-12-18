"""
Base Agent class for Blocksmith agents.
Provides common functionality for all specialist agents.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from anthropic import Anthropic
import time


class BaseAgent(ABC):
    """Base class for all Blocksmith agents."""

    def __init__(self, client: Anthropic, model_name: str = "claude-sonnet-4-5-20250929"):
        """
        Initialize the base agent.

        Args:
            client: Anthropic API client
            model_name: Claude model to use
        """
        self.client = client
        self.model_name = model_name
        self.outputs: Dict[str, str] = {}

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt that defines this agent's role and expertise.
        Must be implemented by subclasses.

        Returns:
            System prompt string
        """
        pass

    @abstractmethod
    def get_agent_name(self) -> str:
        """
        Get the name of this agent.
        Must be implemented by subclasses.

        Returns:
            Agent name string
        """
        pass

    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        max_tokens: int = 16000,
        temperature: float = 1.0
    ) -> str:
        """
        Generate content using this agent.

        Args:
            prompt: The specific task prompt for this generation
            context: Optional context from previous agents/layers
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated content
        """
        print(f"\n{'='*60}")
        print(f"{self.get_agent_name()} working...")
        print(f"{'='*60}\n")

        # Build the full prompt with context if provided
        full_prompt = prompt
        if context:
            full_prompt = f"# Context from Previous Stages\n\n{context}\n\n---\n\n# Your Task\n\n{prompt}"

        # Get system prompt
        system_prompt = self.get_system_prompt()

        try:
            # Call Claude API
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )

            output = message.content[0].text

            # Store output
            self.outputs[prompt[:50]] = output

            print(f"✓ {self.get_agent_name()} completed")

            # Rate limiting delay (3 seconds to be safe with API limits)
            time.sleep(3)

            return output

        except Exception as e:
            print(f"✗ Error in {self.get_agent_name()}: {str(e)}")
            raise

    def get_output(self, key: str) -> Optional[str]:
        """Get a stored output by key."""
        return self.outputs.get(key)

    def clear_outputs(self):
        """Clear all stored outputs."""
        self.outputs.clear()
