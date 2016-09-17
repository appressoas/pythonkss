import os
import re
import textwrap

from pythonkss import markdownformatter
from pythonkss.example import Example


CLASS_MODIFIER = '.'
PSEUDO_CLASS_MODIFIER = ':'
EXAMPLE_START = 'Example:'
REFERENCE_START = 'Styleguide'

intented_line_re = re.compile(r'^\s\s+.*$')
reference_re = re.compile(r'^%s ((?:[0-9a-z_-]*\.)*(?:(?:\d+:)?[0-9a-z_-]+))$' % REFERENCE_START)
optional_re = re.compile(r'\[(.*)\]\?')


class SectionParser(object):
    def __init__(self, comment):
        self.comment = comment
        self.title = None
        self.examples = []
        self.raw_reference = None
        self.reference = None
        self.raw_reference_segment_list = []
        self.reference_segment_list = []
        self.sortkey = None

        self.in_example = False
        self.description_lines = []
        self.example_lines = []
        self.example_argumentstring = None
        self.parse()

    def _reset_in_booleans(self):
        self.in_example = False

    def _parse_last_reference_segment(self, last_reference_segment):
        sortkey = None
        if last_reference_segment.isdigit():
            sortkey = int(last_reference_segment)
            text = last_reference_segment
        elif ':' in last_reference_segment:
            sortkey, text = last_reference_segment.split(':')
            sortkey = int(sortkey)
        else:
            text = last_reference_segment
        return sortkey, text

    def _parse_raw_reference(self, raw_reference):
        self.raw_reference = raw_reference
        if raw_reference:
            self.raw_reference_segment_list = self.raw_reference.split('.')
            self.sortkey, text = self._parse_last_reference_segment(self.raw_reference_segment_list[-1])
            self.reference_segment_list = self.raw_reference_segment_list[0:-1] + [text]
            self.reference = '.'.join(self.reference_segment_list)

    def _parse_reference_start(self, line):
        self._reset_in_booleans()
        match = reference_re.match(line)
        if match:
            self._parse_raw_reference(match.groups()[0])

    def _parse_example_start(self, line):
        if self.example_lines:
            self.examples.append([self.example_lines, self.example_argumentstring])
        self.example_lines = []
        self._reset_in_booleans()
        self.in_example = True
        arguments = line.split(':', 1)
        if len(arguments) > 1:
            self.example_argumentstring = arguments[1]

    def _parse_in_example(self, line):
        self.example_lines.append(line)

    def _parse_description(self, line):
        self._reset_in_booleans()
        self.description_lines.append(line)

    def parse_line(self, line):
        if line.startswith(REFERENCE_START):
            self._parse_reference_start(line=line)

        elif line.startswith(EXAMPLE_START):
            self._parse_example_start(line=line)
        elif self.in_example is True and (intented_line_re.match(line) or line.strip() == ''):
            self._parse_in_example(line=line)

        else:
            self._parse_description(line=line)

    def parse(self):
        lines = self.comment.strip().splitlines()
        if len(lines) == 0:
            return
        self.title = lines[0].strip()
        for line in lines[1:]:
            self.parse_line(line=line)
        self.description = '\n'.join(self.description_lines).strip()
        if self.example_lines:
            self.examples.append([self.example_lines, self.example_argumentstring])


class Section(object):
    """
    A section in the documentation.
    """

    def __init__(self, comment=None, filepath=None):
        self.comment = comment or ''
        self.filepath = filepath

    @property
    def filename(self):
        return os.path.basename(self.filepath)

    def parse(self):
        sectionparser = SectionParser(comment=self.comment)
        self._title = sectionparser.title
        self._description = sectionparser.description
        self._reference = sectionparser.reference
        self._raw_reference = sectionparser.raw_reference
        self._raw_reference_segment_list = sectionparser.raw_reference_segment_list
        self._reference_segment_list = sectionparser.reference_segment_list
        self._sortkey = sectionparser.sortkey
        self._examples = []
        for lines, argumentstring in sectionparser.examples:
            self._add_example_linelist(example_lines=lines, argumentstring=argumentstring)

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
    def examples(self):
        """
        Get all ``Example:`` sections as a list of :class:`pythonkss.example.Example` objects.
        """
        if not hasattr(self, '_examples'):
            self.parse()
        return self._examples

    def has_examples(self):
        """
        Returns ``True`` if the section has at least one ``Example:`` section.
        """
        return len(self._examples) > 0

    def has_multiple_examples(self):
        """
        Returns ``True`` if the section more than one ``Example:`` section.
        """
        return len(self._examples) > 1

    @property
    def reference(self):
        """
        Get the reference.

        This is the part after ``Styleguide`` at the end of the comment.
        If the reference format is ``<number>:<text>``, this is only the ``<text>``.
        """
        if not hasattr(self, '_reference'):
            self.parse()
        return self._reference

    @property
    def raw_reference(self):
        """
        Get the raw reference.

        This is the part after ``Styleguide`` at the end of the comment.

        How a reference is parsed:

        - Split the reference into segments by ``"."``.
        - All the segments except the last refer to the parent.
        - The part after the last ``"."`` is in one of the following formats:
            - ``[a-z0-9_-]+``
            - ``<number>:<[a-z0-9_-]+>``
        - All segments except the last can only contain ``[a-z0-9_-]+``.
        """
        if not hasattr(self, '_reference'):
            self.parse()
        return self._raw_reference

    @property
    def raw_reference_segment_list(self):
        """
        Get :meth:`.raw_reference` as a list of segments.

        Just a shortcut for ``raw_reference.split('.')``, but slightly
        faster because the list is created when the section is parsed.
        """
        if not hasattr(self, '_reference'):
            self.parse()
        return self._raw_reference_segment_list

    @property
    def reference_segment_list(self):
        """
        Get :meth:`.reference` as a list of segments.

        Just a shortcut for ``reference.split('.')``, but slightly
        faster because the list is created when the section is parsed.
        """
        if not hasattr(self, '_reference'):
            self.parse()
        return self._reference_segment_list

    def iter_reference_segments_expanded(self):
        """
        Iterate over :meth:`.reference_segment_list`, and return the
        reference of each segment.

        So if the :meth:`.reference` is ``a.b.c``, this will yield:

        - a
        - a.b
        - a.b.c
        """
        collected = []
        for segment in self.reference_segment_list:
            collected.append(segment)
            yield '.'.join(collected)

    @property
    def sortkey(self):
        """
        Get the sortkey for this reference within the parent section.

        Parses the last segment of the reference, and extracts a sort key.
        Extracted as follows:

        - If the segment is a number, return the number.
        - If the segment starts with ``<number>:``, return the number.
        - Otherwise, return ``None``.

        See :meth:`.reference` for information about what we mean by "segment".

        Some examples (reference -> sortkey):

        - 1 -> 1
        - 4.3  -> 3
        - 4.5.2 -> 2
        - 4.myapp-lists -> None
        - 4.12:myapp-lists -> 12
        """
        if not hasattr(self, '_reference'):
            self.parse()
        return self._sortkey

    def _add_example_linelist(self, example_lines, **kwargs):
        text = '\n'.join(example_lines)
        text = textwrap.dedent(text).strip()
        self.add_example(text=text, **kwargs)

    def add_example(self, text, **kwargs):
        """
        Add a example block to the section.

        Args:
            text: The text for the example.
            **kwargs: Kwargs for :class:`pythonkss.example.Example`.
        """
        example = Example(
            text=text,
            filename=self.filename,
            **kwargs)
        self._examples.append(example)
