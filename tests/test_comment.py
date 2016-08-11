# -*- coding: utf-8 -*-

import os
import unittest

from pythonkss import comment


class CommentMethodTestCase(unittest.TestCase):

    def test_detects_single_line_comment_syntax(self):
        self.assertTrue(comment.is_single_line_comment('// yuuuuup'))
        self.assertFalse(comment.is_single_line_comment('nooooope'))

    def test_detects_start_of_multi_line_comment_syntax(self):
        self.assertTrue(comment.is_multi_line_comment_start('/* yuuuuup'))
        self.assertFalse(comment.is_multi_line_comment_start('nooooope'))

    def test_detects_end_of_multi_line_comment_syntax(self):
        self.assertTrue(comment.is_multi_line_comment_end(" yuuuuup */"))
        self.assertFalse(comment.is_multi_line_comment_end("nooooope"))

    def test_parses_the_single_line_comment_syntax(self):
        self.assertEqual(comment.parse_single_line("// yuuuuup"), ' yuuuuup')

    def test_parses_the_multi_line_comment_syntax(self):
        self.assertEqual(comment.parse_multi_line('/* yuuuup */'), ' yuuuup')


class CommentParserTestCase(unittest.TestCase):

    def setUp(self):
        text = os.path.join(os.path.dirname(__file__), 'fixtures', 'comments.txt')
        self.comments = comment.CommentParser(text).blocks

    def test_finds_single_line_comment_styles(self):
        expected = """
This comment block has comment identifiers on every line.

Fun fact: this is Kyle's favorite comment syntax!
        """
        self.assertTrue(expected.strip() in self.comments)

    def test_finds_block_style_comment_styles(self):
        expected = """
This comment block is a block-style comment syntax.

There's only two identifier across multiple lines.
        """
        self.assertTrue(expected.strip() in self.comments)

        expected = """
This is another common multi-line comment style.

It has stars at the begining of every line.
        """
        self.assertTrue(expected.strip() in self.comments)

    def test_handles_mixed_styles(self):
        expected = "This comment has a /* comment */ identifier inside of it!"
        self.assertTrue(expected.strip() in self.comments)

        expected = 'Look at my //cool// comment art!'
        self.assertTrue(expected.strip() in self.comments)

    def test_handles_indented_comments(self):
        self.assertTrue('Indented single-line comment.' in self.comments)
        self.assertTrue('Indented block comment.' in self.comments)

    def test_handles_indented_example(self):
        expected = """
This comment has a indented example
<div>
    <div></div>
</div>
        """
        self.assertTrue(expected.strip() in self.comments)

    def test_handles_unicode_in_comments(self):
        self.assertTrue(u'Hello, 世界' in self.comments)


class CommentVariablesTestCase(unittest.TestCase):
    def test_no_variables(self):
        filepath = os.path.join(os.path.dirname(__file__), 'fixtures', 'variables_in_comments.txt')
        comments = comment.CommentParser(filepath).blocks
        self.assertEqual('The value of $test-variable is {% $test-variable %}.', comments[0])

    def test_with_variables(self):
        filepath = os.path.join(os.path.dirname(__file__), 'fixtures', 'variables_in_comments.txt')
        comments = comment.CommentParser(filepath, variablemap={
            '{% $test-variable %}': '10px',
            '{% another-variable %}': 'hello'
        }).blocks
        self.assertEqual('The value of $test-variable is 10px.', comments[0])
        self.assertEqual('Another variable: hello.', comments[1])
