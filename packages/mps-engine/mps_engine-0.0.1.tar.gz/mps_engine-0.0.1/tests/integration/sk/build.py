import logging

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)
from semantic_kernel.connectors.ai.ollama import (
    OllamaChatCompletion,
    OllamaChatPromptExecutionSettings,
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.kernel import Kernel
from semantic_kernel.utils.logging import setup_logging

kernel = Kernel()

OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_MODEL = "qwen2.5"

# agent core
chat_completion = OllamaChatCompletion(
    host=str(OLLAMA_HOST), ai_model_id=str(OLLAMA_MODEL)
)


# telemetry
setup_logging()
logging.getLogger("kernel").setLevel(logging.WARNING)

# planners
execution_settings = OllamaChatPromptExecutionSettings()
execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()


# chat history retention
def get_chat_history() -> ChatHistory:
    return ChatHistory()


# build agents
agent = ChatCompletionAgent(
    service=chat_completion,
    kernel=kernel,
)
