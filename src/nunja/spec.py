# -*- coding: utf-8 -*-
import logging
import re

from codecs import encode
from collections import defaultdict
from os.path import dirname
from os.path import join

from calmjs.cli import node
from calmjs.exc import AdviceAbort
from calmjs.rjs.dist import EMPTY
from calmjs.toolchain import BEFORE_COMPILE
from calmjs.toolchain import BUILD_DIR
from calmjs.utils import json_dumps

# TODO figure out where to stash this value
NUNJA_PRECOMP_NS = '__nunja__'
nunjucks_nja_patt = re.compile(
    '^text!(?P<name>(?P<mold_id>[^!\\/]+\\/[^!\\/]+)\\/[^!]*\\.nja)$')

logger = logging.getLogger(__name__)


def to_hex(s):
    return encode(s.encode('utf8'), 'hex_codec').decode('utf8')


def precompile_nunja(spec, slim=False):
    required = {
        'plugin_sourcepath', 'transpile_sourcepath', 'bundle_sourcepath',
        BUILD_DIR,
    }
    missing = required.difference(spec.keys())
    if missing:
        raise AdviceAbort(
            'cannot precompile_nunja if spec is missing keys {%s}' % ', '.join(
                sorted(missing)))

    plugin_sourcepath = spec['plugin_sourcepath']
    require_stmt = 'var nunjucks = require("nunjucks");\n'
    standard_sourcepath = {}
    molds = defaultdict(list)
    for k, path in plugin_sourcepath.items():
        # could express this more succinctly with regex, probably
        values = k.split('!', 2)[:2]
        plugin, name = values
        parts = name.split('/', 2)
        if path == EMPTY:
            continue
        elif plugin != 'text' and not name.endswith('.nja'):
            standard_sourcepath[k] = path
            continue
        elif len(parts) < 3:
            # a template with an incompatible naming scheme
            # TODO should warn about this?
            standard_sourcepath[k] = path
            continue

        mold_id = '/'.join(parts[:2])

        # start processing the name
        stdout, stderr = node(
            '%sprocess.stdout.write(nunjucks.precompile(%s, {"name": %s}));'
            % (require_stmt, json_dumps(path), json_dumps(name))
        )

        if stderr:
            logger.error("failed to precompile '%s'\n%s'", path, stderr)
        else:
            molds[mold_id].append(stdout)

    if molds:
        for mold_id, precompiled in molds.items():
            # use a surrogate name as the bundle process in calmjs will
            # copy that into the final location.
            f = join(spec['build_dir'], to_hex(mold_id) + '.js')
            with open(f, 'w') as fd:
                for stdout in precompiled:
                    fd.write(stdout)
            modname = '/'.join([NUNJA_PRECOMP_NS, mold_id])
            spec['bundle_sourcepath'][modname] = f
            spec['shim'] = spec.get('shim', {})
            spec['shim'][modname] = {
                'exports': 'nunjucksPrecompiled'
            }

    if slim:
        spec['plugin_sourcepath'] = standard_sourcepath
        nunjucks_path = spec['bundle_sourcepath'].get('nunjucks')
        if nunjucks_path and nunjucks_path != EMPTY:
            spec['bundle_sourcepath']['nunjucks'] = join(
                dirname(nunjucks_path), 'nunjucks-slim.js')


def rjs(spec, extras):
    slim = 'slim' in extras
    spec.advise(BEFORE_COMPILE, precompile_nunja, spec, slim)


def precompile_nunja_webpack(spec, slim=False):
    required = {
        'loaderplugin_sourcepath', 'transpile_sourcepath', 'bundle_sourcepath',
        BUILD_DIR,
    }
    missing = required.difference(spec.keys())
    if missing:
        raise AdviceAbort(
            'cannot precompile_nunja if spec is missing keys {%s}' % ', '.join(
                sorted(missing)))

    require_stmt = 'var nunjucks = require("nunjucks");\n'
    standard_sourcepath = {}
    remove = []
    molds = defaultdict(list)
    for k, path in spec['loaderplugin_sourcepath'].items():
        values = k.split('!', 2)[:2]
        plugin, name = values
        parts = name.split('/', 2)
        if plugin != 'text' and not name.endswith('.nja'):
            # standard_sourcepath[k] = path
            continue
        elif len(parts) < 3:
            # a template with an incompatible naming scheme
            # TODO should warn about this?
            # standard_sourcepath[k] = path
            continue

        mold_id = '/'.join(parts[:2])

        # start processing the name
        stdout, stderr = node(
            '%sprocess.stdout.write(nunjucks.precompile(%s, {"name": %s}));'
            % (require_stmt, json_dumps(path), json_dumps(name))
        )

        if stderr:
            logger.error("failed to precompile '%s'\n%s'", path, stderr)
        else:
            molds[mold_id].append(stdout)

    if molds:
        for mold_id, precompiled in molds.items():
            # use a surrogate name as the bundle process in calmjs will
            # copy that into the final location.
            f = join(spec['build_dir'], to_hex(mold_id) + '.js')
            with open(f, 'w') as fd:
                for stdout in precompiled:
                    fd.write(stdout)
            modname = '/'.join([NUNJA_PRECOMP_NS, mold_id])
            spec['bundle_sourcepath'][modname] = f

    if slim:
        nunjucks_path = spec['bundle_sourcepath'].get('nunjucks')
        if nunjucks_path and nunjucks_path != EMPTY:
            spec['bundle_sourcepath']['nunjucks'] = join(
                dirname(nunjucks_path), 'nunjucks-slim.js')


def webpack(spec, extras):
    slim = 'slim' in extras
    spec.advise(BEFORE_COMPILE, precompile_nunja_webpack, spec, slim)
