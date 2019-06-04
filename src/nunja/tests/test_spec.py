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

from nunja.spec import nunjucks_nja_patt
from nunja.spec import precompile_nunja
from nunja.spec import rjs
from nunja.spec import webpack
from nunja.spec import to_hex

from calmjs.testing.mocks import StringIO
from calmjs.testing.utils import mkdtemp
from calmjs.testing.utils import remember_cwd
from calmjs.testing.utils import rmtree
from calmjs.testing.utils import setup_class_install_environment


class MiscTestCase(unittest.TestCase):

    def test_to_hex(self):
        self.assertEqual(to_hex(u'a'), u'61')
        self.assertEqual(to_hex(u'\u306a'), u'e381aa')


class NameTestCase(unittest.TestCase):
    """
    Name matching tests.
    """

    def assertAllValid(self, f, values):
        for value in values:
            self.assertTrue(f(value), msg='%s should be valid' % value)
            plugin, name = value.split('!')
            mold_id = '/'.join(name.split('/', 2)[:2])
            self.assertEqual(f(value).group('name'), name)
            self.assertEqual(f(value).group('mold_id'), mold_id)

    def assertAllInvalid(self, f, values):
        for value in values:
            self.assertFalse(f(value), msg='%s should be invalid' % value)

    def test_valid_names(self):
        valid = (
            'text!nunja.mold/name/index.nja',
            'text!nunja.mold/name/nested/index.nja',
            'text!other/name/nested/template.nja',
            'text!_core_/_default_wrapper_/template.nja',
        )
        self.assertAllValid(nunjucks_nja_patt.match, valid)

    def test_invalid_names(self):
        invalid = (
            'text!//index.nja',
            'text!somename//index.nja',
            'text!/root/path/index.nja',
            'text!text!nunja.mold/name/index.nja',
            'text!css!nunja.mold/name/index.nja',
            'css!nunja.mold/name/index.nja',
            'text!nunja.mold/name/index.nja!strip',
            'text!nunja.mold/template.nja',
            'text!nunja/template.nja',
            'text!/nunja/template.nja',
        )
        self.assertAllInvalid(nunjucks_nja_patt.match, invalid)


class SpecGeneralTestCase(unittest.TestCase):
    """
    Test out the precompile template process using the generic function.
    """

    def test_missing_keys(self):
        build_dir = mkdtemp(self)
        spec = Spec(
            build_dir=build_dir,
        )

        with self.assertRaises(AdviceAbort) as e:
            precompile_nunja(
                spec, False, 'myplugin_sourcepath', 'mybundle_sourcepath')

        self.assertEqual(
            e.exception.args[0],
            'cannot precompile_nunja if spec is missing keys '
            '{mybundle_sourcepath, myplugin_sourcepath}'
        )

    def test_empty(self):
        build_dir = mkdtemp(self)
        spec = Spec(
            build_dir=build_dir,
            plugin_sourcepath={},
            bundle_sourcepath={
            },
        )

        precompile_nunja(spec, False, 'plugin_sourcepath', 'bundle_sourcepath')
        self.assertFalse(exists(join(build_dir, '__nunja_precompiled__.js')))
        self.assertNotIn('nunjucks', spec['bundle_sourcepath'])

    def test_nunjucks(self):
        nunjucks_path = join('node_modules', 'nunjucks', 'nunjucks.js'),
        build_dir = mkdtemp(self)
        spec = Spec(
            build_dir=build_dir,
            plugin_sourcepath={},
            bundle_sourcepath={
                'nunjucks': nunjucks_path,
            },
        )

        precompile_nunja(spec, False, 'plugin_sourcepath', 'bundle_sourcepath')
        self.assertFalse(exists(join(build_dir, '__nunja_precompiled__.js')))
        self.assertEqual(spec['bundle_sourcepath']['nunjucks'], nunjucks_path)

    def test_nunjucks_slim(self):
        nunjucks_path = join('node_modules', 'nunjucks', 'nunjucks.js')
        nunjucks_slim = join('node_modules', 'nunjucks', 'nunjucks-slim.js')
        build_dir = mkdtemp(self)
        spec = Spec(
            build_dir=build_dir,
            plugin_sourcepath={},
            bundle_sourcepath={
                'nunjucks': nunjucks_path,
            },
        )

        precompile_nunja(spec, True, 'plugin_sourcepath', 'bundle_sourcepath')
        self.assertFalse(exists(join(build_dir, '__nunja_precompiled__.js')))
        self.assertEqual(spec['bundle_sourcepath']['nunjucks'], nunjucks_slim)

    def test_nunjucks_slim_empty_unspecified(self):
        nunjucks_path = 'empty:'
        build_dir = mkdtemp(self)
        spec = Spec(
            build_dir=build_dir,
            plugin_sourcepath={},
            bundle_sourcepath={
                'nunjucks': nunjucks_path,
            },
        )
        precompile_nunja(spec, True, 'plugin_sourcepath', 'bundle_sourcepath')
        self.assertNotEqual(spec['bundle_sourcepath']['nunjucks'], 'empty:')

    def test_nunjucks_slim_empty_specified(self):
        nunjucks_path = 'about:blank'
        build_dir = mkdtemp(self)
        spec = Spec(
            build_dir=build_dir,
            plugin_sourcepath={},
            bundle_sourcepath={
                'nunjucks': nunjucks_path,
            },
        )
        precompile_nunja(
            spec, True, 'plugin_sourcepath', 'bundle_sourcepath',
            omit_paths=('about:blank',)
        )
        self.assertEqual(spec['bundle_sourcepath']['nunjucks'], 'about:blank')

    def test_stubbed_empty(self):
        build_dir = mkdtemp(self)
        spec = Spec(
            build_dir=build_dir,
            plugin_sourcepath={
                'text!demo/template.nja': 'empty:',
            },
            bundle_sourcepath={
            },
        )

        with pretty_logging('nunja', stream=StringIO()) as stream:
            precompile_nunja(
                spec, True, 'plugin_sourcepath', 'bundle_sourcepath',
                omit_paths=('empty:',)
            )

        self.assertNotIn('failed', stream.getvalue())
        self.assertFalse(exists(join(build_dir, '__nunja_precompiled__.js')))
        self.assertNotIn('nunjucks', spec['bundle_sourcepath'])


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

    def test_rjs_core_compiled(self):
        remember_cwd(self)
        chdir(self._env_root)

        build_dir = mkdtemp(self)
        src_template = resource_filename(Requirement.parse('nunja'), join(
            'nunja', '_core_', '_default_wrapper_', 'template.nja'))

        spec = Spec(
            build_dir=build_dir,
            plugin_sourcepath={
                'fake!bad': '/some/broken/path',
                'text!_core_/_default_wrapper_/template.nja': src_template,
                'text!some/template.nja': src_template,
                'text!some/other/data.json': src_template,
                'text!some/mold/template.nja': src_template,
            },
            bundle_sourcepath={
                'nunjucks': join('node_modules', 'nunjucks', 'nunjucks.js'),
            },
        )

        rjs(spec, ())
        hex_name = to_hex('_core_/_default_wrapper_')
        precompiled_path = join(build_dir, hex_name + '.js')
        self.assertFalse(exists(precompiled_path))
        self.assertNotIn('slim', spec['bundle_sourcepath']['nunjucks'])

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

        self.assertEqual(
            spec['bundle_sourcepath']['__nunja__/_core_/_default_wrapper_'],
            precompiled_path,
        )
        # mold paths will be precompiled by default now
        self.assertIn('__nunja__/some/mold', spec['bundle_sourcepath'])

        # this one untouched.
        self.assertEqual(spec['plugin_sourcepath'], {
            'fake!bad': '/some/broken/path',
            'text!_core_/_default_wrapper_/template.nja': src_template,
            # all other ones that did not pass the test will be filtered
            # out for other processing
            'text!some/template.nja': src_template,
            'text!some/mold/template.nja': src_template,
            'text!some/other/data.json': src_template,
        })

    def test_rjs_core_compiled_slim(self):
        remember_cwd(self)
        chdir(self._env_root)
        src_template = resource_filename(Requirement.parse('nunja'), join(
            'nunja', '_core_', '_default_wrapper_', 'template.nja'))
        build_dir = mkdtemp(self)

        spec = Spec(
            build_dir=build_dir,
            plugin_sourcepath={
                'text!_core_/_default_wrapper_/template.nja': src_template,
            },
            bundle_sourcepath={
                'nunjucks': join('node_modules', 'nunjucks', 'nunjucks.js'),
            },
        )
        rjs(spec, ('slim',))
        hex_name = to_hex('_core_/_default_wrapper_')
        precompiled_path = join(build_dir, hex_name + '.js')
        spec.handle(BEFORE_COMPILE)
        self.assertIn('slim', spec['bundle_sourcepath']['nunjucks'])
        self.assertTrue(exists(precompiled_path))
        self.assertEqual({
            '__nunja__/_core_/_default_wrapper_': {
                'exports': 'nunjucksPrecompiled'
            },
        }, spec['shim'])

    def test_rjs_core_compiled_raw(self):
        remember_cwd(self)
        chdir(self._env_root)
        build_dir = mkdtemp(self)

        src_dir = mkdtemp(self)
        src_template = join(src_dir, 'template.nja')
        with open(src_template, 'w') as fd:
            fd.write('<p>Hello, {name}</p>')

        spec = Spec(
            build_dir=build_dir,
            plugin_sourcepath={
                'text!some/mold/template.nja': src_template,
            },
            bundle_sourcepath={
                'nunjucks': join('node_modules', 'nunjucks', 'nunjucks.js'),
            },
        )
        with pretty_logging('nunja', stream=StringIO()) as stream:
            rjs(spec, ('raw'))
        # now trigger the advice
        spec.handle(BEFORE_COMPILE)
        # template remains in plugins
        self.assertEqual(spec['plugin_sourcepath'], {
            'text!some/mold/template.nja': src_template,
        })
        # will not be applied in raw.
        self.assertNotIn('__nunja__/some/mold', spec['bundle_sourcepath'])
        self.assertIn(
            'nunja will be skipping precompilation for rjs toolchain',
            stream.getvalue(),
        )

    def test_rjs_core_compiled_slim_empty_case(self):
        remember_cwd(self)
        chdir(self._env_root)
        build_dir = mkdtemp(self)
        spec = Spec(
            build_dir=build_dir,
            plugin_sourcepath={},
            bundle_sourcepath={},
        )
        rjs(spec, ('slim',))
        spec.handle(BEFORE_COMPILE)
        self.assertNotIn('nunjucks', spec['bundle_sourcepath'])

    def test_rjs_core_compiled_failure_bad_template(self):
        remember_cwd(self)
        chdir(self._env_root)
        build_dir = mkdtemp(self)
        src_dir = mkdtemp(self)
        src_template = join(src_dir, 'template.nja')

        with open(src_template, 'w') as fd:
            fd.write('<p>Hello {%World%}</p>')

        spec = Spec(
            build_dir=build_dir,
            plugin_sourcepath={
                'text!mold/dummy/template.nja': src_template,
            },
            bundle_sourcepath={},
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

    def test_rjs_core_compiled_failure_missing_template(self):
        remember_cwd(self)
        chdir(self._env_root)
        build_dir = mkdtemp(self)
        src_template = join(build_dir, 'no_such_template.nja')

        spec = Spec(
            build_dir=build_dir,
            plugin_sourcepath={
                'text!nunja/dummy/no_such_template.nja': src_template,
            },
            bundle_sourcepath={},
        )
        build_dir = mkdtemp(self)
        rjs(spec, ('slim',))

        with pretty_logging('nunja', stream=StringIO()) as stream:
            spec.handle(BEFORE_COMPILE)

        err = stream.getvalue()
        self.assertIn('ERROR', err)
        self.assertIn('failed to precompile', err)

    def test_webpack_core_compiled(self):
        remember_cwd(self)
        chdir(self._env_root)

        build_dir = mkdtemp(self)
        src_template = resource_filename(Requirement.parse('nunja'), join(
            'nunja', '_core_', '_default_wrapper_', 'template.nja'))

        spec = Spec(
            build_dir=build_dir,
            loaderplugin_sourcepath={
                'fake!bad': '/some/broken/path',
                'text!_core_/_default_wrapper_/template.nja': src_template,
                'text!some/template.nja': src_template,
                'text!some/other/data.json': src_template,
            },
            bundle_sourcepath={
                'nunjucks': join('node_modules', 'nunjucks', 'nunjucks.js'),
            },
        )

        webpack(spec, ())
        hex_name = to_hex('_core_/_default_wrapper_')
        precompiled_path = join(build_dir, hex_name + '.js')
        self.assertFalse(exists(precompiled_path))
        self.assertNotIn('slim', spec['bundle_sourcepath']['nunjucks'])

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

        self.assertEqual(
            spec['bundle_sourcepath']['__nunja__/_core_/_default_wrapper_'],
            precompiled_path,
        )

        # this one untouched.
        self.assertEqual(spec['loaderplugin_sourcepath'], {
            'fake!bad': '/some/broken/path',
            'text!_core_/_default_wrapper_/template.nja': src_template,
            # all other ones that did not pass the test will be filtered
            # out for other processing
            'text!some/template.nja': src_template,
            'text!some/other/data.json': src_template,
        })

    def test_webpack_core_compiled_slim(self):
        remember_cwd(self)
        chdir(self._env_root)
        src_template = resource_filename(Requirement.parse('nunja'), join(
            'nunja', '_core_', '_default_wrapper_', 'template.nja'))
        build_dir = mkdtemp(self)

        spec = Spec(
            build_dir=build_dir,
            loaderplugin_sourcepath={
                'text!_core_/_default_wrapper_/template.nja': src_template,
            },
            bundle_sourcepath={
                'nunjucks': join('node_modules', 'nunjucks', 'nunjucks.js'),
            },
        )
        webpack(spec, ('slim',))
        hex_name = to_hex('_core_/_default_wrapper_')
        precompiled_path = join(build_dir, hex_name + '.js')
        spec.handle(BEFORE_COMPILE)
        self.assertIn('slim', spec['bundle_sourcepath']['nunjucks'])
        self.assertTrue(exists(precompiled_path))

    def test_webpack_core_compiled_raw(self):
        remember_cwd(self)
        chdir(self._env_root)
        build_dir = mkdtemp(self)

        src_dir = mkdtemp(self)
        src_template = join(src_dir, 'template.nja')
        with open(src_template, 'w') as fd:
            fd.write('<p>Hello, {name}</p>')

        spec = Spec(
            build_dir=build_dir,
            loaderplugin_sourcepath={
                'text!some/mold/template.nja': src_template,
            },
            bundle_sourcepath={
                'nunjucks': join('node_modules', 'nunjucks', 'nunjucks.js'),
            },
        )
        with pretty_logging('nunja', stream=StringIO()) as stream:
            webpack(spec, ('raw'))
        # now trigger the advice
        spec.handle(BEFORE_COMPILE)
        # template remains in plugins
        self.assertEqual(spec['loaderplugin_sourcepath'], {
            'text!some/mold/template.nja': src_template,
        })
        # will not be applied in raw.
        self.assertIn('__nunja__/some/mold', spec['bundle_sourcepath'])
        self.assertIn(
            'nunja cannot skip precompilation for webpack toolchain',
            stream.getvalue(),
        )
