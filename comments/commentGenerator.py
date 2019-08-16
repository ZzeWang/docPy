import re
import logging
import abc
from exceptions.Exce import *

"""
    #: re, logging, abc, codeObject, exceptions.Exce
    LK: comments
"""
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("CommentBlock")
from codeObject import *

"""
    !: comments
    $: 对文档注释的抽象，定义不同注释类型所对应的类别/定义不同类别
    $: 的注释的提取规则(正则）。如果需要添加新的注释类别，并且该类有除了name和desc以外的
    $: 其它属性字段，那么需要在新的类里对pattern字典进行更新，添加提取规则(re.compile)。
    $: 目前，ProjectObject是一个文档对象的根节点。更广泛的推广，根节点类型只能有一个。
    $: 每个ModuleObject必须从属于一个ProjectObject/一个ClassObject必须从属于一个ModuleObject
    $: 进而类推。这样可以建立起文档关系链接树。因此根节点类型不能处理链接（因为它没有父节点），从而
    $: 必须其pipeline必须不能处理_parse_link()。链接的创建定义在functional模块中，文档节点对象定义在codeObject模块中.
    $: 模块采用工厂模式，通过BlockFactory类向用户提供接口
    LK: docPy
"""

"""
    &: class CommentBlock
    $: 抽象基类，所有注释块对象均继承自CommentBlock
    $: 子类中需要实现pipeline()函数, getObject()函数和_parse_name()函数
    LK: comments
"""


class CommentBlock:
    __module__ = abc.ABCMeta

    """
        @: init
        >: (str) comment : 注释内容
        <:(void)
        $: 构造器
        M:CommentBlock
    """

    def __init__(self, comment):
        """
            Var: (str) chunk
            $: 保存注释内容
            M:CommentBlock
        """
        self.chunk = comment

        """
            Var: (str) name
            $: 从注释内容中解析出注释名
            M:CommentBlock
        """
        self.name = ""
        """
            Var: (ste) desc
            $: 注释内容的描述部分，用于解释说明该对象的用途
            M:CommentBlock
        """
        self.desc = ""
        """
            Var: (str) link_type
            $: 链接的类型，目前只定义了两类链接，一类是LK类型，指该对象链接到模块(ModuleObject)或这项目(ProjectObject)
            $: 第二类是M类型，指该对象链接到类(ClassObject)
            M:CommentBlock
        """
        self.link_type = ""
        """
            Var: (str) link
            $: 从注释内容中提取的链接到对象字符串，对该字符串的链接解析工作则有functional定义
            M: CommentBlock
        """
        self.link = ""

        """
            Var: (dict[str:re.compile]) pattern
            $: 提取规则，在子类中通过update方法拓展
            M: CommentBlock
        """
        self.pattern = {
            "desc": re.compile("\$:(.*?)\n"),
            "link": re.compile("((?:(?:LK|Lk|lk)|(?:[Mm]))): *(.*?) *\n")
        }

    """
        @: _findall
        >: (str) key : 需要提取对象的提取规则，必须在pattern中，否则引发KeyError
        >: (callable) do : 定义提取动作，一般是赋值或者列表拓展动作
        <: (void)
        $: 对re.findall的封装，根据提取规则key从chunk中提取目标内容，如果没有找到任何内容
        $: 会引发SyntaxException错误
        M: CommentBlock
    """

    def _findall(self, key, do):
        if self.pattern[key] is None:
            raise KeyError

        result = re.findall(self.pattern[key], self.chunk)
        if len(result) == 0:
            raise SyntaxException(self.pattern[key].pattern, self.chunk, self)
        # TODO syntax check!! if the reason why length == 0 is cased by a error syntax, there should throw a SyntaxError,
        # TODO rather than just letting it go!

        for sing in result:
            do(self, sing)

    """
        @: _parse_desc
        >:(void) :
        <:(void)
        $: 因为desc的格式在每个注释块中的格式统一，因此该函数不可重写，除非重新定义一种desc格式
        M: CommentBlock
    """

    def _parse_desc(self):
        def __(self, sing):
            self.desc += sing

        self._findall("desc", __)

    """
        @: _parse_name
        >:(void) :
        <:(void)
        $: 由于子类的name格式不统一，因此子类必须在pattern中重新定义自己name的提取规则，
        $: 但提取name的行为一致，所以该类也不用在子类中重写
        M: CommentBlock
    """

    def _parse_name(self):
        def __(self, sing):
            self.name = sing

        self._findall("name", __)

    """
        @: pipeline
        >:(void) :
        <:(void)
        $: 对所有需要从注释块中提取的字段进行批处理，由于每个子类的字段不同，在子类中必须重写该函数
        M: CommentBlock
    """

    @abc.abstractmethod
    def pipeline(self):
        try:
            self._parse_desc()
        except SyntaxException as e:
            logging.fatal(e)  # 交给Lazy的pipeline处理
            print(e)
            exit(0)

        try:
            self._parse_link()
        except SyntaxException as e:
            raise e
    """
        @: _parse_link
        >:(void) :
        <:(void)
        $: 解析链接类型和链接到字符串
        M: CommentBlock
    """

    def _parse_link(self):
        if self.pattern["link"] is None:
            raise KeyError("need 'Lk' keyword")

        result = re.findall(self.pattern["link"], self.chunk)

        try:
            self.link_type = result[0][0]  # trigger IndexError
            self.link = self.link_type + ":"
            for idx, lk in enumerate(result):
                if idx == 0:
                    self.link += lk[1]
                else:
                    self.link += "," + lk[1]
        except IndexError:
            raise SyntaxException(self.pattern["link"].pattern, self.chunk, self)

    """
        @: getObject
        >:(void) :
        <:(subclassOfCommentBlock)
        $: 从已提取的字段中生成对应的文档节点对象
        M: CommentBlock
    """

    @abc.abstractmethod
    def getObject(self):
        return None


class LazyCommentBlock(CommentBlock):
    __module__ = abc.ABCMeta

    def __init__(self, comment):
        super().__init__(comment)
        self.necessary_field = ["name", "desc"]

    def _parse_link(self):
        try:
            result = re.findall(self.pattern["link"], self.chunk)
            self.link_type = result[0][0]  # trigger IndexError
            self.link = self.link_type + ":"
            for idx, lk in enumerate(result):
                if idx == 0:
                    self.link += lk[1]
                else:
                    self.link += "," + lk[1]
        except IndexError:
            tmp = re.compile("((?:(?:LK|Lk|lk)|(?:[Mm]))):.*?")  # TODO 宽松匹配条件
            if len(re.findall(tmp, self.chunk)) == 0:
                self.link_type = "S"
            else:
                raise SyntaxException(self.pattern["link"].pattern, self.chunk, self)

    def _findall(self, key, do):

        if self.pattern[key] is None:
            raise KeyError

        result = re.findall(self.pattern[key], self.chunk)

        if len(result) == 0:

            if key in self.necessary_field:
                raise IntegratedException(key, self)
            else:
                # TODO syntax check!
                logging.warning("You passes a keyword field '{}', if the process of parsing fail, please check "
                                "the information: name='{}' (type={})".format(key, self.name, self.__class__.__name__))
                pass

        for sing in result:
            do(self, sing)

    def pipeline(self):
        try:
            super()._parse_desc()
            self._parse_link()
        except IntegratedException as e:
            logging.fatal(e)
            print(e)
            exit(0)
        except SyntaxException as e:
            logging.fatal(e)
            print(e)
            exit(0)

    @abc.abstractmethod
    def lazy_getObject(self, proxy):
        pass


"""
    &: class ClassBlock
    $: 定义如何从注释中提取一个类的所有信息
    LK: comments
"""


class ClassBlock(CommentBlock):
    """
        @: init
        >: (str) comment : 待提取注释
        $:构造器
        M:ClassBlock
    """

    def __init__(self, comment):
        super().__init__(comment)
        self.pattern.update(
            {"name": re.compile("&: *class *(.*?) *\n")}
        )

    """
        @: pipeline
        >:(void) :
        <:(void)
        $:仅处理类名的提取
        M:ClassBlock
    """

    def pipeline(self):
        try:
            super().pipeline()
            self._parse_name()
        except KeyError as e:
            logging.fatal(e)
            print(e)
            exit(0)
        except SyntaxException as e:
            logging.fatal(e)
            print(e)
            exit(0)

    """
        @: getObject
        >:(void) :
        <:(ClassObject)
        $: 从注释中提取一个ClassObject对象
        M: ClassBlock
    """

    def getObject(self):
        cls = ClassObject(self.name)
        cls.desc = self.desc
        return cls


class LazyClassBlock(ClassBlock, LazyCommentBlock):
    def __init__(self, comment):
        super().__init__(comment)

    def lazy_getObject(self, proxy):
        return self.getObject()

    def pipeline(self):
        try:
            self._parse_name()
            LazyCommentBlock.pipeline(self)
        except IntegratedException as e:
            logging.fatal(e)
            print(e)
            exit(0)


"""
    &: class FunctionBlock
    $: 定义如何从注释中提取一个函数的所有信息
    LK: comments
"""


class FunctionBlock(CommentBlock):
    """
        @: init
        >: (str) comment : 待提取注释
        $:构造器
        M:FunctionBlock
    """

    def __init__(self, comment):
        super().__init__(comment)
        """
            Var: (tuple[type, name, desc]) ins
            $: 函数的输入参数，为一个元组，元组第一个元素为参数类型，第二元素为参数名，第三个元素为参数的描述
            M:FunctionBlock
        """
        self.ins = []
        """
            Var: (str[AnyType]) out
            $: 函数的返回值，可以为任意类型，用一个str表示返回值的类型
            M:FunctionBlock
        """
        self.out = ""
        self.pattern.update({
            "name": re.compile("@: *([a-zA-Z_0-9]+) *\n"),
            "ins": re.compile(">: *\( *(?P<type>[a-zA-Z_0-9:]+) *\) *(?P<name>[a-zA-Z_0-9]+) *: *(?P<desc>.*?) *\n"),
            "out": re.compile("<: *\( *(?P<type>[a-zA-Z_0-9:]+) *\) *\n"),
        })

    """
        @: _parse_name
        >:(void) :
        <:(void)
        $:
        M:FunctionBlock
    """

    def _parse_name(self):
        def __(self, sing):
            self.name = sing

        self._findall("name", __)

    """
        @: __parse_ins
        >:(void) :
        <:(void)
        $:
        M:FunctionBlock
    """

    def __parse_ins(self):
        def __(self, sing):
            self.ins.append(sing)

        self._findall("ins", __)

    """
        @: __parse_out
        >:(void) :
        <:(void)
        $:
        M:FunctionBlock
    """

    def __parse_out(self):
        def __(self, sing):
            self.out = sing

        self._findall("out", __)

    """
        @: pipeline
        >:(void) :
        <:(void)
        $:
        M:FunctionBlock
    """

    def pipeline(self):
        super().pipeline()
        try:
            self._parse_name()
            self.__parse_ins()
            self.__parse_out()
        except SyntaxException as e:
            logging.fatal(e)
            print(e)
            exit(0)

    """
        @: getObject
        >:(void) :
        <:(void)
        $:由于一个函数可以是一个模块内定义的模块级函数，也可以是一个类中定义的方法
        $:所以根据链接类型的不同，返回不同的FunctionObject.当链接到模块时，返回一个
        $: ModuleFunctionObject；如果链接到类，则返回一个ClassMethodObject，二者同
        $:继承自FunctionObject
        M:FunctionBlock
    """

    def getObject(self):
        if self.link_type == "LK":
            func = ModuleFunctionObject(self.name)
        else:
            func = ClassMethodObject(self.name)
        func.desc = self.desc
        func.out_type = self.out
        for input_param in self.ins:
            func.in_param.append(input_param)
        return func


class LazyFunctionBlock(FunctionBlock, LazyCommentBlock):
    def __init__(self, comment):
        super().__init__(comment)
        self.necessary_field.append("desc")

    def lazy_getObject(self, proxy):
        assert isinstance(proxy, (ClassObject, ModuleObject))
        if isinstance(proxy, ClassObject):
            self.link_type = "M"
        elif isinstance(proxy, ModuleObject):
            self.link_type = "LK"
        return self.getObject()

    def pipeline(self):
        try:
            self._parse_name()
            LazyCommentBlock.pipeline(self)
        except IntegratedException as e:
            logging.fatal(e)
            print(e)
            exit(0)


"""
    &: class ModuleBlock
    $: 定义如何从注释中提取一个模块类的所有信息
    LK: comments
"""


class ModuleBlock(CommentBlock):
    """
        @: init
        >: (str) comment : 待提取注释
        $:构造器
        M:ModuleBlock
    """

    def __init__(self, comment):
        super().__init__(comment)
        self.pattern.update(
            {
                "name": re.compile("!: *(.*?) *\n")
            }
        )

    """
        @: pipeline
        >:(void) :
        <:(void)
        $: 仅提取模块名
        M:ModuleBlock
    """

    def pipeline(self):
        super().pipeline()
        try:
            self._parse_name()
        except IndexError as e:
            print(e)

    """
        @: getObject
        >:(void) :
        <:(HaveRefsModuleObject)
        $:返回一个HaveRefsModuleObject对象
        M:ModuleBlock
    """

    def getObject(self):
        mod = HaveRefsModuleObject(self.name)
        mod.desc = self.desc
        return mod


class LazyModuleBlock(ModuleBlock, LazyCommentBlock):
    def __init__(self, comment):
        super().__init__(comment)

    def lazy_getObject(self, proxy):
        return self.getObject()

    def pipeline(self):
        try:
            self._parse_name()
            LazyCommentBlock.pipeline(self)
        except IntegratedException as e:
            logging.fatal(e)
            print(e)
            exit(0)
"""
    &: class VariableBlock
    $: 定义如何从注释中提取一个变量类的所有信息
    LK: comments
"""


class VariableBlock(CommentBlock):
    """
        @: init
        >: (str) comment : 待提取注释
        $:构造器
        M:VariableBlock
    """

    def __init__(self, comment):
        super().__init__(comment)
        """
            Var: (str[AnyType]) type
            $: 变量的类型
            M:VariableBlock
        """
        self.type = ""
        self.pattern.update(
            {
                "name": re.compile("[vV]ar: *\(.*?\) +(.+?) *\n"),
                "type": re.compile("[vV]ar: *\((.+?)\).*? *\n")
            }
        )

    """
        @: _parse_type
        >:(void) :
        <:(void)
        $:解析变量类型
        M:VariableBlock
    """

    def _parse_type(self):
        def __(self, sing):
            self.type = sing

        self._findall("type", __)

    """
        @: pipeline
        >:(void) :
        <:(void)
        $:
        M:VariableBlock
    """

    def pipeline(self):
        super().pipeline()
        try:
            self._parse_name()
            self._parse_type()
        except IndexError as e:
            print(e)

    """
        @: getObject
        >:(void) :
        <:(VariableObject[ModuleVariableObject|MemberVariableObject])
        $: 根据链接性不同返回一个VariableObject的子类。当链接到模块时返回一个ModuleVariableObject对象
        $: 当链接到类时，返回一个MemberVariableObject对象
        M:VariableBlock
    """

    def getObject(self):
        if self.link_type == "LK":
            var = ModuleVariableObject(self.name)
        else:
            var = MemberVariableObject(self.name)

        var.desc = self.desc
        var.type = self.type
        return var


class LazyVariableBlock(VariableBlock, LazyCommentBlock):
    def __init__(self, comment):
        super().__init__(comment)
        self.necessary_field.append("type")

    def lazy_getObject(self, proxy):
        assert isinstance(proxy, (ClassObject, ModuleObject))
        if isinstance(proxy, ClassObject):
            self.link_type = "M"
        elif isinstance(proxy, ModuleObject):
            self.link_type = "LK"
        return self.getObject()

    def pipeline(self):
        try:
            self._parse_type()
            self._parse_name()
            LazyCommentBlock.pipeline(self)
        except IntegratedException as e:
            logging.fatal(e)
            print(e)
            exit(0)

"""
    &: class ReferencedBlock
    $: 定义如何从注释中提取一个依赖类的所有信息
    LK: comments
"""


class ReferencedBlock(CommentBlock):
    """
        @: init
        >: (str) comment : 待提取注释
        $:构造器
        M:ReferencedBlock
    """
    Cnt = 0

    def __init__(self, comment):
        super().__init__(comment)
        """
            Var: (list[str]) referenced
            $: 该模块所依赖的所有对象
            M:ReferencedBlock
        """
        self.referenced = []
        self.pattern.update(
            {
                "ref": re.compile("#:(.*?)\n"),
                "name": re.compile("")
            }
        )

    """
        @: _parse_name 
        >: (void) :
        <:(void)
        $: 引用在一个模块中仅有一个，因此name未固定'Ref'
        M:ReferencedBlock
    """

    def _parse_name(self):
        self.name = "Ref"

    """
        @:_parse_desc
        >:(void):
        <:(void)
        $: 引用的desc未固定的'references'
        M:ReferencedBlock
    """

    def _parse_desc(self):
        self.desc = "references :"

    """
        @:_parse_ref
        >:(void):
        <:(void)
        $: 从注释中提取出所有依赖
        M:ReferencedBlock
    """

    def _parse_ref(self):
        def __(self, sing):
            self.referenced.extend(sing.split(","))

        self._findall("ref", __)

    """
        @:pipeline
        >:(void):
        <:(void)
        $: 
        M:ReferencedBlock
    """

    def pipeline(self):
        try:
            self._parse_name()
            self._parse_desc()
            self._parse_ref()
            super()._parse_link()
        except IndexError as e:
            print(e)

    """
        @:getObject
        >:(void):
        <:(ReferencedObject)
        $: 未完成，如何实现单例模式
        M:ReferencedBlock
    """

    def getObject(self):
        if ReferencedBlock.Cnt == 0:
            ref = ReferencedObject(self.name)
            ref.desc = self.desc
            ref.refs = self.referenced
            return ref
        logging.error("reference only has ONE in a module!")


class LazyReferencedBlock(ReferencedBlock, LazyCommentBlock):
    def lazy_getObject(self, proxy):
        return self.getObject()


"""
    &: class ProjectBlock
    $: 定义如何从注释中提取一个项目类的所有信息
    LK: comments
"""


class ProjectBlock(CommentBlock):
    """
        @: init
        >:(void):
        <:(void)
        $:构造器
        M:ProjectBlock
    """

    def __init__(self, comment):
        super().__init__(comment)
        self.pattern.update(
            {
                "name": re.compile("(?:(?:PJ)|(?:Pj)|(?:pj)) *: *(.*?)\n")
            }
        )

    """
        @: pipeline
        >:(void) :
        <:(void)
        $:
        M:ProjectBlock
    """

    def pipeline(self):
        try:
            self._parse_name()
            self._parse_desc()
        except IndexError as e:
            print(e)

    """
        @:getObject
        >:(void):
        <:(ProjectObject)
        $: 根据提取出的信息返回一个ProjectObject对象
        M:ProjectBlock
    """

    def getObject(self):
        pj = ProjectObject(self.name)
        pj.desc = self.desc
        return pj


class LazyProjectBlock(ProjectBlock, LazyCommentBlock):
    def __init__(self, comment):
        super().__init__(comment)

    def lazy_getObject(self, proxy):
        return self.getObject()


"""
    &: class BlockFactory
    $: 一个工厂模式，提供用户接口，
    $: 例如在代码中 `factory = BlockFactory(); factory.create_bobj_by_name('name')`
    $: 该类产生的对象将会被用在functional中实现链接
    LK: comments
"""


class BlockFactory:

    def __init__(self):
        self.name_map = {
            "ClassBlock": LazyClassBlock,
            "FunctionBlock": LazyFunctionBlock,
            "ModuleBlock": LazyModuleBlock,
            "VariableBlock": LazyVariableBlock,
            "ReferencedBlock": LazyReferencedBlock,
            "ProjectBlock": ProjectBlock,
        }
        self.signal_map = {
            "@": LazyFunctionBlock,
            "&": LazyClassBlock,
            "!": LazyModuleBlock,
            "VAR": LazyVariableBlock,
            "#": LazyReferencedBlock,
            "PJ": ProjectBlock,
        }
        self.logger = logging.getLogger("BlockFactory")

    def create_boby_by_name(self, obj_type: str, comment: str):
        try:
            return self.name_map[obj_type](comment)
        except KeyError:
            self.logger.debug("no block object named '{}'".format(obj_type))
            return None

    def create_bobj_by_signal(self, signal: str, comment: str):
        try:
            return self.signal_map[signal.upper()](comment)
        except KeyError:
            self.logger.debug("no signal '{}'".format(signal))
            return None
