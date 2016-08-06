from pythonkss import markdownformatter
from pythonkss.markup import Markup


class Modifier(object):
    """
    Represents a modifier in a :class:`pythonkss.section.Section`.
    """

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.markup = None

    @property
    def class_name(self):
        """
        Get the class name.
        """
        return self.name.replace('.', ' ').replace(':', ' pseudo-class-').strip()

    def add_markup(self, markup):
        self.markup = Markup(
            text=markup.replace('$modifier_class', ' %s' % self.class_name))

    @property
    def description_html(self):
        """
        Get the description as HTML formatted using
        :class:`pythonkss.markdownformatter.MarkdownFormatter`.
        """
        return markdownformatter.MarkdownFormatter.to_html(markdowntext=self.description)
