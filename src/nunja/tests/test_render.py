import unittest

from pkg_resources import Distribution
from jinja2 import TemplateNotFound

from nunja.engine import Engine
from nunja.registry import MoldRegistry

from calmjs.testing import mocks
import nunja.testing


class BaseTestCase(unittest.TestCase):
    """
    Full test, uses the Jinja2 renderer which will then be able to load
    from the custom paths defined for nunja.
    """

    def setUp(self):
        working_set = mocks.WorkingSet({
            'nunja.mold': [
                '_core_ = nunja:_core_',
                'nunja.testing.mold = nunja.testing:mold',
            ]},
            dist=Distribution(project_name='nunja.testing')
        )
        registry = MoldRegistry('nunja.mold', _working_set=working_set)
        self.engine = Engine(registry)

    def test_base_rendering(self):
        result = self.engine.execute(
            'nunja.testing.mold/basic',
            data={'value': 'Hello World!'})

        self.assertEqual(
            result,
            '<div data-nunja="nunja.testing.mold/basic">\n'
            '<span>Hello World!</span>\n'
            '</div>'
        )

    def test_template_retrieval_and_render(self):
        # As this was retrieved directly, none of the "mold" bits are
        # provided by the result.
        result = self.engine.load_template(
            'nunja.testing.mold/basic/template.nja'
        ).render(value='Hello World!')
        self.assertEqual(result, '<span>Hello World!</span>')

    def test_template_retrieval_not_found(self):
        with self.assertRaises(TemplateNotFound):
            result = self.engine.load_template(
                'nunja.testing.mold/basic/no_such_template.nja')

    def test_base_xss_handling(self):
        result = self.engine.execute(
            'nunja.testing.mold/basic',
            data={'value': '<xss>'})

        self.assertEqual(
            result,
            '<div data-nunja="nunja.testing.mold/basic">\n'
            '<span>&lt;xss&gt;</span>\n'
            '</div>'
        )

    def test_manual_include(self):
        data = {
            'list_template': self.engine.load_mold(
                'nunja.testing.mold/itemlist'),
            'itemlists': [['list_1', ['Item 1', 'Item 2']]],
        }

        result = self.engine.execute(
            'nunja.testing.mold/include_by_value', data=data)

        self.assertEqual(
            result,
            '<div data-nunja="nunja.testing.mold/include_by_value">\n'
            '<dl id="">\n\n'
            '  <dt>list_1</dt>\n'
            '  <dd><ul id="list_1">\n\n'
            '  <li>Item 1</li>\n'
            '  <li>Item 2</li>\n'
            '</ul></dd>\n'
            '</dl>\n'
            '</div>'
        )

    def test_manual_include_multilist(self):
        data = {
            'list_template': self.engine.load_mold(
                'nunja.testing.mold/itemlist'),
            'list_id': 'root_id',
            'itemlists': [
                ['list_1', ['Item 1', 'Item 2']],
                ['list_2', ['Item 3', 'Item 4']],
                ['list_3', ['Item 5', 'Item 6']],
            ],
        }

        result = self.engine.execute(
            'nunja.testing.mold/include_by_value', data=data)

        self.assertEqual(
            result,
            '<div data-nunja="nunja.testing.mold/include_by_value">\n'
            '<dl id="root_id">\n\n'
            '  <dt>list_1</dt>\n'
            '  <dd><ul id="list_1">\n\n'
            '  <li>Item 1</li>\n'
            '  <li>Item 2</li>\n'
            '</ul></dd>\n'
            '  <dt>list_2</dt>\n'
            '  <dd><ul id="list_2">\n\n'
            '  <li>Item 3</li>\n'
            '  <li>Item 4</li>\n'
            '</ul></dd>\n'
            '  <dt>list_3</dt>\n'
            '  <dd><ul id="list_3">\n\n'
            '  <li>Item 5</li>\n'
            '  <li>Item 6</li>\n'
            '</ul></dd>\n'
            '</dl>\n'
            '</div>'
        )

    def test_named_include_multilist(self):
        data = {
            'list_id': 'root_id',
            'itemlists': [
                ['list_1', ['Item 1', 'Item 2']],
                ['list_2', ['Item 3', 'Item 4']],
                ['list_3', ['Item 5', 'Item 6']],
            ],
        }

        result = self.engine.execute(
            'nunja.testing.mold/include_by_name', data=data)

        self.assertEqual(
            result,
            '<div data-nunja="nunja.testing.mold/include_by_name">\n'
            '<dl id="root_id">\n\n'
            '  <dt>list_1</dt>\n'
            '  <dd><ul id="list_1">\n\n'
            '  <li>Item 1</li>\n'
            '  <li>Item 2</li>\n'
            '</ul></dd>\n'
            '  <dt>list_2</dt>\n'
            '  <dd><ul id="list_2">\n\n'
            '  <li>Item 3</li>\n'
            '  <li>Item 4</li>\n'
            '</ul></dd>\n'
            '  <dt>list_3</dt>\n'
            '  <dd><ul id="list_3">\n\n'
            '  <li>Item 5</li>\n'
            '  <li>Item 6</li>\n'
            '</ul></dd>\n'
            '</dl>\n'
            '</div>'
        )
