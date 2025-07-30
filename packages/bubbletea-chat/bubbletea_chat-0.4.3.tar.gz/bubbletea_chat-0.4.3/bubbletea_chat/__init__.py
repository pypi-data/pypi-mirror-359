"""
BubbleTea - A Python package for building AI chatbots
With LiteLLM support for easy LLM integration
"""

from .components import Text, Image, Markdown, Card, Cards, Done
from .decorators import chatbot, config
from .server import run_server
from .schemas import ImageInput, BotConfig

try:
    from .llm import LLM
    __all__ = ["Text", "Image", "Markdown", "Card", "Cards", "Done", "chatbot", "config", "run_server", "LLM", "ImageInput", "BotConfig"]
except ImportError:
    __all__ = ["Text", "Image", "Markdown", "Card", "Cards", "Done", "chatbot", "config", "run_server", "ImageInput", "BotConfig"]
    raise ImportError(
        "LiteLLM is not installed. Please install it with `pip install bubbletea[llm]`"
    )