"""
    dependency
"""
import re

"""
    2019年8月8日 星期四 
    抽象基类
"""


class AbstractParser:

    def __init__(self, *args, **kwargs):
        self._before = ""
        self._after = ""
        if kwargs and kwargs["after"] and kwargs["before"]:
            self._after = kwargs["after"]
            self._before = kwargs["before"]
        else:
            self._after = ""
            self._before = ""

        self._table = {}  # signals table
        self._comment_list = []  # block of comments
        self._comment_pattern = re.compile("{}(?P<content>[\n ]*(.*?)[\n ]*{}".format(self._before, self._after))