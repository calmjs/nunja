# -*- coding: utf-8 -*-
import logging

from os.path import join
from os.path import dirname

from calmjs.cli import node
from calmjs.exc import AdviceAbort
from calmjs.rjs.dist import EMPTY
from calmjs.toolchain import BEFORE_COMPILE
from calmjs.toolchain import BUILD_DIR
from calmjs.utils import json_dumps

logger = logging.getLogger(__name__)


def precompile_nunja(spec, slim=False):
    required = {
        'plugin_source_map', 'transpile_source_map', 'bundle_source_map',
        BUILD_DIR,
    }
    missing = required.difference(spec.keys())
    if missing:
        raise AdviceAbort(
            'cannot precompile_nunja if spec is missing keys {%s}' % ', '.join(
                sorted(missing)))

    plugin_source_map = spec['plugin_source_map']
    require_stmt = 'var nunjucks = require("nunjucks");\n'
    standard_source_map = {}
    compiled = []
    for k, path in plugin_source_map.items():
        values = k.split('!', 2)[:2]
        if values[0] != 'text':
            standard_source_map[k] = path
            continue
        if path == EMPTY:
            continue
        _, name = values
        stdout, stderr = node(
            '%sprocess.stdout.write(nunjucks.precompile(%s, {"name": %s}));'
            % (require_stmt, json_dumps(path), json_dumps(name))
        )

        if stderr:
            logger.error("failed to precompile '%s'\n%s'", path, stderr)
        else:
            compiled.append(stdout)

    if compiled:
        f = join(spec['build_dir'], '__nunja_precompiled__.js')
        with open(f, 'w') as fd:
            for stdout in compiled:
                fd.write(stdout)
        spec['transpile_source_map']['nunja/__precompiled_nunjucks__'] = f

    if slim:
        spec['plugin_source_map'] = standard_source_map
        nunjucks_path = spec['bundle_source_map'].get('nunjucks')
        if nunjucks_path and nunjucks_path != EMPTY:
            spec['bundle_source_map']['nunjucks'] = join(
                dirname(nunjucks_path), 'nunjucks-slim.js')


def rjs(spec, extras):
    slim = 'slim' in extras
    spec.advise(BEFORE_COMPILE, precompile_nunja, spec, slim)
