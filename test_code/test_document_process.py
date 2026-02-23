import asyncio
import asyncio
from pathlib import Path

from core.config import Config
from core.llms import llama_llm
from core.rag.document_processor import DocumentProcessor


async def main() -> None:
    llm_chat, embedding = llama_llm(
        chat_name="llama" ,
        embedding_name=Config.LLM_EMBEDDING,
    )
    processor = DocumentProcessor(
        embedding_model=embedding,
        llm=llm_chat,
    )

    downloads_dir = Path(Config.DOC_SAVE_PATH)
    md_files = list(downloads_dir.glob("*.md"))
    if not md_files:
        print(f"No markdown files found in {downloads_dir}")
        return

    sample_path = md_files[0]
    documents = [
        {
            "extra": {"saved_path": str(sample_path)},
            "source": "test",
            "title": sample_path.stem,
            "url": str(sample_path),
        }
    ]

    nodes = await processor.get_nodes(documents)
    print(f"input_file={sample_path}")
    print(f"node_count={len(nodes)}")
    for index, node in enumerate(nodes):
        metadata = getattr(node, "metadata", {}) or {}
        content = node.get_content()
        questions = metadata.get("questions_this_excerpt_can_answer", [])
        if not isinstance(questions, list):
            questions = [questions]
        print(f"node_index={index}")
        print(f"original_content={content}")
        print(f"rewritten_questions={questions}")


if __name__ == "__main__":
    asyncio.run(main())
