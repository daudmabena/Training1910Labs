"""Fund data pipeline: load -> clean -> validate -> transform -> outputs.

Usage:
    python src/fund_pipeline.py --raw <folder with raw CSVs> --out <output folder>
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")          # draw charts to files, without opening a window
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SNAPSHOT = pd.Timestamp("2026-01-31")
WAGE_OUTLIER_LIMIT = 8         # flag wages this many times the employer median
REGION_FIX = {"dsm": "Dar es Salaam", "dar es salaam": "Dar es Salaam", "dar-es-salaam": "Dar es Salaam"}
PERSONAL_BENEFITS = ["MATERNITY", "UNEMPLOYMENT", "OLD_AGE_PENSION", "OLD_AGE_GRANT", "INVALIDITY_PENSION"]


# ---------- load ----------
def load(raw_dir):
    """Read the four raw CSV files, with ID columns as text and dates parsed."""
    raw_dir = Path(raw_dir)
    employers = pd.read_csv(raw_dir / "employers.csv",
                            dtype={"employer_no": "string", "tin": "string"},
                            parse_dates=["registration_date", "closure_date"])
    members = pd.read_csv(raw_dir / "members.csv",
                          dtype={"member_no": "string", "employer_no": "string", "nida_no": "string", "phone": "string"},
                          parse_dates=["date_of_birth", "employment_start", "registration_date", "exit_date", "date_of_death"])
    contrib = pd.read_csv(raw_dir / "contributions_monthly.csv",
                          dtype={"employer_no": "string", "period": "string", "members_reported": "int32"},
                          parse_dates=["due_date", "payment_date"])
    claims = pd.read_csv(raw_dir / "claims.csv",
                         dtype={"claim_no": "string", "member_no": "string"},
                         parse_dates=["claim_date", "decision_date"])
    print("loaded:", len(employers), "employers,", len(members), "members,",
          len(contrib), "contribution rows,", len(claims), "claims")
    return employers, members, contrib, claims


# ---------- clean ----------
def clean_region(region_column):
    """Trim spaces, fix the Dar es Salaam spellings, and title-case every other region."""
    region = region_column.str.strip().str.lower()
    region = region.replace(REGION_FIX)
    is_dar = region == "Dar es Salaam"
    region[~is_dar] = region[~is_dar].str.title()
    return region


def normalize_phone(phone):
    """Make every phone number look like +255712345678."""
    # Phone numbers come as "+255 712 345 678", "0712345678", ... Make them all "+255712345678".
    # Step 1: keep only the digits. The pattern \D means "any character that is not a digit".
    phone = phone.str.replace(r"\D", "", regex=True)

    # Step 2: a number starting with 0 is a local number: swap the leading 0 for the country code 255.
    phone = phone.str.replace(r"^0", "255", regex=True)

    # Step 3: put a + in front.
    return "+" + phone


def clean_employers(employers_raw):
    employers = employers_raw.copy()
    employers["employer_name"] = employers["employer_name"].str.strip()
    employers["region"] = clean_region(employers["region"])
    employers = employers.sort_values("employer_name")
    employers = employers.drop_duplicates(subset=["employer_no"], keep="first")
    return employers.reset_index(drop=True)


def clean_members(members_raw):
    members = members_raw.copy()
    members["region"] = clean_region(members["region"])

    gender = members["gender"].str.strip().str.upper().str[0]
    gender[~gender.isin(["F", "M"])] = np.nan
    members["gender"] = gender

    members["phone"] = normalize_phone(members["phone"])

    members = members.drop_duplicates(subset=["member_no"], keep="first").reset_index(drop=True)

    age_at_registration = (members["registration_date"] - members["date_of_birth"]).dt.days / 365.25
    members["flag_implausible_dob"] = age_at_registration < 15
    members.loc[members["flag_implausible_dob"], "date_of_birth"] = pd.NaT

    employer_median = members.groupby("employer_no")["monthly_wage_tzs"].transform("median")
    members["flag_wage_outlier"] = members["monthly_wage_tzs"] > WAGE_OUTLIER_LIMIT * employer_median
    return members


def clean_contributions(contrib_raw):
    contrib = contrib_raw.copy()

    # keep every row of employer-months with a reversal; drop exact duplicates elsewhere
    contrib["month_key"] = contrib["employer_no"] + "|" + contrib["period"]
    reversal_keys = contrib.loc[contrib["amount_paid_tzs"] < 0, "month_key"].unique()
    has_reversal = contrib["month_key"].isin(reversal_keys)
    contrib = pd.concat([contrib[has_reversal], contrib[~has_reversal].drop_duplicates()])

    # payment dates after the snapshot are typing errors
    contrib["future_date_fixed"] = contrib["payment_date"] > SNAPSHOT
    contrib.loc[contrib["future_date_fixed"], "payment_date"] = pd.NaT

    # one row per employer-month
    contrib = contrib.groupby(["employer_no", "period"], as_index=False).agg(
        members_reported=("members_reported", "first"),
        gross_wages_tzs=("gross_wages_tzs", "first"),
        contribution_due_tzs=("contribution_due_tzs", "first"),
        due_date=("due_date", "first"),
        amount_paid_tzs=("amount_paid_tzs", "sum"),
        payment_date=("payment_date", "min"),
        n_amounts=("amount_paid_tzs", "count"),
        n_postings=("amount_paid_tzs", "size"),
        future_date_fixed=("future_date_fixed", "max"),
    )
    contrib.loc[contrib["n_amounts"] == 0, "amount_paid_tzs"] = np.nan
    contrib = contrib.drop(columns=["n_amounts"])

    missing_wages = contrib["gross_wages_tzs"].isna()
    contrib.loc[missing_wages, "gross_wages_tzs"] = contrib.loc[missing_wages, "contribution_due_tzs"] / 0.20
    return contrib


def clean_claims(claims_raw):
    claims = claims_raw.copy()
    claims["benefit_type"] = claims["benefit_type"].str.strip().str.upper().str.replace(" ", "_")
    return claims


# ---------- validate ----------
def validate(employers, members, contrib, claims):
    """Count failures for each rule. Stop with an error if a hard rule fails."""
    claims_with_member = claims.merge(members[["member_no", "date_of_death", "gender"]], on="member_no", how="left")
    is_personal = claims_with_member["benefit_type"].isin(PERSONAL_BENEFITS)
    after_death = claims_with_member["claim_date"] > claims_with_member["date_of_death"]
    is_maternity = claims_with_member["benefit_type"] == "MATERNITY"
    is_funeral = claims["benefit_type"] == "FUNERAL_GRANT"

    report = pd.DataFrame(
        [
            ["member_no unique", "hard", members["member_no"].duplicated().sum()],
            ["employer-month unique", "hard", contrib.duplicated(subset=["employer_no", "period"]).sum()],
            ["claim_no unique", "hard", claims["claim_no"].duplicated().sum()],
            ["no negative net contributions", "hard", (contrib["amount_paid_tzs"] < 0).sum()],
            ["no payment dates after snapshot", "hard", (contrib["payment_date"] > SNAPSHOT).sum()],
            ["claim references a known member", "soft", (~claims["member_no"].isin(members["member_no"])).sum()],
            ["personal claim not after recorded death", "soft", (is_personal & after_death).sum()],
            ["maternity claim by female member", "soft", (is_maternity & (claims_with_member["gender"] == "M")).sum()],
            ["funeral grant equals TZS 500,000", "soft", (is_funeral & (claims["amount_claimed_tzs"] != 500_000)).sum()],
            ["paid not above due by more than 15%", "soft", (contrib["amount_paid_tzs"] > 1.15 * contrib["contribution_due_tzs"]).sum()],
        ],
        columns=["rule", "severity", "failures"],
    )
    report["status"] = "pass"
    report.loc[(report["failures"] > 0) & (report["severity"] == "soft"), "status"] = "review"
    report.loc[(report["failures"] > 0) & (report["severity"] == "hard"), "status"] = "FAIL"

    hard_failures = report[report["status"] == "FAIL"]
    if len(hard_failures) > 0:
        raise ValueError("Hard validation rules failed:\n" + hard_failures.to_string(index=False))
    print("validation: hard rules passed;", (report["status"] == "review").sum(), "soft rules to review")
    return report


# ---------- transform ----------
def transform(members, contrib):
    members = members.copy()
    members["age"] = ((SNAPSHOT - members["date_of_birth"]).dt.days / 365.25).round(1)
    end_date = members["exit_date"].fillna(SNAPSHOT)
    members["tenure_years_current_employer"] = ((end_date - members["employment_start"]).dt.days / 365.25).round(1)
    members["registered_late"] = (members["registration_date"] - members["employment_start"]).dt.days > 30

    contrib = contrib.copy()
    contrib["period_start"] = pd.to_datetime(contrib["period"] + "-01")
    settled_date = contrib["payment_date"].fillna(SNAPSHOT)
    contrib["days_late"] = (settled_date - contrib["due_date"]).dt.days.clip(lower=0)
    contrib["months_late"] = np.ceil(contrib["days_late"] / 30).astype(int)
    contrib["unpaid_tzs"] = (contrib["contribution_due_tzs"] - contrib["amount_paid_tzs"].fillna(0)).clip(lower=0)

    contrib["penalty_rate"] = 0.05
    new_rule = contrib["due_date"] >= pd.Timestamp("2025-10-01")
    contrib.loc[new_rule, "penalty_rate"] = 0.025
    contrib["penalty_estimate_tzs"] = contrib["contribution_due_tzs"] * contrib["penalty_rate"] * contrib["months_late"]
    cap = 0.5 * contrib["contribution_due_tzs"]
    over_cap = new_rule & (contrib["penalty_estimate_tzs"] > cap)
    contrib.loc[over_cap, "penalty_estimate_tzs"] = cap[over_cap]
    contrib["penalty_estimate_tzs"] = contrib["penalty_estimate_tzs"].round(-2)

    members_reported = contrib["members_reported"].replace(0, np.nan)
    contrib["contribution_per_member_tzs"] = (contrib["contribution_due_tzs"] / members_reported).round(0)
    return members, contrib


# ---------- outputs ----------
def make_profile(tables):
    """One row per column of every table: type, share missing, number of distinct values."""
    profiles = []
    for table_name, table in tables.items():
        table_profile = pd.DataFrame({
            "dtype": table.dtypes.astype(str),
            "missing_share": table.isna().mean().round(4),
            "distinct": table.nunique(),
        })
        table_profile["table"] = table_name
        profiles.append(table_profile)
    return pd.concat(profiles).rename_axis("column").reset_index()


def save_outputs(tables, report, out_dir):
    out_dir = Path(out_dir)
    (out_dir / "processed").mkdir(parents=True, exist_ok=True)
    (out_dir / "figures").mkdir(parents=True, exist_ok=True)

    for table_name, table in tables.items():
        table.to_parquet(out_dir / "processed" / f"{table_name}.parquet", index=False)
    report.to_csv(out_dir / "validation_report.csv", index=False)
    make_profile(tables).to_csv(out_dir / "profile.csv", index=False)

    contrib = tables["contributions"]
    monthly = contrib.groupby("period_start")[["contribution_due_tzs", "amount_paid_tzs"]].sum() / 1e9
    plt.figure(figsize=(9, 3.8))
    plt.plot(monthly.index, monthly["contribution_due_tzs"], color="#b5b4ad", label="due")
    plt.plot(monthly.index, monthly["amount_paid_tzs"], color="#2a78d6", label="paid")
    plt.title("Contributions due and paid by wage month", loc="left")
    plt.ylabel("TZS billions")
    plt.legend(frameon=False)
    plt.savefig(out_dir / "figures" / "01_contributions_trend.png", dpi=130, bbox_inches="tight")
    plt.close()
    print("done: outputs in", out_dir.resolve())


# ---------- run every stage in order ----------
def main(raw_dir, out_dir):
    employers_raw, members_raw, contrib_raw, claims_raw = load(raw_dir)

    employers = clean_employers(employers_raw)
    members = clean_members(members_raw)
    contrib = clean_contributions(contrib_raw)
    claims = clean_claims(claims_raw)

    report = validate(employers, members, contrib, claims)

    members, contrib = transform(members, contrib)

    tables = {"employers": employers, "members": members, "contributions": contrib, "claims": claims}
    save_outputs(tables, report, out_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fund data pipeline")
    parser.add_argument("--raw", default="data/raw", help="folder containing the raw CSV files")
    parser.add_argument("--out", default="data/processed", help="folder for outputs")
    args = parser.parse_args()
    main(args.raw, args.out)
