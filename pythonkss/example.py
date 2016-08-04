from __future__ import unicode_literals

import os

from pythonkss import markdownformatter


class Example(object):
    def __init__(self, text, filename, syntax=None, title=None, argumentstring=None):
        self.text = text
        self.filename = filename
        self.syntax = syntax
        self.title = title
        self.argumentstring = argumentstring.strip()
        if argumentstring:
            self._parse_argumentstring()

    def _parse_argumentstring(self):
        argumentwords = self.argumentstring.split()
        if len(argumentwords) == 0:
            return
        firstword = argumentwords[0]
        if firstword.startswith('(') and firstword.endswith(')'):
            self.syntax = firstword[1:-1]
            titlewords = argumentwords[1:]
        else:
            titlewords = argumentwords
        if titlewords:
            self.title = ' '.join(titlewords)

    def get_syntax_from_filename(self):
        syntax = 'css'
        if self.filename:
            extension = os.path.splitext(self.filename)[1]
            if extension:
                extension = extension[1:]
                if extension in ['scss', 'sass', 'less']:
                    syntax = extension
        return syntax

    def guess_syntax(self):
        if self.text.startswith('<') and '>' in self.text:
            return 'html'
        else:
            return self.get_syntax_from_filename()

    def get_syntax(self):
        if self.syntax:
            return self.syntax
        else:
            return self.guess_syntax()

    @property
    def html(self):
        markdowntext = '```{syntax}\n{text}\n```'.format(
            syntax=self.get_syntax(),
            text=self.text)
        return markdownformatter.MarkdownFormatter.to_html(markdowntext=markdowntext)
