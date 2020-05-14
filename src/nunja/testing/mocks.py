# -*- coding: utf-8 -*-
import sys
from os import mkdir
from os import utime
from os.path import join
from types import ModuleType

import pkg_resources
from pkg_resources import resource_filename
from pkg_resources import Requirement

from calmjs.testing.utils import mkdtemp_singleton
from calmjs.testing.utils import make_dummy_dist


class MockResourceManager(object):
    """
    Creating a dummy resource manager would have worked if it doesn't
    implicitly rely on the global working_set.

    Note this manager effectively layers on top of the real one.
    """

    def __init__(self, module_path_map):
        self.module_path_map = module_path_map

    def resource_filename(self, package_or_requirement, path):
        module_name = (
            package_or_requirement.name
            if isinstance(package_or_requirement, Requirement) else
            package_or_requirement
        )
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
    testcase_inst.addCleanup(sys.modules.pop, modname)
    # inject the dummy tmp module to sidestep the import error.
    sys.modules[modname] = ModuleType(modname)


def setup_tmp_mold_templates(testcase_inst, namespace='tmp'):
    """
    Set up a temporary module, with a default mold and templates.

    Return a 3-tuple, including an instance of MoldRegistry, and the
    path to main_template and sub_template
    """

    tempdir = mkdtemp_singleton(testcase_inst)

    make_dummy_dist(testcase_inst, (
        ('entry_points.txt', '\n'.join([
            '[nunja.mold]',
            'tmp = tmp:root',
            '[nunja.tmpl]',
            'templates = tmp:root',
        ])),
    ), 'nunjatesting', '0.0')

    working_set = pkg_resources.WorkingSet([
        testcase_inst._calmjs_testing_tmpdir])
    # add the real nunja to provide the data.
    working_set.add(
        pkg_resources.get_distribution('nunja'),
    )

    module_map = {
        'tmp': tempdir,
        'templates': tempdir,
        'nunjatesting': tempdir,
        # include this module, too
        'nunja': resource_filename(Requirement.parse('nunja'), ''),
    }
    setup_tmp_module(testcase_inst)
    # also provide one for nunjatesting
    setup_tmp_module(testcase_inst, 'nunjatesting')

    # Stub out the indexer so it would pick up our dummy files here
    stub_mod_mock_resources_filename(testcase_inst, pkg_resources, module_map)

    module_root = join(tempdir, 'tmp')
    mkdir(module_root)

    moldroot = join(module_root, 'root')
    mkdir(moldroot)

    molddir = join(moldroot, 'mold')
    mkdir(molddir)

    main_template = join(molddir, 'template.nja')
    sub_template = join(molddir, 'sub.nja')
    bad_template = join(moldroot, 'bad.nja')
    filter_dump_template = join(molddir, 'filter_dump.nja')

    with open(main_template, 'w') as fd:
        fd.write('<div>{%% include "%s/mold/sub.nja" %%}</div>' % namespace)

    with open(sub_template, 'w') as fd:
        fd.write('<span>{{ data }}</span>')

    # for path traversal attack tests.
    with open(bad_template, 'w') as fd:
        fd.write('<bad>{{ data }}</bad>')

    # for filter dump test
    with open(filter_dump_template, 'w') as fd:
        fd.write('<div>{{ data | dump }}</div>')

    # force the mtime to some time way in the past
    utime(sub_template, (-1, 1))

    return working_set, main_template, sub_template


def setup_tmp_mold_templates_registry(testcase_inst):
    from nunja.registry import MoldRegistry

    (working_set, main_template,
        sub_template) = setup_tmp_mold_templates(testcase_inst)

    registry = MoldRegistry('nunja.mold', _working_set=working_set)
    return registry, main_template, sub_template


def setup_tmp_jinja_templates_registry(testcase_inst):
    from nunja.registry import JinjaTemplateRegistry

    (working_set, main_template,
        sub_template) = setup_tmp_mold_templates(
            testcase_inst, namespace='templates')

    registry = JinjaTemplateRegistry('nunja.tmpl', _working_set=working_set)
    return registry, main_template, sub_template


def setup_testing_mold_templates_registry(testcase_inst):
    from nunja.registry import MoldRegistry

    # first create a dummy of this package; we need the actual
    # version number
    make_dummy_dist(testcase_inst, ((
        'namespace_packages.txt',
        'nunja\n',
    ), (
        'entry_points.txt',
        '[nunja.mold]\n'
        '_core_ = nunja:_core_\n',
    ),), 'nunja', pkg_resources.get_distribution('nunja').version)

    # then make the one for the testing molds
    make_dummy_dist(testcase_inst, ((
        'namespace_packages.txt',
        'nunja\n',
    ), (
        'entry_points.txt',
        '[nunja.mold]\n'
        'nunja.testing.mold = nunja.testing:mold',
    ),), 'nunja.testing', '0.0.0.dummy')

    working_set = pkg_resources.WorkingSet([
        testcase_inst._calmjs_testing_tmpdir])

    # Ensure that both the "stubbed" modules can be found
    stub_mod_mock_resources_filename(testcase_inst, pkg_resources, {
        'nunja': resource_filename(
            Requirement.parse('nunja'), ''),
        'nunja.testing': resource_filename(
            Requirement.parse('nunja'), ''),
    })

    return MoldRegistry('nunja.mold', _working_set=working_set)
