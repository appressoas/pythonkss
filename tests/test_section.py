import unittest

from pythonkss.section import Section, NotSectionError, InvalidMergeSectionTypeError, InvalidMergeNotSameReferenceError


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

    def test_parse_type_extend_after_title_sanity(self):
        comment = 'Title: The title\nStyleguideExtendAfter a.b'
        section = Section(comment)
        section.parse()
        self.assertEqual(section.reference, 'a.b')
        self.assertEqual(section.title, 'The title')
        self.assertEqual(section.description, '')

    def test_parse_type_extend_after_title_empty(self):
        comment = 'Title: \nStyleguideExtendAfter a.b'
        section = Section(comment)
        section.parse()
        self.assertEqual(section.reference, 'a.b')
        self.assertEqual(section.title, None)
        self.assertEqual(section.description, 'Title:')

    def test_parse_type_extend_after_title_and_description(self):
        comment = 'Title: The title\nThe description\nStyleguideExtendAfter a.b'
        section = Section(comment)
        section.parse()
        self.assertEqual(section.reference, 'a.b')
        self.assertEqual(section.title, 'The title')
        self.assertEqual(section.description, 'The description')

    def test_parse_type_extend_before_title_sanity(self):
        comment = 'Title: The title\nStyleguideExtendBefore a.b'
        section = Section(comment)
        section.parse()
        self.assertEqual(section.reference, 'a.b')
        self.assertEqual(section.title, 'The title')
        self.assertEqual(section.description, '')

    def test_parse_type_extend_before_title_empty(self):
        comment = 'Title: \nStyleguideExtendBefore a.b'
        section = Section(comment)
        section.parse()
        self.assertEqual(section.reference, 'a.b')
        self.assertEqual(section.title, None)
        self.assertEqual(section.description, 'Title:')

    def test_parse_type_extend_before_title_and_description(self):
        comment = 'Title: The title\nThe description\nStyleguideExtendBefore a.b'
        section = Section(comment)
        section.parse()
        self.assertEqual(section.reference, 'a.b')
        self.assertEqual(section.title, 'The title')
        self.assertEqual(section.description, 'The description')

    def test_parse_type_replace_title_sanity(self):
        comment = 'The title\nStyleguideReplace a.b'
        section = Section(comment)
        section.parse()
        self.assertEqual(section.reference, 'a.b')
        self.assertEqual(section.title, 'The title')
        self.assertEqual(section.description, '')

    def test_parse_type_replace_title_empty(self):
        comment = 'StyleguideReplace a.b'
        section = Section(comment)
        with self.assertRaises(NotSectionError):
            section.parse()

    def test_parse_type_replace_title_and_description(self):
        comment = 'The title\nThe description\nStyleguideReplace a.b'
        section = Section(comment)
        section.parse()
        self.assertEqual(section.reference, 'a.b')
        self.assertEqual(section.title, 'The title')
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

    def test_merge_into_section_invalid_section_type(self):
        target = Section('The title\nStyleguide a.b')
        target.parse()
        source = Section('Title suffix\nStyleguide a.b')
        source.parse()
        with self.assertRaises(InvalidMergeSectionTypeError):
            source.merge_into_section(target_section=target)

    def test_merge_into_section_not_same_reference(self):
        target = Section('The title\n'
                         'Styleguide a.b')
        target.parse()
        source = Section('Title suffix\n'
                         'StyleguideExtendBefore a.c')
        source.parse()
        with self.assertRaises(InvalidMergeNotSameReferenceError):
            source.merge_into_section(target_section=target)

    def test_merge_into_section_after_sanity(self):
        target = Section('The title\n'
                         'The description\n'
                         'Styleguide a.b')
        target.parse()
        source = Section('Title: Title suffix\n'
                         'Extra description\n'
                         'StyleguideExtendAfter a.b')
        source.parse()
        source.merge_into_section(target_section=target)
        self.assertEqual(target.reference, 'a.b')
        self.assertEqual(target.title, 'The title Title suffix')
        self.assertEqual(target.description,
                         'The description\n\nExtra description')

    def test_merge_into_section_after_no_title(self):
        target = Section('The title\n'
                         'The description\n'
                         'Styleguide a.b')
        target.parse()
        source = Section('Extra description\n'
                         'StyleguideExtendAfter a.b')
        source.parse()
        source.merge_into_section(target_section=target)
        self.assertEqual(target.title, 'The title')
        self.assertEqual(target.description,
                         'The description\n\nExtra description')

    def test_merge_into_section_after_example(self):
        target = Section('The title\n'
                         'Example:\n  <em>example</em>\n'
                         'Styleguide a.b')
        target.parse()
        source = Section('Example:\n  <em>example2</em>\n'
                         'StyleguideExtendAfter a.b')
        source.parse()
        source.merge_into_section(target_section=target)
        self.assertEqual(target.examples[0].text, '<em>example</em>')
        self.assertEqual(target.examples[1].text, '<em>example2</em>')

    def test_merge_into_section_after_multiple_examples(self):
        target = Section('The title\nExample:\n  <em>example</em>\nStyleguide a.b')
        target.parse()
        source = Section('Example:\n  <em>example2</em>\n'
                         'Example:\n  <em>example3</em>\n'
                         'StyleguideExtendAfter a.b')
        source.parse()
        source.merge_into_section(target_section=target)
        self.assertEqual(target.examples[0].text, '<em>example</em>')
        self.assertEqual(target.examples[1].text, '<em>example2</em>')
        self.assertEqual(target.examples[2].text, '<em>example3</em>')

    def test_merge_into_section_before_sanity(self):
        target = Section('The title\n'
                         'The description\n'
                         'Styleguide a.b')
        target.parse()
        source = Section('Title: Title prefix\n'
                         'Extra description\n'
                         'StyleguideExtendBefore a.b')
        source.parse()
        source.merge_into_section(target_section=target)
        self.assertEqual(target.reference, 'a.b')
        self.assertEqual(target.title, 'Title prefix The title')
        self.assertEqual(target.description, 'Extra description\n\nThe description')

    def test_merge_into_section_before_no_title(self):
        target = Section('The title\nThe description\nStyleguide a.b')
        target.parse()
        source = Section('Extra description\nStyleguideExtendBefore a.b')
        source.parse()
        source.merge_into_section(target_section=target)
        self.assertEqual(target.title, 'The title')
        self.assertEqual(target.description, 'Extra description\n\nThe description')

    def test_merge_into_section_before_example(self):
        target = Section('The title\n'
                         'Example:\n  <em>example</em>\n'
                         'Styleguide a.b')
        target.parse()
        source = Section('Example:\n  <em>example2</em>\n'
                         'StyleguideExtendBefore a.b')
        source.parse()
        source.merge_into_section(target_section=target)
        self.assertEqual(target.examples[0].text, '<em>example2</em>')
        self.assertEqual(target.examples[1].text, '<em>example</em>')

    def test_merge_into_section_before_multiple_examples(self):
        target = Section('The title\nExample:\n  <em>example</em>\nStyleguide a.b')
        target.parse()
        source = Section('Example:\n  <em>example2</em>\n'
                         'Example:\n  <em>example3</em>\n'
                         'StyleguideExtendBefore a.b')
        source.parse()
        source.merge_into_section(target_section=target)
        self.assertEqual(target.examples[0].text, '<em>example2</em>')
        self.assertEqual(target.examples[1].text, '<em>example3</em>')
        self.assertEqual(target.examples[2].text, '<em>example</em>')
