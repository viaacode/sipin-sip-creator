#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

from app.helpers.dcterms import DCTerms
from tests.helpers import load_resource

from lxml import etree


def test_dcterms():
    creator = "Creator"
    identifier = "Identifier"
    title = "Title"
    terms_element = DCTerms(creator, identifier, title).to_element()
    terms_xml = etree.tostring(terms_element, pretty_print=True)
    xml = load_resource(Path("tests", "resources", "dcterms", "dcterms.xml"))
    assert terms_xml == xml
