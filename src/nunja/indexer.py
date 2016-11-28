# -*- coding: utf-8 -*-
"""
Since the AMD module name for Nunja has a prefix with the name based
directly on the entry point name, with all contents provided at the
entry_point.attr section follows the es6 convention (well, url subpath).
This means the modname generator cannot be a static function, so instead
one is created for each entry_point and module combination.
"""

from logging import getLogger
from os.path import join

from calmjs.indexer import resource_filename_mod_entry_point

REQUIREJS_TEXT_PREFIX = 'text!'

logger = getLogger(__name__)


def generate_modname_nunja(
        entry_point, base_module, fext, text_prefix=REQUIREJS_TEXT_PREFIX):
    """
    Generate a 3-tuple for the two modname_* and one modpath_* functions
    required.
    """

    def modname_nunja_template(fragments):
        # Nunja explicitly requires requirejs-text for the dynamic
        # loading of templates.  Also by convention, the filename
        # extension should be included as the modname is based for
        # the "standard" AMD/JavaScript module naming construction.
        return text_prefix + modname_nunja_script(fragments) + fext

    def modname_nunja_script(fragments):
        # Do note that in the main implementation, entry points with
        # multiple attrs will not be resolved and thus this behavior is
        # very undefined; hence the len check is removed.
        offset = len(base_module.__name__.split('.'))
        return '/'.join([entry_point.name] + fragments[offset:])

    def modpath_pkg_resources_entry_point(module, entry_point_=None):
        """
        Goes through pkg_resources for compliance with various PEPs.

        This one accepts a module as argument.
        """

        if entry_point != entry_point_:
            logger.warning(
                'modpath function created for %r got unexpected entrypoint %r',
                entry_point, entry_point_,
            )

        if module is not base_module:
            logger.warning(
                'modpath function created for %r got unexpected module %r',
                base_module, module,
            )

        try:
            # As a consequence of returning the first entry point attrs,
            # we effectively remap the module path for the given module
            # name to this new path, so the above two functions will
            # never see the attrs within the fragment, as all fragments
            # before the base path (which is returned here) are to be
            # provided by the module name.  For more details refer to
            # tests.
            return [join(resource_filename_mod_entry_point(
                module.__name__, entry_point), entry_point.attrs[0])]
        except ImportError:
            logger.warning("%r could not be located as a module", module)
        except Exception:
            logger.warning("%r does not appear to be a valid module", module)

        return []

    return (
        modname_nunja_template, modname_nunja_script,
        modpath_pkg_resources_entry_point,
    )
