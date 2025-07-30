from typing import Any, Generator, List, Optional
import litellm

from injector import inject

from taskweaver.llm.base import (
    CompletionService,
    EmbeddingService,
    LLMServiceConfig
)
from taskweaver.llm.util import ChatMessageType, format_chat_message


class LiteLLMServiceConfig(LLMServiceConfig):
    def _configure(self) -> None:
        self._set_name("agentos")

        shared_api_key = self.llm_module_config.api_key
        self.api_key = self._get_str(
            "api_key",
            shared_api_key,
        )

        shared_model = self.llm_module_config.model
        self.model = self._get_str(
            "model",
            shared_model
            if shared_model is not None else "gpt-4o"
        )

        shared_embedding_model = self.llm_module_config.embedding_model
        self.embedding_model = self._get_str(
            "embedding_model",
            shared_embedding_model
            if shared_embedding_model is not None else self.model,
        )

        shared_callbacks = self.llm_module_config.callbacks
        self.callbacks = self._get_list(
            "callbacks",
            shared_callbacks if shared_callbacks is not None else [],
        )


class LiteLLMService(CompletionService, EmbeddingService):
    @inject
    def __init__(self, config: LiteLLMServiceConfig) -> None:
        self.config = config
        if self.config.callbacks:
            litellm.success_callback = self.config.callbacks
            litellm.failure_callback = self.config.callbacks

    def chat_completion(
        self,
        messages: List[ChatMessageType],
        stream: bool = True,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Generator[ChatMessageType, None, None]:

        gen_config = {
            "temperature": temperature or 0.1,
            "max_tokens": max_tokens,
            "top_p": top_p or 1.0,
            "stop": stop or [],
        }
        litellm.drop_params = True
        if stream:
            response = litellm.completion(
                model=self.config.model,
                messages=messages,
                stream=True,
                **gen_config
            )
            for chunk in response:
                content = chunk.choices[0].delta.content
                if not content:
                    continue
                yield format_chat_message(
                    "assistant", chunk.choices[0].delta.content
                )
        else:
            response = litellm.completion(
                model=self.config.model,
                messages=messages,
                stream=False,
                **gen_config
            )
            result = response.choices[0].message.content
            yield format_chat_message("assistant", result)

    def get_embeddings(self, strings: List[str]) -> List[List[float]]:
        batch_size = 16
        ress = []
        for i in range(0, len(strings), batch_size):
            batch = strings[i:i + batch_size]
            response = litellm.embedding(
                model=self.config.embedding_model,
                input=batch,
            )
            ress.extend([d['embedding'] for d in response.data])
        return ress
