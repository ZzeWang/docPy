import sys, getopt
from parserx.batchDirParser import CppBatchDirParser, PythonBatchDirParser, HtmlBatchDirParser
from parserx.docParser import CppParser, PyParser, HtmlParser
from functional import ToMarkdownSignalFunctional
"""
    !: userInf
    $: 用户命令行接口
"""
def main(argv):
    arg = "i:o:x:t:"
    lg = ["input-file=", "output-file=", "parse-mode=", "type="]
    try:
        opts, args = getopt.getopt(sys.argv[1:], arg, lg)
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        sys.exit(2)

    input_file = None
    output_file = None
    type = None
    parse_mode = None

    for o, a in opts:
        if o in ("-i", "--input-file"):
            input_file = a.replace("\\", "\\\\")
        elif o in ("-o", "--output-file"):
            output_file =  a.replace("\\", "\\\\")
        elif o in ("-x", "--parse-mode"):
            parse_mode = a.upper()
        elif o in ("-t", "--type"):
            type = a.upper()
        else:
            assert False, "unhandled option"

    if type in ("CPP","C++","C"):
        if parse_mode in ("BATCH", "SINGLE"):
            cpp = None
            if parse_mode.upper() == "BATCH":
                cpp = CppBatchDirParser(path=input_file, mapper=ToMarkdownSignalFunctional())
            elif parse_mode == "SINGLE":
                cpp = CppParser(path=input_file, mapper=ToMarkdownSignalFunctional())
            else:
                print("not support")
            cpp.run()
            cpp._mapper.report(output_file)
            print("Done!")

    if type  in ("PY", "PYTHON"):
        if parse_mode in ("BATCH", "SINGLE"):
            pyp = None
            if parse_mode == "BATCH":
                pyp = PythonBatchDirParser(path=input_file, mapper=ToMarkdownSignalFunctional())
            elif parse_mode == "SINGLE":
                pyp = PyParser(path=input_file, mapper=ToMarkdownSignalFunctional())
            pyp.run()
            pyp._mapper.report(output_file)
            print("Done!")

    if type in ("HTML", "H"):
        if parse_mode in ("BATCH", "SINGLE"):
            html = None
            if parse_mode == "BATCH":
                html = HtmlBatchDirParser(path=input_file, mapper=ToMarkdownSignalFunctional())
            elif parse_mode == "SINGLE":
                html = HtmlParser(path=input_file, mapper=ToMarkdownSignalFunctional())
            html.run()
            html._mapper.report(output_file)
            print("Done!")


if __name__ == "__main__":
    main(sys.argv)
