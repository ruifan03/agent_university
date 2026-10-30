
# 中间件的代码
from langchain.agents.middleware import wrap_tool_call, before_model, dynamic_prompt
from utils.logger_handler import logger
from utils.prompt_loader import load_system_prompt, load_report_prompt

@wrap_tool_call # 用处： 可以在工具（tool）执行之前/之后，进行一些自定义的操作，比如打印日志、记录调用次数、统计耗时等
def monitor_tool(  # 用途：打印相应的日志
    # 请求的数据封装 -- 工具调用的核心数据
    request,
    # 执行的函数本身
    handler,
):  # 工具执行的监控

    logger.info(f"[tool mintor]执行工具：{request.tool_call['name']}")
    logger.info(f"[tool mintor]传入参数：{request.tool_call['args']}")

    try:
        result =  handler(request) # 原封不动的返回 或者理解为 执行这个工具，但是在 执行前/后 可以进行一些自定义的操作
        logger.info(f"[tool mintor]工具{request.tool_call['name']}调用成功")

        if request.tool_call['name'] == 'fill_context_for_report': 
            # 如果调用了这个工具，就说明需要使用到生成报告的提示词模板
            # 这个时候需要向 runtime 里面进行一些标记
            request.runtime.context['report'] = True
            # 为什么一开始是 False ？在那里进行的信息注入，或者说一开始是否存在这个字典的key？
            # 使用完这个模板之后


        return result
    except Exception as e:
        logger.error(f"[tool mintor]工具{request.tool_call['name']}调用失败，原因：{str(e)}")
        raise e
    
@before_model
def log_before_model(
    state,    # 整个智能体中的状态记录
    runtime   # 记录了整个执行过程中的上下文信息
):  # 在模型执行前输出日志
    logger.info(f"[log_before_model]即将调用模型，带有{len(state['messages'])}条消息。")

    # 想要打印出来消息的内容一定要debug级别才可以做到  -- 消息每次都是累加上的，所以打印最后一条就可以了
    message_content = state['messages'][-1].content
    if isinstance(message_content, str):
        log_content = message_content.strip()
    else:
        log_content = '[multimodal content]'
    logger.debug(
        f"[log_before_model] {type(state['messages'][-1]).__name__} | {log_content}"
    )

    # return None

@dynamic_prompt              # 在向模板注入提示词之前都会调用这个函数
def report_prompt_switch(request):  # 动态切换提示词
    is_report = request.runtime.context.get('report', False)  # 默认值是 False , 如果拿不到值，就返回这个默认值
    # 这是字典的 get 函数，获得字典的指定的 key 值
    if is_report:  # 是报告生成场景
        return load_report_prompt()

    return load_system_prompt()

    # 问题切换后还可以换回来吗？























