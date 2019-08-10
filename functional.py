"""
    dependency
"""
import re
from threading import Lock, Thread
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - AbstractParser - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BasedObject:
    def __init__(self, name):
        self.name = name
        self.desc = ""
        self.linked_to = None


class DependencyObject(BasedObject):
    def __init__(self, name):
        super().__init__(name)
        self.deps = []


class VariableObject(BasedObject):
    def __init__(self, name):
        super().__init__(name)
        self.type = None



class ModuleObject(BasedObject):
    def __init__(self, name):
        super().__init__(name)
        self.classes = []
        self.variables = []
        self.functions = []


class FunctionObject(BasedObject):
    def __init__(self, name):
        super().__init__(name)
        self.its_class = None
        self.its_module = None
        self.in_param = []
        self.out_type = ""


class ClassObject(BasedObject):
    def __init__(self, name):
        super().__init__(name)
        self.methods = []
        self.variables = []


class AbstractSignalFunctional(object):

    def __init__(self):

        self._patterns = {
            "func_name_pat": re.compile("@: *([a-zA-Z_0-9]+) *\n"),
            "class_name_pat": re.compile("&: *class *(.*?) *\n"),
            "var_name_pat": re.compile("[vV]ar: *\((.*?)\) *(.*?) *\n"),
            "in_param_pat": re.compile(
                ">: *\( *(?P<type>[a-zA-Z_0-9:]+) *\) *(?P<name>[a-zA-Z_0-9]+) *: *(?P<desc>.*?) *\n"),
            "out_param_pat": re.compile("<: *\( *(?P<type>[a-zA-Z_0-9:]+) *\) *\n"),
            "desc_pat": re.compile("\$:(.*?)\n"),
            "header_pat": re.compile("!: *(.*?) *\n"),
            "dep_pat": re.compile("#: *(.*?) *\n"),
            "link_pat": re.compile(" (?:(?:[ToOt]+)|(?:[LKk]+)|(?:[Mm])): *.*? *\n")
        }

        self._class_set = {}
        self._module_set = {}
        self._variable_set = {}
        self._header_set = {}
        self._function_set = {}

    def combine_to_tuple(self, key: str, string: str):
        for single in re.findall(self._patterns[key], string):
            if isinstance(single, tuple):
                yield single
            else:
                yield (single,)

    def __break_down(self, sp: str) -> tuple:
        return sp[:sp.find(":")].strip().upper(), [i.strip() for i in sp[sp.find(":") + 1:].split(",")]

    def link(self, tgt, parents):
        type, pts = self.__break_down(parents)

        if isinstance(tgt, ModuleObject):
            logging.info("{} module do not necessary to have a parent.".format(tgt.name))
            return False

        if isinstance(tgt, ClassObject):
            for parent in pts:
                # TODO when parent do not exits
                try:
                    self._module_set[parent].classes.append(tgt)
                    tgt.linked_to = self._module_set[parent]
                    logging.info("link class '{}' -> module '{}'".format(tgt.name, parent))
                except KeyError as e:
                    logging.error("class '{}' do not exists or have not been created.".format(parent))
                    return False
            return True

        if isinstance(tgt, FunctionObject):
            for parent in pts:
                # TODO when parent do not exits

                if type == "M":
                    try:
                        self._class_set[parent].methods.append(tgt)
                        tgt.linked_to = self._class_set[parent]
                        logging.info("link function '{}' -> class '{}'".format(tgt.name, parent))
                    except KeyError:
                        logging.error("class '{}' do not exists or have not been created.".format(parent))
                elif type == "LK":
                    try:
                        self._module_set[parent].functions.append(tgt)
                        tgt.linked_to = self._module_set[parent]
                        logging.info("link function '{}' -> module '{}'".format(tgt.name, parent))
                    except KeyError:
                        logging.error("module '{}' do not exists or have not been created.".format(parent))
                else:
                    logging.error("suffix may be error, with suffix={}(type)".format(type))
                    return False

            return True
        if isinstance(tgt, VariableObject):
            for parent in pts:
                # TODO when parent do not exits
                try:
                    if type == "M":
                        self._class_set[parent].variables.append(tgt)
                        tgt.linked_to = self._class_set[parent]
                        logging.info("link variable '{}' -> class '{}'".format(tgt.name, parent))
                    elif type == "LK":
                        self._module_set[parent].variables.append(tgt)
                        tgt.linked_to = self._module_set[parent]
                        logging.info("link variable '{}' -> module '{}'".format(tgt.name, parent))
                    else:
                        logging.error("suffix may be error, with suffix={}(type)".format(type))
                        return False
                except KeyError as e:
                    logging.error("class or module '{}' do not exists or have not been created.".format(parent))
                    return False
            return True

    def func_go(self, *args, **kwargs):
        global target
        desc = ""
        for oi in args:
            try:
                result = self.combine_to_tuple(oi, kwargs["comment"])
                while True:
                    try:
                        # TODO refactor
                        tx = next(result)
                        if oi == "class_name_pat":
                            cls = ClassObject(tx[0])
                            self._class_set[tx[0]] = cls
                            target = cls
                            logging.info("create a new class '{}'".format(target.name))
                        elif oi == "func_name_pat":
                            func = FunctionObject(tx[0])
                            self._function_set[tx[0]] = func
                            target = func
                            logging.info("create a new function '{}'".format(target.name))
                        elif oi == "var_name_pat":
                            var = VariableObject(tx[1])
                            var.type = tx[0]
                            self._variable_set[tx[0]] = var
                            target = var
                            logging.info("create a new variable '{}'".format(target.name))
                        elif oi == "header_pat":
                            m = ModuleObject(tx[0])
                            self._module_set[tx[0]] = m
                            target = m
                            logging.info("create a new module '{}'".format(target.name))
                        elif oi == "desc_pat":
                            desc += tx[0]
                        elif oi == "link_pat":
                            self.link(target, tx[0])  # tx(parent) <- target
                        elif oi == "in_param_pat":
                            target.in_param.append(tx)
                            logging.info(
                                "create a new function input param '{}' type={}, desc={}".format(tx[1], tx[0], tx[2]))
                        elif oi == "out_param_pat":
                            target.out_type = tx[0]
                            logging.info(
                                "create a new function output param type={}".format(tx[0]))
                        else:
                            break
                    except StopIteration:
                        break
            except KeyError as e:
                logging.fatal(e)
        target.desc = desc

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
    Desc = " \n "

    def __init__(self):
        super().__init__()
        self.chunk = ""

    def markdown_format(self):
        for md in self._module_set.keys():
            md_name = self._module_set[md].name
            md_desc = self._module_set[md].desc
            self.chunk += ToMarkdownSignalFunctional.H1 + " *Modules* {}\n".format(md_name)
            self.chunk += ToMarkdownSignalFunctional.Desc + " {}\n".format(md_desc)
            self.chunk += ToMarkdownSignalFunctional.Bar + " \n"
            for var in self._module_set[md].variables:
                if var.linked_to is self._module_set[md]:
                    self.chunk += ToMarkdownSignalFunctional.H2 + " *Variable*  {}\n".format(var.name)
                    self.chunk += ToMarkdownSignalFunctional.Desc + " {}\n".format(var.desc)
                    self.chunk += ToMarkdownSignalFunctional.Bar + " \n"
            for func in self._module_set[md].functions:
                if func.linked_to is self._module_set[md]:
                    self.chunk += ToMarkdownSignalFunctional.H2 + "*Function*  {}\n".format(func.name)
                    for param in func.in_param:
                        self.chunk += ToMarkdownSignalFunctional.H4 + "*param*  ({}) {}:\n".format(param[0], param[1])
                        self.chunk += ToMarkdownSignalFunctional.Desc + "{}\n".format(param[2])
                    self.chunk += ToMarkdownSignalFunctional.H4 + "*return*  {}\n".format(func.out_type)
            for cls in self._module_set[md].classes:
                self.chunk += ToMarkdownSignalFunctional.H2 + " *Class*  {}\n".format(cls.name)
                for var in cls.variables:
                    self.chunk += ToMarkdownSignalFunctional.H3 + " *var*  {}: *({})*\n".format(var.name, var.type)
                    self.chunk += ToMarkdownSignalFunctional.Desc + " {}\n".format(var.desc)
                for method in cls.methods:
                    self.chunk += ToMarkdownSignalFunctional.H3 + " *method*  {}\n".format(method.name)
                    for param in method.in_param:
                        self.chunk += ToMarkdownSignalFunctional.H4 + "*param*  ({}) {}:\n".format(param[0], param[1])
                        self.chunk += ToMarkdownSignalFunctional.Desc + "{}\n".format(param[2])
                    self.chunk += ToMarkdownSignalFunctional.H4 + "*return* {}\n".format(method.out_type)
        self.dump(self.chunk, r"E:\file\pyProj\docPy\test\targetfile")
