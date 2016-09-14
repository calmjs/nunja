import unittest


def make_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(
        'nunja.tests', pattern='test_*.py')
    return test_suite
