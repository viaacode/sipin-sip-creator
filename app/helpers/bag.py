#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import mimetypes
import shutil
from datetime import datetime
from pathlib import Path

import bagit
from lxml import etree

from app.helpers.dcterms import DCTerms
from app.helpers.events import WatchfolderMessage
from app.helpers.mets import (
    METSDocSIP,
    Agent,
    AgentRole,
    AgentType,
    Note,
    NoteType,
    File,
    FileGrpUse,
    FileType,
)
from app.helpers.premis import Fixity
from app.helpers.sidecar import Sidecar


MIMETYPE_TYPE_MAP = {
    "image/jpeg": "Photographs - Digital",
    "image/tiff": "Photographs - Digital",
    "image/jp2": "Photographs - Digital",
    "audio/mpeg": "Audio - Media-independent (digital)",
    "audio/x-wav": "Audio - Media-independent (digital)",
    "audio/ogg": "Audio - Media-independent (digital)",
    "application/pdf": "Textual works - Digital",
    "application/zip": "Collection",
    "video/quicktime": "Video - File-based and Physical Media",
    "video/mp4": "Video - File-based and Physical Media",
    "video/mp4": "Video - File-based and Physical Media",
    "video/MP2T": "Video - File-based and Physical Media",
    "video/mpeg": "Video - File-based and Physical Media",
    "application/mxf": "Video - File-based and Physical Media",
}


def calculate_sip_type(mimetype: str) -> str:
    """Calculate the type of the SIP based on the mimetype of the essence.

    Args:
        Mimetype to map to the type.

    Returns:
        The type of the SIP.
    """
    try:
        return MIMETYPE_TYPE_MAP[mimetype]
    except KeyError:
        return "OTHER"


def md5(file: Path) -> str:
    """Calculate the md5 of a given file.

    Args:
        File to calculate the md5 for.

    Returns:
        The md5 value in hex value.
    """
    hash_md5 = hashlib.md5()
    with open(file, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def create_package_mets(
    watchfolder_message: WatchfolderMessage, sip_root_folder: Path, sidecar: Sidecar
):
    """Create the package METS.

    Args:
        watchfolder_message: The parsed watchfolder message.
        sip_root_folder: The root folder of the SIP.

    Returns:
        The METS document as an lxml element.
    """
    # METS doc
    doc = METSDocSIP(
        is_package_mets=True,
        type=calculate_sip_type(
            mimetypes.guess_type(watchfolder_message.get_essence_path())[0]
        ),
    )

    # Mandatory agent
    mandatory_agent = Agent(
        AgentRole.CREATOR,
        AgentType.OTHER,
        other_type="SOFTWARE",
        name="meemoo SIP creator",
        note=Note("0.1.0", NoteType.SOFTWARE_VERSION),
    )
    doc.add_agent(mandatory_agent)

    # Archival agent
    archival_agent = Agent(
        AgentRole.ARCHIVIST, AgentType.ORGANIZATION, name=watchfolder_message.cp_name
    )
    doc.add_agent(archival_agent)

    # Submitting agent
    submitting_agent = Agent(
        AgentRole.CREATOR,
        AgentType.ORGANIZATION,
        name=watchfolder_message.cp_name,
        note=Note(sidecar.cp_id, NoteType.IDENTIFICATIONCODE),
    )
    doc.add_agent(submitting_agent)

    root_folder = File(file_type=FileType.DIRECTORY, use=FileGrpUse.ROOT.value)
    metadata_folder = File(
        file_type=FileType.DIRECTORY,
        use=FileGrpUse.METADATA.value,
        label=FileGrpUse.METADATA.value,
    )
    metadata_desc_folder = File(
        file_type=FileType.DIRECTORY,
        use=f"{FileGrpUse.METADATA.value}/{FileGrpUse.DESCRIPTIVE.value}",
        label=FileGrpUse.DESCRIPTIVE.value,
    )

    # The descriptive metadata on IE level
    desc_ie_path_rel = Path("metadata", "descriptive", "dc.xml")
    desc_ie_path = Path(sip_root_folder, desc_ie_path_rel)
    desc_ie_file = File(
        file_type=FileType.FILE,
        label="descriptive",
        checksum=md5(desc_ie_path),
        size=desc_ie_path.stat().st_size,
        mimetype=mimetypes.guess_type(desc_ie_path)[0],
        created=datetime.fromtimestamp(desc_ie_path.stat().st_ctime),
        path=str(desc_ie_path_rel),
    )
    metadata_desc_folder.add_child(desc_ie_file)

    metadata_preserv_folder = File(
        file_type=FileType.DIRECTORY,
        use=f"{FileGrpUse.METADATA.value}/{FileGrpUse.PRESERVATION.value}",
        label=FileGrpUse.PRESERVATION.value,
    )
    reps_folder = File(
        file_type=FileType.DIRECTORY,
        use=FileGrpUse.REPRESENTATIONS.value,
        label=FileGrpUse.REPRESENTATIONS.value,
    )
    reps_folder_1 = File(
        file_type=FileType.DIRECTORY,
        use=f"{FileGrpUse.REPRESENTATIONS.value}/representation_1",
        label="representation_1",
    )

    # The representation METS File used for fileSec and structMap
    reps_path_rel = Path("representations", "representation_1", "mets.xml")
    reps_path = Path(sip_root_folder, reps_path_rel)
    reps_file = File(
        file_type=FileType.FILE,
        label="representation_1",
        checksum=md5(reps_path),
        size=reps_path.stat().st_size,
        mimetype=mimetypes.guess_type(reps_path)[0],
        created=datetime.fromtimestamp(reps_path.stat().st_ctime),
        path=str(reps_path_rel),
        is_mets=True,
    )
    reps_folder_1.add_child(reps_file)

    reps_folder.add_child(reps_folder_1)

    metadata_folder.add_child(metadata_desc_folder)
    metadata_folder.add_child(metadata_preserv_folder)

    root_folder.add_child(metadata_folder)
    root_folder.add_child(reps_folder)

    doc.add_file(root_folder)

    # dmdsec / amdsec
    doc.add_dmdsec(desc_ie_file)

    return doc.to_element()


def create_representation_mets(
    watchfolder_message: WatchfolderMessage, sip_root_folder: Path, sidecar: Sidecar
):
    """Create the representation METS.

    Args:
        watchfolder_message: The parsed watchfolder message.
        sip_root_folder: The root folder of the SIP.
        sidecar: The parsed sidecar containing metadata info of the essence.

    Returns:
        The METS document as an lxml element.
    """
    # METS doc
    doc = METSDocSIP(
        type=calculate_sip_type(
            mimetypes.guess_type(watchfolder_message.get_essence_path())[0]
        ),
    )

    essence_file_name: Path = watchfolder_message.get_essence_path().name

    metadata_folder = File(
        file_type=FileType.DIRECTORY,
        use=FileGrpUse.METADATA.value,
        label=FileGrpUse.METADATA.value,
    )
    metadata_desc_folder = File(
        file_type=FileType.DIRECTORY,
        use=f"{FileGrpUse.METADATA.value}/{FileGrpUse.DESCRIPTIVE.value}",
        label=FileGrpUse.DESCRIPTIVE.value,
    )
    metadata_preserv_folder = File(
        file_type=FileType.DIRECTORY,
        use=f"{FileGrpUse.METADATA.value}/{FileGrpUse.PRESERVATION.value}",
        label=FileGrpUse.PRESERVATION.value,
    )
    data_folder = File(
        file_type=FileType.DIRECTORY,
        use=FileGrpUse.DATA.value,
        label=FileGrpUse.DATA.value,
    )

    representation_path = Path("representations", "representation_1")

    # The preservation metadata file used for fileSec and structMap
    pres_path_rel = Path(representation_path, "metadata", "preservation", "premis.xml")
    pres_path = Path(sip_root_folder, pres_path_rel)
    pres_file = File(
        file_type=FileType.FILE,
        use=FileGrpUse.PRESERVATION.value,
        label=FileGrpUse.PRESERVATION.value,
        mimetype=mimetypes.guess_type(pres_path)[0],
        path=str(pres_path_rel),
        size=pres_path.stat().st_size,
        checksum=md5(pres_path),
        created=datetime.fromtimestamp(pres_path.stat().st_ctime),
    )

    # The essence file used for fileSec and structMap
    data_path_rel = Path(representation_path, "data", essence_file_name)
    data_path = Path(sip_root_folder, data_path_rel)
    data_file = File(
        file_type=FileType.FILE,
        use=FileGrpUse.DATA.value,
        label=FileGrpUse.DATA.value,
        mimetype=mimetypes.guess_type(data_path)[0],
        path=str(data_path_rel),
        size=data_path.stat().st_size,
        checksum=sidecar.md5,
        created=datetime.fromtimestamp(data_path.stat().st_ctime),
    )

    # Add file(s)
    metadata_preserv_folder.add_child(pres_file)
    data_folder.add_child(data_file)

    # Add folders
    metadata_folder.add_child(metadata_desc_folder)
    metadata_folder.add_child(metadata_preserv_folder)

    doc.add_file(metadata_folder)
    doc.add_file(data_folder)

    # amdsec
    doc.add_amdsec(pres_file)

    return doc.to_element()


def create_sip_bag(watchfolder_message: WatchfolderMessage) -> Path:
    """Create the SIP in the bag format.

     - Create the minimal SIP
     - Create a bag from the minimal SIP
     - Zip the bag
     - Remove the folder

    Structure of SIP:
        mets.xml
        metadata/
            descriptive/
                dc.xml
            preservation/
        representations/representation_1/
            data/
                essence.ext
            metadata/
                descriptive/
                preservation/
                    premis.xml

    Args:
        watchfolder_message: The parse watchfolder message.
    Returns:
        The path of the bag.
    """
    essence_path: Path = watchfolder_message.get_essence_path()
    xml_path = watchfolder_message.get_xml_path()
    if not essence_path.exists() or not xml_path.exists():
        # TODO: raise error
        return

    # Parse sidecar
    sidecar = Sidecar(xml_path)

    # Root folder for bag
    root_folder = Path(essence_path.parent, essence_path.stem)
    root_folder.mkdir(exist_ok=True)

    # /metadata
    metadata_folder = root_folder.joinpath("metadata")
    metadata_folder.mkdir(exist_ok=True)
    # /metadata/descriptive/
    metadata_desc_folder = metadata_folder.joinpath("descriptive")
    metadata_desc_folder.mkdir(exist_ok=True)
    # Create descriptive metadata and store it
    dc_terms = DCTerms.transform(xml_path)
    etree.ElementTree(dc_terms).write(
        str(metadata_desc_folder.joinpath("dc.xml")),
        pretty_print=True,
    )

    # /metadata/preservation/
    metadata_pres_folder = metadata_folder.joinpath("preservation")
    metadata_pres_folder.mkdir(exist_ok=True)
    # /representations/representation_1/
    representations_folder = root_folder.joinpath("representations", "representation_1")
    representations_folder.mkdir(exist_ok=True, parents=True)

    # /representations/representation_1/data/
    representations_data_folder = representations_folder.joinpath("data")
    representations_data_folder.mkdir(exist_ok=True)
    # Move essence
    essence_path.replace(representations_data_folder.joinpath(essence_path.name))

    # representations/representation_1/metadata/
    representations_metadata_folder = representations_folder.joinpath("metadata")
    representations_metadata_folder.mkdir(exist_ok=True)
    # representations/representation_1/metadata/descriptive
    representations_metadata_desc_folder = representations_metadata_folder.joinpath(
        "descriptive"
    )
    representations_metadata_desc_folder.mkdir(exist_ok=True)

    # representations/representation_1/metadata/preservation
    representations_metadata_pres_folder = representations_metadata_folder.joinpath(
        "preservation"
    )
    representations_metadata_pres_folder.mkdir(exist_ok=True)
    fixity = Fixity(sidecar.md5).to_element()
    etree.ElementTree(fixity).write(
        str(representations_metadata_pres_folder.joinpath("premis.xml")),
        pretty_print=True,
    )

    # Create and write representation mets.xml
    representation_mets_element = create_representation_mets(
        watchfolder_message, root_folder, sidecar
    )
    etree.ElementTree(representation_mets_element).write(
        str(representations_folder.joinpath("mets.xml")), pretty_print=True
    )

    # Create and write package mets.xml
    package_mets_element = create_package_mets(
        watchfolder_message, root_folder, sidecar
    )
    etree.ElementTree(package_mets_element).write(
        str(root_folder.joinpath("mets.xml")), pretty_print=True
    )

    # Make bag
    bagit.make_bag(root_folder, checksums=["md5"])

    # Zip bag
    bag_path = shutil.make_archive(
        essence_path.parent.joinpath(essence_path.stem).with_suffix(".bag"),
        "zip",
        root_folder,
    )

    # Remove root folder
    shutil.rmtree(root_folder)

    return Path(bag_path)
