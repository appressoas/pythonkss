# PythonKSS - Knyle Style Sheets

PythonKSS is a Python implementation of [KSS](http://warpspire.com/kss). KSS attempts to provide a
methodology for writing maintainable, documented CSS within a team.

It was originally forked from https://github.com/seanbrant/pykss to be more 
compatible with https://www.npmjs.com/package/kss, but we have:

- added a lot more features, such as:
    - markdown support in description
    - code hilighting with Pygments
    - made API docs
    - made it possible to use not only numbers in the reference, and just give hints
      about preferred sort order.
    - added an new ``Example:`` block that supports much more features than the
      ``Markup:`` block supported. Since it does not work in the same manner as
      ``Markup:`` without some options, we decided to give it a new name.
    - made the first line of a styleguide section the title for the section.
    - and much more
- made some changes, such as:
    - removed the ``Markup:`` block in favor of a more powerful ``Example:`` block.
    - removed the modifier support. We did not really see the need for
      this with markdown support and ``Example:`` after trying it out on a fairly complex
      project. We are open to re-adding modifier support or something that covers the same
      need.
    - stricter parser - block content is indented - everything else is title or description.


## Docs
http://pythonkss.readthedocs.io/
