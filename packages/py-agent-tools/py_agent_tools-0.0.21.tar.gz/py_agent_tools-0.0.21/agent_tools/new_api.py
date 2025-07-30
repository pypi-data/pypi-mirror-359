"""
Not implemented yet.
"""

import asyncio
import json
from typing import Any

from pydantic_ai.settings import ModelSettings

from agent_tools.agent_base import ModelNameBase
from agent_tools.agent_runner import AgentRunner
from agent_tools.api_base import APIBase
from agent_tools.settings import agent_settings


class NewAPIModelName(ModelNameBase):
    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_2_5_PRO_THINKING = "gemini-2.5-pro-thinking"


class NewAPIGenmini(APIBase):
    @property
    def base_url(self) -> str:
        return agent_settings.new_api.base_url

    @property
    def api_key(self) -> str:
        return agent_settings.new_api.key

    async def run(
        self,
        prompt: str,
        model_settings: ModelSettings = ModelSettings(),
    ) -> AgentRunner:
        """
        TODO: Retry
        """
        url = f"{self.base_url}/v1beta/models/{self.model_name}:generateContent"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        contents = []
        if self.system_prompt:
            contents.append({"role": "system", "parts": [{"text": self.system_prompt}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        # Prepare the request payload
        payload: dict[str, Any] = {"contents": contents}
        payload["generationConfig"] = model_settings

        await self.runner.run_api(
            api_url=url,
            headers=headers,
            payload=payload,
        )
        return self.runner


if __name__ == "__main__":

    async def test_api():
        gemini = NewAPIGenmini(
            NewAPIModelName.GEMINI_2_5_FLASH,
            # system_prompt="You are a helpful assistant.",
        )
        try:
            runner = await gemini.run("Write a story about a magic backpack.")
            print("Response:", json.dumps(runner.result, indent=2))
        except Exception as e:
            print(f"Error: {e}")

    # Run the test if API key is available
    if agent_settings.new_api.key:
        asyncio.run(test_api())
    else:
        print("No API key found. Set NEW_API_KEY environment variable.")
