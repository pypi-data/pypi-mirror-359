from enum import Enum
from typing import Any, Literal
from litellm import ChatCompletionMessageToolCall
from pydantic import BaseModel, Field, model_serializer
class ContentType(Enum):
    TEXT = 'text'
    IMAGE_URL = 'image_url'
class Content(BaseModel):
    type: str
    cache_prompt: bool = False
    @model_serializer(mode='plain')
    def serialize_model(
        self,
    ) -> dict[str, str | dict[str, str]] | list[dict[str, str | dict[str, str]]]:
        raise NotImplementedError('Subclasses should implement this method.')
class TextContent(Content):
    type: str = ContentType.TEXT.value
    text: str
    @model_serializer(mode='plain')
    def serialize_model(self) -> dict[str, str | dict[str, str]]:
        data: dict[str, str | dict[str, str]] = {
            'type': self.type,
            'text': self.text,
        }
        if self.cache_prompt:
            data['cache_control'] = {'type': 'ephemeral'}
        return data
class ImageContent(Content):
    type: str = ContentType.IMAGE_URL.value
    image_urls: list[str]
    @model_serializer(mode='plain')
    def serialize_model(self) -> list[dict[str, str | dict[str, str]]]:
        images: list[dict[str, str | dict[str, str]]] = []
        for url in self.image_urls:
            images.append({'type': self.type, 'image_url': {'url': url}})
        if self.cache_prompt and images:
            images[-1]['cache_control'] = {'type': 'ephemeral'}
        return images
class Message(BaseModel):
    role: Literal['user', 'system', 'assistant', 'tool']
    content: list[TextContent | ImageContent] = Field(default_factory=list)
    cache_enabled: bool = False
    vision_enabled: bool = False
    function_calling_enabled: bool = False
    tool_calls: list[ChatCompletionMessageToolCall] | None = None
    tool_call_id: str | None = None
    name: str | None = None
    force_string_serializer: bool = False
    @property
    def contains_image(self) -> bool:
        return any(isinstance(content, ImageContent) for content in self.content)
    @model_serializer(mode='plain')
    def serialize_model(self) -> dict[str, Any]:
        if not self.force_string_serializer and (
            self.cache_enabled or self.vision_enabled or self.function_calling_enabled
        ):
            return self._list_serializer()
        return self._string_serializer()
    def _string_serializer(self) -> dict[str, Any]:
        content = '\n'.join(
            item.text for item in self.content if isinstance(item, TextContent)
        )
        message_dict: dict[str, Any] = {'content': content, 'role': self.role}
        return self._add_tool_call_keys(message_dict)
    def _list_serializer(self) -> dict[str, Any]:
        content: list[dict[str, Any]] = []
        role_tool_with_prompt_caching = False
        for item in self.content:
            d = item.model_dump()
            if self.role == 'tool' and item.cache_prompt:
                role_tool_with_prompt_caching = True
                if isinstance(item, TextContent):
                    d.pop('cache_control', None)
                elif isinstance(item, ImageContent):
                    if hasattr(d, '__iter__'):
                        for d_item in d:
                            if hasattr(d_item, 'pop'):
                                d_item.pop('cache_control', None)
            if isinstance(item, TextContent):
                content.append(d)
            elif isinstance(item, ImageContent) and self.vision_enabled:
                content.extend([d] if isinstance(d, dict) else d)
        message_dict: dict[str, Any] = {'content': content, 'role': self.role}
        if role_tool_with_prompt_caching:
            message_dict['cache_control'] = {'type': 'ephemeral'}
        return self._add_tool_call_keys(message_dict)
    def _add_tool_call_keys(self, message_dict: dict[str, Any]) -> dict[str, Any]:
        """Add tool call keys if we have a tool call or response.
        NOTE: this is necessary for both native and non-native tool calling
        """
        if self.tool_calls is not None:
            message_dict['tool_calls'] = [
                {
                    'id': tool_call.id,
                    'type': 'function',
                    'function': {
                        'name': tool_call.function.name,
                        'arguments': tool_call.function.arguments,
                    },
                }
                for tool_call in self.tool_calls
            ]
        if self.tool_call_id is not None:
            assert self.name is not None, (
                'name is required when tool_call_id is not None'
            )
            message_dict['tool_call_id'] = self.tool_call_id
            message_dict['name'] = self.name
        return message_dict