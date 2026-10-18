"""Build the processed datasets from the raw files.

    python scripts/build_dataset.py

1. verify the SHA-256 of each raw file against config/config.toml
2. parse the CDAW catalog (full remarks and quality flags kept)
3. read the SILSO sunspot number, if present (otherwise SSN columns are omitted, with a warning)
4. build the monthly table and derive the annual table from it
5. export dataset-level numbers to results/numbers.json and manuscript/generated/numbers.tex
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cmerate.config import load_config, repo_path  # noqa: E402
from cmerate.numbers import write_numbers  # noqa: E402
from cmerate.pipeline import build_all, dataset_numbers  # noqa: E402


def main() -> None:
    cfg = load_config()
    out = cfg["outputs"]
    built = build_all(cfg)
    ev = built["events"]
    print(f"CDAW: {len(ev)} events, {ev['datetime'].min()} -> {ev['datetime'].max()}")

    for key, df in built.items():
        path = repo_path(out[key])
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False, lineterminator="\n")
        print(f"wrote {out[key]} ({len(df)} rows)")

    write_numbers(dataset_numbers(ev, built["monthly"]), repo_path(out["numbers"]), repo_path(out["latex_macros"]))
    print(f"wrote {out['numbers']} and {out['latex_macros']}")


if __name__ == "__main__":
    main()
