from __future__ import unicode_literals

from pythonkss import markdownformatter


class Markup(object):
    """
    Represents a Markup part in a :class:`pythonkss.section.Section`
    (the part that starts with ``Markup:``).

    .. attribute:: text

        The markup text (the lines below ``Markup:``)

    .. attribute:: filename

        The filename. Can be ``None``.

    .. attribute:: title

        The title for the markup block. Can be ``None``.

    .. attribute:: syntax

        The syntax for the markup block. Compatible with Pygments syntax hilighter.
        Can be ``None``. You will normally want to use :meth:`.get_syntax`
        instead of this attribute.
    """
    def __init__(self, text, filename=None, syntax=None, title=None, argumentstring=None):
        """

        Args:
            text: The text in the lines below ``Markup:``.
            filename: The filename that the markup belongs to. Optional.
            syntax: The syntax. Optional - if not provided, we try to detect it.
            title: An optional title for the markup block.
            argumentstring: An optional argumentstring in the following format:
                ``[(<syntax>)] [<title>]``. If an argumentstring is provided,
                it overrides anything provided in ``syntax`` and ``title``.
        """
        self.text = text
        self.filename = filename
        self.syntax = syntax
        self.title = title
        self.argumentstring = argumentstring
        if argumentstring:
            self.argumentstring = self.argumentstring.strip()
            self._parse_argumentstring()

    def _parse_argumentstring(self):
        argumentwords = self.argumentstring.split()
        if len(argumentwords) == 0:
            return
        firstword = argumentwords[0]
        if firstword.startswith('(') and firstword.endswith(')'):
            self.syntax = firstword[1:-1]
            titlewords = argumentwords[1:]
        else:
            titlewords = argumentwords
        if titlewords:
            self.title = ' '.join(titlewords)

    def get_syntax(self):
        """
        Get syntax identifier.

        Returns:
            str: Returns :attr:`.syntax` if set, falling back to "html".
        """
        if self.syntax:
            return self.syntax
        else:
            return "html"

    @property
    def html(self):
        """
        Format the text as HTML with syntax hilighting.
        """
        markdowntext = '```{syntax}\n{text}\n```'.format(
            syntax=self.get_syntax(),
            text=self.text)
        return markdownformatter.MarkdownFormatter.to_html(markdowntext=markdowntext)
