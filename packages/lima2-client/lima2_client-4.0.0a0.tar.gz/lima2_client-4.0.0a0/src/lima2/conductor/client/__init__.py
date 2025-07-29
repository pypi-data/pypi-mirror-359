# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Conductor client subpackage.

Contains the HTTP client code for the lima2 conductor server.

Example usage:
```
import lima2.conductor.client as lima2

lima2.acquisition.prepare(...)
lima2.acquisition.start()
print(lima2.pipeline.progress_counters())
```
"""

from lima2.conductor.client import acquisition, detector, pipeline, session
from lima2.conductor.client.exceptions import ConductorConnectionError, ConductorError

__all__ = [
    "acquisition",
    "detector",
    "pipeline",
    "session",
    "ConductorConnectionError",
    "ConductorError",
]
