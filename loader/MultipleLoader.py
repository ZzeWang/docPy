"""
    dependencies
"""
import os
import re
import logging
import threading
from .SingleLoader import SingleFileLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - MultipleFileLoader - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

"""
    加载目录下所有非文件夹文件
"""


class MultipleFileLoader:

    def __init__(self):
        self._files_lib_path = ""
        self._files = []
        self._files_cnt = 0
        self._loaded_file = []  # SingleFileLoader

    """
        setter方法
        vod set_attr(v1)
        :param lib : the group for files
        :return : void
    """
    def set_attr(self, lib):
        self._files_lib_path = lib

    """
        加载单个文件到self._loaded_file 并
        启动多个线程加载单个文件
        void load(void)
        :param:void
        :return:void
    """
    def load(self):
        try:
            for path in os.listdir(self._files_lib_path):
                if not os.path.isdir(path):
                    single = SingleFileLoader()

                    ppath = self._files_lib_path + '\\' + path
                    nname = os.path.basename(path)
                    fformat = os.path.splitext(nname)[-1][1:]
                    single.set_attr(ppath, nname, fformat)
                    self._loaded_file.append(threading.Thread(target=single.load, name=nname))
                else:
                    logging.info("drop a dir with path={}".format(path))
        except FileNotFoundError as f_not_e:
            logging.fatal("path = {} not exists".format(self._files_lib_path))

        try:
            for sing in self._loaded_file:
                sing.start()
        except FileExistsError as e:
            logging.fatal(e.errno)
