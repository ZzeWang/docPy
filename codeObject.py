import abc, logging
import exceptions.Exce
logging.basicConfig(level=logging.INFO, format='%(asctime)s - Factory - %(levelname)s - %(message)s')
logger = logging.getLogger("BasedObject")
"""
    pj:docPy
    $:desc
"""
"""
    !: DocObject
    $: 定义文档节点对象，从注释块对象中生成一个指定的文档节点
    $: 该节点将用于*1.产生链接特性 2.方便functional.report()函数访问文档的所有节点*
"""

"""
    &: class BasedObject
    $: 抽象基类，所有节点对象都继承自它
"""
class BasedObject(object):
    __module__ = abc.ABCMeta

    def __init__(self, name):
        """
            var: (str) name
            $: 文档节点的名称，如一个类名或者一个模块名
        """
        self.name = name
        """
            Var: (str) desc
            $:对该节点的描述，也就是注释内容 
        """
        self.desc = ""
        """
            Var:(str|list) linked_to
            $: 该节点所指向的父节点，根据子类的不同而类型不同
            $: 一个类域下的所有节点的linked_to均未该类的名字，一个Project或者Module下的
            $: 节点均未列表
        """
        self.linked_to = None

    """
        @: add_parent
        >:(subClassOfBaseObject) parent : 该节点链接到的对象
        $: *该类不直接提供给外部使用，仅在add_child中使用，add_child为对外提供的接口*
        $:如果重复父亲添加子，子添加父亲，则会导致关系冗余。
    """
    def add_parent(self, parent):
        pass

    """
        @: add_child
        >:(subClassOfBaseObject) child:指向该类的子节点
        $: 提供给functional中的函数使用，用于添加链接
    """
    def add_child(self, child):
        pass

"""
    &: class Scoped
    $: 定义域对象，提供给*Lazy*对象继承
"""
class Scoped(object):
    __hash__ = object.__hash__
    """
        @:init
        $:构造器
    """
    def __init__(self, priority):
        """
            Var: (int) priority
            $: 在域栈中的优先级，根据该数值的大小进行入栈出栈操作
        """
        self.priority = priority

    """
        @: __eq__
        $: 注意！定义了\_\_eq__的将不再是hashable的对象了，如果想要实现hashable需要继承父类的__hash__对象
    """
    def __eq__(self, other):
        return self.priority == other.priority
    """
        @: __gt__
        $:
    """
    def __gt__(self, other):
        return self.priority > other.priority
    """
        @: __lt__
        $:
    """
    def __lt__(self, other):
        return self.priority < other.priority
    """
        @: __le__
        $:
    """
    def __le__(self, other):
        return self.priority <= other.priority
    """
        @: __ge__
        $:
    """
    def __ge__(self, other):
        return self.priority >= other.priority

"""
    &:class ScopedObject
    $: 在对一个源码文档进行扫描搜索时，随着扫描的进行，指针会不时地进入和退出一个
    $:特点的区域，例如在处理一个类方法时，指针在一个类的域中；处理一个模块时，指针
    $:处在一个项目域中。ScopedObject对这种行为进行了抽象，在解析文档时，有且仅有一个
    $:全域，即ScopedObject自身。当开始扫描文档时，该类自举，将self压入栈内，
    $:当扫描完退出文档时，该域对象弹出域栈。在扫描期间，每进入一个域，则入栈该域对象；
    $:退出该域时，弹出域栈，直到遇到第一个优先级更大的域对象时，停止弹栈。此时栈顶就为
    $:当前域。从广义上将每个文档对象都应当有自己的域，但是在源码文档中，有”域“这个概念的
    $:就仅有Project/Module/Class三个文档节点对象，因此每当进入这三者其一时，域对象需要
    $:表现为一个文档节点对象的代理，通过该代理进行操作，实现了解耦，使得无需再修改functional的代码。它
    $:分别继承BaseObject和Scoped类
"""
class ScopedObject(BasedObject, Scoped):
    """
        @: init
        >:(const str) name: 由于每个文档解析程序仅有一个全域，因此ScopedObject应当为单例模式
        $:
    """
    def __init__(self, name="scope"):
        BasedObject.__init__(self, name)
        Scoped.__init__(self, 4)
        """
            Var: (subClassOf[Scoped]) _proxy
            $: 域对象的代理
        """
        self._proxy = self  # 自举
        """
            Var: (list[stack]) _stack
            $:域栈
        """
        self._stack = [self._proxy]

    """
        @: __del__
        $:析构函数，由于再构造时会将self压入栈内，而且其优先级最高，所以再程序中无法
        $:弹出栈底元素(self)，所以再析构时，应该将其弹出，这样对该域对象(self)的引用计数
        $:就会安全的降为0，否则可能在内存中一直保存(不过肯能在_stack析构之后，该对象的引用计数也会安全降为0)
    """
    def __del__(self):
        self._stack.pop()  # 移除自举时

    """
        @: change_scope
        >: (subClassOf[Scoped]) obj:要切换到的域对象
        $: 当要切换域对象时，函数将要比对当前域（栈顶元素）与将要切换到的域对象的优先级
        $: 当遇到域优先级更大的域对象时，需要弹出栈顶元素直到遇到比obj域范围更大的对象为止
        $: 然后将其压栈；否则直接压栈，表示进入了更小的域范围
    """
    def change_scope(self, obj):
        if self.top() > obj:
            self._stack.append(obj)
        elif self.top() <= obj:
            while 1:
                self._stack.pop()
                if self.top() > obj:
                    break
            self._stack.append(obj)
    """
        @: get_background
        $: 当在同优先级域对象之间切换时，如果不进行退栈处理，那么诸如
        $: `self.scope.add_child(obj) - self.scope.proxy(obj)`着用的用法就会出错，由于代理对象未修改
        $: 而往一个代理对象上添加一个相同优先级的对象显然是不对的（如当前代理对象和obj均为ClassObject，那么在第一句中
        $: add_child()就会抛出一个ValueError错误。因此，在同优先级的域对象之间相互切换应该找到背景域（当前代理对象的父节点）
    """
    def get_background(self, bigger):
        if bigger == self._stack[0]:
            self._stack = [self._stack[0]]
            self._proxy = self.top()
            return
        while self.top() <= bigger:
            self._stack.pop()
            self._proxy = self.top()
            if self.top() == self._stack[0]:
                return


    """
        @: top
        $:返回栈顶元素
    """
    def top(self):
        return self._stack[-1]

    """
        @: proxy
        >:(subClassOf[Scoped]) proxy: 设置域代理对象
        $:提供给外部的接口用于设置域代理对象
    """
    def proxy(self, _p):
        if isinstance(_p, Scoped):
            self.change_scope(_p)
            self._proxy = self.top()

    """
        @: add_child
        >: (subClassOf[BaseObject]) child :
        $: *act-like-a-BaseObject*，实现对文档节点对象的代理功能
    """
    def add_child(self, child):
        try:
            self._proxy.add_child(child)
        except exceptions.Exce.LinkTypeException:
            if self.top() <= child:
                self.get_background(child)
                self._proxy.add_child(child)
                self.proxy(child)
            else:
                raise exceptions.Exce.LinkTypeException(child, self._proxy)

    """
       @: add_parent
       >: (subClassOf[BaseObject]) parent :
       $: *act-like-a-BaseObject*，实现对文档节点对象的代理功能
    """
    def add_parent(self, parent):
        self._proxy.add_parent(parent)

"""
    &: class ReferencedObject
    $: 引用模块类
"""
class ReferencedObject(BasedObject):
    """
        @:init
        >:(str) name: the name of obejct
        $:
    """
    def __init__(self, name):
        super().__init__(name)
        """
            var: (list[str]) linked_to
            $: 父文档节点
        """
        self.linked_to = []
        """
            var: (list[str]) refs
            $:该文档所有引用到的模块名
        """
        self.refs = []

    """
        @:add_parent
        >:(subClassOf[ModuleObject]) parent:ReferencedObject只能连接到模块
        $:
    """
    def add_parent(self, parent):
        if not isinstance(parent, ModuleObject):
            raise exceptions.Exce.LinkTypeException(self, parent)
        self.linked_to.append(parent)
    """
        @:add_child
        $:引用节点暂时无子节点
    """
    def add_child(self, child):
        raise exceptions.Exce.LinkTypeException(child, self)


"""
    &: class ProjectObject
    $: 项目文档节点类，是一个Scoped
"""
class ProjectObject(BasedObject, Scoped):
    def __init__(self, name):
        object.__init__(self)
        BasedObject.__init__(self, name)
        Scoped.__init__(self, 3)
        """
            var:(list[ModuleObject|HaveRefsModuleObject]) modules
            $: ProjectObject所有子节点
        """
        self.modules = []

    """
        @:add_parent
        $:目前项目节点为根节点，再无父节点
    """
    def add_parent(self, parent):
        raise exceptions.Exce.LinkTypeException(self, parent)

    """
        @:add_child
        >:(ModuleObject|HaveRefsModuleObject) child: 该ProjectObject的所有子节点
        $: 添加子节点，应该均为模块
    """
    def add_child(self, child):
        if not isinstance(child, (ModuleObject, HaveRefsModuleObject)):
            raise exceptions.Exce.LinkTypeException(child, self)

        child.add_parent(self)
        self.modules.append(child)

"""
    &: class ModuleObject
    $: 模块文档节点对象， 是一个Scoped
"""
class ModuleObject(BasedObject, Scoped):
    """
    @: init
    $:
    """
    def __init__(self, name):
        object.__init__(self)
        BasedObject.__init__(self, name)
        Scoped.__init__(self, 2)
        """
            var: (list[ClassObject]) classes
            $: 保存该模块下所有类文档节点对象
        """
        self.classes = []
        """
            var: (list[VariableObject]) variables
            $: 保存该模块下所有变量文档节点对象
        """
        self.variables = []
        """
            var: (list[FunctionObject]) functions
            $: 保存该模块下所有函数文档节点对象，包括类方法
        """
        self.functions = []
        """
            var: (list[Object]) linked_to
            $: 所有父节点，是一个列表，也即一个类可以链接到多个模块
        """
        self.linked_to = []

    """
        @: add_parent
        >: (BasedObject) parent:；链接到的父节点
        $:
    """
    def add_parent(self, parent: BasedObject):
        if not isinstance(parent, ProjectObject):
            raise exceptions.Exce.LinkTypeException(self, parent)
        self.linked_to.append(parent)
    """
        @: add_child
        >: (ClassObject|ModuleVariableObject|ModuleFunctionObject) child:子节点
        $:
    """
    def add_child(self, child: BasedObject):
        if not isinstance(child, (ClassObject, ModuleVariableObject, ModuleFunctionObject, ReferencedObject)):
            raise exceptions.Exce.LinkTypeException(child, self)
        child.add_parent(self)  # auto link to parent while adding child
        if isinstance(child, ClassObject):
            self.classes.append(child)
        elif isinstance(child, ModuleVariableObject):
            self.variables.append(child)
        elif isinstance(child, ModuleFunctionObject):
            self.functions.append(child)

"""
    &: class HaveRefsModuleObject
    $: 有引用的模块的文档对象，这是一个包装类
"""
class HaveRefsModuleObject(ModuleObject):
    """
        @:init
        $:
    """
    def __init__(self, name):
        super().__init__(name)
        """
            var: (list) references
            $:所有引用
        """
        self.references = []

    """
        @: add_child
        >:(ReferencedObject) child: 
        $:
    """
    def add_child(self, child: ReferencedObject):
        if isinstance(child, ReferencedObject):
            self.references.append(child)
        super().add_child(child)


"""
    &: class ClassObject
    $:类文档节点对象
"""
class ClassObject(BasedObject, Scoped):
    def __init__(self, name):
        object.__init__(self)
        BasedObject.__init__(self, name)
        Scoped.__init__(self, 1)
        """
            Var:(list[ClassMethodObject]) methods
            $:保存该类下所有方法
        """
        self.methods = []
        """
            Var:(list[MemberVariableObject]) variables
            $:保存该类下所有成员变量
        """
        self.variables = []
        """
            Var: (list[tuple]) bases
            $:保存该类的所有父类
        """
        self.bases = []
        """
            Var:(list) linked_to
            $:所有父节点，为列表，也即一类可以定义再多个模块下
        """
        self.linked_to = []
    """
        @:add_parent
        >:(ModuleObject) parent: 
        $:
    """

    def add_parent(self, parent: ModuleObject):
        if not isinstance(parent, ModuleObject):
            raise exceptions.Exce.LinkTypeException(self, parent)
        self.linked_to.append(parent)
        #  parent.add_child(self) !
        #  !!important this is illegal, because when adding a relations, the parent will add
        # this child automatically by calling parent.add_child() in your code and doing this by yourself!
    """
        @:add_child
        >:(MemberVariableObject|ClassMethodObject) child: 
        $:
    """
    def add_child(self, child: BasedObject):

        if not isinstance(child, (MemberVariableObject, ClassMethodObject)):
            raise exceptions.Exce.LinkTypeException(child, self)

        child.add_parent(self)
        if isinstance(child, MemberVariableObject):
            self.variables.append(child)
        elif isinstance(child, ClassMethodObject):
            self.methods.append(child)

"""
    &: class VariableObject
    $: 变量节点对象，抽象基类
"""
class VariableObject(BasedObject):
    __module__ = abc.ABCMeta
    """
        @:init
        $:
    """
    def __init__(self, name):
        super().__init__(name)
        """
            Var:(str[AnyType]) type
            $:变量类型
        """
        self.type = None

    """
        @:add_child
        $:变量对象无子节点
    """
    def add_child(self, child):
        raise exceptions.Exce.LinkTypeException(child, self)

"""
    &: class MemberVariableObject
    $: 成员变量文档节点对象，特化VariableObject
"""
class MemberVariableObject(VariableObject):
    """
        @:init
        $:
    """
    def __init__(self, name: str):
        super().__init__(name)
        """
            Var: (ClassObject) linked_to
            $:为单个类对象
        """
        self.linked_to = None  # must be a class object

    """
        @:add_parent
        >:(ClassObject) parent :
        $:
    """
    def add_parent(self, parent: ClassObject):
        if not isinstance(parent, ClassObject):
            raise exceptions.Exce.LinkTypeException(self, parent)
        self.linked_to = parent
        # parent.variables.append(self)
        #  !!important this is illegal, because when adding a relations, the parent will add
        # this child automatically by calling parent.add_child() in your code and doing this by yourself!

"""
    &: class ModuleVariableObject
    $: 模块变量文档节点对象，变量对象的特化
"""
class ModuleVariableObject(VariableObject):
    """
        @:init
        $:
    """
    def __init__(self, name: str):
        super().__init__(name)
        """
            Var: (list[ModuleObject]) linked_to
            $:为列表，也即一个模块变量可以定义在多个模块中
        """
        self.linked_to = []  # a variable defined in a module may be used in other module
    """
        @:add_parent
        >:(ModuleObject) parent :
        $:
    """
    def add_parent(self, parent: ModuleObject):
        if not isinstance(parent, ModuleObject):
            raise exceptions.Exce.LinkTypeException(self, parent)

        self.linked_to.append(parent)
        # parent.variables.append(self)
        #  !!important this is illegal, because when adding a relations, the parent will add
        # this child automatically by calling parent.add_child() in your code and doing this by yourself!

"""
    &: class FunctionObject
    $: 函数文档节点对象，抽象基类
"""
class FunctionObject(BasedObject):
    __module__ = abc.ABCMeta
    """
        @:init
        $:
    """
    def __init__(self, name):
        super().__init__(name)
        """
            Var: (list[tuple]) in_param
            $:输入参数列表，每个元素为一个元组；元组的第一个为参数类型，第二个为参数名，第三个为表里的描述信息
        """
        self.in_param = []
        """
            Var: (str[AnyType]) out_type
            $:函数的返回值类型
        """
        self.out_type = ""
        """
            Var: (list[str]) exceptions
            $: 函数可能抛出的异常
        """
        self.exceptions = []
    """
        @:add_child
        $:函数对象无子节点
    """
    def add_child(self, child):
        raise exceptions.Exce.LinkTypeException(child, self)

"""
    &: class ModuleFunctionObject
    $: 模块函数文档节点对象，FunctionObject的特化
"""
class ModuleFunctionObject(FunctionObject):
    """
        @:init
        $:
    """
    def __init__(self, name):
        super().__init__(name)
        """
            Var: (list[ModuleObject]) linked_to
            $:为列表，也即一个模块函数可以定义在多个模块中
        """
        self.linked_to = []

    """
        @:add_parent
        >:(ModuleObject) parent :
        $:
    """
    def add_parent(self, parent: ModuleObject):
        if not isinstance(parent, ModuleObject):
            raise exceptions.Exce.LinkTypeException(self, parent)

        self.linked_to.append(parent)
        # parent.add_child(self)
        #  !!important this is illegal, because when adding a relations, the parent will add
        # this child automatically by calling parent.add_child() in your code and doing this by yourself!

"""
    &: class ClassMethodObject
    $: 类方法文档节点对象，FunctionObject的特化
"""
class ClassMethodObject(FunctionObject):
    """
        @:init
        $:
    """
    def __init__(self, name):
        super().__init__(name)
        """
            Var: (str) linked_to
            $:为单个类节点对象
        """
        self.linked_to = None
    """
        @:add_parent
        >:(ClassObject) parent :
        $:
    """
    def add_parent(self, parent: ClassObject):
        if not isinstance(parent, ClassObject):
            raise exceptions.Exce.LinkTypeException(self, parent)

        self.linked_to = parent
        # parent.add_child(self)
        #  !!important this is illegal, because when adding a relations, the parent will add
        # this child automatically by calling parent.add_child() in your code and doing this by yourself!
