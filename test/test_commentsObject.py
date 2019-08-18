import unittest
from comments.commentGenerator import UsageBlock

class BlockTest(unittest.TestCase):

    def test_usage(self):
        s = "Usage:  \nBEGIN \nwangjijsaodjisaoidj jdsoia\nEND\nLK:mod\n"
        uo = UsageBlock(s)
        uo.pipeline()
        x = uo.getObject()

        print("name:",x.name)
        print("Usage:",x.desc)
        print(s)

