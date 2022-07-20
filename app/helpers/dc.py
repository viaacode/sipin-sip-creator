from pathlib import Path

from lxml import etree


class DC:
    """Class to write descriptive metadata of the representation in DC(Terms) format."""

    @classmethod
    def transform(cls, xml_source_path: Path, **kwargs) -> etree.Element:
        xslt_path = Path("app", "resources", "dc.xslt")
        xslt = etree.parse(str(xslt_path.resolve()))
        transform = etree.XSLT(xslt)
        return transform(etree.parse(str(xml_source_path)), **kwargs).getroot()
