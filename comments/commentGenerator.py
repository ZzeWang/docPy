import re
import logging
import abc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from codeObject import *


class CommentBlock:
    __module__ = abc.ABCMeta

    def __init__(self, comment):
        self.chunk = comment
        self.name = ""
        self.desc = ""
        self.link_type = ""
        self.link = ""
        self.pattern = {
            "desc": re.compile("\$:(.*?)\n"),
            "link": re.compile("((?:(?:LK|Lk|lk)|(?:[Mm]))): *(.*?) *\n")
        }
        self.logger = logging.getLogger("CommentBlock")

    def set_comment(self, comment):
        self.chunk = comment

    def _findall(self, key, do):
        try:
            result = re.findall(self.pattern[key], self.chunk)
            result[0]
            for sing in result:
                do(self, sing)
        except IndexError:
            self.logger.error("do not find '{}' in comment".format(key))
            raise IndexError

    def _parse_desc(self):
        def __(self, sing):
            self.desc += sing

        self._findall("desc", __)

    def _parse_name(self):
        def __(self, sing):
            self.name = sing

        self._findall("name", __)

    @abc.abstractmethod
    def pipeline(self):
        self._parse_desc()
        self._parse_link()

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
            self.logger.error("do not find input params!")
            raise IndexError

    @abc.abstractmethod
    def getObject(self):
        return None


class ClassBlock(CommentBlock):
    ClassSignal = r"&"

    def __init__(self, comment):
        super().__init__(comment)
        self.pattern.update(
            {"name": re.compile("&: *class *(.*?) *\n")}
        )

    def pipeline(self):
        super().pipeline()
        try:
            self._parse_name()
        except IndexError as e:
            print(e)

    def getObject(self):
        cls = ClassObject(self.name)
        cls.desc = self.desc
        return cls


class FunctionBlock(CommentBlock):
    FuncSignal = r"@"

    def __init__(self, comment):
        super().__init__(comment)
        self.ins = []
        self.out = ""
        self.pattern.update({
            "name": re.compile("@: *([a-zA-Z_0-9]+) *\n"),
            "ins": re.compile(">: *\( *(?P<type>[a-zA-Z_0-9:]+) *\) *(?P<name>[a-zA-Z_0-9]+) *: *(?P<desc>.*?) *\n"),
            "out": re.compile("<: *\( *(?P<type>[a-zA-Z_0-9:]+) *\) *\n"),
        })

    def _parse_name(self):
        def __(self, sing):
            self.name = sing

        self._findall("name", __)

    def __parse_ins(self):
        def __(self, sing):
            self.ins.append(sing)

        self._findall("ins", __)

    def __parse_out(self):
        def __(self, sing):
            self.out = sing

        self._findall("out", __)

    def _parse_desc(self):
        def __(self, sing):
            self.desc += sing

        self._findall("desc", __)

    def pipeline(self):
        super().pipeline()
        try:
            self._parse_name()
            self.__parse_ins()
            self.__parse_out()
        except IndexError as e:
            print(e)

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


class ModuleBlock(CommentBlock):
    def __init__(self, comment):
        super().__init__(comment)
        self.pattern.update(
            {
                "name": re.compile("!: *(.*?) *\n")
            }
        )

    def pipeline(self):
        try:
            self._parse_name()
            self._parse_desc()
        except IndexError as e:
            print(e)

    def getObject(self):
        mod = ModuleObject(self.name)
        mod.desc = self.desc
        return mod


class VariableBlock(CommentBlock):
    def __init__(self, comment):
        super().__init__(comment)
        self.type = ""
        self.pattern.update(
            {
                "name": re.compile("[vV]ar: *\(.*?\) *(.*?) *\n"),
                "type": re.compile("[vV]ar: *\((.*?)\) .*? *\n")
            }
        )

    def _parse_type(self):
        def __(self, sing):
            self.type = sing

        self._findall("type", __)

    def pipeline(self):
        super().pipeline()
        try:
            self._parse_name()
            self._parse_type()
        except IndexError as e:
            print(e)

    def getObject(self):
        if self.link_type == "LK":
            var = ModuleVariableObject(self.name)
        else:
            var = MemberVariableObject(self.name)

        var.desc = self.desc
        var.type = self.type
        return var


class ReferencedBlock(CommentBlock):
    def __init__(self, comment):
        super().__init__(comment)
        self.referenced = []
        self.pattern.update(
            {
                "ref": re.compile("#:(.*?)\n"),
                "name": re.compile("")
            }
        )

    def _parse_name(self):
        self.name = "Ref"

    def _parse_desc(self):
        self.desc = "references :"

    def _parse_ref(self):
        def __(self, sing):
            self.referenced.extend(sing.split(","))

        self._findall("ref", __)

    def pipeline(self):
        try:
            self._parse_name()
            self._parse_desc()
            self._parse_ref()
            super()._parse_link()
        except IndexError as e:
            print(e)

    def getObject(self):
        ref = ReferencedObject(self.name)
        ref.desc = self.desc
        ref.refs = self.referenced
        return ref


class BlockFactory:

    def __init__(self):
        self.name_map = {
            "ClassBlock": ClassBlock,
            "FunctionBlock": FunctionBlock,
            "ModuleBlock": ModuleBlock,
            "VariableBlock": VariableBlock,
            "ReferencedBlock": ReferencedBlock
        }
        self.signal_map = {
            "@": FunctionBlock,
            "&": ClassBlock,
            "!": ModuleBlock,
            "VAR": VariableBlock,
            "#": ReferencedBlock
        }
        self.logger = logging.getLogger("BlockFactory")

    def create_boby_by_name(self, obj_type: str, comment: str):
        try:
            return self.name_map[obj_type](comment)
        except KeyError:
            self.logger.error("no block object named '{}'".format(obj_type))

    def create_bobj_by_signal(self, signal: str, comment: str):
        try:
            return self.signal_map[signal.upper()](comment)
        except KeyError:
            self.logger.error("no signal '{}'".format(signal))
