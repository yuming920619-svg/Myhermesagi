# Myhermesagi Repo Rules

這個倉庫是 Hermes 的工作區規則與同步控制倉庫。

目標
- 保存此 repo 本身的規則檔、說明文件與之後明確放入 repo 的工作檔案。
- 讓 Hermes 在進入此 repo 工作時，遵循安全的同步與提交規則。

同步範圍
- 預設只同步這個 git repo 目錄中的檔案。
- 不要自動把整個 home 目錄、整個 ~/.hermes、或其他未明確指定的資料夾複製進來。
- 若未來要保存 Hermes 的上下文檔（例如 SOUL.md、USER.md、MEMORY.md），應先由使用者明確要求，再以匯出副本的方式放進 repo 的子目錄，例如 `hermes-context/`。

安全規則
- 這個 repo 目前是公開倉庫；預設以公開倉庫標準處理所有內容。
- 絕對不要提交任何憑證、token、密碼、session、私鑰或機密設定。
- 不要提交以下檔案：
  - `.env`, `.env.*`
  - `.git-credentials`
  - `*.pem`, `*.key`, `*.p12`, `*.pfx`
  - `~/.ssh/` 下任何檔案
  - 任何包含 GitHub PAT、API key、Cookie、OAuth token 的檔案

工作方式
- 在提交前先檢查 `git status --short`。
- 優先做小而清楚的變更。
- 若只是更新規則或說明文件，commit message 應簡潔描述變更內容。
- 若沒有變更，不要建立空 commit。

對自動同步工作的要求
- 自動同步工作只應在這個 repo 內執行。
- 若 repo 根目錄存在 `HERMES.md` 或 `AGENTS.md`，先讀取並遵循其規則。
- 在 stage/commit 之前再次檢查是否有敏感檔案被納入。

如果規則與使用者當前明確指示衝突
- 以使用者當前明確指示為準，但仍須避免洩漏敏感資訊。
