# -*- coding: utf-8 -*-
import unittest
from os import remove

from jinja2 import TemplateNotFound

from nunja.engine import Engine
from nunja.testing import mocks


class EngineTestCase(unittest.TestCase):
    """
    The core engine test case for testing the integration with the
    loader.
    """

    def setUp(self):
        (registry, self.main_template,
            self.sub_template) = mocks.setup_tmp_mold_templates_registry(self)
        self.engine = Engine(registry)

    def test_unregistered_not_found(self):
        with self.assertRaises(TemplateNotFound):
            self.engine.load_template('some/id')

    def test_base_loading(self):
        template = self.engine.load_template('tmp/mold/sub.nja')
        result = template.render(data='Hello World!')
        self.assertEqual(result, '<span>Hello World!</span>')

    def test_nested_loading(self):
        template = self.engine.load_template('tmp/mold/template.nja')
        result = template.render(data='Hello World!')
        self.assertEqual(result, '<div><span>Hello World!</span></div>')

    def test_base_auto_reload(self):
        template = self.engine.load_template('tmp/mold/template.nja')
        result = template.render(data='Hello World!')
        self.assertEqual(result, '<div><span>Hello World!</span></div>')

        with open(self.sub_template, 'w') as fd:
            fd.write('<div>{{ data }}</div>')

        result = template.render(data='Hello World!')
        self.assertEqual(result, '<div><div>Hello World!</div></div>')
        remove(self.sub_template)

        with self.assertRaises(TemplateNotFound):
            # as that was removed
            template.render(data='Hello World!')

    def test_fetch_path_basic(self):
        tmpl = self.engine.fetch_path('tmp/mold/template.nja')
        self.assertEqual('<div>{% include "tmp/mold/sub.nja" %}</div>', tmpl)

    def test_fetch_path_itemlist(self):
        registry = mocks.setup_testing_mold_templates_registry(self)
        engine = Engine(registry)
        tmpl = engine.fetch_path('nunja.testing.mold/itemlist/template.nja')
        self.assertTrue(tmpl.startswith('<ul'))
        script = engine.fetch_path('nunja.testing.mold/itemlist/index.js')
        self.assertTrue(script.startswith('define(['))
