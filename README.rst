==============================
Mutant - Python code generator
==============================

.. image:: https://img.shields.io/travis/peterdemin/mutant.svg
        :target: https://travis-ci.org/peterdemin/mutant

.. image:: https://coveralls.io/repos/github/peterdemin/mutant/badge.svg?branch=master
        :target: https://coveralls.io/github/peterdemin/mutant?branch=master
        :alt: Test Coverage

..
    .. image:: https://img.shields.io/pypi/v/mutant.svg
           :target: https://pypi.python.org/pypi/mutant
    .. image:: https://readthedocs.org/projects/mutant/badge/?version=latest
            :target: https://readthedocs.org/projects/mutant/?badge=latest
            :alt: Documentation Status

Define your data once and auto generate all representations.
Mutant takes YAML formatted schema definition and generates django_ models files, cerberus_ validation rules and so on (currently there is nothing more ;).

Project Status
--------------

I started this project to aid development of Django-based RESTfull APIs.
I found myself defining the same data schema several times - once for database, once for serialization framework, once for cerberus validator, once for Solr and so on.
Every time I made a change to a schema I had to visit all this places often forgetting about one or two.
I thought what if I define my data schema once and then will automatically derive all representation from it.
I liked the idea, but the project finished before I had a chance to apply mutant to it.
So now I don't have enough motivation for contributing much time to this project, but maybe some day I will, or someone else will.

Design
------

Mutant's design is inspired by Flask_. One creates an app, registers parsers, renderers and extensions on it. Then run the generator pipeline and converts input schema definition to one of available representations.
tests directory has some examples of current mutant abilities.

* Free software: ISC license
.. * Documentation: https://mutant.readthedocs.org.

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
.. _django: https://www.djangoproject.com/
.. _cerberus: http://docs.python-cerberus.org/en/stable/
.. _Flask: http://flask.pocoo.org/
