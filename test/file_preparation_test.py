import logging

from rag_module import DataPreparationModule


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

dataPath = "../data/cook/"

preparationer = DataPreparationModule(dataPath)
print(preparationer)
res = preparationer.load_documents()
print(res)