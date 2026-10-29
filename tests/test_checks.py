"""The checks must find every problem planted in the messy export."""

import numpy as np
import pandas as pd

from bemlops.checks import check_data
from bemlops.schema import parse_columns


def _report(df, points, target="AHU1_CLG_KW"):
    return check_data(df, parse_columns(points), target)


def test_correct_declarations_have_no_errors(messy_indexed, points):
    df, _ = messy_indexed
    rep = _report(df, points)
    assert rep.ok, str(rep)


def test_wrong_unit_is_an_error_and_names_the_right_unit(messy_indexed, points):
    df, _ = messy_indexed
    points["RM204_ZN_T"] = "zone_air_temperature [degC]"
    issue = _report(df, points).get("unit_mismatch:RM204_ZN_T")
    assert issue.severity == "error" and "degF" in issue.message


def test_planted_problems_are_found(messy_indexed, points):
    df, truth = messy_indexed
    rep = _report(df, points)
    ids = {i.id for i in rep.issues}
    assert {"index:unsorted", "index:duplicates", "index:gaps", "columns:undeclared",
            "text_numbers:OAT", "non_numeric:RM204_CO2", "stuck:RM204_CO2",
            "sentinel:AHU1_CLG_KW", "spikes:RM204_ZN_T"} <= ids
    assert rep.get("index:duplicates").evidence["n"] == truth["duplicates"]
    assert "-999" in rep.get("sentinel:AHU1_CLG_KW").message
    assert f"{truth['kw_sentinels']} readings" in rep.get("sentinel:AHU1_CLG_KW").message
    assert rep.get("non_numeric:RM204_CO2").evidence["values"] == {"OFFLINE": truth["co2_offline"]}
    assert rep.get("spikes:RM204_ZN_T").message.startswith(f"{truth['zone_spikes']} single-sample")
    stuck = rep.get("stuck:RM204_CO2").message
    assert str(truth["co2_stuck"][0].date()) in stuck
    gaps = rep.get("index:gaps").message
    assert "7 h" in gaps


def test_humidity_as_fraction_is_caught():
    idx = pd.date_range("2025-01-01", periods=2000, freq="15min")
    rh = pd.Series(0.45 + 0.1 * np.sin(np.arange(2000) / 50), index=idx)
    df = pd.DataFrame({"rh": rh, "y": rh * 2})
    rep = check_data(df, parse_columns({"rh": "relative_humidity [%]", "y": "other"}), "y")
    assert "fraction" in rep.get("unit_mismatch:rh").message


def test_cumulative_meter_is_caught():
    idx = pd.date_range("2025-01-01", periods=3000, freq="15min")
    reading = pd.Series(np.cumsum(np.random.default_rng(0).uniform(1, 3, 3000)), index=idx)
    rep = check_data(pd.DataFrame({"kwh": reading}), parse_columns({"kwh": "energy [kWh]"}), "kwh")
    assert rep.get("cumulative:kwh").severity == "error"


def test_setpoints_may_be_constant_but_sensors_may_not():
    idx = pd.date_range("2025-01-01", periods=2000, freq="15min")
    df = pd.DataFrame({"sp": 22.0, "t": 22.0, "y": np.arange(2000.0)}, index=idx)
    rep = check_data(df, parse_columns({"sp": "temperature_setpoint [degC]",
                                        "t": "zone_air_temperature [degC]", "y": "other"}), "y")
    ids = {i.id for i in rep.issues}
    assert "stuck:t" in ids and "stuck:sp" not in ids
