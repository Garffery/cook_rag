"""
@description: 索引构建模块
"""
import logging

from langchain_huggingface import HuggingFaceEmbeddings

logger = logging.getLogger(__name__)
class IndexConstructionModule:

    def __init__(self,model_name: str = "BAAI/bge-small-zh-v1.5", index_save_path: str = "./vector_index"):
        self.model_name = model_name
        self.index_save_path = index_save_path
        self.embeddings = None
        self.vectorstore = None
        self.setup_embeddings()

    def setup_embeddings(self):
        """初始化嵌入模型"""
        logger.info(f"正在初始化嵌入模型: {self.model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        logger.info("嵌入模型初始化完成")