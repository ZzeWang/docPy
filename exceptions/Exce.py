import abc

"""
    !: Exceptions
    $: 定义在docPy中需要用到的异常，方便后期维护
"""

"""
    &: class CommentParserException
    $: 抽象基类，定义在一个CommentBlock对象解析所需关键字字段时，出现完整性缺失异常
"""


class CommentParserException(Exception):
    __module__ = abc.ABCMeta
    """
        @: init
        >:(subclassOfCommentBlock) comment_obj : 出现解析错误时的注释文档节点对象
        $:构造器
    """

    def __init__(self, comment_obj):
        super().__init__()
        """
            Var: (subclassOfCommentBlock) comment_obj
            $: 解析时异常对象
        """
        self.comment_obj = comment_obj


"""
    &: class IntegratedException
    $: 定义完整性异常字段
"""


class IntegratedException(CommentParserException):
    """
        @: init
        >: (list[str]) nec: 必须字段
        >:(subclassOfCommentBlock) comment_obj : 出现解析错误时的注释文档节点对象
        $:
    """

    def __init__(self, nec: str, c_obj):
        super().__init__(c_obj)
        """
            Var: (str) necessary_field
            $: 完整性定义
        """
        self.necessary_field = nec

    def __str__(self):
        return r"comment object '{}' (type={}) needs necessary field '{}', but not found.". \
            format(self.comment_obj.name, self.comment_obj.__class__.__name__, self.necessary_field)


class SyntaxException(CommentParserException):

    def __init__(self, right:str, error:str,c_obj):
        super().__init__(c_obj)
        self.right = right
        self.error = error

    def __str__(self):
        return r"comment block syntax error: expect '%s' , but found '%s'" % \
               (self.right.replace("\n", "\\n"), self.error.replace("\n", "\\n"))


