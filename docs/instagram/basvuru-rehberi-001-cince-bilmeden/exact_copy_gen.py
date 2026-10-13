# -*- coding: utf-8 -*-
"""Regenerate exact-copy.json from the locked copy definitions."""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from slides_data import COPY, SUPPLIED, LOCKUP

# Generated inline by the revision-2 record step (see exact-copy.md).
