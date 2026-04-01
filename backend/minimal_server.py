#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEPRECATED — Minimal GödelOS Backend Server.

This module is superseded by ``backend.unified_server``, which is the single
canonical runtime entrypoint for all GödelOS server startup paths.

This file is a pure compatibility shim.  It re-exports the canonical ``app``
so that any external tooling referencing ``backend.minimal_server:app`` will
still work.  It will be removed in a future release.
"""
import warnings as _warnings
_warnings.warn(
    "backend.minimal_server is deprecated. Use backend.unified_server as the "
    "canonical server entrypoint.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export the canonical app so ``backend.minimal_server:app`` resolves.
from backend.unified_server import app  # noqa: F401 — intentional re-export

__all__ = ["app"]
