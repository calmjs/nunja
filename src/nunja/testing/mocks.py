# -*- coding: utf-8 -*-
import sys
from os import mkdir
from os import utime
from os.path import join
from types import ModuleType

from pkg_resources import resource_filename
from pkg_resources import Distribution

from calmjs.testing.mocks import WorkingSet
from calmjs.testing.utils import mkdtemp_singleton


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


def setup_tmp_module(testcase_inst, modname='tmp'):
    def cleanup():
        sys.modules.pop(modname)

    testcase_inst.addCleanup(cleanup)
    # inject the dummy tmp module to sidestep the import error.
    sys.modules[modname] = ModuleType(modname)


def setup_tmp_mold_templates(testcase_inst):
    """
    Set up a temporary module, with a default mold and templates.

    Return a 3-tuple, including an instance of MoldRegistry, and the
    path to main_template and sub_template
    """

    from nunja import indexer

    tempdir = mkdtemp_singleton(testcase_inst)

    # using nunja.testing as a surrogate module
    working_set = WorkingSet({
        'nunja.mold': [
            'tmp = tmp:root',
            '_core_ = nunja:_core_',
        ]},
        dist=Distribution(project_name='nunjatesting')
    )
    module_map = {
        'tmp': tempdir,
    }
    setup_tmp_module(testcase_inst)

    # Stub out the indexer so it would pick up our dummy files here
    stub_mod_mock_resources_filename(testcase_inst, indexer, module_map)

    moldroot = join(tempdir, 'root')
    mkdir(moldroot)

    molddir = join(moldroot, 'mold')
    mkdir(molddir)

    main_template = join(molddir, 'template.nja')
    sub_template = join(molddir, 'sub.nja')
    bad_template = join(moldroot, 'bad.nja')

    with open(main_template, 'w') as fd:
        fd.write('<div>{% include "tmp/mold/sub.nja" %}</div>')

    with open(sub_template, 'w') as fd:
        fd.write('<span>{{ data }}</span>')

    # for path traversal attack tests.
    with open(bad_template, 'w') as fd:
        fd.write('<bad>{{ data }}</bad>')

    # force the mtime to some time way in the past
    utime(sub_template, (-1, 1))

    return working_set, main_template, sub_template


def setup_tmp_mold_templates_registry(testcase_inst):
    from nunja.registry import MoldRegistry

    (working_set, main_template,
        sub_template) = setup_tmp_mold_templates(testcase_inst)

    registry = MoldRegistry('nunja.mold', _working_set=working_set)
    return registry, main_template, sub_template
