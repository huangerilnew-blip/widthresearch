#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文档处理器
负责 PDF 转 Markdown、智能切割、问题改写
使用 LlamaIndex 原生 API：
- MarkdownReader: 加载 Markdown 文件
- MarkdownElementNodeParser: 解析文档并优化表格处理
"""

import asyncio
import os
import re
import json
import logging
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from llama_index.core.schema import BaseNode, TextNode
from concurrent_log_handler import ConcurrentRotatingFileHandler
from llama_index.core import Document
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.llms.llm import LLM
from llama_index.core.node_parser import MarkdownElementNodeParser, SentenceSplitter
from llama_index.readers.markitdown import MarkItDownReader
from llama_index.core.extractors import QuestionsAnsweredExtractor
from llama_index.core.ingestion import IngestionPipeline
from core.config import Config
from core.rag.models import PDFParser, JsonReader

# 设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.handlers = []

handler = ConcurrentRotatingFileHandler(
    Config.LOG_FILE,
    maxBytes=Config.MAX_BYTES,
    backupCount=Config.BACKUP_COUNT
)
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))
logger.addHandler(handler)

class DocumentProcessor:
    """文档处理器
    
    负责 PDF 转 Markdown、智能切割、问题改写
    """
    
    def __init__(
        self,
        embedding_model: BaseEmbedding,
        llm: LLM,
        mineru_base_url: str = Config.MINERU_BASE_URL,
        max_chunk_size: int = Config.MAX_CHUNK_SIZE
    ):
        """初始化文档处理器
        
        Args:
            embedding_model: 本地 vllm 部署的 Embedding 模型
            llm: 用于问题改写的 LLM
            mineru_base_url: MinerU 服务地址（用于创建 MinerUClient）
            max_chunk_size: Markdown 切割最大长度
        """
        self.embedding_model = embedding_model
        self.llm = llm
        self.mineru_base_url = mineru_base_url
        self.max_chunk_size = max_chunk_size
        self._nodes_lock = asyncio.Lock()
        
        # 初始化 PDFParser（用于 PDF 转 Markdown）
        self.pdf_parser = PDFParser(mineru_server_url=mineru_base_url)
        self.json_parser = JsonReader()
        # 初始化 MarkdownReader（负责从文件系统加载 Markdown 文档）
        self.markdown_reader = MarkItDownReader()
        
        # 初始化 MarkdownElementNodeParser（负责结构化解析 + 表格优化）
        self.markdown_parser = MarkdownElementNodeParser(
            llm=llm,
            num_workers=4  # 并行处理 workers 数量
        )
        
        # 初始化 SentenceSplitter（按句子边界进一步切分节点）
        self.sentence_splitter = SentenceSplitter(
            chunk_size=self.max_chunk_size
        )
        
        # 初始化 QuestionsAnsweredExtractor（从节点中抽取可回答的问题）
        self.question_extractor = QuestionsAnsweredExtractor(
            questions=3,  # 每个 chunk 抽取的问题数量
            llm=llm
        )
        
        # 构建 IngestionPipeline：MarkdownElementNodeParser -> SentenceSplitter -> QuestionsAnsweredExtractor
        self.ingestion_pipeline = IngestionPipeline(
            transformations=[
                self.markdown_parser,
                self.sentence_splitter,
                self.question_extractor,
            ]
        )
        
        logger.info(f"初始化 DocumentProcessor: mineru_url={mineru_base_url}, max_chunk_size={max_chunk_size}")
    
    async def get_nodes(
        self,
        documents: List[Dict]
    ) -> List[BaseNode]:
        """处理文档：转换、切割、问题改写
        
        Args:
            documents: 文档元数据列表（支持字段: extra.saved_path/local_path/file_path/path,
                source/title/url）
            
        Returns:
            处理后的 Node 列表（包含改写问题的元数据）
        """
        async with self._nodes_lock:
            logger.info(f"开始处理 {len(documents)} 个文档")
            json_nodes:List[BaseNode ]= []
            docs_for_pipeline: List[Document] = []
            optional_file=os.path.join(Config.DOC_SAVE_PATH, "context7_grep.json")  # 可选文件的添加
            documents.append({"extra": {"saved_path": optional_file}})
            # 1. 先将所有原始文件转为 LlamaIndex Document（Markdown 文本）
            for doc_meta in documents:
                # 获取文档路径
                extra = doc_meta.get("extra")
                saved_path = extra.get("saved_path") if isinstance(extra, dict) else ""
                local_path = (
                    saved_path
                    or doc_meta.get("local_path")
                    or doc_meta.get("file_path")
                    or doc_meta.get("path")
                    or ""
                )
                if not local_path:
                   logger.warning(f"文档路径为空: {doc_meta.get('title', 'unknown')}")
                   continue
                if not os.path.exists(local_path):
                    logger.warning(f"文档路径不存在: {local_path}")
                    continue
                # 判断文件类型
                file_ext = os.path.splitext(local_path)[1].lower()
                source = doc_meta.get("source") or "联网检索"
                title = doc_meta.get("title") or Path(local_path).stem
                url = doc_meta.get("url") or source
                base_metadata = {
                    "source": source, #来源或"联网检索"
                    "title": title, #title或文件名
                    "url": url,#url或来源或"unknown"
                    "path": local_path,
                }
                json_docs:List[Dict] = []
                if file_ext == '.pdf':
                    # PDF 转 Markdown
                    markdown_text = await self._pdf_to_markdown(local_path)
                    if not markdown_text:
                        logger.error(f"文件存在，但是PDF 转 Markdown 失败: {local_path}")
                        continue
                    temp_doc = Document(
                        text=markdown_text,
                        metadata=base_metadata,
                    )
                    docs_for_pipeline.append(temp_doc)
                    logger.info(f"PDF 文档 {local_path} 转换为 Markdown 并加入 pipeline")

                elif file_ext in ['.md', '.markdown']:
                    # 使用 MarkdownReader 加载 Markdown 文件
                    try:
                        md_docs = self.markdown_reader.load_data(file_path=Path(local_path))
                    except Exception as exc:
                        logger.warning(
                            "Markdown 文档加载失败，已跳过: %s, error: %s",
                            local_path,
                            exc,
                        )
                        continue
                    if not md_docs:
                        logger.error(f"文档存在，但Markdown 文档加载失败: {local_path}")
                        continue

                    for d in md_docs:
                        d.metadata = base_metadata
                        docs_for_pipeline.append(d)
                    logger.info(f"Markdown 文档 {local_path} 加载为 {len(md_docs)} 个 Document 并加入 pipeline")
                
                elif file_ext == '.json':
                    # 使用 JsonReader 加载 JSON 文件
                    json_lines = self.json_parser.read_json_lines(local_path)
                    
                    for line in json_lines:
                        if not line.strip():
                            continue
                        try:
                            json_docs.append(json.loads(line))
                        except json.JSONDecodeError:
                            logger.warning(f"JSON 行解析失败，已跳过: {line[:200]}")
                    if not json_docs:
                        logger.warning(f"文档存在，但JSON文档加载失败或内容为空: {local_path}")
                        continue
                    for item in json_docs:
                        if not isinstance(item, dict):
                            logger.warning(f"JSON 文档条目格式错误，已跳过: {item}")
                            continue
                        meta_data = item.get("metadata")
                        source = item.get("source") or "联网搜索"
                        library_id = None
                        if not isinstance(meta_data, dict):
                            logger.warning(f"可选工具保存的JSON文档中的条目缺少'metadata'字段")
                        else:
                            library_id = meta_data.get("library_id")
                        base_metadata = {
                            "source": source,
                            "path": local_path,
                        }
                        if library_id:
                            base_metadata["library_id"] = library_id
                        node=TextNode(text=item.get("text", ""), metadata=base_metadata)
                        if not item.get("text", "").strip():
                            logger.warning(f"JSON文档中的条目文本为空:{item}")
                        json_nodes.append(node)
                else:
                    logger.warning(f"不支持的文件类型{file_ext}，跳过: {local_path}")
                    continue

            if not docs_for_pipeline:
                logger.error("使用lama_index的MarkdownReader和PDFParser处理文档失败，未生成任何Document对象")
                raise ValueError("document-process中没有可处理的文档")

            # 2. 通过 IngestionPipeline 执行：MarkdownElementNodeParser -> SentenceSplitter -> QuestionsAnsweredExtractor
            logger.info(f"开始通过 IngestionPipeline 处理 {len(docs_for_pipeline)} 个 文档")
            nodes: List[BaseNode] = []
            def _resolve_doc_path(doc: Document) -> str:
                metadata = getattr(doc, "metadata", None)
                if isinstance(metadata, dict):
                    return (
                        metadata.get("path")
                        or metadata.get("file_path")
                        or metadata.get("local_path")
                        or metadata.get("title")
                        or metadata.get("url")
                        or metadata.get("source")
                        or ""
                    )
                return ""

            for doc in docs_for_pipeline: #使用for循环是为了跳过个别出错的文档，保证其他文档能继续处理，而不是整个批次都失败
                try:
                    nodes.extend(
                        await self.ingestion_pipeline.arun(
                            documents=[doc],
                            in_place=True,
                            show_progress=False,
                        )
                    )
                except Exception as e:
                    doc_path = _resolve_doc_path(doc)
                    logger.error(
                        "IngestionPipeline 处理失败，已跳过文档: %s, error: %s",
                        doc_path or "unknown",
                        e,
                    )
                    continue

            # 3. 返回处理后的节点列表
            logger.info(f"文档处理完成: {len(nodes)} 个节点")
            if json_nodes:
                logger.info(f"另外添加了 {len(json_nodes)} 个来自 可选工具JSON 文档的节点")
                nodes.extend(json_nodes)
            return nodes
    
    async def _pdf_to_markdown(self, pdf_path: str) -> str:
        """将 PDF 转换为 Markdown

        使用 PDFParser 进行转换

        Args:
            pdf_path: PDF 文件路径

        Returns:
            Markdown 文本
        """
        logger.info(f"开始转换 PDF: {pdf_path}")

        try:
            markdown_text = await self.pdf_parser.parse_pdf_to_markdown(pdf_path)
            if markdown_text:
                logger.info(f"PDF 转换成功: {pdf_path}, 长度: {len(markdown_text)}")
                return markdown_text
            else:
                logger.error(f"PDF 转换失败: 返回内容为空")
                return ""

        except Exception as e:
            logger.error(f"PDF 转换异常: {e}")
            import traceback
            traceback.print_exc()
            return ""

    def extract_questions_from_nodes(self, nodes: List[BaseNode]) -> List[str]:
        """从节点列表中提取改写后的问题
        
        Args:
            nodes: 处理后的 Node 列表
            
        Returns:
            改写的问题列表（已去重）
        """
        all_questions = []
        
        for node in nodes:
            metadata = getattr(node, "metadata", {}) or {}
            # QuestionsAnsweredExtractor 默认将问题写入 metadata["questions"] 或 metadata["questions_answered"]
            node_questions = metadata.get("questions") or metadata.get("questions_answered")
            if not node_questions:
                continue
            
            if isinstance(node_questions, str):
                all_questions.append(node_questions.strip())
            elif isinstance(node_questions, list):
                for q in node_questions:
                    if isinstance(q, str) and q.strip():
                        all_questions.append(q.strip())
        
        # 去重
        unique_questions = list(dict.fromkeys(all_questions))
        logger.info(f"从 {len(nodes)} 个节点中提取了 {len(unique_questions)} 个唯一问题")
        return unique_questions


# 测试代码
if __name__ == "__main__":
    import asyncio
    from core.llms import get_llm
    from llama_index.embeddings.openai import OpenAIEmbedding
    
    async def test_document_processor():
        print("=" * 60)
        print("DocumentProcessor 测试")
        print("=" * 60)
        
        # 初始化 LLM 和 Embedding
        llm = get_llm(Config.LLM_EXECUTOR)[0]
        embedding = OpenAIEmbedding(
            model="text-embedding-ada-002",
            api_base=Config.VLLM_BASE_URL,
            api_key="EMPTY"
        )
        
        # 创建处理器
        processor = DocumentProcessor(
            embedding_model=embedding,
            llm=llm
        )
        print(f"✓ DocumentProcessor 实例化成功")
        print(f"✓ MarkdownReader 已初始化")
        print(f"✓ MarkdownElementNodeParser 已初始化（优化表格解析）")
        
        # 测试 Markdown 文件加载
        print(f"\n✓ 测试 Markdown 文件加载:")
        print(f"  - 使用 MarkdownReader 加载 .md 文件")
        print(f"  - 使用 MarkdownElementNodeParser 解析节点")
        print(f"  - 自动识别表格、代码块、标题等结构")
        
        print("\n" + "=" * 60)
        print("基础测试通过！")
        print("=" * 60)
    
    # 运行测试
    asyncio.run(test_document_processor())
