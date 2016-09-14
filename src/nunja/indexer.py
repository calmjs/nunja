# -*- coding: utf-8 -*-
"""
Since the AMD module name for Nunja has a prefix with the name based
directly on the entry point name, with all contents provided at the
entry_point.attr section follows the es6 convention (well, url subpath).
This means the modname generator cannot be a static function, so instead
one is created for each entry_point and module combination.
"""


def generate_modname_nunja(entry_point, module):

    def modname_nunja_template(fragments):
        # Nunja explicitly requires requirejs-text for the dynamic
        # loading of templates.
        return 'text!' + modname_nunja_script(fragments)

    def modname_nunja_script(fragments):
        # Do note that in the main implementation, entry points with
        # multiple attrs will not be resolved and thus this behavior is
        # very undefined; hence the len check is removed.
        offset = len(module.__name__.split('.')) + 1  # len(entry_point.attrs)
        return '/'.join([entry_point.name] + fragments[offset:])

    return modname_nunja_template, modname_nunja_script
