# -*- coding: utf-8 -*-
"""
Pluggable registry system for the nunja framework
"""


from logging import getLogger

# from .exc import FileNotFoundError
# from .exc import TemplateNotFoundError

from calmjs.base import BaseModuleRegistry
from calmjs.indexer import mapper

from nunja.indexer import generate_modname_nunja
from nunja.indexer import REQUIREJS_TEXT_PREFIX

TMPL_FN_EXT = '.nja'
REQ_TMPL_NAME = 'template' + TMPL_FN_EXT
ENTRY_POINT_NAME = 'nunja.mold'

# I supposed this can all be hardcoded, but eating ones dogfood can be
# useful as a litmus test while this keeps the naming scheme consistent,
# even if usage is a bit different.
DEFAULT_REGISTRY_NAME = 'nunja.mold'
DEFAULT_WRAPPER_NAME = '_core_/_default_wrapper_'
# DEFAULT_MOLDS = {
#     DEFAULT_WRAPPER_NAME: join(dirname(__file__), DEFAULT_WRAPPER_NAME)
# }

logger = getLogger(__name__)
_marker = object()


def _remap(locals_, type_, mold_id, related):
    # this only works on sorted list.
    type_keys = type_ + '_keys'
    type_map = type_ + '_map'

    # pop all keys we don't care about
    while locals_.get(type_keys):
        if locals_.get(type_keys)[-1].startswith(mold_id):
            break
        locals_.get(type_keys).pop()

    # start using our keys
    while locals_.get(type_keys):
        if locals_.get(type_keys)[-1].startswith(mold_id):
            key = locals_[type_keys].pop()
            related[key] = locals_.get(type_map).pop(key)
        else:
            break


class MoldRegistry(BaseModuleRegistry):
    """
    Default registry implementation.
    """

    def _init(
            self, default_prefix='_',
            fext=TMPL_FN_EXT, req_tmpl_name=REQ_TMPL_NAME, *a, **kw):
        """
        Arguments:

        registry_name
            The name of this registry.
        """

        self.default_prefix = default_prefix
        self.molds = {}
        self.fext = fext
        self.req_tmpl_name = req_tmpl_name
        # Forcibly register the default one here as the core rendering
        # need this wrapper.
        # self.molds.update(DEFAULT_MOLDS)

    def _generate_maps(self, entry_point, module):
        (modname_nunja_template, modname_nunja_script,
            modpath_pkg_resources_entry_point) = generate_modname_nunja(
                entry_point, module, fext=self.fext)
        template_map = mapper(
            module, modpath=modpath_pkg_resources_entry_point,
            globber='recursive', modname=modname_nunja_template,
            fext=self.fext,
        )
        script_map = mapper(
            module, modpath=modpath_pkg_resources_entry_point,
            globber='recursive', modname=modname_nunja_script,
        )

        logger.info(
            "entry_point '%s' from package '%s' provided "
            "%d templates and %d scripts.",
            entry_point, entry_point.dist, len(template_map), len(script_map),
        )

        return template_map, script_map

    def _generate_and_store_mold_id_map(self, template_map):
        """
        Not a pure generator expression as this has the side effect of
        storing the resulting id and map it into a local dict.  Produces
        a list of all valid mold_ids from the input template_keys.

        Internal function; NOT meant to be used outside of this class.
        """

        name = self.req_tmpl_name
        for key in sorted(template_map.keys(), reverse=True):
            if len(key.split('/')) == 3 and key.endswith(name):
                mold_id = key[len(REQUIREJS_TEXT_PREFIX):-len(name) - 1]
                self.molds[mold_id] = template_map[key][:-len(name) - 1]
                yield mold_id

    def _map_entry_point_module(self, entry_point, module):
        if len(entry_point.attrs) != 1:
            logger.warning(
                "entry_point '%s' from package '%s' incompatible with "
                "registry '%s'; a target dir must be provided after the "
                "module.",
                entry_point, entry_point.dist, self.registry_name,
            )
            return {}

        template_map, script_map = self._generate_maps(entry_point, module)

        # molds are effectively modules, so split them up as such.
        # first derive all the keys and sort them for easier processing
        template_keys = sorted(template_map.keys())
        script_keys = sorted(script_map.keys())

        mold_ids = self._generate_and_store_mold_id_map(template_map)

        # the "discard" pile, where would-be molds that do not contain a
        # default template will be dumped to - at the module level.
        discard = {}
        result = {module.__name__: discard}
        script_key = template_key = ''

        for mold_id in mold_ids:
            related = result[mold_id] = {}
            template_prefix = REQUIREJS_TEXT_PREFIX + mold_id
            _remap(locals(), 'template', template_prefix, related)
            _remap(locals(), 'script', mold_id, related)

        # discard everything else.
        discard.update(template_map)
        discard.update(script_map)

        logger.info("total of %d molds extracted", len(result) - 1)

        return result

    def mold_id_to_path(self, mold_id, default=_marker):
        """
        Lookup the path of a mold identifier.
        """

        return self.molds.get(mold_id)


# TODO migrate the rest of the crufty old bits to above.
