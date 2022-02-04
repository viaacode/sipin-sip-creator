from lxml import etree

from app.helpers.xml_utils import qname_text


class DCTerms:
    """Class to write descriptive metadata of the representation in DCTerms format.

    Args:
        creator: Creator of the representation.
        identifier: Identifier of the representation.
        title: Title of the representation.
    """

    NSMAP = {
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "dcterms": "http://purl.org/dc/terms/",
        "dc": "http://purl.org/dc/elements/1.1/",
    }

    def __init__(self, creator: str, identifier: str, title: str):
        self.creator = creator
        self.identifier = identifier
        self.title = title

    def to_element(self):
        """Returns the DCterms node as an lxml element.

        Returns:
            The DCterms root element."""
        attrs = {"version": "1.0"}
        root = etree.Element(
            "item",
            nsmap=self.NSMAP,
            attrib=attrs,
        )
        # Creator
        etree.SubElement(
            root, qname_text(self.NSMAP, "dcterms", "creator")
        ).text = self.creator

        # Identifier
        etree.SubElement(
            root, qname_text(self.NSMAP, "dcterms", "identifier")
        ).text = self.identifier

        # Title
        etree.SubElement(
            root, qname_text(self.NSMAP, "dcterms", "title")
        ).text = self.title

        return root
