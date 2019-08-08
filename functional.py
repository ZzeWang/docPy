"""
    dependency
"""
import re
from threading import Lock, Thread


class AbstractSignalFunctional(object):
    """
        用于处理输入参数映射  > to any
    """

    def func_in(self, **kwargs):
        pass

    """
        用于处理返回值映射  < to any
    """

    def func_out(self, **kwargs):
        pass

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
       用于处理描述映射  $ to any
    """

    def func_desc(self, **kwargs):
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
    C++ 到 .md 格式的映射规则
"""


class CppToMdSignalFunctional(SynSignalFunctional):
    """

    """
    H1 = "#"
    H2 = "##"
    H3 = "###"
    H4 = "####"
    Bar = "---"
    Desc = "\n"

    """
        such as
        /*
            @: foo
            >: (int) para1
            >: (string) para2
            <: bool
            $: this function calls foo, and it has two param , which type is int and string respectively
            $: And its returned value's type is a bool variable
        */
    """

    def func_function_signature(self, **kwargs):
        name_pat = re.compile("@: *([a-zA-Z_0-9]+) *\n")
        in_pat = re.compile(">: \(([a-zA-Z_0-9:]+)\) *([a-zA-Z_0-9]+) *\n")
        out_pat = re.compile("<: *[a-zA-Z_0-9:]+\n")
        desc_pat = re.compile("\$:(.*?) *\n")

        try:
            func_name = re.findall(name_pat, kwargs["comment"])[0]
            in_list = re.findall(in_pat, kwargs["comment"])
            out_list = re.findall(out_pat, kwargs["comment"])
            desc_list = re.findall(desc_pat, kwargs["comment"])
        except KeyError as e:
            pass


    """
           such as
           /*
               &: CppClass
               $: this is a c++ class
           */
           class CppClass ... 
       """

    def func_class_signature(self, **kwargs):
        pattern = re.compile("@:(.*?) *\n\s*\$:(.*?) *\n", re.DOTALL)
        try:
            class_name = re.findall(pattern, kwargs["comment"])[0][0]
            class_desc = re.findall(pattern, kwargs["comment"])[0][1]
            md_class = "{} {}".format(CppToMdSignalFunctional.H2, class_name)
            md_desc = "{} {}".format(CppToMdSignalFunctional.Desc, class_desc)
            self.dump("{}\n{}".format(md_class, md_desc), kwargs["path"])
        except IndexError as e:
            pass
