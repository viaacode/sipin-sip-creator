from pathlib import Path

from lxml import etree


class DCTerms:
    """Class to write descriptive metadata of the representation in DCTerms format."""

    @classmethod
    def transform(cls, xml_source_path: Path) -> etree.Element:
        xslt_path = Path("app", "resources", "dcterms.xslt")
        xslt = etree.parse(str(xslt_path.resolve()))
        transform = etree.XSLT(xslt)
        return transform(etree.parse(str(xml_source_path))).getroot()
