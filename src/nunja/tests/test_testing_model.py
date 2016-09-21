# -*- coding: utf-8 -*-
import unittest

from nunja.testing import model


class TestDummyTableData(unittest.TestCase):
    """
    These tests here serves as active documentation on what a given
    endpoint will need to generate.
    """

    def test_basic(self):
        data = model.DummyTableData([], [])
        self.assertEqual(data.to_jsonable(), {
            'active_columns': [],
            'column_map': {},
            'data': [],
            'css': {},
        })

    def test_one(self):
        data = model.DummyTableData([
            ['ID', 'Identifier']
        ], [
            ['1'],
            ['2'],
        ])
        self.assertEqual(data.to_jsonable(), {
            'active_columns': ['ID'],
            'column_map': {
                'ID': 'Identifier',
            },
            'data': [
                {'ID': '1'},
                {'ID': '2'},
            ],
            'css': {},
        })

    def test_two(self):
        data = model.DummyTableData([
            ['id', 'Id'],
            ['name', 'Given Name'],
        ], [
            ['1', 'John Smith'],
            ['2', 'Eve Adams'],
        ])
        self.assertEqual(data.to_jsonable(), {
            'active_columns': ['id', 'name'],
            'column_map': {
                'id': 'Id',
                'name': 'Given Name',
            },
            'data': [
                {'id': '1', 'name': 'John Smith'},
                {'id': '2', 'name': 'Eve Adams'},
            ],
            'css': {},
        })

    def test_jsonld_id(self):
        data = model.DummyTableData([
            ['@id', ''],  # human readable can be empty
            ['name', 'Name'],
            ['desc', 'Description'],
            ['size', 'Size'],
        ], [
            ['http://example.com/documents', 'documents', 'My Documents', '9'],
            ['http://example.com/pictures', 'pictures', 'My Pictures', '43'],
            ['http://example.com/videos', 'videos', 'My Videos', '0'],
        ])
        self.assertEqual(data.to_jsonable(), {
            'active_columns': ['name', 'desc', 'size'],
            'column_map': {
                'name': 'Name',
                'desc': 'Description',
                'size': 'Size',
            },
            'data': [
                {'size': '9', '@id': 'http://example.com/documents',
                    'name': 'documents', 'desc': 'My Documents'},
                {'size': '43', '@id': 'http://example.com/pictures',
                    'name': 'pictures', 'desc': 'My Pictures'},
                {'size': '0', '@id': 'http://example.com/videos',
                    'name': 'videos', 'desc': 'My Videos'},
            ],
            'css': {},
        })
