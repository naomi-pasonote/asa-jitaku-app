# 朝じたく（公開用）

- `web/` … ホーム画面用PWA。パターン名・時刻はiPhone内だけに保存し、このPublicリポジトリには入れない。
- `shortcuts/asa_jitaku_renkei.cherri` … 共有シートからJSONを受け取り、「朝じたく｜」アラームだけを操作するショートカット。
- `tools/sign_hubsign.py` … Cherri出力に正式名・共有シート設定・テキスト入力設定を付与してからHubSignで署名する。
- `.github/workflows/pages.yml` … コンパイル、設定付与、署名、ZIP作成、GitHub Pages公開を行う。

## 連携方式

`shortcuts://run-shortcut` / x-callback-url による名前起動は使用しない。

PWAはiPhone標準のWeb Share API (`navigator.share`) でJSONテキストを共有し、
共有シートから `AsaJitakuShare` を選ぶ。ショートカットは `ActionExtension` として共有シートに表示され、
`WFStringContentItem` を受け取れる設定にする。

JSON: `{"mode":"ping|set|stop|clear","pattern":"名前","times":["HH:mm",…]}`

- `set`: 既存の「朝じたく｜」アラームだけを削除し、新しい時刻を作成。
- `stop`: 「朝じたく｜」アラームだけをOFF。
- `clear`: 「朝じたく｜」アラームだけを削除。
- `ping`: 連携確認。
- 他の通常アラームには触れない。
