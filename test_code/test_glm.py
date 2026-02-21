import asyncio
from langchain_core.messages import HumanMessage

from core.llms import LLMInitializationError, lang_llm


async def main() -> None:
    print("--- GLM Connectivity Test ---")
    try:
        llm = lang_llm("glm", "bge")[0]
    except LLMInitializationError as exc:
        print(f"LLM 初始化失败: {exc}")
        return

    messages = [
        HumanMessage(content="你好，GLM！请介绍一下你自己。"),
    ]

    print("Status: Sending async request...")
    try:
        response = await llm.ainvoke(messages)
    except Exception as exc:
        print(f"Test Failed: {exc}")
        return

    print("Result:")
    content = getattr(response, "content", "")
    print(str(content))


if __name__ == "__main__":
    asyncio.run(main())
