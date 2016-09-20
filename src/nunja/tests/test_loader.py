# -*- coding: utf-8 -*-
import unittest
from os.path import exists
from os.path import join
from os.path import dirname
from os.path import pardir
from os import remove

from jinja2 import TemplateNotFound

from nunja.loader import NunjaLoader

from nunja.testing.mocks import setup_tmp_mold_templates_registry


class LoaderTestCase(unittest.TestCase):
    """
    There is a bit of coupling with registry as that is the only
    implementation that we intend to support at the moment.
    """

    def setUp(self):
        (self.registry, self.main_template,
            self.sub_template) = setup_tmp_mold_templates_registry(self)

    def test_loader_core(self):
        loader = NunjaLoader(self.registry)
        src, p, checker = loader.get_source(None, 'tmp/mold/sub.nja')
        self.assertEqual(src, '<span>{{ data }}</span>')

    def test_loader_core_notfound_checks(self):
        loader = NunjaLoader(self.registry)
        with self.assertRaises(TemplateNotFound):
            loader.get_source(None, 'tmp/mold/nothere.nja')

        # Especially won't work with raw filesystem paths.
        with self.assertRaises(TemplateNotFound):
            loader.get_source(None, self.sub_template)

    def test_loader_reload_checker(self):
        loader = NunjaLoader(self.registry)
        src, p, checker = loader.get_source(None, 'tmp/mold/sub.nja')
        remove(self.sub_template)
        self.assertFalse(checker())

    def test_loader_traversal_safety(self):
        loader = NunjaLoader(self.registry)

        self.assertTrue(exists(
            join(dirname(self.main_template), pardir, 'bad.nja')))

        with self.assertRaises(TemplateNotFound):
            loader.get_source(None, 'tmp/mold/../bad.nja')

    def test_dev_addition_template_existing_mold(self):
        # Test that the support for late addition is enabled.
        loader = NunjaLoader(self.registry)
        new_nja = join(dirname(self.main_template), 'new.nja')

        # Does not current exists
        self.assertFalse(exists(new_nja))
        with self.assertRaises(TemplateNotFound):
            loader.get_source(None, 'tmp/mold/new.nja')

        tmpl = '<span>static</span>'
        with open(new_nja, 'w') as fd:
            fd.write(tmpl)

        src, p, checker = loader.get_source(None, 'tmp/mold/new.nja')
        self.assertEqual(src, tmpl)
