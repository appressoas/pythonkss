import os

from pythonkss.comment import CommentParser
from pythonkss.exceptions import SectionDoesNotExist, DuplicateReferenceError
from pythonkss.section import Section
from pythonkss.sectiontree import SectionTree


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

                if section.has_examples() or section.has_markups():
                    print()
                    print('Usage:')
                    print('=' * 70)
                    print()
                    for example in section.examples:
                        if example.title:
                            print('-- ', example.title, ' --')
                        print(example.html)
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
            variables (dict): Dict that maps variables to values.
                Variables can be used anywhere in the comments, and they are
                applied before any other parsing of the comments.
            variablepattern: The pattern used to insert variables. Defaults
                to ``{{% {variable} %}}``, which means that you would
                insert a variable added as ``$my-variable`` via the ``variables``
                parameter with something like this::

                    /* My title

                    The value of $my-variable is {% $my-variable %}.

                    Styleguide 1.1
                    */
        """
        self.paths = paths
        self.variables = kwargs.pop('variables', None)
        self.variablepattern = kwargs.pop('variablepattern', '{{% {variable} %}}')
        extensions = kwargs.pop('extensions', None)
        if extensions is None:
            extensions = ['.less', '.css', '.sass', '.scss']
        self.extensions = extensions

    def _make_variablemap(self):
        variablemap = {}
        if not self.variables:
            return variablemap
        for variable, value in self.variables.items():
            mapkey = self.variablepattern.format(variable=variable)
            variablemap[mapkey] = value
        return variablemap

    def parse(self):
        sections = {}
        variablemap = self._make_variablemap()

        for filepath in self.find_files():
            parser = CommentParser(filepath, variablemap=variablemap)
            for block in parser.blocks:
                section = Section(block, filepath=filepath)
                if section.reference:
                    if section.reference in sections:
                        first_defined_section = sections[section.reference]
                        raise DuplicateReferenceError(
                            reference=section.reference,
                            first_defined_section=first_defined_section,
                            duplicate_section=section
                        )
                    else:
                        sections[section.reference] = section
        return sections

    def find_files(self):
        """
        Find files in `paths` which match valid extensions.

        Returns:
            iterator: An iterable yielding file paths.
        """
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

    def as_tree(self):
        """
        Get sections organized in :class:`pythonkss.sectiontree.SectionTree`.

        Returns:
            pythonkss.sectiontree.SectionTree: The built tree.
        """
        if not hasattr(self, '_built_tree'):
            self._built_tree = SectionTree(sections=self.iter_sorted_sections())
        return self._built_tree

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
