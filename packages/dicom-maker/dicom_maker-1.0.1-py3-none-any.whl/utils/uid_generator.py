#!/usr/bin/env python3
"""
UID generation utilities for DICOM Generator
"""

import uuid
from config import UID_ROOT


def generate_uid(prefix=UID_ROOT):
    """
    Generate a unique DICOM UID

    Args:
        prefix (str): UID prefix/root

    Returns:
        str: A valid DICOM UID
    """
    unique_part = str(uuid.uuid4().int)[:16]
    return f"{prefix}.{unique_part}"