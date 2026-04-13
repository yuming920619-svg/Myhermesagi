#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
BOOKKEEPING_DIR = REPO_ROOT / "bookkeeping"
LEDGER_PATH = BOOKKEEPING_DIR / "ledger.csv"
SUMMARY_PATH = BOOKKEEPING_DIR / "SUMMARY.md"
CURRENCY = "TWD"
CSV_FIELDS = ["date", "item", "amount", "currency", "category", "note", "created_at"]
TWOPLACES = Decimal("0.01")


@dataclass
class Entry:
    date: date
    item: str
    amount: Decimal
    currency: str
    category: str
    note: str
    created_at: str


def parse_amount(raw: str) -> Decimal:
    cleaned = raw.strip().replace(",", "")
    value = Decimal(cleaned)
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def normalize_amount(value: Decimal) -> str:
    s = format(value.quantize(TWOPLACES), "f")
    if s.endswith(".00"):
        return s[:-3]
    if s.endswith("0"):
        return s[:-1]
    return s


def format_money(value: Decimal) -> str:
    return f"{CURRENCY} {normalize_amount(value)}"


def ensure_files() -> None:
    BOOKKEEPING_DIR.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LEDGER_PATH.exists():
        with LEDGER_PATH.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()


def load_entries() -> list[Entry]:
    ensure_files()
    entries: list[Entry] = []
    with LEDGER_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("date"):
                continue
            try:
                entries.append(
                    Entry(
                        date=date.fromisoformat(row["date"]),
                        item=row.get("item", "").strip(),
                        amount=parse_amount(row.get("amount", "0")),
                        currency=row.get("currency", CURRENCY).strip() or CURRENCY,
                        category=row.get("category", "未分類").strip() or "未分類",
                        note=row.get("note", "").strip(),
                        created_at=row.get("created_at", "").strip(),
                    )
                )
            except Exception:
                continue
    return entries


def entry_sort_key(entry: Entry) -> tuple[date, str, str]:
    return (entry.date, entry.created_at, entry.item)


def save_entries(entries: Iterable[Entry]) -> None:
    ensure_files()
    sorted_entries = sorted(entries, key=entry_sort_key)
    with LEDGER_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for entry in sorted_entries:
            writer.writerow(
                {
                    "date": entry.date.isoformat(),
                    "item": entry.item,
                    "amount": normalize_amount(entry.amount),
                    "currency": entry.currency,
                    "category": entry.category,
                    "note": entry.note,
                    "created_at": entry.created_at,
                }
            )


def save_entry(entry: Entry) -> None:
    entries = load_entries()
    entries.append(entry)
    save_entries(entries)


def iso_week_key(d: date) -> tuple[int, int]:
    iso = d.isocalendar()
    return (iso.year, iso.week)


def week_bounds(year: int, week: int) -> tuple[date, date]:
    start = date.fromisocalendar(year, week, 1)
    end = date.fromisocalendar(year, week, 7)
    return start, end


def categorize_hint(item: str, note: str) -> str:
    text = f"{item} {note}".lower()
    mapping = [
        (["早餐", "午餐", "晚餐", "宵夜", "餐", "便當", "麵", "飯", "火鍋", "pizza", "lunch", "dinner", "breakfast"], "餐飲"),
        (["咖啡", "奶茶", "飲料", "茶", "可樂", "drink", "coffee", "boba"], "飲料"),
        (["捷運", "公車", "火車", "高鐵", "uber", "taxi", "計程車", "停車", "交通", "車票"], "交通"),
        (["超商", "日用品", "雜貨", "生活", "家樂福", "全聯", "711", "7-11", "全家"], "生活雜支"),
        (["書", "文具", "課", "學費", "paper", "conference", "研究"], "學習研究"),
        (["電影", "遊戲", "娛樂", "netflix", "steam"], "娛樂"),
        (["藥", "醫院", "診所", "health", "醫療"], "醫療"),
    ]
    for keywords, category in mapping:
        if any(keyword in text for keyword in keywords):
            return category
    return "未分類"


def sum_amount(entries: Iterable[Entry]) -> Decimal:
    total = Decimal("0")
    for entry in entries:
        total += entry.amount
    return total.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def category_totals(entries: Iterable[Entry]) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for entry in entries:
        totals[entry.category] += entry.amount
    return totals


def render_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    line1 = "| " + " | ".join(headers) + " |"
    line2 = "| " + " | ".join(["---"] * len(headers)) + " |"
    lines = [line1, line2]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return lines


def write_summary(entries: list[Entry], today: date | None = None) -> None:
    ensure_files()
    today = today or date.today()
    now = datetime.now().astimezone()

    sorted_entries = sorted(entries, key=lambda e: (e.date, e.created_at, e.item), reverse=True)
    all_total = sum_amount(sorted_entries)
    current_week = iso_week_key(today)
    current_month = (today.year, today.month)

    week_entries = [e for e in sorted_entries if iso_week_key(e.date) == current_week]
    month_entries = [e for e in sorted_entries if (e.date.year, e.date.month) == current_month]

    monthly_totals: dict[tuple[int, int], Decimal] = defaultdict(lambda: Decimal("0"))
    weekly_totals: dict[tuple[int, int], Decimal] = defaultdict(lambda: Decimal("0"))
    current_week_categories = category_totals(week_entries)
    current_month_categories = category_totals(month_entries)

    for entry in sorted_entries:
        monthly_totals[(entry.date.year, entry.date.month)] += entry.amount
        weekly_totals[iso_week_key(entry.date)] += entry.amount

    lines: list[str] = []
    lines.append("# 記帳總覽")
    lines.append("")
    lines.append(f"- 更新時間：{now.isoformat(timespec='seconds')}")
    lines.append(f"- 記錄筆數：{len(sorted_entries)}")
    lines.append(f"- 本週花費：{format_money(sum_amount(week_entries))}")
    lines.append(f"- 本月花費：{format_money(sum_amount(month_entries))}")
    lines.append(f"- 累積總花費：{format_money(all_total)}")
    lines.append("")

    lines.append("## 最近 20 筆")
    lines.append("")
    if sorted_entries:
        rows = []
        for entry in sorted_entries[:20]:
            rows.append([
                entry.date.isoformat(),
                entry.item,
                normalize_amount(entry.amount),
                entry.category,
                entry.note or "-",
            ])
        lines.extend(render_table(["日期", "項目", "金額(TWD)", "分類", "備註"], rows))
    else:
        lines.append("目前沒有任何記帳資料。")
    lines.append("")

    lines.append("## 最近 12 週統計")
    lines.append("")
    if weekly_totals:
        rows = []
        for (year, week), total in sorted(weekly_totals.items(), reverse=True)[:12]:
            start, end = week_bounds(year, week)
            rows.append([f"{year}-W{week:02d}", f"{start.isoformat()} ~ {end.isoformat()}", normalize_amount(total)])
        lines.extend(render_table(["週別", "日期範圍", "總花費(TWD)"], rows))
    else:
        lines.append("目前沒有任何週統計。")
    lines.append("")

    lines.append("## 最近 12 個月統計")
    lines.append("")
    if monthly_totals:
        rows = []
        for (year, month), total in sorted(monthly_totals.items(), reverse=True)[:12]:
            rows.append([f"{year}-{month:02d}", normalize_amount(total)])
        lines.extend(render_table(["月份", "總花費(TWD)"], rows))
    else:
        lines.append("目前沒有任何月統計。")
    lines.append("")

    lines.append("## 本週分類統計")
    lines.append("")
    if current_week_categories:
        rows = []
        for category, total in sorted(current_week_categories.items(), key=lambda kv: (-kv[1], kv[0])):
            rows.append([category, normalize_amount(total)])
        lines.extend(render_table(["分類", "總花費(TWD)"], rows))
    else:
        lines.append("本週尚無任何分類花費。")
    lines.append("")

    lines.append("## 本月分類統計")
    lines.append("")
    if current_month_categories:
        rows = []
        for category, total in sorted(current_month_categories.items(), key=lambda kv: (-kv[1], kv[0])):
            rows.append([category, normalize_amount(total)])
        lines.extend(render_table(["分類", "總花費(TWD)"], rows))
    else:
        lines.append("本月尚無任何分類花費。")
    lines.append("")

    SUMMARY_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def cmd_add(args: argparse.Namespace) -> int:
    ensure_files()
    try:
        expense_date = date.fromisoformat(args.date) if args.date else date.today()
    except ValueError:
        raise SystemExit("日期格式錯誤，請使用 YYYY-MM-DD")

    try:
        amount = parse_amount(args.amount)
    except (InvalidOperation, ValueError):
        raise SystemExit("金額格式錯誤，請輸入數字，例如 120 或 59.5")

    category = (args.category or "").strip() or categorize_hint(args.item, args.note or "")
    entry = Entry(
        date=expense_date,
        item=args.item.strip(),
        amount=amount,
        currency=CURRENCY,
        category=category,
        note=(args.note or "").strip(),
        created_at=datetime.now().astimezone().isoformat(timespec="seconds"),
    )
    save_entry(entry)
    entries = load_entries()
    write_summary(entries)

    today = date.today()
    week_total = sum_amount([e for e in entries if iso_week_key(e.date) == iso_week_key(today)])
    month_total = sum_amount([e for e in entries if (e.date.year, e.date.month) == (today.year, today.month)])

    print(f"已記帳：{entry.date.isoformat()} | {entry.item} | {format_money(entry.amount)} | {entry.category}")
    if entry.note:
        print(f"備註：{entry.note}")
    print(f"本週花費：{format_money(week_total)}")
    print(f"本月花費：{format_money(month_total)}")
    print(f"總覽檔案：{SUMMARY_PATH}")
    return 0


def cmd_refresh(args: argparse.Namespace) -> int:
    entries = load_entries()
    save_entries(entries)
    write_summary(entries)
    print(f"已刷新摘要：{SUMMARY_PATH}")
    print(f"目前筆數：{len(entries)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Expense bookkeeping helper")
    sub = parser.add_subparsers(dest="command", required=True)

    add_p = sub.add_parser("add", help="新增一筆記帳")
    add_p.add_argument("--date", help="日期，格式 YYYY-MM-DD；省略則用今天")
    add_p.add_argument("--item", required=True, help="項目名稱")
    add_p.add_argument("--amount", required=True, help="金額")
    add_p.add_argument("--category", help="分類；省略則自動推測，推測不到用未分類")
    add_p.add_argument("--note", default="", help="備註")
    add_p.set_defaults(func=cmd_add)

    refresh_p = sub.add_parser("refresh", help="重新產生摘要")
    refresh_p.set_defaults(func=cmd_refresh)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
