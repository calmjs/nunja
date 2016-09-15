import unittest

import json
import sys
from os.path import join
from os.path import dirname
from pkg_resources import EntryPoint
from pkg_resources import Distribution

import calmjs.registry

from nunja.registry import MoldRegistry
from nunja.registry import DEFAULT_REGISTRY_NAME

from calmjs.testing import mocks
from calmjs.utils import pretty_logging
import nunja.testing

basic_tmpl_str = '<span>{{ value }}</span>\n'


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

        # XXX TODO figure out how to represent these as molds
        # 'nunja.testing.molds/include_by_name',
        # 'nunja.testing.molds/include_by_value',
        # 'nunja.testing.molds/itemlist',

    def test_registry_load_entry_point_missing_attrs(self):
        working_set = mocks.WorkingSet({
            'nunja.mold': [
                'nunja.testing.molds = nunja.testing',
            ]},
            dist=Distribution(project_name='nunjatesting')
        )

        with pretty_logging(logger='nunja', stream=mocks.StringIO()) as stream:
            registry = MoldRegistry('nunja.mold', _working_set=working_set)

        records = registry.get_records_for_package('nunjatesting')
        self.assertEqual(records, {})
        self.assertIn('nunjatesting', stream.getvalue())
        self.assertIn('incompatible', stream.getvalue())


# TODO migrate crufty old bits to above
