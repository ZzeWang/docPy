"""
    dependency
"""
import re
from threading import Lock, Thread
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - AbstractParser - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AbstractSignalFunctional(object):
    """


    """

    def __init__(self):
        self._patterns = {}
        self.have_set_header = False
        self.have_set_dependency = False

    """
        用来提取仅有一个内容的情况，
    """

    def combine_to_tuple(self, key, string):
        for single in re.findall(self._patterns[key], string):
            if isinstance(single, tuple):
                yield single
            else:
                yield (single,)

    def func_go(self, *args, **kwargs):
        for oi in args:
            try:
                result = self.combine_to_tuple(oi, kwargs["comment"])
                while True:
                    try:
                        __class = next(result)  # class of result
                        formatted_info = self.format_this(__class, kwargs["format"])
                        self.dump(formatted_info, kwargs["path"])
                    except StopIteration:
                        break
            except KeyError as e:
                logging.fatal(e)

    def format_this(self, result, format_str):
        return ""

    """
        用于处理函数签名映射 @ to any
    """

    def func_function_signature(self, **kwargs):
        pass

    """
        用于处理类签名映射 & to any
    """

    def func_class_signature(self, **kwargs):
        pass

    """
        用于处理源文件综述映射 ! to any
    """

    def func_header(self, **kwargs):
        pass

    """
        用于处理依赖映射 # to any
    """

    def func_dependency(self, **kwargs):
        pass

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


class LinkAbleSignalFunctional(SynSignalFunctional):

    def __init__(self):
        super().__init__()
        self._class_set = set()  # record the parsed class's name
        self._function_set = set()
        self._module_set = set()
        self._var_set = set()

        self.__class_of_module = {}  # {module_name: [classes of it]}
        self.__function_of_module = {}  # {module_name: [function of it]}
        self.__method_of_class = {}  # {class_name: [methods of it]}
        self.__var_of_module = {}
        self.__var_of_class = {}


# TODO wait to refactor
class ToMdSignalFunctional(SynSignalFunctional):
    H1 = "#"
    H2 = "##"
    H3 = "###"
    H4 = "####"
    Bar = "---"
    Desc = "\n"

    def __init__(self):
        super().__init__()
        self._patterns = {
            "func_name_pat": re.compile("@: *([a-zA-Z_0-9]+) *\n"),
            "class_name_pat": re.compile("&:(.*?) *\n\s*\$:(.*?) *\n", re.DOTALL),
            "var_name_pat": re.compile("Var: *\((.*?)\)*(.+?)\n"),
            "in_param_pat": re.compile(">: *\( *(?P<type>[a-zA-Z_0-9:]+) *\) *(?P<name>[a-zA-Z_0-9]+) *: *(?P<desc>.*?) *\n"),
            "out_param_pat": re.compile("<: *\( *(?P<type>[a-zA-Z_0-9:]+) *\) *\n"),
            "desc_pat": re.compile("\$:(.*?) *\n"),
            "header_pat": re.compile("!: *(.*?) *\n"),
            "dep_pat": re.compile("#: *(.*?) *\n"),
            "link_pat": re.compile("(?:(?:To|O)|(?:Lk|K)|(?:[Mm])): *(?:(.*?),|(.*?)) *\n")
        }

    """
        such as
        /*
            @: foo
            >: (int) para1:desc
            >: (string) para2:desc
            <: (bool)
            $: this function calls foo, and it has two param , which type is int and string respectively
            $: And its returned value's type is a bool variable
        */
    """

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
