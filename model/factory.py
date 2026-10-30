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
# ABC: 抽象基类
# 作用：标记这个类是「模板父类」，不能直接 new 出来实例用，只能用来被别的类继承。
# @abstractmethod ：**抽象方法装饰器**
# 规则：任何子类继承 BaseModelFactory，必须重写、实现这个 generator 方法；不写的话，代码运行直接抛报错
# 强制所有的子类都要遵守统一的接口规范，保证了代码的可维护性和可扩展性。


class ChatModelFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return init_chat_model(  model=rag_conf['chat_model_name'],  
                               api_key = rag_conf['DEEPSEEK_API_KEY'] , 
                               base_url=rag_conf['DEEPSEEK_BASE_URL'])


class EmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(model= rag_conf['embedding_model_name'], dashscope_api_key= rag_conf['DASHSCOPE_API_KEY'])

# 创建相应的实例
chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()


# 疑问：为什么要这个样子创建？不能直接创 llm/嵌入 建模型实例吗？
# 1. 创建一个类可以统一接口，方便后续统一修改和管理，在这个类里面可以有很多其他的方法
# 2. 面向对象的一个思想，模型是一个对象，可以进行创建实例
# 3. 如果没有类的建立，就不能所有的实例都采用统一的调用函数来进行输出等
# 4. 不方便附加其他的属性

# 普通函数可以完成对象创建，但缺少统一接口约束、不方便扩展多模型；
# 类 + 抽象基类是为了多模型扩展、多态、规范约束，是面向扩展的写法。
# 小项目没必要上抽象类，但是你这个 RAG 工程后续要扩展多种模型，抽象工厂会更省心





    