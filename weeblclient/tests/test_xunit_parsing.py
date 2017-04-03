import testtools
import os
from weeblclient.weebl import utils


ASSETS_PATH = os.path.join(os.path.dirname(__file__), 'assets')
XUNIT_PATH = os.path.join(ASSETS_PATH, 'tempest_xunit.xml')


class XunitParsingTests(testtools.TestCase):
    def test_get_test_data(self):
        test_data = list(utils.get_next_test_data(XUNIT_PATH))
        self.assertEqual(len(test_data), 85)
        found_setup = False
        found_teardown = False
        for test in test_data:
            self.assertIn('testcase_name', test)
            self.assertIn('testcaseclass_name', test)
            self.assertIn('testcaseinstancestatus', test)
            self.assertNotEqual(test['testcaseclass_name'], '')
            if not found_setup:
                found_setup = test['testcase_name'] == 'setUpClass'
            if not found_teardown:
                found_teardown = test['testcase_name'] == 'tearDownClass'
        self.assertTrue(found_setup)
        self.assertTrue(found_teardown)
