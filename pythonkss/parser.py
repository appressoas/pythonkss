import os

from pythonkss.comment import CommentParser
from pythonkss.exceptions import SectionDoesNotExist
from pythonkss.section import Section


class Parser(object):
    """
    KSS parser.

    Examples:

        Parse a directory and print a styleguide (nice getting started exmaple for
        generating your own styleguide)::

            parser = pythonkss.Parser('/path/to/my/styles/')
            for section in parser.iter_sorted_sections():
                print()
                print('*' * 70)
                print(section.reference, section.title)
                print('*' * 70)
                print()

                for modifier in section.modifiers:
                    print('-- ', modifier.name, ' --')
                    print(modifier.description_html)

                if section.description:
                    print()
                    print(section.description_html)

                if section.has_markups():
                    print()
                    print('Usage:')
                    print('=' * 70)
                    print()
                    for markup in section.markups:
                        if markup.title:
                            print('-- ', markup.title, ' --')
                        print(markup.html)
    """

    def __init__(self, *paths, **kwargs):
        """

        Args:
            *paths: One or more directories to search for style files.
            extensions: List of file extensions to search for.
                Optional - defaults to ``['.less', '.css', '.sass', '.scss']``.

        Returns:

        """
        self.paths = paths
        extensions = kwargs.pop('extensions', None)
        if extensions is None:
            extensions = ['.less', '.css', '.sass', '.scss']
        self.extensions = extensions

    def parse(self):
        sections = {}

        for filename in self.find_files():
            parser = CommentParser(filename)
            for block in parser.blocks:
                section = Section(block, os.path.basename(filename))
                if section.reference:
                    sections[section.reference] = section

        return sections

    def find_files(self):
        '''Find files in `paths` which match valid extensions'''
        for path in self.paths:
            for subpath, dirs, files in os.walk(path):
                for filename in files:
                    (name, ext) = os.path.splitext(filename)
                    if ext in self.extensions:
                        yield os.path.join(subpath, filename)

    @property
    def sections(self):
        """
        A dict of sections with :meth:`~pythonkss.section.Section.reference` as key
        and :class:`:meth:`~pythonkss.section.Section` objects as value.
        """
        if not hasattr(self, '_sections'):
            self._sections = self.parse()
        return self._sections

    def get_sections(self, referenceprefix=None):
        """
        Get sections, optionally only sections with :meth:`~pythonkss.section.Section.reference`
        starting with ``referenceprefix``.

        Args:
            referenceprefix: If this is provided, only sections with :meth:`~pythonkss.section.Section.reference`
                starting with ``referenceprefix`` is included.

        Returns:
            list: A list of sections.
        """
        sections = self.sections.values()
        if referenceprefix:
            sections = filter(lambda s: s.reference.startswith(referenceprefix), sections)
        return sections

    def iter_sorted_sections(self, referenceprefix=None):
        """
        Iterate sections sorted by :meth:`pythonkss.section.Section.reference`.

        Args:
            referenceprefix: See :meth:`.get_sections`.

        Returns:
            generator: Iterable of :class:`pythonkss.section.Section` objects.
        """
        return sorted(self.get_sections(referenceprefix=referenceprefix), key=lambda s: s.reference)

    def get_section_by_reference(self, reference):
        """
        Get a section by its :meth:`pythonkss.section.Section.reference`.

        Raises:
            KeyError: If no section with the provided reference exists.
        """
        try:
            return self.sections[reference]
        except KeyError:
            raise SectionDoesNotExist('Section "%s" does not exist.' % reference)
