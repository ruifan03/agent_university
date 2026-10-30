# 提示词文件
from utils.config_handler import prompts_conf
from utils.path_tool import get_abs_path
from utils.logger_handler import logger

# 主提示词
def load_system_prompt():  # 先尝试获取路径，然后打开文件全部读取

    # 关于读取路径相关的报错
    try:
        system_prompt_path = get_abs_path(prompts_conf['main_prompt_path'])
    except KeyError as e:
        logger.error('[load_system_promprt]在yaml配置中没有 main_prompt_path 配置项')
        raise e # 将异常扔出去

    # 关于读取文件相关的
    try:
        with open(system_prompt_path, 'r', encoding='utf-8') as f:
            content = f.read() # 返回值是 字符串
        return content # 全部内容读出来
       # return open(system_prompt_path, 'r', encoding='utf-8').read() # 全部内容读出来，但是这个样子的话就没有关闭文件
   
    except Exception as e:
        logger.error(f'[load_system_promprt]在yaml解析系统提示词出错，{str(e)}')
        raise e # 将异常扔出去



# RAG提示词
def load_rag_prompt():

    # 关于读取路径相关的报错
    try:
        rag_prompt_path = get_abs_path(prompts_conf['rag_summarize_prompt_path'])
    except KeyError as e:
        logger.error('[load_rag_promprt]在yaml配置中没有 rag_summarize_prompt_path 配置项')
        raise e # 将异常扔出去

    # 关于读取文件相关的
    try:
        with open(rag_prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content # 全部内容读出来
    except Exception as e:
        logger.error(f'[load_rag_promprt]RAG总结提示词出错，{str(e)}')
        raise e # 将异常扔出去



# 报告提示词
def load_report_prompt():

    # 关于读取路径相关的报错
    try:
        report_prompt_path = get_abs_path(prompts_conf['report_prompt_path'])
    except KeyError as e:
        logger.error('[load_report_prompt]在yaml配置中没有 report_prompt_path 配置项')
        raise e # 将异常扔出去

    # 关于读取文件相关的
    try:
        with open(report_prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content # 全部内容读出来
    
    except Exception as e:
        logger.error(f'[load_report_prompt]解析report提示词出错，{str(e)}')
        raise e # 将异常扔出去



if __name__ == '__main__':
    print(load_rag_prompt())

# 如果想要测试
# cd D:\01\ai\python\rag-gsg\agent
# python -m utils.prompt_loader







