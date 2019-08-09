import unittest
from loader.SingleLoader import SingleFileLoader
from loader.MultipleLoader import MultipleFileLoader
"""
    2019年8月8日 星期四 
    本类主要测试文件加载功能
    1. 加载单个指定格式文件进入内存
    2. 加载整个目录下所有指定格式文件进入内存
"""


class LoaderTest(unittest.TestCase):

    def setUp(self) -> None:
        pass

    def test_read_single_with_too_big_file(self):
        single = SingleFileLoader()
        single.set_attr(r"E:\file\pyProj\docPy\static\test_too_big_file.cpp", "test_too_big_file.cpp", "cpp")
        single.load()

    def test_read_mul_with_too_big_file(self):
        mul = MultipleFileLoader()
        mul.set_attr(r"E:\file\pyProj\docPy\static")
        mul.load()

