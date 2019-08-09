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


class DependencyObject(BasedObject):
    def __init__(self, name):
        super().__init__(name)
        self.deps = []


class VariableObject(BasedObject):
    def __init__(self, name):
        super().__init__(name)
        self.its_module = None
        self.its_class = None


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
                        logging.info("link function '{}' -> class '{}'".format(tgt.name, parent))
                    except KeyError:
                        logging.error("class '{}' do not exists or have not been created.".format(parent))
                elif type == "LK":
                    try:
                        self._module_set[parent].functions.append(tgt)
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
                        logging.info("link variable '{}' -> class '{}'".format(tgt.name, parent))
                    elif type == "LK":
                        self._module_set[parent].variables.append(tgt)
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
                            var = VariableObject(tx[0])
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


"""
   建立模块/类/函数之间的链接
"""


# TODO wait to refactor
class ToMdSignalFunctional(SynSignalFunctional):
    H1 = "#"
    H2 = "##"
    H3 = "###"
    H4 = "####"
    Bar = "---"
    Desc = "\n"

    def func_function_signature(self, **kwargs):
        name_pat = re.compile("@: *([a-zA-Z_0-9]+) *\n")
        in_pat = re.compile(">: *\( *(?P<type>[a-zA-Z_0-9:]+) *\) *(?P<name>[a-zA-Z_0-9]+) *: *(?P<desc>.*?) *\n")
        out_pat = re.compile("<: *\( *(?P<type>[a-zA-Z_0-9:]+) *\) *\n")
        desc_pat = re.compile("\$:(.*?) *\n")
        try:
            func_name = re.findall(name_pat, kwargs["comment"])[0]
            in_list = re.findall(in_pat, kwargs["comment"])
            out_type = re.findall(out_pat, kwargs["comment"])[0]
            desc_list = re.findall(desc_pat, kwargs["comment"])

            md_func_name = "{} {}\n\n".format(self.__class__().H2, func_name)

            if out_type == "void":
                md_out_type = "{} *return:* void\n\n".format(self.__class__().H3)
            else:
                md_out_type = "{} *return:* void\n\n".format(self.__class__().H3, out_type)
            md_input_param = ""
            md_desc_info = ""

            for val in in_list:
                type, name, desc = val[0], val[1], val[2]
                md_input_param += "{} {}->(*{}*):\n{} {}\n".format(self.__class__().H3, name, type,
                                                                   self.__class__().Desc,
                                                                   desc)
            for desc in desc_list:
                md_desc_info += desc

            md_desc_info += "\n\n" + self.__class__().Bar + "\n\n"

            self.dump(md_func_name + md_input_param + md_out_type + md_desc_info, kwargs["path"])
            logging.info("add a function name={}".format(md_func_name))
        except KeyError as e:
            logging.fatal(e)
        except IndexError as e:
            logging.fatal(e)

    """
           such as
           /*
               &: CppClass
               $: this is a c++ class
           */
           class CppClass ... 
       """

    def func_class_signature(self, **kwargs):
        pattern = re.compile("&:(.*?) *\n\s*\$:(.*?) *\n", re.DOTALL)
        try:
            class_name = re.findall(pattern, kwargs["comment"])[0][0]
            class_desc = re.findall(pattern, kwargs["comment"])[0][1]
            md_class = "{} {}\n".format(ToMdSignalFunctional.H2, class_name)
            md_desc = "{} {}\n".format(ToMdSignalFunctional.Desc, class_desc)
            self.dump("{}\n{}\n\n{}\n".format(md_class, md_desc, self.__class__().Bar), kwargs["path"])
            logging.info("add a class name={}".format(class_name))
        except KeyError as e:
            logging.fatal(e)
        except IndexError as e:
            logging.fatal(e)

    """
        such as
        /*
            !: this file contains all class 
            !: that be used to deal with regex language
            !: and some functional object.
        */
    """

    def func_header(self, **kwargs):
        pattern = re.compile("!: *(.*?) *\n")
        try:
            desc = re.findall(pattern, kwargs["comment"])
            md_desc = self.__class__().H1 + " Description\n"
            for d in desc:
                md_desc += "{} ".format(d)
            md_desc += "\n\n{}\n\n".format(self.__class__().Bar)
            self.dump(md_desc, kwargs["path"])
            logging.info("add a title")
        except KeyError as e:
            logging.fatal(e)
        except IndexError as e:
            logging.fatal(e)

    """
        such as 
        /*
            # iostream
            # osgGA
            # boost/smart_ptr/scoped_ptr
        */
    """

    def func_dependency(self, **kwargs):
        try:
            dep = self.combine_to_tuple("dep_pat", kwargs["comment"])
            md_dep = self.__class__().H1 + " Dependency\n"
            while True:
                try:
                    md_dep += "{}\n".format(next(dep))
                except StopIteration:
                    break
            md_dep += "\n\n{}\n\n".format(self.__class__().Bar)
            self.dump(md_dep, kwargs["path"])
            logging.info("add a title")
        except KeyError as e:
            logging.fatal(e)
        except IndexError as e:
            logging.fatal(e)
