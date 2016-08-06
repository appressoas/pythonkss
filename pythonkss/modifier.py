from pythonkss import markdownformatter
from pythonkss.markup import Markup


class Modifier(object):

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.markup = None

    @property
    def class_name(self):
        return self.name.replace('.', ' ').replace(':', ' pseudo-class-').strip()

    def add_markup(self, markup):
        self.markup = Markup(
            text=markup.replace('$modifier_class', ' %s' % self.class_name))

    @property
    def description_html(self):
        return markdownformatter.MarkdownFormatter.to_html(markdowntext=self.description)
