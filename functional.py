"""
    dependency
"""
import re


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


"""
    C++ 到 .md 格式的映射规则
"""


class CppToMdSignalFunctional(AbstractSignalFunctional):
    """

    """

    """
        such as
        /*
            @: CppClass
            $: this is a c++ class
        */
        class CppClass ... 
    """

    def func_class_signature(self, **kwargs):
        pattern = re.compile("@:(.*?) *\n\$:(.*?) *\n", re.DOTALL)
