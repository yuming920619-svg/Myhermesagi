# AGENTS.md Compatibility Note

如果你是 Hermes 或其他會讀取 AGENTS.md 的代理，請優先遵循同目錄下的 `HERMES.md`。

關鍵規則摘要：
- 這個 repo 目前視為公開倉庫。
- 只同步此 repo 目錄本身，不要自動納入整個 home 或整個 `~/.hermes`。
- 不要提交任何敏感資訊、憑證、token、私鑰、`.env`、`.git-credentials`、SSH 金鑰。
- 若要保存 Hermes 的上下文檔，應由使用者明確要求，並以「公開遮罩版匯出副本」方式放到 repo 子目錄中。
- 提交前先檢查 `git status --short`。

若 `HERMES.md` 與本檔內容有差異，以 `HERMES.md` 為準。
