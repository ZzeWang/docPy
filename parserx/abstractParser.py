"""
    dependency
"""
import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from loader.SingleLoader import *
from functional import AbstractSignalFunctional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - AbstractParser - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
"""
    2019年8月8日 星期四 
    抽象基类
"""


class AbstractParser:

    def __init__(self, *args, **kwargs):
        self._before = r""
        self._after = r""

        if kwargs and kwargs["after"] and kwargs["before"]:
            self._after = kwargs["after"]
            self._before = kwargs["before"]
        else:
            self._after = ""
            self._before = ""

        self._mapper = AbstractSignalFunctional()
        if kwargs and kwargs["mapper"]:
            if isinstance(kwargs["mapper"], AbstractSignalFunctional):
                self._mapper = kwargs["mapper"]

        self.file = FileLoader()
        if kwargs and kwargs["loader"]:
            if isinstance(kwargs["loader"], FileLoader):
                self.file = kwargs["loader"]

        if kwargs and kwargs["path"]:
            self.file.set_attr_by_path(kwargs["path"])
            self.file.load()
        else:
            logging.fatal("no file input")
            raise Exception

        self._comment_list = []  # block of comments \/\*
        self._comment_pattern = re.compile("{}(.*?){}".format(self._before, self._after), re.DOTALL)

        self.iter_of_comment = iter(self._comment_list)

        # 用于处理符号时
        self._thread_executor = ThreadPoolExecutor(max_workers=3)

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
        return False

    def parse_comments(self, who):
        page_c = 0
        while page_c < len(who.pages):
            not_page = self.pre_symmetric_check(who.pages[page_c])

            tmp = re.findall(self._comment_pattern, who.pages[page_c])
            for result in tmp:
                self._comment_list.append(result)
                logging.info("find a comment block with length={}".format(len(result)))

            start = who.pages[page_c].rfind(self._before.replace("\\", ""))
            if start == -1:
                page_c += 1
                continue
            org_line = page_c
            if not not_page:
                while True:
                    end = who.pages[page_c + 1].find(self._after.replace("\\", ""))
                    page_c += 1
                    if end != -1:
                        break
                base = who.pages[org_line][start + len(self._before.replace("\\", "")):]
                org_line += 1
                while org_line < page_c:
                    base += who.pages[org_line]
                    org_line += 1

                self._comment_list.append(base + who.pages[page_c][:end])
            else:
                page_c += 1

            if page_c + 1 == len(who.pages):
                break
        for idx, item in enumerate(self._comment_list):
            self._comment_list[idx] = self._comment_list[idx].strip()

    def parse_comment(self):
        self.parse_comments(self.file)

    def __get_next_comment(self):
        try:
            return next(self.iter_of_comment).strip()
        except StopIteration as e:
            return None

    """
        对每一块注释，匹配特征符号（@，#，！等），调用
        self._mapper的方法处理，此处_mapper必须是AbstractSignalFunctional的子类
    """

    def switch(self, target_file):
        function_pat = re.compile("@: *[a-zA-Z_0-9]+ *(?:[a-zA-Z_0-9]+|[a-zA-Z_0-9]+:{2}) *")
        class_pat = re.compile("&: *class *[a-zA-Z_0-9]")
        dependency_pat = re.compile("#:")
        header_pat = re.compile("!:")
        variable_pat = re.compile("v|Var:")
        while True:
            comment = self.__get_next_comment()
            if comment is None:
                break

            if comment[0] == "#" and re.search(dependency_pat, comment):
                self._mapper.func_go("dep_pat", comment=comment + "\n", path=target_file)
            elif comment[0] == "!" and re.search(header_pat, comment):
                self._mapper.func_go("header_pat", "desc_pat", comment=comment + "\n", path=target_file)
            elif comment[0] == "&" and re.search(class_pat, comment) is not None:
                self._mapper.func_go("class_name_pat", "desc_pat", "link_pat", comment=comment + "\n", path=target_file)
            elif comment[0] == "@" and re.search(function_pat, comment) is not None:
                self._mapper.func_go("func_name_pat", "in_param_pat", "out_param_pat", "desc_pat", "link_pat",
                                     comment=comment + "\n", path=target_file)
            elif comment[:3].upper() == "VAR" and re.search(variable_pat, comment):
                self._mapper.func_go("var_name_pat", "desc_pat", "link_pat", comment=comment + "\n", path=target_file)
        self.link()

    def link(self):
        self._mapper.link2()


class BADiffCommentParser(AbstractParser):

    def __init__(self, *args, **kwargs):
        try:
            if kwargs["before"] == kwargs["after"]:
                logging.error(
                    "BADiffCommentParser(aka BeforeAfterDifferentCommentParser) cannot parse the same beginning "
                    "and ending signal.\nWith begin={} end={}".format(kwargs["before"], kwargs["before"]))
                raise TypeError
        except KeyError as e:
            logging.fatal(e)
        super().__init__(*args, **kwargs)

    def __gleft__(self, ps):
        idx, l = -1, []
        while True:
            idx = ps.find(self._before.replace("\\", ""), idx + 1)
            if idx == -1:
                break
            l.append(idx)
        return l

    def __gright__(self, ps):
        idx, r = -1, []
        while True:
            idx = ps.find(self._after.replace("\\", ""), idx + 1)
            if idx == -1:
                break
            r.append(idx)
        return r

    def pre_symmetric_check(self, page_content):
        lc, rc = self.__gleft__(page_content), self.__gright__(page_content)
        if len(lc) != len(rc):
            return False
        for left, right in zip(lc, rc):
            if left > right:
                return False

        return True
