"""LLM provider unified interface.

各厂商 API 说明：
- OpenAI:    https://platform.openai.com/docs  — ChatOpenAI, base_url 默认
- Anthropic: https://docs.anthropic.com       — ChatAnthropic, model: claude-3-5-sonnet-20241022
- DeepSeek:  https://platform.deepseek.com   — OpenAI 兼容, base_url: https://api.deepseek.com
- Gemini:    https://ai.google.dev/gemini-api — OpenAI 兼容接口, base_url: https://generativelanguage.googleapis.com/v1beta/openai/
- Ollama:    https://ollama.com               — 本地部署, 无需 API key
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from e2sc.utils import get_logger

logger = get_logger(__name__)


class LLMProvider(ABC):
    """Base class for LLM providers."""

    def __init__(self, api_key: str, model: str, temperature: float = 0.7, max_tokens: int = 81920):  # 81920 = half of 163840
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self._max_tokens = max_tokens
        self._reasoner_mode = False
        self.llm = self._initialize_llm()

    @property
    def max_tokens(self) -> int:
        return self._max_tokens

    @max_tokens.setter
    def max_tokens(self, value: int):
        """Update max_tokens and propagate to the underlying LangChain LLM object."""
        self._max_tokens = value
        if hasattr(self, 'llm') and self.llm is not None:
            # LangChain ChatOpenAI / ChatAnthropic expose max_tokens directly
            try:
                self.llm.max_tokens = value
            except Exception:
                pass

    @property
    def reasoner_mode(self) -> bool:
        return self._reasoner_mode

    @reasoner_mode.setter
    def reasoner_mode(self, value: bool):
        """Enable/disable reasoner mode (DeepSeek-R1 / o3-mini etc.)."""
        self._reasoner_mode = value

    @abstractmethod
    def _initialize_llm(self) -> Any:
        """Initialize the LLM client."""
        pass

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat messages and get response."""
        langchain_messages = self._convert_messages(messages)
        if self._reasoner_mode:
            kwargs.setdefault('reasoning_effort', 'high')
        response = self.llm.invoke(langchain_messages, **kwargs)
        return response.content

    def stream_chat(self, messages: List[Dict[str, str]], **kwargs):
        """Stream chat response."""
        langchain_messages = self._convert_messages(messages)
        if self._reasoner_mode:
            kwargs.setdefault('reasoning_effort', 'high')
        for chunk in self.llm.stream(langchain_messages, **kwargs):
            yield chunk.content

    def test_connection(self) -> Dict[str, Any]:
        """发送一条最小请求测试连通性，返回 {success, message, model}。"""
        try:
            reply = self.chat([
                {"role": "user", "content": "Reply with the single word: OK"}
            ])
            return {"success": True, "message": f"连接成功，模型回复: {reply.strip()[:50]}", "model": self.model}
        except Exception as e:
            return {"success": False, "message": str(e), "model": self.model}

    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[BaseMessage]:
        """Convert message dicts to LangChain messages."""
        result = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                result.append(SystemMessage(content=content))
            elif role == "assistant":
                result.append(AIMessage(content=content))
            else:
                result.append(HumanMessage(content=content))
        return result


class OpenAIProvider(LLMProvider):
    """OpenAI LLM provider.

    官方文档: https://platform.openai.com/docs/api-reference
    支持模型: gpt-5.4, gpt-5, gpt-4o, gpt-4o-mini, gpt-4-turbo
    API Key:  https://platform.openai.com/api-keys
    """

    def _initialize_llm(self):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )


class AnthropicProvider(LLMProvider):
    """Anthropic (Claude) LLM provider.

    官方文档: https://docs.anthropic.com/en/api/getting-started
    支持模型: claude-opus-4-7, claude-sonnet-4-6, claude-haiku-4-5
    API Key:  https://console.anthropic.com/settings/keys
    """

    def _initialize_llm(self):
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )


class DeepSeekProvider(LLMProvider):
    """DeepSeek LLM provider (OpenAI 兼容接口).

    官方文档: https://platform.deepseek.com/api-docs
    base_url:  https://api.deepseek.com
    支持模型: deepseek-v4-flash, deepseek-v4-pro
    API Key:  https://platform.deepseek.com/api_keys
    注意: deepseek-chat 和 deepseek-reasoner 已废弃(2026-07-24停用), 请使用新版模型
    注意: base_url 不带 /v1，langchain-openai SDK 会自动补全
          deepseek-reasoner 会输出 <think> 标签，已自动过滤
    """

    def _initialize_llm(self):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            base_url="https://api.deepseek.com",
        )

    def chat(self, messages, **kwargs):
        """Chat with thinking token stripped."""
        import re
        response = super().chat(messages, **kwargs)
        response = re.sub(r'<think>[\s\S]*?</think>\s*', '', response).strip()
        return response

    def stream_chat(self, messages, **kwargs):
        """Stream chat with thinking tokens filtered out."""
        import re
        in_think = False
        buf = ''
        for chunk in super().stream_chat(messages, **kwargs):
            buf += chunk
            while True:
                if in_think:
                    end = buf.find('</think>')
                    if end != -1:
                        buf = buf[end + len('</think>'):].lstrip('\n')
                        in_think = False
                    else:
                        buf = ''
                        break
                else:
                    start = buf.find('<think>')
                    if start != -1:
                        if start > 0:
                            yield buf[:start]
                        buf = buf[start + len('<think>'):]
                        in_think = True
                    else:
                        if len(buf) > 7:
                            yield buf[:-7]
                            buf = buf[-7:]
                        break
        if buf and not in_think:
            buf = re.sub(r'<think>[\s\S]*?</think>\s*', '', buf)
            if buf:
                yield buf


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider (OpenAI 兼容接口).

    官方文档: https://ai.google.dev/gemini-api/docs/openai
    base_url:  https://generativelanguage.googleapis.com/v1beta/openai/
    支持模型: gemini-2.0-flash, gemini-1.5-flash, gemini-1.5-pro
    API Key:  https://aistudio.google.com/app/apikey
    """

    def _initialize_llm(self):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )


class SiliconFlowProvider(LLMProvider):
    """硅基流动 LLM provider (OpenAI 兼容接口).

    官方文档: https://docs.siliconflow.cn/cn/api-reference
    base_url:  https://api.siliconflow.cn/v1
    支持模型: Qwen/Qwen2.5-72B-Instruct, THUDM/glm-4-9b-chat,
              deepseek-ai/DeepSeek-V3, deepseek-ai/DeepSeek-R1,
              Pro/Qwen/Qwen2.5-72B-Instruct, 等
    API Key:  https://cloud.siliconflow.cn/account/ak
    注意: thinking/reasoning token 已在 stream_chat/chat 中自动过滤
    """

    def _initialize_llm(self):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            base_url="https://api.siliconflow.cn/v1",
        )

    def chat(self, messages, **kwargs):
        """Chat with thinking token stripped."""
        import re
        response = super().chat(messages, **kwargs)
        # Strip <think>...</think> blocks from reasoner models
        response = re.sub(r'<think>[\s\S]*?</think>\s*', '', response).strip()
        return response

    def stream_chat(self, messages, **kwargs):
        """Stream chat with thinking tokens filtered out."""
        import re
        in_think = False
        buf = ''
        for chunk in super().stream_chat(messages, **kwargs):
            buf += chunk
            while True:
                if in_think:
                    end = buf.find('</think>')
                    if end != -1:
                        buf = buf[end + len('</think>'):].lstrip('\n')
                        in_think = False
                    else:
                        buf = ''
                        break
                else:
                    start = buf.find('<think>')
                    if start != -1:
                        if start > 0:
                            yield buf[:start]
                        buf = buf[start + len('<think>'):]
                        in_think = True
                    else:
                        # No think tag, yield all but last 6 chars (guard against split tags)
                        if len(buf) > 7:
                            yield buf[:-7]
                            buf = buf[-7:]
                        break
        if buf and not in_think:
            # Filter any residual think tags
            buf = re.sub(r'<think>[\s\S]*?</think>\s*', '', buf)
            if buf:
                yield buf


class OllamaProvider(LLMProvider):
    """Ollama 本地 LLM provider.

    官方文档: https://github.com/ollama/ollama
    无需 API key，需本地运行: ollama serve
    支持模型: llama3.2, mistral, qwen2.5, deepseek-r1 等
    """

    def _initialize_llm(self):
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            from langchain_community.chat_models import ChatOllama
        return ChatOllama(
            model=self.model,
            temperature=self.temperature,
        )


class GLMProvider(LLMProvider):
    """Zhipu AI (GLM) API provider.

    官方文档: https://docs.bigmodel.cn
    API endpoint: https://open.bigmodel.cn/api/paas/v4/chat/completions
    支持模型: GLM-5, GLM-5.1, GLM-4-Plus, GLM-4, GLM-Z1 (推理) 等
    """

    def _initialize_llm(self):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=self.model,
            openai_api_key=self.api_key,
            openai_api_base="https://open.bigmodel.cn/api/paas/v4/",
            temperature=self.temperature,
        )


class KimiProvider(LLMProvider):
    """Moonshot AI (Kimi) API provider.

    官方文档: https://platform.kimi.com/docs/api/overview
    API endpoint: https://api.moonshot.cn/v1/chat/completions
    支持模型: kimi-k2.6, moonshot-v2.5-250415, moonshot-v1.5-32k 等
    API Key: https://platform.kimi.com/console/api-keys
    """

    def _initialize_llm(self):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            base_url="https://api.moonshot.cn/v1",
        )


# 所有支持的 provider 映射
_PROVIDERS: Dict[str, type] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "deepseek": DeepSeekProvider,
    "gemini": GeminiProvider,
    "siliconflow": SiliconFlowProvider,
    "glm": GLMProvider,
    "kimi": KimiProvider,
    "ollama": OllamaProvider,
}

# 各 provider 的默认模型 + 推荐模型列表（2026-04 最新）
_DEFAULT_MODELS: Dict[str, str] = {
    "openai":      "gpt-5.5",
    "anthropic":   "claude-sonnet-4-6",
    "deepseek":    "deepseek-v4-flash",
    "gemini":      "gemini-3.1-pro-preview",
    "siliconflow": "deepseek-ai/DeepSeek-V3",
    "glm":         "glm-5.1",
    "kimi":        "kimi-k2.6",
    "ollama":      "llama3.2",
}

# 推荐模型列表（供前端展示，用户可从API动态获取完整列表）
_RECOMMENDED_MODELS: Dict[str, list] = {
    "openai": [
        "gpt-5.5",
        "gpt-5.5-pro",
        "gpt-5.1",
        "gpt-5.2",
        "gpt-5.3-chat-latest",
        "gpt-4o",
    ],
    "anthropic": [
        "claude-sonnet-4-6",
        "claude-opus-4-7",
        "claude-haiku-4-5",
    ],
    "deepseek": [
        "deepseek-v4-flash",
        "deepseek-v4-pro",
    ],
    "gemini": [
        "gemini-3.1-pro-preview",
        "gemini-3-flash-preview",
        "gemini-3.1-flash-lite-preview",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
    ],
    "siliconflow": [
        "deepseek-ai/DeepSeek-V3",
        "deepseek-ai/DeepSeek-R1",
        "Qwen/Qwen2.5-72B-Instruct",
    ],
    "glm": [
        "glm-5.1",
        "glm-4-Plus",
        "glm-4",
    ],
    "kimi": [
        "kimi-k2.6",
        "moonshot-v2.5-250415",
    ],
    "ollama": [
        "llama3.2",
        "qwen2.5",
        "deepseek-r1",
    ],
}


def create_llm_provider(
    provider: str,
    api_key: str = "",
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 81920,
) -> LLMProvider:
    """Factory function to create LLM provider.

    Args:
        provider:    Provider name (openai, anthropic, deepseek, gemini, siliconflow, glm, ollama)
        api_key:     明文 API key（server 层传入前已解密）
        model:       Model name，为空时使用各 provider 默认模型
        temperature: 生成温度
        max_tokens:  最大 token 数

    Returns:
        LLMProvider instance

    Raises:
        ValueError: 不支持的 provider
    """
    provider_lower = provider.lower()

    if provider_lower not in _PROVIDERS:
        raise ValueError(
            f"不支持的 provider: '{provider}'。"
            f"支持的 provider: {list(_PROVIDERS.keys())}"
        )

    resolved_model = model or _DEFAULT_MODELS[provider_lower]
    logger.info(f"创建 LLM provider: {provider_lower}, model: {resolved_model}")
    return _PROVIDERS[provider_lower](api_key, resolved_model, temperature, max_tokens)


def get_supported_providers() -> Dict[str, Dict[str, Any]]:
    """返回所有支持的 provider 及其默认模型和推荐模型列表。"""
    return {
        name: {
            "default_model": _DEFAULT_MODELS[name],
            "recommended_models": _RECOMMENDED_MODELS.get(name, []),
        }
        for name in _PROVIDERS
    }
