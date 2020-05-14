# -*- coding: utf-8 -*-
import unittest

from os import mkdir
from os.path import exists
from os.path import join
from os.path import sep
from pkg_resources import Distribution
import pkg_resources

import calmjs.registry

from nunja.registry import _remap
from nunja.registry import MoldRegistry
from nunja.registry import JinjaTemplateRegistry
from nunja.registry import DEFAULT_REGISTRY_NAME
from nunja.registry import JINJA_TEMPLATE_REGISTRY_NAME

from calmjs.testing import mocks
from calmjs.testing.utils import mkdtemp_singleton
from calmjs.utils import pretty_logging

from nunja.testing.mocks import setup_tmp_module
from nunja.testing.mocks import setup_tmp_mold_templates
from nunja.testing.mocks import stub_mod_mock_resources_filename

basic_tmpl_str = '<span>{{ value }}</span>\n'


def to_os_sep_path(p):
    # turn the given / separated path into an os specific path
    return sep.join(p.split('/'))


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
            dist=Distribution(project_name='nunjatesting', version='0.0')
        )

        with pretty_logging(logger='nunja', stream=mocks.StringIO()) as stream:
            registry = MoldRegistry('nunja.mold', _working_set=working_set)

        records = registry.get_records_for_package('nunjatesting')
        keys = [
            'nunja.testing.molds/include_by_name/index',
            'nunja.testing.molds/include_by_value/index',
            'nunja.testing.molds/itemlist/index',
            'nunja.testing.molds/noinit/index',
            'nunja.testing.molds/problem/index',
            'text!nunja.testing.molds/basic/template.nja',
            'text!nunja.testing.molds/include_by_name/empty.nja',
            'text!nunja.testing.molds/include_by_name/template.nja',
            'text!nunja.testing.molds/include_by_value/template.nja',
            'text!nunja.testing.molds/itemlist/template.nja',
            'text!nunja.testing.molds/noinit/template.nja',
            'text!nunja.testing.molds/problem/template.nja',
        ]

        self.assertEqual(sorted(records.keys()), keys)

        self.assertIn('7 templates', stream.getvalue())
        self.assertIn('5 scripts', stream.getvalue())
        self.assertIn('generated 6 molds', stream.getvalue())

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

    def test_no_valid_file(self):
        working_set = mocks.WorkingSet({
            'nunja.mold': [
                'nunja.testing.badmold = nunja.testing:badmold',
            ]},
            dist=Distribution(project_name='nunjatesting', version='0.0')
        )

        with pretty_logging(logger='nunja', stream=mocks.StringIO()) as stream:
            registry = MoldRegistry('nunja.mold', _working_set=working_set)

        records = registry.get_records_for_package('nunjatesting')

        self.assertEqual(
            sorted(records.keys()),
            ['text!nunja.testing.badmold/nomold/empty.nja'],
        )

        self.assertIn('1 templates', stream.getvalue())
        self.assertIn('0 scripts', stream.getvalue())
        self.assertIn('generated 0 molds', stream.getvalue())

    def mk_test_registry(self, entry_points=None):
        if entry_points is None:
            entry_points = ['nunja.testing.mold = nunja.testing:mold']

        working_set = mocks.WorkingSet(
            {'nunja.mold': entry_points},
            dist=Distribution(project_name='nunjatesting', version='0.0')
        )
        return MoldRegistry.create(_working_set=working_set)

    def test_registry_mold_id_to_path_registered_entry_point(self):
        registry = self.mk_test_registry()
        # Test that the lookup works.
        path = registry.mold_id_to_path('nunja.testing.mold/basic')
        with open(join(path, 'template.nja'), 'r') as fd:
            contents = fd.read()
        self.assertEqual(contents, basic_tmpl_str)

    def test_registry_mold_id_to_path_unregistered(self):
        registry = self.mk_test_registry([])
        with self.assertRaises(KeyError):
            registry.mold_id_to_path('nunja.testing.mold/basic')

        # default to None
        self.assertIsNone(
            registry.mold_id_to_path('nunja.testing.mold/basic', None))

        # TODO expand this if this eventually support arbitrarily added
        # entry points.

    def test_registry_lookup_path_registered_found(self):
        registry = self.mk_test_registry(['ntm = nunja.testing:mold'])
        path1 = registry.lookup_path('ntm/itemlist/template.nja')

        with open(join(path1), 'r') as fd:
            contents = fd.readline()
        self.assertEqual(
            contents, '<ul{%- if list_id %} id="{{ list_id }}"{% endif -%}>\n')

        # no such path will still be returned
        path2 = registry.lookup_path('ntm/itemlist/nosuchpath.nja')
        self.assertTrue(path2.endswith('nosuchpath.nja'))
        self.assertFalse(exists(path2))

    def test_registry_lookup_path_registered_not_found(self):
        registry = self.mk_test_registry(['ntm = nunja.testing:mold'])

        with self.assertRaises(KeyError):
            registry.lookup_path('ntm/nomold/nosuchpath.nja')

        with self.assertRaises(KeyError):
            registry.lookup_path('nothing_here')

    def test_registry_lookup_path_default(self):
        registry = self.mk_test_registry(['ntm = nunja.testing:mold'])

        result = registry.lookup_path('ntm/nomold/nosuchpath.nja', '<default>')
        self.assertEqual(result, '<default>')

    def test_registry_lookup_block_parent_traversal(self):
        registry = self.mk_test_registry(['ntm = nunja.testing:mold'])

        # Parent traversal blocked.
        with self.assertRaises(KeyError):
            registry.lookup_path('ntm/itemlist/../itemlist/template.nja')

        with self.assertRaises(KeyError):
            registry.lookup_path('ntm/itemlist/../../../registry.py')

        # single dots will be omitted.
        path1 = registry.lookup_path('ntm/itemlist/./template.nja')
        self.assertTrue(path1.endswith(to_os_sep_path(
            'testing/mold/itemlist/template.nja')))

    def test_registry_verify_path_registered(self):
        registry = self.mk_test_registry()
        path = registry.verify_path('nunja.testing.mold/itemlist/template.nja')
        with open(join(path), 'r') as fd:
            contents = fd.readline()
        self.assertEqual(
            contents, '<ul{%- if list_id %} id="{{ list_id }}"{% endif -%}>\n')

    def test_registry_verify_path_unregistered(self):
        registry = self.mk_test_registry(['ntm = nunja.testing:mold'])
        with self.assertRaises(OSError):
            registry.verify_path('ntm/itemlist/nosuchpath.nja')

    def test_registry_verify_traversal(self):
        registry = self.mk_test_registry()
        path = registry.verify_path('nunja.testing.mold/itemlist/template.nja')
        with open(join(path), 'r') as fd:
            contents = fd.readline()
        self.assertEqual(
            contents, '<ul{%- if list_id %} id="{{ list_id }}"{% endif -%}>\n')

    def test_registry_autoreload_base_support(self):
        setup_tmp_module(self)

        entry_points = ['tmp = tmp:mold']

        working_set = mocks.WorkingSet(
            {'nunja.mold': entry_points},
            dist=Distribution(project_name='nunjatesting', version='0.0')
        )

        registry = MoldRegistry.create(
            _working_set=working_set, auto_reload=False)
        self.assertFalse(registry.tracked_entry_points)
        with self.assertRaises(KeyError):
            registry.mold_id_to_path('tmp/new_mold')

        registry = MoldRegistry.create(
            _working_set=working_set, auto_reload=True)
        self.assertEqual(
            str(registry.tracked_entry_points['tmp']), entry_points[0])

    def test_registry_entry_point_to_path(self):
        module_map = {'tmp': mkdtemp_singleton(self)}
        stub_mod_mock_resources_filename(self, pkg_resources, module_map)

        (working_set, main_template,
            sub_template) = setup_tmp_mold_templates(self)
        registry = MoldRegistry.create(
            _working_set=working_set, auto_reload=True)

        # poking internals to test internals
        tmpdir = mkdtemp_singleton(self)
        tmp_entry_point = registry.tracked_entry_points['tmp']
        self.assertEqual(registry._entry_point_to_path(tmp_entry_point), join(
            tmpdir, 'tmp', 'root'))

        # Using the API quickly
        self.assertEqual(registry.mold_id_to_path('tmp/mold'), join(
            tmpdir, 'tmp', 'root', 'mold'))
        self.assertEqual(registry.mold_id_to_path('tmp/new_mold'), join(
            tmpdir, 'tmp', 'root', 'new_mold'))

        with self.assertRaises(KeyError):
            registry.mold_id_to_path('no_such_entry/point')

        with self.assertRaises(KeyError):
            registry.mold_id_to_path('mold_id_not_like_this')

    def test_registry_dynamic_template_addition(self):
        module_map = {'tmp': mkdtemp_singleton(self)}
        stub_mod_mock_resources_filename(self, pkg_resources, module_map)
        (working_set, main_template,
            sub_template) = setup_tmp_mold_templates(self)
        registry = MoldRegistry.create(
            _working_set=working_set, auto_reload=True)

        path = registry.lookup_path('tmp/mold/template.nja')
        self.assertEqual(main_template, path)

        tmpdir = mkdtemp_singleton(self)
        mold_root = join(tmpdir, 'tmp', 'root')
        mold_base = join(mold_root, 'new_mold')
        mkdir(mold_base)
        path = registry.lookup_path('tmp/new_mold/template.nja')
        new_tmpl = join(mold_base, 'template.nja')
        self.assertEqual(path, new_tmpl)

        with self.assertRaises(OSError):
            registry.verify_path('tmp/new_mold/template.nja')

        with open(new_tmpl, 'w') as fd:
            fd.write('<div>New Template</div>')

        self.assertEqual(
            registry.verify_path('tmp/new_mold/template.nja'), new_tmpl)


class JinjaTemplateRegistryTestCase(unittest.TestCase):

    def test_registered_to_root_registry(self):
        registry = calmjs.registry.get('nunja.tmpl')
        self.assertTrue(isinstance(registry, JinjaTemplateRegistry))
        self.assertIs(
            registry, calmjs.registry.get(JINJA_TEMPLATE_REGISTRY_NAME))

    def test_registry_load_working_set(self):
        # do note these mocking sets are for the registry; actual
        # filenames is not overridden (uses pkg_resources directly)
        working_set = mocks.WorkingSet({
            'nunja.tmpl': [
                'nunja.testing.templates = nunja.testing:mold',
            ]},
            dist=Distribution(project_name='nunjatesting', version='0.0')
        )

        with pretty_logging(logger='nunja', stream=mocks.StringIO()) as stream:
            registry = JinjaTemplateRegistry(
                'nunja.tmpl', _working_set=working_set)

        self.assertIn('7 templates', stream.getvalue())
        self.assertNotIn('scripts', stream.getvalue())

        # to prevent the export of names into the calmjs toolchain, the
        # standard record retrieval provides nothing.
        self.assertEqual({}, registry.get_records_for_package('nunjatesting'))
        self.assertEqual(
            registry.get_record('nunja.testing.templates/basic'), {})

        # records are available via an alternative method.
        self.assertEqual([
            'nunja.testing.templates/basic/template.nja',
            'nunja.testing.templates/include_by_name/empty.nja',
            'nunja.testing.templates/include_by_name/template.nja',
            'nunja.testing.templates/include_by_value/template.nja',
            'nunja.testing.templates/itemlist/template.nja',
            'nunja.testing.templates/noinit/template.nja',
            'nunja.testing.templates/problem/template.nja',
        ], sorted(registry.templates.keys()))

    def test_incompat_with_molds(self):
        # molds will fail on this.
        working_set = mocks.WorkingSet({
            'nunja.tmpl': [
                'nunja.testing.templates = nunja.testing:badmold',
            ]},
            dist=Distribution(project_name='nunjatesting', version='0.0')
        )

        with pretty_logging(logger='nunja', stream=mocks.StringIO()) as stream:
            registry = JinjaTemplateRegistry(
                'nunja.tmpl', _working_set=working_set)

        self.assertIn('1 templates', stream.getvalue())
        self.assertEqual(
            sorted(registry.templates.keys()),
            ['nunja.testing.templates/nomold/empty.nja'],
        )

    def mk_test_registry(self, entry_points=None):
        if entry_points is None:
            entry_points = ['nunja.testing.templates = nunja.testing:mold']

        working_set = mocks.WorkingSet(
            {'nunja.tmpl': entry_points},
            dist=Distribution(project_name='nunjatesting', version='0.0')
        )
        return JinjaTemplateRegistry.create(_working_set=working_set)

    def test_registry_mold_id_to_path_registered_entry_point(self):
        registry = self.mk_test_registry()
        # Test that the lookup works.
        path = registry.lookup_path(
            'nunja.testing.templates/basic/template.nja')
        with open(join(path), 'r') as fd:
            contents = fd.read()
        self.assertEqual(contents, basic_tmpl_str)

    def test_registry_mold_id_to_path_unregistered(self):
        registry = self.mk_test_registry([])
        with self.assertRaises(KeyError):
            registry.lookup_path(
                'nunja.testing.templates/basic/template.nja')

    def test_registry_lookup_path_registered_not_found(self):
        registry = self.mk_test_registry(['ntm = nunja.testing:mold'])

        with self.assertRaises(KeyError):
            registry.lookup_path('ntm/template/nosuchpath.nja')

        with self.assertRaises(KeyError):
            registry.lookup_path('nothing_here')

    def test_registry_lookup_path_default(self):
        registry = self.mk_test_registry(['ntm = nunja.testing:mold'])
        result = registry.lookup_path('ntm/nomold/nosuchpath.nja', '<default>')
        self.assertEqual(result, '<default>')

    def test_registry_verify_path_registered(self):
        registry = self.mk_test_registry()
        path = registry.verify_path(
            'nunja.testing.templates/itemlist/template.nja')
        with open(path, 'r') as fd:
            contents = fd.readline()
        self.assertEqual(
            contents, '<ul{%- if list_id %} id="{{ list_id }}"{% endif -%}>\n')

        # fake a registration
        registry.templates['ntm/faketemplate/nosuchpath.nja'] = 'nowhere_path'
        with self.assertRaises(OSError):
            registry.verify_path('ntm/faketemplate/nosuchpath.nja')

    def test_registry_verify_path_unregistered(self):
        registry = self.mk_test_registry(['ntm = nunja.testing:mold'])
        with self.assertRaises(OSError):
            registry.verify_path('ntm/itemlist/nosuchpath.nja')

    def test_registry_verify_traversal(self):
        registry = self.mk_test_registry()
        path = registry.verify_path(
            'nunja.testing.templates/itemlist/template.nja')
        with open(path, 'r') as fd:
            contents = fd.readline()
        self.assertEqual(
            contents, '<ul{%- if list_id %} id="{{ list_id }}"{% endif -%}>\n')

    def test_registry_autoreload_base_support(self):
        # This is just to test the setup of the relevant entry correctly
        # but does not actually deal with the more dynamic functionality
        # that molds offer.
        setup_tmp_module(self)

        entry_points = ['tmp = tmp:mold']

        working_set = mocks.WorkingSet(
            {'nunja.tmpl': entry_points},
            dist=Distribution(project_name='nunjatesting', version='0.0')
        )

        registry = JinjaTemplateRegistry.create(
            _working_set=working_set, auto_reload=False)
        self.assertFalse(registry.tracked_entry_points)
        with self.assertRaises(KeyError):
            registry.lookup_path('tmp/itemlist')

        registry = JinjaTemplateRegistry.create(
            _working_set=working_set, auto_reload=True)
        self.assertEqual(
            str(registry.tracked_entry_points['tmp']), entry_points[0])
