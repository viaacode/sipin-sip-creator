#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import pytest

from app.helpers.events import WatchfolderMessage, InvalidMessageException
from tests.helpers import load_resource


folder = Path("tests", "resources", "watchfolder")


def _load_resource(filename):
    return load_resource(folder.joinpath(filename))


def test_message_valid():
    event = WatchfolderMessage(_load_resource("message.json"))
    assert event.cp_name == "CPFIELD"
    assert event.flow_id == "FLOWFIELD"
    essence_file = event.essence_file
    assert essence_file.file_name == "file.mxf"
    assert essence_file.file_path == "/path/to/essence/file"
    assert essence_file.md5 == "5"

    xml_file = event.xml_file
    assert xml_file.file_name == "file.mxf.xml"
    assert xml_file.file_path == "/path/to/xml/file"
    assert xml_file.md5 == "1"


def test_message_invalid_json():
    with pytest.raises(InvalidMessageException) as e:
        WatchfolderMessage(_load_resource("message_invalid.json"))
    assert (
        str(e.value)
        == "Message is not valid JSON: 'Expecting value: line 1 column 1 (char 0)'"
    )


def test_message_missing_key():
    with pytest.raises(InvalidMessageException) as e:
        WatchfolderMessage(_load_resource("message_missing_cp_name.json"))
    assert str(e.value) == "Missing mandatory key: 'cp_name'"
