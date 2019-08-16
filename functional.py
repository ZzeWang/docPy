from threading import Lock
from comments.commentGenerator import *
from codeObject import ScopedObject
from exceptions.Exce import LinkTypeException
logging.basicConfig(level=logging.INFO, format='%(asctime)s - AbstractParser - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
"""
    #:threading.Lock,comments.commentGenerator,ScopedObject
    LK:functional
"""

"""
    !: functional
    $: 模块的主要任务用来解决依赖关系实现对文档节点的链接，其次将链接好的文档节点
    $: 转换为指定的格式（如.md/.html等）。
"""

"""
    &: class AbstractSignalFunctional
    $: 实现链接。把在解析文档的时候产生的注释对象节点按照其指定的链接规则链接起来，链接有两个
    $: 第一种是M类链接，它表示为将该节点链接到类节点对象，因此只能够将函数和变量定义给该链接类型
    $: 第二中是LK类链接，它表示将该节点链接到模块或者项目对象节点，因此可以定义给任意节点类型定义该链接
    $: 当然这是链接的内部实现，在使用时可以不用显式的定义LK或者M，但是当该节点对象需要链接到多个
    $: 父节点时，需要显示地标出LK。函数lazy_link()实现了隐式链接
"""


class AbstractSignalFunctional(object):
    __module__ = abc.ABCMeta

    """
        @: init
        $: 构造器 
    """

    def __init__(self):
        """
            Var: (dict[str:BaseObject]) _unresolved_relations
            $: 存放未解决的关系
        """
        self._unresolved_relations = {}

        """
            Var: (dict[str:BaseObject]) _obj_set
            $: 存放文档的所有文档节点对象
        """
        self._obj_set = {}

        """
            Var: (ScopedObject) scope
            $: 每个项目项目仅有一个scope，随着注释的解析，每进入一个Scoped对象
            $: scope就会将其进行代理，并将其压入scope的对象栈。具体参看codeObject/Scoped对象
            $:的实现
        """
        self.scope = ScopedObject("scope")

    def __break_down(self, sp: str) -> tuple:
        return sp[:sp.find(":")].strip().upper(), [i.strip() for i in sp[sp.find(":") + 1:].split(",")]

    def __find_parent_to_add_tgt(self, tgt, parent, header):
        try:
            if len(self._obj_set[parent]) == 1:
                try:
                    self._obj_set[parent][0].add_child(tgt)

                    logging.info(
                        "{} link '{}' (type='{}') -> '{}' (type={})".
                            format(header, tgt.name, tgt.__class__.__name__,
                                   self._obj_set[parent][0].name,
                                   self._obj_set[parent][0].__class__.__name__))
                    # TODO
                except LinkTypeException as e:
                    logging.fatal(e)
                    exit(0)
            else:
                for sub in self._obj_set[parent]:
                    try:
                        sub.add_child(tgt)
                        logging.info(
                            "link '{}' (type='{}') -> '{}' (type={})".
                                format(tgt.name, tgt.__class__.__name__,
                                       sub.name,
                                       sub.__class__.__name__))
                        break
                    except LinkTypeException as e:
                        logging.fatal(e)
                        exit(0)
        except KeyError:
            raise KeyError

    def __add_obj(self, name, obj):
        try:
            self._obj_set[name].append(obj)
        except KeyError:
            self._obj_set[name] = [obj]

    """
        @:  links
        >: (subClassOfBaseObject) tgt: 需要链接的对象
        >: (list[str]) parents: tgt需要链接到的域对象列表
        $: link()的具体实现，在当前已经解析的所有文档对象_obj_set中依次查找
        $: 每个parent，如果找到则将tgt链接到_obj_set[parent]，否则将tgt加入的
        $: _unresolved_relations中。
    """

    def __link(self, tgt, parents):
        if isinstance(tgt, ProjectObject):
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

    """
        @: link2
        $: 在解析完一个源码文件后对所有未解决的关系进行再一次链接
        $: 如果没有发现待解决的关系，将会报错
    """

    def link2(self):
        for tgt in self._unresolved_relations.keys():
            for parent in self._unresolved_relations[tgt]:
                try:
                    self.__find_parent_to_add_tgt(tgt, parent, "resolve")
                except KeyError:
                    logging.error(
                        "unresolved relations happened!  {}' -> '{}' . '{}' not find!".format(tgt.name, parent, parent))

    """
        @: link
        >:(CommentBlock) bobj
        <:(BaseObject)
        $: 从注释块对象bobj中获取一个BaseObject对象，并链接。是对\_\_link()的包装
    """

    def link(self, bobj: CommentBlock):
        assert issubclass(bobj.__class__, CommentBlock)

        obj = bobj.getObject()
        logging.info("create new obj '{}' (type='{}')".format(obj.name, obj.__class__.__name__))
        self.__add_obj(obj.name, obj)
        _, links = self.__break_down(bobj.link)

        self.__link(obj, links)
        return obj

    """
        @: lazy_link
        >: (subClassOfCommentBlock) bobj : 文档注释对象
        $: 对link()的包装。需要强调的一点是，由于scope对象在构造时使用自己自举
        $: 因此在解析文档时，如果不定义Pj/Module或者Class，而直接定义函数或者变量
        $: 那么会在解析第一个文档注释的时候进入第一个判断块，而此时scope的当前域为其自身（一个ScopedObject对象）
        $: 必然会引起错误。因此，在编写代码时，必须有项目有模块，结构逻辑清晰
    """

    def lazy_link(self, bobj: LazyCommentBlock):
        assert issubclass(bobj.__class__, CommentBlock)
        if bobj.link_type == "S" and isinstance(bobj, LazyCommentBlock):
            if not isinstance(self.scope.top(), ScopedObject):
                obj = bobj.lazy_getObject(self.scope.top())
                self.__add_obj(obj.name, obj)
                self.scope.add_child(obj)
                self.scope.proxy(obj)
                logger.info(
                    "create new obj '{}<-{}' (type={})".format(self.scope.top().name, obj.name, obj.__class__.__name__))
            else:
                print("You Haven't Defined Any Project/Module/Class!")
                raise TypeError
        else:
            linked_obj = self.link(bobj)
            self.scope.proxy(linked_obj)

    """
        @: dump
        >: (str) info : 需要保存的信息
        >: (path) path: 保存地点
        $: 该方法放在这里意义不明确，待改进
    """

    def dump(self, info, path):
        pass

    """
        @: report
        $: 对所有产生的文档对象和链接进行报道，子类通过重写该方法实现
        $: 转换到指定文档格式的任务
    """

    @abc.abstractmethod
    def report(self, path):
        if path is None:
            raise FileNotFoundError
        pass


"""
    &: class SynSignalFunctional
    $: 提供写保护，但似乎没啥卵用
"""


class SynSignalFunctional(AbstractSignalFunctional):
    __module__ = abc.ABCMeta

    def __init__(self):
        super().__init__()
        """
            Var:(threading.Lock) file_lock
            $:提供对文件的互斥访问锁
        """
        self.file_lock = Lock()

    """
        @: dump
        >: (str) info:要输出到文件的信息
        >:(str) path: 输出路径
        $:
     """

    def dump(self, info, path):
        self.file_lock.acquire()
        with open(path, "a") as f:
            f.write(info)
        self.file_lock.release()


"""
    &: class ReportSignalFunctional
    $: 提供print风格的简单解析结果的报表格式类
"""


class ReportSignalFunctional(SynSignalFunctional):
    def __init__(self):
        super().__init__()
        self.mods = [mod[0] for mod in self._obj_set.values() if isinstance(mod[0], ModuleObject)]
        self.queue = []

    def report(self, path="", prefix=""):
        obj = self.queue[-1]
        self.queue.pop()
        print(obj.name)
        if isinstance(obj, ProjectObject):
            self.queue.extend(obj.modules)
        elif isinstance(obj, ModuleObject):
            self.queue.extend(obj.variables)
            self.queue.extend(obj.functions)
            self.queue.extend(obj.classes)
        elif isinstance(obj, ClassObject):
            self.queue.extend(obj.variables)
            self.queue.extend(obj.methods)
        if len(self.queue) == 0:
            return
        else:
            self.report("", prefix)


"""
    &: class ToMarkdownSignalFunctional
    $: 转换到markdown格式
    LK:functional
"""


class ToMarkdownSignalFunctional(SynSignalFunctional):

    @classmethod
    def H1(cls, *args):
        return "# {} {}\n".format(args[0], args[1])

    @classmethod
    def H2(cls, *args):
        return "## {} {}\n".format(args[0], args[1])

    @classmethod
    def H3(cls, *args):
        return "### {} {}\n".format(args[0], args[1])

    @classmethod
    def Bar(cls):
        return "---\n"

    @classmethod
    def Desc(cls, info):
        return "{}\n\n".format(info)

    def __init__(self):
        super().__init__()
        self.chunk = ""
        self.mods = []

    def report(self, path):
        super().report(path)
        pj = [i[0] for i in self._obj_set.values() if isinstance(i[0], ProjectObject)][0]
        self.dump("Project *{}*\n\n{}\n\n---\n\n".format(pj.name, pj.desc), path)
        self.mods = [mod[0] for mod in self._obj_set.values() if isinstance(mod[0], ModuleObject)]

        for mod in self.mods:
            block = ""
            mod_block = self.__class__.H1("Module", mod.name) + self.__class__.Desc(mod.desc) + self.__class__.Bar()
            block += mod_block
            for ref in mod.references:
                ref_block = self.__class__.H2("", ref.name)
                for parent in ref.linked_to:
                    if parent is mod:
                        ref_block += ",".join(ref.refs)
                block += ref_block + "\n\n"
            for cls in mod.classes:
                cls_block = self.__class__.H2("Class", cls.name) + self.__class__.Desc(cls.desc) + self.__class__.Bar()

                for base in cls.bases:
                    cls_block += "*derived from* **{} {}**\n\n".format(base[1], base[0])

                block += cls_block
                for parent in cls.linked_to:
                    if parent is mod:
                        for var in cls.variables:
                            var_block = "### {}  (*type*={})\n\n{}\n\n".format(var.name, var.type, var.desc)
                            block += var_block
                        for mth in cls.methods:
                            func_block = "### {}()\n\n".format(mth.name)
                            for inp in mth.in_param:
                                func_block += "**{}** (*type=*{})\n\n> {}\n\n".format(inp[1], inp[0], inp[2])

                            for exc in mth.exceptions:
                                func_block += "**throw**  {}\n\n> {}\n\n".format(exc[0], exc[1])

                            if mth.out_type != "":
                                func_block += "**return**  {}\n\n".format(mth.out_type)
                            func_block += mth.desc + "\n\n"
                            block += func_block
            for var in mod.variables:
                if isinstance(var, ModuleVariableObject):
                    for parent in var.linked_to:
                        if parent is mod:
                            var_block = "### {}  (*type*={})\n\n{}\n\n".format(var.name, var.type, var.desc)
                            block += var_block
            for func in mod.functions:
                if isinstance(func, ModuleFunctionObject):
                    for parent in func.linked_to:
                        if parent is mod:
                            func_block = "### {}()\n".format(func.name)
                            for inp in func.in_param:
                                func_block += "**{}** (*type=*{})\n\n> {}\n\n".format(inp[1], inp[0], inp[2])
                                block += func_block

                            for exc in func.exceptions:
                                func_block += "**throw**  {}\n\n> {}\n\n".format(exc[0], exc[1])
                            block += "**return**  {}\n\n".format(mth.out_type)
                            block += func.desc + "\n\n"

            self.dump(block, path)
