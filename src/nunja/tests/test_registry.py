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
        working_set = mocks.WorkingSet({
            'nunja.mold': [
                'nunja.testing.molds = nunja.testing:mold',
            ]},
            dist=Distribution(project_name='nunjatesting')
        )

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

        # XXX TODO figure out how to represent these as molds
        # 'nunja.testing.molds/include_by_name',
        # 'nunja.testing.molds/include_by_value',
        # 'nunja.testing.molds/itemlist',


# TODO migrate crufty old bits to above
