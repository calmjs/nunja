# -*- coding: utf-8 -*-
import unittest
from os.path import join
from types import ModuleType
from pkg_resources import EntryPoint

from calmjs.utils import pretty_logging
from calmjs.testing.mocks import StringIO
from nunja.indexer import generate_modname_nunja

from nunja import testing


class IndexerTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_indexer_generate_modname_nunja_modpath_pkg_resources(self):
        entry_point = EntryPoint.parse('nunja.testing = nunja.testing:mold')

        nunja_template, nunja_script, nunja_modpath = generate_modname_nunja(
            entry_point, testing, fext='.tmpl')
        # the names provided will be the fragments based on actual file
        # name, with the final filename extension stripped.
        name = nunja_modpath(testing, entry_point)
        self.assertEqual(len(name), 1)
        # make it easier to see wrong than just not True
        self.assertIn(join('nunja', 'testing', 'mold'), name[0])
        self.assertTrue(name[0].endswith(join('nunja', 'testing', 'mold')))

        # Please do note the next comment, this causes an apparent
        # mismatch with expected behavior however is within the design
        # of how such mapping is supposed to work.

    def test_indexer_generate_modname_nunja_template(self):
        entry_point = EntryPoint.parse(
            'example.package.mold = example.package:mold')
        module = ModuleType('example.package')

        nunja_template, nunja_script, nunja_modpath = generate_modname_nunja(
            entry_point, module, fext='.tmpl')
        # the names provided will be the fragments based on actual file
        # name, with the final filename extension stripped.  However a
        # **HUGE** difference is that the customized modpath function
        # (nunja_modpath_pkg_resources) ALSO provides the first attrs
        # (the name) to the module_base_path, thus generating the
        # mapping that effectively truncates out the attrs.

        # Normally this is what might be expected
        # ['example', 'package', 'mold', 'table', 'template'])

        # However, this is what we actually get
        name = nunja_template(
            ['example', 'package', 'table', 'template'])

        # Naturally, this applies for the rest of the functions.

        self.assertEqual(name, 'text!example.package.mold/table/template.tmpl')

    def test_indexer_generate_modname_nunja_script(self):
        entry_point = EntryPoint.parse(
            'example.package.mold = example.package:mold')
        module = ModuleType('example.package')

        nunja_template, nunja_script, nunja_modpath = generate_modname_nunja(
            entry_point, module, fext='.tmpl')
        # the names provided will be the fragments based on actual file
        # name, with the final filename extension stripped.
        name = nunja_script(
            ['example', 'package', 'table', 'index'])

        self.assertEqual(name, 'example.package.mold/table/index')

    # altname tests are where the name defined is not similar to the
    # actual module import name (alternative name)

    def test_indexer_generate_modname_nunja_template_altname(self):
        entry_point = EntryPoint.parse('example.mold = example.package:mold')
        module = ModuleType('example.package')

        nunja_template, nunja_script, nunja_modpath = generate_modname_nunja(
            entry_point, module, fext='.tmpl')
        # the names provided will be the fragments based on actual file
        # name, with the final filename extension stripped.
        name = nunja_template(
            ['example', 'package', 'table', 'template'])

        self.assertEqual(name, 'text!example.mold/table/template.tmpl')

    def test_indexer_generate_modname_nunja_script_altname(self):
        entry_point = EntryPoint.parse('example.mold = example.package:mold')
        module = ModuleType('example.package')

        nunja_template, nunja_script, nunja_modpath = generate_modname_nunja(
            entry_point, module, fext='.tmpl')
        # the names provided will be the fragments based on actual file
        # name, with the final filename extension stripped.
        name = nunja_script(
            ['example', 'package', 'table', 'index'])

        self.assertEqual(name, 'example.mold/table/index')

    def test_indexer_modpath_pkg_resources_entry_point_fail_import(self):
        entry_point = EntryPoint.parse('example.mold = example.package:mold')
        module = ModuleType('example.package')

        nunja_template, nunja_script, nunja_modpath = generate_modname_nunja(
            entry_point, module, fext='.tmpl')

        with pretty_logging(logger='nunja', stream=StringIO()) as stream:
            nunja_modpath(None, None)

        msg = stream.getvalue()
        self.assertIn("does not appear to be a valid module", msg)
        self.assertIn("got unexpected entrypoint", msg)

    def test_indexer_modpath_pkg_resources_entry_point_mismatch_module(self):
        entry_point = EntryPoint.parse('example.mold = example.package1:mold')
        module1 = ModuleType('example.package1')
        module2 = ModuleType('example.package2')

        nunja_template, nunja_script, nunja_modpath = generate_modname_nunja(
            entry_point, module1, fext='.tmpl')

        with pretty_logging(logger='nunja', stream=StringIO()) as stream:
            nunja_modpath(module2, entry_point)

        msg = stream.getvalue()
        self.assertIn(
            "modpath function created for <module 'example.package1'", msg)
        self.assertIn(
            "got unexpected module <module 'example.package2'", msg)
        self.assertIn(
            "could not be located as a module", msg)

    def test_indexer_modpath_pkg_resources_entry_point_not_import(self):
        entry_point = EntryPoint.parse('nunjatest = nunja.testing:mold')

        nunja_template, nunja_script, nunja_modpath = generate_modname_nunja(
            entry_point, testing, fext='.tmpl')

        with pretty_logging(logger='nunja', stream=StringIO()) as stream:
            path = nunja_modpath(testing, entry_point)

        msg = stream.getvalue()
        self.assertEqual(msg, '')
        self.assertTrue(path[0].endswith(join('nunja', 'testing', 'mold')))
