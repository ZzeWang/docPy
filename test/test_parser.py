import unittest
from parserx.docParser import PyParser
from parserx.batchDirParser import PythonBatchDirParser
from functional import ToMarkdownSignalFunctional
from codeObject import ProjectObject
"""
    2019年8月8日 星期四 
    本类主要测试对源文件注释的解析
    1. 解析多行式注释
    2. 生成导出符号表
"""


class ParserTest(unittest.TestCase):
    # 生成测试.cpp文件

    def test_parse_commend(self):
        pass

    def test_batch(self):
        pyp = PythonBatchDirParser(path=r"E:\file\pyProj\docPy", mapper=ToMarkdownSignalFunctional())
        pyp.run()
        pyp._mapper.report(r"E:\file\pyProj\docPy\test\targetfile")

    def test_single(self):
        pyp = PyParser(path=r"E:\file\pyProj\docPy\comments\UsageBlock.py")
        pyp.run()
        pyp._mapper.queue = [i[0] for i in pyp._mapper._obj_set.values() if isinstance(i[0], ProjectObject)]
        pyp._mapper.report(path="")