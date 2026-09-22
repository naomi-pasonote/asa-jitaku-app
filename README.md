# 朝じたく（公開用）

- `web/` … ホーム画面用PWA。パターンの名前・時刻はiPhone内だけに保存（このリポジトリには入れない）。
- `shortcuts/asa_jitaku_renkei.cherri` … ショートカット「朝じたく連携」（1本方式）。Cherriで作成。
- `.github/workflows/pages.yml` … CherriでビルドしたショートカットをHubSignで署名し、署名済み `.shortcut` と配布用ZIPをGitHub Pagesへ公開する。

## 連携仕様
PWA → `shortcuts://x-callback-url/run-shortcut?name=朝じたく連携&input=text&text=<JSON>&x-success=…&x-cancel=…&x-error=…`

JSON: `{"mode":"ping|set|stop|clear","rid":"…","pattern":"名前","times":["HH:mm",…]}`

- ラベルは常に `朝じたく｜` で始まるものだけを操作（ショートカット内で固定。JSONの `prefix` は無視）。
- `set`: 古い「朝じたく｜」を削除→`times`の各時刻で作成（非繰り返し・スヌーズなし）。`stop`: OFF。`clear`: 削除。`ping`: 件数確認。
- 応答（`result`）: `ok|<mode>|<件数>`。PWAは success かつ `result` が `ok|<mode>|<件数>` の形で一致し、setのときは件数も一致した場合だけ「セット済み／停止済み」にする。それ以外は表示を変えない。
- 初回導入はPages上の配布ZIPをiPhoneへ保存し、「ファイル」アプリで展開した署名済み `.shortcut` を開く方式。
