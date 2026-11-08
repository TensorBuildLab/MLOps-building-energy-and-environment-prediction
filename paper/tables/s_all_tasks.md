| Dataset | Task | Chosen | Reference | Skill | Backtest skill | 90% coverage | Gates |
|---|---|---|---|---|---|---|---|
| ROBOD | room1-indoor_co2-30min | persistence | persistence | 0.00 | 0.00 | 90% | refused |
| ROBOD | room1-air_temperature-30min | persistence | persistence | 0.00 | 0.00 | 95% | refused |
| ROBOD | room1-indoor_relative_humidity-30min | persistence | persistence | 0.00 | 0.00 | 91% | refused |
| ROBOD | room1-pm25-30min | ridge | persistence | 0.14 | 0.11 | 78% | passed |
| ROBOD | room1-occupant_count-30min | persistence | persistence | 0.00 | 0.00 | 98% | refused |
| ROBOD | room1-occupant_presence-30min | persistence | persistence | 0.00 | 0.00 | – | refused |
| ROBOD | room1-occupant_count-now | random forest | training mean | 0.76 | 0.47 | 99% | passed |
| ROBOD | room1-chilled_water_energy-1h | gbm change | persistence | −0.15 | −0.02 | 93% | refused |
| ROBOD | room1-plug_load_energy-1h | gbm | time of day profile | 0.19 | 0.14 | 82% | refused |
| ROBOD | room2-indoor_co2-30min | gbm change | persistence | 0.15 | 0.06 | 91% | passed |
| ROBOD | room2-air_temperature-30min | persistence | persistence | 0.00 | 0.00 | 86% | refused |
| ROBOD | room2-indoor_relative_humidity-30min | ridge | persistence | −0.16 | −0.06 | 88% | refused |
| ROBOD | room2-pm25-30min | ridge | persistence | 0.19 | 0.11 | 79% | passed |
| ROBOD | room2-occupant_count-30min | ridge | persistence | 0.39 | 0.30 | 88% | passed |
| ROBOD | room2-occupant_presence-30min | persistence | persistence | 0.00 | 0.00 | – | refused |
| ROBOD | room2-occupant_count-now | ridge | time of day profile | 0.36 | 0.35 | 84% | passed |
| ROBOD | room2-chilled_water_energy-1h | persistence | persistence | 0.00 | 0.00 | 75% | refused |
| ROBOD | room2-plug_load_energy-1h | gbm | time of day profile | 0.16 | 0.11 | 94% | refused |
| ROBOD | room3-indoor_co2-30min | gbm change | persistence | 0.04 | 0.03 | 95% | refused |
| ROBOD | room3-air_temperature-30min | gbm change | persistence | 0.18 | 0.21 | 91% | passed |
| ROBOD | room3-indoor_relative_humidity-30min | gbm change | persistence | 0.36 | 0.18 | 99% | passed |
| ROBOD | room3-pm25-30min | ridge | persistence | −0.17 | 0.01 | 91% | refused |
| ROBOD | room3-occupant_count-30min | gbm | persistence | −0.17 | 0.03 | 91% | refused |
| ROBOD | room3-occupant_presence-30min | random forest | persistence | −0.09 | 0.09 | – | refused |
| ROBOD | room3-occupant_count-now | gbm | time of day profile | 0.06 | 0.20 | 71% | passed |
| ROBOD | room3-chilled_water_energy-1h | gbm change | persistence | 0.49 | 0.30 | 96% | passed |
| ROBOD | room3-plug_load_energy-1h | persistence | persistence | 0.00 | 0.00 | 88% | refused |
| ROBOD | room4-indoor_co2-30min | gbm | persistence | 0.27 | 0.28 | 93% | passed |
| ROBOD | room4-air_temperature-30min | gbm change | persistence | 0.25 | 0.25 | 92% | passed |
| ROBOD | room4-indoor_relative_humidity-30min | random forest | persistence | 0.60 | 0.62 | 88% | passed |
| ROBOD | room4-pm25-30min | gbm change | persistence | 0.05 | 0.07 | 94% | passed |
| ROBOD | room4-occupant_count-30min | random forest | persistence | 0.18 | 0.17 | 92% | passed |
| ROBOD | room4-occupant_presence-30min | persistence | persistence | 0.00 | 0.00 | – | refused |
| ROBOD | room4-occupant_count-now | ridge | time of day profile | 0.00 | 0.02 | 96% | refused |
| ROBOD | room4-chilled_water_energy-1h | random forest | time of day profile | 0.24 | 0.23 | 90% | refused |
| ROBOD | room4-plug_load_energy-1h | gbm change | time of day profile | −0.01 | 0.03 | 83% | refused |
| ROBOD | room5-indoor_co2-30min | gbm change | persistence | −0.01 | 0.08 | 97% | refused |
| ROBOD | room5-air_temperature-30min | gbm | persistence | 0.30 | 0.27 | 89% | passed |
| ROBOD | room5-indoor_relative_humidity-30min | gbm | persistence | 0.44 | 0.41 | 90% | passed |
| ROBOD | room5-pm25-30min | random forest | persistence | 0.09 | 0.11 | 91% | passed |
| ROBOD | room5-occupant_count-30min | gbm change | persistence | 0.09 | 0.05 | 98% | passed |
| ROBOD | room5-occupant_presence-30min | persistence | persistence | 0.00 | 0.00 | – | refused |
| ROBOD | room5-occupant_count-now | gbm | time of day profile | 0.53 | 0.33 | 98% | passed |
| ROBOD | room5-chilled_water_energy-1h | time of day profile | time of day profile | 0.00 | 0.00 | 81% | refused |
| ROBOD | room5-plug_load_energy-1h | persistence | persistence | 0.00 | 0.00 | 77% | refused |
| Aalborg | rooma-sensor-co2-1h | gbm change | persistence | 0.18 | 0.18 | 92% | passed |
| Aalborg | rooma-sensor-roomtemperature-1h | ridge | persistence | 0.07 | 0.08 | 93% | passed |
| Aalborg | rooma-people-amount-1h | gbm change | persistence | 0.16 | 0.14 | 91% | passed |
| Aalborg | rooma-room-active-1h | gbm | persistence | 0.32 | 0.38 | – | passed |
| Aalborg | roomb-sensor-co2-1h | gbm change | persistence | 0.08 | 0.09 | 92% | passed |
| Aalborg | roomb-sensor-roomtemperature-1h | gbm | persistence | −0.51 | −0.06 | 66% | refused |
| Aalborg | roomb-people-amount-1h | ridge | persistence | 0.19 | 0.16 | 84% | passed |
| Aalborg | roomb-room-active-1h | gbm | persistence | 0.25 | 0.26 | – | passed |
| Aalborg | roomc-sensor-co2-1h | gbm | persistence | 0.11 | 0.09 | 91% | passed |
| Aalborg | roomc-sensor-roomtemperature-1h | persistence | persistence | 0.00 | 0.00 | 90% | refused |
| Aalborg | roomc-people-amount-1h | gbm | time of day profile | 0.02 | 0.08 | 84% | refused |
| Aalborg | roomc-room-active-1h | gbm | persistence | 0.25 | 0.21 | – | passed |
| Aalborg | roomd-sensor-co2-1h | gbm change | persistence | 0.11 | 0.14 | 90% | passed |
| Aalborg | roomd-sensor-roomtemperature-1h | ridge | persistence | 0.06 | 0.13 | 79% | passed |
| Aalborg | roomd-people-amount-1h | gbm change | time of day profile | −0.01 | 0.07 | 87% | refused |
| Aalborg | roomd-room-active-1h | gbm | persistence | 0.31 | 0.36 | – | passed |
| Aalborg | roome-sensor-co2-1h | gbm change | persistence | 0.15 | 0.14 | 94% | passed |
| Aalborg | roome-sensor-roomtemperature-1h | ridge | persistence | −1.03 | 0.05 | 47% | refused |
| Aalborg | roome-people-amount-1h | time of day profile | time of day profile | 0.00 | 0.00 | 91% | refused |
| Aalborg | roome-room-active-1h | gbm | persistence | 0.31 | 0.36 | – | passed |
| Aalborg | roomf-sensor-co2-1h | gbm change | persistence | 0.18 | 0.17 | 94% | passed |
| Aalborg | roomf-sensor-roomtemperature-1h | gbm change | persistence | 0.08 | 0.07 | 93% | passed |
| Aalborg | roomf-people-amount-1h | ridge | persistence | −0.12 | −0.03 | 85% | refused |
| Aalborg | roomf-room-active-1h | logistic | persistence | 0.24 | 0.30 | – | passed |
| Aalborg | ventilation-elmeter-power-1h | gbm change | persistence | 0.46 | 0.43 | 91% | passed |
| Aalborg | heating-dh-power-1h | ridge | persistence | 0.19 | 0.22 | 26% | passed |
| Aalborg | heating-dh-power-24h | ridge | persistence | 0.12 | 0.12 | 28% | passed |
| BDG2 | Bear_education_Chana | gbm | time of day profile | 0.40 | 0.38 | 88% | passed |
| BDG2 | Bear_education_Wilton | ridge | persistence | 0.13 | 0.10 | 86% | passed |
| BDG2 | Bobcat_lodging_Nickolas | ridge | persistence | 0.05 | 0.07 | 87% | refused |
| BDG2 | Bobcat_other_Timothy | gbm | persistence | 0.23 | 0.25 | 61% | passed |
| BDG2 | Bull_lodging_Allen | persistence | persistence | 0.00 | 0.00 | 84% | refused |
| BDG2 | Bull_lodging_Jeremiah | gbm change | persistence | 0.48 | 0.46 | 89% | passed |
| BDG2 | Cockatoo_office_Jodie | gbm | time of day profile | 0.37 | 0.41 | 67% | passed |
| BDG2 | Cockatoo_public_Caleb | ridge | persistence | 0.29 | 0.41 | 88% | passed |
| BDG2 | Crow_education_Winston | ridge | persistence | 0.16 | 0.13 | 92% | passed |
| BDG2 | Eagle_education_Samantha | time of day profile | time of day profile | 0.00 | 0.00 | 73% | refused |
| BDG2 | Fox_office_Clayton | gbm | persistence | 0.34 | 0.29 | 93% | passed |
| BDG2 | Gator_public_Dionna | time of day profile | time of day profile | 0.00 | 0.00 | 44% | refused |
| BDG2 | Hog_office_Elke | gbm change | time of day profile | 0.51 | 0.37 | 97% | passed |
| BDG2 | Lamb_education_Princess | persistence | persistence | 0.00 | 0.00 | 69% | refused |
| BDG2 | Moose_education_Rene | gbm | time of day profile | 0.11 | 0.22 | 91% | passed |
| BDG2 | Mouse_lodging_Vicente | gbm | time of day profile | 0.00 | 0.10 | 94% | refused |
| BDG2 | Peacock_education_Anita | ridge | persistence | 0.33 | 0.34 | 93% | passed |
| BDG2 | Rat_education_Colin | gbm | persistence | −5.15 | −0.89 | 37% | refused |
| BDG2 | Robin_education_Audrea | ridge | persistence | 0.03 | 0.07 | 86% | refused |
| BDG2 | Wolf_office_Elisabeth | time of day profile | time of day profile | 0.00 | 0.00 | 80% | refused |
