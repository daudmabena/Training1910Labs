# Day 4 Labs: Forecasting Contributions and Payouts

The Fund's finance and investment teams plan months ahead. How much cash will come in from contributions?
How much will go out in benefits? A good forecast doesn't need to be perfect. It needs to be **better than
the obvious guess**, and **honest about its uncertainty**.

That's the rule for the whole day:

> Never report a forecast's accuracy on its own. Always compare it with a naive baseline, and always show
> a range, not just a line.

## Today's labs

| Lab | File | Time |
|---|---|---|
| 1. Forecasting monthly contribution inflows | `Lab1_Contribution_Inflows.ipynb` | about 75 min |
| 2. Forecasting benefit payouts with XGBoost | `Lab2_Payouts_XGBoost.ipynb` | about 60 min |
| 3. Testing forecasts over several years, and a planning pack | `Lab3_Backtesting_and_Planning_Pack.ipynb` | about 75 min |

## Files in this folder

| File | What it is |
|---|---|
| `contributions_monthly_clean.csv` | One row per employer per wage month, 2017-2025: amount due, amount paid, due date, payment date. This is the cleaned version of the table you worked with on Day 1. |
| `benefit_payouts_monthly.csv` | Benefits paid per month and benefit type, 2017-2025: number of beneficiaries and amount |
| `requirements.txt` | Today's libraries |

## Setup

Open `Lab1_Contribution_Inflows.ipynb` and run its first code cell. It finds the course environment you built on Day 1,
installs today's libraries into it, and tells you if the notebook needs switching to the
**Python (fund-ai)** kernel. If it asks you to switch, do that and run the cell once more. You can run it as
often as you like; it only installs what's missing.

Prophet installs a small compiled component (CmdStan) the first time it's imported. If `from prophet import
Prophet` fails on Windows, try `python -m pip install --upgrade prophet`, or use conda:
`conda install -c conda-forge prophet`. If you still can't get it working, skip the Prophet cells. Every
other part of today's labs runs without it.

## A word about the Fund's calendar

Tanzania's government financial year runs from **1 July to 30 June**, and the Fund's compliance team pushes
hard to collect arrears before year-end. You'll see that in the data as a jump in cash received every June.
Whether a forecast should include it depends on the question: *contributions due* (what employers owe for a
month) or *cash received* (what lands in the bank that month). Finance usually wants the second. Keep asking
which one you're forecasting.
