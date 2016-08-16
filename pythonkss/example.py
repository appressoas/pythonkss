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

    #: Supported ``type`` option values.
    supported_types = {'embedded', 'isolated', 'fullpage'}

    def __init__(self, text, filename=None, argumentstring=None):
        super(Example, self).__init__(text=text, filename=filename, argumentstring=argumentstring)

    @property
    def type(self):
        """
        Get the value of the ``type`` option, or ``"embedded"`` if it is not specified.

        Raises:
            pythonkss.exceptions.ArgumentStringError: If the specified ``type``
                option is not in :obj:`~.Example.supported_types`.
        """
        exampletype = self.argumentdict.get('type', 'embedded')
        if exampletype not in self.supported_types:
            raise exceptions.ArgumentStringError('Unsupported example type: {}'.format(exampletype))
        return exampletype

    @property
    def height(self):
        """
        Get the value of the ``height`` option, or ``None`` if it is not specified.
        """
        return self.argumentdict.get('height', None)
