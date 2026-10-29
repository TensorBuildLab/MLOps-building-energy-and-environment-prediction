# Decoding BAS point names

Point names are written by controls contractors, and every site is
different. Use these abbreviations as a starting point, then **confirm each
guess from the values**: the range, the unit, and the daily pattern.
`check_data()` will flag a declaration that does not fit the values.

## Equipment prefixes

| Abbreviation | Usually means |
|---|---|
| AHU, RTU, MAU, DOAS | Air handling unit, rooftop unit, makeup air unit, dedicated outdoor air system |
| VAV, FCU, UH, CAV | Variable air volume box, fan coil unit, unit heater, constant air volume box |
| CH, CHLR, BLR, HX | Chiller, boiler, heat exchanger |
| CT | Cooling tower **or** current transformer (check the units) |
| CHWP, HWP, CWP | Chilled-water, hot-water, condenser-water pump |
| SF, RF, EF | Supply, return, exhaust fan |
| ERV, HRV | Energy / heat recovery ventilator |
| RM, ZN, SPC | Room, zone, space |
| MTR, EM, WM | Meter, electric meter, water meter |

## Measurements

| Abbreviation | Usually means | Declare as | Typical values |
|---|---|---|---|
| ZN-T, ZNT, ZAT, RMT, SPT, SPC-T | Zone / room / space temperature | `zone_air_temperature` | 68-78 degF / 20-26 degC, daily cycle |
| OAT, OA-T, OADB | Outdoor air dry-bulb temperature | `outdoor_air_temperature` | site climate |
| SAT, DAT, SA-T, DA-T | Supply / discharge air temperature | `supply_air_temperature` | 50-60 degF cooling, up to 90+ degF heating |
| RAT, RA-T | Return air temperature | `return_air_temperature` | close to zone temperature |
| MAT, MA-T | Mixed air temperature | `mixed_air_temperature` | between OAT and RAT |
| CHWST, CHWS-T / CHWRT | Chilled-water supply / return temperature | `water_temperature` | 40-48 / 50-60 degF |
| HWST / HWRT | Hot-water supply / return temperature | `water_temperature` | 120-180 degF |
| RH, ZN-RH, OA-RH | Relative humidity | `relative_humidity` | 20-70 %, sometimes 0-1 |
| CO2, ZN-CO2, PPM | Carbon dioxide | `co2` | ~420 ppm empty, 600-1200 ppm occupied |
| PM25, PM2.5 | Fine particles | `pm25` | ug/m3 |
| KW, DMD | Electric demand | `electric_power` | kW (or W: check the magnitude) |
| KWH, CONS | Electric energy | `energy` | per interval, or cumulative if it only goes up |
| BTU, TON, CLG-LOAD | Thermal load | `thermal_power` (rate) or `energy` (ton-h, kBtu) | |
| CFM, SAF, OAF, L/S | Airflow | `airflow` | |
| GPM | Water flow | `other` (no water-flow quantity yet) | |
| DSP, SA-SP, BSP | Duct / building static pressure | `pressure` | 0.5-2 inH2O duct, ~0.02-0.05 inH2O building |
| OCC, OCC-CNT, PPL | Occupancy count from a people counter | `occupancy_count` | integers |
| OCC, OCC-STS, PIR | Occupancy sensor or occupied mode | `occupancy_status` | 0/1 |

## Setpoints, commands and status

| Abbreviation | Usually means | Declare as |
|---|---|---|
| SP, STPT, CSP, HSP, EFF-SP | Setpoint (cooling, heating, effective) | `temperature_setpoint` (if a temperature) |
| DPR, DMPR, OAD, POS | Damper position or command | `position` |
| VLV, CHW-VLV, HW-VLV | Valve position or command | `position` |
| VFD, SPD, HZ | Fan or pump speed | `position` (%) or `other` (Hz) |
| CMD, SS, EN | Command, start/stop, enable | `equipment_status` |
| STS, ST, PRF | Status / proof of flow | `equipment_status` |
| ALM | Alarm | usually leave undeclared |
| BYP, OVRD, HOA | Bypass, override, hand-off-auto | `other`; overrides often explain odd periods |

## BACnet object types in names

Names like `AI-3`, `AV12.PV` or `.Present_Value` carry the BACnet object type:

| Type | Meaning |
|---|---|
| AI | Analog input: a sensor reading |
| AO | Analog output: a command to a damper, valve or drive |
| AV | Analog value: often a setpoint or calculated value |
| BI | Binary input: a status |
| BO | Binary output: an on/off command |
| BV | Binary value: often a mode (occupied/unoccupied) |
| MSV | Multi-state value: a mode with several states |

`PV` usually means "present value".

## Known ambiguities

- **SP**: setpoint or static pressure. Units settle it (degF vs inH2O).
- **OCC**: a people count, an occupancy sensor, or the scheduled occupied mode.
  Integers above 1 mean a count; 0/1 that changes at the same times every
  weekday is a schedule.
- **CT**: cooling tower or current transformer (amps).
- **T** at the end of a name is nearly always temperature, but check the range.
- Energy points may be per-interval or cumulative. Cumulative values only go
  up, and `check_data()` reports it as a `cumulative` error.

When a point cannot be identified confidently, leave it undeclared and tell
the human which points you skipped.
