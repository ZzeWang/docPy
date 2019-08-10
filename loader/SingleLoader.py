"""
    dependencies
"""
import os
import re
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - SingleFileLoader - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FileLoader:
    def load(self):
        pass

    def set_attr_by_path(self, path):
        pass

    def set_attr(self,v1,v2,v3):
        pass


class SingleFileLoader(FileLoader):

    def __init__(self, limit=100):
        super().__init__()
        self._file_path = ""
        self._file_format = ""  # .cpp, .hpp, .h, .py, .java, ...
        self._file_name = ""
        self.chunk = ""
        self.limitation = limit  #
        self.pages = []  # 对于超过限制大小的单个文件进行分页处理

    """
        setter方法
        void set_attr(v1,v2,v3)
        :param path : 文件路径
        :param name : 文件名
        :param format : 文件格式
        :return : void
    """

    def set_attr_by_path(self, path):
        self._file_path = path
        self._file_name = os.path.basename(path)
        self._file_format = os.path.splitext(path)[-1][1:]
        assert self._file_format in ["cpp", "hpp", "h", "py", "java", "html"]

    def set_attr(self, path, name, format):
        assert format in ["cpp", "hpp", "h", "py", "java", "html"]

        self._file_format = format
        self._file_name = name
        self._file_path = path

    """
        将文件加载进入内存，如果文件大小超过限制，则进行分页
        分页结果存入self.pages列表
        void load(void)
        :param:void
        :return :void
    """

    def load(self):
        assert self._file_path
        assert self._file_name

        try:
            file_size = os.path.getsize(self._file_path)
            logging.info("open file '{}' with size={}, aka {}MB".format(self._file_name, file_size, file_size / self.limitation))
            if file_size > self.limitation:  # if source code file's size bigger than 1MB

                with open(self._file_path, "r", encoding="utf8") as target:
                    while True:
                        self.chunk = target.read(self.limitation)
                        if len(self.chunk) == 0:
                            break
                        else:
                            self.pages.append(self.chunk)
                logging.info("do paging , count = {}".format(len(self.pages)))
            else:
                with open(self._file_path, "r", encoding="utf8") as target:
                    self.pages.append(target.read())

        except FileNotFoundError as e1:
            logging.error(msg="file: {} not exists".format(self._file_path))
