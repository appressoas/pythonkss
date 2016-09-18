import os
import re
import textwrap

from pythonkss import markdownformatter
from pythonkss.example import Example
from pythonkss.exceptions import NotSectionError, InvalidMergeSectionTypeError, InvalidMergeNotSameReferenceError

EXAMPLE_START = 'Example:'

intented_line_re = re.compile(r'^\s\s+.*$')
reference_re = re.compile(
    r'^Styleguide(?P<type>(?:ExtendBefore|ExtendAfter|Replace))? '
    r'(?P<reference>(?:[0-9a-z_-]*\.)*(?:(?:\d+:)?[0-9a-z_-]+))$')
extend_title_re = re.compile(r'Title:(?P<title>.+)$')


class SectionParser(object):
    def __init__(self, comment):
        self.comment = comment
        self.title = None
        self.section_type = None
        self.examples = []
        self.raw_reference = None
        self.reference = None
        self.raw_reference_segment_list = []
        self.reference_segment_list = []
        self.sortkey = None
        self.description = None

        self.in_example = False
        self.description_lines = []
        self.example_lines = []
        self.example_argumentstring = None

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

    def parse_body_line(self, line):
        if line.startswith(EXAMPLE_START):
            self._parse_example_start(line=line)
        elif self.in_example is True and (intented_line_re.match(line) or line.strip() == ''):
            self._parse_in_example(line=line)

        else:
            self._parse_description(line=line)

    def _parse_extend_title(self, line):
        match = extend_title_re.match(line)
        if match:
            return match.groupdict()['title'].strip()
        else:
            return None

    def _parse_title(self, line):
        title_line_consumed = False
        line = line.strip()
        if self.section_type in Section.EXTEND_TYPES:
            title = self._parse_extend_title(line)
            if title:
                self.title = title
                title_line_consumed = True
        else:
            self.title = line
            title_line_consumed = True
        return title_line_consumed

    def _parse_raw_reference(self, raw_reference):
        self.raw_reference = raw_reference
        if raw_reference:
            self.raw_reference_segment_list = self.raw_reference.split('.')
            self.sortkey, text = self._parse_last_reference_segment(self.raw_reference_segment_list[-1])
            self.reference_segment_list = self.raw_reference_segment_list[0:-1] + [text]
            self.reference = '.'.join(self.reference_segment_list)

    def _parse_styleguide_line(self, line):
        match = reference_re.match(line)
        if match:
            groupdict = match.groupdict()
            self.section_type = groupdict['type'] or Section.TYPE_DEFAULT
            self._parse_raw_reference(groupdict['reference'])

    def parse(self, reference=None, title=None):
        """
        Parse the section.

        Args:
            reference: If provided, we parse the provided reference
                instead of extracting it from the content
                after ``Styleguide`` on the last line of the comment.
            title: If provided, we use the provided title
                instead of extracting it from the first line of the comment.
        """
        lines = self.comment.strip().splitlines()
        minimum_lines = 2
        if reference:
            minimum_lines -= 1
        if title:
            minimum_lines -= 1
        if len(lines) < minimum_lines:
            raise NotSectionError('Not a section. A section must have at least 2 lines.',
                                  comment_lines=lines)
        if reference:
            self._parse_raw_reference(reference)
        else:
            styleguide_line = lines.pop()
            self._parse_styleguide_line(styleguide_line)
        if self.reference is None:
            raise NotSectionError('Not a section. A section must have the reference on the last line.',
                                  comment_lines=lines)

        if title:
            self._parse_title(title)
        else:
            title_line_consumed = self._parse_title(lines[0])
            if title_line_consumed:
                lines = lines[1:]

        self._reset_in_booleans()
        for line in lines:
            self.parse_body_line(line=line)
        self.description = '\n'.join(self.description_lines).strip()
        if self.example_lines:
            self.examples.append([self.example_lines, self.example_argumentstring])


class Section(object):
    """
    A section in the documentation.
    """
    TYPE_DEFAULT = 'Default'
    TYPE_EXTEND_AFTER = 'ExtendAfter'
    TYPE_EXTEND_BEFORE = 'ExtendBefore'
    EXTEND_TYPES = {TYPE_EXTEND_BEFORE, TYPE_EXTEND_AFTER}
    TYPE_REPLACE = 'Replace'

    def __init__(self, comment=None, filepath=None):
        self.comment = comment or ''
        self.filepath = filepath
        self._parsed = False

    @property
    def filename(self):
        if self.filepath:
            return os.path.basename(self.filepath)
        else:
            return self.filepath

    def parse(self, **kwargs):
        """
        Parse the section.

        Args:
            **kwargs: Forwarded to :meth:`.SectionParser.parse`.
        """
        sectionparser = SectionParser(comment=self.comment)
        sectionparser.parse(**kwargs)
        self._section_type = sectionparser.section_type
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

    def parse_if_needed(self):
        if not self._parsed:
            self.parse()

    @property
    def section_type(self):
        """
        Get the title (the first line of the comment).
        """
        if not hasattr(self, '_section_type'):
            self.parse()
        return self._section_type

    @property
    def title(self):
        """
        Get the title (the first line of the comment).
        """
        if not hasattr(self, '_title'):
            self.parse()
        return self._title

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

    def _merge_title_into_section(self, target_section, after):
        if after:
            formattingstring = '{target} {source}'
        else:
            formattingstring = '{source} {target}'
        target_section._title = formattingstring.format(
            source=self.title,
            target=target_section.title)

    def _merge_description_into_section(self, target_section, after):
        if after:
            formattingstring = '{target}\n\n{source}'
        else:
            formattingstring = '{source}\n\n{target}'
        target_section._description = formattingstring.format(
            source=self.description,
            target=target_section.description)

    def _merge_examples_into_section(self, target_section, after):
        if after:
            target_section._examples.extend(self._examples)
        else:
            target_section._examples = self._examples + target_section._examples

    def merge_into_section(self, target_section):
        if self.section_type not in self.EXTEND_TYPES:
            raise InvalidMergeSectionTypeError(
                'Can only merge sections of the following types '
                'into other sections: {extend_types}'.format(
                    extend_types=', '.join(self.EXTEND_TYPES)
                ))
        elif self.reference != target_section.reference:
            raise InvalidMergeNotSameReferenceError(
                'Can only merge sections with the same reference.'
                'Trying to merge {source} into {target}'.format(
                    source=self.reference,
                    target=target_section.reference
                ))
        after = self.section_type == self.TYPE_EXTEND_AFTER
        if self.title:
            self._merge_title_into_section(target_section=target_section, after=after)
        if self.description:
            self._merge_description_into_section(target_section=target_section, after=after)
        if self.examples:
            self._merge_examples_into_section(target_section=target_section, after=after)
