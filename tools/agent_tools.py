
from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
import random
from utils.config_handler import agent_conf
from utils.path_tool import get_abs_path
import os
from utils.logger_handler import logger

rag = RagSummarizeService()

@tool(description='从向量存储中检索参考资料') 
def rag_summarize(query): 
    return rag.rag_summarize(query)


@tool(description='传入参数无返回值，调用后触发中间件自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文信息。')
def fill_context_for_report():
    return 'fill_context_for_report已调用'
