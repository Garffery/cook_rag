import logging

from rag_module import DataPreparationModule, IndexConstructionModule


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

dataPath = "../data/cook/"

preparationer = DataPreparationModule(dataPath)
print(preparationer)
preparationer.load_documents()
res = preparationer.chunk_documents()
# for chunk in res:
#     print("===="*30)
#     print(chunk)



# 向量数据构建
indexModule = IndexConstructionModule()
vectorStore = indexModule.build_vector_index(res)
res = vectorStore.similarity_search("番茄炒鸡蛋", 1)
print(res)