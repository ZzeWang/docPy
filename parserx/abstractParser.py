"""
    dependency
"""
import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from loader.SingleLoader import SingleFileLoader
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
        self.file = SingleFileLoader()

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
        pattern_before = re.compile(self._before)
        pattern_after = re.compile(self._after)

        if len(re.findall(pattern_before, page_content)) == \
                len(re.findall(pattern_after, page_content)):
            return True, -1
        else:
            return False, page_content.rfind(self._before.replace('\\', ''))

    """
        从每页中提取出一个完整的注释快，并保存到self._comment_list中
        :param:void
        :return:void
    """

    def parse_comment(self):
        for page_c in range(len(self.file.pages)):
            is_not_page, idx = self.pre_symmetric_check(self.file.pages[page_c])
            tmp = re.findall(self._comment_pattern, self.file.pages[page_c])
            for result in tmp:
                self._comment_list.append(result)
                logging.info("find a comment block with length={}".format(len(result)))

            if page_c + 1 == len(self.file.pages):
                break

            if is_not_page:
                pass
            else:
                pos = self.file.pages[page_c + 1].find(self._after.replace("\\", ""))

                if pos == -1:  #
                    self._comment_list.append(self.file.pages[page_c][idx + 2:])
                    logging.info(
                        "find a vary special situation with starting at page={}:{}, end up with page={}:{}".format(
                            page_c, idx, page_c + 1, pos))
                else:
                    #  idx + len(...) 去除掉注释前缀的前一部分，
                    #  pos  去除注释后缀的后一部分
                    self._comment_list.append(
                        self.file.pages[page_c][idx + len(self._before.replace("\\", "")):] + self.file.pages[
                                                                                                  page_c + 1][:pos])
                    self.file.pages[page_c + 1] = self.file.pages[page_c + 1][pos + 2:]  # 对齐
                    logging.info(
                        "find a not-continuity comment block with starting at page={}:{}, end up with page={}:{}".format(
                            page_c, idx, page_c + 1, pos))

    def __get_next_comment(self):
        try:
            return next(self.iter_of_comment).strip()
        except StopIteration as e:
            return None
        pass

    """
        对每一块注释，匹配特征符号（@，#，！等），调用
        self._mapper的方法处理，此处_mapper必须是AbstractSignalFunctional的子类
    """

    def switch(self, target_file):
        function_pat = re.compile("@: *[a-zA-Z_0-9]+ *(?:[a-zA-Z_0-9]+|[a-zA-Z_0-9]+:{2}) *")
        class_pat = re.compile("&: *class *[a-zA-Z_0-9]")
        dependency_pat = re.compile("#:")
        header_pat = re.compile("!:")
        tasks = []
        while True:
            comment = self.__get_next_comment()
            if comment is None:
                break

            if comment[0] == "#" and re.search(dependency_pat, comment):
                tasks.append(self._thread_executor.submit(self._mapper.func_dependency, comment=comment + "\n",
                                                          path=target_file))
            elif comment[0] == "!" and re.search(header_pat, comment):
                tasks.append(
                    self._thread_executor.submit(self._mapper.func_header, comment=comment + "\n", path=target_file))
            elif comment[0] == "&" and re.search(class_pat, comment) is not None:
                tasks.append(self._thread_executor.submit(self._mapper.func_class_signature, comment=comment + "\n",
                                                          path=target_file))
            elif comment[0] == "@" and re.search(function_pat, comment) is not None:
                tasks.append(self._thread_executor.submit(self._mapper.func_function_signature, comment=comment + "\n",
                                                          path=target_file))
            else:
                logging.debug("capture a Non-doc comment")
        for future in as_completed(tasks):
            logging.info("task {} have finished".format(future))
