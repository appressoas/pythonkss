from collections import OrderedDict


class SectionTreeSection(object):
    def __init__(self, section):
        self.section = section


class SectionTree(object):
    def __init__(self, sections):
        """

        Args:
            sections: An iterable of :class:`pythonkss.section.Section`.
                Must be sorted by :class:`pythonkss.section.Section.reference`.
        """
        self.sections = sections
        self._tree = OrderedDict()
        for section in self.sections:
            self.add_section(section=section)

    # def add_section(self, section):
