import os
import unittest

import pythonkss


class ParseTestCase(unittest.TestCase):

    def setUp(self):
        fixtures = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.scss = pythonkss.Parser(os.path.join(fixtures, 'scss'))
        self.less = pythonkss.Parser(os.path.join(fixtures, 'less'))
        self.sass = pythonkss.Parser(os.path.join(fixtures, 'sass'))
        self.css = pythonkss.Parser(os.path.join(fixtures, 'css'))
        self.css_with_variables = pythonkss.Parser(
            os.path.join(fixtures, 'css'),
            variables={
                '$test-variable': '"The test variable value"'
            }
        )
        self.na = pythonkss.Parser(os.path.join(fixtures, 'scss'), extensions=['.css'])
        self.multiple = pythonkss.Parser(os.path.join(fixtures, 'scss'), os.path.join(fixtures, 'less'))

    def test_parses_kss_comments_in_scss(self):
        self.assertEqual(self.scss.get_section_by_reference('2.1.1').title, 'Your standard form button.')

    def test_parses_kss_comments_in_less(self):
        self.assertEqual(self.less.get_section_by_reference('2.1.1').title, 'Your standard form button.')

    def test_parses_kss_multi_line_comments_in_sass(self):
        self.assertEqual(self.sass.get_section_by_reference('2.1.1').title, 'Your standard form button.')

    def test_parses_kss_single_line_comments_in_sass(self):
        self.assertEqual(self.sass.get_section_by_reference('2.2.1').title,
                         'A button suitable for giving stars to someone.')

    def test_parses_kss_comments_in_css(self):
        self.assertEqual(self.css.get_section_by_reference('2.1.1').title, 'Your standard form button.')

    def test_parses_nested_scss_documents(self):
        self.assertEqual(self.scss.get_section_by_reference('3.0.0').title, 'Your standard form element.')
        self.assertEqual(self.scss.get_section_by_reference('3.0.1').title, 'Your standard text input box.')

    def test_parses_nested_less_documents(self):
        self.assertEqual(self.less.get_section_by_reference('3.0.0').title, 'Your standard form element.')
        self.assertEqual(self.less.get_section_by_reference('3.0.1').title, 'Your standard text input box.')

    def test_parses_nested_sass_documents(self):
        self.assertEqual(self.sass.get_section_by_reference('3.0.0').title, 'Your standard form element.')
        self.assertEqual(self.sass.get_section_by_reference('3.0.1').title, 'Your standard text input box.')

    def test_parse_returns_dictionary_of_sections(self):
        self.assertEqual(len(self.css.sections), 3)

    def test_parse_multiple_paths(self):
        self.assertEqual(len(self.multiple.sections), 6)

    def test_parse_ext_mismatch(self):
        self.assertDictEqual(self.na.sections, {})

    def test_get_sections(self):
        sections = self.css.get_sections()
        references = set(section.reference for section in sections)
        self.assertEqual(references, {'1', '2.1.1', '2.2.1'})

    def test_get_sections_referenceprefix(self):
        sections = list(self.css.get_sections(referenceprefix='2'))
        references = set(section.reference for section in sections)
        self.assertEqual(references, {'2.1.1', '2.2.1'})

    def test_iter_sorted_sections(self):
        sorted_sections = list(self.css.iter_sorted_sections())
        self.assertEqual(sorted_sections[0].reference, '1')
        self.assertEqual(sorted_sections[1].reference, '2.1.1')
        self.assertEqual(sorted_sections[2].reference, '2.2.1')

    def test_iter_sorted_sections_referenceprefix(self):
        sorted_sections = list(self.css.iter_sorted_sections(referenceprefix='2'))
        self.assertEqual(sorted_sections[0].reference, '2.1.1')
        self.assertEqual(sorted_sections[1].reference, '2.2.1')

    def test_variable(self):
        description = self.css_with_variables.get_section_by_reference('2.2.1').description
        self.assertEqual('The value of $test-variable: "The test variable value"', description)
