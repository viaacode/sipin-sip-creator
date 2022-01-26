from pathlib import Path
import shutil

import bagit

from app.helpers.events import WatchfolderMessage


def create_sip_bag(watchfolder_message: WatchfolderMessage):
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
        representations/representations1/
            data/
                essence.ext
            metadata/
                descriptive/
                    file.xml
                preservation/
                    file.xml

    Args:
        watchfolder_message: The parse watchfolder message.
    """
    essence_path: Path = watchfolder_message.get_essence_path()
    xml_path = watchfolder_message.get_xml_path()
    if not essence_path.exists() or not xml_path.exists():
        # TODO: raise error
        return

    # Root folder for bag
    root_folder = Path(essence_path.parent, essence_path.stem)
    root_folder.mkdir(exist_ok=True)
    # TODO: Create and write mets.xml

    # /metadata
    metadata_folder = root_folder.joinpath("metadata")
    metadata_folder.mkdir(exist_ok=True)
    # /metadata/descriptive/
    metadata_desc_folder = metadata_folder.joinpath("descriptive")
    metadata_desc_folder.mkdir(exist_ok=True)
    # /metadata/preservation/
    metadata_pres_folder = metadata_folder.joinpath("preservation")
    metadata_pres_folder.mkdir(exist_ok=True)
    # /representations/representations1/
    representations_folder = root_folder.joinpath("representations", "representations1")
    representations_folder.mkdir(exist_ok=True, parents=True)
    # /representations/representations1/data/
    representations_data_folder = representations_folder.joinpath("data")
    representations_data_folder.mkdir(exist_ok=True)
    # Move essence
    essence_path.replace(representations_data_folder.joinpath(essence_path.name))

    # representations/representations1/metadata/
    representations_metadata_folder = representations_folder.joinpath("metadata")
    representations_metadata_folder.mkdir(exist_ok=True)
    # representations/representations1/metadata/descriptive
    representations_metadata_desc_folder = representations_metadata_folder.joinpath(
        "descriptive"
    )
    representations_metadata_desc_folder.mkdir(exist_ok=True)
    # TODO: Create descriptive metadata

    # representations/representations1/metadata/preservation
    representations_metadata_pres_folder = representations_metadata_folder.joinpath(
        "preservation"
    )
    representations_metadata_pres_folder.mkdir(exist_ok=True)
    # TODO: create preservation metadata and store it

    # Make bag
    bagit.make_bag(root_folder, checksums=["md5"])

    # Zip bag
    shutil.make_archive(
        essence_path.parent.joinpath(essence_path.stem).with_suffix(".bag"),
        "zip",
        root_folder,
    )

    # Remove root folder
    shutil.rmtree(root_folder)