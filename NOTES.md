# What I checked, and what the agent got wrong

## What I checked

1. In km_wachter.py:

i. The normal division ( / ) viz, 14,900 / 15,000 = 0.993 keeps the full answer, so wear = 99%.
But the older code had whole-number division ( // ) viz, 14,900 // 15,000 = 0 throws the decimal away, so wear = 0%, which was incorrect and gives flawed output.

ii. The needs_service function had `last = car.get("last_service_km", car["odometer"])` treating the last reading as 0 km if last_service_km is missing. Hence the code was then corrected to `if "last_service_km" not in car: return False` to avoid this error. The agent's first fix for the missing-reading bug used `car.get("last_service_km", car["odometer"])` as a default. This passed the tests but the intent was wrong — defaulting to the odometer pretends the car was just serviced, which is not the same as saying the history is unknown. I noticed the mismatch between the code and the explanation and asked about it. It was corrected to an explicit key check: `if "last_service_km" not in car: return False`.

2. In fleet_report.py,
The whole number division again gave wrong output in average hence // was changed to /.

3. In fleet_utils.py,
1.609 is the km-per-mile conversion (how many km are in one mile), used backwards. So km_to_miles(100) was returning 160.9 instead of 62.1 where every nightly UK partner report showed distances roughly 2.6× too large. We changed it to 0.621371 (the correct miles-per-km factor).

4. The agent put a `→` arrow character in analyze.py which crashed immediately on Windows with a UnicodeEncodeError. It had to be changed to a plain `->`.

## What I checked before I accepted its work

- Ran `python verify.py` and read every line of output before and after the fixes.
- Checked that `SERVICE_INTERVAL_KM = 15000` and `WARN_AT_PERCENT = 80` were untouched in `km_wachter.py` and that `settings.cfg` still had the same values — both confirmed by verify.py checks 4 and 5.
- Traced `wear_percent(14900, 15000)` by hand: `14900 / 15000 * 100 = 99.33` — above 80%, so the car is correctly flagged.
- Traced `needs_service({"id": "VOS-7788", "odometer": 92000})` with the fixed code: key absent → returns False immediately, car is not flagged.
- Ran `python -m pytest test_km_wachter.py test_fleet_report.py -v` and confirmed all 4 tests pass, as shown below.
  Test	Result
test_almost_due_car_is_flagged	✅ PASSED
test_missing_reading_is_not_treated_as_zero	✅ PASSED
test_summary_counts_due_cars	✅ PASSED
test_summary_does_not_crash_on_missing_reading	✅ PASSED
- Ran `python analyze.py` and confirmed it prints the full ranking without errors.

## What the data actually said

I read the CSV first with Python's built-in csv module to see the column names and value ranges. Then I compared the mean of every column between the broke-down group and the fine group, and ran an above-median test — what share of broke-down cars sit above the fine-group median for each column. A column that separates nothing gives about 50%.

The results:
odometer_km and age_years are noise - 0% and -0% gap, 50% and 42% above-median. Exactly what you'd expect from a coin flip.
km_since_service is the dominant signal - 61% mean gap, 85% of broke-down cars above the fine-group median.
Top 10: 8 out of 10 actually broke down , the score is picking the right cars.
Sanity check: 65% recall vs 22% for random guessing, with no machine learning — just three weighted columns.
- `odometer_km`: 50% above-median, 0.3% mean gap - coin flip, not predictive.
- `age_years`: 42% above-median, -0.2% mean gap - lso noise, slightly negative.
- `km_since_service`: 85% above-median, 61% mean gap - strongest signal by far.
- `load_factor`: 77% above-median, 19% mean gap - second strongest.
- `avg_daily_km`: 62% above-median, 22% mean gap - third.

The obvious assumption — that older, higher-mileage cars break down more — is not what the data shows. Total mileage and age are indistinguishable between the two groups. What separates them is how overdue the car is for a service, how hard it is driven daily, and how heavily it is loaded.

The risk score weights those three columns by their mean-gap percentages (61/22/19), min-max normalises each one, and rescales the result to 0–100. The top 26 cars by score captured 17 of the 26 real breakdowns — 65% recall compared to 22% for random guessing.
