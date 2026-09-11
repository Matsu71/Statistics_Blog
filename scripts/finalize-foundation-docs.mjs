import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root=fileURLToPath(new URL('../',import.meta.url));
const filename=path.join(root,'src/content/lessons/weighted-and-grouped-means.md');
let source=await readFile(filename,'utf8');
if(!source.includes('f13-grouped-variance')){
  const section=String.raw`<details id="f13-grouped-variance"><summary>階級値から分散を近似するときの注意（第15講を読んだ後に）</summary>

各階級内の観測を階級値に置き換えたデータとして、分母nの分散も計算できます。この例の近似平均は6なので、置換後の分散は

$$
\frac{4(2.5-6)^2+5(7.5-6)^2+(12.5-6)^2}{10}=10.25.
$$

これは元の観測の分散そのものではありません。元の10値の二乗の合計は413、平均は5.5なので、元の分母nの分散は413/10−5.5²=11.05です。階級値に置き換えると階級内の位置を失うため、平均だけでなく散らばりの計算にも近似が入ります。分散や標準偏差の定義は第15講で学びます。

</details>

`;
  source=source.replace('## まとめと次の一歩',section+'## まとめと次の一歩');await writeFile(filename,source);
}
// Name the proof in the visible disclosure title so natural keyword search can find it.
const normalPath=path.join(root,'src/content/lessons/normal-density-basics.md');
const normal=await readFile(normalPath,'utf8');
const named=normal.replace('正規化定数を求め、全体の面積1を証明する（積分・極座標）','正規化定数を求め、全体の面積1を証明する（ガウス積分・極座標）');
if(named!==normal)await writeFile(normalPath,named);
async function prepend(relative,marker,note){const file=path.join(root,relative),old=await readFile(file,'utf8');if(!old.includes(marker))await writeFile(file,`${marker}\n${note}\n\n---\n\n${old}`);}
await prepend('README.md','<!-- FOUNDATION_COMPLETE_20260911 -->',[
'# 統計ラボ：基礎コース完全版','',
'4級・3級を統合した基礎40講座、独自問題130問、操作型教材3本、本文・詳説検索、端末内の確認マーク・再開位置、公開範囲対応表を含みます。下に残る初期6講座の説明は初期版の記録です。','',
'[基礎コース](https://matsu71.github.io/Statistics_Blog/courses/foundation/) · [学習実験](https://matsu71.github.io/Statistics_Blog/labs/) · [範囲対応](https://matsu71.github.io/Statistics_Blog/coverage/foundation/) · [編集・訂正・プライバシー](https://matsu71.github.io/Statistics_Blog/about/)','',
'## 確認記録','',
'[内容レビュー](project-docs/learning-platform-design/13-foundation-content-review.md)、[競合比較と不足改善](project-docs/learning-platform-design/15-competitor-comparison-and-remediation.md)、[進捗と次の作業](project-docs/learning-platform-design/11-completion-progress.md)を保存しています。自動テストの実行結果は10・12・16・18・19番のJSONです。第三者監修・実利用者による効果検証は実施済みとは表示していません。','',
'## 再現する確認手順','',
'Node.js 22.12以上。`npm ci` の後、`node scripts/prepare-foundation-release.mjs && node scripts/finalize-foundation-docs.mjs && npm run generate:index && npm run verify && node scripts/validate-foundation.mjs && node scripts/test-foundation-math.mjs && node scripts/test-release-extras.mjs` を実行します。SciPyによる別実装の照合は `python scripts/check-foundation-oracle.py` です。','',
'ブラウザ検証はPlaywrightとChromium/WebKitを用意したうえで、`node scripts/test-foundation-browser.mjs && node scripts/test-learning-labs.mjs` を実行します。Actionsの検証ブランチでも同じ工程を実行します。','',
'検証ブランチでは、`src/data/foundation-release.json` のstageを `release_candidate` にした場合に限り、全テスト成功後に生成物と確認記録を保存します。mainへの反映は別の明示的な操作です。未検証のソースをmainへ強制上書きしません。'
].join('\n'));
await prepend('AGENTS.md','<!-- FOUNDATION_COMPLETE_POLICY_20260911 -->',[
'## 基礎完全版の現行方針','',
'基礎（4級・3級統合）40講座を正本として維持する。講座と問題・解答の品質を優先し、基本を表示、証明・詳説・解答を折りたたむ。公式範囲の対応は `src/data/foundation-coverage.json`、公開状態は `src/data/foundation-release.json`、残作業は11-completion-progress.mdで追う。','',
'新しい表示・計算・学習記録機能を変更した場合は、既存検証に加えて `test-release-extras.mjs` と `test-learning-labs.mjs` を実行する。数値・証明・図の自己点検と、自動テストと、独立監修を区別する。localStorageのメモは明示的な操作でだけ保存し、検索語とメモを外部へ送信しない。','',
'進捗は小さな区切りでGitHubへ保存する。最終報告では、実際の完了範囲、未実施の検証、次に行う作業を示す。全40原稿があるだけで公開完了と扱わず、全件検証・比較による改善・Pages公開確認を経る。2級以降の将来コースの実装済み扱いはしない。','',
'以下の旧方針は履歴。矛盾する初期6講座・2級用語中心の優先度は本節に置き換える。'
].join('\n'));
await prepend('project-docs/learning-platform-design/09-foundation-course.md','<!-- FOUNDATION_COMPLETE_SPEC_20260911 -->','> 現行版は全40講座・130問です。初期6講座に加えて残りを実装し、3実験・検索・確認マーク・再開位置・公開対応表・訂正方針を追加しました。以下の「今回の実装範囲」は初期版の履歴です。現在の確認は13の内容レビュー、15の比較記録、10/12/16/18/19の実行記録を参照してください。公開処理の完了は11の進捗とPages実行で確認します。');
console.log('Foundation documentation, proof findability and grouped-variance supplement updated.');
