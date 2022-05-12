#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

from app.helpers.sidecar import Sidecar


def test_sidecar():
    sidecar = Sidecar(Path("tests", "resources", "sidecar", "sidecar.xml"))
    assert not sidecar.md5
    assert sidecar.cp_id == "CP ID"


def test_sidecar_md5():
    sidecar = Sidecar(Path("tests", "resources", "sidecar", "sidecar_md5.xml"))
    assert sidecar.md5 == "7e0ef8c24fe343d98fbb93b6a7db6ccb"


def test_sidecar_calculate_original_filename():
    sidecar = Sidecar(
        Path("tests", "resources", "sidecar", "sidecar_bestandsnaam_source.xml")
    )
    assert sidecar.calculate_original_filename() == "bestandsnaam"


def test_sidecar_calculate_original_filename_source():
    sidecar = Sidecar(Path("tests", "resources", "sidecar", "sidecar_source.xml"))
    assert sidecar.calculate_original_filename() == "source"


def test_sidecar_calculate_original_filename_bestandsnaam():
    sidecar = Sidecar(Path("tests", "resources", "sidecar", "sidecar_bestandsnaam.xml"))
    assert sidecar.calculate_original_filename() == "bestandsnaam"


def test_sidecar_calculate_original_filename_none():
    sidecar = Sidecar(Path("tests", "resources", "sidecar", "sidecar.xml"))
    assert sidecar.calculate_original_filename() is None
