import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
const root = fileURLToPath(new URL('../', import.meta.url));
async function edit(relative, transform) {
  const filename = path.join(root, relative);
  const original = await readFile(filename, 'utf8');
  const changed = transform(original);
  if (original !== changed) { await writeFile(filename, changed); console.log(`Reviewed correction: ${relative}`); }
}
const lesson = (slug) => `src/content/lessons/${slug}.md`;
// Idempotent, reviewable migration: values are preserved, only the figure scale is corrected.
await edit(lesson('quartiles-and-boxplots'), (s) => s.replace('M55 65H110M270 65H490M55 45V85', 'M50 65H110M270 65H490M50 45V85').replace('<text x="55" y="122">1</text>', '<text x="50" y="122">1</text>'));
await edit(lesson('scatter-covariance-correlation'), (s) => s.replace('M55 20V220H415', 'M45 20V220H415'));
await edit(lesson('trees-and-counting'), (s) => s.replace('「場合の数」。[とけたろう', 'の確率分野に向けた数え上げの補習です。[とけたろう'));
await edit(lesson('normal-table-and-tail-area'), (s) => s.replace('\n[NIST・Normal Distribution]', '\n[1] [NIST・Normal Distribution]'));
await edit(lesson('reporting-statistical-results'), (s) => {
  const old = '|試料|S01|S02|S03|S04|S05|S06|S07|S08|S09|S10|\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n|変化（℃）|4|5|5|6|6|7|7|8|8|9|';
  const rows = [4,5,5,6,6,7,7,8,8,9].map((v,i)=>`|S${String(i+1).padStart(2,'0')}|${v}|`).join('\n');
  return s.replace(old, '|試料|温度変化（℃）|\n|---|---:|\n'+rows);
});
await edit(lesson('population-and-sampling'), (s) => {
  if (s.includes('id="f04-random-table"')) return s;
  const block = String.raw`<h2 id="f04-random-table">乱数表を使って、実際に3人を選ぶ</h2>

12人の名簿へ01〜12の番号を付け、重複なしで3人を選びます。読み始める場所、読む方向、二桁ずつ読むことを結果を見る前に決めます。00と13〜99は範囲外として飛ばし、既に選んだ番号も飛ばします。

説明用に作った二桁の列を、左から **04、17、04、00、11、08** と読みます。04を採用、17は範囲外、次の04は重複、00は範囲外、11と08を採用し、04・11・08の3人で止めます。都合のよい番号が出るまで読み始める位置を選び直すことはしません。

実際には十分な長さの乱数表や適切な生成器を使います。この短い列は読み方の例で、実測の抽出ログでも乱数品質を検証した表でもありません。等確率に生成された候補をこの規則で選別するなら、残っている各有効番号を等しく扱えます。

`;
  s = s.replace('## 確認問題', block+'## 確認問題').replace('practice_count: 3', 'practice_count: 4');
  const question = String.raw`<section class="practice-question" data-question="F04-Q4">

### 問4：範囲外と重複を飛ばす

01〜12から3人を選びます。左から「13、02、02、12、00、07」と読みました。採用する番号と、飛ばす理由を答えてください。

<details id="f04-q4-answer"><summary>解答と理由</summary>

02・12・07です。13と00は対象範囲外、二回目の02は重複として飛ばします。除外規則と停止条件は抽出前に決め、選びたい人に合わせて途中で変えません。

</details>
</section>

`;
  return s.replace('## 詳しく確かめる', question+'## 詳しく確かめる');
});
await edit(lesson('frequency-tables'), (s) => {
  if (s.includes('f07-cumulative-figure')) return s;
  const svg = `<figure id="f07-cumulative-figure"><svg viewBox="0 0 520 280" role="img" aria-labelledby="f07-fig-title f07-fig-desc"><title id="f07-fig-title">階級の境界と累積相対度数</title><desc id="f07-fig-desc">0分で0、5分で0.4、10分で0.9、15分で1。各境界で、その値未満の割合を表示。点を結ぶ線は見やすくする補助線で、階級内の分布を確定するものではない。</desc><path d="M60 30V230H470" fill="none" stroke="currentColor"/><path d="M60 230L190 150L320 50L450 30" fill="none" stroke="#144a56" stroke-width="3"/><g fill="#144a56"><circle cx="60" cy="230" r="5"/><circle cx="190" cy="150" r="5"/><circle cx="320" cy="50" r="5"/><circle cx="450" cy="30" r="5"/></g><g fill="currentColor" font-size="16" text-anchor="middle"><text x="60" y="251">0</text><text x="190" y="251">5</text><text x="320" y="251">10</text><text x="450" y="251">15</text><text x="190" y="138">0.4</text><text x="320" y="38">0.9</text><text x="450" y="18">1.0</text><text x="270" y="277">待ち時間の境界（分）</text></g><text x="5" y="22" font-size="14" fill="currentColor">累積割合</text></svg><figcaption>表の境界と割合を同じ尺度で描きました。線の途中から7分未満の正確な割合は復元できません。</figcaption></figure>\n\n`;
  return s.replace('## この表だけでは答えられない問い', svg+'## この表だけでは答えられない問い');
});
await edit(lesson('regression-line-and-prediction'), (s) => {
  if (s.includes('f20-regression-figure')) return s;
  const points = [[1,2],[2,3],[3,5],[4,4]], x=(v)=>60+80*v, y=(v)=>230-35*v;
  const dots=points.map(([a,b])=>`<line x1="${x(a)}" y1="${y(b)}" x2="${x(a)}" y2="${y(1.5+.8*a)}" stroke="#77512b" stroke-width="3" stroke-dasharray="4 3"/><circle cx="${x(a)}" cy="${y(b)}" r="5" fill="#144a56"/>`).join('');
  const svg=`<figure id="f20-regression-figure"><svg viewBox="0 0 480 290" role="img" aria-labelledby="f20-fig-title f20-fig-desc"><title id="f20-fig-title">回帰直線と縦方向の残差</title><desc id="f20-fig-desc">4点と予測直線y=1.5+0.8x。観測から直線へ垂直に引いた破線がy方向の残差。x=3では観測5、予測3.9で残差1.1。</desc><path d="M60 20V230H430" stroke="currentColor" fill="none"/><line x1="60" y1="177.5" x2="420" y2="51.5" stroke="#144a56" stroke-width="2"/>${dots}<g fill="currentColor" font-size="15" text-anchor="middle">${[0,1,2,3,4].map(v=>`<text x="${x(v)}" y="251">${v}</text>`).join('')}${[0,1,2,3,4,5].map(v=>`<text x="38" y="${y(v)+5}">${v}</text>`).join('')}<text x="260" y="278">学習時間（時間）</text></g><text x="3" y="16" fill="currentColor" font-size="14">得点</text></svg><figcaption>実線は予測、点は観測、破線は残差です。点から直線への最短距離を最小化した図ではありません。</figcaption></figure>\n\n`;
  return s.replace('## 当てはまりと予測性能は別', svg+'## 当てはまりと予測性能は別');
});
const labLinks = {
  'normal-density-basics':['normal','平均・標準偏差と塗られる領域を変える'],
  'normal-table-and-tail-area':['normal','片側・両側を切り替えて面積を確かめる'],
  'probability-and-repetition':['frequency','確率・試行回数・乱数の初期値を変える'],
  'mean-confidence-interval-basics':['confidence','信頼区間を繰り返し作り、母平均を含む割合を見る']
};
for (const [slug,[anchor,text]] of Object.entries(labLinks)) await edit(lesson(slug), s => {
  if (s.includes('id="try-lab"')) return s;
  return s.replace('## 確認問題', `<h2 id="try-lab">動かして確かめる</h2>\n\n[${text}](../../labs/#${anchor})。操作前に結果を予想し、操作後に変わった量と変わらなかった量を説明してください。図を動かした結果は、一般的な数学の証明とは区別します。\n\n## 確認問題`);
});
await edit('src/pages/learn/[slug].astro', s => {
  if (!s.includes('LearningTools.astro')) s=s.replace("import course from '../../data/foundation-course.json';", "import course from '../../data/foundation-course.json';\nimport LearningTools from '../../components/LearningTools.astro';");
  if (!s.includes('<LearningTools ')) s=s.replace('<article class="lesson-body"', '<LearningTools lessonId={lesson.data.lesson_id} />\n\n    <article class="lesson-body"');
  return s;
});
await edit('src/pages/courses/foundation/index.astro', s => {
  if (!s.includes('LearningTools.astro')) s=s.replace("import course from '../../../data/foundation-course.json';", "import course from '../../../data/foundation-course.json';\nimport LearningTools from '../../../components/LearningTools.astro';");
  if (!s.includes('<LearningTools')) s=s.replace('<section class="course-contents"', '<LearningTools />\n    <p class="learning-note"><a href={withBase(\'/labs/\')}>図を動かして学ぶ</a> · <a href={withBase(\'/coverage/foundation/\')}>出題範囲との対応を見る</a></p>\n    <section class="course-contents"');
  return s.replace('準備中の講座はまだ読めず、現時点で全範囲の教材が揃っているわけではありません。', '基礎40講座を公開しています。各テーマの説明・問題との対応は範囲対応表で確認できます。全種類の本試験問題を再現した教材や、合格を保証するものではありません。');
});
await edit('src/components/SiteFooter.astro', s => s.includes('/about/') ? s : s.replace('<a href={withBase(\'/topics/\')}>分野解説</a>', '<a href={withBase(\'/topics/\')}>分野解説</a>\n      <a href={withBase(\'/about/\')}>編集方針・訂正・プライバシー</a>'));
await edit('src/styles/learning.css', s => s.includes('foundation-release-layout') ? s : s+'\n/* foundation-release-layout: local scroll instead of compressed unreadable columns. */\n.lesson-body table{display:block;max-width:100%;overflow-x:auto}.lesson-body th,.lesson-body td{min-width:3.5em}.lesson-body .practice-question{min-width:0}.site-footer__links{flex-wrap:wrap}\n');
await mkdir(path.join(root,'project-docs/learning-platform-design'),{recursive:true});
console.log('All audited content corrections applied; publication is still gated by the release stage and tests.');
