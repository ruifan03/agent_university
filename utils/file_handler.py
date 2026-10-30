# 文件处理函数
import os
import hashlib
from utils.logger_handler import logger
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader

def get_file_md5_hex(filepath):   # 获取文件的MD5的十六进制字符串

    if not os.path.exists(filepath):
        logger.error(f'[md5计算]文件{filepath}不存在')
        return

    if not os.path.isfile(filepath):
        logger.error(f'[md5计算]路径{filepath}不是文件')
        return

    # 计算MD5
    md5_obj = hashlib.md5()

    chunk_size = 4096 # 分片计算每一段的MD5
    try:
        with open(filepath, 'rb') as f: # 二进制的方式进行读取
            while chunk := f.read(chunk_size):
                md5_obj.update(chunk) # 把本次的 chunk 字节，追加合并到之前已经计算的哈希状态里
                # 等价逻辑：`md5.update(a); md5.update(b)` = `md5.update(a+b)`

        md5_hex = md5_obj.hexdigest()
        return md5_hex
    except Exception as e:
        logger.error(f'计算文件{filepath}md5失败，{str(e)}')
        return None


def listdir_with_allowed_type(path, allowed_types):   # 返回文件夹内的文件列表（允许的文件后缀）
    files = []

    # 先判断给出的路径是否是文件夹
    if not os.path.isdir(path):
        logger.error(f'[listdir_with_allowed_type]{path}不是文件夹')
        return allowed_types

    for f in os.listdir(path): # 列出文件夹里面的东西
        if f.endswith(allowed_types): # 拿取文件的后缀进行比对
            files.append(os.path.join(path, f)) # 传回去的是整个文件的路径

    return tuple(files)

def pdf_loader(filepath, passwd = None):  # 加载pdf文件的函数 -- 返回值就是list[Document]
    return PyPDFLoader(filepath, passwd).load()

def txt_loader(filepath):  # 加在txt文件的函数 -- 返回值就是list[Document]
    return TextLoader(filepath, encoding='utf-8').load()
# 文件过大怎么办？直接下载的话









