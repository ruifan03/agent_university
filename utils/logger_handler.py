import logging
import os
from utils.path_tool import get_abs_path

# 日志保存的根目录
LQG_ROOT = get_abs_path('logs')# 关于输出的日志都在这个文件夹下面进行保存

# 确保日志的目录存在
os.makedirs(LQG_ROOT, exist_ok=True)

# 日志格式配置
DEFAULT_LOG_FORMAT = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
# 日志的时间 名字 级别 文件名字：文件哪一行 日志正文


def get_logger(
        name = 'agent',
        console_level = logging.INFO,
        file_level = logging.DEBUG,
        log_file = None,
):
    logger = logging.getLogger(name) # 创建一个日志对象
    logger.setLevel(logging.DEBUG)

    # 避免重复添加Handler
    if logger.handlers:
        return logger

    # 控制台的 Handler -- 日志信息会在控制台上进行输出
    console_handler = logging.StreamHandler() # 创建在控制台输出 Handler
    console_handler.setLevel(console_level) # 设置级别
    console_handler.setFormatter(DEFAULT_LOG_FORMAT) # 设置控制台日志输出的格式

    logger.addHandler(console_handler) # 将控制台 Handler 加入到 logger 里面

    # 文件 Handler -- 在文件中显示日志
    if not log_file:
        log_file = os.path.join(LQG_ROOT, f"{name}.log") # 日志文件的存放路径

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(file_handler)

    return logger


# 快捷获取日志
logger = get_logger()

# logger.info('日志信息')
# logger.error('cuowu')
















