from functional import ToMdSignalFunctional
from parserx.cppParser import CppParser
from parserx.pyParser import PyParser
from functional import AbstractSignalFunctional
import unittest


class FuncTest(unittest.TestCase):

    def setUp(self) -> None:
        pass


    def test_parser_py(self):
        pyp = PyParser(r"E:\file\pyProj\docPy\static\test_main.py")
        pyp.switch(r"E:\file\pyProj\docPy\test\targetfile")


    def test_class_signature(self):

        cpp_parser = CppParser(r"E:\file\pyProj\docPy\static\test_cpp_main.cpp")
        cpp_parser.switch(r"E:\file\pyProj\docPy\test\targetfile")
        pass

    def test_format_this(self):
        abs = AbstractSignalFunctional()
        abs.format_this((1,2,3), "{} {} {}")