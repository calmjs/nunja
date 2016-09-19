# -*- coding: utf-8 -*-
from os.path import join
from pkg_resources import resource_filename


class MockResourceManager(object):
    """
    Creating a dummy resource manager would have worked if it doesn't
    implicitly rely on the global working_set.

    Note this manager effectively layers on top of the real one.
    """

    def __init__(self, module_path_map):
        self.module_path_map = module_path_map

    def resource_filename(self, module_name, path):
        result = self.module_path_map.get(module_name)
        if result is None:
            return resource_filename(module_name, path)
        return join(result, path) if path else result


def stub_mod_mock_resources_filename(testcase_inst, module, module_path_map):
    """
    Replace the resource_filename function for the target module
    """

    def restore():
        module.resource_filename = original

    testcase_inst.addCleanup(restore)

    manager = MockResourceManager(module_path_map)
    original, module.resource_filename = (
        module.resource_filename, manager.resource_filename)

