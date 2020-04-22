# -*- coding: utf-8 -*-
import logging
import re

import codecs
from collections import defaultdict
from os.path import dirname
from os.path import join

from calmjs.cli import node
from calmjs.exc import AdviceAbort

try:
    from calmjs.rjs.dist import EMPTY
except ImportError:  # pragma: no cover
    # just define it here...
    EMPTY = 'empty:'

from calmjs.toolchain import BEFORE_COMPILE
from calmjs.toolchain import BUILD_DIR
from calmjs.utils import json_dumps

# TODO figure out where to stash this value
NUNJA_PRECOMP_NS = '__nunja__'
nunjucks_nja_patt = re.compile(
    '^text!(?P<name>(?P<mold_id>[^!\\/]+\\/[^!\\/]+)\\/[^!]*\\.nja)$')

logger = logging.getLogger(__name__)


def to_hex(s):
    return codecs.encode(s.encode('utf8'), 'hex_codec').decode('utf8')


def nunjucks_precompile(path, name):
    require_stmt = 'var nunjucks = require("nunjucks");\n'
    stdout, stderr = node(
        '%sprocess.stdout.write(nunjucks.precompile(%s, {"name": %s}));'
        % (require_stmt, json_dumps(path), json_dumps(name))
    )
    if stderr:
        logger.error("failed to precompile '%s'\n%s'", path, stderr)
        return None
    else:
        return stdout


def precompile_nunja(
        spec, slim,
        base_sourcepath_key, bundle_sourcepath_key, omit_paths=()):
    """
    The generic precompile_nunja function.
    """

    required = {base_sourcepath_key, bundle_sourcepath_key, BUILD_DIR}
    missing = required.difference(spec.keys())
    if missing:
        raise AdviceAbort(
            'cannot precompile_nunja if spec is missing keys {%s}' % ', '.join(
                sorted(missing)))

    base_sourcepath = spec[base_sourcepath_key]
    precompiled_modnames = []
    molds = defaultdict(list)
    slim_bundle_modnames = []

    for modname, path in base_sourcepath.items():
        # could express this more succinctly with regex, probably
        if path in omit_paths:
            continue

        match = nunjucks_nja_patt.match(modname)
        if not match:
            logger.debug("'%s' is an incompatible nunja template name", path)
            continue

        mold = nunjucks_precompile(path, match.group('name'))
        if mold:
            molds[match.group('mold_id')].append(mold)
            precompiled_modnames.append(modname)

    for mold_id, precompiled in molds.items():
        # use a surrogate name as the bundle process in calmjs will
        # copy that into the final location.
        f = join(spec['build_dir'], to_hex(mold_id) + '.js')
        with codecs.open(f, 'w', encoding='utf8') as fd:
            for stdout in precompiled:
                fd.write(stdout)
        modname = '/'.join([NUNJA_PRECOMP_NS, mold_id])
        slim_bundle_modnames.append(modname)
        spec[bundle_sourcepath_key][modname] = f

    if slim:
        for modname in precompiled_modnames:
            base_sourcepath.pop(modname)
        nunjucks_path = spec[bundle_sourcepath_key].get('nunjucks')
        if nunjucks_path and nunjucks_path not in omit_paths:
            spec[bundle_sourcepath_key]['nunjucks'] = join(
                dirname(nunjucks_path), 'nunjucks-slim.js')

    return slim_bundle_modnames,


def precompile_nunja_rjs(spec, slim=False):
    slim_bundle_modnames = precompile_nunja(
        spec, slim, 'plugin_sourcepath', 'bundle_sourcepath',
        omit_paths=(EMPTY,)
    )[0]

    shim = spec['shim'] = spec.get('shim', {})
    for modname in slim_bundle_modnames:
        shim[modname] = {'exports': 'nunjucksPrecompiled'}


def rjs(spec, extras):
    if 'raw' in extras:
        logger.debug(
            'nunja will be skipping precompilation for rjs toolchain')
        return
    slim = 'slim' in extras
    spec.advise(BEFORE_COMPILE, precompile_nunja_rjs, spec, slim)


def webpack(spec, extras):
    if 'raw' in extras:
        logger.warning(
            'nunja cannot skip precompilation for webpack toolchain')
    slim = 'slim' in extras
    spec.advise(
        BEFORE_COMPILE, precompile_nunja,
        spec, slim, 'loaderplugin_sourcepath', 'bundle_sourcepath',
    )
