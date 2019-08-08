"""
    dependency
"""
import re, logging
from .abstractParser import AbstractParser
from ..loader.SingleLoader import SingleFileLoader

"""
    解析C++文件
"""
logging.basicConfig(level=logging.INFO, format='%(asctime)s - CppParser - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

signal_table = {

}


class CppParser(AbstractParser):
    def __init__(self, path):
        super().__init__(before=r"\/\*", after=r"\*\/")
        self.file = SingleFileLoader()
        self.file.set_attr_by_path(path)

        try:
            self.file.load()
        except FileNotFoundError as e:
            logging.fatal("file {} not exists".format(path))

    """
        由于存在分页问题，可能会造成同一页内
        注释不闭合，比如在第一页最后出现一次注释
        /* 不啦不啦不啦 EOF
        然后在下一页出现该注释
        不啦不啦不啦 */
        如果不事先检查在同一页内注释符号是否对称，则可能会导致正则匹配缺少一项
        (bool, int) pre_symmetric_check(int)
        :param page_num: 本页内容
        :return :(bool , int) 返回是否不对称，如果不对称则需要在元组的第二项里表明最后一个
            注释在上一页的位置
    """

    def pre_symmetric_check(self, page_content):
        pattern_before = re.compile("/\*")
        pattern_after = re.compile("\\*/")

        if len(re.findall(pattern_before, page_content)) == \
                len(re.findall(pattern_after, page_content)):
            return True, -1
        else:
            return False, page_content.rfind("/*")

    def parse_comment(self):
        for page in self.file.pages:
            if self.pre_symmetric_check(page)[0] :
                pass
