nunja
=====

A minimum framework for building reuseable templates for consumption by
Python backends and JavaScript frontends.

Features
--------

``nunja`` is a framework that offers developers a way to build templates
in Jinja that can be easily used from within Python and from the web
browser using JavaScript for the frontend user facing UI components.
This is achieved by making use of Jinja2 templates that can be rendered
using `Jinja2`_ for the Python side, and the `Nunjucks`_ JavaScript
package for the rendering on the client side.

The package leverages upon the |calmjs|_ framework for the management of
access to Jinja templates with associated JavaScript front-end libraries
embedded inside Python packages.

.. _Jinja2: http://jinja.pocoo.org/
.. _Nunjucks: http://mozilla.github.io/nunjucks/
.. |calmjs| replace:: ``calmjs``
.. _calmjs: https://pypi.python.org/pypi/calmjs


Installation
------------

Currently under development, please install by cloning this repository
and run ``python setup.py develop`` within your environment, or follow
your framework's method on installation of development packages.


Contribute
----------

- Issue Tracker: https://github.com/calmjs/nunja/issues
- Source Code: https://github.com/calmjs/nunja


License
-------

The project is licensed under the GPLv2.
