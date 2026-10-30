import os

from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from model.factory import embed_model
from utils.config_handler import chroma_conf
from utils.file_handler import (
    get_file_md5_hex,
    listdir_with_allowed_type,
    pdf_loader,
    txt_loader,
)
from utils.logger_handler import logger
from utils.path_tool import get_abs_path


class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_conf['collection_name'],
            embedding_function=embed_model,
            persist_directory=get_abs_path(chroma_conf['persist_directory']),
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf['chunk_size'],
            chunk_overlap=chroma_conf['chunk_overlap'],
            separators=chroma_conf['separators'],
            length_function=len,
        )

    def get_retriever(self):
        return self.vector_store.as_retriever(
            search_kwargs={'k': chroma_conf['k']}
        )

    def _load_file_documents(self, path):
        if path.lower().endswith('.txt'):
            return txt_loader(path)
        if path.lower().endswith('.pdf'):
            return pdf_loader(path)
        return []

    def _indexed_files(self):
        indexed = self.vector_store.get(include=['metadatas'])
        files = {}
        for doc_id, metadata in zip(
            indexed['ids'],
            indexed['metadatas'] or [],
        ):
            metadata = metadata or {}
            name = metadata.get('source_name') or os.path.basename(
                metadata.get('source', '')
            )
            if name:
                files.setdefault(
                    name,
                    {'ids': [], 'md5': metadata.get('file_md5')},
                )
                files[name]['ids'].append(doc_id)
                if metadata.get('file_md5'):
                    files[name]['md5'] = metadata['file_md5']
        return files

    def sync_documents(self):
        """Synchronize knowledge files and vectors, including updates and deletions."""
        data_path = get_abs_path(chroma_conf['data_path'])
        os.makedirs(data_path, exist_ok=True)
        allowed_types = tuple(
            extension.lower()
            for extension in chroma_conf['allow_knowledge_file_type']
        )
        current_paths = listdir_with_allowed_type(data_path, allowed_types)
        indexed_files = self._indexed_files()
        current_names = {os.path.basename(path) for path in current_paths}
        stats = {'added': [], 'updated': [], 'deleted': [], 'failed': []}

        for name, indexed_file in indexed_files.items():
            if name not in current_names:
                self.vector_store.delete(ids=indexed_file['ids'])
                stats['deleted'].append(name)

        for path in current_paths:
            name = os.path.basename(path)
            file_md5 = get_file_md5_hex(path)
            if not file_md5:
                stats['failed'].append(name)
                continue

            existing = indexed_files.get(name)
            if existing and existing['md5'] == file_md5:
                continue

            try:
                documents = self._load_file_documents(path)
                split_documents = self.spliter.split_documents(documents)
                if not split_documents:
                    raise ValueError('文件没有可索引的文本')

                for document in split_documents:
                    document.metadata = {
                        **document.metadata,
                        'source_name': name,
                        'file_md5': file_md5,
                    }
                ids = [
                    f'{file_md5}-{index}'
                    for index in range(len(split_documents))
                ]
                if existing:
                    self.vector_store.delete(ids=existing['ids'])
                    operation = 'updated'
                else:
                    operation = 'added'
                self.vector_store.add_documents(split_documents, ids=ids)
                stats[operation].append(name)
            except Exception as exc:
                logger.error(f'[同步知识库]{path}失败：{exc}', exc_info=True)
                stats['failed'].append(name)

        logger.info(f'[同步知识库]完成：{stats}')
        return stats

    def load_document(self):
        """Backward-compatible alias for the old indexing entry point."""
        return self.sync_documents()


if __name__ == '__main__':
    vs = VectorStoreService()
    print(vs.sync_documents())
