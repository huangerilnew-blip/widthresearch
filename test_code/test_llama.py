from core.config import Config
from core.llms import llama_llm


def main() -> None:
    llm_chat, _ = llama_llm(
        chat_name="llama",
        embedding_name=Config.LLM_EMBEDDING,
    )
    prompt = "请用一句话自我介绍。"
    try:
        response = llm_chat.complete(prompt)
    except Exception as exc:
        print(f"llama_complete_error={exc}")
        return

    text = getattr(response, "text", None)
    if text is None:
        text = str(response)
    print(f"prompt={prompt}")
    print(f"response={text}")


if __name__ == "__main__":
    main()
