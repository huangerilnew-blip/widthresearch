import os
import logging
import importlib
from typing import cast, Any
from concurrent_log_handler import ConcurrentRotatingFileHandler
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from llama_index.embeddings.openai_like import OpenAILikeEmbedding
from pydantic import SecretStr
from core.config import Config
from dotenv import load_dotenv

# # 设置日志基本配置，级别为DEBUG或INFO
logger = logging.getLogger(__name__)
# 设置日志器级别为DEBUG
logger.setLevel(logging.DEBUG)
# logger.setLevel(logging.INFO)
logger.handlers = []  # 清空默认处理器
# 使用ConcurrentRotatingFileHandler
handler = ConcurrentRotatingFileHandler(
    # 日志文件
    Config.LOG_FILE,
    # 日志文件最大允许大小为5MB，达到上限后触发轮转
    maxBytes = Config.MAX_BYTES,
    # 在轮转时，最多保留3个历史日志文件
    backupCount = Config.BACKUP_COUNT
)
# 设置处理器级别为DEBUG
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
logger.addHandler(handler)

load_dotenv()
# 模型配置字典
MODEL_CONFIGS = {
    "chat": {
        "qwen": {
            "base_url": os.getenv("BASE_URL"),
            "api_key": os.getenv("API_KEY"),
            "model_name": os.getenv("CHAT_MODEL")
        }
    },
    "embedding": {
        "qwen": {
            "base_url": os.getenv("BASE_URL"),
            "api_key": os.getenv("API_KEY"),
            "model_name": os.getenv("EMBEDDING_MODEL", Config.BL_MODEL_NAME)
        },
        "bge": {
            "base_url": Config.VLLM_BASE_URL,
            "api_key": "NA",
            "model_name": "bge-m3"
    }
}
}

# 默认配置
DEFAULT_CHAT_NAME = "qwen"
DEFAULT_EMBEDDING_NAME = "bge"
DEFAULT_TEMPERATURE = 0


class LLMInitializationError(Exception):
    """自定义异常类用于LLM初始化错误"""
    pass


def _resolve_model_configs(
    chat_name: str,
    embedding_name: str
):
    if chat_name not in MODEL_CONFIGS["chat"]:
        raise ValueError(
            f"不支持的Chat模型类型: {chat_name}. 可用的类型: {list(MODEL_CONFIGS['chat'].keys())}"
        )
    if embedding_name not in MODEL_CONFIGS["embedding"]:
        raise ValueError(
            f"不支持的Embedding模型类型: {embedding_name}. 可用的类型: {list(MODEL_CONFIGS['embedding'].keys())}"
        )
    return MODEL_CONFIGS["chat"][chat_name], MODEL_CONFIGS["embedding"][embedding_name]


def _resolve_model_values(chat_config, embedding_config):
    chat_base_url = cast(str, chat_config["base_url"])
    chat_api_key = cast(str, chat_config["api_key"])
    chat_model_name = cast(str, chat_config["model_name"])
    if not chat_base_url:
        raise ValueError("Chat 模型配置不完整，缺少 base_url")
    if not chat_api_key:
        raise ValueError("Chat 模型配置不完整，缺少 api_key")
    if not chat_model_name:
        raise ValueError("Chat 模型配置不完整，缺少 model_name")

    embedding_base_url = cast(str, embedding_config["base_url"])
    embedding_api_key = cast(str, embedding_config["api_key"]) or "NA"
    embedding_model_name = cast(str, embedding_config["model_name"])
    if not embedding_base_url:
        raise ValueError("Embedding 模型配置不完整，缺少 base_url")
    if not embedding_model_name:
        raise ValueError("Embedding 模型配置不完整，缺少 model_name")

    return (
        chat_base_url,
        chat_api_key,
        chat_model_name,
        embedding_base_url,
        embedding_api_key,
        embedding_model_name,
    )


def _initialize_lang_llm(
    chat_name: str,
    embedding_name: str
) -> tuple[ChatOpenAI, OpenAIEmbeddings]:
    try:
        chat_config, embedding_config = _resolve_model_configs(chat_name, embedding_name)
        (
            chat_base_url,
            chat_api_key,
            chat_model_name,
            embedding_base_url,
            embedding_api_key,
            embedding_model_name,
        ) = _resolve_model_values(chat_config, embedding_config)

        if chat_name == "ollama" or embedding_name == "ollama":
            os.environ["API_KEY"] = "NA"

        chat_api_key_secret = SecretStr(chat_api_key)
        embedding_api_key_secret = SecretStr(embedding_api_key)

        llm_chat = ChatOpenAI(
            base_url=chat_base_url,
            api_key=chat_api_key_secret,
            model=chat_model_name,
            temperature=DEFAULT_TEMPERATURE,
            timeout=30,
            max_retries=2,
        )

        llm_embedding = OpenAIEmbeddings(
            base_url=embedding_base_url,
            api_key=embedding_api_key_secret,
            model=embedding_model_name,
        )

        logger.info(f"成功初始化 LangChain Chat({chat_name})/Embedding({embedding_name})")
        return llm_chat, llm_embedding

    except ValueError as ve:
        logger.error(f"LLM配置错误: {str(ve)}")
        raise LLMInitializationError(f"LLM配置错误: {str(ve)}")
    except Exception as e:
        logger.error(f"初始化LLM失败: {str(e)}")
        raise LLMInitializationError(f"初始化LLM失败: {str(e)}")


def _get_openai_like_cls() -> type[Any]:
    try:
        module = importlib.import_module("llama_index.llms.openai_like")
        return getattr(module, "OpenAILike")
    except (ImportError, AttributeError):
        from llama_index.llms.openai import OpenAI
        return OpenAI


def _initialize_llama_llm(
    chat_name: str,
    embedding_name: str
) -> tuple[Any, OpenAILikeEmbedding]:
    try:
        chat_config, embedding_config = _resolve_model_configs(chat_name, embedding_name)
        (
            chat_base_url,
            chat_api_key,
            chat_model_name,
            embedding_base_url,
            embedding_api_key,
            embedding_model_name,
        ) = _resolve_model_values(chat_config, embedding_config)

        if chat_name == "ollama" or embedding_name == "ollama":
            os.environ["API_KEY"] = "NA"

        openai_like_cls = _get_openai_like_cls()
        llm_chat = openai_like_cls(
            model=chat_model_name,
            api_base=chat_base_url,
            api_key=chat_api_key,
            temperature=DEFAULT_TEMPERATURE,
        )

        llm_embedding = OpenAILikeEmbedding(
            model_name=embedding_model_name,
            api_base=embedding_base_url,
            api_key=embedding_api_key,
        )

        logger.info(f"成功初始化 LlamaIndex Chat({chat_name})/Embedding({embedding_name})")
        return llm_chat, llm_embedding

    except ValueError as ve:
        logger.error(f"LLM配置错误: {str(ve)}")
        raise LLMInitializationError(f"LLM配置错误: {str(ve)}")
    except Exception as e:
        logger.error(f"初始化LLM失败: {str(e)}")
        raise LLMInitializationError(f"初始化LLM失败: {str(e)}")


def lang_llm(
    chat_name: str = DEFAULT_CHAT_NAME,
    embedding_name: str = DEFAULT_EMBEDDING_NAME
) -> tuple[ChatOpenAI, OpenAIEmbeddings]:
    """获取 LangChain/LangGraph 使用的 LLM 实例。"""
    try:
        return _initialize_lang_llm(chat_name, embedding_name)
    except LLMInitializationError as e:
        logger.warning(f"使用默认配置重试: {str(e)}")
        if chat_name != DEFAULT_CHAT_NAME or embedding_name != DEFAULT_EMBEDDING_NAME:
            return _initialize_lang_llm(DEFAULT_CHAT_NAME, DEFAULT_EMBEDDING_NAME)
        raise e


def llama_llm(
    chat_name: str = DEFAULT_CHAT_NAME,
    embedding_name: str = DEFAULT_EMBEDDING_NAME
) -> tuple[Any, OpenAILikeEmbedding]:
    """获取 LlamaIndex 使用的 LLM 实例。"""
    try:
        return _initialize_llama_llm(chat_name, embedding_name)
    except LLMInitializationError as e:
        logger.warning(f"使用默认配置重试: {str(e)}")
        if chat_name != DEFAULT_CHAT_NAME or embedding_name != DEFAULT_EMBEDDING_NAME:
            return _initialize_llama_llm(DEFAULT_CHAT_NAME, DEFAULT_EMBEDDING_NAME)
        raise e



# 示例使用
if __name__ == "__main__":
    try:
        # 测试不同类型的LLM初始化
        llm_openai, llm_embedding = lang_llm("qwen", "qwen")
        llama_openai, llama_embedding = llama_llm("qwen", "qwen")

        # 测试无效类型
        llm_invalid = lang_llm("invalid_type", "invalid_type")
    except LLMInitializationError as e:
        logger.error(f"程序终止: {str(e)}")
