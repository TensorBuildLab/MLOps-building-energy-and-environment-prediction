import numpy as np
import pandas as pd
import pytest

from bemlops.cleaning import coerce_numeric
from bemlops.quantities import get_quantity, normalize_unit, to_canonical
from bemlops.schema import ColumnSpec, parse_columns, parse_spec


def test_shorthand_forms():
    assert parse_spec("a", "zone_air_temperature [degF]").unit == "degF"
    s = parse_spec("b", "cooling load, kW")
    assert (s.quantity, s.unit) == ("thermal_power", "kW")
    assert parse_spec("c", "co2").unit == "ppm"  # only one possible unit
    assert parse_spec("d", "Room Temperature (°C)").quantity == "zone_air_temperature"
    assert parse_spec("d", "Room Temperature (°C)").unit == "degC"


def test_dict_and_spec_forms():
    specs = parse_columns({
        "x": {"quantity": "outdoor_air_temperature", "unit": "F", "known_ahead": True},
        "y": ColumnSpec("other_name", "co2"),
    })
    assert specs["x"].unit == "degF" and specs["x"].known_ahead
    assert specs["y"].name == "y"


def test_unknown_quantity_lists_options():
    with pytest.raises(ValueError, match="Known quantities"):
        parse_spec("z", "flux capacitance [GW]")


def test_unit_conversions():
    q = get_quantity("zone_air_temperature")
    assert np.allclose(to_canonical(np.array([32.0, 212.0]), q, "degF"), [0.0, 100.0])
    assert np.isclose(to_canonical(np.array([1.0]), get_quantity("thermal_power"), "ton")[0], 3.5168525)
    assert normalize_unit("°F") == "degF" and normalize_unit("BTU/hr") == "Btu/h"


def test_coerce_text_numbers_words_and_junk():
    s = pd.Series(["72.5 °F", "1,234.5", "OFFLINE", "N/A", None, 3, "-4e1"])
    co = coerce_numeric(s)
    assert co.values.tolist()[:2] == [72.5, 1234.5]
    assert np.isnan(co.values.iloc[2]) and np.isnan(co.values.iloc[4])
    assert co.values.iloc[6] == -40.0
    assert co.unparseable == {"OFFLINE": 1, "N/A": 1}
    status = coerce_numeric(pd.Series(["On", "OFF", "Occupied", "1"]), binary=True)
    assert status.values.tolist() == [1.0, 0.0, 1.0, 1.0]


def test_decimal_commas_are_never_guessed():
    co = coerce_numeric(pd.Series(["21,5", "1,234", "1.234,5", "22.0"]))
    assert np.isnan(co.values.iloc[0]) and co.values.iloc[1] == 1234.0 and np.isnan(co.values.iloc[2])
    assert set(co.decimal_comma) == {"21,5", "1.234,5"}


def test_timestamps_dst_offsets_and_bad_formats():
    from bemlops.schema import to_time_index

    df = pd.DataFrame({"t": ["2023-03-26T01:55:00+0100", "2023-03-26T03:00:00+0200", "2023-03-26T03:05:00+0200"],
                       "v": [1, 2, 3]})
    out, _ = to_time_index(df, "t", "%Y-%m-%dT%H:%M:%S%z", tz="Europe/Copenhagen")
    assert str(out.index.tz) == "Europe/Copenhagen" and out.index[1].hour == 3
    day_first = pd.DataFrame({"t": [f"{d:02d}/03/2024 10:00" for d in range(1, 29)], "v": range(28)})
    with pytest.raises(ValueError, match="could not be read"):
        to_time_index(day_first, "t", "%m/%d/%Y %H:%M")
    with pytest.raises(ValueError, match="numeric index"):
        to_time_index(pd.DataFrame({"v": [1, 2]}))
    with pytest.raises(ValueError, match="not found"):
        to_time_index(pd.DataFrame({"v": [1, 2]}), "Timestamp")


def test_shorthand_flags():
    s = parse_spec("c", "co2 [ppm] flat_ok")
    assert s.flat_ok and s.unit == "ppm"
    assert parse_spec("o", "outdoor temperature [degC], known_ahead").known_ahead
