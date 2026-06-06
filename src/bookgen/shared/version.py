"""Single source of truth for the package version.

Course guideline 8.1 requires explicit, centralized version tracking that starts
at an initial value and increases with significant changes. Keeping the version
here (instead of duplicating the literal across modules) follows the DRY rule
from guideline 3.3, so other modules import it rather than redeclaring it.
"""

from __future__ import annotations

# Code version. Bump on every significant change (guideline 8.1).
__version__ = "1.0.2"


def get_version() -> str:
    """Return the current package version string."""
    return __version__
