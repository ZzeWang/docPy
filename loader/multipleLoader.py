
import os
import re
import logging
import threading
from .SingleLoader import SingleFileLoader, FileLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - Factory - %(levelname)s - %(message)s')
logger = logging.getLogger("BasedObject")

"""
    #: os,re,logging,threading,SingleFileLoader,FileLoader
    LK: Loader
"""

"""
    &: class MultipleFileLoader
    $: 多文件加载器，仅处理一个目录下的所有文件，将所有文件加载
    $: 进入_loaded_file中，并进行分页。打开文件读操作使用匿名的线程处理
    LK: Loader
"""
class MultipleFileLoader(FileLoader):
    """
        @: init
        >:(str) path: 文档目录
        <:(void)
        $:构造器
        M:MultipleFileLoader
    """
    def __init__(self, path=""):
        """
            Var:(str) path
            $: 保存文档路径
            M: MultipleFileLoader
        """
        self._files_lib_path = path
        """
            Var: (list[SingleFileLoader]) _loaded_file
            $: 保存_files_lib_path下所有文件的文件加载器
            M:MultipleFileLoader
        """
        self._loaded_file = []  # SingleFileLoader
        self.logger = logging.getLogger("MultipleFileLoader")

    """
        @: set_attr_by_path
        >:(str) lib
        <:(void)
        $:设置_files_lib_path属性，由于本人最早开始写该类并在此之前
        $:一直在用Java所以免不了有些Java的'不良习惯'，忍着吧
        M:MultipleFileLoader
    """
    def set_attr_by_path(self, lib):
        self._files_lib_path = lib

    """
        @: load
        >:(void):
        <:(void)
        $: 加载文件进入内存，并启动加载线程
        M:MultipleFileLoader
    """
    def load(self):
        threads = []
        try:
            for p in os.listdir(self._files_lib_path):
                path = os.path.join(self._files_lib_path, p)
                if not os.path.isdir(path):
                    single = SingleFileLoader()
                    ppath = self._files_lib_path + '\\' + path
                    nname = os.path.basename(path)
                    fformat = os.path.splitext(nname)[-1][1:]
                    try:
                        single.set_attr(ppath, nname, fformat)
                    except TypeError:
                        continue
                    self._loaded_file.append(single)
                    threads.append(threading.Thread(target=single.load, name=single._file_name))
                else:
                    logging.info("drop a dir with path={}".format(path))
        except FileNotFoundError as f_not_e:
            self.logger.fatal(f_not_e)
            self.logger.fatal("path = {} not exists".format(self._files_lib_path))

        try:
            for sing in threads:
                sing.start()
            for sing in threads:
                sing.join()
        except FileExistsError as e:
            self.logger.fatal(e.errno)

"""
    &: class MultipleDirsLoader
    $: 递归查询整个目录并将文档加载进入内存
    LK:Loader
"""
class MultipleDirsLoader(MultipleFileLoader):

    """
        @: load
        >:(void):
        <:(void)
        $:对函数load_recursion的包装
        m:MultipleDirsLoader
    """
    def load(self):
        self.__load_recursion(self._files_lib_path)
    """
        @:__load_recursion
        >:(str) _path : 递归路径  
        <:(void)
        $:递归查找路径下的所有文档，并加载进入内存，起始路径未_files_lib_path
        $:通过包装器load传入启动递归
        M:MultipleDirsLoader
    """
    def __load_recursion(self, _path):
        threads = []
        try:
            for p in os.listdir(_path):
                if p[0] == ".":
                    continue
                path = os.path.join(_path, p)
                if not os.path.isdir(path):
                    single = SingleFileLoader()
                    ppath = path
                    nname = os.path.basename(path)
                    fformat = os.path.splitext(nname)[-1][1:]
                    try:
                        single.set_attr(ppath, nname, fformat)
                    except TypeError:
                        continue
                    self._loaded_file.append(single)
                    threads.append(threading.Thread(target=single.load, name=single._file_name))
                else:
                    self.__load_recursion(path)
        except FileNotFoundError as f_not_e:
            self.logger.fatal(f_not_e)
            self.logger.fatal("path = {} not exists".format(self._files_lib_path))
        try:
            for sing in threads:
                sing.start()
            for sing in threads:
                sing.join()
        except FileExistsError as e:
            self.logger.fatal(e.errno)
