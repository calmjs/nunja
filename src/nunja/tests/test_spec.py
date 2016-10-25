# -*- coding: utf-8 -*-
import unittest

from os import chdir
from os.path import exists
from os.path import join

from pkg_resources import resource_filename

from calmjs.exc import AdviceAbort
from calmjs.toolchain import Spec
from calmjs.toolchain import BEFORE_COMPILE
from calmjs.npm import npm_install
from calmjs.utils import which

from nunja.spec import precompile_nunja
from nunja.spec import rjs

from calmjs.testing.utils import mkdtemp
from calmjs.testing.utils import remember_cwd


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
            bundle_source_map={},
            transpile_source_map={},
        )

        precompile_nunja(spec)
        self.assertFalse(exists(join(build_dir, '__nunja_precompiled__.js')))

    @unittest.skipIf(which('npm') is None, 'npm not found.')
    def test_core_compiled(self):
        remember_cwd(self)
        tmpdir = mkdtemp(self)
        chdir(tmpdir)
        npm_install('nunja', production=True)
        build_dir = mkdtemp(self)
        src_template = resource_filename('nunja', join(
            '_core_', '_default_wrapper_', 'template.nja'))

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

        core_path = resource_filename('nunja', '__core__.js')
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

        # TODO split this test out to different function
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
        build_dir = mkdtemp(self)
        rjs(spec, ('slim',))
        precompiled_path = join(build_dir, '__nunja_precompiled__.js')
        spec.handle(BEFORE_COMPILE)
        self.assertIn('slim', spec['bundle_source_map']['nunjucks'])
