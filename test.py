from os import path
import shutil
import tempfile
import unittest
from unittest import mock


class DummyBaseClass:
    def __init__(self, vim):
        self.vim = vim
        self.Base = type(self)
        self.expand = lambda x: path.expanduser(path.expandvars(x))


patches = {
    'rplugin.python3.deoplete.filter.base': DummyBaseClass(None),
    'rplugin.python3.deoplete.sources.base': DummyBaseClass(None),
    'deoplete.util': DummyBaseClass(None),
}

with mock.patch.dict('sys.modules', patches):
    from rplugin.python3.deoplete.sources import mutt as source
    from rplugin.python3.deoplete.filter import matcher_mutt_alias as matcher


class TestSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.mkdtemp()
        alias = 'alias -group {x}-group {x} {X} Mc{X}face <{x}@example.com>'

        # files with aliases to test multiple alias files get searched
        for dummy in ('foo', 'bar', 'baz'):
            with open(path.join(cls.tempdir, dummy), 'w') as f:
                f.write(alias.format(x=dummy, X=dummy.title()))

        # file _without_ aliases to test that it is skipped
        with open(path.join(cls.tempdir, 'quux'), 'w') as f:
            f.write('foobar')

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tempdir)

    def setUp(self):
        self.vim = mock.Mock()
        self.source = source.Source(self.vim)

    def test_expand(self):
        import os
        with mock.patch.dict(os.environ, {'FOO': '~/foo'}):
            result = source.expand('$FOO/bar')

        expected = os.path.expanduser('~/foo/bar')
        self.assertEqual(result, expected)

    def test_attributes(self):
        self.assertEqual(self.source.name, 'mutt')
        self.assertEqual(self.source.mark, '[mutt]')
        self.assertEqual(self.source.rank, 150)
        self.assertEqual(self.source.filetypes, ['mail'])
        self.assertEqual(self.source.matchers, ['matcher_mutt_alias'])

    def test_find_mutt_dirs(self):
        expected = [self.tempdir]
        with mock.patch.object(source, 'POSSIBLE_MUTT_DIRS', new=expected):
            result = self.source._find_mutt_dirs()
        self.assertEqual(expected, result)

    def test_load_aliases(self):
        self.assertIsNone(self.source._aliases)

        expected = {
            ('foo', 'Foo McFooface', '<foo@example.com>',),
            ('bar', 'Bar McBarface', '<bar@example.com>',),
            ('baz', 'Baz McBazface', '<baz@example.com>',),
        }

        # aliases are implicitly loaded using the `aliases` property
        with mock.patch.object(source, 'POSSIBLE_MUTT_DIRS',
                               new=(self.tempdir,)):
            self.assertEqual(expected, self.source.aliases)

    def test_find_alias_files(self):
        self.assertIsNone(self.source._alias_files)

        with mock.patch.object(source, 'POSSIBLE_MUTT_DIRS',
                               new=(self.tempdir,)):
            self.source._find_alias_files()

        expected = {
            path.join(self.tempdir, 'foo'),
            path.join(self.tempdir, 'bar'),
            path.join(self.tempdir, 'baz'),
        }

        self.assertEqual(expected, self.source._alias_files)

    def test_gather_candidates(self):
        items = [
            ('key1', 'name1', 'email1'),
            ('key2', 'name2', 'email2'),
            ('key3', 'name3', 'email3'),
        ]
        with mock.patch.object(self.source, '_aliases', new=items):
            result = self.source.gather_candidates(None)

        expected = [
            {'word': 'name1 email1', 'abbr': 'key1: name1 email1'},
            {'word': 'name2 email2', 'abbr': 'key2: name2 email2'},
            {'word': 'name3 email3', 'abbr': 'key3: name3 email3'},
        ]

        self.assertEqual(result, expected)


class TestMatcher(unittest.TestCase):
    def setUp(self):
        self.vim = mock.Mock()
        self.filter = matcher.Filter(self.vim)

    def test_is_header(self):
        self.assertTrue(matcher.is_header('To: '))
        self.assertFalse(matcher.is_header('To :'))

    def test_attributes(self):
        self.assertEqual(self.filter.name, 'matcher_mutt_alias')
        self.assertEqual(self.filter.description, 'matcher for mutt aliases')

    def test_filter_no_header(self):
        ctx = {'input': 'this is not a header'}
        self.assertFalse(matcher.is_header(ctx['input']))
        self.assertEqual(self.filter.filter(ctx), [])

    def test_filter_with_header(self):
        ctx = {'input': 'validheader:'}
        self.assertTrue(matcher.is_header(ctx['input']))

        ctx['candidates'] = [
            {'abbr': 'FOOBAR'},
            {'abbr': 'foobar'},
            {'abbr': 'BARFOO'},
            {'abbr': 'barfoo'},
            {'abbr': 'BAZQUUX'},
            {'abbr': 'bazquux'},
        ]
        ctx['complete_str'] = 'foo'

        ctx['ignorecase'] = False
        result = self.filter.filter(ctx)
        self.assertEqual(result, [
            {'abbr': 'foobar'},
            {'abbr': 'barfoo'},
        ])

        ctx['ignorecase'] = True
        result = self.filter.filter(ctx)
        self.assertEqual(result, [
            {'abbr': 'FOOBAR'},
            {'abbr': 'foobar'},
            {'abbr': 'BARFOO'},
            {'abbr': 'barfoo'},
        ])


if __name__ == '__main__':
    unittest.main()
