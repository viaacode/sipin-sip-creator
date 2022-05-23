#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from json import JSONDecodeError


class InvalidMessageException(Exception):
    pass


class WatchfolderMessage:
    """Class representing an incoming watchfolder message

    Args:
        message: The incoming watchfolder message.
    """

    def __init__(self, message: bytes):
        try:
            msg: dict = json.loads(message)
        except JSONDecodeError as e:
            raise InvalidMessageException(f"Message is not valid JSON: '{e}'")
        try:
            self.cp_name = msg["cp_name"]
            self.flow_id = msg["flow_id"]
            self.essence_file = SIPItem(msg["sip_package"][0])
            self.xml_file = SIPItem(msg["sip_package"][1])
        except KeyError as e:
            raise InvalidMessageException(f"Missing mandatory key: {e}")

    def get_essence_path(self) -> Path:
        """Return the path of the essence file.

        Returns: The essence file as a Path.
        """

        return Path(self.essence_file.file_path, self.essence_file.file_name)

    def get_xml_path(self) -> Path:
        """Return the path of the metadata file.

        Returns: The metadata file as a Path.
        """

        return Path(self.xml_file.file_path, self.xml_file.file_name)


class SIPItem:
    """Class representing the information of a SIP item

    This is a composite part of the watchfolder message.

    Args:
        message: The SIP item.
    """

    def __init__(self, sip_item: dict):
        self.file_name = sip_item["file_name"]
        self.file_path = sip_item["file_path"]
