"""
    dependency
"""
import re, logging
from .abstractParser import AbstractParser
from loader.SingleLoader import SingleFileLoader

"""
    解析C++文件
"""
logging.basicConfig(level=logging.INFO, format='%(asctime)s - CppParser - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

signal_table = {

}


class CppParser(AbstractParser):
    def __init__(self, path):
        super().__init__(before=r"\/\*", after=r"\*\/", path=path)