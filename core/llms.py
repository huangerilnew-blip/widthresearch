import os
import logging
from concurrent_log_handler import ConcurrentRotatingFileHandler
from langchain_openai import ChatOpenAI,OpenAIEmbeddings
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
            "model_name": os.getenv("EMBEDDING_MODEL", Config.EMBEDDING_MODEL_NAME)
        },
        "bge": {
            "base_url": Config.VLLM_BASE_URL,
            "api_key": "NA",
            "model_name": "BAAI/bge-m3"
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


def initialize_llm(
    chat_name: str = DEFAULT_CHAT_NAME,
    embedding_name: str = DEFAULT_EMBEDDING_NAME
) -> tuple[ChatOpenAI, OpenAIEmbeddings]:
    """
    初始化LLM实例

    Args:
        chat_name (str): Chat 模型类型
        embedding_name (str): Embedding 模型类型

    Returns:
        ChatOpenAI: 初始化后的LLM实例

    Raises:
        LLMInitializationError: 当LLM初始化失败时抛出
    """
    try:
        if chat_name not in MODEL_CONFIGS["chat"]:
            raise ValueError(
                f"不支持的Chat模型类型: {chat_name}. 可用的类型: {list(MODEL_CONFIGS['chat'].keys())}"
            )
        if embedding_name not in MODEL_CONFIGS["embedding"]:
            raise ValueError(
                f"不支持的Embedding模型类型: {embedding_name}. 可用的类型: {list(MODEL_CONFIGS['embedding'].keys())}"
            )

        chat_config = MODEL_CONFIGS["chat"][chat_name]
        embedding_config = MODEL_CONFIGS["embedding"][embedding_name]

        # 特殊处理ollama类型
        if chat_name == "ollama" or embedding_name == "ollama":
            os.environ["API_KEY"] = "NA"
        # 创建LLM实例
        llm_chat = ChatOpenAI(
            base_url=chat_config["base_url"],
            api_key=chat_config["api_key"],
            model=chat_config["model_name"],
            temperature=DEFAULT_TEMPERATURE,
            timeout=30,  # 添加超时配置（秒）
            max_retries=2  # 添加重试次数
        )

        llm_embedding = OpenAIEmbeddings(
            base_url=embedding_config["base_url"],
            api_key=embedding_config["api_key"],
            model=embedding_config["model_name"],
            deployment=embedding_config["model_name"]
        )

        logger.info(f"成功初始化 Chat({chat_name})/Embedding({embedding_name}) LLM")
        return llm_chat, llm_embedding

    except ValueError as ve:
        logger.error(f"LLM配置错误: {str(ve)}")
        raise LLMInitializationError(f"LLM配置错误: {str(ve)}")
    except Exception as e:
        logger.error(f"初始化LLM失败: {str(e)}")
        raise LLMInitializationError(f"初始化LLM失败: {str(e)}")


def get_llm(
    chat_name: str = DEFAULT_CHAT_NAME,
    embedding_name: str = DEFAULT_EMBEDDING_NAME
) -> tuple[ChatOpenAI, OpenAIEmbeddings]:
    """
    获取LLM实例的封装函数，提供默认值和错误处理

    Args:
        chat_name (str): Chat 模型类型
        embedding_name (str): Embedding 模型类型

    Returns:
        tuple[ChatOpenAI, OpenAIEmbeddings]: LLM实例
    """
    try:
        return initialize_llm(chat_name, embedding_name)
    except LLMInitializationError as e:
        logger.warning(f"使用默认配置重试: {str(e)}")
        if chat_name != DEFAULT_CHAT_NAME or embedding_name != DEFAULT_EMBEDDING_NAME:
            return initialize_llm(DEFAULT_CHAT_NAME, DEFAULT_EMBEDDING_NAME)
        raise e # 如果默认配置也失败，则抛出异常



# 示例使用
if __name__ == "__main__":
    try:
        # 测试不同类型的LLM初始化
        llm_openai, llm_embedding = get_llm("qwen", "qwen")

        # 测试无效类型
        llm_invalid = get_llm("invalid_type", "invalid_type")
    except LLMInitializationError as e:
        logger.error(f"程序终止: {str(e)}")
