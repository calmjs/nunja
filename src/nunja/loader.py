# -*- coding: utf-8 -*-
import codecs

from os.path import getmtime

from jinja2.loaders import BaseLoader
from jinja2.loaders import TemplateNotFound

from .exc import FileNotFoundError


def uptodate_checker(filename):
    mtime = getmtime(filename)

    def checker():
        try:
            return getmtime(filename) == mtime
        except OSError:
            return False

    return checker


class NunjaLoader(BaseLoader):

    def __init__(self, registry):
        self.registry = registry

    def get_source(self, environment, template):
        try:
            path = self.registry.verify_path(template)
        except FileNotFoundError:
            raise TemplateNotFound(template)

        with codecs.open(path, encoding='utf-8') as f:
            source = f.read()
        return source, path, uptodate_checker(path)
