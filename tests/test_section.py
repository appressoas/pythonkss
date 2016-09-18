import unittest

from pythonkss.section import Section, NotSectionError


class SectionSanityTestCase(unittest.TestCase):

    def setUp(self):
        comment = """
Form Button

Your standard form button.

    This is also part of the description!.

Example:
    <strong>Hello</strong>

Styleguide 2.1.1
        """
        self.section = Section(comment.strip(), 'example.css')

    def test_parses_the_title(self):
        self.assertEqual(self.section.title, 'Form Button')

    def test_parses_the_description(self):
        self.assertEqual(self.section.description,
                         ('Your standard form button.\n\n'
                          '    This is also part of the description!.'))

    def test_parses_examples(self):
        expected = '<strong>Hello</strong>'
        self.assertEqual(self.section.examples[0].text, expected)

    def test_parses_the_styleguide_reference(self):
        self.assertEqual(self.section.reference, '2.1.1')

    def test_handles_when_no_reference(self):
        section = Section('Styleguide', 'example.css')
        with self.assertRaises(NotSectionError):
            section.parse()


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
        return Section(comment, filepath='example.css')

    def test_parse_reference_supplied(self):
        comment = 'The title\nThe description'
        section = Section(comment)
        section.parse(reference='a.b')
        self.assertEqual(section.reference, 'a.b')
        self.assertEqual(section.title, 'The title')
        self.assertEqual(section.description, 'The description')

    def test_parse_title_supplied(self):
        comment = 'The description\nStyleguide a.b'
        section = Section(comment)
        section.parse(title='Provided title')
        self.assertEqual(section.reference, 'a.b')
        self.assertEqual(section.title, 'Provided title')
        self.assertEqual(section.description, 'The description')

    def test_parse_title_and_reference_supplied_empty_body(self):
        comment = ''
        section = Section(comment)
        section.parse(title='Provided title', reference='a.b')
        self.assertEqual(section.reference, 'a.b')
        self.assertEqual(section.title, 'Provided title')
        self.assertEqual(section.description, '')

    def test_parse_title_and_reference_supplied_with_body(self):
        comment = 'The description'
        section = Section(comment)
        section.parse(title='Provided title', reference='a.b')
        self.assertEqual(section.reference, 'a.b')
        self.assertEqual(section.title, 'Provided title')
        self.assertEqual(section.description, 'The description')

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
