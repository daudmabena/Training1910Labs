# Day 5 Labs: Fraud and Anomaly Detection

Every pension fund has the same uncomfortable problems: pensions that keep being paid after the pensioner has died,
several "members" whose benefits all land in one account, lump sums approved for more than the entitlement, the same
benefit paid twice. Most payments are perfectly fine. A tiny share aren't, and finding them by hand in tens of
thousands of payments is impossible.

Today you'll build the tools to help: detectors that spot unusual payments with no labels at all, models trained on
past confirmed cases, and a review workflow that turns scores into a queue a small investigations team can actually
work through.

One thing to keep in mind all day: **unusual is not the same as fraudulent.** A large arrears payment after a delayed
verification is unusual and perfectly legitimate. A guardian receiving pensions for three orphaned children into one
account is unusual and exactly what the rules intend. Your tools find candidates. People decide.

## Today's labs

| Lab | File | Time |
|---|---|---|
| 1. Anomaly detection without labels: isolation forest and an autoencoder | `Lab1_Anomaly_Detection.ipynb` | about 75 min |
| 2. Learning from confirmed cases when fraud is rare | `Lab2_Imbalanced_Learning.ipynb` | about 60 min |
| 3. A scoring and case-review workflow | `Lab3_Review_Workflow.ipynb` | about 75 min |

## Files in this folder

| File | What it is |
|---|---|
| `benefit_payments_2025.csv` | About 34,000 benefit payments made in 2025: monthly pensions, arrears, lump sums, grants and unemployment instalments |
| `requirements.txt` | Today's libraries |

The main columns:

| Column | Meaning |
|---|---|
| `payment_type` | `MONTHLY_PENSION`, `ARREARS`, `LUMP_SUM`, `GRANT` or `INSTALMENT` |
| `amount_tzs`, `entitlement_tzs` | What was paid, and what the member's benefit record says they're entitled to |
| `payee_account`, `account_type` | A masked account reference, and whether it's a bank or mobile money account |
| `account_changed_days_ago` | Days since the payee's account details were last changed |
| `members_sharing_account` | How many different members were paid into this account during 2025 |
| `payee_age` | Age of the person receiving the payment |
| `months_since_life_verification`, `last_verification_channel` | For pensions: when and how the pensioner last proved they're alive |
| `approving_officer`, `approval_hour` | Who approved the payment and at what hour of the day |
| `days_claim_to_payment` | For one-off benefits: days from the claim to payment |
| `confirmed_fraud` | 1 if a 2025 investigation confirmed fraud. **Only used to evaluate in Lab 1**; used for training in Lab 2. |

## Setup

Open `Lab1_Anomaly_Detection.ipynb` and run its first code cell. It finds the course environment you built on Day 1,
installs today's libraries into it, and tells you if the notebook needs switching to the
**Python (fund-ai)** kernel. If it asks you to switch, do that and run the cell once more. You can run it as
often as you like; it only installs what's missing.

The autoencoder in Lab 1 uses PyTorch. It runs on a CPU in a minute or two. If your machine has an NVIDIA GPU and a
CUDA build of PyTorch, the notebook uses the GPU automatically.
