from langchain_chroma import Chroma

from utils.config_handler import chroma_conf
from utils.path_tool import get_abs_path
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from utils.file_handler import pdf_loader, txt_loader, listdir_with_allowed_type, get_file_md5_hex
from utils.logger_handler import logger


class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name= chroma_conf['collection_name'],
            embedding_function=embed_model,
            persist_directory=get_abs_path(chroma_conf['persist_directory'])
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size = chroma_conf['chunk_size'],
            chunk_overlap = chroma_conf['chunk_overlap'],
            separators= chroma_conf['separators'],
            length_function = len
        )

    # 返回检查到的相似片段
    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs = {'k': chroma_conf['k']})
        # 这个 RAG 不是在 Python 层把所有片段逐个暴力比较，而是通过 Chroma 使用向量索引进行近似最近邻检索。
        # Chroma 默认使用 HNSW（Hierarchical Navigable Small World）近似最近邻索引。
        

    # 加载文档
    def load_document(self):
        # 从数据文件夹中读取数据文件，转为向量存入向量库中
        # 需要计算文件的MD5做去重 


        # 创建一个检查MD5是否重复的函数
        def check_md5_hex(md5_for_check):
            if not os.path.exists(get_abs_path(chroma_conf['md5_hex_store'])):
                # 如果没有，就创建一个文件
                open(get_abs_path(chroma_conf['md5_hex_store']), 'w', encoding='utf-8').close()
                return False

            with open(get_abs_path(chroma_conf['md5_hex_store']), 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line == md5_for_check:
                        return True # md5处理过

                return False

        # 保存MD5码
        def save_md5_hex(md5_for_check):
            with open(get_abs_path(chroma_conf['md5_hex_store']), 'a', encoding='utf-8') as f:
                f.write(md5_for_check + '\n')
            
        # 读取txt/pdf文件
        def get_file_documents(read_path):
            if read_path.endswith('txt'): # endswith 后缀
                return txt_loader(read_path)
            if read_path.endswith('pdf'):
                return pdf_loader(read_path)

            return [] # 如果上面都不是的话，返回空列表

        allowed_files_path = listdir_with_allowed_type(get_abs_path(chroma_conf['data_path']), 
                                                       tuple(chroma_conf['allow_knowledge_file_type'])) # 收集想要文件格式的数据路径

        #--------------------------------------------------------------------
        # 开始处理文件
        for path in allowed_files_path:
            # 获取文件的MD5
            md5_hex = get_file_md5_hex(path)

            if check_md5_hex(md5_hex):
                logger.info(f"[加载知识库]{path}内容已经存在知识库内，跳过")
                continue  # 如果这个文件已经在知识库中，那么就进行下一个文件的加载

            try:
                documents = get_file_documents(path) # 获取到了 list[document] 

                if not documents:
                    logger.warning(f'[加载知识库]{path}内没有有效文本，跳过')
                    continue

                # 进行文本分割
                split_document = self.spliter.split_documents(documents) # 分割完成之后是 list[Documents]

                if not split_document:
                    logger.warning(f'[加载知识库]{path}分片后没有有效文本，跳过')
                    continue

                # 将内容存入向量库中
                self.vector_store.add_documents(split_document)
                save_md5_hex(md5_hex)

                logger.info(f'[加载知识库]{path}内容加载成功')

            except Exception as e:
                # exc_info=True 会记录详细的报错堆栈， 如果是False仅记录报错信息本身
                logger.error(f'[加载知识库]{path}内容加载失败：{str(e)}', exc_info=True)
                continue 
    


if __name__ == '__main__':
    vs = VectorStoreService()
    vs.load_document()

    retriever = vs.get_retriever().invoke('创新创业')
    for r in retriever:
        print(r.page_content)
        print('-'*20)

# 如果想要测试
# cd D:\01\ai\python\rag\agent_university
# python -m rag.vector_store



