
"""
    !: PyTest
    $: The unittest module can be used from the command line to run tests from modules, classes or even individual test methods:
"""

"""
    @: GloFuncOfPyTest
    >: (str) string: input a string of params
    >: (int) idx: this index of all
    <: (bool)
    $:The setUp() and tearDown() methods allow you to define instructions that will be executed before and after each test method. They are covered in more detail in the section Organizing test code.
    LK: PyTest
"""
def GloFuncOfPyTest(string:str, idx:int):
    pass

"""
    @: LocalFuncOfPyText
    >: (str) string: input a string of params
    <: (bool)
    $:The setUp() and tearDown() methods allow you to define instructions that will be executed before and after each test method. They are covered in more detail in the section Organizing test code.
    LK: PyTest
"""
def LocalFuncOfPyText(string):
    pass

"""
    Var: (GIL::Lock) Lock
    $: The final block shows a simple way to run the tests. unittest.main() provides a command-line interface to the test script. When run from the command line, the above script produces an output that looks like this:
    LK: PyTest
"""
Lock = None

"""
    &: class Pypp
    $: This allows you to use the shell filename completion to specify the test module. The file specified must still be importable as a module. The path is converted to a module name by removing the ‘.py’ and converting path separators into ‘.’. If you want to execute a test file that isn’t importable as a module you should execute the file directly instead.
    Lk: PyTest
"""
class Pypp:

    """
        @: init
        >:(void) v:
        <:(void)
        $: The script Tools/unittestgui/unittestgui.py in the Python source distribution is a GUI tool for test discovery and execution. This is intended largely for ease of use for those new to unit testing. For production environments it is recommended that tests be driven by a continuous integration system such as Buildbot, Jenkins or Hudson.
        M: Pypp
    """
    def __init__(self):
        """
        Var: (Pypp) this
        $: The unittest module provides a rich set of tools for constructing and running tests. This section demonstrates that a small subset of the tools suffice to meet the needs of most users.
        M: Pypp
        """
        self.this = None

    """
        @: foo
        >:(int) i1: id
        >:(str) l2: name
        <:(bool)
        $: A testcase is created by subclassing unittest.TestCase. The three individual tests are defined with methods whose names start with the letters test. This naming convention informs the test runner about which methods represent tests.
        M: Pypp
    """
    def foo(self):
        pass