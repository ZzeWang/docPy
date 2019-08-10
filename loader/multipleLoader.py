"""
    dependencies
"""
import os
import re
import logging
import threading
from .SingleLoader import SingleFileLoader, FileLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - MultipleFileLoader - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

"""
    加载目录下所有非文件夹文件
"""


class MultipleFileLoader(FileLoader):

    def __init__(self, path=""):
        self._files_lib_path = path
        self._loaded_file = []  # SingleFileLoader

    """
        setter方法
        vod set_attr(v1)
        :param lib : the group for files
        :return : void
    """

    def set_attr_by_path(self, lib):
        self._files_lib_path = lib

    """
        加载单个文件到self._loaded_file 并
        启动多个线程加载单个文件
        void load(void)
        :param:void
        :return:void
    """

    def load(self):
        threadings = []
        try:
            for path in os.listdir(self._files_lib_path):
                if not os.path.isdir(path):
                    single = SingleFileLoader()
                    ppath = self._files_lib_path + '\\' + path
                    nname = os.path.basename(path)
                    fformat = os.path.splitext(nname)[-1][1:]
                    single.set_attr(ppath, nname, fformat)
                    self._loaded_file.append(single)
                    threadings.append(threading.Thread(target=single.load, name=single._file_name))
                else:
                    logging.info("drop a dir with path={}".format(path))
        except FileNotFoundError as f_not_e:
            logging.fatal(f_not_e)
            logging.fatal("path = {} not exists".format(self._files_lib_path))

        try:
            for sing in threadings:
                sing.start()
            for sing in threadings:
                sing.join()
        except FileExistsError as e:
            logging.fatal(e.errno)