"""
    dependency
"""
import re, logging
from .abstractParser import BADiffCommentParser
from functional import ToMarkdownSignalFunctional

"""
    解析C++文件
"""
logging.basicConfig(level=logging.INFO, format='%(asctime)s - CppParser - %(levelname)s - %(message)s')
logger = logging.getLogger("CppParser")


class CppParser(BADiffCommentParser):
    def __init__(self, path):
        super().__init__(before=r"\/\*", after=r"\*\/", path=path, mapper=ToMarkdownSignalFunctional())
        try:
            self.parse_comment()
        except Exception as e:
            print(e)
            logging.fatal("comment parse fail")
        self.iter_of_comment = iter(self._comment_list)