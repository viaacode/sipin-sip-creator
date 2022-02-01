#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

from lxml import etree


class Sidecar:
    """Class used for parsing the metadata sidecar of the essence pair."""

    def __init__(self, path: Path):
        self.root = etree.parse(str(path))
        self.md5 = self.root.findtext("md5")
