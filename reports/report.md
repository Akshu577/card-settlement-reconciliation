# Card Operations Report

Generated from synthetic data by `src/run_report.py`.

## Dispute Kpis

| reason | disputes | disputed_amount | avg_days_to_close | closed_over_30_days | refund_rate_pct | still_open |
|---|---|---|---|---|---|---|
| Unrecognised transaction | 77 | 5106.32 | 14.2 | 5 | 48.6 | 5 |
| Goods not received | 53 | 2432.25 | 12.6 | 0 | 58.3 | 5 |
| ATM cash not dispensed | 37 | 2300.48 | 12.4 | 0 | 51.6 | 6 |
| Duplicate charge | 34 | 1932.02 | 13.4 | 0 | 64.3 | 6 |
| Incorrect amount | 25 | 1772.21 | 15.3 | 2 | 69.6 | 2 |

## Monthly Dispute Trend

| month | disputes_opened | avg_days_to_close |
|---|---|---|
| 2025-07 | 44 | 15.5 |
| 2025-08 | 65 | 13.3 |
| 2025-09 | 74 | 13.4 |
| 2025-10 | 43 | 12.3 |

## Repeat Dispute Cards

| card_id | disputes | disputed_amount |
|---|---|---|
| C02365 | 3 | 292.96 |

## Recon Summary

| recon_status | transactions | switch_amount | net_variance |
|---|---|---|---|
| Matched | 18541 | 1027459.01 | 0.0 |
| Missing in settlement | 151 | 8440.54 | -8440.54 |
| Amount mismatch | 93 | 5225.2 | -10.43 |
| Duplicate settlement | 37 | 1872.45 | 1872.45 |

## Orphan Settlements

| orphan_records | orphan_amount |
|---|---|
| 25 | 1436.53 |

## Exceptions By Channel

| channel | approved_txns | exceptions | exception_rate_pct |
|---|---|---|---|
| ATM | 2765 | 55 | 1.99 |
| Mobile | 2290 | 42 | 1.83 |
| POS | 8587 | 121 | 1.41 |
| E-commerce | 5180 | 63 | 1.22 |
