
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompt
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model
from langchain_core.output_parsers import StrOutputParser

# 总结服务类：用户提问，搜索参考资料，将提问和参考资料交给模型，让模型总结回复

class RagSummarizeService:
    def __init__(self):
        self.vector_store = VectorStoreService() # 向量存储
        self.retriever = self.vector_store.get_retriever() # 向量检索
        self.prompt_text = load_rag_prompt() # RAG总结提示词
        self.prompt_template = PromptTemplate.from_template(self.prompt_text) # 提示词模板
        self.model = chat_model
        self.chain = self.__init__chain()

    def __init__chain(self):
        chain = self.prompt_template | self.model | StrOutputParser()
        return chain

    # 检索函数 -- 用于查找和问题相似的片段
    def retriever_docs(self, query):  # 输出是 list[Document]
        return self.retriever.invoke(query)

    # 总结 -- 核心功能
    def rag_summarize(self, query):

        context_docs = self.retriever_docs(query)

        # 参考资料拼接
        context = ''
        counter = 0
        for doc in context_docs:
            counter += 1
            context += f'【参考资料{counter}】：参考资料：{doc.page_content}  |  参考元数据：{doc.metadata} \n'

        return self.chain.invoke(
            {
                'input': query,
                'context':context 
            }
        )


if __name__ == "__main__":
    rag = RagSummarizeService()
    print(rag.rag_summarize('小户型适合哪些扫地机器人'))


# 如果想要测试
# cd D:\01\ai\python\rag-gsg\agent
# python -m rag.rag_service







