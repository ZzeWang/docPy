"""
    #:rReportSignalFunctional, AbstractSignalFunctional,BlockFactory,multipleLoader,SingleLoader
    LK: Parser
"""

from loader.SingleLoader import *
from loader.multipleLoader import *
from functional import ReportSignalFunctional, AbstractSignalFunctional
from comments.commentGenerator import BlockFactory
import time

from queue import Queue
from threading import Thread
logging.basicConfig(level=logging.INFO, format='%(asctime)s - AbstractParser - %(levelname)s - %(message)s')
logger = logging.getLogger("BADiffCommentParser")

"""
    &: class AbstractParser
    $: 定义解析从指定文件中读取出来的块的行为，是一个抽象基类
    $: 目前出现的问题在于是否得把对文件注释块的解析工作交给FileLoader，因为在定义了CommentBlock之后
    $: 原本AbstractParser的解析工作突然全部抽象出来并移交给CommentBlock的pipeline函数和getObject函数
    LK: Parser
"""

class AbstractParser:
    __module__ = abc.ABCMeta

    """
        @: __init__
        >: (str) after: 注释后符号
        >: (str) before: 注释前符号
        >: (str) path: 需要加载的文档，批处理类为目录
        >: (AbstractSignalFunctional) mapper: 默认使用ReportSignalFunctional,指定符号与CommentBlock的映射关系。该类使用工厂模式产生CommentBlock对象
        >: (FileLoader) loader: 文件加载器，默认使用SingleFileLoader，批处理类使用MultipleFileLoader
        <:(void)
        $: 构造函数，必须的参数为after和before
        M: AbstractParser
    """

    def __init__(self, *args, **kwargs):
        """
            Var: (str) _before
            $: 注释开始符
            M: AbstractParser
        """
        self._before = r""
        """
            Var: (str) _after
            $: 注释结束符
            M: AbstractParser
        """
        self._after = r""

        if kwargs and kwargs["after"] and kwargs["before"]:
            self._after = kwargs["after"]
            self._before = kwargs["before"]
        else:
            self._after = ""
            self._before = ""

        try:
            if isinstance(kwargs["mapper"], AbstractSignalFunctional):
                self._mapper = kwargs["mapper"]
        except KeyError:
            self._mapper = ReportSignalFunctional()

        try:
            if isinstance(kwargs["loader"], FileLoader):
                self.file = kwargs["loader"]
        except KeyError:
            self.file = SingleFileLoader()

        if kwargs and kwargs["path"]:
            self.file.set_attr_by_path(kwargs["path"])
            self.file.load()
        else:
            logging.fatal("no file input")
            raise Exception

        """
            Var: (Queue) _comment_list
            $: 将解析注释内容和处理链接的任务异步，提高效率
            M:AbstractParser
        """
        self._comment_list = Queue(maxsize=100)
        """
            var: (re.compile) _comment_pattern
            $: 从文档流中提取注释块
            M:AbstractParser
        """
        self._comment_pattern = re.compile("{}(.*?){}".format(self._before, self._after), re.DOTALL)

        """
            Var: (iter) iter_of_comment
            $: _comment_pattern的迭代器
             M:AbstractParser
        """
        # self.iter_of_comment = iter(self._comment_list)

    """
        @: pre_symmetric_check
        >: (str) page_content: 注释内容
        <: (bool)
        $: 对偶性检查，对_comment_list的每一块注释进行注释符号对偶检查
        $: 如果对称，那么返回True，parse_comment()函数将不再会检查下一条注释块的结束注释符号
        $: 否则返回False，parse_comment()函数就会进一步在下下面若干条注释块中查找结束注释符号
        $: 如果SingleFileLoader的limitation设置的足够大，足以容纳下文档中的最大注释块的大小，那么
        $: 只要编译器通过，则注释符号一定对称
        M:AbstractParser
    """

    @abc.abstractmethod
    def pre_symmetric_check(self, page_content):
        return False

    """
        @: _safe_suffix
        >:(SingleFileLoader) who: 指定需要检查行结束安全性的对象
        >:(str) after: 注释结束符
        <:(void)
        $: 当在_comment_list中的一个注释块结束时，由于FileLoader会分页，因此有可能块与块之间
        $: 隔断了一个完整的注释符号，因此要确保在每一页的最后有一个完整的注释符。函数总是检查结束符号，
        $: 这是由于在parse_comment中，函数不论注释符是否对称，都会用正则匹配一次，因此，经过正则匹配，
        $: 在该注释块中，总是第一个出现注释起始符。如果出现截断，那么函数会将下一块被截断的注释结束符
        $: 复制到上一块中，并删除掉下一行被截断的结束符
        M:AbstractParser
    """

    def _safe_suffix(self, who, after):
        page = 0
        while page + 1 != len(who.pages):
            max_len_suffix = len(after)
            P1, P2 = False, False  # guess
            while max_len_suffix != 0:
                suffix = who.pages[page][-max_len_suffix:]
                if after[:max_len_suffix] == suffix:
                    P1 = True
                    break
                max_len_suffix -= 1

            if not P1:
                page += 1
                continue
            next_page = page + 1
            min_len_suffix = len(after) - max_len_suffix

            if who.pages[next_page][:min_len_suffix] == after[-min_len_suffix:]:
                P2 = True

            if P1 and P2:
                who.pages[page] += who.pages[next_page][:min_len_suffix]
                who.pages[next_page] = who.pages[next_page][min_len_suffix:]
            page += 1

    """
        @: parse_comments
        >: (FileLoader) who: 指定需要解析的对象
        <:(void)
        $: 将分页的注释块根据注释开始和结束符组合成一个完整的注释段，该函数在批处理类中重写
        M:AbstractParser
    """

    def parse_comments(self, who):
        page_c = 0
        if not isinstance(self, GCommentParser):
            self._safe_suffix(who, self._after.replace("\\", ""))
        while page_c < len(who.pages):
            not_page = self.pre_symmetric_check(who.pages[page_c])
            # TODO
            items = re.findall(self._comment_pattern, who.pages[page_c])
            for item in items:
                self._comment_list.put(item)
            # self._comment_list.extend(re.findall(self._comment_pattern, who.pages[page_c]))

            start = who.pages[page_c].rfind(self._before.replace("\\", ""))
            if start == -1:
                page_c += 1
                continue
            org_line = page_c
            if not not_page:
                while True:
                    end = who.pages[page_c + 1].find(self._after.replace("\\", ""))
                    page_c += 1
                    if end != -1 or page_c + 1 == len(who.pages) :
                        break
                base = who.pages[org_line][start + len(self._before.replace("\\", "")):]
                org_line += 1
                while org_line < page_c:
                    base += who.pages[org_line]
                    org_line += 1

                self._comment_list.put(base + who.pages[page_c][:end])
                #self._comment_list.append(base + who.pages[page_c][:end])
                who.pages[page_c] = who.pages[page_c][end+len(self._after.replace("\\", "")):]
            else:
                page_c += 1

            if page_c + 1 == len(who.pages):
                items = re.findall(self._comment_pattern, who.pages[page_c])
                for item in items:
                    self._comment_list.put(item)
                break
        #
        # for idx, item in enumerate(self._comment_list):
        #     self._comment_list[idx] = self._comment_list[idx].strip()

    """
        @: parse_comment
        >: (void) v:
        <:(void)
        $: 将分页的注释块根据注释开始和结束符组合成一个完整的注释段，parse_comments的一个包装器
        M:AbstractParser
    """

    def parse_comment(self):
        self.parse_comments(self.file)

    """
        @: __prefix_standard
        >: (str) comment: 注释块
        <: (str) 
        $: 从注释块comment中提取在CommentBlock的工程类中已定义的块前缀，如类&/函数@等
        M:AbstractParser
    """

    def __prefix_standard(self, comment: str) -> str:
        return comment[:comment.find(":")]

    """
        @: resolve_unlinked
        >:(void) v:
        <:(void)
        $:解决所有在处理单个文件时没出解决的链接，如果在处理完所有目标文件时
        $:没有发现需要链接的对象，则会报错
        M:AbstractParser
    """

    def resolve_unlinked(self):
        self._mapper.link2()

    """
        @:switch
        >:(void) v:
        <:(void)
        $: 从所有注释块中取出每个注释块，获取其前缀以从CommentBlock生成已定义的Block对象。
        $: 在生成指定的注释对象后，块对象会解析该注释块并产生一个Object.之后，函数将会第一次
        $: 尝试解决该Object的链接性，如果暂时没有解析则会等到处理完所有comment之后再次尝试
        $: 解决
        M:AbstractParser
    """

    def switch(self):

        factory = BlockFactory()
        while True:
            if self._comment_list.empty():
                break
            comment = self._comment_list.get().strip()
            comment += "\n"
            obj = factory.create_bobj_by_signal(self.__prefix_standard(comment), comment)
            if obj:
                obj.pipeline()

                self._mapper.lazy_link(obj)



    """
        @: run
        >:(void) v:
        <:(void)
        $: 用户接口，在使用类时，直接使用该函数即可产生所有对象
        M:AbstractParser
    """

    def  run(self):
        parse_comment = Thread(target=self.parse_comment)
        switch = Thread(target=self.switch)

        now = time.time()
        parse_comment.start()
        switch.start()
        parse_comment.join()
        switch.join()
        print("time consuming: ", (time.time()-now)*1000, "ms")
        self.resolve_unlinked()

"""
    &: class BADiffCommentParser
    $: 注释结束符和开始符不同的文档类型（如cpp,html)处理器
    $: 由于前后符号不同，处理方法相对简单，速读更快
    LK: Parser
"""


class BADiffCommentParser(AbstractParser):
    """
        @:init
        >:(tuple) args: 位置参数
        >:(dict) kwargs: 关键字参数
        <:(void)
        $: 构造器，其必须参数同AbstractParser
        M: BADiffCommentParser
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    """
        @: __gleft__
        >: (str) ps: 注释内容 
        <: (list)
        $: 找到一个注释块的所有注释开始符位置
        M:BADiffCommentParser
    """

    def __gleft__(self, ps):
        idx, l = -1, []
        while True:
            idx = ps.find(self._before.replace("\\", ""), idx + 1)
            if idx == -1:
                break
            l.append(idx)
        return l

    """
        @: __gright__
        >: (str) ps: 注释内容 
        <: (list)
        $: 找到一个注释块的所有注释结束符位置
        M:BADiffCommentParser
    """

    def __gright__(self, ps):
        idx, r = -1, []
        while True:
            idx = ps.find(self._after.replace("\\", ""), idx + 1)
            if idx == -1:
                break
            r.append(idx)
        return r

    """
        @:pre_symmetric_check
        >: (str) page_content: 同AbstractParser
        <: (void)
        $: 对偶检查的具体实现，该函数冗余，应当定义在AbstractParser中 
        M:BADiffCommentParser
    """

    def pre_symmetric_check(self, page_content):
        lc, rc = self.__gleft__(page_content), self.__gright__(page_content)
        if len(lc) != len(rc):
            return False
        for left, right in zip(lc, rc):
            if left > right:
                return False

        return True


"""
    &: class GCommentParser
    $: 通用注释解析器，不论注释结束和开始符是否相同都可以使用该类进行解析.
    $: 如果开始和结束符相同，则在类构造时会给开始符和结束符添加区分符，实现隐型替换
    $: 如果不同，则表现为BADiffCommentParser
    LK: Parser
"""


class GCommentParser(BADiffCommentParser):
    """
        @: init
        >:(tuple) args: 位置参数
        >:(dict) kwargs: 关键字参数
        <:(void)
        $:构造器，必须参数同AbstractParser
        M:GCommentParser
    """

    def __init__(self, *args, **kwargs):

        if kwargs["after"] == kwargs["before"]:
            """
                Var:(str)  _org_ab
                $: 未添加区分符的原始注释开始结束符
                M:GCommentParser
            """
            self._org_ab = kwargs["after"]
            kwargs["before"] += "<"
            kwargs["after"] = ">" + kwargs["after"]
            super().__init__(*args, **kwargs)
            if isinstance(self.file, SingleFileLoader):
                self._safe_suffix(self.file, self._org_ab.replace("\\", ""))
                self.__differ(self.file)
            elif isinstance(self.file, MultipleFileLoader):
                for sing in self.file._loaded_file:
                    self._safe_suffix(sing, self._org_ab.replace("\\", ""))
                    self.__differ(sing)
        else:
            super().__init__(*args, **kwargs)

    """
        @: __differ
        >:(SingleFileLoader) who: 为了能够尽量通用化__differ函数，指定who为一个单文件加载
        <:(void)
        $: 对所有以确保安全的注释块添加区分符
        M:GCommentParser
    """

    def __differ(self, who):
        flag = 0
        sig = self._org_ab.replace("\\", "")
        for page_idx, _ in enumerate(who.pages):
            idx = -3
            while True:
                idx = who.pages[page_idx].find(sig, idx + 3)
                if idx == -1:
                    break
                if flag == 0:
                    who.pages[page_idx] = who.pages[page_idx][:idx + len(sig)] \
                                          + "<" + \
                                          who.pages[page_idx][idx + len(sig):]
                    flag = 1
                else:
                    who.pages[page_idx] = who.pages[page_idx][:idx] \
                                          + ">" + \
                                          who.pages[page_idx][idx:]
                    flag = 0
