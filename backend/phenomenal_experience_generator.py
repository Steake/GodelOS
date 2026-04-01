"""
DEPRECATED — Phenomenal Experience Generator for GödelOS.

This module is superseded by ``backend.core.phenomenal_experience``, which
provides the canonical qualia and subjective-experience simulation used by
``UnifiedConsciousnessEngine``.

This file is a pure compatibility shim.  It re-exports the canonical
implementation so any code referencing ``backend.phenomenal_experience_generator``
will still work.  It will be removed in a future release.
"""
import warnings as _warnings
_warnings.warn(
    "backend.phenomenal_experience_generator is deprecated. Use "
    "backend.core.phenomenal_experience instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export canonical implementation
from backend.core.phenomenal_experience import *  # noqa: F401,F403

__all__ = ["PhenomenalExperienceGenerator"]
