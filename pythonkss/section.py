import os
import re

from pythonkss import markdownformatter
from pythonkss.example import Example
from pythonkss.modifier import Modifier


CLASS_MODIFIER = '.'
PSEUDO_CLASS_MODIFIER = ':'
MODIFIER_DESCRIPTION_SEPARATOR = ' - '
EXAMPLE_START_ALT1 = 'Markup:'
EXAMPLE_START_ALT2 = 'Example:'
REFERENCE_START = 'Styleguide'

reference_re = re.compile(r'%s ([\d\.]+)' % REFERENCE_START)
optional_re = re.compile(r'\[(.*)\]\?')
multiline_modifier_re = re.compile(r'^\s+(\w.*)')


class Section(object):

    def __init__(self, comment=None, filename=None):
        self.comment = comment or ''
        self.filename = filename

    def parse(self):
        self._heading = None
        self._description_lines = []
        self._modifiers = []
        self._examples = []
        self._reference = None

        in_example = False
        in_modifiers = False
        example_lines = []
        example_argumentstring = None

        lines = self.comment.strip().splitlines()
        if len(lines) == 0:
            return

        self._heading = lines[0].strip()

        for line in lines[1:]:
            if line.startswith(CLASS_MODIFIER) or line.startswith(PSEUDO_CLASS_MODIFIER):
                in_modifiers = True
                try:
                    modifier, description = line.split(MODIFIER_DESCRIPTION_SEPARATOR)
                except ValueError:
                    pass
                else:
                    self._modifiers.append(Modifier(modifier.strip(), description.strip()))

            elif in_modifiers and multiline_modifier_re.match(line):
                match = multiline_modifier_re.match(line)
                if match:
                    description = match.groups()[0]
                    last_modifier = self._modifiers[-1]
                    last_modifier.description += ' {0}'.format(description)

            elif line.startswith(EXAMPLE_START_ALT1) or line.startswith(EXAMPLE_START_ALT2):
                if example_lines:
                    self.add_example_linelist(example_lines, argumentstring=example_argumentstring)
                example_lines = []
                in_example = True
                in_modifiers = False
                arguments = line.split(':', 1)
                if len(arguments) > 1:
                    example_argumentstring = arguments[1]

            elif line.startswith(REFERENCE_START):
                in_example = False
                in_modifiers = False
                match = reference_re.match(line)
                if match:
                    self._reference = match.groups()[0].rstrip('.')

            elif in_example is True:
                example_lines.append(line)

            else:
                in_modifiers = False
                self._description_lines.append(line)

        self._description = '\n'.join(self._description_lines).strip()
        if example_lines:
            self.add_example_linelist(example_lines, argumentstring=example_argumentstring)

    @property
    def heading(self):
        if not hasattr(self, '_heading'):
            self.parse()
        return self._heading

    @property
    def description(self):
        if not hasattr(self, '_description'):
            self.parse()
        return self._description

    @property
    def description_html(self):
        return markdownformatter.MarkdownFormatter.to_html(markdowntext=self.description)

    @property
    def modifiers(self):
        if not hasattr(self, '_modifiers'):
            self.parse()
        return self._modifiers

    @property
    def examples(self):
        if not hasattr(self, '_modifiers'):
            self.parse()
        return self._examples

    def has_examples(self):
        return len(self._examples) > 0

    def has_multiple_examples(self):
        return len(self._examples) > 1

    @property
    def section(self):
        if not hasattr(self, '_reference'):
            self.parse()
        return self._reference

    def add_example_linelist(self, example_lines, **kwargs):
        text = '\n'.join(example_lines).strip()
        self.add_example(text=text, **kwargs)

    def add_example(self, text, **kwargs):
        example = Example(
            text=optional_re.sub('', text).replace('$modifier_class', ''),
            filename=self.filename,
            **kwargs)
        self._examples.append(example)
        for modifier in self._modifiers:
            modifier.add_example(optional_re.sub(r'\1', text))
