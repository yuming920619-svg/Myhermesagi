# 記帳系統

這個資料夾保存 Hermes 的記帳資料與自動統計。

檔案說明：
- `ledger.csv`：原始記帳資料
- `SUMMARY.md`：自動產生的總覽，包含本週、本月、最近 12 週、最近 12 個月，以及本週/本月分類統計
- `scripts/expense_bookkeeping.py`：新增記帳與刷新摘要的腳本
- `scripts/import_legacy_csv.py`：把舊版月記帳 CSV 合併匯入目前 ledger 的工具（會去重）

預設規則：
- 幣別：TWD
- 若未提供日期，記帳時使用當天日期
- 若未提供分類，會依項目內容自動推測；推測不到則記為 `未分類`

範例：
```bash
python3 bookkeeping/scripts/expense_bookkeeping.py add --item "午餐" --amount 120
python3 bookkeeping/scripts/expense_bookkeeping.py add --date 2026-04-11 --item "捷運" --amount 35 --category "交通"
python3 bookkeeping/scripts/expense_bookkeeping.py refresh
python3 bookkeeping/scripts/import_legacy_csv.py "/mnt/d/USER/下載/2026-03.csv" "/mnt/d/USER/下載/2026-04.csv"
```
