"""Wrapper around GreenNode Serverless AI's Chat Completions API."""

import openai

from typing_extensions import Self
from typing import Any, Dict, Optional
from pydantic import ConfigDict, Field, SecretStr, model_validator


from langchain_core.utils import from_env, secret_from_env
from langchain_core.language_models.chat_models import LangSmithParams
from langchain_openai.chat_models.base import BaseChatOpenAI


class ChatGreenNode(BaseChatOpenAI):


    @property
    def lc_secrets(self) -> Dict[str, str]:
        """A map of constructor argument names to secret ids.

        For example,
            {"greennode_api_key": "GREENNODE_API_KEY"}
        """
        return {"greennode_api_key": "GREENNODE_API_KEY"}
    
    @classmethod
    def get_lc_namespace(cls) -> list[str]:
        """Get the namespace of the langchain object."""
        return ["langchain", "chat_models", "greennode"]
    
    @property
    def lc_attributes(self) -> dict[str, Any]:
        attributes: dict[str, Any] = {}

        if self.openai_api_base:
            attributes["greennode_api_base"] = self.greennode_api_base

        return attributes
    
    @property
    def _llm_type(self) -> str:
        """Return type of chat model."""
        return "greennode-chat"
    
    def _get_ls_params(
        self, stop: Optional[list[str]] = None, **kwargs: Any
    ) -> LangSmithParams:
        """Get standard params for tracing."""
        params = super()._get_ls_params(stop=stop, **kwargs)
        params["ls_provider"] = "greennode"
        return params
    
    model_name: str = Field(default="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", alias="model")
    """Model name to use."""
    greennode_api_key: Optional[SecretStr] = Field(
        alias="api_key",
        default_factory=secret_from_env("GREENNODE_API_KEY", default=None),
    )
    """GreenNode AI API key.

    Automatically read from env variable `GREENNODE_API_KEY` if not provided.
    """
    greennode_api_base: str = Field(
        default_factory=from_env(
            "GREENNODE_API_BASE", default="https://maas.api.greennode.ai/v1/"
        ),
        alias="base_url",
    )

    model_config = ConfigDict(
        populate_by_name=True,
    )

    @model_validator(mode="after")
    def validate_environment(self) -> Self:
        """Validate that api key and python package exists in environment."""
        if self.n is not None and self.n < 1:
            raise ValueError("n must be at least 1.")
        if self.n is not None and self.n > 1 and self.streaming:
            raise ValueError("n must be 1 when streaming.")

        client_params: dict = {
            "api_key": (
                self.greennode_api_key.get_secret_value()
                if self.greennode_api_key
                else None
            ),
            "base_url": self.greennode_api_base,
            "timeout": self.request_timeout,
            "default_headers": self.default_headers,
            "default_query": self.default_query,
        }
        if self.max_retries is not None:
            client_params["max_retries"] = self.max_retries

        if not (self.client or None):
            sync_specific: dict = {"http_client": self.http_client}
            self.client = openai.OpenAI(
                **client_params, **sync_specific
            ).chat.completions
        if not (self.async_client or None):
            async_specific: dict = {"http_client": self.http_async_client}
            self.async_client = openai.AsyncOpenAI(
                **client_params, **async_specific
            ).chat.completions
        return self