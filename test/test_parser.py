import unittest
import random
import re

from loader.SingleLoader import SingleFileLoader
from loader.MultipleLoader import MultipleFileLoader
from parserx.cppParser import CppParser

"""
    2019年8月8日 星期四 
    本类主要测试对源文件注释的解析
    1. 解析多行式注释
    2. 生成导出符号表
"""


class ParserTest(unittest.TestCase):
    # 生成测试.cpp文件

    test_cpp_file = r"E:\file\pyProj\docPy\static\test_cpp.cpp"
    test_cpp_source_code = r"E:\file\pyProj\docPy\static\test_cpp_main.cpp"

    def setUp(self) -> None:
        with open(ParserTest.test_cpp_file, "w") as fcpp:
            for idx in range(10):
                content = "/*"
                for char in range(random.randint(10, 100)):
                    content += str(random.randint(char, char * 10) % 10)
                content += "*/"
                fcpp.write(content + "\n\n")

    def test_parse_commend(self):
        pass

    def test_page_symmetric_check(self):
        cpp = CppParser(path=ParserTest.test_cpp_file)
        cpp.parse_comment()

    def test_parse_cpp_source_code(self):
        cpp = CppParser(path=ParserTest.test_cpp_source_code)
        cpp.switch()
