import re
import logging
import abc

logging.basicConfig(level=logging.INFO, format='%(asctime)s - Factory - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


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
            "link": re.compile("((?:(?:[ToOt]+)|(?:[LKk]+)|(?:[Mm]))): *(.*?) *\n")
        }

    def _findall(self, key, do):
        try:
            result = re.findall(self.pattern[key], self.chunk)
            result[0]
            for sing in result:
                do(self, sing)
        except IndexError:
            logging.error("do not find {} in comment".format(key))
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
            logging.error("do not find input params!")
            raise IndexError


class ClassBlock(CommentBlock):
    ClassSignal = r"&"

    def __init__(self, comment):
        super().__init__(comment)
        self.pattern.update(
            {"name": re.compile("&: *class *(.*?) *\n")}
        )

    def pipeline(self):
        super().pipeline()
        self._parse_name()


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
        self._parse_name()
        self.__parse_ins()
        self.__parse_out()


class ModuleBlock(CommentBlock):
    def __init__(self, comment):
        super().__init__(comment)
        self.pattern.update(
            {
                "name": re.compile("!: *(.*?) *\n")
            }
        )

    def pipeline(self):
        self._parse_name()
        self._parse_desc()
