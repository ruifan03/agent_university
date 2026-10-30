
from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
import random
from utils.config_handler import agent_conf
from utils.path_tool import get_abs_path
import os
from utils.logger_handler import logger


rag = RagSummarizeService()


# 大模型是怎么知道工具的功能，就是通过 @tool(description='xxx') 这个装饰器来实现的
# LangChain / ReAct Agent 是把**所有 tool 的名字 + 工具描述**，自动打包，塞给大模型的 prompt。不是你手动写到 system prompt 里。
# 工具列表是 LangChain 框架自动追加到 prompt 里的

# @tool(description='xxx') 在里面写清楚适用场景，说明 入参 含义避免传参错误
# 【工具能干什么】+【适用场景】+【入参说明】+【禁忌/不能做什么】



@tool(description='从向量存储中检索参考资料') # 这个工具能干什么、不能干什么，参数是什么
def rag_summarize(query):  # 最后输出 字符串
    return rag.rag_summarize(query)


# @tool(description="获取用户的ID，以纯字符串形式返回")
# def get_user_id() -> str:
#     return random.choice(user_ids)


# @tool(description="获取当前月份，以纯字符串形式返回")
# def get_current_month() -> str:
#     return random.choice(month_arr)



@tool(description='传入参数无返回值，调用后触发中间件自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文信息。')
def fill_context_for_report():
    return 'fill_context_for_report已调用'


# if __name__ == '__main__':
#     pass


# 如果想要测试
# 把 @tools 注释掉
# cd D:\01\ai\python\rag-gsg\agent
# python -m tools.agent_tools

