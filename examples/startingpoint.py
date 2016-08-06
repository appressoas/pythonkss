from __future__ import print_function
import sys

import pythonkss


def generate_styleguide(*paths):
    """
    A good starting point for generating your styleguide.
    Uses all the important features, but prints to stdout.
    """
    parser = pythonkss.Parser(*paths)
    for section in parser.iter_sorted_sections():
        print()
        print('*' * 70)
        print(section.reference, section.title)
        print('*' * 70)
        print()

        for modifier in section.modifiers:
            print('-- ', modifier.name, ' --')
            print(modifier.description_html)

        if section.description:
            print()
            print(section.description_html)

        if section.has_markups():
            print()
            print('Usage:')
            print('=' * 70)
            print()
            for markup in section.markups:
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
