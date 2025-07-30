from cubicweb_web.devtools.testlib import AutomaticWebTest
from logilab.common.testlib import unittest_main


class AutomaticWebTest(AutomaticWebTest):
    def to_test_etypes(self):
        return {"Link"}

    def list_startup_views(self):
        return ()


if __name__ == "__main__":
    unittest_main()
