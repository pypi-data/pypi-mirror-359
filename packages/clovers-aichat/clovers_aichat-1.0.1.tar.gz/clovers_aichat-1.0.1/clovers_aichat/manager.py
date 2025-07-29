import httpx
from pathlib import Path
from pydantic import BaseModel
from .core import AIChat, ChatInterface
from .ai.mix import Chat as MixChat
from .ai.openai import Chat as OpenAIChat
from .ai.hunyuan import Chat as HunYuanChat
from .ai.gemini import Chat as GeminiChat


def matchChat(key: str) -> tuple[type[ChatInterface], str]:
    match key:
        case "chatgpt":
            return OpenAIChat, "ChatGPT"
        case "qwen":
            return OpenAIChat, "通义千问"
        case "deepseek":
            return OpenAIChat, "DeepSeek"
        case "hunyuan":
            return HunYuanChat, "腾讯混元"
        case "gemini":
            return GeminiChat, "Gemini"
        case _:
            from importlib import import_module

            Chat = getattr(import_module(".".join(Path(key.rstrip(".py")).relative_to(Path()).parts)), "Chat", None)
            if Chat and issubclass(Chat, ChatInterface):
                return Chat, key
            raise ValueError(f"不支持的模型:{key}")


class ManagerInfo:
    """实例设置"""

    whitelist: set[str] = set()
    """白名单"""
    blacklist: set[str] = set()
    """黑名单"""
    proxy: str | None = None
    """代理地址"""


class ManagerConfig(ManagerInfo, BaseModel):
    pass


class MixManagerConfig(ManagerInfo, BaseModel):
    text: dict
    image: dict


class Manager(ManagerInfo):
    """实例运行管理类"""

    name: str
    """实例名称"""

    def __init__(self, config: dict) -> None:
        self.chats: dict[str, AIChat] = {}
        self.config = config
        if config["key"] == "mix":
            _config = MixManagerConfig.model_validate(config)
            self.async_client = httpx.AsyncClient(proxy=_config.proxy, timeout=60.0)
            ChatText, ChatTextName = matchChat(_config.text["key"])
            chat_text = ChatText(config | _config.text, self.async_client)
            ChatImage, ChatImageName = matchChat(_config.image["key"])
            chat_image = ChatImage(config | _config.image, self.async_client)
            self.name = f"Mix({ChatTextName},{ChatImageName})"
            self.newChat = lambda: MixChat(_config.whitelist, _config.blacklist, chat_text, chat_image)
        else:
            _config = ManagerConfig.model_validate(config)
            self.async_client = httpx.AsyncClient(proxy=_config.proxy, timeout=60.0)
            newChat, self.name = matchChat(config["key"])
            self.newChat = lambda: newChat(self.config, self.async_client)
        self.whitelist = _config.whitelist
        self.blacklist = _config.blacklist

    def chat(self, group_id: str):
        if group_id not in self.chats:
            self.chats[group_id] = self.newChat()
        return self.chats[group_id]

    def check(self, group_id: str) -> bool:
        raise NotImplementedError("check 方法未注入，请在创建实例时设置 check 方法")

    def none_check(self, group_id: str) -> bool:
        return True

    def whitelist_check(self, group_id: str) -> bool:
        return group_id in self.whitelist

    def blacklist_check(self, group_id: str) -> bool:
        return group_id not in self.blacklist
