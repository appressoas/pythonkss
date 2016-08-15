from __future__ import unicode_literals

import yaml
from yaml.error import YAMLError

from pythonkss import markdownformatter
from pythonkss import exceptions


class MarkupExampleBase(object):
    """
    Represents a Example part in a :class:`pythonkss.section.Section`
    (the part that starts with ``Example:``).

    .. attribute:: text

        The markup text (the lines below ``Example:``)

    .. attribute:: filename

        The filename. Can be ``None``.

    .. attribute:: title

        The title for the markup block. Can be ``None``.

    .. attribute:: argumentstring

        The argument string.
    """
    def __init__(self, text, filename=None, syntax=None, title=None, argumentstring=None):
        """

        Args:
            text: The text in the lines below ``Example:``.
            filename: The filename that the markup belongs to. Optional.
            argumentstring: An optional argumentstring in the following format:
                ``[(<arguments>)] [<title>]``, where (<arguments>) are arguments
                on formatted as ``key: value``. The only argument supported
                by this class is ``syntax``, but the subclasses for supported
                arguments.
        """
        self.text = text
        self.filename = filename
        self.argumentstring = None
        self.argumentdict = {}
        self.title = ''
        if argumentstring:
            self.argumentstring = argumentstring.strip()
            self.title, self.argumentdict = self._parse_argumentstring()
        else:
            self.argumentstring = argumentstring

    def _parse_argumentstring(self):
        argumentdict = {}
        if self.argumentstring.startswith('{') and '}' in self.argumentstring:
            arguments, title = self.argumentstring.split('}', 1)
            arguments = arguments[1:]
            title = title.strip()
            try:
                argumentdict = yaml.load('{{{arguments}}}'.format(arguments=arguments))
            except YAMLError as e:
                raise exceptions.ArgumentStringError('Invalid argument string: {!r}. {}'.format(
                    self.argumentstring, e))
        else:
            title = self.argumentstring

        return title, argumentdict

    @property
    def syntax(self):
        """
        Get syntax identifier.

        Returns:
            str: Returns :attr:`.syntax` if set, falling back to "html".
        """
        return self.argumentdict.get('syntax', 'html')

    @property
    def html(self):
        """
        Format the text as HTML with syntax hilighting.
        """
        markdowntext = '```{syntax}\n{text}\n```'.format(
            syntax=self.syntax,
            text=self.text)
        return markdownformatter.MarkdownFormatter.to_html(markdowntext=markdowntext)
