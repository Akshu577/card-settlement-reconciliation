"""Run every named query in sql/*.sql and write the results to reports/report.md."""
import re
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def named_queries(sql_text):
    parts = re.split(r"^-- name: (\w+)\s*$", sql_text, flags=re.M)
    # parts = [preamble, name1, body1, name2, body2, ...]
    return [(parts[i], parts[i + 1].strip()) for i in range(1, len(parts), 2)]


def to_markdown(df):
    header = "| " + " | ".join(df.columns) + " |"
    sep = "|" + "---|" * len(df.columns)
    rows = ["| " + " | ".join("" if pd.isna(v) else str(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join([header, sep, *rows])


def main():
    out = ["# Card Operations Report", "",
           "Generated from synthetic data by `src/run_report.py`.", ""]
    with sqlite3.connect(ROOT / "card_ops.db") as con:
        for sql_file in sorted((ROOT / "sql").glob("*.sql")):
            for name, query in named_queries(sql_file.read_text()):
                df = pd.read_sql_query(query, con)
                out += [f"## {name.replace('_', ' ').title()}", "", to_markdown(df), ""]
    (ROOT / "reports" / "report.md").write_text("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
