import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# 创建logs目录（如果不存在）
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# 配置日志文件路径
log_file = os.path.join(log_dir, 'meituan_personal_mcp.log')

# 创建日志记录器
logger = logging.getLogger('meituan_personal_mcp')
logger.setLevel(logging.INFO)

# 创建rotating file handler，每个日志文件最大10MB，保留10个备份文件
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10*1024*1024,  # 10MB
    backupCount=10,
    encoding='utf-8'
)

# 创建控制台handler
console_handler = logging.StreamHandler()

# 设置日志格式
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

# 设置handler的格式
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 添加handler到logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# 导出logger实例
def get_logger():
    return logger 