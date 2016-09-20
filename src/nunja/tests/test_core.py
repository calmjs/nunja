# -*- coding: utf-8 -*-
import unittest
from os.path import join

from nunja.core import engine
from nunja.testing import model


class DefaultCoreEngineTestCase(unittest.TestCase):
    """
    Just directly import and invoke it on common templates and see that
    it works as expected.
    """

    def test_load_resource(self):
        result = engine.lookup_path(
            'nunja.molds/table/template.nja')
        self.assertTrue(result.endswith(
            join('nunja', 'molds', 'table', 'template.nja')))

    def test_null_rendering(self):
        result = engine.execute('nunja.molds/table', data={
            'css': {},
        })

        self.assertEqual(
            result,
            '<div data-nunja="nunja.molds/table">\n'
            '<table class="">\n'
            '  <thead>\n'
            '    <tr class="">\n'
            '    \n'
            '    </tr>\n'
            '  </thead>\n'
            '  <tbody>\n'
            '    \n'
            '  </tbody>\n'
            '</table>\n'
            '</div>'
        )

    def test_basic_table_contents(self):
        data = model.DummyTableData([
            ['id', 'Id'],
            ['name', 'Given Name'],
        ], [
            ['1', 'John Smith'],
            ['2', 'Eve Adams'],
        ])

        result = engine.execute(
            'nunja.molds/table', data=data.to_jsonable())

        self.assertEqual(
            result,
            '<div data-nunja="nunja.molds/table">\n'
            '<table class="">\n'
            '  <thead>\n'
            '    <tr class="">\n'
            '    <td>Id</td><td>Given Name</td>\n'
            '    </tr>\n'
            '  </thead>\n'
            '  <tbody>\n'
            '    <tr class="">\n'
            '      <td>1</td><td>John Smith</td>\n'
            '    </tr><tr class="">\n'
            '      <td>2</td><td>Eve Adams</td>\n'
            '    </tr>\n'
            '  </tbody>\n'
            '</table>\n'
            '</div>'
        )
