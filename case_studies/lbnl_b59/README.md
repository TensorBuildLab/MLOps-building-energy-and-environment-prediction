# LBNL Building 59 (optional case study)

A three-year (2018–2020) operational dataset from an office building in
Berkeley, California: end-use electricity, 51 zone temperatures, zone CO2,
setpoints, rooftop-unit and heat-pump data, camera and Wi-Fi occupancy
counts, and weather.

- Paper: Luo, N., Wang, Z., Blum, D., Weyandt, C., Bourassa, N., Piette, M.A.,
  Hong, T., 2022. A three-year dataset supporting research on building energy
  management and occupancy analytics. *Scientific Data* 9, 156.
  https://doi.org/10.1038/s41597-022-01257-x
- Data: Hong, T., Luo, N., Blum, D., Wang, Z., 2022. Dryad.
  https://doi.org/10.7941/D1N33Q (licence CC0 1.0)

## Why it is not in the automatic case studies

Dryad does not allow scripted downloads without an account: its download API
needs a bearer token, and the web link refuses non-browser clients. The other
case studies (Aalborg, ROBOD, BDG2) download automatically.

## Manual steps

1. Open https://doi.org/10.7941/D1N33Q in a browser and download
   `Building_59.zip` (263,162,077 bytes).
2. Put it in `data/raw/lbnl_b59/Building_59.zip`.
3. Check it: SHA-256
   `1e224dd7479bb196a8e0368fceb70aa6f699c1d39e1e895ceba7f3b25150b1b4`.

Alternatively, create a Dryad API account (self-service under "My account")
and use its client credentials to get a token.

## Known issues to handle (from the dataset documentation and our review)

- The time zone is not documented. The data looks like UTC: solar radiation is
  non-zero at 00:00, and occupancy logging starts at 07:00. Check daily profiles
  before declaring.
- Timestamp formats differ between files (`YYYY-MM-DD HH:MM:SS` and `YYYY/M/D H:MM`).
- The "clean" data were gap-filled by the authors (linear, KNN or matrix
  factorization), without flags. Report this as a limitation.
- Interior temperature loggers are documented as degF but look like degC. This is
  exactly what `check_data()` is for.
- There is no whole-building meter; the total is the sum of the end uses in `ele.csv`.
- Periods to treat with care: wildfire outdoor-air closures (2018-11-12 to
  11-20 and 2020-08-24 to 09-06), COVID shelter-in-place from 2020-03-18, MPC
  tests from October to December 2020, and a heat-pump replacement in March 2019.

A loader will be added once the data has been downloaded and checked.
