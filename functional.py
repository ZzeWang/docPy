"""
    dependency
"""
import re, abc
from threading import Lock, Thread
import logging

from codeObject import *
from comments.commentGenerator import CommentBlock

logging.basicConfig(level=logging.INFO, format='%(asctime)s - AbstractParser - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AbstractSignalFunctional(object):
    __module__ = abc.ABCMeta

    def __init__(self):

        self._unresolved_relations = {}
        self._obj_set = {}

    def __break_down(self, sp: str) -> tuple:
        return sp[:sp.find(":")].strip().upper(), [i.strip() for i in sp[sp.find(":") + 1:].split(",")]

    def __find_parent_to_add_tgt(self, tgt, parent, header):
        try:
            if len(self._obj_set[parent]) == 1:
                self._obj_set[parent][0].add_child(tgt)
                logging.info(
                    "{} link '{}' (type='{}') -> '{}' (type={})".format(header, tgt.name, tgt.__class__.__name__,
                                                                        self._obj_set[parent][0].name,
                                                                        self._obj_set[parent][0].__class__.__name__))
            else:
                for sub in self._obj_set[parent]:
                    try:
                        sub.add_child(tgt)
                        logging.info(
                            "link '{}' (type='{}') -> '{}' (type={})".format(tgt.name, tgt.__class__.__name__,
                                                                             sub.name,
                                                                             sub.__class__.__name__))
                        break
                    except ValueError:
                        return
                    except TypeError as e:
                        return
                    except Exception as e:
                        logging.fatal(e)
        except KeyError:
            raise KeyError

    def __add_obj(self, name, obj):
        try:
            self._obj_set[name].append(obj)
        except KeyError:
            self._obj_set[name] = [obj]

    def link(self, tgt, parents):
        if isinstance(tgt, ModuleObject):
            return
        for parent in parents:
            try:
                self.__find_parent_to_add_tgt(tgt, parent, "")
            except KeyError:
                if isinstance(tgt.linked_to, list):
                    try:
                        self._unresolved_relations[tgt].append(parent)
                    except KeyError:
                        self._unresolved_relations[tgt] = [parent]
                    logging.info("unresolved link: '{}' "
                                 "(type={}) -> '{}' (type=unknown)".format(tgt.name, tgt.__class__.__name__, parent))

    def link2(self):
        for tgt in self._unresolved_relations.keys():
            for parent in self._unresolved_relations[tgt]:
                try:
                    self.__find_parent_to_add_tgt(tgt, parent, "resolve")
                except KeyError:
                    logging.error(
                        "unresolved relations happened!  {}' -> '{}' . '{}' not find!".format(tgt.name, parent, parent))

    def func_go1(self, bobj: CommentBlock):
        assert issubclass(bobj.__class__, CommentBlock)

        obj = bobj.getObject()
        logging.info("create new obj '{}' (type='{}')".format(obj.name, obj.__class__.__name__))
        self.__add_obj(obj.name, obj)
        _, links = self.__break_down(bobj.link)

        self.link(obj, links)

    def dump(self, info, path):
        pass


class SynSignalFunctional(AbstractSignalFunctional):
    def __init__(self):
        super().__init__()
        self.file_lock = Lock()

    def dump(self, info, path):
        self.file_lock.acquire()
        with open(path, "a") as f:
            f.write(info)
        self.file_lock.release()


class ToMarkdownSignalFunctional(SynSignalFunctional):
    H1 = "# "
    H2 = "## "
    H3 = "### "
    H4 = "#### "
    Bar = " --- "
    Desc = "\n"

    def __init__(self):
        super().__init__()
        self.chunk = ""
        self.mods = []

    def transform_to_md(self):
        self.mods = [mod[0] for mod in self._obj_set.values() if isinstance(mod[0], ModuleObject)]

        for mod in self.mods:
            print("module: " + mod.name)
            for cls in mod.classes:
                for parent in cls.linked_to:
                    if parent is mod:
                        print(mod.name + "::" + "class:" + cls.name)
                        for var in cls.variables:
                            print(cls.name + "::", var.name, var.type)
                        for mth in cls.methods:
                            print(cls.name + "::", mth.name)
            for var in mod.variables:
                if isinstance(var, ModuleVariableObject):
                    for parent in var.linked_to:
                        if parent is mod:
                            print(mod.name + "::", var.name, var.type)
            for func in mod.functions:
                if isinstance(func, ModuleFunctionObject):
                    for parent in func.linked_to:
                        if parent is mod:
                            print(mod.name + "::", func.name)
