# -*- coding: utf-8 -*-
import logging

from os.path import join

from calmjs.cli import node
from calmjs.toolchain import BEFORE_COMPILE

logger = logging.getLogger(__name__)


def precompile_nunja(spec):
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

    # spec['plugin_source_map'] = filtered


def rjs(spec):
    spec.advise(BEFORE_COMPILE, precompile_nunja, spec)
