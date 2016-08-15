from __future__ import unicode_literals

from pythonkss import exceptions
from pythonkss.markupexamplebase import MarkupExampleBase


class Example(MarkupExampleBase):
    """
    Represents a Example part in a :class:`pythonkss.section.Section`
    (the part that starts with ``Example:``).

    .. attribute:: text

        The markup text (the lines below ``Example:``)

    .. attribute:: filename

        The filename. Can be ``None``.

    .. attribute:: title

        The title for the markup block. Can be ``None``.
    """
    supported_types = {'embedded', 'isolated', 'fullpage'}

    def __init__(self, text, filename=None, argumentstring=None):
        super(Example, self).__init__(text=text, filename=filename, argumentstring=argumentstring)

    @property
    def type(self):
        exampletype = self.argumentdict.get('type', 'embedded')
        if exampletype not in self.supported_types:
            raise exceptions.ArgumentStringError('Unsupported example type: {}'.format(exampletype))
        return exampletype

    @property
    def height(self):
        return self.argumentdict.get('height', '300px')
