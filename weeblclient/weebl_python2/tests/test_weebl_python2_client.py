import testtools
from weeblclient.weebl_python2.weebl import utils


class WeeblClientTests(testtools.TestCase):
    pass


class WeeblClientUtilsTests(testtools.TestCase):
    def test_build_dict_of_linked_items(self):
        target_file_globs = [
            {'glob_pattern': 'juju_status.yaml',
             'jobtypes': ['/api/v1/jobtype/pipeline_deploy/'],
             'resource_uri': '/api/v1/targetfileglob/juju_status.yaml/'},
            {'glob_pattern': 'console.txt',
             'jobtypes': ['/api/v1/jobtype/pipeline_deploy/'],
             'resource_uri': '/api/v1/targetfileglob/console.txt/'},
            {'glob_pattern': 'tempest_xunit.xml',
             'jobtypes': ['/api/v1/jobtype/test_tempest_smoke/'],
             'resource_uri': '/api/v1/targetfileglob/tempest_xunit.xml/'}]
        known_bug_regexes = [
            {'bug': '/api/v1/bug/bug1/',
             'regex': 're_1',
             'resource_uri': '/api/v1/knownbugregex/kbr1/',
             'targetfileglobs': ['/api/v1/targetfileglob/juju_status.yaml/'],
             'uuid': 'kbr1'},
            {'bug': '/api/v1/bug/bug2/',
             'regex': 're_2',
             'resource_uri': '/api/v1/knownbugregex/kbr2/',
             'targetfileglobs': ['/api/v1/targetfileglob/console.txt/'],
             'uuid': 'kbr2'}, ]
        bugs = [
            {'bugtrackerbug': {'bug_number': 1,
                               'resource_uri': '/api/v1/bugtrackerbug/lpbug1/',
                               'uuid': 'lpbug1'},
             'knownbugregex': ['/api/v1/knownbugregex/kbr1/'],
             'resource_uri': '/api/v1/bug/bug1/',
             'uuid': 'bug1'},
            {'bugtrackerbug': {'bug_number': 2,
                               'resource_uri': '/api/v1/bugtrackerbug/lpbug2/',
                               'uuid': 'lpbug2'},
             'knownbugregex': ['/api/v1/knownbugregex/kbr2/'],
             'resource_uri': '/api/v1/bug/bug2/',
             'uuid': 'bug2'}, ]

        regex_dict, tfile_list = utils.build_dict_of_linked_items(
            target_file_globs, known_bug_regexes, bugs)

        ideal_regex_dict = {
            're_1': [('juju_status.yaml', 'pipeline_deploy', 1)],
            're_2': [('console.txt', 'pipeline_deploy', 2)]}
        ideal_tfile_list = ['juju_status.yaml',
                            'console.txt',
                            'tempest_xunit.xml']
        self.assertEqual(ideal_regex_dict, regex_dict)
        self.assertEqual(ideal_tfile_list, tfile_list)

    def test_build_bug_info_dict(self):
        regex_dict = {'re_1': [('tempest_xunit.xml', 'test_tempest_smoke', 1)],
                      're_2': [('console.txt', 'pipeline_deploy', 2),
                               ('juju_status.yaml', 'pipeline_prepare', 2),
                               ('juju_status.yaml', 'pipeline_prepare', 3), ]}
        tfile_list = ['juju_status.yaml', 'console.txt', 'tempest_xunit.xml', ]
        wbugs = [{'bugtrackerbug': {'bug_number': 1}},
                 {'bugtrackerbug': {'bug_number': 2}},
                 {'bugtrackerbug': {'bug_number': 3}}, ]
        output = utils.build_bug_info_dict(regex_dict, tfile_list, wbugs)

        ideal_output = {'bugs': {
            1: {'test_tempest_smoke': [
                {'tempest_xunit.xml': {'regexp': ['re_1']}}]},
            2: {'pipeline_deploy': [
                {'console.txt': {'regexp': ['re_2']}}],
                'pipeline_prepare': [
                {'juju_status.yaml': {'regexp': ['re_2']}}]},
            3: {'pipeline_prepare': [
                {'juju_status.yaml': {'regexp': ['re_2']}}]}
            }}

        self.assertEqual(ideal_output, output)
