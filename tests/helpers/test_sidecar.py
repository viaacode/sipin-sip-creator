#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

from app.helpers.sidecar import Sidecar


def test_sidecar():
    sidecar = Sidecar(Path("tests", "resources", "sidecar", "sidecar.xml"))
    assert not sidecar.md5


def test_sidecar_md5():
    sidecar = Sidecar(Path("tests", "resources", "sidecar", "sidecar_md5.xml"))
    assert sidecar.md5 == "7e0ef8c24fe343d98fbb93b6a7db6ccb"