
from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompt
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from model.factory import chat_model
from langchain_core.output_parsers import StrOutputParser
import os
import re
from utils.config_handler import chroma_conf
from utils.path_tool import get_abs_path

# 总结服务类：用户提问，搜索参考资料，将提问和参考资料交给模型，让模型总结回复

class RagSummarizeService:
    def __init__(self):
        self.vector_store = VectorStoreService() # 向量存储
        self.prompt_text = load_rag_prompt() # RAG总结提示词
        self.prompt_template = PromptTemplate.from_template(self.prompt_text) # 提示词模板
        self.model = chat_model
        self._keyword_documents = None
        self.query_rewrite_chain = self.__init_query_rewrite_chain()
        self.chain = self.__init__chain()

    def __init_query_rewrite_chain(self):
        prompt_path = get_abs_path('prompts/query_rewrite.txt')
        with open(prompt_path, 'r', encoding='utf-8') as prompt_file:
            prompt = prompt_file.read()
        return PromptTemplate.from_template(prompt) | self.model | StrOutputParser()

    def rewrite_query(self, query):
        if not chroma_conf.get('query_rewrite_enabled', False):
            return query
        rewritten_query = self.query_rewrite_chain.invoke({'input': query}).strip()
        if not rewritten_query:
            raise ValueError('查询改写模型返回了空查询')
        return rewritten_query

    def __init__chain(self):
        chain = self.prompt_template | self.model | StrOutputParser()
        return chain

    @staticmethod
    def _keyword_terms(text):
        return [
            term.lower()
            for term in re.findall(
                r'[\u4e00-\u9fff]{2,}|[a-zA-Z0-9][a-zA-Z0-9._-]*',
                text,
            )
        ]

    def _keyword_scores(self, query):
        if self._keyword_documents is None:
            indexed = self.vector_store.vector_store.get(
                include=['documents', 'metadatas']
            )
            self._keyword_documents = [
                (content, metadata or {})
                for content, metadata in zip(
                    indexed['documents'] or [],
                    indexed['metadatas'] or [],
                )
                if content
            ]

        normalized_query = ' '.join(query.lower().split())
        compact_query = re.sub(r'\s+', '', normalized_query)
        terms = self._keyword_terms(query)
        if not terms:
            return {}

        scores = {}
        for content, metadata in self._keyword_documents:
            normalized_content = ' '.join(content.lower().split())
            compact_content = re.sub(r'\s+', '', normalized_content)
            matched_terms = sum(
                term in normalized_content for term in set(terms)
            )
            score = matched_terms / len(set(terms))
            if compact_query and compact_query in compact_content:
                score = 1.0
            if score:
                key = (metadata.get('source_name'), content)
                scores[key] = score
        return scores

    def retrieve_scored_docs(self, retrieval_query, k=None, min_score=None):
        k = k if k is not None else chroma_conf['k']
        min_score = (
            min_score
            if min_score is not None
            else chroma_conf['min_relevance_score']
        )
        scored_docs = (
            self.vector_store.vector_store
            .similarity_search_with_relevance_scores(
                retrieval_query,
                k=k,
            )
        )
        if not chroma_conf.get('keyword_search_enabled', False):
            return [
                (document, score)
                for document, score in scored_docs
                if score >= min_score
            ]

        keyword_scores = self._keyword_scores(retrieval_query)
        vector_scores = {
            (document.metadata.get('source_name'), document.page_content): (
                document,
                score,
            )
            for document, score in scored_docs
        }
        keyword_limit = int(chroma_conf.get('keyword_candidate_limit', k))
        keyword_matches = sorted(
            keyword_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:keyword_limit]
        for key, keyword_score in keyword_matches:
            if key not in vector_scores:
                document = next(
                    (
                        Document(page_content=content, metadata=metadata)
                        for content, metadata in self._keyword_documents
                        if (
                            metadata.get('source_name'),
                            content,
                        )
                        == key
                    ),
                    None,
                )
                if document is None:
                    continue
                vector_scores[key] = (document, 0.0)

        keyword_weight = float(chroma_conf.get('keyword_weight', 0.4))
        ranked = []
        for key, (document, vector_score) in vector_scores.items():
            keyword_score = keyword_scores.get(key, 0.0)
            combined_score = (
                vector_score * (1 - keyword_weight)
                + keyword_score * keyword_weight
            )
            ranked.append((document, combined_score))
        ranked.sort(key=lambda item: item[1], reverse=True)
        return [
            (document, score)
            for document, score in ranked[:k]
            if score >= min_score
        ]

    # 检索函数 -- 用于查找和问题相似的片段
    def retriever_docs(self, query):
        retrieval_query = self.rewrite_query(query)
        return self.retrieve_scored_docs(retrieval_query)

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

