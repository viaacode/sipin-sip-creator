#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

from app.helpers.dcterms import DCTerms
from tests.helpers import load_resource

from lxml import etree


def test_transform():
    # Arrange
    medadata_path = Path("tests", "resources", "dcterms", "metadata.xml")
    # Act
    terms_element = DCTerms.transform(medadata_path)
    # Assert
    terms_xml = etree.tostring(terms_element, pretty_print=True)
    xml = load_resource(Path("tests", "resources", "dcterms", "dcterms.xml"))
    assert terms_xml == xml
