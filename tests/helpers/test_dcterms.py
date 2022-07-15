#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import pytest
from app.helpers.dcterms import DCTerms
from tests.helpers import load_resource

from lxml import etree


@pytest.mark.parametrize(
    "input_file,output_file",
    [
        ("metadata_deelarchief.xml", "dcterms_deelarchief.xml"),
        ("metadata_archief.xml", "dcterms_archief.xml"),
        ("metadata_seizoen.xml", "dcterms_seizoen.xml"),
        ("metadata_seizoennummer.xml", "dcterms_seizoennummer.xml"),
        ("metadata_serienummer.xml", "dcterms_serienummer.xml"),
        ("metadata_deelreeks.xml", "dcterms_deelreeks.xml"),
        ("metadata_deelreeks_serienummer.xml", "dcterms_deelreeks_serienummer.xml"),
        ("metadata_reeks.xml", "dcterms_reeks.xml"),
        ("metadata_reeks_serienummer.xml", "dcterms_reeks_serienummer.xml"),
        ("metadata_reeks_deelreeks.xml", "dcterms_reeks_deelreeks.xml"),
        ("metadata_serie.xml", "dcterms_serie.xml"),
        ("metadata_serie_serienummer.xml", "dcterms_serie_serienummer.xml"),
        ("metadata_serie_deelreeks.xml", "dcterms_serie_deelreeks.xml"),
        ("metadata_programma.xml", "dcterms_programma.xml"),
        (
            "metadata_programmabeschrijving.xml",
            "dcterms_programmabeschrijving.xml",
        ),
        ("metadata_bestandsnamen.xml", "dcterms_bestandsnamen.xml"),
        ("metadata_dc_Subjects.xml", "dcterms_dc_Subjects.xml"),
        ("metadata_description_short.xml", "dcterms_description_short.xml"),
        ("metadata_titles_empty_title.xml", "dcterms_titles_empty_title.xml"),
        ("metadata_all_empty_titles.xml", "dcterms_all_empty_titles.xml"),
    ],
)
def test_transform(input_file, output_file):
    # Arrange
    medadata_path = Path("tests", "resources", "dcterms", input_file)
    # Act
    terms_element = DCTerms.transform(medadata_path)
    # Assert
    terms_xml = etree.tostring(terms_element, pretty_print=True).strip()
    xml = load_resource(Path("tests", "resources", "dcterms", output_file))
    assert terms_xml == xml


def test_transform_uuid():
    # Arrange
    medadata_path = Path("tests", "resources", "dcterms", "metadata.xml")
    # Act
    terms_element = DCTerms.transform(
        medadata_path,
        ie_uuid=etree.XSLT.strparam("865b767d-05f9-49d5-ba54-e9e82acec30d"),
    )
    # Assert
    terms_xml = etree.tostring(terms_element, pretty_print=True).strip()
    xml = load_resource(Path("tests", "resources", "dcterms", "dcterms.xml"))
    assert terms_xml == xml
