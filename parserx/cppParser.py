"""
    dependency
"""
import re, logging
from .abstractParser import AbstractParser
from loader.SingleLoader import SingleFileLoader
from functional import CppToMdSignalFunctional

"""
    解析C++文件
"""
logging.basicConfig(level=logging.INFO, format='%(asctime)s - CppParser - %(levelname)s - %(message)s')
logger = logging.getLogger("CppParser")

"""
    /*
        @:template<class|typename T> CppParser : public|protected|private{}
        $:the class to parse a list of comments for c++ lang
        $:bala bala bala...
    */
    
    /*
        @:void getName(std::string, int idx)
        >:(std::string) v1: $a string of name
        >:(int) idx: $a index of name
        <:void 
        $:this method is going to be deleted after version 1.0.3
        ---
    */
"""


class CppParser(AbstractParser):
    def __init__(self, path):
        super().__init__(before=r"\/\*", after=r"\*\/", path=path, mapper=CppToMdSignalFunctional())
        try:
            self.parse_comment()
        except Exception as e:
            logging.fatal("comment parse fail")
        self.iter_of_comment = iter(self._comment_list)

    """
        there are three types of doc comment
        1. class doc
            document this doc as class doc 
        2. function/method doc
            document this doc as function doc
        3. dependency doc
            document this doc as reference file doc
            such as c++'s header file or Python's imported module
        4. header-description doc
            document this doc as the detail description of this source code
    """