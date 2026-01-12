#数据预处理
import uuid
from ast import Try
import hashlib
from pathlib import Path
from typing import List, Dict
import logging
from langchain_core.documents import Document
from langchain.text_splitter import MarkdownHeaderTextSplitter

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class DataPreparationModule:

    CATEGORY_MAPPING = {
        'meat_dish': '荤菜',
        'vegetable_dish': '素菜',
        'soup': '汤品',
        'dessert': '甜品',
        'breakfast': '早餐',
        'staple': '主食',
        'aquatic': '水产',
        'condiment': '调料',
        'drink': '饮品'
    }
    CATEGORY_LABELS = list(set(CATEGORY_MAPPING.values()))
    DIFFICULTY_LABELS = ['非常简单', '简单', '中等', '困难', '非常困难']

    def __init__(self, data_path:str):
        self.data_path = data_path
        self.documents: List[Document] = []  # 父文档
        self.chunks: List[Document] = []     # 子文档
        self.parent_child_map: Dict[str, str] = {}  # 子块ID -> 父文档ID的映射

    def load_documents(self) -> List[Document]:
        logger.info(f"正在从 {self.data_path} 加载文档...")
        documents = []
        data_path_obj = Path(self.data_path)
        print(data_path_obj)
        for md_file in data_path_obj.rglob("*.md"):
            logger.info(f"文档路径：{md_file}")
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    # 为每个父文档分配确定性的唯一ID（基于数据根目录的相对路径）
                    try:
                        data_root = Path(self.data_path).resolve()
                        relative_path = Path(md_file).resolve().relative_to(data_root).as_posix()
                    except Exception:
                        relative_path = Path(md_file).as_posix()
                    parent_id = hashlib.md5(relative_path.encode("utf-8")).hexdigest()

                    # 创建Document对象
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": str(md_file),
                            "parent_id": parent_id,
                            "doc_type": "parent"  # 标记为父文档
                        }
                    )
                    documents.append(doc)

            except Exception as e:
                logger.warning(f"读取文件 {md_file} 失败: {e}")

        # 增强文档元数据
        for doc in documents:
            self._enhance_metadata(doc)

        self.documents = documents
        logger.info(f"成功加载 {len(documents)} 个文档")
        return documents

    def _enhance_metadata(self, doc: Document):
        """
        增强文档元数据

        Args:
            doc: 需要增强元数据的文档
        """
        file_path = Path(doc.metadata.get('source', ''))
        path_parts = file_path.parts

        # 提取菜品分类
        doc.metadata['category'] = '其他'
        for key, value in self.CATEGORY_MAPPING.items():
            if key in path_parts:
                doc.metadata['category'] = value
                break

        # 提取菜品名称
        doc.metadata['dish_name'] = file_path.stem

        # 分析难度等级
        content = doc.page_content
        if '★★★★★' in content:
            doc.metadata['difficulty'] = '非常困难'
        elif '★★★★' in content:
            doc.metadata['difficulty'] = '困难'
        elif '★★★' in content:
            doc.metadata['difficulty'] = '中等'
        elif '★★' in content:
            doc.metadata['difficulty'] = '简单'
        elif '★' in content:
            doc.metadata['difficulty'] = '非常简单'
        else:
            doc.metadata['difficulty'] = '未知'

    def chunk_documents(self) -> List[Document]:
        logger.info(f"正在对文档进行分块...")
        if not self.documents:
            ValueError("请先加载文档")
        
        # 使用Markdown标题分割器
        chunks = self._markdown_header_split()
        # 为每个chunk添加基础元数据
        for i, chunk in enumerate(chunks):
            if 'chunk_id' not in chunk.metadata:
                # 如果没有chunk_id（比如分割失败的情况），则生成一个
                chunk.metadata['chunk_id'] = str(uuid.uuid4())
            chunk.metadata['batch_index'] = i  # 在当前批次中的索引
            chunk.metadata['chunk_size'] = len(chunk.page_content)

        self.chunks = chunks
        logger.info(f"Markdown分块完成，共生成 {len(chunks)} 个chunk")
        return chunks

    
    def _markdown_header_split(self) -> List[Document]:
        """
        使用Markdown标题分割文档
        """
        # 定义要分割的标题层级
        headers_to_split_on = [
            ("#", "主标题"),      # 菜品名称
            ("##", "二级标题"),   # 必备原料、计算、操作等
            ("###", "三级标题")   # 简易版本、复杂版本等
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers=False)
        all_chunks = []
        for doc in self.documents:
            try:
                content_preview = doc.page_content[:200]
                has_headers = any(line.strip().startswith('#') for line in content_preview.split('\n'))
                if not has_headers:
                    logger.warning(f"文档 {doc.metadata.get('dish_name', '未知')} 内容中没有发现Markdown标题")
                    logger.debug(f"内容预览: {content_preview}")
                # 对每个文档进行Markdown分割
                md_chunks = markdown_splitter.split_text(doc.page_content)

                logger.debug(f"文档 {doc.metadata.get('dish_name', '未知')} 分割成 {len(md_chunks)} 个chunk")

                # 如果没有分割成功，说明文档可能没有标题结构
                if len(md_chunks) <= 1:
                    logger.warning(f"文档 {doc.metadata.get('dish_name', '未知')} 未能按标题分割，可能缺少标题结构")

                # 为每个子块建立与父文档的关系
                parent_id = doc.metadata["parent_id"]

                for i, chunk in enumerate(md_chunks):
                    # 为子块分配唯一ID
                    child_id = str(uuid.uuid4())

                    # 合并原文档元数据和新的标题元数据
                    chunk.metadata.update(doc.metadata)
                    chunk.metadata.update({
                        "chunk_id": child_id,
                        "parent_id": parent_id,
                        "doc_type": "child",  # 标记为子文档
                        "chunk_index": i      # 在父文档中的位置
                    })

                    # 建立父子映射关系
                    self.parent_child_map[child_id] = parent_id
                all_chunks.extend(md_chunks)
            except Exception as e:
                logger.warning(f"对文档 {doc.metadata.get('source', '')} 进行Markdown标题分割失败: {e}")
        logger.info(f"Markdown结构分割完成，生成 {len(all_chunks)} 个结构化块")
        return all_chunks