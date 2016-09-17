class SectionDoesNotExist(Exception):
    pass


class DuplicateReferenceError(Exception):
    def __init__(self, reference, first_defined_section, duplicate_section):
        self.reference = reference
        self.first_defined_section = first_defined_section
        self.duplicate_section = duplicate_section
        message = ('Duplicate section reference: {reference!r}. '
                   'Defined both in {filepath1!r} and {filepath2!r}.').format(
            reference=reference,
            filepath1=self.first_defined_section.filepath,
            filepath2=self.duplicate_section.filepath)
        super(DuplicateReferenceError, self).__init__(message)


class ArgumentStringError(Exception):
    pass
