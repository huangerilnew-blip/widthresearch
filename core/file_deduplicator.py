#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
文件去重器

基于 TF-IDF 和余弦相似度的文档内容去重
支持多种文件格式：.md, .json, .pdf, .html
"""

import os
import hashlib
import logging
from typing import List, Dict, Set, Tuple
from pathlib import Path
from core.log_config import setup_logger

logger = setup_logger(__name__)

# 尝试导入 sklearn，如果不可用则使用 MD5 回退方案
TfidfVectorizer = None
cosine_similarity = None
np = None
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn 未安装，将使用 MD5 哈希去重作为回退方案")


class FileDeduplicator:
    """文件去重器
    
    使用 TF-IDF + 余弦相似度进行内容去重
    若 sklearn 不可用，退化为 MD5 哈希去重
    """
    
    def __init__(self, similarity_threshold: float = 0.8, batch_size: int = 500):
        """初始化去重器
        
        Args:
            similarity_threshold: 余弦相似度阈值（默认 0.8）
            batch_size: 批处理大小，超过此数量分批处理以保护内存
        """
        self.similarity_threshold = similarity_threshold
        self.batch_size = batch_size
        self.allowed_extensions = {'.md', '.json', '.pdf'}
        
        logger.info(
            f"初始化 FileDeduplicator: threshold={similarity_threshold}, "
            f"sklearn={'可用' if SKLEARN_AVAILABLE else '不可用'}"
        )
    
    def _read_file_content(self, file_path: str) -> str:
        """读取文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容（字符串）
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"读取文件失败 {file_path}: {e}")
            return ""

    def _filter_valid_paths(self, file_paths: List[str]) -> Tuple[List[str], List[str]]:
        """过滤有效文件路径

        Args:
            file_paths: 文件路径列表

        Returns:
            Tuple[List[str], List[str]]: (有效路径, 无效路径)
        """
        valid_paths: List[str] = []
        invalid_paths: List[str] = []

        for file_path in file_paths:
            if not file_path:
                continue

            ext = Path(file_path).suffix.lower()
            if ext not in self.allowed_extensions:
                logger.debug(f"跳过不支持的文件类型: {file_path}")
                invalid_paths.append(file_path)
                continue

            if not os.path.exists(file_path):
                logger.warning(f"文件不存在，跳过: {file_path}")
                invalid_paths.append(file_path)
                continue

            if os.path.getsize(file_path) == 0:
                logger.debug(f"跳过空文件: {file_path}")
                invalid_paths.append(file_path)
                continue

            valid_paths.append(file_path)

        return valid_paths, invalid_paths
    
    def _calculate_md5(self, content: str) -> str:
        """计算内容的 MD5 哈希值
        
        Args:
            content: 文件内容
            
        Returns:
            MD5 哈希值
        """
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _md5_deduplicate(self, file_paths: List[str]) -> List[str]:
        """基于 MD5 的硬去重（回退方案）
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            去重后的文件路径列表
        """
        logger.info(f"使用 MD5 哈希去重: {len(file_paths)} 个文件")
        
        seen_hashes: Set[str] = set()
        unique_files: List[str] = []
        duplicates: List[str] = []
        
        for file_path in file_paths:
            content = self._read_file_content(file_path)
            if not content:
                duplicates.append(file_path)
                continue
            
            content_hash = self._calculate_md5(content)
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_files.append(file_path)
            else:
                duplicates.append(file_path)
                logger.debug(f"检测到重复文件（MD5）: {file_path}")
        
        logger.info(f"MD5 去重完成: 保留 {len(unique_files)} 个, 未输出 {len(duplicates)} 个")
        return unique_files
    
    def _tfidf_deduplicate(self, file_paths: List[str]) -> List[str]:
        """基于 TF-IDF 和余弦相似度的内容去重
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            去重后的文件路径列表
        """
        if not SKLEARN_AVAILABLE:
            return self._md5_deduplicate(file_paths)
        
        logger.info(f"使用 TF-IDF 去重: {len(file_paths)} 个文件, 阈值={self.similarity_threshold}")
        
        # 特殊文件：context7_grep.json 只做 MD5 去重
        special_files = [fp for fp in file_paths if os.path.basename(fp) == "context7_grep.json"]
        normal_files = [fp for fp in file_paths if os.path.basename(fp) != "context7_grep.json"]
        
        if special_files:
            logger.info(f"检测到 {len(special_files)} 个 context7_grep.json，单独使用 MD5 去重")
            special_deduped = self._md5_deduplicate(special_files)
        else:
            special_deduped = []
        
        if not normal_files:
            return special_deduped
        
        # 分批处理以保护内存
        if len(normal_files) > self.batch_size:
            logger.info(f"文件数量超过 {self.batch_size}，分批处理")
            batches = [
                normal_files[i:i + self.batch_size]
                for i in range(0, len(normal_files), self.batch_size)
            ]
            
            all_unique = []
            for i, batch in enumerate(batches):
                logger.info(f"处理批次 {i+1}/{len(batches)}: {len(batch)} 个文件")
                unique_batch = self._tfidf_deduplicate_batch(batch)
                all_unique.extend(unique_batch)
            
            # 合并特殊文件和普通文件
            return special_deduped + all_unique
        
        # 单批处理
        unique_normal = self._tfidf_deduplicate_batch(normal_files)
        return special_deduped + unique_normal
    
    def _tfidf_deduplicate_batch(self, file_paths: List[str]) -> List[str]:
        """处理单个批次的 TF-IDF 去重
        
        Args:
            file_paths: 文件路径列表
            
        Returns:
            去重后的文件路径列表
        """
        if not SKLEARN_AVAILABLE or TfidfVectorizer is None or cosine_similarity is None:
            return self._md5_deduplicate(file_paths)

        # 读取文件内容
        contents = []
        valid_paths = []
        
        for file_path in file_paths:
            content = self._read_file_content(file_path)
            if content.strip():  # 过滤空文件
                contents.append(content)
                valid_paths.append(file_path)
            else:
                logger.debug(f"跳过空文件: {file_path}")
        
        if len(valid_paths) == 0:
            return []
        
        if len(valid_paths) == 1:
            return valid_paths
        
        try:
            # 构建 TF-IDF 向量
            vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words=None,  # 不移除停用词（支持中英文）
                ngram_range=(1, 2)  # unigram + bigram
            )
            
            tfidf_matrix = vectorizer.fit_transform(contents)
            
            # 计算余弦相似度矩阵
            similarity_matrix = cosine_similarity(tfidf_matrix)
            
            # 去重逻辑：保留第一个遇到的文档，删除后续相似的
            to_keep = set(range(len(valid_paths)))
            
            for i in range(len(valid_paths)):
                if i not in to_keep:
                    continue
                
                for j in range(i + 1, len(valid_paths)):
                    if j not in to_keep:
                        continue
                    
                    similarity = similarity_matrix[i, j]
                    
                    if similarity >= self.similarity_threshold:
                        to_keep.discard(j)
                        logger.debug(
                            f"检测到相似文件 (sim={similarity:.3f}): "
                            f"{os.path.basename(valid_paths[i])} vs "
                            f"{os.path.basename(valid_paths[j])}"
                        )
            
            unique_files = [valid_paths[i] for i in sorted(to_keep)]
            
            removed_count = len(valid_paths) - len(unique_files)
            logger.info(f"TF-IDF 去重完成: 保留 {len(unique_files)} 个, 未输出 {removed_count} 个")
            
            return unique_files
            
        except Exception as e:
            logger.error(f"TF-IDF 去重失败，回退到 MD5 方案: {e}")
            return self._md5_deduplicate(valid_paths)

    def deduplicate_file_list(self, file_paths: List[str]) -> Tuple[List[str], List[str]]:
        """对文件路径列表进行去重（不做物理删除）

        Args:
            file_paths: 文件路径列表

        Returns:
            Tuple[List[str], List[str]]: (保留的文件列表, 未输出的文件列表)
        """
        if not file_paths:
            return [], []

        valid_paths, invalid_paths = self._filter_valid_paths(file_paths)

        if not valid_paths:
            return [], invalid_paths

        unique_files = self._tfidf_deduplicate(valid_paths)
        unique_set = set(unique_files)
        duplicate_files = [path for path in valid_paths if path not in unique_set]
        duplicate_files.extend(invalid_paths)

        logger.info(
            f"列表去重完成: 输入 {len(file_paths)} 个, 输出 {len(unique_files)} 个, "
            f"未输出 {len(duplicate_files)} 个"
        )

        return unique_files, duplicate_files

    def deduplicate_against_reference(
        self,
        reference_paths: List[str],
        candidate_paths: List[str]
    ) -> Tuple[List[str], List[str]]:
        """基于参考集合对候选集合去重（不做物理删除）

        Args:
            reference_paths: 参考文件路径列表（优先保留）
            candidate_paths: 候选文件路径列表

        Returns:
            Tuple[List[str], List[str]]: (保留的候选路径, 未输出的候选路径)
        """
        if not candidate_paths:
            return [], []

        valid_reference, _ = self._filter_valid_paths(reference_paths)
        valid_candidates, invalid_candidates = self._filter_valid_paths(candidate_paths)

        if not valid_candidates:
            return [], invalid_candidates

        combined_paths = valid_reference + valid_candidates
        unique_files = self._tfidf_deduplicate(combined_paths)
        unique_set = set(unique_files)

        kept_candidates = [path for path in valid_candidates if path in unique_set]
        removed_candidates = [path for path in valid_candidates if path not in unique_set]
        removed_candidates.extend(invalid_candidates)

        logger.info(
            f"跨集合去重完成: 候选 {len(candidate_paths)} 个, 输出 {len(kept_candidates)} 个, "
            f"未输出 {len(removed_candidates)} 个"
        )

        return kept_candidates, removed_candidates
    
    def deduplicate(
        self,
        directory: str,
        remove_duplicates: bool = False
    ) -> Tuple[List[str], List[str]]:
        """对目录中的文件进行去重
        
        Args:
            directory: 目标目录
            remove_duplicates: 是否物理删除重复文件（默认 False）
            
        Returns:
            Tuple[List[str], List[str]]: (保留的文件列表, 删除的文件列表)
        """
        if not os.path.exists(directory):
            logger.warning(f"目录不存在: {directory}")
            return [], []
        
        # 扫描目录
        all_files = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                ext = Path(file_path).suffix.lower()
                
                # 检查后缀
                if ext in self.allowed_extensions:
                    # 检查文件大小
                    if os.path.getsize(file_path) == 0:
                        logger.debug(f"删除空文件: {file_path}")
                        try:
                            os.remove(file_path)
                        except Exception as e:
                            logger.warning(f"删除空文件失败 {file_path}: {e}")
                    else:
                        all_files.append(file_path)
        
        logger.info(f"扫描到 {len(all_files)} 个有效文件（已过滤空文件）")
        
        if not all_files:
            return [], []
        
        # 执行去重
        unique_files = self._tfidf_deduplicate(all_files)
        duplicate_files = list(set(all_files) - set(unique_files))
        
        # 物理删除重复文件
        if remove_duplicates and duplicate_files:
            logger.info(f"开始删除 {len(duplicate_files)} 个重复文件")
            for dup_file in duplicate_files:
                try:
                    os.remove(dup_file)
                    logger.debug(f"已删除: {dup_file}")
                except Exception as e:
                    logger.warning(f"删除文件失败 {dup_file}: {e}")
        
        return unique_files, duplicate_files


# 测试代码
if __name__ == "__main__":
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    logger.debug("=" * 80)
    logger.info("FileDeduplicator 测试")
    logger.debug("=" * 80)
    
    if SKLEARN_AVAILABLE:
        logger.info("✓ scikit-learn 可用: 是")
    else:
        logger.warning("✓ scikit-learn 可用: 否（将使用 MD5 回退）")
    
    # 创建去重器实例
    deduplicator = FileDeduplicator(similarity_threshold=0.8)
    logger.info("✓ FileDeduplicator 初始化成功")
    logger.debug(f"  - 相似度阈值: {deduplicator.similarity_threshold}")
    logger.debug(f"  - 批处理大小: {deduplicator.batch_size}")
    logger.debug(f"  - 支持的文件类型: {deduplicator.allowed_extensions}")
    
    logger.debug("=" * 80)
    logger.info("测试通过！")
    logger.debug("=" * 80)
