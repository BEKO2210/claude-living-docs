"""Living Docs Engine — generate documentation directly from source code.

The package is split into three cooperating layers:

* :mod:`living_docs.extractors` turns Python source into immutable, typed
  data structures (pure parsing, no rendering).
* :mod:`living_docs.generators` turns those data structures — plus feature,
  changelog and prompt data — into Markdown (pure rendering, no I/O).
* :mod:`living_docs.build` holds shared build utilities (deterministic
  timestamps, idempotent file writing, repository discovery).

Keeping extraction, rendering and I/O separate is what makes every generator
idempotent and therefore safe to run inside CI drift checks.
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "0.1.0"
