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


def create_package_mets(watchfolder_message: WatchfolderMessage, sip_root_folder: Path):
    """Create the package METS.

    Args:
        watchfolder_message: The parsed watchfolder message.
        sip_root_folder: The root folder of the SIP.

    Returns:
        The METS document as an lxml element.
    """
    # METS doc
    doc = METSDocSIP(is_package_mets=True)

    # Mandatory agent
    mandatory_agent = Agent(
        AgentRole.CREATOR,
        AgentType.OTHER,
        other_type="SOFTWARE",
        name="meemoo SIP creator",
        note=Note("0.1.", NoteType.SOFTWARE_VERSION),
    )
    doc.add_agent(mandatory_agent)

    # Archival agent
    archival_agent = Agent(
        AgentRole.ARCHIVIST, AgentType.ORGANIZATION, name=watchfolder_message.cp_name
    )
    doc.add_agent(archival_agent)

    # Submitting agent
    submitting_agent = Agent(
        AgentRole.CREATOR, AgentType.ORGANIZATION, name=watchfolder_message.cp_name
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
        use=FileGrpUse.DESCRIPTIVE.value,
        label=FileGrpUse.DESCRIPTIVE.value,
    )
    metadata_preserv_folder = File(
        file_type=FileType.DIRECTORY,
        use=FileGrpUse.PRESERVATION.value,
        label=FileGrpUse.PRESERVATION.value,
    )
    reps_folder = File(
        file_type=FileType.DIRECTORY,
        use=FileGrpUse.REPRESENTATIONS.value,
        label=FileGrpUse.REPRESENTATIONS.value,
    )
    reps_folder_1 = File(
        file_type=FileType.DIRECTORY,
        use=FileGrpUse.REPRESENTATIONS.value,
        label="representation_1",
    )

    # The representation METS File used for fileSec and strutMap
    reps_path_rel = Path("representations", "representation_1", "mets.xml")
    reps_path = Path(sip_root_folder, reps_path_rel)
    reps_file = File(
        file_type=FileType.FILE,
        use=FileGrpUse.REPRESENTATIONS.value,
        label="representation_1",
        checksum=md5(reps_path),
        size=reps_path.stat().st_size,
        mimetype=mimetypes.guess_type(reps_path)[0],
        created=datetime.fromtimestamp(reps_path.stat().st_ctime),
        path=str(reps_path_rel),
    )
    reps_folder_1.add_child(reps_file)

    reps_folder.add_child(reps_folder_1)

    metadata_folder.add_child(metadata_desc_folder)
    metadata_folder.add_child(metadata_preserv_folder)

    root_folder.add_child(metadata_folder)
    root_folder.add_child(reps_folder)

    doc.add_file(root_folder)

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
    doc = METSDocSIP()

    xml_file_name: Path = watchfolder_message.get_xml_path().name
    essence_file_name: Path = watchfolder_message.get_essence_path().name

    metadata_folder = File(
        file_type=FileType.DIRECTORY,
        use=FileGrpUse.METADATA.value,
        label=FileGrpUse.METADATA.value,
    )
    metadata_desc_folder = File(
        file_type=FileType.DIRECTORY,
        use=FileGrpUse.DESCRIPTIVE.value,
        label=FileGrpUse.DESCRIPTIVE.value,
    )
    metadata_preserv_folder = File(
        file_type=FileType.DIRECTORY,
        use=FileGrpUse.PRESERVATION.value,
        label=FileGrpUse.PRESERVATION.value,
    )
    data_folder = File(
        file_type=FileType.DIRECTORY,
        use=FileGrpUse.DATA.value,
        label=FileGrpUse.DATA.value,
    )

    representation_path = Path("representations", "representation_1")

    # The descriptive metadata file used for fileSec and strutMap
    descr_path_rel = Path(representation_path, "metadata", "descriptive", xml_file_name)
    descr_path = Path(sip_root_folder, descr_path_rel)
    descr_file = File(
        file_type=FileType.FILE,
        use=FileGrpUse.DESCRIPTIVE.value,
        label=FileGrpUse.DESCRIPTIVE.value,
        mimetype=mimetypes.guess_type(descr_path)[0],
        path=str(descr_path_rel),
        size=descr_path.stat().st_size,
        checksum=md5(descr_path),
        created=datetime.fromtimestamp(descr_path.stat().st_ctime),
    )

    # The preservation metadata file used for fileSec and strutMap
    pres_path_rel = Path(representation_path, "metadata", "preservation", xml_file_name)
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

    # The essence file used for fileSec and strutMap
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

    # Add files
    metadata_desc_folder.add_child(descr_file)
    metadata_preserv_folder.add_child(pres_file)
    data_folder.add_child(data_file)

    # Add folders
    metadata_folder.add_child(metadata_desc_folder)
    metadata_folder.add_child(metadata_preserv_folder)

    doc.add_file(metadata_folder)
    doc.add_file(data_folder)

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
            preservation/
        representations/representation_1/
            data/
                essence.ext
            metadata/
                descriptive/
                    file.xml
                preservation/
                    file.xml

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
    "Create descriptive metadata and store it"
    dc_terms = DCTerms(
        watchfolder_message.cp_name, essence_path.stem, essence_path.name
    ).to_element()
    etree.ElementTree(dc_terms).write(
        str(representations_metadata_desc_folder.joinpath(xml_path.name)),
        pretty_print=True,
    )

    # representations/representation_1/metadata/preservation
    representations_metadata_pres_folder = representations_metadata_folder.joinpath(
        "preservation"
    )
    representations_metadata_pres_folder.mkdir(exist_ok=True)
    fixity = Fixity(sidecar.md5).to_element()
    etree.ElementTree(fixity).write(
        str(representations_metadata_pres_folder.joinpath(xml_path.name)),
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
    package_mets_element = create_package_mets(watchfolder_message, root_folder)
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
