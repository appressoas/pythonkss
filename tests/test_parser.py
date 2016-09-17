import os
import unittest

import pythonkss
from pythonkss.exceptions import DuplicateReferenceError


class ParseTestCase(unittest.TestCase):

    def setUp(self):
        self.fixtures_path = os.path.join(os.path.dirname(__file__), 'fixtures')
        self.scss = pythonkss.Parser(os.path.join(self.fixtures_path, 'scss'))
        self.less = pythonkss.Parser(os.path.join(self.fixtures_path, 'less'))
        self.sass = pythonkss.Parser(os.path.join(self.fixtures_path, 'sass'))
        self.css = pythonkss.Parser(os.path.join(self.fixtures_path, 'css'))
        self.automatic_references = pythonkss.Parser(os.path.join(self.fixtures_path, 'automatic_references'))
        self.css_with_variables = pythonkss.Parser(
            os.path.join(self.fixtures_path, 'css'),
            variables={
                '$test-variable': '"The test variable value"'
            }
        )
        self.na = pythonkss.Parser(os.path.join(self.fixtures_path, 'scss'), extensions=['.css'])
        self.multiple = pythonkss.Parser(os.path.join(self.fixtures_path, 'scss'),
                                         os.path.join(self.fixtures_path, 'less'))

    def test_parses_kss_comments_in_scss(self):
        self.assertEqual(self.scss.get_section_by_reference('2.1.1').title, 'Your standard form button.')

    def test_parses_kss_comments_in_less(self):
        self.assertEqual(self.less.get_section_by_reference('3.1.1').title, 'Your standard form button.')

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
        self.assertEqual(self.less.get_section_by_reference('10.0.0').title, 'Your standard form element.')
        self.assertEqual(self.less.get_section_by_reference('10.0.1').title, 'Your standard text input box.')

    def test_parses_nested_sass_documents(self):
        self.assertEqual(self.sass.get_section_by_reference('3.0.0').title, 'Your standard form element.')
        self.assertEqual(self.sass.get_section_by_reference('3.0.1').title, 'Your standard text input box.')

    def test_parse_returns_dictionary_of_sections(self):
        self.assertEqual(len(self.css.sections), 3)

    def test_parse_multiple_paths(self):
        self.assertEqual(len(self.multiple.sections), 10)

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

    def test_example_sanity(self):
        markup = self.css.get_section_by_reference('1').examples[0]
        self.assertEqual(
            '<div>\n'
            '  An <em>example</em>\n'
            '</div>',
            markup.text)
        self.assertEqual('embedded', markup.type)
        self.assertEqual('html', markup.syntax)
        self.assertEqual('', markup.title)

    def test_example_title(self):
        markup = self.css.get_section_by_reference('1').examples[1]
        self.assertEqual('The example', markup.title)
        self.assertEqual('Example here', markup.text)

    def test_example_type_only(self):
        markup = self.css.get_section_by_reference('1').examples[2]
        self.assertEqual('Standalone example here', markup.text)
        self.assertEqual('isolated', markup.type)
        self.assertEqual('', markup.title)

    def test_example_type_title_and_sytax(self):
        markup = self.css.get_section_by_reference('1').examples[3]
        self.assertEqual('Standalone example with everything', markup.text)
        self.assertEqual('isolated', markup.type)
        self.assertEqual('css', markup.syntax)
        self.assertEqual('A title', markup.title)

    def test_example_notindented(self):
        self.assertEqual(0, len(self.css.get_section_by_reference('2.1.1').examples))

    def test_markup_sanity(self):
        markup = self.css.get_section_by_reference('1').markups[0]
        self.assertEqual(
            '<div>\n'
            '  A <em>markup</em>\n'
            '</div>',
            markup.text)
        self.assertEqual('html', markup.syntax)
        self.assertEqual('', markup.title)

    def test_markup_title(self):
        markup = self.css.get_section_by_reference('1').markups[1]
        self.assertEqual('The title', markup.title)
        self.assertEqual('with title', markup.text)

    def test_markup_syntax(self):
        markup = self.css.get_section_by_reference('1').markups[2]
        self.assertEqual('', markup.title)
        self.assertEqual('css', markup.syntax)
        self.assertEqual('with syntax', markup.text)

    def test_markup_with_title_and_syntax(self):
        markup = self.css.get_section_by_reference('1').markups[3]
        self.assertEqual('The title', markup.title)
        self.assertEqual('with syntax and title', markup.text)
        self.assertEqual('css', markup.syntax)

    def test_markup_notindented(self):
        self.assertEqual(0, len(self.css.get_section_by_reference('2.1.1').markups))

    def test_non_numeric_reference(self):
        sections = self.automatic_references.get_sections()
        references = set(section.reference for section in sections)
        self.assertEqual(references, {
            'buttons',
            'buttons.link',
            'buttons.normal',
            'buttons.fancy',
            'lists.fancy.another-fancy-list',
            'lists.fancy.alternative1',
            'lists.fancy',
            'lists.numbered',
            'lists.fancy.alternative2',
            'lists.bullet',
        })

    def test_non_numeric_reference_sorted(self):
        sections = self.automatic_references.iter_sorted_sections()
        references = [section.reference for section in sections]
        self.assertEqual(references, [
            'buttons',
            'buttons.fancy',
            'buttons.link',
            'buttons.normal',
            'lists.bullet',
            'lists.fancy',
            'lists.fancy.alternative1',
            'lists.fancy.alternative2',
            'lists.fancy.another-fancy-list',
            'lists.numbered',
        ])

    def test_as_tree(self):
        tree = self.automatic_references.as_tree()
        # tree.prettyprint_tree()
        # for treenode in tree.sorted_all_descendants_flat():
        #     print(treenode.prettyformat())
        self.assertEqual(set(tree.children.keys()), {'buttons', 'lists'})
        self.assertEqual(set(tree['buttons'].children.keys()),
                         {'fancy', 'link', 'normal'})
        self.assertEqual(set(tree['lists'].children.keys()),
                         {'bullet', 'fancy', 'numbered'})
        self.assertEqual(set(tree['lists']['fancy'].children.keys()),
                         {'alternative1', 'alternative2', 'another-fancy-list'})

    def test_as_tree_get_node_by_reference(self):
        tree = self.automatic_references.as_tree()
        self.assertEqual(
            tree.get_node_by_reference(reference='lists.numbered').section.title,
            'Numbered lists.')

    def test_as_tree_sorted_children(self):
        tree = self.automatic_references.as_tree()
        # tree.prettyprint_tree()
        self.assertEqual(set(tree.children.keys()), {'buttons', 'lists'})
        self.assertEqual(tree.sorted_children[0].segment_text, 'buttons')
        self.assertEqual(tree.sorted_children[1].segment_text, 'lists')
        self.assertEqual(tree.sorted_children[1].sorted_children[0].segment_text, 'bullet')

    def test_as_tree_sorted_dotted_numbered_path(self):
        tree = self.automatic_references.as_tree()
        self.assertEqual(set(tree.children.keys()), {'buttons', 'lists'})
        self.assertEqual(tree.sorted_children[0].dotted_numbered_path, '1')
        self.assertEqual(tree.sorted_children[1].dotted_numbered_path, '2')
        self.assertEqual(tree.sorted_children[1].sorted_children[2].dotted_numbered_path, '2.3')

    def test_duplicate_references(self):
        parser = pythonkss.Parser(os.path.join(self.fixtures_path, 'duplicate_reference'))
        with self.assertRaises(DuplicateReferenceError):
            parser.parse()
