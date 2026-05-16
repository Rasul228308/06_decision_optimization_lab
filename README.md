# Decision Optimization Lab

Minimal logistics decision-optimization dry run using the Kaggle SCMS shipment dataset.

It reads historical shipment records, builds country/product/vendor/mode candidates, compares baseline plans against a constrained plan, runs an air-capacity stress scenario, and writes a decision memo.

Rows with unknown shipment mode are excluded from optimization, and `Air` plus `Air Charter` both count against air-capacity limits.

This is a practice project, not a procurement, humanitarian-aid, military-logistics, or medical-supply decision system.

## Files

| File | Purpose |
| --- | --- |
| `optimize.py` | Runnable logistics planning dry run with self-tests. |
| `decision_memo.md` | Generated optimization report and scenario comparison. |
| `DATASET.md` | Kaggle dataset source and scope constraints. |
| `appendix.md` | Methodology, assumptions, ethics, tests, and limitations. |

## Run

```powershell
python optimize.py kaggle_raw/Raw_Data.csv --output decision_memo.md
```

Run self-tests:

```powershell
python optimize.py --self-test
```

Stress air capacity:

```powershell
python optimize.py kaggle_raw/Raw_Data.csv --air-cap 0.35 --stress-air-cap 0.15
```

## What It Shows

- candidate generation from historical logistics records
- cost, delay, and reliability objective terms
- constrained greedy assignment
- vendor concentration and air-capacity constraints
- infeasibility/violation notes
- baseline vs optimized vs stress scenario comparison
- basic raw-data text repair for analyst-readable output
- explicit ethical/scope limits

## Ethical Scope

Use this for learning and decision-support design. Do not use it to restrict medical access, discriminate against countries/vendors, bypass procurement rules, hide supply disruption, optimize military harm, or override humanitarian/clinical priorities. A real deployment needs procurement governance, local context, equity review, and human approval.
