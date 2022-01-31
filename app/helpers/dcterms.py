from lxml import etree


class DCTerms:

    NSMAP = {
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "dcterms": "http://purl.org/dc/terms/",
        "dc": "http://purl.org/dc/elements/1.1/",
    }

    def __init__(self, creator: str, identifier: str, title: str):
        """Class to write descriptive metadata of the representation in DCTerms format.

        Args:
            creator: Creator of the representation.
            identifier: Identifier of the representation.
            title: Title of the representation.
        """
        self.creator = creator
        self.identifier = identifier
        self.title = title

    def to_element(self):
        attrs = {"version": "1.0"}
        root = etree.Element(
            "item",
            nsmap=self.NSMAP,
            attrib=attrs,
        )
        prefix = f'{{{"http://purl.org/dc/terms/"}}}'
        # Creator
        etree.SubElement(root, f"{prefix}creator").text = self.creator

        # Identifier
        etree.SubElement(root, f"{prefix}identifier").text = self.identifier

        # Title
        etree.SubElement(root, f"{prefix}title").text = self.title

        return root
