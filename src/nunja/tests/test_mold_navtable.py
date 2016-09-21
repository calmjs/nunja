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
        result = self.engine.execute('nunja.molds/navtable', data={
            'css': {},
        })

        self.assertEqual(
            result,
            '<div data-nunja="nunja.molds/navtable">\n'
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

    def test_basic_navtable_contents(self):
        data = model.DummyTableData([
            ['@id', ''],
            ['name', 'Name'],
            ['desc', 'Description'],
            ['size', 'Size'],
        ], [
            ['http://example.com/documents', 'documents', 'My Documents', '9'],
            ['http://example.com/pictures', 'pictures', 'My Pictures', '43'],
            ['http://example.com/videos', 'videos', 'My Videos', '0'],
            ['', 'file', 'A File', '100'],
        ])

        result = self.engine.execute(
            'nunja.molds/navtable', data=data.to_jsonable())

        self.assertEqual(
            result,
            '<div data-nunja="nunja.molds/navtable">\n'
            '<table class="">\n'
            '  <thead>\n'
            '    <tr class="">\n'
            '    <td>Name</td><td>Description</td><td>Size</td>\n'
            '    </tr>\n'
            '  </thead>\n'
            '  <tbody>\n'
            '    <tr class="">\n'
            '      <td><a href="http://example.com/documents">documents</a>'
            '</td><td>My Documents</td><td>9</td>\n'
            '    </tr><tr class="">\n'
            '      <td><a href="http://example.com/pictures">pictures</a>'
            '</td><td>My Pictures</td><td>43</td>\n'
            '    </tr><tr class="">\n'
            '      <td><a href="http://example.com/videos">videos</a>'
            '</td><td>My Videos</td><td>0</td>\n'
            '    </tr><tr class="">\n'
            '      <td>file</td><td>A File</td><td>100</td>\n'
            '    </tr>\n'
            '  </tbody>\n'
            '</table>\n'
            '</div>'
        )
