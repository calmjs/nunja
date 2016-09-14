# -*- coding: utf-8 -*-
import unittest
from types import ModuleType
from pkg_resources import EntryPoint

from nunja.indexer import generate_modname_nunja


class IndexerTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_indexer_generate_modname_nunja_template(self):
        entry_point = EntryPoint.parse(
            'example.package.mold = example.package:mold')
        module = ModuleType('example.package')

        modname_nunja_template, modname_nunja_script = generate_modname_nunja(
            entry_point, module)
        # the names provided will be the fragments based on actual file
        # name, with the final filename extension stripped.
        name = modname_nunja_template(
            ['example', 'package', 'mold', 'table', 'template'])

        self.assertEqual(name, 'text!example.package.mold/table/template')

    def test_indexer_generate_modname_nunja_script(self):
        entry_point = EntryPoint.parse(
            'example.package.mold = example.package:mold')
        module = ModuleType('example.package')

        modname_nunja_template, modname_nunja_script = generate_modname_nunja(
            entry_point, module)
        # the names provided will be the fragments based on actual file
        # name, with the final filename extension stripped.
        name = modname_nunja_script(
            ['example', 'package', 'mold', 'table', 'index'])

        self.assertEqual(name, 'example.package.mold/table/index')

    # mismatch tests are where the name defined is not similar to the
    # actual module import name.

    def test_indexer_generate_modname_nunja_template_mismatch(self):
        entry_point = EntryPoint.parse('example.mold = example.package:mold')
        module = ModuleType('example.package')

        modname_nunja_template, modname_nunja_script = generate_modname_nunja(
            entry_point, module)
        # the names provided will be the fragments based on actual file
        # name, with the final filename extension stripped.
        name = modname_nunja_template(
            ['example', 'package', 'mold', 'table', 'template'])

        self.assertEqual(name, 'text!example.mold/table/template')

    def test_indexer_generate_modname_nunja_script_mismatch(self):
        entry_point = EntryPoint.parse('example.mold = example.package:mold')
        module = ModuleType('example.package')

        modname_nunja_template, modname_nunja_script = generate_modname_nunja(
            entry_point, module)
        # the names provided will be the fragments based on actual file
        # name, with the final filename extension stripped.
        name = modname_nunja_script(
            ['example', 'package', 'mold', 'table', 'index'])

        self.assertEqual(name, 'example.mold/table/index')
