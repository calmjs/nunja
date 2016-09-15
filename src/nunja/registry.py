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

        (modname_nunja_template, modname_nunja_script,
            modpath_pkg_resources_entry_point) = generate_modname_nunja(
                entry_point, module, fext=self.fext)
        templates = mapper(
            module, modpath=modpath_pkg_resources_entry_point,
            globber='recursive', modname=modname_nunja_template,
            fext=self.fext,
        )
        scripts = mapper(
            module, modpath=modpath_pkg_resources_entry_point,
            globber='recursive', modname=modname_nunja_script,
        )
        result = {}
        result.update(templates)
        result.update(scripts)
        return {module.__name__: result}


# TODO migrate the rest of the crufty old bits to above.
