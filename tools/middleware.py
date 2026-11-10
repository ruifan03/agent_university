
# 中间件的代码
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt
from utils.logger_handler import logger
from utils.prompt_loader import load_system_prompt, load_report_prompt

@wrap_tool_call
def monitor_tool( 
    request,
    handler,):  

    logger.info(f"[tool mintor]执行工具：{request.tool_call['name']}")
    logger.info(f"[tool mintor]传入参数：{request.tool_call['args']}")

    try:
        result =  handler(request) 
        logger.info(f"[tool mintor]工具{request.tool_call['name']}调用成功")

        if request.tool_call['name'] == 'fill_context_for_report': 
            request.runtime.context['report'] = True

        return result
    except Exception as e:
        logger.error(f"[tool mintor]工具{request.tool_call['name']}调用失败，原因：{str(e)}")
        raise e
    
@before_model
def log_before_model(
    state,    
    runtime   ): 
    logger.info(f"[log_before_model]即将调用模型，带有{len(state['messages'])}条消息。")

    message_content = state['messages'][-1].content
    if isinstance(message_content, str):
        log_content = message_content.strip()
    else:
        log_content = '[multimodal content]'
    logger.debug(
        f"[log_before_model] {type(state['messages'][-1]).__name__} | {log_content}"
    )

    # return None

@dynamic_prompt            
def report_prompt_switch(request):  # 动态切换提示词
    is_report = request.runtime.context.get('report', False)  
  
    if is_report: 
        return load_report_prompt()

    return load_system_prompt()

