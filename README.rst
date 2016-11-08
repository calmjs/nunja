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


Troubleshooting
---------------

Using ``--bundle-map-method=empty`` with the ``rjs`` tool will result in
this error message

.. code:: sh

    $ calmjs rjs nunja --bundle-map-method=empty

    Tracing dependencies for: /tmp/nunja/nunja.testing.js
    Error: TypeError: Cannot read property 'normalize' of undefined
        at Object.<anonymous> (/tmp/nunja/node_modules/requirejs/bin/r.js:1221:35)

This is caused by the provided templates done through the ``text``
plugin which is not being provided.  To work around this, either ensure
the templates registries are NOT provided, or apply the optional advice
nunja[slim] to precompile the template and not include the raw source
template strings.  Alternatively, if the ``text`` module is to be made
available through a different artifact bundle for a given deployment,
the ``--empty`` flag may be employed to stub out the missing modules
completely, i.e.:

.. code:: sh

    $ calmjs rjs --empty nunja --bundle-map-method=empty


License
-------

The project is licensed under the GPLv2.
