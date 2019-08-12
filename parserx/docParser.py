
import  logging
from .abstractParser import BADiffCommentParser
from functional import ReportSignalFunctional
from loader.SingleLoader import SingleFileLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - CppParser - %(levelname)s - %(message)s')
logger = logging.getLogger("CppParser")


class CppParser(BADiffCommentParser):
    def __init__(self, path, mapper=ReportSignalFunctional()):
        super().__init__(
            before=r"\/\*",
            after=r"\*\/",
            path=path,
            mapper=mapper,
            loader=SingleFileLoader()
        )


class HtmlParser(BADiffCommentParser):
    def __init__(self, path, mapper=ReportSignalFunctional()):
        super().__init__(
            before=r"<!--",
            after=r"-->",
            path=path,
            loader=SingleFileLoader(),
            mapper=mapper
        )