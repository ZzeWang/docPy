import re, logging
from .abstractParser import BADiffCommentParser
from functional import ToMarkdownSignalFunctional
from loader.multipleLoader import MultipleFileLoader


class BatchDirParser(BADiffCommentParser):
    def __init__(self, *args, **kwargs):
        kwargs["loader"] = MultipleFileLoader()
        super().__init__(*args, **kwargs)


    def parse_comment(self):
        for file in self.file._loaded_file:
            self.parse_comments(file)
