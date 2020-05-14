# -*- coding: utf-8 -*-
import codecs
import json
from functools import partial

from jinja2 import Environment

from calmjs.registry import get
from nunja.registry import REQ_TMPL_NAME
from nunja.registry import DEFAULT_WRAPPER_NAME
from nunja.registry import DEFAULT_REGISTRY_NAME
from nunja.registry import JINJA_TEMPLATE_REGISTRY_NAME
from nunja.registry import MoldRegistry
from nunja.registry import JinjaTemplateRegistry
from nunja.loader import NunjaLoader


def join(*p):
    # the engine internally use standard path separator characters, the
    # registry is responsible for resolving that to the underlying path
    # on the actual filesystem.
    return '/'.join(p)


class Engine(object):
    """
    Nunja core engine

    This takes a nunja mold registry and is able to execute the
    rendering of templates through nunja identifiers.
    """

    def __init__(
            self,
            registry=DEFAULT_REGISTRY_NAME,
            env=None,
            _wrapper_name=DEFAULT_WRAPPER_NAME,
            _required_template_name=REQ_TMPL_NAME,
            ):
        """
        By default, the engine can be created without arguments which
        will initialize using the default registry.

        It is possible to initialize using other arguments, but this is
        unsupported by the main system, and only useful for certain
        specialized implementations.
        """

        self.registry = (
            registry if isinstance(registry, MoldRegistry) else get(registry))
        self.env = env if env else Environment(
            autoescape=True,
            loader=NunjaLoader(self.registry)
        )
        # this filter is to match with nunjucks version (which calls
        # JSON.stringify in JavaScript); construct a partial which is a
        # callable to json.dumps with default parameters that mimic the
        # JavaScript version of the called function.
        self.env.filters['dump'] = partial(
            json.dumps, sort_keys=True, separators=(',', ':'))
        self._required_template_name = _required_template_name

        self._core_template_ = self.load_mold(_wrapper_name)

    def lookup_path(self, name):
        """
        Lookup the path of the underlying resource identified by name
        through the loader.
        """

        return self.registry.verify_path(name)

    def fetch_path(self, name):
        """
        Fetch contents from the path retrieved via lookup_path.

        No caching will be done.
        """

        with codecs.open(self.lookup_path(name), encoding='utf-8') as fd:
            return fd.read()

    def load_template(self, name):
        """
        Load the template identified by name as found in the registry.
        """

        return self.env.get_template(name)

    def load_mold(self, mold_id):
        """
        Load the default, required template from the mold `mold_id`.

        This is useful to explicitly render something without being
        wrapped by the helper div to avoid the automatic client-side
        execution hooks.  Example:

            engine.load_mold('nunja.molds/html5').render(title='Hello')
        """

        return self.load_template(join(mold_id, self._required_template_name))

    def execute(self, mold_id, data, wrapper_tag='div'):
        """
        Execute a mold `mold_id` by rendering through ``env``.

        This is done using its default template, with data provided as
        dict.

        This returns the wrapped content, which contains the bits that
        the client-side on-load script trigger will execute the index.js
        defined for this mold; if this is not desired, simply call the
        render method instead.
        """

        template = self.load_mold(mold_id)

        kwargs = {}
        kwargs.update(data)
        kwargs['_nunja_data_'] = 'data-nunja="%s"' % mold_id
        kwargs['_template_'] = template
        kwargs['_wrapper_tag_'] = wrapper_tag

        return self._core_template_.render(**kwargs)

    def render(self, mold_id, data):
        """
        Render a mold `mold_id`.  No wrappers are applied as only the
        default template defined for the mold is rendered.
        """

        template = self.load_mold(mold_id)
        return template.render(**data)


class JinjaEngine(object):
    """
    Jinja only engine.

    This takes a jinja template registry for use of loading and
    rendering of templates.
    """

    def __init__(self, registry=JINJA_TEMPLATE_REGISTRY_NAME, env=None):
        """
        By default, the engine can be created without arguments which
        will initialize using the default registry.

        It is possible to initialize using other arguments, but this is
        unsupported by the main system, and only useful for certain
        specialized implementations.
        """

        self.registry = (
            registry
            if isinstance(registry, JinjaTemplateRegistry) else get(registry)
        )
        self.env = env if env else Environment(
            autoescape=True,
            loader=NunjaLoader(self.registry)
        )
        # this filter is to match with nunjucks version (which calls
        # JSON.stringify in JavaScript); construct a partial which is a
        # callable to json.dumps with default parameters that mimic the
        # JavaScript version of the called function.
        self.env.filters['dump'] = partial(
            json.dumps, sort_keys=True, separators=(',', ':'))

    def lookup_path(self, name):
        """
        Lookup the path of the underlying resource identified by name
        through the loader.
        """

        return self.registry.verify_path(name)

    def fetch_path(self, name):
        """
        Fetch contents from the path retrieved via lookup_path.

        No caching will be done.
        """

        with codecs.open(self.lookup_path(name), encoding='utf-8') as fd:
            return fd.read()

    def load_template(self, name):
        """
        Load the template identified by name as found in the registry.
        """

        return self.env.get_template(name)

    def render_template(self, name, data):
        """
        Render a template.
        """

        template = self.load_template(name)
        return template.render(**data)
