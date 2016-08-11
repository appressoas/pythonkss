import codecs
import re


single_line_re = re.compile(r'^\s*\/\/')
single_line_strip_re = re.compile(r'\s*\/\/')

multi_line_start_re = re.compile(r'^\s*\/\*')
multi_line_end_re = re.compile(r'.*\*\/')
multi_line_start_strip_re = re.compile(r'\s*\/\*')
multi_line_end_strip_re = re.compile(r'\*\/')
multi_line_middle_strip_re = re.compile(r'^(\s*\*+)')

preceding_white_space_re = re.compile(r'^\s*')


def is_single_line_comment(line):
    return single_line_re.match(line) is not None


def is_multi_line_comment_start(line):
    return multi_line_start_re.match(line) is not None


def is_multi_line_comment_end(line):
    if is_single_line_comment(line):
        return False
    return multi_line_end_re.match(line) is not None


def parse_single_line(line):
    return single_line_strip_re.sub('', line).rstrip()


def parse_multi_line(line):
    cleaned = multi_line_start_strip_re.sub('', line)
    return multi_line_end_strip_re.sub('', cleaned).rstrip()


def normalize(lines):
    cleaned = []
    indents = []

    for line in lines:
        line = multi_line_middle_strip_re.sub('', line)
        cleaned.append(line)
        match = preceding_white_space_re.match(line)
        if line:
            indents.append(len(match.group()))

    indent = min(indents) if indents else 0

    return '\n'.join([l[indent:] for l in cleaned]).strip()


class CommentParser(object):
    """
    The comment parser.

    Takes a filename, and parses it into a list of comment blocks.

    Used by :class:`pythonkss.parser.Parser`.
    """

    def __init__(self, filename, variablemap=None):
        """
        Args:
            filename: The path to a style file.
            variablemap (dict): Maps variable substitution strings to values.
                We replace all occurrences of each key with the value in all parsed
                comments.
        """
        self.filename = filename
        self.variablemap = variablemap

    def _apply_variables_to_commentblock(self, commentblock):
        for key, value in self.variablemap.items():
            commentblock = commentblock.replace(key, value)
        return commentblock

    def _apply_variables_to_commentblocks(self, commentblocks):
        commentblocks_with_variables_applied = []
        for commentblock in commentblocks:
            commentblocks_with_variables_applied.append(
                self._apply_variables_to_commentblock(commentblock=commentblock))
        return commentblocks_with_variables_applied

    def parse(self):
        """
        Parse the file and collect comment blocks in a list.

        Returns:
            list: Comment blocks list.
        """
        blocks = []
        current_block = []
        inside_single_line_block = False
        inside_multi_line_block = False

        with codecs.open(self.filename, 'r', 'utf-8') as fileobj:
            for line in fileobj:
                # Parse single-line style
                if is_single_line_comment(line) and not inside_multi_line_block:
                    parsed = parse_single_line(line)

                    if inside_single_line_block:
                        current_block.append(parsed)
                    else:
                        current_block = [parsed]
                        inside_single_line_block = True

                # Prase multi-line style
                if is_multi_line_comment_start(line) or inside_multi_line_block:
                    parsed = parse_multi_line(line)

                    if inside_multi_line_block:
                        current_block.append(parsed)
                    else:
                        current_block = [parsed]
                        inside_multi_line_block = True

                # End a multi-line block if detected
                if is_multi_line_comment_end(line):
                    inside_multi_line_block = False

                # Store the current block if we're done
                if is_single_line_comment(line) is False and inside_multi_line_block is False:
                    if current_block:
                        blocks.append(normalize(current_block))

                    inside_single_line_block = False
                    current_block = []

        if self.variablemap:
            blocks = self._apply_variables_to_commentblocks(commentblocks=blocks)

        return blocks

    @property
    def blocks(self):
        """
        Property that returns a list of comment blocks in the file.

        Parses the file using :meth:`.parse` the first time it is called.
        """
        if not hasattr(self, '_blocks'):
            self._blocks = self.parse()
        return self._blocks
