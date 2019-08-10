import re, logging
from .abstractParser import BADiffCommentParser
from loader.SingleLoader import SingleFileLoader
from functional import ToMarkdownSignalFunctional

class HtmlParser(BADiffCommentParser):
    def __init__(self, path):
        super().__init__(before=r"<!--", after=r"-->", path=path, mapper=ToMarkdownSignalFunctional())
        try:
            self.parse_comment()
        except Exception as e:
            print(e)
            logging.fatal("comment parse fail")
        self.iter_of_comment = iter(self._comment_list)