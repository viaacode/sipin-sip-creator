#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

from app.helpers.premis import Fixity
from tests.helpers import load_resource

from lxml import etree
import pprint


def test_fixity():
    fixity = Fixity(md5="digest", uuid="e864ca60-97c2-468c-89be-061328aa154e")
    fixity_xml = etree.tostring(fixity.to_element(), pretty_print=True)
    xml = load_resource(Path("tests", "resources", "premis", "fixity_object.xml"))

    pprint.pprint(xml.decode("utf8"))
    assert fixity_xml == xml


def test_fixity_no_md5():
    fixity = Fixity(uuid="e864ca60-97c2-468c-89be-061328aa154e")
    fixity_xml = etree.tostring(fixity.to_element(), pretty_print=True)
    xml = load_resource(
        Path("tests", "resources", "premis", "fixity_object_no_md5.xml")
    )
    assert fixity_xml == xml
