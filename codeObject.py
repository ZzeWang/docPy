import abc, logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - Factory - %(levelname)s - %(message)s')
logger = logging.getLogger("BasedObject")

"""
    !: DocObject
"""
class BasedObject(object):
    __module__ = abc.ABCMeta

    def __init__(self, name):
        self.name = name
        self.desc = ""
        self.linked_to = None

    def add_parent(self, parent):
        pass

    def travel(self):
        return None

    def add_child(self, child):
        """
        !! IMPORTANT
        child node must point to parent while adding a child node of this
        :param child:
        :return:
        """
        pass


class Scoped(object):
    __hash__ = object.__hash__

    def __init__(self, priority):
        self.priority = priority


    def __eq__(self, other):
        return self.priority == other.priority

    def __gt__(self, other):
        return self.priority > other.priority

    def __lt__(self, other):
        return self.priority < other.priority

    def __le__(self, other):
        return self.priority <= other.priority

    def __ge__(self, other):
        return self.priority >= other.priority


class ScopedObject(BasedObject, Scoped):
    def __init__(self, name="scope"):
        BasedObject.__init__(self, name)
        Scoped.__init__(self, 4)
        self.is_proxy = False
        self._proxy = self  # 自举
        self._stack = [self._proxy]

    def __del__(self):
        self._stack.pop()  # 移除自举时

    def change_scope(self, obj):
        if self._proxy > obj:
            self._stack.append(obj)
        elif self._proxy < obj or self._proxy == obj:
            while 1:
                self._stack.pop()
                if self.top() > obj:
                    break
            self._stack.append(obj)

    def top(self):
        return self._stack[-1]

    def proxy(self, _p):
        if isinstance(_p, Scoped):
            self.change_scope(_p)
            self._proxy = self.top()

    def add_child(self, child):
        self._proxy.add_child(child)

    def add_parent(self, parent):
        self._proxy.add_parent(parent)


class ReferencedObject(BasedObject):
    def __init__(self, name):
        super().__init__(name)
        self.linked_to = []
        self.refs = []

    def add_parent(self, parent):
        assert isinstance(parent, ModuleObject)
        self.linked_to.append(parent)

    def add_child(self, child):
        logging.debug("referenced object have no child")
        return


class ProjectObject(BasedObject, Scoped):
    def __init__(self, name):
        object.__init__(self)
        BasedObject.__init__(self, name)
        Scoped.__init__(self, 3)
        self.modules = []

    def add_parent(self, parent):
        pass

    def add_child(self, child):
        try:
            isinstance(child, (ModuleObject, HaveRefsModuleObject))
        except ValueError:
            return
        child.add_parent(self)
        if isinstance(child, (ModuleObject, HaveRefsModuleObject)):
            self.modules.append(child)


class ModuleObject(BasedObject, Scoped):
    def __init__(self, name):
        object.__init__(self)
        BasedObject.__init__(self, name)
        Scoped.__init__(self, 2)
        self.classes = []
        self.variables = []
        self.functions = []
        self.linked_to = []

    def travel(self):
        for cls in self.classes:
            cls.travel()

        for var in self.variables:
            yield var

        for func in self.functions:
            yield func

    def add_parent(self, parent: BasedObject):
        assert isinstance(parent, ProjectObject)
        self.linked_to.append(parent)

    def add_child(self, child: BasedObject):
        try:
            isinstance(child, (ClassObject, ModuleVariableObject, ModuleFunctionObject))
        except ValueError:
            return
        child.add_parent(self)  # auto link to parent while adding child
        if isinstance(child, ClassObject):
            self.classes.append(child)
        elif isinstance(child, ModuleVariableObject):
            self.variables.append(child)
        elif isinstance(child, ModuleFunctionObject):
            self.functions.append(child)


class HaveRefsModuleObject(ModuleObject):
    def __init__(self, name):
        super().__init__(name)
        self.references = []

    def add_child(self, child: BasedObject):
        try:
            isinstance(child, ReferencedObject)
        except ValueError:
            return
        super().add_child(child)
        if isinstance(child, ReferencedObject):
            self.references.append(child)


class ClassObject(BasedObject, Scoped):
    def __init__(self, name):
        object.__init__(self)
        BasedObject.__init__(self, name)
        Scoped.__init__(self, 1)
        self.methods = []
        self.variables = []
        self.linked_to = []

    def travel(self):
        for md in self.methods:
            yield md

        for var in self.variables:
            yield var

    def add_parent(self, parent: ModuleObject):
        assert isinstance(parent, ModuleObject)
        self.linked_to.append(parent)
        #  parent.add_child(self) !
        #  !!important this is illegal, because when adding a relations, the parent will add
        # this child automatically by calling parent.add_child() in your code and doing this by yourself!

    def add_child(self, child: BasedObject):

        try:
            isinstance(child, (MemberVariableObject, ClassMethodObject))
        except ValueError:
            return

        child.add_parent(self)
        if isinstance(child, MemberVariableObject):
            self.variables.append(child)
        elif isinstance(child, ClassMethodObject):
            self.methods.append(child)


class VariableObject(BasedObject):
    __module__ = abc.ABCMeta

    def __init__(self, name):
        super().__init__(name)
        self.type = None

    def add_child(self, child):
        logging.error("variable object have no child!")
        raise TypeError


class MemberVariableObject(VariableObject):
    def __init__(self, name: str):
        super().__init__(name)
        self.linked_to = None  # must be a class object

    def add_parent(self, parent: ClassObject):
        try:
            assert isinstance(parent, ClassObject)
        except ValueError:
            return
        self.linked_to = parent
        # parent.variables.append(self)
        #  !!important this is illegal, because when adding a relations, the parent will add
        # this child automatically by calling parent.add_child() in your code and doing this by yourself!


class ModuleVariableObject(VariableObject):
    def __init__(self, name: str):
        super().__init__(name)
        self.linked_to = []  # a variable defined in a module may be used in other module

    def add_parent(self, parent: ModuleObject):
        try:
            assert isinstance(parent, ModuleObject)
        except ValueError:
            return
        self.linked_to.append(parent)
        # parent.variables.append(self)
        #  !!important this is illegal, because when adding a relations, the parent will add
        # this child automatically by calling parent.add_child() in your code and doing this by yourself!


class FunctionObject(BasedObject):
    __module__ = abc.ABCMeta

    def __init__(self, name):
        super().__init__(name)
        self.in_param = []
        self.out_type = ""

    def add_child(self, child):
        logging.error("function object have no child!")
        raise TypeError


class ModuleFunctionObject(FunctionObject):
    def __init__(self, name):
        super().__init__(name)
        self.linked_to = []

    def add_parent(self, parent: ModuleObject):
        try:
            assert isinstance(parent, ModuleObject)
        except ValueError:
            return
        self.linked_to.append(parent)
        # parent.add_child(self)
        #  !!important this is illegal, because when adding a relations, the parent will add
        # this child automatically by calling parent.add_child() in your code and doing this by yourself!


class ClassMethodObject(FunctionObject):
    def __init__(self, name):
        super().__init__(name)
        self.linked_to = None

    def add_parent(self, parent: ClassObject):
        try:
            assert isinstance(parent, ClassObject)
        except ValueError:
            return
        self.linked_to = parent
        # parent.add_child(self)
        #  !!important this is illegal, because when adding a relations, the parent will add
        # this child automatically by calling parent.add_child() in your code and doing this by yourself!
