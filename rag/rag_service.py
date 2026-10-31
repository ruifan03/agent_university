
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompt
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model
from langchain_core.output_parsers import StrOutputParser
import os
from utils.config_handler import chroma_conf

# 总结服务类：用户提问，搜索参考资料，将提问和参考资料交给模型，让模型总结回复

class RagSummarizeService:
    def __init__(self):
        self.vector_store = VectorStoreService() # 向量存储
        self.prompt_text = load_rag_prompt() # RAG总结提示词
        self.prompt_template = PromptTemplate.from_template(self.prompt_text) # 提示词模板
        self.model = chat_model
        self.chain = self.__init__chain()

    def __init__chain(self):
        chain = self.prompt_template | self.model | StrOutputParser()
        return chain

    # 检索函数 -- 用于查找和问题相似的片段
    def retriever_docs(self, query):
        scored_docs = (
            self.vector_store.vector_store
            .similarity_search_with_relevance_scores(
                query,
                k=chroma_conf['k'],
            )
        )
        min_score = chroma_conf['min_relevance_score']
        return [
            (document, score)
            for document, score in scored_docs
            if score >= min_score
        ]

    # 总结 -- 核心功能
    def rag_summarize(self, query):

        scored_docs = self.retriever_docs(query)
        if not scored_docs:
            return '未找到与该问题直接相关的参考资料。'

        # 参考资料拼接
        context = ''
        counter = 0
        source_names = []
        for doc, score in scored_docs:
            counter += 1
            source_name = doc.metadata.get('source_name')
            if not source_name:
                source_name = os.path.basename(doc.metadata.get('source', '未知文件'))
            if source_name not in source_names:
                source_names.append(source_name)
            context += (
                f'【参考资料{counter}】：参考资料：{doc.page_content}'
                f' | 参考来源：{source_name} | 相关性：{score:.3f}\n'
            )

        answer = self.chain.invoke(
            {
                'input': query,
                'context':context 
            }
        )
        sources = '\n'.join(f'- {source}' for source in source_names)
        return f'{answer.strip()}\n\n【参考来源】\n{sources}'


if __name__ == "__main__":
    rag = RagSummarizeService()
    print(rag.rag_summarize('小户型适合哪些扫地机器人'))


# 如果想要测试
# cd D:\01\ai\python\rag-gsg\agent_university
# python -m rag.rag_service





