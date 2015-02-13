#!/usr/bin/python

import unittest
from tempfile import mkstemp

import sys, os.path
sys.path.insert(0, os.path.realpath(
        os.path.join(os.path.dirname(__file__), "..")))

from arsenal.utils.config import Config
from arsenal.utils.file_io import FileDoesntExist

class TestUtilsConfig(unittest.TestCase):
    def test_init_empty(self):
        config = Config(lines=[])

        self.assertEqual(Config, type(config))
        self.assertEqual({}, config.__dict__)

    def test_init_multiline_string(self):
        s = "one=1\ntwo=2"
        config = Config(lines=s)

        self.assertEqual('1', config.one)
        self.assertEqual('2', config.two)

    def test_init_list_of_lines(self):
        config = Config(lines=['a=1','b=2','c=3'])

        self.assertEqual('1', config.a)
        self.assertEqual('2', config.b)
        self.assertEqual('3', config.c)

    def test_init_missing_file(self):
        self.assertRaises(FileDoesntExist,
                          Config, ".../invalid.conf")

    def test_init_blank_file(self):
        fd, conf_file = mkstemp()
        config = Config(conf_file)

        self.assertEqual({'_filename': conf_file},
                         config.__dict__)

    def test_init_trivial_file(self):
        fd, conf_file = mkstemp()
        os.write(fd, "a = 1\n")
        os.write(fd, "b = 2\n")
        config = Config(conf_file)

        self.assertEqual(3, len(config.__dict__))
        self.assertEqual('1', config.a)
        self.assertEqual('2', config.b)

    def test_init_file_and_lines(self):
        fd, conf_file = mkstemp()
        os.write(fd, "a = 1\n")
        os.write(fd, "b = 2\n")
        config = Config(conf_file, lines=["c=3", "d=4"])

        self.assertEqual(5, len(config.__dict__))
        self.assertEqual('2', config.b)
        self.assertEqual('4', config.d)

    def test_filename(self):
        fd, conf_file = mkstemp()
        config = Config(conf_file)

        self.assertEqual(conf_file, config.filename)

    def test_clear(self):
        config = Config(lines=['a=1','b=2','c=3'])
        config.clear()

        self.assertEqual({}, config.__dict__)

    def test_get(self):
        config = Config(lines=['a=1','b=2','c=3'])

        self.assertEqual('2', config.get('b'))

    def test_set(self):
        config = Config(lines=['a=1','b=2','c=3'])
        config.set('a', '4')

        self.assertEqual('4', config.a)

    def test_load(self):
        config = Config(lines=['a=1','b=2','c=3'])
        config.load(['d=4', 'e=5', 'f=6'])

        print config.__dict__.keys()

        self.assertEqual('2', config.b)
        self.assertEqual('5', config.e)
        self.assertEqual(6, len(config.__dict__.keys()))

    def test_load_whitespace(self):
        config = Config(lines=[])
        config.load([
            "a = 1",
            "  b  =  2",
            "c=    3",
            "d = ",
            "",
            "  ",
            " = ",
            ])

        self.assertEqual('1', config.a)
        self.assertEqual('2', config.b)
        self.assertEqual('3', config.c)
        self.assertEqual('',  config.d)
        self.assertEqual(4, len(config.__dict__.keys()))

    def test_load_line_continuation_comma(self):
        config = Config(lines=[])
        # TODO: Test with various line endings and continuations
        config.load([
            "a = 1,",
            "    2,",
            "    3"])

        self.assertEqual(1, len(config.__dict__.keys()))
        self.assertEqual('1, 2, 3', config.a)

    def test_load_line_continuation_backslash(self):
        config = Config(lines=[])
        # TODO: Test with various line endings and continuations
        config.load([
            "a = the \\",
            "    quick \\ ",
            "    brown\\",
            "    fox"])

        self.assertEqual(1, len(config.__dict__.keys()))
        self.assertEqual("the quick brown fox", config.get('a'))

    def test_load_includes(self):
        fd, conf_file = mkstemp()
        os.write(fd, "a = 1\n")
        config = Config(conf_file)
        config = Config(lines=["include %s" %(conf_file)])
        self.assertEqual(1, len(config.__dict__.keys()))
        self.assertEqual('1', config.get('a'))

    def test_iter(self):
        config = Config(lines=['a=1', 'b=2', 'c=3'])
        text = ""
        for key, value in config:
            text += "%s=%s " %(key, value)

        self.assertEqual("a=1 b=2 c=3 ", text)

    def test_len(self):
        config = Config(lines=[])

        self.assertEqual(0, config.__len__())
        self.assertEqual(0, len(config))

        config.set('a', '1')
        config.set('b', '2')

        self.assertEqual(2, config.__len__())
        self.assertEqual(2, len(config))

    def test_str(self):
        config = Config(lines=['a=1', 'b=2'])

        text = str(config)
        self.assertEqual("a=1\nb=2\n", text)

    def test_str_list(self):
        config = Config(lines=[])
        config.set('a', [1, 2, 3])

        text = str(config)
        self.assertEqual("a=1, 2, 3\n", text)

    def test_getitem(self):
        config = Config(lines=['a=1', 'b=2'])
        self.assertEqual('1', config['a'])
        self.assertEqual('2', config['b'])

    def test_contains(self):
        config = Config(lines=['a=1', 'b=2'])
        self.assertTrue('a' in config)
        self.assertTrue('b' in config)

if __name__ == "__main__":
    unittest.main()
