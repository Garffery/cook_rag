#数据预处理
import hashlib
from pathlib import Path
from typing import List, Dict
import logging
from langchain_core.documents import Document

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
        self.chuck: List[Document] = []     # 子文档
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