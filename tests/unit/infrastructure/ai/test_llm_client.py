from types import SimpleNamespace

import pytest

from infrastructure.ai.llm_client import LLMClient
from infrastructure.ai.providers.mock_provider import MockProvider


class _CapturingProvider:
    def __init__(self):
        self.prompt = None

    async def generate(self, prompt, config):
        self.prompt = prompt
        return SimpleNamespace(content="ok")


@pytest.mark.asyncio
async def test_generate_forwards_custom_system_prompt():
    provider = _CapturingProvider()
    client = LLMClient(provider=provider)

    result = await client.generate("user prompt", system_prompt="market analyst")

    assert result == "ok"
    assert provider.prompt.system == "market analyst"
    assert provider.prompt.user == "user prompt"


@pytest.mark.asyncio
async def test_generate_can_require_a_real_provider():
    client = LLMClient(provider=MockProvider())

    with pytest.raises(RuntimeError, match="真实 LLM"):
        await client.generate("market prompt", require_real_provider=True)
