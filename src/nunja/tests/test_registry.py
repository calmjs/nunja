import unittest

import json
import sys
from os.path import join
from os.path import dirname
from pkg_resources import EntryPoint
from pkg_resources import Distribution

import calmjs.registry

from nunja.registry import _remap
from nunja.registry import MoldRegistry
from nunja.registry import DEFAULT_REGISTRY_NAME

from calmjs.testing import mocks
from calmjs.utils import pretty_logging
import nunja.testing

basic_tmpl_str = '<span>{{ value }}</span>\n'


class RegistryUtilsTestCase(unittest.TestCase):

    def test_remap_basic(self):
        values = {
            'abc/123': 'this/is/abc',
            'def/456': 'this/is/def',
        }
        locals_ = {
            'item_map': values,
            'item_keys': sorted(values.keys()),
        }

        # start with the "last" item.
        related = {}
        _remap(locals_, 'item', 'def', related)
        self.assertEqual(related['def/456'], 'this/is/def')
        _remap(locals_, 'item', 'abc', related)
        self.assertEqual(related['abc/123'], 'this/is/abc')

    def test_remap_skipping(self):
        values = {
            'abc/123': 'this/is/abc',
            'def/456': 'this/is/def',
            'def/432': 'this/is/def',
            'def/932': 'this/is/def',
            'ghi/234': 'this/is/ghi',
            'jkl/234': 'this/is/jkl',
        }
        locals_ = {
            'item_map': values,
            'item_keys': sorted(values.keys()),
        }

        # start with the "last" item.
        related = {}
        _remap(locals_, 'item', 'ghi', related)
        # the first key should be popped
        self.assertNotIn('jkl/234', locals_['item_keys'])
        self.assertEqual(related['ghi/234'], 'this/is/ghi')
        _remap(locals_, 'item', 'def', related)
        self.assertEqual(related['def/932'], 'this/is/def')
        self.assertEqual(related['def/432'], 'this/is/def')
        self.assertEqual(related['def/456'], 'this/is/def')


class MoldRegistryTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_registered_to_root_registry(self):
        registry = calmjs.registry.get('nunja.mold')
        self.assertTrue(isinstance(registry, MoldRegistry))
        self.assertIs(registry, calmjs.registry.get(DEFAULT_REGISTRY_NAME))

    def test_registry_load_working_set(self):
        # do note these mocking sets are for the registry; actual
        # filenames is not overridden (uses pkg_resources directly)
        working_set = mocks.WorkingSet({
            'nunja.mold': [
                'nunja.testing.molds = nunja.testing:mold',
            ]},
            dist=Distribution(project_name='nunjatesting')
        )

        with pretty_logging(logger='nunja', stream=mocks.StringIO()) as stream:
            registry = MoldRegistry('nunja.mold', _working_set=working_set)

        records = registry.get_records_for_package('nunjatesting')
        keys = [
            'nunja.testing.molds/include_by_name/index',
            'nunja.testing.molds/include_by_value/index',
            'nunja.testing.molds/itemlist/index',
            'text!nunja.testing.molds/basic/template.nja',
            'text!nunja.testing.molds/include_by_name/empty.nja',
            'text!nunja.testing.molds/include_by_name/template.nja',
            'text!nunja.testing.molds/include_by_value/template.nja',
            'text!nunja.testing.molds/itemlist/template.nja',
        ]

        self.assertEqual(sorted(records.keys()), keys)

        self.assertIn('5 templates', stream.getvalue())
        self.assertIn('3 scripts', stream.getvalue())
        self.assertIn('4 molds extracted', stream.getvalue())

        # select directly by mold_id through get_record
        self.assertEqual(
            sorted(registry.get_record('nunja.testing.molds/basic').keys()),
            ['text!nunja.testing.molds/basic/template.nja'],
        )
        self.assertEqual(
            sorted(registry.get_record('nunja.testing.molds/itemlist').keys()),
            [
                'nunja.testing.molds/itemlist/index',
                'text!nunja.testing.molds/itemlist/template.nja',
            ],
        )
        self.assertEqual(
            sorted(registry.get_record(
                'nunja.testing.molds/include_by_name').keys()),
            [
                'nunja.testing.molds/include_by_name/index',
                'text!nunja.testing.molds/include_by_name/empty.nja',
                'text!nunja.testing.molds/include_by_name/template.nja',
            ],
        )

    def test_registry_load_entry_point_missing_attrs(self):
        working_set = mocks.WorkingSet({
            'nunja.mold': [
                'nunja.testing.mold1 = nunja.testing',
                'nunja.testing.mold2 = nunja:testing.mold',
            ]},
            dist=Distribution(project_name='nunjatesting', version='0.0')
        )

        with pretty_logging(logger='nunja', stream=mocks.StringIO()) as stream:
            registry = MoldRegistry('nunja.mold', _working_set=working_set)

        msg = stream.getvalue()
        self.assertIn(
            "entry_point 'nunja.testing.mold1 = nunja.testing' "
            "from package 'nunjatesting 0.0' incompatible ",
            msg,
        )
        self.assertIn(
            "entry_point 'nunja.testing.mold2 = nunja:testing.mold' "
            "from package 'nunjatesting 0.0' incompatible ",
            msg,
        )

        records = registry.get_records_for_package('nunjatesting')
        self.assertEqual(records, {})


# TODO migrate crufty old bits to above
