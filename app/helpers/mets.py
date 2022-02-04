#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations
from datetime import datetime
from enum import Enum
from uuid import uuid4

from lxml import etree

from app.helpers.xml_utils import qname_text


class AgentRole(Enum):
    CREATOR = "CREATOR"
    EDITOR = "EDITOR"
    ARCHIVIST = "ARCHIVIST"
    PRESERVATION = "PRESERVATION"
    DISSEMINATOR = "DISSEMINATOR"
    CUSTODIAN = "CUSTODIAN"
    IPOWNER = "IPOWNER"
    OTHER = "OTHER"


class AgentType(Enum):
    INDIVIDUAL = "INDIVIDUAL"
    ORGANIZATION = "ORGANIZATION"
    OTHER = "OTHER"


class NoteType(Enum):
    SOFTWARE_VERSION = "SOFTWARE VERSION"
    IDENTIFICATIONCODE = "IDENTIFICATIONCODE"


class FileType(Enum):
    DIRECTORY = "DIRECTORY"
    FILE = "FILE"


class FileGrpUse(Enum):
    DOCUMENTATION = "documentation"
    SCHEMAS = "schemas"
    REPRESENTATIONS = "representations"
    METADATA = "metadata"
    DESCRIPTIVE = "descriptive"
    PRESERVATION = "preservation"
    DATA = "data"
    ROOT = "root"


NAMESPACES = {
    "mets": "http://www.loc.gov/METS/",
    "csip": "https://DILCIS.eu/XML/METS/CSIPExtensionMETS",
    "sip": "https://DILCIS.eu/XML/METS/SIPExtensionMETS",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "xlink": "http://www.w3.org/1999/xlink",
}


def generate_uuid() -> str:
    """Generates a UUID with prefix "uuid".

    The ID attribute is of type "xs:id" meaning that it only can begin with a
    letter, not a number. Prefixing the UUID with "uuid" fulfills this requirement.

    Returns:
        The prefixed UUID.
    """
    return f"uuid-{uuid4()}"


ATTRS = {
    "OBJID": "54c3a254-9c78-494d-a1f1-d07640989038",
    "TYPE": "OTHER",
    qname_text(NAMESPACES, "csip", "OTHERTYPE"): "Photographs - Digital",
    "PROFILE": "https://earksip.dilcis.eu/profile/E-ARK-SIP.xml",
}


class Note:
    """Class representing a METS note.

    Example:
        <mets:note csip:NOTETYPE="SOFTWARE VERSION">2.1.0-beta.7</mets:note>

    Args:
        value: The textual value of the note.
        type: The type of the note.
    """

    NOTE_TAG = etree.QName(NAMESPACES["mets"], "note")

    def __init__(
        self,
        value: str,
        type: NoteType = None,
    ):
        self.value = value
        self.type = type

    def to_element(self):
        """Returns the Note node as an lxml element.

        Returns:
            The Note element."""
        note_attrs = {}
        if self.type:
            note_attrs[qname_text(NAMESPACES, "csip", "NOTETYPE")] = self.type.value
        note_element = etree.Element(self.NOTE_TAG, note_attrs)
        note_element.text = self.value
        return note_element


class Agent:
    """Class representing a METS agent.

    Example:
        <mets:agent ROLE="ARCHIVIST" TYPE="ORGANIZATION">
            <mets:name>The Swedish health agency</mets:name>
            <mets:note csip:NOTETYPE="IDENTIFICATIONCODE">VAT:SE201345098701</mets:note>
        </mets:agent>

    Args:
        role: The role of the agent.
        type: The type of the agent.
        other_role: If the role is "other", this field is needed to denote the value
                    of the other role.
        other_type: If the type is "other", this field is needed to denote the value
                    of the other type.
        name: The name of the agent.
        note: The note of the agent.
    """

    AGENT_TAG = etree.QName(NAMESPACES["mets"], "agent")

    def __init__(
        self,
        role: AgentRole,
        type: AgentType,
        other_role: str = "",
        other_type: str = "",
        name: str = "",
        note: Note = None,
    ):
        self.role = role
        # If role is "OTHER" the other_role needs to be filled in
        if role == AgentRole.OTHER and not other_role:
            raise ValueError("The field 'other_role' is mandatory when role is 'OTHER'")
        self.other_role = other_role

        self.type = type
        # If type is "OTHER" the other_type needs to be filled in
        if type == AgentType.OTHER and not other_type:
            raise ValueError("The field 'other_type' is mandatory when type is 'OTHER'")
        self.other_type = other_type

        self.name = name
        self.note = note

    def to_element(self):
        """Returns the Agent node as an lxml element.

        Returns:
            The Agent element."""
        agents_attrs = {}
        if self.role:
            agents_attrs["ROLE"] = self.role.value
        if self.other_role:
            agents_attrs["OTHERROLE"] = self.other_role

        if self.type:
            agents_attrs["TYPE"] = self.type.value
        if self.other_type:
            agents_attrs["OTHERTYPE"] = self.other_type

        element = etree.Element(self.AGENT_TAG, **agents_attrs)

        if self.name:
            name_tag = etree.QName(NAMESPACES["mets"], "name")
            name_element = etree.Element(name_tag)
            name_element.text = self.name
            element.append(name_element)
        if self.note:
            element.append(self.note.to_element())
        return element


class File:
    """Class representing a File to create sctructMap and fileSec elements.

    Args:
        path: The path to the file.
        checksum: The checksum value of the file used in a fileSec entry.
        file_type: The type: "directory" or "file".
        use: The use used in a fileSec entry.
        label: The label used in a structMap entry.
        mimetype: The mimetype of the file used in a fileSec entry.
        size: The size of the file used in a fileSec entry.
        created: The creation date of the file used in a fileSec entry.
    """

    FILE_TAG = etree.QName(NAMESPACES["mets"], "file")
    FILEGRP_TAG = etree.QName(NAMESPACES["mets"], "fileGrp")
    DIV_TAG = etree.QName(NAMESPACES["mets"], "div")
    MPTR_TAG = etree.QName(NAMESPACES["mets"], "mptr")
    FPTR_TAG = etree.QName(NAMESPACES["mets"], "fptr")

    def __init__(
        self,
        path: str = None,
        checksum: str = None,
        file_type: FileType = None,
        use: str = None,
        label: str = "",
        mimetype: str = None,
        size: int = None,
        created: str = None,
    ):

        self.path = path
        self.checksum = checksum
        self.type = file_type
        self.use = use
        self.is_fptr = False
        self.label = label
        self.mimetype = mimetype
        self.size = size
        self.created = created
        self.children = []

    def add_child(self, file: File):
        """Add a child to the file.

        In the case of a file, this calculates if the file should have a "fptr" or a
        "mptr" tag in the structMap.

        Args:
            file: The file to add.
        """
        # Calculate "ftpr" or "mptr"
        if self.type == FileType.DIRECTORY and file.type == FileType.FILE:
            if file.use in (
                FileGrpUse.DOCUMENTATION.value,
                FileGrpUse.METADATA.value,
                FileGrpUse.DESCRIPTIVE.value,
                FileGrpUse.PRESERVATION.value,
            ):
                file.is_fptr = True
            elif file.use in (FileGrpUse.REPRESENTATIONS.value,):
                file.is_fptr = False
        self.children.append(file)

    def to_filesec_element(self):
        """Returns the fileSec node as an lxml element.

        Returns:
            The fileSec element."""
        if self.type == FileType.DIRECTORY:
            file_tag = self.FILEGRP_TAG
            file_element = etree.Element(file_tag, ID=generate_uuid())
            for child in self.children:
                file_element.append(child.to_filesec_element())
        elif self.type == FileType.FILE:
            file_tag = self.FILE_TAG
            file_element = etree.Element(file_tag, ID=generate_uuid())
        else:
            raise ValueError("No valid type")

        if self.checksum:
            file_element.attrib["CHECKSUM"] = self.checksum
            file_element.attrib["CHECKSUMTYPE"] = "MD5"

        if self.use:
            file_element.attrib["USE"] = self.use

        if self.path:
            flocat_tag = qname_text(NAMESPACES, "mets", "FLocat")
            flocat_attribs = {
                "LOCTYPE": "URL",
                qname_text(NAMESPACES, "xlink", "type"): "simple",
                qname_text(NAMESPACES, "xlink", "href"): self.path,
            }
            flocat_element = etree.Element(flocat_tag, flocat_attribs)
            file_element.append(flocat_element)

        if self.mimetype:
            file_element.attrib["MIMETYPE"] = self.mimetype
        if self.size:
            file_element.attrib["SIZE"] = str(self.size)
        if self.created:
            file_element.attrib["CREATED"] = self.created.astimezone().isoformat()

        return file_element

    def to_structmap_element(self):
        """Returns the structMap node as an lxml element.

        Returns:
            The structMap element."""
        if self.type == FileType.DIRECTORY:
            file_tag = self.DIV_TAG
            file_element = etree.Element(file_tag, ID=generate_uuid(), LABEL=self.label)
            for child in self.children:
                file_element.append(child.to_structmap_element())
        elif self.type == FileType.FILE:
            if self.is_fptr:
                file_tag = self.FPTR_TAG
                file_attrs = {"FILEID": generate_uuid()}
            else:
                file_tag = self.MPTR_TAG
                file_attrs = {
                    qname_text(NAMESPACES, "xlink", "type"): "simple",
                    qname_text(NAMESPACES, "xlink", "href"): self.path,
                    "LOCTYPE": "URL",
                }
            file_element = etree.Element(file_tag, file_attrs)
        else:
            raise ValueError("No valid type")
        return file_element


class METSDocSIP:
    """Class representing a METS document with (C)SIP extension.

    Args:
        is_package_mets: Denotes if this is the package mets."""

    FILESEC_TAG = etree.QName(NAMESPACES["mets"], "fileSec")
    STRUCTMAP_TAG = etree.QName(NAMESPACES["mets"], "structMap")

    def __init__(self, is_package_mets: bool = False):
        self.agents = []
        self.files = []
        self.date_created: str = datetime.now().astimezone().isoformat()
        self.is_package_mets = is_package_mets

    def _document_root(self):
        """Returns the METS root node as an lxml element.

        Returns:
            The root element."""
        return etree.Element(
            qname_text(NAMESPACES, "mets", "mets"),
            nsmap=NAMESPACES,
            attrib=ATTRS,
        )

    def _document_hdr(self):
        """Returns the metsHdr node as an lxml element.

        Returns:
            The metsHdr element."""
        hdr_tag = etree.QName(NAMESPACES["mets"], "metsHdr")
        hdr_attrs = {
            "CREATEDATE": self.date_created,
        }
        if self.is_package_mets:
            hdr_attrs[qname_text(NAMESPACES, "csip", "OAISPACKAGETYPE")] = "SIP"
        hdr_element = etree.Element(hdr_tag, **hdr_attrs)
        for agent in self.agents:
            hdr_element.append(agent.to_element())
        return hdr_element

    def _filesec(self):
        """Returns fileSec node for all files as an lxml element.

        Returns:
            The fileSec element."""
        filesec_element = etree.Element(self.FILESEC_TAG, ID=generate_uuid())
        for file in self.files:
            filesec_element.append(file.to_filesec_element())
        return filesec_element

    def _structmap(self):
        """Returns structMap node for all files as an lxml element.

        Returns:
            The structMap element."""
        structmap_attrs = {"ID": generate_uuid(), "TYPE": "PHYSICAL", "LABEL": "CSIP"}
        structmap_element = etree.Element(self.STRUCTMAP_TAG, structmap_attrs)
        for file in self.files:
            structmap_element.append(file.to_structmap_element())
        return structmap_element

    def add_file(self, file: File):
        """Adds a file to the METS docs.

        Args:
            file: File to add.
        """
        self.files.append(file)

    def add_agent(self, agent: Agent):
        """Adds an agent to the METS docs.

        Args:
            file: Agent to add.
        """
        self.agents.append(agent)

    def to_element(self):
        """Returns the METS document as an lxml element.

        Returns:
            The METS document."""
        root = self._document_root()
        # Add metsHdr
        root.append(self._document_hdr())
        # Add files: fileSec and StructMap
        root.append(self._filesec())
        root.append(self._structmap())

        return root
