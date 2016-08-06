import re

from pythonkss import markdownformatter
from pythonkss.markup import Markup
from pythonkss.modifier import Modifier


CLASS_MODIFIER = '.'
PSEUDO_CLASS_MODIFIER = ':'
MODIFIER_DESCRIPTION_SEPARATOR = ' - '
MARKUP_START_ALT1 = 'Markup:'
REFERENCE_START = 'Styleguide'

reference_re = re.compile(r'%s ([\d\.]+)' % REFERENCE_START)
optional_re = re.compile(r'\[(.*)\]\?')
multiline_modifier_re = re.compile(r'^\s+(\w.*)')


class SectionParser(object):
    def __init__(self, comment):
        self.comment = comment
        self.title = None
        self.description_lines = []
        self.modifiers = []
        self.markups = []
        self.reference = None
        self.markups = []

        self.in_markup = False
        self.in_modifiers = False
        self.markup_lines = []
        self.markup_argumentstring = None
        self.parse()

    def parse_line(self, line):
        if line.startswith(CLASS_MODIFIER) or line.startswith(PSEUDO_CLASS_MODIFIER):
            self.in_modifiers = True
            try:
                modifier, description = line.split(MODIFIER_DESCRIPTION_SEPARATOR)
            except ValueError:
                pass
            else:
                self.modifiers.append(Modifier(modifier.strip(), description.strip()))

        elif self.in_modifiers and multiline_modifier_re.match(line):
            match = multiline_modifier_re.match(line)
            if match:
                description = match.groups()[0]
                last_modifier = self.modifiers[-1]
                last_modifier.description += ' {0}'.format(description)

        elif line.startswith(MARKUP_START_ALT1):
            if self.markup_lines:
                self.markups.append([self.markup_lines, self.markup_argumentstring])
            self.markup_lines = []
            self.in_markup = True
            self.in_modifiers = False
            arguments = line.split(':', 1)
            if len(arguments) > 1:
                self.markup_argumentstring = arguments[1]

        elif line.startswith(REFERENCE_START):
            self.in_markup = False
            self.in_modifiers = False
            match = reference_re.match(line)
            if match:
                self.reference = match.groups()[0].rstrip('.')

        elif self.in_markup is True:
            self.markup_lines.append(line)

        else:
            self.in_modifiers = False
            self.description_lines.append(line)

    def parse(self):
        lines = self.comment.strip().splitlines()
        if len(lines) == 0:
            return
        self.title = lines[0].strip()
        for line in lines[1:]:
            self.parse_line(line=line)
        self.description = '\n'.join(self.description_lines).strip()
        if self.markup_lines:
            self.markups.append([self.markup_lines, self.markup_argumentstring])


class Section(object):
    """
    A section in the documentation.
    """

    def __init__(self, comment=None, filename=None):
        self.comment = comment or ''
        self.filename = filename

    def parse(self):
        sectionparser = SectionParser(comment=self.comment)
        self._title = sectionparser.title
        self._description = sectionparser.description
        self._modifiers = sectionparser.modifiers
        self._reference = sectionparser.reference
        self._markups = []
        for lines, argumentstring in sectionparser.markups:
            self._add_markup_linelist(markup_lines=lines, argumentstring=argumentstring)

    @property
    def title(self):
        """
        Get the title (the first line of the comment).
        """
        if not hasattr(self, '_title'):
            self.parse()
        return self._title

    @property
    def description(self):
        """
        Get the description as plain text.
        """
        if not hasattr(self, '_description'):
            self.parse()
        return self._description

    @property
    def description_html(self):
        """
        Get the :meth:`.description` converted to markdown using
        :class:`pythonkss.markdownformatter.MarkdownFormatter`.
        """
        return markdownformatter.MarkdownFormatter.to_html(markdowntext=self.description)

    @property
    def modifiers(self):
        """
        Get a list of :class:`pythonkss.modifier.Modifier` objects.
        One for each modifier in the comment.
        """
        if not hasattr(self, '_modifiers'):
            self.parse()
        return self._modifiers

    @property
    def markups(self):
        """
        Get all ``Markup:`` sections as a list of :class:`pythonkss.markup.Markup` objects.
        """
        if not hasattr(self, '_modifiers'):
            self.parse()
        return self._markups

    def has_markups(self):
        """
        Returns ``True`` if the section has at least one ``Markup:`` section.
        """
        return len(self._markups) > 0

    def has_multiple_markups(self):
        """
        Returns ``True`` if the section more than one ``Markup:`` section.
        """
        return len(self._markups) > 1

    @property
    def reference(self):
        """
        Get the reference.

        This is the part after ``Styleguide:`` at the end of the comment.
        """
        if not hasattr(self, '_reference'):
            self.parse()
        return self._reference

    def _add_markup_linelist(self, markup_lines, **kwargs):
        text = '\n'.join(markup_lines).strip()
        self.add_markup(text=text, **kwargs)

    def add_markup(self, text, **kwargs):
        """
        Add a markup block to the section

        Args:
            text: The text for the example.
            **kwargs: Kwargs for :class:`pythonkss.markup.Markup`.
        """
        markup = Markup(
            text=optional_re.sub('', text).replace('$modifier_class', ''),
            filename=self.filename,
            **kwargs)
        self._markups.append(markup)
        for modifier in self._modifiers:
            modifier.add_markup(optional_re.sub(r'\1', text))
