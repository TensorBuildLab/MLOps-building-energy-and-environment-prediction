| Planted fault | Detected as | Detection rate |
|---|---|---|
| unit change mid-series (degC to degF) | out_of_range:RoomA:Sensor__room_temperature | 100% |
| stuck sensor (3 days) | stuck:Ventilation:EL_meter__power | 50% |
| 10 single-sample spikes | spikes:Outdoor:Temperature_air | 90% |
| 20 placeholder values (-999) | sentinel:RoomA:Sensor__CO2 | 100% |
| 20 'OFFLINE' text entries | non_numeric:Outdoor:Wind__velocity | 100% |
| 12-hour outage | index:gaps | 100% |
| one day of rows exported twice | index:duplicates | 100% |
| 30 rows out of order | index:unsorted | 100% |
