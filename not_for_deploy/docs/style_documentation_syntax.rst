#########################
Style documenation syntax
#########################


********************
Documentation format
********************

Format overview
===============

.. code-block:: css

    /*
    title (first line)

    description (multiple lines)

    modifiers (described below)

    Markup: (followed by the lines of the example)

    Styleguide <section - I.E.: 2.3>
    */


A full example (using sass):

.. code-block:: scss


    /*
    Buttons

    We provide several different kinds of buttons:

    - <button class="button">Default</button>
    - <button class="button button--primary">Primary</button>
    - <button class="button button--secondary">Secondary</button>

    .button--primary: A primary button.
    .button--secondary: A secondary button.
    :hover: Something about the hover style.

    Markup:
    <button class="button">Default</button>
    <button class="button button--primary">Primary</button>
    <button class="button button--secondary">Secondary</button>

    Styleguide 1.3
    */
    .button {
        // Your styles here

        &--primary {
            // Your styles here
        }

        &--secondary {
            // Your styles here
        }

        &:hover {
            // Your hover styles here
        }
    }


Title
=====
The first line in the comment is the title.


Description
===========
Description is optional. It is written using Markdown.
See :ref:`markdown_format_details` for details about the markdown format.


Modifier
========
A list of modifiers. Any line starting with ``.`` or ``:`` is parsed as docs for a modifier.

Format specification::

    <.|:><modifier>: <description>


Markup
======
A markup section is a (typically syntax hilighted) example. You start a markup part
with ``Markup:`` and any line below that until another ``Markup:`` or a ``Styleguide:``
line is part of the example.

Simple exmaple:

    Markup:
    <button class="default">Default button</button>
    <button class="primary">Primary button</button>


The default syntax is ``html``, but you can override this with ``Markup: (<syntax>)``
where ``<syntax>`` is the same as for :ref:`Markdown code blocks <markdown_code_blocks>`.
Example using scss syntax::

    Markup: (scss)
    .my-primary-button {
        @include button-primary();
    }

You can also provide a title for your markup parts. This is mostly useful when you
have multiple markup parts in a section::

    Markup: In HTML
    <button class="default">Default button</button>
    <button class="primary">Primary button</button>

    Markup: (scss) Using the mixins
    .my-primary-button {
        @include button-primary();
        color: red;
    }



.. _markdown_format_details:

***************
Markdown format
***************

Paragraphs
==========
Paragraphs are just one or more lines of consecutive text followed by one or more blank lines::

    Maecenas faucibus mollis interdum. Vestibulum id ligula porta felis euismod
    semper. Vestibulum id ligula porta felis euismod semper. Aenean lacinia
    bibendum nulla sed consectetur.

    Donec id elit non mi porta gravida at eget metus. Vestibulum id ligula
    porta felis euismod semper. Praesent commodo cursus magna, vel scelerisque
    nisl consectetur et.


Headings
========
.. code-block:: markdown

    # Largest heading
    ## Second largest heading
    ### Third heading

.. note:: In markdown, these formats normally would result in H1, H2 and H3 tags,
    but our parser converts these to H3, H4 and H5 to make it easier to integrate docs
    in a page. This is because the typical use case is to have a H1 at the top of the
    page and a H2 for each section. This means that any text in a description
    should be H3 to be semantically correct.

    To change this behavior, make a subclass of :class:`pythonkss.markdownformatter.MarkdownFormatter`,
    override :meth:`~pythonkss.markdownformatter.MarkdownFormatter.postprocess_html` and
    use your own MarkdownFormatter subclass with
    :meth:`pythonkss.section.Section.description` as input instead of using
    :meth:`pythonkss.section.Section.description_html`.


Text styles
===========
::

    *Italic text*
    _Italic text_

    **Bold text**
    __Bold text__


Links
=====
::

    Check out [http://example.com](The example website).


Lists
=====

Unordered lists (bullet lists)::

    * This
    * is
    * a
    * test

Ordered lists (numbered lists)::

    1. Item one
    2. Item two
    3. Item three


Definition lists::

    Apple
    :   Pomaceous fruit of plants of the genus Malus in
        the family Rosaceae.

    Orange
    :   The fruit of an evergreen tree of the genus Citrus.


Blockquotes
===========
::

    As stated on the first page of the 101 guide:

    > You have to learn to walk before you can learn how to run



HTML mixed with the Markdown
============================
We do not strip HTML from the markdown, so you can do stuff like this::

    Button style examples:

    - <button>Default button</button>
    - <button class="primary">Primary button</button>

Markdown syntax does not work within a HTML element.


Escape Markdown characters
==========================
If you want to use a special Markdown character in your document (such as
displaying literal asterisks), you can escape the character with a backslash.
Markdown will ignore the character directly after a backslash. Example::

    This is how the \_ (underscore) and \* asterisks characters look.


.. _markdown_code_blocks:

Code blocks
===========
You can easily show syntax highlighted code blocks::

    JavaScript:
    HTML:
    ``` html
    <h1 class="xlarge">Hello world</h1>
    ```

    CSS:
    ``` css
    body {
        background-color: pink;
        color: green;
        font-size: 80px;
    }
    ```

    SASS (scss):
    ```scss
    .button {
        font-size: 14px;
        padding: 6px 12px;
        &--large {
            font-size: 20px;
            padding: 10px 20px;
        }
    }
    ```

    LESS:
    ```less
    .button {
        font-size: 14px;
        padding: 6px 12px;
        &.button--large {
            font-size: 20px;
            padding: 10px 20px;
        }
    }
    ```

    ``` javascript
    function helloworld() {
        var message = "Hello World";
        console.log(message);
    }
    ```

    Not hilighted:
    ```
    for x in 1 through 3
        show x
    ```

We support `all languages supported by Pygments <http://pygments.org/languages/>`_.
The actual name of each language can be found in the `pygments lexer docs <http://pygments.org/docs/lexers/>`_.


***********************
Markdown format details
***********************
We use the [Markdown](http://pythonhosted.org/Markdown/) library with the following extensions:

- [sane_lists](http://pythonhosted.org/Markdown/extensions/sane_lists.html)
- [smart_strong](http://pythonhosted.org/Markdown/extensions/smart_strong.html)
- [def_list](http://pythonhosted.org/Markdown/extensions/definition_lists.html)
- [tables](http://pythonhosted.org/Markdown/extensions/tables.html)
- [smarty](http://pythonhosted.org/Markdown/extensions/smarty.html)
- [codehilite](http://pythonhosted.org/Markdown/extensions/code_hilite.html)
- [fenced_code](http://pythonhosted.org/Markdown/extensions/fenced_code_blocks.html)

Each of these extensions have extensive docs if you want to know more.
