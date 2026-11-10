from langchain.chat_models import init_chat_model, BaseChatModel
from abc import ABC, abstractmethod
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_community.embeddings import DashScopeEmbeddings
from utils.config_handler import rag_conf

class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        pass

class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return init_chat_model(  model=rag_conf['chat_model_name'],  
                               api_key = rag_conf['DEEPSEEK_API_KEY'] , 
                               base_url=rag_conf['DEEPSEEK_BASE_URL'])


class EmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(model= rag_conf['embedding_model_name'], dashscope_api_key= rag_conf['DASHSCOPE_API_KEY'])


chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()






    
