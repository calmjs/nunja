# -*- coding: utf-8 -*-
import unittest
from os.path import join
from types import ModuleType

from nunja.testing import mocks


class MockResourceManagerTestCase(unittest.TestCase):

    def test_simple(self):
        p = join('tmp', 'somewhere')
        module_map = {
            'dummy.module': p,
        }

        manager = mocks.MockResourceManager(module_map)
        self.assertEqual(manager.resource_filename('dummy.module', ''), p)
        self.assertEqual(
            manager.resource_filename('dummy.module', 'dir'),
            join('tmp', 'somewhere', 'dir'),
        )

        with self.assertRaises(ImportError):
            manager.resource_filename('bad.module', '')

        # Note that real modules are still accessible beneath the fake
        # layer
        self.assertIn('_core_', manager.resource_filename('nunja', '_core_'))

    def test_setup_restore(self):
        module = ModuleType('dummymodule')

        def resource_filename(x):
            """dummy"""

        module.resource_filename = resource_filename
        mocks.stub_mod_mock_resources_filename(self, module, {
            'dummy.module': 'dummy',
        })

        self.assertEqual(module.resource_filename('dummy.module', ''), 'dummy')
        self.doCleanups()
        self.assertIs(module.resource_filename, resource_filename)
