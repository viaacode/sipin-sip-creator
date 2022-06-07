#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import pytest

from app.helpers.sidecar import Sidecar


def test_sidecar():
    sidecar = Sidecar(Path("tests", "resources", "sidecar", "sidecar.xml"))
    assert not sidecar.md5
    assert sidecar.cp_id == "CP ID"


def test_sidecar_md5():
    sidecar = Sidecar(Path("tests", "resources", "sidecar", "sidecar_md5.xml"))
    assert sidecar.md5 == "7e0ef8c24fe343d98fbb93b6a7db6ccb"


@pytest.mark.parametrize(
    "input_file,bestandsnaam",
    [
        ("sidecar_bestandsnaam_source.xml", "bestandsnaam"),
        ("sidecar_source.xml", "source"),
        ("sidecar_bestandsnaam.xml", "bestandsnaam"),
        ("sidecar_bestandsnamen_source.xml", "Bestandsnaam"),
        ("sidecar.xml", None),
    ],
)
def test_sidecar_calculate_original_filename(input_file, bestandsnaam):
    sidecar = Sidecar(Path("tests", "resources", "sidecar", input_file))
    assert sidecar.calculate_original_filename() == bestandsnaam
