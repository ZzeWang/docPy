import logging
from .abstractParser import GCommentParser
from loader.multipleLoader import MultipleFileLoader, MultipleDirsLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - AbstractParser - %(levelname)s - %(message)s')
logger = logging.getLogger("BatchDirParser")

"""
    &: class BatchDirParser
    $: 批处理处理器，加载一个目录下的所有文件，一般不直接使用
    $: 而是使用其特化的子类，如专门批处理c++或者python源码的批处理器。它的FileLoader
    $: 是MultipleFileLoader。
    LK: Parser
"""
"""
    # GCommentParser,MultipleFileLoader,logging
    LK: Parser
"""


class BatchDirParser(GCommentParser):
    """
        @: init
        >: (void) :
        <:(void)
        $:构造器，必须参数同AbstractParser
        M:BatchDirParser
    """

    def __init__(self, *args, **kwargs):
        kwargs["loader"] = MultipleDirsLoader()
        super().__init__(*args, **kwargs)

    """
        @: parse_comment
        >: (void) :
        <:(void)
        $: 对AbstractParser.parse_comment的重写。对每个加载进入内存的文件对象(SingleFileLoader)
        $: 进行提取注释操作
        M:BatchDirParser
    """

    def parse_comment(self):
        for file in self.file._loaded_file:
            self.parse_comments(file)


"""
    &: class CppBatchDirParser
    $: c++源码批处理文档生成器，特化了注释起始和结束符为/* */
    LK:Parser
"""


class CppBatchDirParser(BatchDirParser):
    def __init__(self, *args, **kwargs):
        kwargs["before"] = r"\/\*"
        kwargs["after"] = r"\*\/"
        super().__init__(*args, **kwargs)


"""
    &: class HtmlBatchDirParser
    $: html源码批处理文档生成器，特化了注释起始和结束符<!-- -->
    LK:Parser
"""


class HtmlBatchDirParser(BatchDirParser):
    def __init__(self, *args, **kwargs):
        kwargs["before"] = r"<!--"
        kwargs["after"] = r"-->"
        super().__init__(*args, **kwargs)


"""
    &: class PythonBatchDirParser
    $: python源码批处理文档生成器，特化了注释起始和结束符
    LK: Parser
"""


class PythonBatchDirParser(BatchDirParser):
    def __init__(self, *args, **kwargs):
        kwargs["before"] = r"\"\"\""
        kwargs["after"] = r"\"\"\""
        super().__init__(*args, **kwargs)

