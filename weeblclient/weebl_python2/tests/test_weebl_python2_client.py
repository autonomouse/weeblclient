import testtools
from weeblclient.weebl_python2.weebl import utils


class WeeblClientTests(testtools.TestCase):
    pass


class WeeblClientUtilsTests(testtools.TestCase):
    def test_build_bug_info_dict(self):
        regexes = [
         {u'bug': {u'bugtrackerbug': {u'bug_number': 905638,
            u'created_at': u'2016-07-05T18:45:00.800467',
            u'project': {u'name': u'qdaemon',
             u'uuid': u'57e49478-d678-4230-b9e9-7cba1418837f'},
            u'updated_at': u'2016-07-05T18:45:00.800467',
            u'uuid': u'8daca2b5-55d3-494e-9ec1-b4c19479b139'},
           u'description': None,
           u'last_seen': u'2016-05-31T12:01:06',
           u'occurrence_count': 40,
           u'summary': u'qdaemon failed to restart charm',
           u'uuid': u'21755bbc-2874-47f0-aa4e-5c1223059d64'},
          u'regex': u'45886{93802}-62702(52772)',
          u'targetfileglobs': [{u'glob_pattern': u'console.txt',
          u'jobtypes': [{u'description': None, u'name': u'pipeline_start'}]}],
          u'uuid': u'63fedc7e-ca8f-4a12-9de9-3fd81ecd2e72'},
         {u'bug': {u'bugtrackerbug': {u'bug_number': 1578891,
            u'created_at': u'2016-07-05T18:45:01.179299',
            u'project': {u'name': u'kernel',
             u'uuid': u'80bee406-3bec-4465-86f2-e6c8ce6b091a'},
            u'updated_at': u'2016-07-05T18:45:01.179299',
            u'uuid': u'3c1e96b8-549c-478e-8067-41431ed1058b'},
           u'description': None,
           u'last_seen': u'2016-07-03T16:18:19',
           u'occurrence_count': 39,
           u'summary': u'kernel did not start up',
           u'uuid': u'7ce19b08-9876-46b8-8028-c7d75cd6b938'},
          u'regex': u'13539{94476}-97589(5091)',
          u'targetfileglobs': [{u'glob_pattern': u'juju_debug_log.txt',
          u'jobtypes': [{u'description': None, u'name': u'pipeline_deploy'}]}],
          u'uuid': u'bb14eb84-4708-43ad-a8dc-81137aded083'}]

        output = utils.munge_bug_info_data(regexes)

        ideal_output = {'bugs': {
            905638: {
                u'pipeline_start':
                    [{'regexp': [u'45886{93802}-62702(52772)'],
                      'uuids': [u'63fedc7e-ca8f-4a12-9de9-3fd81ecd2e72']}],
                'regex_uuid': u'63fedc7e-ca8f-4a12-9de9-3fd81ecd2e72'},
            1578891: {
                u'pipeline_deploy':
                    [{'regexp': [u'13539{94476}-97589(5091)'],
                      'uuids': [u'bb14eb84-4708-43ad-a8dc-81137aded083']}],
                'regex_uuid': u'bb14eb84-4708-43ad-a8dc-81137aded083'}}}

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
