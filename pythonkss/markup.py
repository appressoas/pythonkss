from __future__ import unicode_literals

from pythonkss.markupexamplebase import MarkupExampleBase


class Markup(MarkupExampleBase):
    """
    Represents a Markup part in a :class:`pythonkss.section.Section`
    (the part that starts with ``Markup:``).

    .. attribute:: text

        The markup text (the lines below ``Markup:``)

    .. attribute:: filename

        The filename. Can be ``None``.

    .. attribute:: title

        The title for the markup block. Can be ``None``.
    """
    def __init__(self, text, filename=None, argumentstring=None):
        super(Markup, self).__init__(text=text, filename=filename, argumentstring=argumentstring)
