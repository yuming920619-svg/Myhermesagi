#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from decimal import Decimal
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
BOOKKEEPING_DIR = REPO_ROOT / "bookkeeping"
LEDGER_PATH = BOOKKEEPING_DIR / "ledger.csv"
LEDGER_FIELDS = ["date", "item", "amount", "currency", "category", "note", "created_at"]
SOURCE_FIELDS = ["date", "time", "category", "item", "amount", "note"]
TIMEZONE_SUFFIX = "+08:00"
CURRENCY = "TWD"


def normalize_amount(raw: str) -> str:
    value = Decimal(raw.strip().replace(",", ""))
    text = format(value.normalize(), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def ensure_ledger() -> None:
    BOOKKEEPING_DIR.mkdir(parents=True, exist_ok=True)
    if not LEDGER_PATH.exists():
        with LEDGER_PATH.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
            writer.writeheader()


def load_existing_keys() -> set[tuple[str, str, str, str, str, str, str]]:
    ensure_ledger()
    keys: set[tuple[str, str, str, str, str, str, str]] = set()
    with LEDGER_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            keys.add(
                (
                    row.get("date", "").strip(),
                    row.get("item", "").strip(),
                    normalize_amount(row.get("amount", "0")),
                    row.get("currency", CURRENCY).strip() or CURRENCY,
                    row.get("category", "未分類").strip() or "未分類",
                    row.get("note", "").strip(),
                    row.get("created_at", "").strip(),
                )
            )
    return keys


def load_existing_rows() -> list[dict[str, str]]:
    ensure_ledger()
    rows: list[dict[str, str]] = []
    with LEDGER_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "date": row.get("date", "").strip(),
                    "item": row.get("item", "").strip(),
                    "amount": normalize_amount(row.get("amount", "0")),
                    "currency": row.get("currency", CURRENCY).strip() or CURRENCY,
                    "category": row.get("category", "未分類").strip() or "未分類",
                    "note": row.get("note", "").strip(),
                    "created_at": row.get("created_at", "").strip(),
                }
            )
    return rows


def source_to_row(row: dict[str, str]) -> dict[str, str]:
    d = row.get("date", "").strip()
    t = row.get("time", "").strip() or "00:00"
    category = row.get("category", "").strip() or "未分類"
    item = row.get("item", "").strip()
    amount = normalize_amount(row.get("amount", "0"))
    note = row.get("note", "").strip()
    created_at = f"{d}T{t}:00{TIMEZONE_SUFFIX}"
    return {
        "date": d,
        "item": item,
        "amount": amount,
        "currency": CURRENCY,
        "category": category,
        "note": note,
        "created_at": created_at,
    }


def row_key(row: dict[str, str]) -> tuple[str, str, str, str, str, str, str]:
    return (
        row["date"],
        row["item"],
        normalize_amount(row["amount"]),
        row["currency"],
        row["category"],
        row["note"],
        row["created_at"],
    )


def row_sort_key(row: dict[str, str]) -> tuple[str, str, str]:
    return (row["date"], row["created_at"], row["item"])


def write_rows(rows: Iterable[dict[str, str]]) -> None:
    ensure_ledger()
    with LEDGER_PATH.open("w", encoding="utf-8", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=LEDGER_FIELDS)
        writer.writeheader()
        for row in sorted(rows, key=row_sort_key):
            writer.writerow(row)


def import_files(paths: Iterable[Path]) -> tuple[int, int]:
    existing = load_existing_keys()
    all_rows = load_existing_rows()
    imported = 0
    skipped = 0

    for path in paths:
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            missing = [field for field in SOURCE_FIELDS if field not in (reader.fieldnames or [])]
            if missing:
                raise SystemExit(f"來源檔缺少欄位 {missing}: {path}")
            for raw in reader:
                row = source_to_row(raw)
                if not row["date"] or not row["item"]:
                    skipped += 1
                    continue
                key = row_key(row)
                if key in existing:
                    skipped += 1
                    continue
                all_rows.append(row)
                existing.add(key)
                imported += 1

    write_rows(all_rows)
    return imported, skipped


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import legacy bookkeeping CSV files into the repo ledger")
    parser.add_argument("paths", nargs="+", help="One or more legacy CSV file paths")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    paths = [Path(p).expanduser().resolve() for p in args.paths]
    for path in paths:
        if not path.is_file():
            raise SystemExit(f"找不到檔案：{path}")
    imported, skipped = import_files(paths)
    print(f"imported={imported}")
    print(f"skipped={skipped}")
    print(f"ledger={LEDGER_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
