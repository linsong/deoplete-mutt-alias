from os import path
import glob

from .base import Base
from deoplete.util import expand


POSSIBLE_MUTT_DIRS = ('$XDG_CONFIG_HOME/mutt', '~/.mutt',
                      '$XDG_CONFIG_HOME/neomutt', '~/.neomutt')


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'mutt'
        self.mark = '[mutt]'
        self.rank = 150
        self.filetypes = ['mail']
        self.matchers = ['matcher_mutt_alias']

        self._aliases = None
        self._alias_files = None

    @property
    def aliases(self):
        if self._aliases is None:
            self._load_aliases()

        return self._aliases

    def _load_aliases(self):
        self._aliases = set()
        if self._alias_files is None:
            self._find_alias_files()

        for file in self._alias_files:
            with open(file) as f:
                lines = f.read().splitlines()

            for line in lines:
                if line.strip().startswith('alias'):
                    pieces = line.split()
                    pieces.pop(0)  # remove 'alias'

                    if pieces[0] == '-group':
                        pieces.pop(0)  # remove '-group'
                        pieces.pop(0)  # remove group name

                    key = pieces.pop(0)
                    email = pieces.pop(-1)
                    name = ' '.join(pieces)
                    self._aliases.add((key, name, email))

    def _find_mutt_dirs(self):
        return [
            expand(location)
            for location in POSSIBLE_MUTT_DIRS
            if path.isdir(expand(location))
        ]

    def _find_alias_files(self):
        self._alias_files = set()

        for dir in self._find_mutt_dirs():
            for file in glob.glob(expand(dir + '/aliases')):
                if path.isdir(file):
                    continue
                with open(file) as f:
                    if any(line.lstrip().startswith('alias') for line in f):
                        self._alias_files.add(file)

    def gather_candidates(self, ctx):
        return [{
            'word': '{} {}'.format(name, email),
            'abbr': '{}: {} {}'.format(key, name, email),
        } for key, name, email in self.aliases]
