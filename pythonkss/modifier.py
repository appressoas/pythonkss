from pythonkss import markdownformatter
from pythonkss.example import Example


class Modifier(object):

    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.example = None

    @property
    def class_name(self):
        return self.name.replace('.', ' ').replace(':', ' pseudo-class-').strip()

    def add_example(self, example):
        self.example = Example(
            text=example.replace('$modifier_class', ' %s' % self.class_name))

    @property
    def description_html(self):
        return markdownformatter.MarkdownFormatter.to_html(markdowntext=self.description)
