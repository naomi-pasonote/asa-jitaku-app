# 朝じたく（公開用）

- `web/` … ホーム画面用PWA。パターンの名前・時刻はiPhone内だけに保存（このリポジトリには入れない）。
- `shortcuts/asa_jitaku_renkei.cherri` … ショートカット「朝じたく連携」（1本方式）。Cherriで作成。
- `.github/workflows/pages.yml` … Cherriでビルドし、Cherri標準の `--hubsign`（RoutineHubの無料署名サービスを内部で使用）で署名。署名が失敗した場合はWorkflow自体を失敗させ、未署名のまま公開しない。

## 連携仕様
PWA → `shortcuts://x-callback-url/run-shortcut?name=朝じたく連携&input=text&text=<JSON>&x-success=…&x-cancel=…&x-error=…`

JSON: `{"mode":"ping|set|stop|clear","rid":"…","pattern":"名前","times":["HH:mm",…]}`

- ラベルは常に `朝じたく｜` で始まるものだけを操作（ショートカット内で固定。JSONの `prefix` は無視）。
- `set`: 古い「朝じたく｜」を削除→`times`の各時刻で作成（非繰り返し・スヌーズなし）。`stop`: OFF。`clear`: 削除。`ping`: 件数確認。
- 応答（`result`）: `ok|<mode>|<件数>`。PWAは success かつ `result` が `ok|<mode>|<件数>` の形で一致し、setのときは件数も一致した場合だけ「セット済み／停止済み」にする。それ以外（結果なし・不一致・cancel・error）は表示を変えない。
- `set` はPWAが計算した `times`("HH:mm")をそのまま `createAlarm` に渡す（Cherri側での分→日付変換はしない）。
- ショートカットのURL起動が失敗した場合に備え、「設定」に署名済み `.shortcut` を直接開く／URLコピーする予備ボタンを用意。