import logging
from .abstractParser import BADiffCommentParser
from loader.multipleLoader import MultipleFileLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - AbstractParser - %(levelname)s - %(message)s')
logger = logging.getLogger("BatchDirParser")


class BatchDirParser(BADiffCommentParser):
    def __init__(self, *args, **kwargs):
        kwargs["loader"] = MultipleFileLoader()
        super().__init__(*args, **kwargs)

    def parse_comment(self):
        for file in self.file._loaded_file:
            self.parse_comments(file)


class CppBatchDirParser(BatchDirParser):
    def __init__(self, *args, **kwargs):
        kwargs["before"] = r"\/\*"
        kwargs["after"] = r"\*\/"
        super().__init__(*args, **kwargs)


class HtmlBatchDirParser(BatchDirParser):
    def __init__(self, *args, **kwargs):
        kwargs["before"] = r"<!--"
        kwargs["after"] = r"-->"
        super().__init__(*args, **kwargs)
