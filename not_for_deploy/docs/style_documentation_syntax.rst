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

    Example: (followed by the lines of the example)

    Styleguide <reference - I.E.: components.button>
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

    Example:
        <button class="button">Default</button>
        <button class="button button--primary">Primary</button>
        <button class="button button--secondary">Secondary</button>

    Styleguide components.button
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



Reference
=========
The reference must be a unique dotted path for the section.

Examples:

.. code-block:: scss

    /* Buttons

    Styleguide buttons
    */

    /* Primary button

    Styleguide buttons.primary
    */


    /* Default button

    Styleguide buttons.button
    */


Sorting sections
----------------
The styleguide is grouped and sorted by the reference. If you want to
override how a reference is sorted, you can use ``<number>:<text>`` for
the last part of the reference. E.g.:

.. code-block:: scss

    /* Buttons

    Styleguide 1:buttons
    */

    /* Primary button

    Styleguide buttons.1:primary
    */


    /* Default button

    Styleguide buttons.2:button
    */


    /* Danger button
    I do not care how this is sorted. It will be sorted after
    the explicitly sorted "Primary button" and "Default button".

    Styleguide buttons.danger
    */

The ``<number>:<text>`` format can only be used for the last part of the reference path.

.. note:: You can, alternatively, use numbers instead of text for the reference path,
    but this is a pain to keep organized in any larger project.


Example
=======
An Earkup section is a (typically syntax hilighted) example. You start an Example part
with ``Example:`` and any line indented by at least 2 spaces below that line is part of the markup.

Simple example::

    Example:
        <button class="default">Default button</button>
        <button class="primary">Primary button</button>


Example syntax
--------------

The default syntax is ``html``, but you can override this with ``Example: (<syntax>)``
where ``<syntax>`` is the same as for :ref:`Markdown code blocks <markdown_code_blocks>`.
Example using scss syntax::

    Example: {syntax: scss}
        .my-primary-button {
            @include button-primary();
        }

You can also provide a title for your markup parts. This is mostly useful when you
have multiple markup parts in a section::

    Example: In HTML
        <button class="default">Default button</button>
        <button class="primary">Primary button</button>

    Example: {syntax: scss} Using the mixins
        .my-primary-button {
            @include button-primary();
            color: red;
        }


Example type
------------

You can specify a *type* to indicate the type of your example. We recommend
that all styleguide renderers using pythonkss at least support:

- ``embedded`` (the default): Embed the preview HTML within the styleguide.
- ``isolated``: Isolated preview typically opened in a new window or iframe
  with the example code in the body of the page.

.. - ``fullpage``: Just like ``isolated``, but the example code is assumed to be a full HTML page.


Using the isolated type::

    Example: {type: isolated} An isolated example

        <nav class="mainnavigation">
            <a href="#">Page 1</a>
            <a href="#">Page 2</a>
        </nav>


Code-only examples and preview-only examples
--------------------------------------------
You can control if your example should be shown as:

- A preview.
- Code only (normally syntax hilighted)
- Both (the default when syntax is ``html``)

The preview and code options in action::

    Example: With both preview and (syntax hilighted) code

        <h1>This is the primary heading</h1>

    Example: {preview: false} Without preview - code only

        <h1>This is the primary heading</h1>

    Example: {code: false} Without code - preview only

        <h1>This is the primary heading</h1>

    Example: {syntax: css} Syntax other than HTML - preview is off by default!

        .stuff {
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
