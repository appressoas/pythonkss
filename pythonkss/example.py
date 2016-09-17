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

    def __init__(self, text, filename=None, argumentstring=None):
        super(Example, self).__init__(text=text, filename=filename, argumentstring=argumentstring)

    @property
    def type(self):
        """
        Get the value of the ``type`` option, or ``"embedded"`` if it is not specified.
        """
        return self.argumentdict.get('type', 'embedded')

    @property
    def height(self):
        """
        Get the value of the ``height`` option, or ``None`` if it is not specified.
        """
        return self.argumentdict.get('height', None)

    @property
    def code(self):
        return self.argumentdict.get('code', True)

    @property
    def preview(self):
        return self.argumentdict.get('preview', self.syntax == 'html')
