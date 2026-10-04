# 朝じたく（公開用）

このリポジトリはClaude側が管理するファイルと、ChatGPT側が管理するWebデザイン(`web/`)が
同居する構成です。`.github/workflows/pages.yml` は両方をまとめてGitHub Pagesへ公開しますが、
Claude側のスクリプト(`setup-asa-jitaku.ps1`)は次のパスだけを管理し、それ以外（`web/` 等）は
書き換えません。

管理対象:
- `shortcuts/asa_jitaku_native.cherri` … `AsaJitakuNative4`。実機で日常使用中の完成版。以後変更しない。
- `shortcuts/asa_jitaku_cards.cherri` … `AsaJitakuCards1`。パターン選択をリスト表示にした派生版。
- `shortcuts/asa_jitaku_cards2.cherri` … `AsaJitakuCards2`。クリップボード経由でWebカード画面と連携する派生版。
- `shortcuts/asa_jitaku_cards2_debug.cherri` … `AsaJitakuCards2Debug`。クリップボードの生値と解析結果(codePart/offsetPart/partCount)を1回のアラートで表示するだけの診断専用版。アラーム操作は一切行わない。
- `shortcuts/asa_jitaku_cards3.cherri` … `AsaJitakuCards3`。Web/clipboard/share sheet/URLスキームを使わず、ショートカット単体で完結する最終形。パターン選択はCards1と同じ複数行リスト表示(chooseFromList)、offsetメニュー、「起きました」を内蔵。「日曜日」表記に統一。
- `shortcuts/asa_jitaku_native5.cherri` … `AsaJitakuNative5`。Native4の実績ロジックをベースに新仕様へ更新: 東二・出勤6:21開始/3分おき/15回、パシーナ・出勤5:51開始/3分おき/15回(他3パターン+休日は既存どおり)。「起きました」はOFFではなく削除(delete)に変更。時刻計算はdivmodの整数演算で時をまたぐケースにも対応。
- `tools/sign_hubsign.py` … 各ショートカットの署名前に `WFWorkflowName` を明示的に設定してから、
  RoutineHubの無料署名サービス(HubSign)で署名する。
- `.github/workflows/pages.yml` … 3つのショートカットをそれぞれコンパイル・署名し、`web/` があれば
  合わせてGitHub Pagesへ公開する。署名に失敗した場合はWorkflow自体を失敗させる。

管理対象外（Claude側では触れない）:
- `web/` … Webデザイン一式。ChatGPT側が別途このリポジトリへ配置する想定。

## パターンの扱い
各ショートカットの `.cherri` ソースには、個人のパターン名・時刻を含みません
（`/* PATTERNS_START */` 〜 `/* PATTERNS_END */` は汎用のプレースホルダーのみ）。
実際の値は、対応するリポジトリ シークレット
（`PATTERNS_CHERRI` / `PATTERNS_CARDS_CHERRI` / `PATTERNS_CARDS2_CHERRI`）
からビルド時に注入されます。シークレットの中身自体もこのリポジトリには残りません。

## AsaJitakuCards2: クリップボード連携の仕様
Web側のカードをタップすると、次の形式の文字列をクリップボードにコピーする想定です。

```
AJK:<パターンコード>[:<offset>]
```

- パターンコード: `higashi2`(東二・出勤) / `pasina`(パシーナ・出勤) / `sunday`(日曜日) /
  `holiday`(休日) / `morning`(モーニング) / `school`(平日登校日)
- 起きました専用: `AJK:wake`（offsetなし）
- offset（省略可）: `+5` / `+10` / `+15` / `+30` / `-5` / `-10` / `-15` / `-30` のみ有効。
  それ以外の文字列や省略時は ±0分として扱う（ホワイトリスト方式・不正な値でも安全に無視）。

例: `AJK:higashi2:+10`（東二・出勤を10分遅らせてセット）、`AJK:holiday`（休日、offset無視）。

ショートカット起動時にクリップボードがこの形式と一致すればメニューを出さず直接処理へ進み、
一致しなければ従来どおりメニュー（今夜のアラームをセット／起きました／テスト）を表示します。
