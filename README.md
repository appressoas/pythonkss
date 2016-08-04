# PythonKSS - Knyle Style Sheets

PythonKSS is a Python implementation of [KSS](http://warpspire.com/kss). KSS attempts to provide a
methodology for writing maintainable, documented CSS within a team.

It was originally forked from to be more compatible with https://www.npmjs.com/package/kss.

The official [page](http://warpspire.com/kss/) provide a good introduction to KSS.


Installing
----------

```
$ pip install pythonkss
```


Usage
-----

```python
>>> import pythonkss
>>>
>>> styleguide = pythonkss.Parser('static/css')
>>>
>>> styleguide.section('2.1.1')
<pythonkss.section.Section object at 0x10c1d1190>
>>>
>>> styleguide.section('2.1.1').description
'A button suitable for giving stars to someone.'
>>>
>>> styleguide.section('2.1.1').modifiers[0]
<pythonkss.modifier.Modifier object at 0x10c1d1290>
>>>
>>> styleguide.section('2.1.1').modifiers[0].name
':hover'
>>>
>>> styleguide.section('2.1.1').modifiers[0].class_name
'pseudo-class-hover'
>>>
>>> styleguide.section('2.1.1').modifiers[0].description
'Subtle hover highlight'
```
