========
Tutorial
========

Mutant converts from one entity defition to set of other formats.
Consider for example, having an application, that stores basic User information.
Let's pretend it's not an abstract user, but Author.
Here is how a Author entity can be described using Mutant YAML format:

.. literalinclude:: ../tests/regression/author/defition.yml
    :linenos:
    :language: yaml

At the command line::
    
    $ mutate author.yml --format=django > author.py

Will produce following django model definition file:

.. literalinclude:: ../tests/regression/author/models.py
    :linenos:
    :language: python

If application is meant to accept new entities, Cerberus validation rules may come in hand:

.. literalinclude:: ../tests/regression/author/cerberus.py
    :linenos:
    :language: python

It's the basics of Mutant - define entity schema once and derive (mutate) it to all forms you need.

===============
Succinct syntax
===============

Mutant accepts (extendable) list of input formats. We'll use YAML for it's human-friendliness.

Let's define blog entity structure. Each `Blog` has `Posts`, that link to `Tags`, which are simple strings:

.. literalinclude:: ../tests/regression/blog/definition.yml
    :linenos:
    :language: yaml

Here we see several features:

    * Inline entity definition - Blog contains Posts;
    * Many-to-Many relations - each Post can have many Tags and each Tag may be linked to many Posts;

Here is Django's models.py:

.. literalinclude:: ../tests/regression/blog/models.py
    :linenos:
    :language: python
