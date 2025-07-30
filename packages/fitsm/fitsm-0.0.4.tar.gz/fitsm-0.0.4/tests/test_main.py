import pytest
from datetime import datetime
from fitsm import core


FAKE_CONFIG = {
    "test": {
        "instrument_names": {
            "main": ["name1", "name2", "name3"],
        },
        "definition": {
            "keyword_instrument": "INSTRUMENT",
        },
    }
}


def test_instruments_definitions():

    definitions = core.instruments_definitions(FAKE_CONFIG)

    for name in ["name1", "name2", "name3"]:
        assert name in definitions and definitions[name]["name"] == "main"


def test_get_definition():
    definitions = core.instruments_definitions(FAKE_CONFIG)
    fake_header = {"INSTRUMENT": "name1"}

    definition = core.get_definition(fake_header, ["INSTRUMENT"], definitions)

    assert definition["name"] == "main"


def test_no_config():
    assert core.gat_data_from_header({}, core.get_definition)["instrument"] == "default"
