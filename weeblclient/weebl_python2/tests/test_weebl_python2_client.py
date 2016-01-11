import testtools
from weeblclient.weebl_python2.weebl import utils


class WeeblClientTests(testtools.TestCase):
    pass


class WeeblClientUtilsTests(testtools.TestCase):
    def test_build_dict_of_linked_items(self):
        file1 = utils.generate_random_string()
        file2 = utils.generate_random_string()
        unused_file = utils.generate_random_string()
        target_file_globs = [
            {'glob_pattern': file1,
             'jobtypes': ['/api/v1/jobtype/pipeline_deploy/'],
             'resource_uri': '/api/v1/targetfileglob/{}/'.format(file1)},
            {'glob_pattern': file2,
             'jobtypes': ['/api/v1/jobtype/pipeline_deploy/'],
             'resource_uri': '/api/v1/targetfileglob/{}/'.format(file2)},
            {'glob_pattern': unused_file,
             'jobtypes': ['/api/v1/jobtype/test_tempest_smoke/'],
             'resource_uri': '/api/v1/targetfileglob/{}/'.format(unused_file)}]
        known_bug_regexes = [
            {'bug': '/api/v1/bug/bug1/',
             'regex': 're_1',
             'resource_uri': '/api/v1/knownbugregex/kbr1/',
             'targetfileglobs': ['/api/v1/targetfileglob/{}/'.format(file1)],
             'uuid': 'kbr1'},
            {'bug': '/api/v1/bug/bug2/',
             'regex': 're_2',
             'resource_uri': '/api/v1/knownbugregex/kbr2/',
             'targetfileglobs': ['/api/v1/targetfileglob/{}/'.format(file2)],
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
            're_1': [(file1, 'pipeline_deploy', 1, 'kbr1')],
            're_2': [(file2, 'pipeline_deploy', 2, 'kbr2')]}
        ideal_tfile_list = set([file1, file2])
        self.assertEqual(ideal_regex_dict, regex_dict)
        self.assertEqual(ideal_tfile_list, tfile_list)
        self.assertNotIn(unused_file, tfile_list)

    def test_build_bug_info_dict(self):
        regex_dict = {'re_1': [('tempest_xunit.xml', 'test_tempest_smoke', 1,
                                'kbr1')],
                      're_2': [('console.txt', 'pipeline_deploy', 2, 'kbr2'),
                               ('juju_status.yaml', 'pipeline_prepare', 2,
                                'kbr2'),
                               ('juju_status.yaml', 'pipeline_prepare', 3,
                                'kbr2'), ]}
        tfile_list = ['juju_status.yaml', 'console.txt', 'tempest_xunit.xml', ]
        wbugs = [{'bugtrackerbug': {'bug_number': 1}},
                 {'bugtrackerbug': {'bug_number': 2}},
                 {'bugtrackerbug': {'bug_number': 3}}, ]
        output = utils.build_bug_info_dict(regex_dict, tfile_list, wbugs)

        ideal_output = {'bugs': {
            1: {'regex_uuid': 'kbr1',
                'test_tempest_smoke': [
                    {'tempest_xunit.xml': {'regexp': ['re_1']}}]},
            2: {'regex_uuid': 'kbr2',
                'pipeline_deploy': [
                    {'console.txt': {'regexp': ['re_2']}}],
                'pipeline_prepare': [
                    {'juju_status.yaml': {'regexp': ['re_2']}}]},
            3: {'regex_uuid': 'kbr2',
                'pipeline_prepare': [
                    {'juju_status.yaml': {'regexp': ['re_2']}}]}
            }}

        self.assertEqual(ideal_output, output)

    def test_generate_bug_entries_no_generics(self):
        include_generics = False
        job1 = utils.generate_random_string()
        job2 = utils.generate_random_string()
        job3 = utils.generate_random_string()
        regex1 = utils.generate_random_string()
        regex2 = utils.generate_random_string()
        regex3 = utils.generate_random_string()
        bugs_dict = {'bugs': {
            '0001': {
                job1: [{'console.txt': {'regexp': [regex1]}}],
                job2: [{'console.txt': {'regexp': [regex1]}}],
                job3: [{'console.txt': {'regexp': [regex1]}}]},
            '0002': {
                job1: [{'console.txt': {'regexp': [regex2]}}],
                },
            '0003': {
                job2: [{'some.yaml': {'regexp': [regex3]}}],
                },
            '0004': {
                job1: [{'console.txt': {'regexp': [regex1]}}],
                },
            }
        }
        entry_list = utils.generate_bug_entries(bugs_dict, include_generics)
        self.assertEqual(len(entry_list), 6)
        self.assertEqual(len([entry for entry in entry_list if
                         entry.lp_bug_no == '0001']), 3)
        self.assertEqual(len([entry for entry in entry_list if
                         entry.lp_bug_no == '0002']), 1)
        self.assertEqual(len([entry for entry in entry_list if
                         entry.lp_bug_no == '0003']), 1)
        self.assertEqual(len([entry for entry in entry_list if
                         entry.lp_bug_no == '0004']), 1)
        self.assertEqual(set([entry.job for entry in entry_list if
                         entry.lp_bug_no == '0001']), set([job2, job1, job3]))
        self.assertEqual(set([entry.targetfileglob for entry in entry_list]),
                         set(['some.yaml', 'console.txt']))
        self.assertEqual(set([entry.regex for entry in entry_list if
                         entry.lp_bug_no == '0001']), set([regex1]))
