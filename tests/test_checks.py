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


def test_runs_and_spikes_never_span_gaps():
    """Found on ROBOD (weekdays only): equal values either side of a weekend are not a stuck sensor,
    and the first reading after a long gap is not a spike."""
    from bemlops.cleaning import spike_mask, stuck_runs

    rng = np.random.default_rng(1)
    fri = pd.date_range("2021-09-17 18:00", "2021-09-17 23:55", freq="5min")
    mon = pd.date_range("2021-09-20 00:00", "2021-09-20 05:55", freq="5min")
    idx = fri.append(mon)
    s = pd.Series(np.r_[20 + rng.normal(0, 0.1, len(fri) - 3), [1, 1, 1], [1, 1, 1], 26 + rng.normal(0, 0.1, len(mon) - 3)],
                  index=idx)
    assert stuck_runs(s, pd.Timedelta(hours=6), ignore_zero=False) == []
    # Monday's first readings are judged only against Monday's readings, never against Friday's.
    assert not spike_mask(s).iloc[len(fri):len(fri) + 3].any()


def test_flat_ok_and_change_of_value_hint():
    """Found on Aalborg: CO2 logged on change of value looks 'stuck' for hours. The warning should say so,
    and a flat_ok declaration should switch the check off for that column only."""
    idx = pd.date_range("2023-03-01", periods=4000, freq="5min")
    steps = np.repeat(np.r_[420.0, 455.0, 490.0, 455.0], 1000)  # changes rarely, by ~35 ppm
    df = pd.DataFrame({"co2": steps, "y": np.arange(4000.0)}, index=idx)
    rep = check_data(df, parse_columns({"co2": "co2 [ppm]", "y": "other"}), "y")
    issue = rep.get("stuck:co2")
    assert "change-of-value" in issue.message and "flat_ok" in issue.fix
    rep2 = check_data(df, parse_columns({"co2": {"quantity": "co2", "unit": "ppm", "flat_ok": True}, "y": "other"}), "y")
    assert "stuck:co2" not in {i.id for i in rep2.issues}


def test_seasonal_inputs_need_a_full_year():
    from bemlops.features import build_features

    specs = parse_columns({"y": "other"})
    for days, expected in ((200, False), (400, True)):
        idx = pd.date_range("2022-01-01", periods=days * 24, freq="1h")
        X, _, _ = build_features(pd.DataFrame({"y": np.arange(len(idx), dtype=float)}, index=idx), "y", specs, 1,
                                 pd.Timedelta("1h"))
        assert ("doy_sin" in X.columns) == expected


def test_unit_switch_is_located_and_sparse_meters_are_not_cumulative():
    idx = pd.date_range("2025-01-01", periods=3000, freq="15min")
    t = 21 + np.sin(np.arange(3000) / 40)
    t[2000:] = t[2000:] * 9 / 5 + 32  # switched to degF
    rep = check_data(pd.DataFrame({"t": t, "y": 1.0}, index=idx),
                     parse_columns({"t": "zone_air_temperature [degC]", "y": "other"}), "y")
    issue = rep.get("out_of_range:t")
    assert "degF" in issue.message and str(idx[2000].date()) in issue.message
    sparse = np.zeros(3000)
    sparse[::25] = np.random.default_rng(0).uniform(1, 2, 120)
    rep2 = check_data(pd.DataFrame({"e": sparse}, index=idx), parse_columns({"e": "energy [kWh]"}), "e")
    assert "cumulative:e" not in {i.id for i in rep2.issues}


def test_duplicated_rows_do_not_hide_stuck_sensors():
    idx = pd.date_range("2025-01-01", periods=2000, freq="5min")
    v = 450 + np.random.default_rng(0).normal(0, 5, 2000)
    v[500:800] = 612.0
    df = pd.DataFrame({"c": v, "y": 1.0}, index=idx)
    twice = pd.concat([df, df])
    rep = check_data(twice, parse_columns({"c": "co2 [ppm]", "y": "other"}), "y")
    assert "stuck:c" in {i.id for i in rep.issues}
