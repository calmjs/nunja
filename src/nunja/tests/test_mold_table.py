# -*- coding: utf-8 -*-
import unittest

from nunja.engine import Engine
from nunja.testing import model


class MoldTableTestCase(unittest.TestCase):

    def setUp(self):
        self.engine = Engine()

    def tearDown(self):
        pass

    def test_null_rendering(self):
        result = self.engine.execute('nunja.molds/table', data={
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

        result = self.engine.execute(
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
