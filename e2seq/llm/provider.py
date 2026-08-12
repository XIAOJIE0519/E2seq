"""LLM provider unified interface.

各厂商 API 说明：
- OpenAI:    https://platform.openai.com/docs  — ChatOpenAI, base_url 默认
- Anthropic: https://docs.anthropic.com       — ChatAnthropic, model: claude-3-5-sonnet-20241022
- DeepSeek:  https://platform.deepseek.com   — OpenAI 兼容, base_url: https://api.deepseek.com
- Gemini:    https://ai.google.dev/gemini-api — OpenAI 兼容接口, base_url: https://generativelanguage.googleapis.com/v1beta/openai/
- Ollama:    https://ollama.com               — 本地部署, 无需 API key
"""

from abc import ABC, abstractmethod
import threading
import time
from typing import Any, Dict, List, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from e2seq.utils import get_logger

logger = get_logger(__name__)


class LLMProvider(ABC):
    """Base class for LLM providers.

    Thinking / reasoning support is a first-class concept: every provider has
    its own way of enabling the model's chain-of-thought mode (OpenAI uses
    ``reasoning_effort``, Anthropic uses ``thinking`` + ``output_config.effort``,
    DeepSeek uses ``extra_body={"thinking": {...}}`` etc.). Each subclass
    overrides ``_thinking_kwargs(enabled, effort)`` to translate the abstract
    "do thinking at this effort" intent into the provider-specific request
    payload. The base ``chat()`` and ``stream_chat()`` then inject those kwargs
    automatically — callers don't need to know the provider's dialect.

    Effort values are normalised to ``low|medium|high|max``. Subclasses can
    override ``_normalize_effort`` to translate to their enum (e.g. GLM has
    ``none|minimal|low|medium|high|xhigh|max`` and Anthropic uses the same set).
    """

    # Capability flags the frontend uses to show / hide the Thinking toggle.
    # Override per subclass. ``supports_thinking=True`` means the provider
    # can pass an explicit thinking switch; ``effort_levels`` is the list of
    # values the UI should offer in the dropdown.
    supports_thinking: bool = False
    effort_levels: tuple = ()            # type: ignore[var-annotated]
    # When True, ``reasoning_effort`` (or its provider alias) is included in
    # every request even if the user didn't explicitly toggle thinking. This
    # is the right behaviour for "always-think" models like Claude Opus 4.7+.
    thinking_always_on: bool = False
    # A stable name for the request dialect used by the capability registry.
    # Subclasses may override ``thinking_parameter_for_model`` when a provider
    # has more than one dialect (for example SiliconFlow Qwen3).
    thinking_parameter: str = "none"

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 81920,
        thinking_enabled: bool = False,
        thinking_effort: str = "high",
        base_url: Optional[str] = None,
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self._max_tokens = max_tokens
        # Keep the legacy ``_reasoner_mode`` flag as a synonym for
        # ``thinking_enabled`` so old call sites that still poke
        # ``provider.reasoner_mode = True`` keep working.
        self._reasoner_mode = bool(thinking_enabled)
        self._thinking_enabled = bool(thinking_enabled)
        self._thinking_effort = thinking_effort or "high"
        # Optional custom base URL (any OpenAI/Anthropic/Gemini-compatible
        # proxy such as a6api, OpenRouter, etc.). When None, subclass defaults apply.
        self.base_url = (base_url or "").strip() or None
        # Keep request-level telemetry on the provider instance so one answer
        # can report exactly which model/API was used, how long the model calls
        # took, and how many tokens the provider actually returned.  Some
        # gateways omit usage metadata; those requests are counted but marked
        # unavailable instead of being guessed.
        self._usage_lock = threading.Lock()
        self._usage_totals = {
            "requests": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "reasoning_tokens": 0,
            "usage_reports": 0,
            "latency_seconds": 0.0,
        }
        self._last_usage = {}
        self.llm = self._initialize_llm()

    @staticmethod
    def _coerce_token_count(value: Any) -> Optional[int]:
        """Convert a provider usage value to an integer when possible."""
        if value is None or isinstance(value, bool):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _extract_usage(self, response: Any) -> Dict[str, Any]:
        """Read token usage from common LangChain/OpenAI-compatible shapes."""
        usage = getattr(response, "usage_metadata", None) or {}
        metadata = getattr(response, "response_metadata", None) or {}
        token_usage = metadata.get("token_usage") or metadata.get("usage") or {}
        if not isinstance(usage, dict):
            usage = {}
        if not isinstance(metadata, dict):
            metadata = {}
        if not isinstance(token_usage, dict):
            token_usage = {}

        def first(*values: Any) -> Optional[int]:
            for value in values:
                converted = self._coerce_token_count(value)
                if converted is not None:
                    return converted
            return None

        input_details = usage.get("input_token_details") or {}
        output_details = usage.get("output_token_details") or {}
        completion_details = token_usage.get("completion_tokens_details") or {}
        if not isinstance(input_details, dict):
            input_details = {}
        if not isinstance(output_details, dict):
            output_details = {}
        if not isinstance(completion_details, dict):
            completion_details = {}

        prompt_tokens = first(
            usage.get("input_tokens"), usage.get("prompt_tokens"),
            token_usage.get("prompt_tokens"), token_usage.get("input_tokens"),
        )
        completion_tokens = first(
            usage.get("output_tokens"), usage.get("completion_tokens"),
            token_usage.get("completion_tokens"), token_usage.get("output_tokens"),
        )
        total_tokens = first(
            usage.get("total_tokens"), token_usage.get("total_tokens"),
        )
        reasoning_tokens = first(
            output_details.get("reasoning"), output_details.get("reasoning_tokens"),
            completion_details.get("reasoning_tokens"),
            token_usage.get("reasoning_tokens"),
        )
        if total_tokens is None and prompt_tokens is not None and completion_tokens is not None:
            total_tokens = prompt_tokens + completion_tokens

        return {
            "prompt_tokens": prompt_tokens or 0,
            "completion_tokens": completion_tokens or 0,
            "total_tokens": total_tokens or 0,
            "reasoning_tokens": reasoning_tokens or 0,
            "usage_available": any(
                value is not None
                for value in (prompt_tokens, completion_tokens, total_tokens, reasoning_tokens)
            ),
        }

    def _record_usage(self, response: Any, elapsed_seconds: Optional[float] = None) -> None:
        """Accumulate one completed model call without exposing credentials."""
        usage = self._extract_usage(response)
        latency = max(0.0, float(elapsed_seconds or 0.0))
        record = {
            "prompt_tokens": int(usage["prompt_tokens"]),
            "completion_tokens": int(usage["completion_tokens"]),
            "total_tokens": int(usage["total_tokens"]),
            "reasoning_tokens": int(usage["reasoning_tokens"]),
            "usage_available": bool(usage["usage_available"]),
            "latency_seconds": round(latency, 3),
        }
        with self._usage_lock:
            self._usage_totals["requests"] += 1
            for key in ("prompt_tokens", "completion_tokens", "total_tokens", "reasoning_tokens"):
                self._usage_totals[key] += record[key]
            if record["usage_available"]:
                self._usage_totals["usage_reports"] += 1
            self._usage_totals["latency_seconds"] += latency
            self._last_usage = dict(record)

    def usage_snapshot(self) -> Dict[str, Any]:
        """Return a copy of provider telemetry suitable for delta accounting."""
        with self._usage_lock:
            return dict(self._usage_totals)

    def usage_delta(self, before: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Return usage accumulated since ``before`` (or for this provider)."""
        before = before or {}
        current = self.usage_snapshot()
        delta_reports = max(0, int(current.get("usage_reports", 0)) - int(before.get("usage_reports", 0)))
        return {
            "requests": max(0, int(current.get("requests", 0)) - int(before.get("requests", 0))),
            "prompt_tokens": max(0, int(current.get("prompt_tokens", 0)) - int(before.get("prompt_tokens", 0))),
            "completion_tokens": max(0, int(current.get("completion_tokens", 0)) - int(before.get("completion_tokens", 0))),
            "total_tokens": max(0, int(current.get("total_tokens", 0)) - int(before.get("total_tokens", 0))),
            "reasoning_tokens": max(0, int(current.get("reasoning_tokens", 0)) - int(before.get("reasoning_tokens", 0))),
            "token_usage_available": bool(delta_reports),
            "latency_seconds": round(max(
                0.0,
                float(current.get("latency_seconds", 0.0)) - float(before.get("latency_seconds", 0.0)),
            ), 3),
        }

    @property
    def max_tokens(self) -> int:
        return self._max_tokens

    @max_tokens.setter
    def max_tokens(self, value: int):
        """Update max_tokens and propagate to the underlying LangChain LLM object."""
        self._max_tokens = value
        if hasattr(self, 'llm') and self.llm is not None:
            try:
                self.llm.max_tokens = value
            except Exception:
                pass

    @property
    def reasoner_mode(self) -> bool:
        return self._thinking_enabled

    @reasoner_mode.setter
    def reasoner_mode(self, value: bool):
        """Backwards-compat setter; also enables thinking."""
        self.set_thinking(bool(value), self._thinking_effort)

    @property
    def thinking_enabled(self) -> bool:
        return self._thinking_enabled

    @property
    def thinking_effort(self) -> str:
        return self._thinking_effort

    def set_thinking(self, enabled: bool, effort: str = "high") -> None:
        """Enable/disable chain-of-thought reasoning for this provider.

        Subclasses that need to reinitialise their LangChain client when
        thinking toggles (because the parameter is set at construction time,
        not per-request) override ``_apply_thinking_to_client`` instead of
        doing the work here.
        """
        self._thinking_enabled = bool(enabled)
        self._thinking_effort = self._normalize_effort(effort)
        self._reasoner_mode = self._thinking_enabled
        self._apply_thinking_to_client()

    def _normalize_effort(self, effort: str) -> str:
        """Map an abstract effort value to this provider's enum.

        Default: accept the common subset ``low|medium|high|max`` verbatim.
        Subclasses can expand / translate (e.g. GLM has ``xhigh`` and
        Anthropic has ``none|minimal``).
        """
        e = (effort or "").lower()
        if e in {"low", "medium", "high", "max"}:
            return e
        return "high"

    def _apply_thinking_to_client(self) -> None:
        """Hook for subclasses that set thinking parameters at construction.

        Default: nothing to do — thinking is passed per-request in
        ``_thinking_kwargs``. Subclasses that store thinking on the LangChain
        client (e.g. by passing it to ``ChatOpenAI(..., extra_body=...)``)
        override this and call ``self.llm = self._initialize_llm()`` to
        rebuild the client with the new parameters.
        """

    def _thinking_kwargs(self) -> Dict[str, Any]:
        """Translate the abstract thinking intent into provider kwargs.

        Returns the kwargs dict to merge into every ``invoke`` / ``stream``
        call. Base implementation: do nothing (provider doesn't support
        thinking). Subclasses override.
        """
        return {}

    @abstractmethod
    def _initialize_llm(self) -> Any:
        """Initialize the LLM client."""
        pass

    def _invoke_kwargs(self, **kwargs) -> Dict[str, Any]:
        """Merge provider-specific thinking kwargs into the call kwargs."""
        # Ask every thinking-capable provider for its explicit off payload as
        # well as its on payload.  This matters for models whose server-side
        # default is thinking-enabled (for example DeepSeek V4): merely
        # omitting the parameter does not reliably disable reasoning.
        if self.supports_thinking:
            for k, v in self._thinking_kwargs().items():
                kwargs.setdefault(k, v)
        return kwargs

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat messages and get response."""
        from langchain_core.messages import convert_to_messages  # noqa: F401  (ensures dep present)
        langchain_messages = self._convert_messages(messages)
        kwargs = self._invoke_kwargs(**kwargs)
        started = time.perf_counter()
        response = self.llm.invoke(langchain_messages, **kwargs)
        self._record_usage(response, time.perf_counter() - started)
        return response.content

    def stream_chat(self, messages: List[Dict[str, str]], **kwargs):
        """Stream chat response."""
        langchain_messages = self._convert_messages(messages)
        kwargs = self._invoke_kwargs(**kwargs)
        started = time.perf_counter()
        last_chunk = None
        usage_chunk = None
        try:
            for chunk in self.llm.stream(langchain_messages, **kwargs):
                last_chunk = chunk
                if getattr(chunk, "usage_metadata", None) or getattr(chunk, "response_metadata", None):
                    usage_chunk = chunk
                content = getattr(chunk, "content", "") or ""
                if content:
                    yield content
        finally:
            if usage_chunk is not None or last_chunk is not None:
                self._record_usage(usage_chunk or last_chunk, time.perf_counter() - started)

    def test_connection(self) -> Dict[str, Any]:
        """Verify API key + model exist by listing available models.

        We deliberately do NOT send an actual chat completion here, because:
        1. Reasoner models (GLM-5.2, DeepSeek-R1, o3-mini) take 10-30s just to
           emit thinking tokens before answering "OK", which makes the test
           look like it timed out.
        2. Some models require special parameters (e.g. GLM-5.2 needs thinking
           enabled) that the generic test prompt can't satisfy.
        3. The model existence + key validity is enough to know the model is
           selectable. The real chat will reveal any model-side issue anyway.

        Subclasses override this if their provider has a cheaper validation API.
        """
        try:
            import urllib.request
            import urllib.error
            url = self._models_list_url()
            req = urllib.request.Request(url, method="GET")
            req.add_header("Authorization", f"Bearer {self.api_key}")
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status != 200:
                    return {"success": False, "message": f"模型列表 API 返回 {resp.status}", "model": self.model}
                body = resp.read().decode("utf-8", errors="replace")
                # Look for the model id (case-insensitive) in the response
                if self.model.lower() in body.lower():
                    return {"success": True, "message": f"模型 {self.model} 可用", "model": self.model}
                # Some providers return objects without the id; fall back to
                # "key accepted" as success.
                return {"success": True, "message": f"API key 已认证（{self.model} 未在模型列表中找到，可能未开通）", "model": self.model}
        except urllib.error.HTTPError as he:
            if he.code in (401, 403):
                return {"success": False, "message": f"API key 无权限（HTTP {he.code}）", "model": self.model}
            return {"success": False, "message": f"HTTP {he.code}: {he.reason}", "model": self.model}
        except Exception as e:
            return {"success": False, "message": str(e), "model": self.model}

    def _models_list_url(self) -> str:
        """Override in subclasses to return the provider's model-list endpoint."""
        raise NotImplementedError

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

    Thinking: passes ``reasoning_effort`` per-request to OpenAI reasoning
    models (o-series, gpt-5.x). Non-reasoning models ignore it.
    """

    supports_thinking = True
    effort_levels = ("low", "medium", "high", "xhigh")
    thinking_parameter = "reasoning_effort"

    # Models that have reasoning capability per OpenAI's docs. We use this
    # to suppress the toggle in the UI for purely chat models so users don't
    # toggle a no-op. Reasoning-capable family prefixes per the docs.
    REASONING_MODEL_PREFIXES = (
        "o1", "o3", "o4", "gpt-5",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def model_supports_thinking(cls, model: str) -> bool:
        m = (model or "").lower()
        return any(m.startswith(p) for p in cls.REASONING_MODEL_PREFIXES)

    def _initialize_llm(self):
        import httpx
        from langchain_openai import ChatOpenAI
        kwargs = dict(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            request_timeout=httpx.Timeout(10.0, read=600.0, write=30.0, pool=10.0),
            max_retries=0,
        )
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return ChatOpenAI(**kwargs)

    def _thinking_kwargs(self) -> Dict[str, Any]:
        if not (self._thinking_enabled or self.thinking_always_on):
            return {}
        if not self.model_supports_thinking(self.model):
            return {}
        # OpenAI accepts low / medium / high / xhigh on most reasoning
        # models. ``none`` / ``minimal`` disable thinking on the models
        # that support those values; we don't expose those in the UI
        # because they're a no-op when the toggle is already off.
        effort = self._thinking_effort if self._thinking_effort in self.effort_levels else "high"
        return {"reasoning_effort": effort}

    def _models_list_url(self) -> str:
        base = (self.base_url or "https://api.openai.com/v1").rstrip("/")
        return f"{base}/models"


class AnthropicProvider(LLMProvider):
    """Anthropic (Claude) LLM provider.

    官方文档: https://docs.anthropic.com/en/api/getting-started
    支持模型: claude-opus-4-7, claude-sonnet-4-6, claude-haiku-4-5
    API Key:  https://console.anthropic.com/settings/keys

    Thinking: Anthropic's API uses ``thinking.type: "adaptive"`` for newer
    Claude 4.6+ models (Opus 4.7, Opus 4.8, Fable 5, Mythos 5) and a manual
    ``thinking.type: "enabled" + budget_tokens`` for older ones. We always
    use the adaptive form here because the curated Claude model list we
    expose (Opus 4.7/4.8, Sonnet 4.6, Haiku 4.5) all support it. The effort
    level is passed via ``output_config.effort``. For older models that
    only understand the legacy ``budget_tokens`` form, the request will
    fail with a 400 — that is the user's signal to switch models.

    On Opus 4.8 / Opus 4.7 / Fable 5 / Mythos 5, thinking cannot be
    disabled (it's always on). ``thinking_always_on`` flags this so the
    UI can hide the toggle.
    """

    supports_thinking = True
    effort_levels = ("low", "medium", "high", "max")
    thinking_parameter = "anthropic_thinking"

    # Per Anthropic docs: these models don't allow turning thinking off.
    ALWAYS_THINKING_PREFIXES = (
        "claude-opus-4-7",
        "claude-opus-4-8",
        "claude-fable",
        "claude-mythos",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._is_always_thinking(self.model):
            self._thinking_enabled = True
            self._reasoner_mode = True
            self.thinking_always_on = True

    @classmethod
    def _is_always_thinking(cls, model: str) -> bool:
        m = (model or "").lower()
        return any(m.startswith(p) for p in cls.ALWAYS_THINKING_PREFIXES)

    @classmethod
    def model_supports_thinking(cls, model: str) -> bool:
        m = (model or "").lower()
        return any(m.startswith(prefix) for prefix in (
            "claude-opus-4-", "claude-sonnet-4-", "claude-haiku-4-",
            "claude-fable", "claude-mythos",
        ))

    def _initialize_llm(self):
        import httpx
        from langchain_anthropic import ChatAnthropic
        kwargs = dict(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=httpx.Timeout(10.0, read=600.0, write=30.0, pool=10.0),
        )
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return ChatAnthropic(**kwargs)

    def _thinking_kwargs(self) -> Dict[str, Any]:
        # Even if the toggle is off, models that force thinking still emit
        # thinking blocks; pass an empty ``type: "adaptive"`` so the API
        # doesn't reject the request.
        if not (self._thinking_enabled or self.thinking_always_on):
            return {}
        if not self.model_supports_thinking(self.model):
            return {}
        effort = self._thinking_effort if self._thinking_effort in self.effort_levels else "high"
        # LangChain ChatAnthropic accepts ``thinking`` and ``output_config``
        # as kwargs to ``invoke`` and ``stream``. See
        # https://docs.anthropic.com/en/docs/build-with-claude/adaptive-thinking
        return {
            "thinking": {"type": "adaptive"},
            "output_config": {"effort": effort},
        }

    def _models_list_url(self) -> str:
        base = (self.base_url or "https://api.anthropic.com").rstrip("/")
        return f"{base}/v1/models"


class DeepSeekProvider(LLMProvider):
    """DeepSeek LLM provider (OpenAI 兼容接口).

    官方文档: https://platform.deepseek.com/api-docs
    base_url:  https://api.deepseek.com
    支持模型: deepseek-v4-flash, deepseek-v4-pro
    API Key:  https://platform.deepseek.com/api_keys
    注意: deepseek-chat 和 deepseek-reasoner 已废弃(2026-07-24停用), 请使用新版模型
    注意: base_url 不带 /v1，langchain-openai SDK 会自动补全
          deepseek-reasoner 会输出 <think> 标签，已自动过滤

    Thinking: DeepSeek V4 API expects thinking control via
    ``extra_body={"thinking": {"type": "enabled" | "disabled"}}`` and
    ``reasoning_effort="high"|"max"``. Per DeepSeek docs, thinking is enabled
    by default on V4 models; we explicitly toggle it when the user wants
    thinking off. LangChain's ChatOpenAI forwards ``extra_body`` to the
    underlying OpenAI client.
    """

    supports_thinking = True
    effort_levels = ("high", "max")
    thinking_parameter = "deepseek_thinking"

    @classmethod
    def model_supports_thinking(cls, model: str) -> bool:
        """Known DeepSeek reasoning families exposed by the current API."""
        m = (model or "").lower()
        return m.startswith(("deepseek-v4", "deepseek-reasoner"))

    def _initialize_llm(self):
        import httpx
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            base_url=self.base_url or "https://api.deepseek.com",
            request_timeout=httpx.Timeout(10.0, read=600.0, write=30.0, pool=10.0),
            max_retries=0,
        )

    def _thinking_kwargs(self) -> Dict[str, Any]:
        if not self.model_supports_thinking(self.model):
            return {}
        effort = self._thinking_effort if self._thinking_effort in self.effort_levels else "high"
        # If thinking is disabled we still pass ``thinking.type: disabled``
        # so the server doesn't fall back to its default (enabled on V4).
        if self._thinking_enabled:
            thinking = {"type": "enabled"}
            return {
                "reasoning_effort": effort,
                "extra_body": {"thinking": thinking},
            }
        return {
            "extra_body": {"thinking": {"type": "disabled"}},
        }

    def _models_list_url(self) -> str:
        base = (self.base_url or "https://api.deepseek.com/v1").rstrip("/")
        return f"{base}/models"

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

    Thinking: Gemini's OpenAI-compat endpoint maps OpenAI's
    ``reasoning_effort`` automatically to Gemini's native
    ``thinking_level`` (per Google docs). So we use the same shape as
    OpenAI and rely on Google's adapter. For Gemini 2.5 series (which
    use ``thinkingBudget`` not ``thinking_level``), the OpenAI-compat
    layer may ignore effort entirely; users on 2.5 will not see thinking
    toggle change anything but the chat still works.
    """

    supports_thinking = True
    effort_levels = ("low", "medium", "high")
    thinking_parameter = "reasoning_effort"

    # Models that understand the OpenAI reasoning_effort mapping. Gemini
    # 3.x uses thinking_level; 2.5 series uses thinkingBudget which the
    # OpenAI-compat layer may or may not honor.
    REASONING_PREFIXES = ("gemini-3", "gemini-2.5")

    @classmethod
    def model_supports_thinking(cls, model: str) -> bool:
        m = (model or "").lower()
        return any(m.startswith(p) for p in cls.REASONING_PREFIXES)

    def _initialize_llm(self):
        import httpx
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            base_url=self.base_url or "https://generativelanguage.googleapis.com/v1beta/openai/",
            request_timeout=httpx.Timeout(10.0, read=600.0, write=30.0, pool=10.0),
            max_retries=0,
        )

    def _thinking_kwargs(self) -> Dict[str, Any]:
        if not self.model_supports_thinking(self.model):
            return {}
        if not self._thinking_enabled:
            return {}
        effort = self._thinking_effort if self._thinking_effort in self.effort_levels else "high"
        # Gemini's OpenAI-compat layer accepts ``reasoning_effort`` and
        # maps it to thinking_level for Gemini 3.x models.
        return {"reasoning_effort": effort}

    def _models_list_url(self) -> str:
        # Gemini's native endpoint — accepts the API key as ?key= and returns
        # a JSON list of models. The OpenAI-compat endpoint does not expose
        # /models, so we use the native one for the connection test.
        return f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"


class SiliconFlowProvider(LLMProvider):
    """硅基流动 LLM provider (OpenAI 兼容接口).

    官方文档: https://docs.siliconflow.cn/cn/api-reference
    base_url:  https://api.siliconflow.cn/v1
    支持模型: Qwen/Qwen2.5-72B-Instruct, THUDM/glm-4-9b-chat,
              deepseek-ai/DeepSeek-V3, deepseek-ai/DeepSeek-R1,
              Pro/Qwen/Qwen2.5-72B-Instruct, 等
    API Key:  https://cloud.siliconflow.cn/account/ak
    注意: thinking/reasoning token 已在 stream_chat/chat 中自动过滤

    Thinking: SiliconFlow hosts DeepSeek-R1, Qwen-QwQ, and other reasoner
    models. Their reasoning models emit ``<think>...</think>`` blocks
    (filtered out automatically by chat/stream_chat below). SiliconFlow's
    API accepts ``reasoning_effort`` on supported models; for Qwen / V3
    it is silently ignored.
    """

    supports_thinking = True
    effort_levels = ("low", "medium", "high")
    thinking_parameter = "reasoning_effort"

    # Models on SiliconFlow that have reasoning capability.
    REASONING_SUBSTRINGS = (
        "DeepSeek-R1", "QwQ", "deepseek-r1", "qwq",
        "Hunyuan-A13B-Instruct",  # Tencent reasoning model
        "Kimi-K2-Thinking",
    )

    # SiliconFlow documents a separate ``enable_thinking`` switch for Qwen3
    # and Qwen3.5.  It is sent through OpenAI-compatible clients as
    # ``extra_body``; ``reasoning_effort`` is not the correct dialect there.
    QWEN_THINKING_MARKER = "qwen3"

    @classmethod
    def _uses_enable_thinking(cls, model: str) -> bool:
        return cls.QWEN_THINKING_MARKER in (model or "").lower()

    @classmethod
    def model_supports_thinking(cls, model: str) -> bool:
        m = model or ""
        ml = m.lower()
        return cls._uses_enable_thinking(model) or any(s.lower() in ml for s in cls.REASONING_SUBSTRINGS)

    @classmethod
    def thinking_parameter_for_model(cls, model: str) -> str:
        if cls._uses_enable_thinking(model):
            return "enable_thinking"
        return cls.thinking_parameter

    def _initialize_llm(self):
        import httpx
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            base_url=self.base_url or "https://api.siliconflow.cn/v1",
            request_timeout=httpx.Timeout(10.0, read=600.0, write=30.0, pool=10.0),
            max_retries=0,
        )

    def _thinking_kwargs(self) -> Dict[str, Any]:
        if not self.model_supports_thinking(self.model):
            return {}
        if self._uses_enable_thinking(self.model):
            body = {"enable_thinking": bool(self._thinking_enabled)}
            if self._thinking_enabled:
                budget = {
                    "low": 2048,
                    "medium": 4096,
                    "high": 8192,
                }.get(self._thinking_effort, 4096)
                body["thinking_budget"] = budget
            return {"extra_body": body}
        if not self._thinking_enabled:
            return {}
        effort = self._thinking_effort if self._thinking_effort in self.effort_levels else "high"
        return {"reasoning_effort": effort}

    def _models_list_url(self) -> str:
        base = (self.base_url or "https://api.siliconflow.cn/v1").rstrip("/")
        return f"{base}/models"

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
            timeout=600,  # seconds; raises requests.Timeout if exceeded
        )

    def _models_list_url(self) -> str:
        # Ollama's API doesn't require a key — just list tags to confirm liveness.
        return "http://localhost:11434/api/tags"

    def test_connection(self) -> Dict[str, Any]:
        try:
            import urllib.request
            with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as resp:
                if resp.status != 200:
                    return {"success": False, "message": f"Ollama 返回 {resp.status}", "model": self.model}
                body = resp.read().decode("utf-8", errors="replace")
                if self.model.lower() in body.lower():
                    return {"success": True, "message": f"Ollama 模型 {self.model} 可用", "model": self.model}
                return {"success": False, "message": f"Ollama 已运行，但未找到模型 {self.model}", "model": self.model}
        except Exception as e:
            return {"success": False, "message": f"Ollama 未运行: {e}", "model": self.model}


class GLMProvider(LLMProvider):
    """Zhipu AI (GLM) API provider.

    官方文档: https://docs.bigmodel.cn
    API endpoint: https://open.bigmodel.cn/api/paas/v4/chat/completions
    支持模型: GLM-5.2, GLM-5.1, GLM-4-Plus, GLM-4, GLM-Z1 (推理) 等

    Thinking: GLM accepts ``thinking: {type: enabled|disabled}`` as a top
    level request field and ``reasoning_effort`` to control depth. Only
    GLM-5.2 honours the full effort enum; older GLM-4.5/4.6 series only
    return ``reasoning_content`` without effort tuning. Per docs:
    ``none``/``minimal`` disable thinking, ``low``/``medium`` map to
    ``high``, ``xhigh`` maps to ``max``. We pass ``thinking`` as a top
    level body field via ``model_kwargs`` so LangChain forwards it.
    """

    supports_thinking = True
    effort_levels = ("low", "medium", "high", "xhigh", "max")
    thinking_parameter = "glm_thinking"

    # Models that fully support thinking + effort tuning.
    FULL_THINKING_PREFIXES = ("glm-5",)

    @classmethod
    def model_supports_thinking(cls, model: str) -> bool:
        m = (model or "").lower()
        # All glm-4.5+ series support the binary thinking switch.
        return any(m.startswith(p) for p in ("glm-5", "glm-4.5", "glm-4.6", "glm-4.7", "glm-z1", "glm-4.1v-thinking"))

    def _normalize_effort(self, effort: str) -> str:
        e = (effort or "").lower()
        if e in self.effort_levels:
            return e
        return "high"

    def _initialize_llm(self):
        import httpx
        from langchain_openai import ChatOpenAI
        # NOTE: 600s read timeout for GLM/DeepSeek synthesis on 25-60k-char prompts.
        # A read timeout causes httpx.ReadTimeout → synthesizer catches it → returns
        # event:error to frontend instead of hanging indefinitely.
        return ChatOpenAI(
            model=self.model,
            openai_api_key=self.api_key,
            openai_api_base=self.base_url or "https://open.bigmodel.cn/api/paas/v4/",
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            request_timeout=httpx.Timeout(10.0, read=600.0, write=30.0, pool=10.0),
            max_retries=0,
        )

    def _thinking_kwargs(self) -> Dict[str, Any]:
        if not self.model_supports_thinking(self.model):
            return {}
        if self._thinking_enabled:
            effort = self._thinking_effort
            # GLM only differentiates high/xhigh vs max for full-thinking
            # models; for older models we still send effort but it may be
            # silently ignored.
            return {
                "thinking": {"type": "enabled"},
                "reasoning_effort": effort,
            }
        return {"thinking": {"type": "disabled"}}

    def _models_list_url(self) -> str:
        base = (self.base_url or "https://open.bigmodel.cn/api/paas/v4").rstrip("/")
        return f"{base}/models"


class KimiProvider(LLMProvider):
    """Moonshot AI (Kimi) API provider.

    官方文档: https://platform.kimi.com/docs/api/overview
    API endpoint: https://api.moonshot.cn/v1/chat/completions
    支持模型: kimi-k2.6, moonshot-v2.5-250415, moonshot-v1.5-32k 等
    API Key: https://platform.kimi.com/console/api-keys

    Thinking: Kimi's current thinking-capable models (kimi-k2.6, kimi-k2.7-code,
    kimi-k2-thinking) control thinking via ``thinking: {type: enabled|disabled,
    keep: null|"all"}``. There is NO ``reasoning_effort`` — it's a binary
    switch. ``keep: "all"`` enables Preserved Thinking for multi-turn tool
    calls. We default to ``keep: "all"`` so the agent's multi-step workflows
    don't degrade across turns.
    """

    supports_thinking = True
    # No effort levels — Kimi is binary.
    effort_levels = ()
    thinking_parameter = "kimi_thinking"
    # Models that support the thinking switch.
    THINKING_PREFIXES = ("kimi-k2",)

    @classmethod
    def model_supports_thinking(cls, model: str) -> bool:
        m = (model or "").lower()
        return any(m.startswith(p) for p in cls.THINKING_PREFIXES)

    def _initialize_llm(self):
        import httpx
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            base_url=self.base_url or "https://api.moonshot.cn/v1",
            request_timeout=httpx.Timeout(10.0, read=600.0, write=30.0, pool=10.0),
            max_retries=0,
        )

    def _thinking_kwargs(self) -> Dict[str, Any]:
        if not self.model_supports_thinking(self.model):
            return {}
        if self._thinking_enabled:
            return {"thinking": {"type": "enabled", "keep": "all"}}
        return {"thinking": {"type": "disabled", "keep": "all"}}

    def _models_list_url(self) -> str:
        base = (self.base_url or "https://api.moonshot.cn/v1").rstrip("/")
        return f"{base}/models"


class SDUProvider(LLMProvider):
    """山东大学 SDU-AI 大模型平台 (OpenAI 兼容接口).

    平台文档: https://xplt.sdu.edu.cn:4000
    API endpoint: https://xplt.sdu.edu.cn:4000/v1/chat/completions
    base_url:  https://xplt.sdu.edu.cn:4000/v1
    接口格式:  OpenAI Chat Completions 兼容，支持 messages/stream/model/temperature/top_p/max_tokens/tools 等
    支持模型:  SDU-AI/DeepSeek-V4-Flash, SDU-AI/GLM-5, SDU-AI/Qwen3-235B, SDU-AI/Kimi-K2 等
    API Key:   https://xplt.sdu.edu.cn:4000 用户中心获取

    Thinking: SDU-AI 平台支持 reasoning_content 字段，按模型而定
    """

    DEFAULT_BASE_URL = "https://xplt.sdu.edu.cn:4000/v1"
    # SDU-AI platform reports max_model_len ≈ 71680 for current models (DeepSeek-V4-Flash
    # & GLM-5). To leave headroom for input, cap requested completion tokens to
    # roughly half of the model window — input prompts with KB context can reach
    # 30-50k chars (~10-15k tokens) on this codebase.
    MAX_OUTPUT_TOKENS_CAP = 32768

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Clamp max_tokens at construction so the value is consistent everywhere
        # (provider cache + LangChain client).
        if self._max_tokens > self.MAX_OUTPUT_TOKENS_CAP:
            self._max_tokens = self.MAX_OUTPUT_TOKENS_CAP
            if getattr(self, "llm", None) is not None:
                try:
                    self.llm.max_tokens = self._max_tokens
                except Exception:
                    pass

    def _initialize_llm(self):
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.MAX_OUTPUT_TOKENS_CAP,
            base_url=self.base_url or self.DEFAULT_BASE_URL,
        )

    def _models_list_url(self) -> str:
        base = (self.base_url or "https://xplt.sdu.edu.cn:4000/v1").rstrip("/")
        return f"{base}/models"


class CustomProvider(LLMProvider):
    """OpenAI-compatible proxy / custom endpoint (e.g. a6api, OpenRouter, etc.).

    This provider exists purely so the user can point E2seq at any OpenAI-compatible
    HTTP endpoint and have it work out of the box — the ChatOpenAI client is
    instantiated with whatever ``base_url`` the user supplied.
    """

    supports_thinking: bool = True   # OpenAI-compatible endpoints often support reasoning_effort
    effort_levels: tuple = ("low", "medium", "high", "max")
    # A custom endpoint has no universal capability metadata.  We only enable
    # thinking after the model id matches a known request dialect; unknown
    # models remain disabled instead of receiving a speculative parameter.
    thinking_parameter = "unknown"

    @classmethod
    def thinking_parameter_for_model(cls, model: str) -> str:
        ml = (model or "").lower()
        if "qwen3" in ml:
            return "enable_thinking"
        if ml.startswith(("deepseek-v4", "deepseek-reasoner")):
            return "deepseek_thinking"
        if ml.startswith(("gpt-5", "o1", "o3", "o4")):
            return "reasoning_effort"
        if ml.startswith("kimi-k2"):
            return "kimi_thinking"
        return cls.thinking_parameter

    @classmethod
    def model_supports_thinking(cls, model: str) -> bool:
        return cls.thinking_parameter_for_model(model) != cls.thinking_parameter

    @classmethod
    def model_capability_known(cls, model: str) -> bool:
        """Custom endpoints cannot certify an unrecognised model id."""
        return cls.thinking_parameter_for_model(model) != cls.thinking_parameter

    def _initialize_llm(self):
        import httpx
        from langchain_openai import ChatOpenAI
        if not self.base_url:
            raise ValueError("CustomProvider requires a base_url")
        return ChatOpenAI(
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            base_url=self.base_url.rstrip("/"),
            request_timeout=httpx.Timeout(10.0, read=600.0, write=30.0, pool=10.0),
            max_retries=0,
        )

    def _thinking_kwargs(self) -> Dict[str, Any]:
        parameter = self.thinking_parameter_for_model(self.model)
        if parameter == self.thinking_parameter:
            return {}
        if parameter == "enable_thinking":
            body = {"enable_thinking": bool(self._thinking_enabled)}
            if self._thinking_enabled:
                body["thinking_budget"] = {
                    "low": 2048,
                    "medium": 4096,
                    "high": 8192,
                    "max": 16384,
                }.get(self._thinking_effort, 4096)
            return {"extra_body": body}
        if parameter == "deepseek_thinking":
            if not self._thinking_enabled:
                return {"extra_body": {"thinking": {"type": "disabled"}}}
            effort = self._thinking_effort if self._thinking_effort in self.effort_levels else "high"
            return {
                "reasoning_effort": effort,
                "extra_body": {"thinking": {"type": "enabled"}},
            }
        if parameter == "kimi_thinking":
            return {
                "thinking": {
                    "type": "enabled" if self._thinking_enabled else "disabled",
                    "keep": "all",
                }
            }
        if not self._thinking_enabled:
            return {}
        effort = self._thinking_effort if self._thinking_effort in self.effort_levels else "high"
        return {"reasoning_effort": effort}

    def _models_list_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/models"


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
    "sdu": SDUProvider,
    "custom": CustomProvider,
}

# 各 provider 的默认模型 + 推荐模型列表（2026-06 最新）
_DEFAULT_MODELS: Dict[str, str] = {
    "openai":      "gpt-5.5",
    "anthropic":   "claude-opus-4-8",
    "deepseek":    "deepseek-v4-flash",
    "gemini":      "gemini-3.1-pro-preview",
    "siliconflow": "deepseek-ai/DeepSeek-V3",
    "glm":         "glm-5.2",
    "kimi":        "kimi-k2.6",
    "ollama":      "llama3.2",
    "sdu":         "SDU-AI/DeepSeek-V4-Flash",
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
        "claude-opus-4-8",
        "claude-opus-4-7",
        "claude-sonnet-4-6",
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
        "glm-5.2",
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
    "sdu": [
        "SDU-AI/DeepSeek-V4-Flash",
        "SDU-AI/GLM-5",
        "SDU-AI/Qwen3-235B",
        "SDU-AI/Kimi-K2",
    ],
}


def create_llm_provider(
    provider: str,
    api_key: str = "",
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 81920,
    thinking_enabled: bool = False,
    thinking_effort: str = "high",
    base_url: Optional[str] = None,
) -> LLMProvider:
    """Factory function to create LLM provider.

    Args:
        provider:    Provider name (openai, anthropic, deepseek, gemini, siliconflow, glm, ollama)
        api_key:     明文 API key（server 层传入前已解密）
        model:       Model name，为空时使用各 provider 默认模型
        temperature: 生成温度
        max_tokens:  最大 token 数
        thinking_enabled: Enable chain-of-thought reasoning on the model
            (only meaningful if the selected model supports thinking).
        thinking_effort: One of the values in ``LLMProvider.effort_levels`` for
            the chosen provider. Defaults to ``"high"``. Ignored by providers
            that don't support effort tuning (e.g. Kimi is binary).
        base_url:    Optional custom base URL (any OpenAI/Anthropic/Gemini
            compatible proxy such as a6api, OpenRouter). Empty/None means
            ``use the provider's hard-coded default``.

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
    logger.info(
        f"创建 LLM provider: {provider_lower}, model: {resolved_model}, "
        f"thinking={thinking_enabled}, effort={thinking_effort}, "
        f"base_url={base_url or '<default>'}"
    )
    return _PROVIDERS[provider_lower](
        api_key, resolved_model, temperature, max_tokens,
        thinking_enabled=thinking_enabled, thinking_effort=thinking_effort,
        base_url=base_url,
    )


def provider_supports_thinking(provider: str, model: Optional[str] = None) -> Dict[str, Any]:
    """Capability probe for the frontend.

    Returns ``{"supports_thinking": bool, "always_on": bool, "model_supported":
    bool, "capability_known": bool, "effort_levels": [...]}`` for the
    (provider, model) pair. Used by
    the settings UI to decide whether to show / hide the Thinking toggle and
    what effort options to put in the dropdown.
    """
    provider_lower = (provider or "").lower()
    if provider_lower not in _PROVIDERS:
        return {
            "supports_thinking": False,
            "always_on": False,
            "model_supported": False,
            "capability_known": True,
            "capability_state": "unsupported",
            "thinking_parameter": "none",
            "effort_levels": [],
        }
    cls = _PROVIDERS[provider_lower]
    always_on = bool(getattr(cls, "thinking_always_on", False))
    if model and hasattr(cls, "_is_always_thinking"):
        try:
            always_on = bool(cls._is_always_thinking(model))
        except Exception:
            pass
    supports = bool(getattr(cls, "supports_thinking", False))
    effort_levels = list(getattr(cls, "effort_levels", ()))
    # Probe per-model if the subclass exposes a classmethod.  Unknown model
    # ids are deliberately not treated as supported: a provider can expose a
    # thinking dialect while a particular model silently rejects it.
    capability_known = bool(model and hasattr(cls, "model_supports_thinking"))
    model_supported = False
    if capability_known:
        try:
            model_supported = bool(cls.model_supports_thinking(model))
            if hasattr(cls, "model_capability_known"):
                capability_known = bool(cls.model_capability_known(model))
        except Exception:
            capability_known = False
            model_supported = False
    if always_on:
        model_supported = True
        capability_known = True
    if always_on:
        capability_state = "always_on"
    elif not model:
        capability_state = "unknown" if supports else "unsupported"
    elif not supports:
        capability_state = "unsupported"
        capability_known = True
    elif not capability_known:
        capability_state = "unknown"
    else:
        capability_state = "supported" if model_supported else "unsupported"
    thinking_parameter = getattr(cls, "thinking_parameter", "none")
    if model and hasattr(cls, "thinking_parameter_for_model"):
        try:
            thinking_parameter = cls.thinking_parameter_for_model(model)
        except Exception:
            thinking_parameter = "unknown"
    return {
        "supports_thinking": supports,
        "always_on": always_on,
        "model_supported": model_supported,
        "capability_known": capability_known,
        "capability_state": capability_state,
        "thinking_parameter": thinking_parameter,
        "effort_levels": effort_levels,
    }


def thinking_enabled_for_model(provider: str, model: Optional[str], requested: bool) -> bool:
    """Return the safe, effective value for a thinking-mode request.

    The UI disables the control for unknown models, but the server must enforce
    the same rule because settings endpoints are also callable directly.  An
    unknown or unsupported model therefore never receives a speculative
    thinking parameter.
    """
    if not requested:
        return False
    capability = provider_supports_thinking(provider, model)
    return bool(
        capability.get("always_on")
        or capability.get("capability_state") == "supported"
    )


def get_supported_providers() -> Dict[str, Dict[str, Any]]:
    """返回所有支持的 provider 及其默认模型和推荐模型列表。"""
    return {
        name: {
            "default_model": _DEFAULT_MODELS[name],
            "recommended_models": _RECOMMENDED_MODELS.get(name, []),
        }
        for name in _PROVIDERS
    }
