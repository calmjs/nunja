# -*- coding: utf-8 -*-
import logging

from os.path import join
from os.path import dirname

from calmjs.cli import node
from calmjs.exc import AdviceAbort
from calmjs.toolchain import BEFORE_COMPILE
from calmjs.toolchain import BUILD_DIR

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
    filtered = {}
    script = []
    for k, path in plugin_source_map.items():
        values = k.split('!', 2)[:2]
        if values[0] != 'text':
            filtered[k] = path
            continue
        _, name = values
        script.append(
            'process.stdout.write(nunjucks.precompile("%s", {"name": "%s"}));'
            % (path, name)
        )
    if script:
        stdout, stderr = node(
            'var nunjucks = require("nunjucks");\n' + '\n'.join(script))
        f = join(spec['build_dir'], '__nunja_precompiled__.js')
        with open(f, 'w') as fd:
            fd.write(stdout)
        spec['transpile_source_map']['nunja/__precompiled_nunjucks__'] = f

    if slim:
        spec['plugin_source_map'] = filtered
        nunjucks_path = spec['bundle_source_map'].get('nunjucks')
        if nunjucks_path:
            spec['bundle_source_map']['nunjucks'] = join(
                dirname(nunjucks_path), 'nunjucks-slim.js')


def rjs(spec, extras):
    slim = 'slim' in extras
    spec.advise(BEFORE_COMPILE, precompile_nunja, spec, slim)
