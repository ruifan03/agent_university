
# 为整个工程提供一个统一的绝对路径
import os 

def get_project_root():

    current_file = os.path.abspath(__file__) 
    current_dir = os.path.dirname(current_file) 
    project_root = os.path.dirname(current_dir)

    return project_root


def get_abs_path(relative_path):
    """
    传递相对路径，得到绝对路径
    ：param relative_path 相对路径
    return 绝对路径
    """
    project_root = get_project_root()
    return os.path.join(project_root, relative_path)

# print('---------------------')
# print(get_project_root())
# print(get_abs_path('123/123'))


