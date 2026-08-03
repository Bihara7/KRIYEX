"""
System Information Engine.

Provides information about the user's computer.
"""

from __future__ import annotations

import platform
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class SystemInfo:
    operating_system: str
    python_version: str
    machine: str
    processor: str


def detect_system() -> SystemInfo:
    """
    Detect the current system information.
    """

    os_name = platform.system()

    if os_name == "Windows":
        version = platform.version()

        # Windows 11 uses build numbers >= 22000
        try:
            build = int(version.split(".")[-1])
        except ValueError:
            build = 0

        if build >= 22000:
            operating_system = "Windows 11"
        else:
            operating_system = "Windows 10"

    else:
        operating_system = f"{os_name} {platform.release()}"

    return SystemInfo(
        operating_system=operating_system,
        python_version=sys.version.split()[0],
        machine=platform.machine(),
        processor=platform.processor(),
    )


system_info = detect_system()