# -*- coding: utf-8 -*-
try:
    from builtins import FileNotFoundError
except ImportError:  # pragma: no cover
    # this is second best...
    FileNotFoundError = OSError


class TemplateNotFoundError(FileNotFoundError):
    pass
