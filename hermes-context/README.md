# Hermes Context Snapshots

這個目錄保存 Hermes 目前主要對話上下文檔的「公開遮罩版匯出副本」，供版本控管與備份。

目前包含：
- `SOUL.md`
- `USER.md`
- `MEMORY.md`

注意事項：
- 這些是從 `~/.hermes/` 匯出的快照，不是符號連結，也不是即時雙向同步。
- 匯出時會先做公開版遮罩，例如遮罩 email、Telegram user ID、GitHub token 等敏感內容。
- 自動同步工作會先重新匯出這些公開遮罩版快照，再視是否有變更進行 commit 與 push。
- 因此 GitHub 上看到的是某次同步時點的公開版快照，而不是本機原始檔的完整原文。
