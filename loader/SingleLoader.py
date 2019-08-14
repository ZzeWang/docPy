
import os
import re
import logging
import abc


logging.basicConfig(level=logging.INFO, format='%(asctime)s - Factory - %(levelname)s - %(message)s')
logger = logging.getLogger("BasedObject")

"""
    &: class FileLoader
    $: 抽象基类，定义一些函数, SingleFileLoad/MultipleFileLoader/MultipleDirsLoader均继承自它
    LK: Loader
"""
class FileLoader:
    __module__ = abc.ABCMeta

    def load(self):
        pass

    def set_attr_by_path(self, path):
        pass

    def set_attr(self, v1, v2, v3):
        pass

"""
    &: class SingleFileLoader
    $: 加载单个文件进入内存，并分页
    LK: Loader
"""
class SingleFileLoader(FileLoader):
    """
        @: init
        >:(int) limit : 定义一个页面大小，默认未5KB
        <:(void)
        $:构造器
        M:SingleFileLoader
    """
    def __init__(self, limit=5 * 1024):
        """
            Var: (str) _file_path
             $:文件路径
             M:SingleFileLoader
        """
        self._file_path = ""
        """
            Var:(str) _file_format
            $:文件格式
            M:SingleFileLoader
        """
        self._file_format = ""  # .cpp, .hpp, .h, .py, .java, ...
        """
            Var:(str) _file_name
            $:文件名
            M:SingleFileLoader
        """
        self._file_name = ""
        """
            Var:(str) chunk
            $:读入的文件内容缓冲区
            M:SingleFileLoader
        """
        self.chunk = ""
        """
            Var:(str) limitation
            $:单页面的大小限制
            M:SingleFileLoader
        """
        self.limitation = limit  #
        """
            Var:(str) pages
            $: 分页存储
            M:SingleFileLoader
        """
        self.pages = []  #
        self.logger = logging.getLogger("SingleFileLoader")

    """
        @: set_attr_by_path
        >:(str) path: 文件路径
        <:(void)
        $:set方法
        M:SingleFileLoader
    """
    def set_attr_by_path(self, path):
        _ff = os.path.splitext(path)[-1][1:]

        if _ff not in ["cpp", "hpp", "h", "py", "java", "html"]:
            logging.debug("{} do not grasp".format(format))
            raise TypeError

        self._file_path = path
        self._file_name = os.path.basename(path)
        self._file_format = os.path.splitext(path)[-1][1:]

    """
        @: set_attr
        >:(str) path: 文件路径
        >:(str) name: 文件名
        >:(str) format: 文件格式
        <:(void)
        $:set方法
        M:SingleFileLoader
    """
    def set_attr(self, path, name, format):
        if format not in ["cpp", "hpp", "h", "py", "java", "html"]:
            logging.debug("{} do not grasp".format(format))
            raise TypeError

        self._file_format = format
        self._file_name = name
        self._file_path = path

    """
          @: load
          >:(void):
          <:(void)
          $:加载单个文件进入你日常并分页
          M:SingleFileLoader
      """
    def load(self):
        assert self._file_path
        assert self._file_name

        try:
            file_size = os.path.getsize(self._file_path)
            self.logger.info(
                "open file '{}' with size={}, aka {}MB".format(self._file_name, file_size, file_size / self.limitation))
            if file_size > self.limitation:  # if source code file's size bigger than 1MB

                with open(self._file_path, "r", encoding="utf8") as target:
                    while True:
                        self.chunk = target.read(self.limitation)
                        if len(self.chunk) == 0:
                            break
                        else:
                            self.pages.append(self.chunk)
                self.logger.info("do paging , count = {}".format(len(self.pages)))
            else:
                with open(self._file_path, "r", encoding="utf8") as target:
                    self.pages.append(target.read())

        except FileNotFoundError as e1:
            self.logger.error(msg="file: {} not exists".format(self._file_path))
