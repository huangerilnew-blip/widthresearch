# -*- coding: utf-8 -*-

import traceback
from llama_index.readers.markitdown import MarkItDownReader


def main() -> None:
    file_path = "/home/qinshan/widthresearch/data/downloads/exa_LangGraph从.md"
    reader = MarkItDownReader()
    try:
        docs = reader.load_data(file_path=file_path)
        print(f"load_data 成功: 文档数={len(docs)}")
        if docs:
            print(f"首个文档长度={len(docs[0].text)}")
    except Exception as exc:
        print("load_data 失败:")
        print(f"{type(exc).__name__}: {exc}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
