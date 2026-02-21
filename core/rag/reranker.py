import asyncio
import logging
import os
from typing import Any, Awaitable, Dict, List, Optional, cast

import httpx
from tei_client import HttpClient

from concurrent_log_handler import ConcurrentRotatingFileHandler
from core.config import Config

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


class BGEReranker:
    """BGE Reranker 类，使用 tei_client 调用 TEI 部署的 bge-reranker"""
    
    def __init__(
        self,
        base_url: str = Config.RERANK_BASE_URL,
        batch_size: int = Config.RERANK_BATCH_SIZE,
        max_concurrent: int = Config.RERANK_MAX_CONCURRENT
    ):
        """初始化 BGE Reranker
        
        Args:
            base_url: TEI API 地址
            batch_size: 批处理大小（保留参数以兼容，但 TEI 本身支持批量）
            max_concurrent: 最大并发请求数（保留参数以兼容）
        """
        self.base_url = base_url or Config.RERANK_BASE_URL
        self.backend: Optional[str] = None
        self.client = HttpClient(url=self.base_url)
        self.vllm_client: Optional[httpx.AsyncClient] = None
        self.vllm_model_id = os.getenv("VLLM_RERANK_MODEL_ID", "")

        logger.info(f"初始化 BGEReranker: base_url={self.base_url}")

    async def _detect_backend(self) -> None:
        if self.backend:
            return
        async with httpx.AsyncClient(base_url=self.base_url, timeout=10.0) as probe_client:
            try:
                response = await probe_client.get("/info")
                if response.status_code == 200:
                    payload = response.json()
                    if isinstance(payload, dict) and payload.get("model_type"):
                        self.backend = "tei"
                        return
            except Exception:
                pass

            try:
                response = await probe_client.get("/v1/models")
                if response.status_code == 200:
                    self.backend = "vllm"
                    return
            except Exception:
                pass

        raise RuntimeError(f"无法识别 rerank 服务类型: {self.base_url}")

    async def _get_vllm_client(self) -> httpx.AsyncClient:
        if self.vllm_client is None:
            self.vllm_client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)
        return self.vllm_client

    async def _resolve_vllm_model_id(self) -> str:
        if self.vllm_model_id:
            return self.vllm_model_id
        vllm_client = await self._get_vllm_client()
        response = await vllm_client.get("/v1/models")
        response.raise_for_status()
        payload = response.json()
        data = payload.get("data", []) if isinstance(payload, dict) else []
        if not data:
            raise RuntimeError("vLLM /v1/models 未返回任何模型")
        model_id = data[0].get("id")
        if not model_id:
            raise RuntimeError("vLLM /v1/models 返回结果缺少 model id")
        self.vllm_model_id = model_id
        return model_id

    def _parse_scores(self, items: List[Any]) -> List[Dict[str, float]]:
        rerank_results = []
        for item in items:
            if isinstance(item, dict):
                idx = item.get("index")
                score = item.get("score") if "score" in item else item.get("relevance_score")
            elif isinstance(item, (tuple, list)) and len(item) >= 2:
                idx, score = item[0], item[1]
            else:
                idx = getattr(item, "index", None)
                score = getattr(item, "score", None)
                if idx is None or score is None:
                    logger.warning(f"无法解析 rerank 结果项: {item}")
                    continue
            if idx is None or score is None:
                logger.warning(f"rerank 结果缺少 index/score: {item}")
                continue
            try:
                parsed_index = int(idx)
                parsed_score = float(score)
            except (TypeError, ValueError):
                logger.warning(f"rerank 结果 index/score 无法转换: {item}")
                continue
            rerank_results.append({
                "index": parsed_index,
                "score": parsed_score
            })
        rerank_results.sort(key=lambda x: x["score"], reverse=True)
        return rerank_results
    
    async def rerank_async(self, query: str, documents: List[str]) -> List[Dict[str, float]]:
        """异步对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 待重排序的文档列表
            
        Returns:
            重排序结果列表，每个元素包含 {"index": int, "score": float}
            按分数从高到低排序
        """
        if not documents:
            logger.warning("文档列表为空，跳过 rerank")
            return []
        
        try:
            logger.info(f"开始异步 rerank，查询: {query[:50]}..., 文档数量: {len(documents)}")
            await self._detect_backend()
            if self.backend == "tei":
                result = await self.client.async_rerank(query=query, texts=documents)
                ranks = getattr(result, "ranks", result)
                rerank_results = self._parse_scores(list(ranks))
            else:
                vllm_client = await self._get_vllm_client()
                model_id = await self._resolve_vllm_model_id()
                response = await vllm_client.post(
                    "/v1/rerank",
                    json={
                        "model": model_id,
                        "query": query,
                        "documents": documents,
                    },
                )
                response.raise_for_status()
                payload = response.json()
                results = payload.get("results", []) if isinstance(payload, dict) else []
                rerank_results = self._parse_scores(list(results))

            logger.info(f"异步 Rerank 完成，返回 {len(rerank_results)} 个结果")
            return rerank_results

        except Exception as e:
            logger.error(f"异步 Rerank 过程出错: {e}")
            import traceback
            traceback.print_exc()
            return [{"index": i, "score": 0.5} for i in range(len(documents))]
    
    def rerank(self, query: str, documents: List[str]) -> List[Dict[str, float]]:
        """同步接口：对文档进行重排序
        
        Args:
            query: 查询文本
            documents: 待重排序的文档列表
            
        Returns:
            重排序结果列表，每个元素包含 {"index": int, "score": float}
            按分数从高到低排序
        """
        # 在同步环境中运行异步方法
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.rerank_async(query, documents))
    
    async def close(self):
        """关闭 TEI 客户端"""
        if self.client is not None:
            close_method = getattr(self.client, "close", None)
            if callable(close_method):
                result = close_method()
                if asyncio.iscoroutine(result):
                    await cast(Awaitable[object], result)
                logger.info("BGEReranker TEI 客户端已关闭")
        if self.vllm_client is not None:
            await self.vllm_client.aclose()
            logger.info("BGEReranker vLLM 客户端已关闭")
    
    def __del__(self):
        """析构函数，确保客户端关闭"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.close())
            else:
                loop.run_until_complete(self.close())
        except Exception:
            pass


# 测试代码
if __name__ == "__main__":
    async def test_reranker():
        # 测试 BGEReranker
        reranker = BGEReranker()
        
        query = "人工智能在医疗领域的应用"
        documents = [
            "人工智能技术在医疗诊断中发挥着重要作用",
            "机器学习算法可以帮助医生更准确地诊断疾病",
            "今天天气很好，适合出去玩",
            "深度学习在图像识别领域取得了突破性进展",
            "AI 辅助医疗影像分析提高了诊断准确率",
            "自然语言处理技术在电子病历分析中的应用"
        ]
        
        results = await reranker.rerank_async(query, documents)
        
        print("Rerank 结果:")
        for item in results:
            doc_index = int(item["index"])
            print(f"  文档 {doc_index}: {documents[doc_index][:30]}... (分数: {item['score']:.4f})")
        
        await reranker.close()
    
    # 运行测试
    asyncio.run(test_reranker())
