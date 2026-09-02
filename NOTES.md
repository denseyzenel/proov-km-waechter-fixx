# What I checked, and what the agent got wrong

## What the agent got wrong

There were five concrete bugs in the codebase, not one. The agent initially missed several of them:

1. **Integer division in wear_percent (km_wachter.py)**
The original code used `//` (floor division): `ratio = km_since_service // interval`, then multiplied by 100. For a car at 14,900 km with a 15,000 km interval that gives `14900 // 15000 = 0`, so the car reports 0% wear and is never flagged. The fix was to use true float division: `(km_since_service / interval) * 100`, which correctly returns ~99.3%.

2. **Missing-reading handling in needs_service (km_wachter.py)**
The original used `car.get("last_service_km", 0)`, treating a missing reading as 0 km. For VOS-7788 with odometer 92,000 and no `last_service_km`, that means 92,000 km since last service — 613% wear — so the car is wrongly flagged as needing service. The fix: if the key is absent, return False immediately. You cannot flag a car whose service history is unknown. The agent's first attempt used `car.get("last_service_km", car["odometer"])` which passed the tests but obscured the intent — I caught the mismatch and had it corrected to an explicit key check.

3. **Crash in fleet_report.car_wear on missing reading (fleet_report.py)**
`car["last_service_km"]` raises a KeyError the moment any car lacks that key. The fix was to check explicitly for the key and return 0.0 if it is absent.

4. **Integer division killing the average in fleet_report.fleet_summary (fleet_report.py)**
`average = total // len(fleet)` drops all decimal places. For the two-car test case the true average is ~59.67% but the code returned 0. Changed `//` to `/`.

5. **Inverted km-to-miles constant (fleet_utils.py)**
`MILES_PER_KM = 1.609` is actually km per mile (the wrong direction). 100 km was reported as 160.9 miles instead of 62.1 miles. The correct constant is 0.621371 (1 / 1.609344). The comment in the file even asked "is that right?" — it was not.

## What I checked before I accepted its work

- Ran `python verify.py` before and after every change and compared the output line by line.
- Confirmed `SERVICE_INTERVAL_KM = 15000` and `WARN_AT_PERCENT = 80` are untouched in `km_wachter.py` and that `settings.cfg` still reads `service_interval_km = 15000` and `warn_at_percent = 80`.
- Manually traced `wear_percent(14900, 15000)` by hand: `14900 / 15000 * 100 = 99.33` — above the 80% threshold, so the car is correctly flagged.
- Traced `needs_service({"id": "VOS-7788", "odometer": 92000})` with the new code: key absent → returns False immediately.
- Verified that `0.621371 * 100 = 62.1371`, which is in the 61–63.5 range the check requires.
- Ran `python analyze.py` to confirm it prints the full ranking without errors.
- Ran `python -m pytest test_km_wachter.py test_fleet_report.py -v` to confirm all unit tests pass, including the new missing-reading test.

## What the data actually said

The obvious guess — that high-mileage or older cars break down more — is wrong in this dataset. The mean `odometer_km` is 53,448 km for cars that broke down versus 53,302 km for those that did not (a difference of 146 km over 120 cars — essentially noise). The mean `age_years` is 5.88 vs 5.89 — indistinguishable.

The three factors that actually separate the groups are:

- **km_since_service**: +4,417 km higher in the broke-down group (11,678 vs 7,261). Cars that are well into their service interval break down more.
- **avg_daily_km**: +28 km/day higher (160 vs 131). Cars driven harder every day are at more risk.
- **load_factor**: +0.09 higher (0.60 vs 0.51). Higher utilisation correlates with breakdown.

The risk score in `analyze.py` min-max normalises those three columns and averages them into a 0–100 score. The top 26 cars by risk capture 65% of all actual breakdowns, compared to 22% for random guessing. This lets the team act on the riskiest cars before the 80% wear rule would ever raise a flag.
