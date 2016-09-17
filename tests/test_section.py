import unittest

from pythonkss.section import Section


class SectionSanityTestCase(unittest.TestCase):

    def setUp(self):
        comment = """
Form Button

Your standard form button.

:hover    - Highlights when hovering.
:disabled - Dims the button when disabled.
.primary  - Indicates button
            is the primary action.
.smaller  - A smaller button

    This is part of the description, not a multiline modifier.

Markup:
    <a href="#" class="button$modifier_class">Button</a><a href="#"[ class="$modifier_class"]?>Button</a>

Styleguide 2.1.1
        """
        self.section = Section(comment.strip(), 'example.css')

    def test_parses_the_title(self):
        self.assertEqual(self.section.title, 'Form Button')

    def test_parses_the_description(self):
        self.assertEqual(self.section.description,
                         ('Your standard form button.\n\n\n'
                          '    This is part of the description, '
                          'not a multiline modifier.'))

    def test_parses_the_modifiers(self):
        self.assertEqual(len(self.section.modifiers), 4)

    def test_parses_modifier_names(self):
        self.assertEqual(self.section.modifiers[0].name, ':hover')

    def test_parses_modifier_descriptions(self):
        self.assertEqual(self.section.modifiers[0].description, 'Highlights when hovering.')

    def test_parses_modifier_multiline_descriptions(self):
        self.assertEqual(self.section.modifiers[2].description,
                         'Indicates button is the primary action.')

    def test_parses_the_markup(self):
        expected = '<a href="#" class="button">Button</a><a href="#">Button</a>'
        self.assertEqual(self.section.markups[0].text, expected)

    def test_parses_the_styleguide_reference(self):
        self.assertEqual(self.section.reference, '2.1.1')

    def test_handles_when_no_reference(self):
        section = Section('Styleguide', 'example.css')
        self.assertEqual(section.reference, None)


class SectionTestCase(unittest.TestCase):
    def __make_section(self, title='The title',
                       description=None,
                       modifiers=None,
                       markup=None,
                       reference='1.1'):
        commentparts = [title]
        for part in description, modifiers, markup:
            if part:
                commentparts.append(part)
        if reference:
            commentparts.append('Styleguide {}'.format(reference))
        comment = '\n\n'.join(commentparts)
        return Section(comment, filename='example.css')

    def test_description_html_from_markdown(self):
        self.assertEqual(
            '<p>\n   Hello\n  </p>',
            self.__make_section(description='Hello').description_html)

    def test_reference_numeric_only(self):
        self.assertEqual(
            '1.3.25',
            self.__make_section(reference='1.3.25').reference)

    def test_reference_text(self):
        self.assertEqual(
            '1.3.hello2',
            self.__make_section(reference='1.3.hello2').reference)

    def test_reference_explicit_sortkey(self):
        self.assertEqual(
            '1.3.hello',
            self.__make_section(reference='1.3.10:hello').reference)

    def test_reference_segment_list_numeric_only(self):
        self.assertEqual(
            ['1', '3', '25'],
            self.__make_section(reference='1.3.25').reference_segment_list)

    def test_reference_segment_list_text(self):
        self.assertEqual(
            ['1', '3', 'hello2'],
            self.__make_section(reference='1.3.hello2').reference_segment_list)

    def test_reference_segment_list_explicit_sortkey(self):
        self.assertEqual(
            ['1', '3', 'hello'],
            self.__make_section(reference='1.3.10:hello').reference_segment_list)

    def test_raw_reference_segment_list_numeric_only(self):
        self.assertEqual(
            ['1', '3', '25'],
            self.__make_section(reference='1.3.25').raw_reference_segment_list)

    def test_raw_reference_segment_list_text(self):
        self.assertEqual(
            ['1', '3', 'hello2'],
            self.__make_section(reference='1.3.hello2').raw_reference_segment_list)

    def test_raw_reference_segment_list_explicit_sortkey(self):
        self.assertEqual(
            ['1', '3', '10:hello'],
            self.__make_section(reference='1.3.10:hello').raw_reference_segment_list)

    def test_sortkey_numeric_only(self):
        self.assertEqual(
            25,
            self.__make_section(reference='1.3.25').sortkey)

    def test_sortkey_text(self):
        self.assertEqual(
            None,
            self.__make_section(reference='1.3.hello2').sortkey)

    def test_sortkey_explicit(self):
        self.assertEqual(
            10,
            self.__make_section(reference='1.3.10:hello').sortkey)
