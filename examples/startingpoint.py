from __future__ import print_function
import sys

import pythonkss


def generate_styleguide(*paths):
    """
    A good starting point for generating your styleguide.
    Uses all the important features, but prints to stdout.
    """
    parser = pythonkss.Parser(*paths)
    for node in parser.as_tree().sorted_all_descendants_flat():
        print()
        print('*' * 70)
        if node.section:
            print(node.section.reference, node.section.title)
        else:
            print(node.reference, node.segment_text.capitalize())
        print('*' * 70)
        print()

        if not node.section:
            continue

        for modifier in node.section.modifiers:
            print('-- ', modifier.name, ' --')
            print(modifier.description_html)

        if node.section.description:
            print()
            print(node.section.description_html)

        if node.section.has_examples() or node.section.has_markups():
            print()
            print('Usage:')
            print('=' * 70)
            print()
            for example in node.section.examples:
                if example.title:
                    print('-- ', example.title, ' --')
                print(example.html)
            for markup in node.section.markups:
                if markup.title:
                    print('-- ', markup.title, ' --')
                print(markup.html)


if __name__ == '__main__':
    paths = sys.argv[1:]
    if len(paths) == 0:
        print('You may want to try this with the "examples/examplestyles/" directory as input.')
        print()
        raise SystemExit('Usage: {} <styledirectory1> [styledirectory2] [..styledirectoryN]'.format(sys.argv[0]))
    generate_styleguide(*paths)
