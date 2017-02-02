# -*- coding: utf-8 -*-
import unittest

from os import chdir
from os.path import exists
from os.path import join

from pkg_resources import resource_filename
from pkg_resources import Requirement

from calmjs.exc import AdviceAbort
from calmjs.npm import Driver
from calmjs.toolchain import Spec
from calmjs.toolchain import BEFORE_COMPILE
from calmjs.utils import pretty_logging
from calmjs.utils import which

from nunja.spec import precompile_nunja
from nunja.spec import rjs

from calmjs.testing.mocks import StringIO
from calmjs.testing.utils import mkdtemp
from calmjs.testing.utils import remember_cwd
from calmjs.testing.utils import rmtree
from calmjs.testing.utils import setup_class_install_environment


class SpecTestCase(unittest.TestCase):
    """
    Test out the precompiled template compiler
    """

    def test_missing_keys(self):
        build_dir = mkdtemp(self)
        spec = Spec(
            build_dir=build_dir,
        )

        with self.assertRaises(AdviceAbort) as e:
            precompile_nunja(spec)

        self.assertEqual(
            e.exception.args[0],
            'cannot precompile_nunja if spec is missing keys '
            '{bundle_source_map, plugin_source_map, transpile_source_map}'
        )

    def test_empty(self):
        build_dir = mkdtemp(self)
        spec = Spec(
            build_dir=build_dir,
            plugin_source_map={},
            bundle_source_map={
            },
            transpile_source_map={},
        )

        precompile_nunja(spec)
        self.assertFalse(exists(join(build_dir, '__nunja_precompiled__.js')))
        self.assertNotIn('nunjucks', spec['bundle_source_map'])

    def test_nunjucks(self):
        nunjucks_path = join('node_modules', 'nunjucks', 'nunjucks.js'),
        build_dir = mkdtemp(self)
        spec = Spec(
            build_dir=build_dir,
            plugin_source_map={},
            bundle_source_map={
                'nunjucks': nunjucks_path,
            },
            transpile_source_map={},
        )

        precompile_nunja(spec)
        self.assertFalse(exists(join(build_dir, '__nunja_precompiled__.js')))
        self.assertEqual(spec['bundle_source_map']['nunjucks'], nunjucks_path)

    def test_nunjucks_slim(self):
        nunjucks_path = join('node_modules', 'nunjucks', 'nunjucks.js')
        nunjucks_slim = join('node_modules', 'nunjucks', 'nunjucks-slim.js')
        build_dir = mkdtemp(self)
        spec = Spec(
            build_dir=build_dir,
            plugin_source_map={},
            bundle_source_map={
                'nunjucks': nunjucks_path,
            },
            transpile_source_map={},
        )

        precompile_nunja(spec, slim=True)
        self.assertFalse(exists(join(build_dir, '__nunja_precompiled__.js')))
        self.assertEqual(spec['bundle_source_map']['nunjucks'], nunjucks_slim)

    def test_nunjucks_slim_empty(self):
        nunjucks_path = 'empty:'
        build_dir = mkdtemp(self)
        spec = Spec(
            build_dir=build_dir,
            plugin_source_map={},
            bundle_source_map={
                'nunjucks': nunjucks_path,
            },
            transpile_source_map={},
        )

        precompile_nunja(spec, slim=True)
        self.assertEqual(spec['bundle_source_map']['nunjucks'], 'empty:')

    def test_stubbed_empty(self):
        build_dir = mkdtemp(self)
        spec = Spec(
            build_dir=build_dir,
            plugin_source_map={
                'text!demo/template.nja': 'empty:',
            },
            bundle_source_map={
            },
            transpile_source_map={},
        )

        with pretty_logging('nunja', stream=StringIO()) as stream:
            precompile_nunja(spec)

        self.assertNotIn('failed', stream.getvalue())
        self.assertFalse(exists(join(build_dir, '__nunja_precompiled__.js')))
        self.assertNotIn('nunjucks', spec['bundle_source_map'])


@unittest.skipIf(which('npm') is None, 'npm not found.')
class SpecIntegrationTestCase(unittest.TestCase):
    """
    Actually do some real template precompilation.
    """

    @classmethod
    def setUpClass(cls):
        # nosetest will still execute setUpClass, so the test condition
        # will need to be checked here also.
        if which('npm') is None:  # pragma: no cover
            return
        setup_class_install_environment(
            cls, Driver, ['nunja'], production=True)

    @classmethod
    def tearDownClass(cls):
        # Ditto, as per above.
        if which('npm') is None:  # pragma: no cover
            return
        rmtree(cls._cls_tmpdir)

    def test_core_compiled(self):
        remember_cwd(self)
        chdir(self._env_root)

        build_dir = mkdtemp(self)
        src_template = resource_filename(Requirement.parse('nunja'), join(
            'nunja', '_core_', '_default_wrapper_', 'template.nja'))

        spec = Spec(
            build_dir=build_dir,
            plugin_source_map={
                'fake!bad': '/some/broken/path',
                'text!_core_/_default_wrapper_/template.nja': src_template,
            },
            bundle_source_map={
                'nunjucks': join('node_modules', 'nunjucks', 'nunjucks.js'),
            },
            transpile_source_map={},
        )

        rjs(spec, ())
        precompiled_path = join(build_dir, '__nunja_precompiled__.js')
        self.assertFalse(exists(precompiled_path))
        self.assertNotIn('slim', spec['bundle_source_map']['nunjucks'])

        # now trigger the advice
        spec.handle(BEFORE_COMPILE)
        self.assertTrue(exists(precompiled_path))

        with open(precompiled_path) as fd:
            precompiled = fd.read()

        core_path = resource_filename(Requirement.parse('nunja'), join(
            'nunja', '__core__.js'))
        with open(core_path) as fd:
            core_compiled = fd.read()

        # the compiled template should be identical with the one that
        # is stored in this source tree for the core
        self.assertEqual(precompiled, core_compiled)

        self.assertEqual(spec['transpile_source_map'], {
            'nunja/__precompiled_nunjucks__': precompiled_path,
        })

        # this one untouched.
        self.assertEqual(spec['plugin_source_map'], {
            'fake!bad': '/some/broken/path',
            'text!_core_/_default_wrapper_/template.nja': src_template,
        })

    def test_core_compiled_slim(self):
        remember_cwd(self)
        chdir(self._env_root)
        src_template = resource_filename(Requirement.parse('nunja'), join(
            'nunja', '_core_', '_default_wrapper_', 'template.nja'))
        build_dir = mkdtemp(self)

        spec = Spec(
            build_dir=build_dir,
            plugin_source_map={
                'text!_core_/_default_wrapper_/template.nja': src_template,
            },
            transpile_source_map={},
            bundle_source_map={
                'nunjucks': join('node_modules', 'nunjucks', 'nunjucks.js'),
            },
        )
        rjs(spec, ('slim',))
        precompiled_path = join(build_dir, '__nunja_precompiled__.js')
        spec.handle(BEFORE_COMPILE)
        self.assertIn('slim', spec['bundle_source_map']['nunjucks'])
        self.assertTrue(exists(precompiled_path))

    def test_core_compiled_slim_empty_case(self):
        remember_cwd(self)
        chdir(self._env_root)
        build_dir = mkdtemp(self)
        spec = Spec(
            build_dir=build_dir,
            plugin_source_map={},
            transpile_source_map={},
            bundle_source_map={},
        )
        rjs(spec, ('slim',))
        spec.handle(BEFORE_COMPILE)
        self.assertNotIn('nunjucks', spec['bundle_source_map'])

    def test_core_compiled_failure_bad_template(self):
        remember_cwd(self)
        chdir(self._env_root)
        build_dir = mkdtemp(self)
        src_dir = mkdtemp(self)
        src_template = join(src_dir, 'template.nja')

        with open(src_template, 'w') as fd:
            fd.write('<p>Hello {%World%}</p>')

        spec = Spec(
            build_dir=build_dir,
            plugin_source_map={
                'text!mold/dummy/template.nja': src_template,
            },
            transpile_source_map={},
            bundle_source_map={},
        )
        build_dir = mkdtemp(self)
        rjs(spec, ())

        with pretty_logging('nunja', stream=StringIO()) as stream:
            spec.handle(BEFORE_COMPILE)

        err = stream.getvalue()
        self.assertIn('ERROR', err)
        self.assertIn('failed to precompile', err)
        self.assertIn(
            'Template render error: (mold/dummy/template.nja)', err)

    def test_core_compiled_failure_missing_template(self):
        remember_cwd(self)
        chdir(self._env_root)
        build_dir = mkdtemp(self)
        src_template = join(build_dir, 'no_such_template.nja')

        spec = Spec(
            build_dir=build_dir,
            plugin_source_map={
                'text!nunja/dummy/no_such_template.nja': src_template,
            },
            transpile_source_map={},
            bundle_source_map={},
        )
        build_dir = mkdtemp(self)
        rjs(spec, ('slim',))

        with pretty_logging('nunja', stream=StringIO()) as stream:
            spec.handle(BEFORE_COMPILE)

        err = stream.getvalue()
        self.assertIn('ERROR', err)
        self.assertIn('failed to precompile', err)
