import logging
from .abstractParser import BADiffCommentParser, GCommentParser
from functional import ReportSignalFunctional
from loader.SingleLoader import SingleFileLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - CppParser - %(levelname)s - %(message)s')
logger = logging.getLogger("CppParser")

"""
    &: class CppParser
    $: c++单源码文档处理器，用于解析单个c++源码文档
    LK: Parser
"""

class CppParser(BADiffCommentParser):
    """
        @: init
        >: (str) path: 源码文档路径
        >: (AbstractSignalFunctional) mapper: 匹配器，默认为报表匹配器*ReportSignalFunctional*，可以自定义匹配器，目前提供了转为Markdown格式的ToMarkdownSignalFunctional匹配器
        >: (FileLoader) loader: 文档加载器，默认为SingleFileLoader
        <:(void)
        $: 构造器
        M: CppParser
    """

    def __init__(self, path, mapper=ReportSignalFunctional()):
        super().__init__(
            before=r"\/\*",
            after=r"\*\/",
            path=path,
            mapper=mapper,
            loader=SingleFileLoader()
        )


"""
    &: class PyParser
    $: Python单源码文档处理器，用于解析单个Python源码文档
    LK: Parser
"""


class PyParser(GCommentParser):

    """
        @: init
        >: (str) path: 源码文档路径
        >: (AbstractSignalFunctional) mapper: 匹配器，默认为报表匹配器*ReportSignalFunctional*，可以自定义匹配器，目前提供了转为Markdown格式的ToMarkdownSignalFunctional匹配器
        >: (FileLoader) loader: 文档加载器，默认为SingleFileLoader
        <:(void)
        $: 构造器
        M: PyParser
    """
    def __init__(self, path, mapper=ReportSignalFunctional()):
        super().__init__(
            before=r"\"\"\"",
            after=r"\"\"\"",
            path=path,
            mapper=mapper,
            loader=SingleFileLoader()
        )


"""
    &: class HtmlParser
    $: Html单源码文档处理器，用于解析单个Html源码文档
    LK: Parser
"""

class HtmlParser(BADiffCommentParser):
    """
        @: init
        >: (str) path: 源码文档路径
        >: (AbstractSignalFunctional) mapper: 匹配器，默认为报表匹配器*ReportSignalFunctional*，可以自定义匹配器，目前提供了转为Markdown格式的ToMarkdownSignalFunctional匹配器
        >: (FileLoader) loader: 文档加载器，默认为SingleFileLoader
        <:(void)
        $: 构造器
        M: HtmlParser
    """
    def __init__(self, path, mapper=ReportSignalFunctional()):
        super().__init__(
            before=r"<!--",
            after=r"-->",
            path=path,
            loader=SingleFileLoader(),
            mapper=mapper
        )
