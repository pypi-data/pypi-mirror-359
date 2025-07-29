import time
import traceback
from typing import Any, Callable

import httpx
from pydantic_ai.agent import Agent
from pydantic_ai.settings import ModelSettings
from pydantic_ai.usage import Usage

from agent_tools._log import log


class AgentRunner:
    """
    AgentRunner is a class that
    1. keep model settings.
    2. runs an agent and returns the result.
    3. keep attempts, usage, and time_elapsed.
    """

    def __init__(
        self,
        elapsed_time: float = 0.0,
        attempts: int = 0,
        usage: Usage = Usage(),
        model_settings: ModelSettings = ModelSettings(),
    ):
        self.elapsed_time = elapsed_time
        self.attempts = attempts
        self.model_settings = model_settings
        self.usage = usage
        self.result: Any | None = None

    def _raise_error(self, e: Exception, start_time: float):
        self.attempts = self.attempts + 1
        self.elapsed_time += time.perf_counter() - start_time
        log.error(f'AgentRunner failed: {self.attempts} attempts: {traceback.format_exc()}')
        raise e

    async def run(
        self,
        agent: Agent[Any, str],
        prompt: str,
        postprocess_fn: Callable[[str], str] | None = None,
        **kwargs: Any,
    ) -> None:
        start_time = time.perf_counter()
        try:
            result = await agent.run(
                prompt,
                model_settings=self.model_settings,
            )
            self.usage += result.usage()
            self.elapsed_time += time.perf_counter() - start_time
            self.result = result.output
        except Exception as e:
            self._raise_error(e, start_time)

        if postprocess_fn and self.result is not None:
            try:
                self.result = postprocess_fn(self.result, **kwargs)
            except Exception as e:
                self._raise_error(e, start_time)

    async def run_stream(
        self,
        agent: Agent[Any, str],
        prompt: str,
        postprocess_fn: Callable[[str], str] | None = None,
        **kwargs: Any,
    ) -> None:
        start_time = time.perf_counter()
        try:
            async with agent.run_stream(
                prompt,
                model_settings=self.model_settings,
            ) as result:
                async for message in result.stream_text(debounce_by=1):
                    self.result = message
            self.usage += result.usage()
            self.elapsed_time += time.perf_counter() - start_time
        except Exception as e:
            self._raise_error(e, start_time)

        if postprocess_fn and self.result is not None:
            try:
                self.result = postprocess_fn(self.result, **kwargs)
            except Exception as e:
                self._raise_error(e, start_time)

    async def embedding(
        self,
        client: Any,
        model_name: str,
        input: str,
        dimensions: int = 1024,
    ) -> None:
        start_time = time.perf_counter()
        try:
            response = await client.embeddings.create(
                model=model_name,
                input=input,
                dimensions=dimensions,
            )
            self.usage += response.usage()
            self.elapsed_time = self.elapsed_time + (time.perf_counter() - start_time)
            self.result = response.data[0].embedding
        except Exception as e:
            self._raise_error(e, start_time)

    async def run_api(
        self,
        api_url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
    ) -> None:
        """
        Not implemented yet.
        """
        start_time = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=600) as client:
                response = await client.post(api_url, headers=headers, json=payload)
                response.raise_for_status()
                self.result = response.json()
                self.usage += response.json()["usage"]
                self.elapsed_time = self.elapsed_time + (time.perf_counter() - start_time)
        except Exception as e:
            self._raise_error(e, start_time)
