# -*- coding: utf-8 -*-
"""
Pluggable registry system for the nunja framework
"""

from errno import ENOENT
from logging import getLogger
from os.path import altsep
from os.path import exists
from os.path import join
from os.path import pardir
from os.path import sep

from pkg_resources import resource_filename

# from .exc import FileNotFoundError
# from .exc import TemplateNotFoundError

from calmjs.base import BaseModuleRegistry
from calmjs.indexer import mapper
from calmjs.utils import raise_os_error

from nunja.indexer import generate_modname_nunja
from nunja.indexer import REQUIREJS_TEXT_PREFIX

TMPL_FN_EXT = '.nja'
REQ_TMPL_NAME = 'template' + TMPL_FN_EXT
ENTRY_POINT_NAME = 'nunja.mold'
DEFAULT_REGISTRY_NAME = ENTRY_POINT_NAME
DEFAULT_WRAPPER_NAME = '_core_/_default_wrapper_'

logger = getLogger(__name__)
_marker = object()


def _remap(locals_, type_, mold_id, related):
    # this only works on sorted list.
    type_keys = type_ + '_keys'
    type_map = type_ + '_map'

    # these keys are assumed to be skipped as they are in the way.
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
            fext=TMPL_FN_EXT, req_tmpl_name=REQ_TMPL_NAME,
            text_prefix=REQUIREJS_TEXT_PREFIX,
            auto_reload=False,
            *a, **kw):
        """
        Arguments:

        registry_name
            The name of this registry.
        """

        self.default_prefix = default_prefix
        self.molds = {}
        self.tracked_entry_points = {}
        self.fext = fext
        self.req_tmpl_name = req_tmpl_name
        self.text_prefix = text_prefix
        self.auto_reload = auto_reload

    @classmethod
    def create(cls, registry_name=DEFAULT_REGISTRY_NAME, *a, **kw):
        return cls(registry_name=registry_name, *a, **kw)

    def _generate_maps(self, entry_point, module):
        (modname_nunja_template, modname_nunja_script,
            modpath_pkg_resources_entry_point) = generate_modname_nunja(
                entry_point, module, fext=self.fext,
                text_prefix=self.text_prefix)
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
                mold_id = key[len(self.text_prefix):-len(name) - 1]
                self.molds[mold_id] = template_map[key][:-len(name) - 1]
                yield mold_id

    def register_entry_point(self, entry_point):
        if len(entry_point.attrs) != 1:
            logger.warning(
                "entry_point '%s' from package '%s' incompatible with "
                "registry '%s'; a target dir must be provided after the "
                "module.",
                entry_point, entry_point.dist, self.registry_name,
            )
            return

        if self.auto_reload:
            self.tracked_entry_points[entry_point.name] = entry_point

        return super(MoldRegistry, self).register_entry_point(entry_point)

    def _map_entry_point_module(self, entry_point, module):
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
            template_prefix = self.text_prefix + mold_id
            _remap(locals(), 'template', template_prefix, related)
            _remap(locals(), 'script', mold_id, related)

        # discard everything else.
        discard.update(template_map)
        discard.update(script_map)

        logger.info("total of %d molds extracted", len(result) - 1)

        return result

    def _entry_point_to_path(self, entry_point):
        return resource_filename(entry_point.module_name, entry_point.attrs[0])

    def mold_id_to_path(self, mold_id, default=_marker):
        """
        Lookup the filesystem path of a mold identifier.
        """

        def handle_default(debug_msg=None):
            if debug_msg:
                logger.debug('mold_id_to_path:' + debug_msg, mold_id)
            if default is _marker:
                raise KeyError(
                    'Failed to lookup mold_id %s to a path' % mold_id)
            return default

        result = self.molds.get(mold_id)
        if result:
            return result

        if not self.tracked_entry_points:
            return handle_default()

        try:
            prefix, mold_basename = mold_id.split('/')
        except ValueError:
            return handle_default(
                'mold_id %s not found and not in standard format')

        entry_point = self.tracked_entry_points.get(prefix)
        if entry_point is None:
            return handle_default()
        return join(self._entry_point_to_path(entry_point), mold_basename)

    def lookup_path(self, mold_id_path, default=_marker):
        """
        For the given mold_id_path, look up the mold_id and translate
        that path to its filesystem equivalent.
        """

        fragments = mold_id_path.split('/')
        mold_id = '/'.join(fragments[:2])
        try:
            subpath = []
            for piece in fragments[2:]:
                if (sep in piece or (altsep and altsep in piece) or
                        piece == pardir):
                    raise KeyError
                elif piece and piece != '.':
                    subpath.append(piece)
            path = self.mold_id_to_path(mold_id)
        except KeyError:
            if default is _marker:
                raise
            return default

        return join(path, *subpath)
        # TODO Should a lookup_template be implemented?

    def verify_path(self, mold_id_path):
        """
        Lookup and verify path.
        """

        try:
            path = self.lookup_path(mold_id_path)
            if not exists(path):
                raise KeyError
        except KeyError:
            raise_os_error(ENOENT)
        return path


# TODO migrate the rest of the crufty old bits to above.
