# 統計ラボ

基礎から順番に学び、必要な定義・式・証明をその場で確認できる統計学習サイトです。学習順序は **基礎（統計検定4級・3級の内容を統合）→2級→準1級→1級**。独立した4級コースは設けません。

[公開サイト](https://matsu71.github.io/Statistics_Blog/) · [学習コース](https://matsu71.github.io/Statistics_Blog/courses/)

## 公開済みの範囲

2026-09-11時点。原稿の存在ではなく、main反映・検証済み生成物との実配信照合を確認した本数です。

|コース|公開講座|確認問題|状態|
|---|---:|---:|---|
|[基礎](https://matsu71.github.io/Statistics_Blog/courses/foundation/)|40|130|全40講座を公開確認済み|
|[2級](https://matsu71.github.io/Statistics_Blog/courses/grade2/)|40|172|全40講座を公開確認済み|
|[準1級](https://matsu71.github.io/Statistics_Blog/courses/pregrade1/)|6|24|P01〜P06公開。全72講座の構成中、残る66講座は未公開|
|1級|0|0|順序コースは未実装|
|合計|86|326|サイト全体の最終目標は継続中|

講座のほかに、既存71用語の辞典を維持しています。用語記事と順序講座の件数は混ぜません。準1級の公式範囲は2026年末までと2027年以降を区別し、適用時期を目次・構成データに示しています。

### 公開状態の正本

[全体の進捗](project-docs/project-status.json)は一覧、各公開記録は実際の確認結果です。

- [基礎リリース](project-docs/foundation-release/README.md)と[その時点の公開記録](project-docs/foundation-release/publication.json)
- [2級の公開記録](project-docs/grade2/release/publication.json)と[回収・検証記録](project-docs/grade2/release/recovery.json)
- [準1級初期版・現在の全サイト配信確認](project-docs/pregrade1/release/publication.json)：168 HTMLページを含む242ファイル、全86講座・326問を照合

後続コースの追加で共通ページの生成物は変わります。古いリリースのハッシュは、その時点の証拠です。現在のサイト全体の判定には最新の公開記録を使ってください。`src/data/*-release.json`の候補段階と、配信後の`publication.json`は違う時点を記録しています。

## 教材と使い方

基本説明、数値例、重要な使用条件はそのまま表示し、解答・導出・証明は必要に応じて開けます。前提となる講座、前後の講座、目次を行き来できます。JavaScriptが無効でも基本本文・数式・開閉できる解答を読めます。

講座検索、端末内の確認マークと再開位置、記録の書き出し・削除、確率・正規分布・信頼区間の操作型教材を実装しています。確認マークは利用者の自己記録で、習得や合格可能性の自動認定ではありません。基礎・2級・準1級の保存領域を分け、検索語や学習記録を外部へ送信しません。

## 原稿と構成

|対象|原稿|構成の正本|
|---|---|---|
|基礎|`src/content/lessons/`|`src/data/foundation-course.json`|
|2級|`src/content/grade2/`|`src/data/grade2-course.json`|
|準1級|`src/content/pregrade1/`|`src/data/pregrade1-course.json`|
|用語辞典|`src/content/terms/`|`data/term-queue.json`と`src/content.config.ts`|
|公開用生成物|`docs/`|検証後のビルドと、リリースごとのハッシュ記録|

次のP07・P08は[公開前の原稿フォルダ](project-docs/pregrade1/drafts/)に保存しています。2講座・8問、21件の数値検算を行いましたが、画面への組み込み・ブラウザ検証・公開は未実施です。公開6講座に加算しません。[次の工程と検算の再現方法](project-docs/pregrade1/checkpoints/03-main-published-and-next-drafts.md)を参照してください。

## 開発と検証

Node.js 22.12以上を使用します。通常の開発は`npm ci`の後、`npm run dev`です。

準1級の現在の公開候補を再検証する基本手順：

```sh
npm ci
node scripts/test-lesson-search-text.mjs
node scripts/check-pregrade1-content.mjs prepare
npm run generate:index
npm run verify
node scripts/validate-foundation.mjs
node scripts/validate-grade2.mjs
node scripts/check-pregrade1-content.mjs validate
```

数値検証は、Python・NumPy・SciPyを用いたコース別の検算と、既存のJavaScript検算を組み合わせます。ブラウザ検証にはPlaywrightのChromium/WebKitと日本語フォントが必要です。[検証ワークフロー](.github/workflows/verify-pregrade1.yml)に、使用する版と完全な実行順を保存しています。ブラウザ用依存は、サイトのロックされた依存関係と別の場所にインストールします。

現行の準1級検証・公開スクリプトは初期6講座に件数を固定しています。P07以降の追加時には、実装済みIDと構成上の予定IDを分けた件数管理へ改修し、既存の検査を削減せずに対象を増やしてください。未公開原稿の検算だけを再現する場合は`python scripts/check-pregrade1-next-drafts.py`です。

## 品質確認の範囲

初期準1級の最終確認は、55件の数値照合、370項目のブラウザ検証、11項目の検索テキスト単体検証に成功しています。既存の基礎・2級についても回帰検証しています。[検証結果](project-docs/pregrade1/release/final-gates.json)と[教材比較・修正の記録](project-docs/pregrade1/checkpoints/02-quality-review-and-search-fix.md)を参照してください。

自己点検・別実装による数値照合・ブラウザ検査と、独立した人間の数学監修や学習効果の比較実験は区別しています。後者は未実施です。公式認定教材、合格保証、競合より高い学習効果の実証済みサービスとは表示しません。既存教材は構造・説明の役割・数学の確認に用い、文章・図・問題の転載や数字だけを替えた複製はしません。

## 次に行うこと

**P07・P08を組み込み、全件再検証と公開確認を行った後、P09のガンマ・ベータ分布以降へ進みます。** 準1級の残る66講座と1級コースが、長期目標に対する未完了範囲です。

詳細な制作ルールは[AGENTS.md](AGENTS.md)。以前のREADME・制作ルールは[履歴フォルダ](project-docs/history/20260911-before-course-status/)に元の内容のまま保存しました。履歴内の相対パスは元のリポジトリルートを基準とする記録であり、古い件数・制作対象・公開状態を現行仕様と混同しないでください。
