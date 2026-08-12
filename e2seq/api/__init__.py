"""E2seq API module."""

from e2seq.api.server import AbortChat, app

# Backwards-compatible alias — older call sites use ``from e2seq.api import AbortChat``.
# ``AbortChat`` actually lives inside ``server.py`` to avoid pulling the full HTTP
# stack in standalone contexts (e.g. unit tests). Re-exporting here preserves the
# flat import path.
__all__ = ['app', 'AbortChat']
