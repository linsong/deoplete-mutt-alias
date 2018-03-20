from .base import Base
import re


def is_header(line):
    return re.match('[^ :\t\r\n\f\v]+:', line, re.ASCII) is not None


class Filter(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'matcher_mutt_alias'
        self.description = 'matcher for mutt aliases'

    def filter(self, ctx):
        if not is_header(ctx['input']):
            return []

        complete_str = ctx['complete_str']

        if ctx['ignorecase']:
            complete_str = complete_str.lower()
            return [c for c in ctx['candidates']
                    if complete_str in c['abbr'].lower()]

        return [c for c in ctx['candidates'] if complete_str in c['abbr']]
