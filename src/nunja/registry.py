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

    def _init(self, default_prefix='_', fext=TMPL_FN_EXT, *a, **kw):
        """
        Arguments:

        registry_name
            The name of this registry.
        """

        self.default_prefix = default_prefix
        self.molds = {}
        self.fext = fext
        # Forcibly register the default one here as the core rendering
        # need this wrapper.
        # self.molds.update(DEFAULT_MOLDS)

    def _map_entry_point_module(self, entry_point, module):

        if len(entry_point.attrs) != 1:
            logger.warning(
                "entry_point '%s' from package '%s' incompatible with "
                "registry '%s'; a target dir must be provided after the "
                "module.",
                entry_point, entry_point.dist, self.registry_name,
            )
            return {}

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

        # molds are effectively modules, so split them up as such.
        # first derive all the keys and sort them for easier processing
        template_keys = sorted(template_map.keys())
        script_keys = sorted(script_map.keys())
        # the generator expression containing all possible mold_ids that
        # follow the nunja mold requirements (i.e. directory within the
        # location specified by the entry point that that also contain a
        # file named after the default template.
        mold_ids = (
            mold_id[:-len(REQ_TMPL_NAME) - 1] for mold_id in (
                key[len(REQUIREJS_TEXT_PREFIX):] for key in list(
                    reversed(template_keys))
                if len(key.split('/')) == 3 and key.endswith(REQ_TMPL_NAME)
            )
        )
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


# TODO migrate the rest of the crufty old bits to above.
