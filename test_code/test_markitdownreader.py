from pathlib import Path

from llama_index.readers.markitdown import MarkItDownReader


def main() -> None:
    reader = MarkItDownReader()
    sample_path = Path("/home/qinshan/widthresearch/data/downloads")
    md_files = list(sample_path.glob("*.md"))
    if not md_files:
        print("No markdown files found in data/downloads")
        return

    file_path = md_files[0]
    documents = reader.load_data(file_path=file_path)
    print(f"file={file_path}")
    print(f"document_count={len(documents)}")
    if documents:
        print(f"first_document_length={len(documents[0].text)}")


if __name__ == "__main__":
    main()
