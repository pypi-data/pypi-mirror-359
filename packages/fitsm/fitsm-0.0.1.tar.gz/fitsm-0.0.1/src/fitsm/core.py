from pathlib import Path
from astropy.io import fits
from datetime import datetime
from dateutil import parser
from astropy import units as astropy_units
from astropy.coordinates import Angle
from astropy.io.fits import Header
import json


def get_files(folder: str | Path, name: str) -> list[Path]:
    return Path(folder).rglob(name)


def fits_to_dict(fits_header: Header | Path, definition: dict) -> dict:
    # date
    date = fits_header.get(definition["keyword_observation_date"], None)
    date = parser.parse(date) if date else datetime(1800, 1, 1)

    # image type
    im_type = fits_header.get(definition["keyword_image_type"], None)

    type_dict = {
        definition["keyword_light_images"]: "light",
        definition["keyword_dark_images"]: "dark",
        definition["keyword_flat_images"]: "flat",
        definition["keyword_bias_images"]: "bias",
    }

    im_type = type_dict.get(im_type, "")

    def get_deg(key):
        value = fits_header.get(definition[f"keyword_{key}"], None)
        if value is None:
            return -1.0
        else:
            unit = astropy_units.__dict__[definition[f"unit_{key}"]]
            return Angle(value, unit).to(astropy_units.deg).value

    return dict(
        date=date,
        type=im_type,
        exposure=float(fits_header.get(definition["keyword_exposure_time"], -1.0)),
        object=fits_header.get(definition["keyword_object"], ""),
        filter=fits_header.get(definition["keyword_filter"], ""),
        width=fits_header.get("NAXIS1", 1),
        height=fits_header.get("NAXIS2", 1),
        jd=float(fits_header.get(definition["keyword_jd"], -1.0)),
        ra=float(get_deg("ra")),
        dec=float(get_deg("dec")),
    )


def instruments_name_keywords(config: dict) -> list[str]:
    return list(
        set(
            [
                value["definition"]["keyword_instrument"]
                for value in config.values()
                if "keyword_instrument" in value["definition"]
            ]
        )
    )


def instruments_definitions(config: dict) -> dict:
    default_definition = config["default"]["definition"]
    definitions = {}
    for _, value in config.items():
        for main_name, names in value["instrument_names"].items():
            for name in names:
                definitions[name.strip().lower()] = {
                    "name": main_name.strip().lower(),
                    **default_definition,
                    **value["definition"],
                }

    return definitions


def get_definition(
    fits_header: Header, keywords: list = None, definitions: dict = None
) -> dict:
    for keyword in keywords:
        if keyword in fits_header:
            instrument_name = fits_header[keyword].strip().lower()
            if instrument_name not in definitions:
                continue
            else:
                return definitions[instrument_name]

    return definitions["default"]


def get_data(file: Path | str, get_definition: callable) -> dict:
    header = fits.getheader(file)
    definiton = get_definition(header)
    data = fits_to_dict(header, definiton)
    data["path"] = str(file.absolute()) if isinstance(file, Path) else file
    data["instrument"] = definiton["name"]
    _data = data.copy()
    _data["date"] = data["date"].strftime("%Y-%m-%d %H:%M:%S")
    data["hash"] = hash(json.dumps(_data, sort_keys=True))
    return data
