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


"""
    &: class SyntaxException
    $: 定义语法异常
"""


class SyntaxException(CommentParserException):

    def __init__(self, right: str, error: str, c_obj):
        super().__init__(c_obj)
        self.right = right
        self.error = error

    def __str__(self):
        return r"comment block syntax error: expect '%s' , but found '%s'" % \
               (self.right.replace("\n", "\\n"), self.error.replace("\n", "\\n"))


import codeObject

"""
    &: class LinkTypeException
    $: 定义连接异常，主要是检查用户在编写文档注释时是否符合节点之间的逻辑继承关系
"""
class LinkTypeException(Exception):

    def __init__(self, child, parent):
        super().__init__()
        self.child = child
        self.parent = parent

    def __str__(self):
        if not isinstance(self.parent, codeObject.Scoped):
            return "linking error: object '{}' (type={}) is not a Scoped Object.\n" \
                   "it shell not have Child Node!".format(self.parent.name, self.parent.__class__.__name__)

        if isinstance(self.parent, codeObject.ProjectObject):
            return "linking error: object '{}' (type={}) can't be linked to '{}' (type={})\n" \
                   "A Project can only add ModuleObject". \
                format(self.child.name, self.child.__class__.__name__, self.parent.name, self.parent.__class__.__name__)
        if isinstance(self.parent, codeObject.ModuleObject):
            return "linking error: object '{}' (type={}) can't be linked to '{}' (type={})\n" \
                   "A Module can only add ClassObject/ModuleFunction/ModuleVariable". \
                format(self.child.name, self.child.__class__.__name__, self.parent.name, self.parent.__class__.__name__)
        if isinstance(self.parent, codeObject.ClassObject):
            return "linking error: object '{}' (type={}) can't be linked to '{}' (type={})\n" \
                   "A Class can only add MethodObject/MemberVariableObject". \
                format(self.child.name, self.child.__class__.__name__, self.parent.name, self.parent.__class__.__name__)
        if isinstance(self.parent, codeObject.ReferencedObject):
            return "linking error: object '{}' (type={}) can't be linked to '{}' (type={})\n" \
                   "A ReferencedObject is not a ScopedObject". \
                format(self.child.name, self.child.__class__.__name__, self.parent.name, self.parent.__class__.__name__)
