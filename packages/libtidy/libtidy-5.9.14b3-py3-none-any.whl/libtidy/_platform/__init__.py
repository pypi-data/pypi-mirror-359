# flake8-in-file-ignores: noqa: E305,F401,F403,F405

# Copyright (c) 2024 Adam Karpierz
# SPDX-License-Identifier: HTMLTIDY

import sys
import os
import ctypes as ct

from ._platform import *

def defined(varname, __getframe=sys._getframe):
    frame = __getframe(1)
    return varname in frame.f_locals or varname in frame.f_globals

def from_oid(oid, __cast=ct.cast, __py_object=ct.py_object):
    return __cast(oid, __py_object).value if oid else None

del sys, os, ct

if is_windows:  # pragma: no cover
    from ._windows import (DLL_PATH, DLL, dlclose, CFUNC,
                           time_t, timeval)
elif is_linux:  # pragma: no cover
    from ._linux import (DLL_PATH, DLL, dlclose, CFUNC,
                         time_t, timeval)
elif is_macos:  # pragma: no cover
    from ._macos import (DLL_PATH, DLL, dlclose, CFUNC,
                         time_t, timeval)
else:  # pragma: no cover
    raise ImportError("unsupported platform")
