# Hermes Context Snapshots

這個目錄保存 Hermes 目前主要對話上下文檔的「匯出副本」，供版本控管與備份。

目前包含：
- `SOUL.md`
- `USER.md`
- `MEMORY.md`

注意事項：
- 這些是從 `~/.hermes/` 匯出的快照，不是符號連結，也不是即時雙向同步。
- 自動同步工作會先刷新這些快照，再視是否有變更進行 commit 與 push。
- 因此 GitHub 上看到的是某次同步時點的內容。
- 若內容含個人資訊或偏好，推送到公開 repo 後將會公開可見。
