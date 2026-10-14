"""Generate synthetic card data: the bank's switch log, the card network's settlement file, and disputes.

The data is synthetic (no real customer data), but it reproduces the mismatches seen in real
card reconciliation: transactions missing on either side, amount differences, and duplicates.
"""
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "card_ops.db"
rng = np.random.default_rng(7)
N = 20_000

MERCHANT_CATEGORIES = ["Grocery", "Fuel", "Restaurant", "Online Retail", "ATM Withdrawal", "Utilities", "Travel"]
CHANNELS = ["POS", "ATM", "E-commerce", "Mobile"]


def build_switch_log():
    dates = pd.Timestamp("2025-07-01") + pd.to_timedelta(rng.integers(0, 92 * 24 * 60, N), unit="m")
    df = pd.DataFrame({
        "txn_id": [f"T{i:07d}" for i in range(N)],
        "card_id": [f"C{c:05d}" for c in rng.integers(0, 3000, N)],
        "txn_time": dates.strftime("%Y-%m-%d %H:%M:%S"),
        "merchant_category": rng.choice(MERCHANT_CATEGORIES, N, p=[.25, .12, .18, .2, .15, .06, .04]),
        "channel": rng.choice(CHANNELS, N, p=[.45, .15, .28, .12]),
        "amount": np.round(rng.lognormal(3.6, 0.9, N), 2),
        "status": rng.choice(["APPROVED", "DECLINED"], N, p=[.94, .06]),
    })
    return df


def build_settlement(switch):
    settled = switch[switch.status == "APPROVED"].copy()
    # About 0.8% of approved transactions never reach the network file
    settled = settled.drop(settled.sample(frac=0.008, random_state=1).index)
    # About 0.5% settle at a different amount (FX rounding, partial reversals, tips)
    diff = settled.sample(frac=0.005, random_state=2).index
    settled.loc[diff, "amount"] = np.round(settled.loc[diff, "amount"] * rng.uniform(0.8, 1.2, len(diff)), 2)
    # About 0.2% are duplicated by the network
    dupes = settled.sample(frac=0.002, random_state=3)
    # A few settlement records with no matching switch transaction
    orphans = settled.sample(25, random_state=4).assign(
        txn_id=[f"X{i:07d}" for i in range(25)])
    settled = pd.concat([settled, dupes, orphans], ignore_index=True)
    settled["settlement_date"] = (pd.to_datetime(settled.txn_time)
                                  + pd.to_timedelta(rng.integers(1, 4, len(settled)), unit="D")).dt.strftime("%Y-%m-%d")
    return settled[["txn_id", "card_id", "amount", "settlement_date"]].rename(columns={"amount": "settled_amount"})


def build_disputes(switch):
    approved = switch[switch.status == "APPROVED"]
    base = approved.sample(frac=0.012, random_state=5)
    reasons = rng.choice(["Unrecognised transaction", "Duplicate charge", "Goods not received",
                          "ATM cash not dispensed", "Incorrect amount"], len(base), p=[.35, .15, .2, .2, .1])
    opened = pd.to_datetime(base.txn_time) + pd.to_timedelta(rng.integers(1, 30, len(base)), unit="D")
    days_to_close = rng.gamma(2.2, 6, len(base)).round().astype(int) + 1
    closed = opened + pd.to_timedelta(days_to_close, unit="D")
    still_open = rng.random(len(base)) < 0.08
    return pd.DataFrame({
        "dispute_id": [f"D{i:05d}" for i in range(len(base))],
        "txn_id": base.txn_id.values,
        "reason": reasons,
        "opened_date": opened.dt.strftime("%Y-%m-%d"),
        "closed_date": np.where(still_open, None, closed.dt.strftime("%Y-%m-%d")),
        "outcome": np.where(still_open, "OPEN",
                            rng.choice(["Customer refunded", "Declined - valid charge"], len(base), p=[.62, .38])),
    })


def main():
    switch = build_switch_log()
    with sqlite3.connect(DB) as con:
        switch.to_sql("switch_transactions", con, if_exists="replace", index=False)
        build_settlement(switch).to_sql("network_settlement", con, if_exists="replace", index=False)
        build_disputes(switch).to_sql("disputes", con, if_exists="replace", index=False)
    print(f"Wrote {DB.name}")


if __name__ == "__main__":
    main()
