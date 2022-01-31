#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from uuid import uuid4

from lxml import etree


def _lxmlns(nsmap: dict, ns: str) -> str:
    """Return namespace"""
    return f"{{{nsmap[ns]}}}"


def _qname_text(nsmap: dict, ns: str, local_name: str) -> str:
    return f"{_lxmlns(nsmap, ns)}{local_name}"


class Fixity:
    """Class to write the fixity preservation metadata of the representation.

    Args:
        md5: the md5"""

    NSMAP = {
        "premis": "http://www.loc.gov/premis/v3",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }
    ATTRS = {"version": "3.0"}

    def __init__(self, md5: str = None, uuid: str = str(uuid4())):
        self.md5 = md5
        self.uuid = uuid

    def to_element(self):
        """Returns the fixity premis object as a lxml element.

        Returns:
            The Premis fixity object element."""
        # Root element
        root_element = etree.Element(
            _qname_text(self.NSMAP, "premis", "premis"),
            nsmap=self.NSMAP,
            attrib=self.ATTRS,
        )

        # Premis object
        object_element = etree.SubElement(
            root_element,
            _qname_text(self.NSMAP, "premis", "object"),
            attrib={_qname_text(self.NSMAP, "xsi", "type"): "premis:file"},
        )
        # Premis object identifier
        object_identifier_element = etree.SubElement(
            object_element, _qname_text(self.NSMAP, "premis", "objectIdentifier")
        )
        etree.SubElement(
            object_identifier_element,
            _qname_text(self.NSMAP, "premis", "objectIdentifierType"),
        ).text = "UUID"
        etree.SubElement(
            object_identifier_element,
            _qname_text(self.NSMAP, "premis", "objectIdentifierValue"),
        ).text = self.uuid

        # Premis object category
        etree.SubElement(
            object_element, _qname_text(self.NSMAP, "premis", "objectCategory")
        ).text = "file"

        # Premis object characteristics

        object_characteristics_element = etree.SubElement(
            object_element,
            _qname_text(self.NSMAP, "premis", "objectCharacteristics"),
        )
        fixity_element = etree.SubElement(
            object_characteristics_element,
            _qname_text(self.NSMAP, "premis", "fixity"),
        )
        if self.md5:
            etree.SubElement(
                fixity_element,
                _qname_text(self.NSMAP, "premis", "messageDigestAlgorithm"),
                attrib={
                    "authority": "cryptographicHashFunctions",
                    "authorityURI": "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions",
                    "valueURI": "http://id.loc.gov/vocabulary/preservation/cryptographicHashFunctions/md5",
                },
            ).text = "MD5"
            etree.SubElement(
                fixity_element,
                _qname_text(self.NSMAP, "premis", "messageDigest"),
            ).text = self.md5

        return root_element
