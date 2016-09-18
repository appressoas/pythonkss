import fnmatch
import os

from pythonkss.comment import CommentParser
from pythonkss.exceptions import SectionDoesNotExist, DuplicateReferenceError, ExtendReferenceDoesNotExistError, \
    ReplaceReferenceDoesNotExistError, NotSectionError
from pythonkss.section import Section
from pythonkss.sectiontree import SectionTree


class MultiCommentBlockParser(object):
    def __init__(self):
        self._finished = False
        self._sections = {}
        self._extend_sections_map = {}
        self._replace_sections_map = {}

        # For debugging
        self._ignored_extend_sections = []
        self._replaced_sections = []

    def _add_section_to_list_in_dict(self, dct, section):
        if section.reference not in dct:
            dct[section.reference] = []
        dct[section.reference].append(section)

    def _add_section_type_extend(self, section):
        self._add_section_to_list_in_dict(
            dct=self._extend_sections_map,
            section=section
        )

    def _add_section_type_replace(self, section):
        self._add_section_to_list_in_dict(
            dct=self._replace_sections_map,
            section=section
        )

    def _add_section_type_default(self, section):
        if section.reference in self._sections:
            first_defined_section = self._sections[section.reference]
            raise DuplicateReferenceError(
                reference=section.reference,
                first_defined_section=first_defined_section,
                duplicate_section=section
            )
        else:
            self._sections[section.reference] = section

    def _add_section(self, section):
        if section.section_type == Section.TYPE_DEFAULT:
            self._add_section_type_default(section)
        elif section.section_type in Section.EXTEND_TYPES:
            self._add_section_type_extend(section)
        elif section.section_type == Section.TYPE_REPLACE:
            self._add_section_type_replace(section)

    def parse_commentblock(self, commentblock, filepath):
        section = Section(commentblock, filepath=filepath)
        try:
            section.parse()
        except NotSectionError:
            pass
        else:
            self._add_section(section)

    def _replace_sections(self):
        for reference, sections in self._replace_sections_map.items():
            if reference in self._sections:
                self._replaced_sections.append(
                    self._sections.pop(reference))
                if reference in self._extend_sections_map:
                    self._ignored_extend_sections.extend(
                        self._extend_sections_map.pop(reference))
                self._sections[reference] = sections[-1]
            else:
                raise ReplaceReferenceDoesNotExistError(
                    'Invalid "StyleguideReplace {reference}". '
                    'No normal section with this reference exists. '
                    'In file: {filepath}.'.format(
                        reference=reference,
                        filepath=sections[0].filepath))

    def _merge_sections(self):
        for reference, source_sections in self._extend_sections_map.items():
            try:
                target_section = self._sections[reference]
            except KeyError:
                raise ExtendReferenceDoesNotExistError(
                    'Invalid "Styleguide{section_type} {reference}". '
                    'No normal section with this reference exists. '
                    'In file: {filepath}.'.format(
                        section_type=source_sections[0].section_type,
                        filepath=source_sections[0].filepath,
                        reference=reference
                    ))
            else:
                for source_section in source_sections:
                    source_section.merge_into_section(target_section=target_section)

    def finish(self):
        """
        Handle merge and replace, and set ``self.sections`` to
        the resulting dict of sections.
        """
        self._replace_sections()
        self._merge_sections()
        self._finished = True

    def __check_finished(self, property_):
        if not self._finished:
            raise Exception('You have to call finish() before using '
                            'the {} property'.format(property_))

    @property
    def sections(self):
        self.__check_finished('sections')
        return self._sections

    @property
    def ignored_extend_sections(self):
        self.__check_finished('ignored_extend_sections')
        return self._ignored_extend_sections

    @property
    def replaced_sections(self):
        self.__check_finished('replaced_sections')
        return self._replaced_sections


class Parser(object):
    """
    Parses one or more directories of style files.

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
            filename_patterns: Optional list of :func:`fnmatch.fnmatchcase` patterns for
                files to include in the styleguide.

                If this is not provided, all files in the directories specified
                in ``*paths`` is included.

                If this is provided, it must be a list/iterable of :func:`fnmatch.fnmatchcase`
                patterns. All file-paths matching any of the patterns in the list is included.
                Example::

                    filename_patterns=[
                        '*mytheme/*',
                        '*external_theme/essentials/*',
                        '*external_theme/advanced/menu.scss',
                        '*external_theme/advanced/navbar.scss',
                    ]

                The check agains filename_patterns is performed after the check for
                filename extensions (see ``extensions`` kwarg). So if a filename
                does not match the required extensions, putting it in ``filename_patterns``
                does not help at all.
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
        self.filename_patterns = kwargs.pop('filename_patterns', None)
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

    def _has_match_in_filename_patterns(self, filepath):
        for pattern in self.filename_patterns:
            if fnmatch.fnmatchcase(filepath, pattern):
                return True
        return False

    def should_include_file(self, filepath):
        if self.filename_patterns is None:
            return True
        if self._has_match_in_filename_patterns(filepath):
            return True
        else:
            return False

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
                        filepath = os.path.join(subpath, filename)
                        if self.should_include_file(filepath):
                            yield filepath

    def parse(self):
        variablemap = self._make_variablemap()
        multiblockparser = MultiCommentBlockParser()
        for filepath in self.find_files():
            commentparser = CommentParser(filepath, variablemap=variablemap)
            for commentblock in commentparser.blocks:
                multiblockparser.parse_commentblock(
                    commentblock=commentblock,
                    filepath=filepath)
        multiblockparser.finish()
        return multiblockparser

    @property
    def multiblockparser(self):
        if not hasattr(self, '_multiblockparser'):
            self._multiblockparser = self.parse()
        return self._multiblockparser

    @property
    def sections(self):
        """
        A dict of sections with :meth:`~pythonkss.section.Section.reference` as key
        and :class:`:meth:`~pythonkss.section.Section` objects as value.
        """
        return self.multiblockparser.sections

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
