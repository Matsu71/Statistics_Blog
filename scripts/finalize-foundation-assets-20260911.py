#!/usr/bin/env python3
"""Prepare the foundation release without changing published branches.

This script applies explicit, reviewable corrections and writes original UI assets.
Numerical, content, browser, security and publication gates run separately in CI.
It never treats generated prose or a successful build as independent peer review.
"""
from __future__ import annotations
import hashlib
import html
import json
import math
import re
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'project-docs/learning-platform-design'
NOW = datetime.now(timezone.utc).isoformat()

def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding='utf-8')

def write(relative: str, value: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + '\n', encoding='utf-8')

def write_json(relative: str, value: object) -> None:
    write(relative, json.dumps(value, ensure_ascii=False, indent=2))

def insert_before_questions(relative: str, marker: str, supplement: str) -> None:
    text = read(relative)
    if marker in text:
        return
    target = '## 確認問題'
    if target not in text:
        raise RuntimeError(f'Missing question section in {relative}')
    write(relative, text.replace(target, supplement.strip() + '\n\n' + target, 1))

course = json.loads(read('src/data/foundation-course.json'))
planned = [lesson for module in course['modules'] for lesson in module['lessons']]
if len(planned) != 40 or len({x['id'] for x in planned}) != 40:
    raise RuntimeError('The release requires the agreed forty unique foundation lessons.')
for lesson in planned:
    text = read(f"src/content/lessons/{lesson['slug']}.md")
    if not re.search(r'^status:\s*published\s*$', text, re.M):
        raise RuntimeError(f"Unfinished lesson: {lesson['id']}")

corrections: list[dict[str, str]] = []
variance_path = 'src/content/lessons/variance-and-standard-deviation.md'
variance = read(variance_path)
wrong = '標準偏差の平方根を取った量まで自動的に不偏になるわけではありません'
right = '不偏分散の平方根を取った標準偏差も、一般には母標準偏差の不偏推定量ではありません'
if wrong in variance:
    write(variance_path, variance.replace(wrong, right))
    corrections.append({'lesson':'F15','change':'不偏分散の平方根に関する誤った名詞を訂正。分散と標準偏差の不偏性を区別。'})

box_path = 'src/content/lessons/quartiles-and-boxplots.md'
box = read(box_path)
if 'f14-release-box-title' not in box:
    svg = '''<svg viewBox="0 0 560 165" role="img" aria-labelledby="f14-release-box-title f14-release-box-desc">
<title id="f14-release-box-title">1、2、3、4、5、6、7、12の箱ひげ図</title>
<desc id="f14-release-box-desc">横軸は0から12まで等間隔。最小値1、第一四分位数2.5、中央値4.5、第三四分位数6.5、最大値12。本文の四分位数の定義による図。</desc>
<path d="M40 125H520" stroke="currentColor" fill="none"/>
<path d="M80 66H520 M80 48V84 M520 48V84" stroke="currentColor" fill="none" stroke-width="2"/>
<rect x="140" y="44" width="160" height="44" fill="#e8f2f4" stroke="#144a56" stroke-width="2"/>
<path d="M220 44V88" stroke="#144a56" stroke-width="3"/>
<g text-anchor="middle" font-size="13" fill="currentColor">
<text x="80" y="33">1</text><text x="140" y="33">2.5</text><text x="220" y="33">4.5</text><text x="300" y="33">6.5</text><text x="520" y="33">12</text>
<text x="40" y="149">0</text><text x="120" y="149">2</text><text x="200" y="149">4</text><text x="280" y="149">6</text><text x="360" y="149">8</text><text x="440" y="149">10</text><text x="520" y="149">12</text>
</g><path d="M40 121V129 M120 121V129 M200 121V129 M280 121V129 M360 121V129 M440 121V129 M520 121V129" stroke="currentColor"/>
</svg>'''
    if re.search(r'<svg\b', box):
        box = re.sub(r'<svg\b[\s\S]*?</svg>', lambda _: svg, box, count=1)
    else:
        box = box.replace('## 確認問題', '<figure>' + svg + '<figcaption>同じ数値差を同じ横幅で描いています。</figcaption></figure>\n\n## 確認問題', 1)
    write(box_path, box)
    corrections.append({'lesson':'F14','change':'五数要約の位置を x=40+40×値 に統一し、等間隔の軸目盛りを追加。'})

insert_before_questions('src/content/lessons/population-and-sampling.md', 'f04-random-digit-example', '''
## 乱数表の読み方を、実際の番号で確かめる

<span id="f04-random-digit-example"></span>
12人の完全な名簿に01〜12の番号を付け、重複しない4人を選びます。2桁ずつ左から読み、01〜12以外の番号と、一度採用した番号を飛ばす、と先に決めます。

|読む順番|07|03|16|03|12|00|09|
|---|---|---|---|---|---|---|---|
|判断|採用|採用|範囲外|重複|採用|範囲外|採用|

選ばれる番号は07・03・12・09です。この短い列は手順を説明するための作例であり、この列だけで乱数の品質を判定したものではありません。元の2桁の数が00〜99に同じ確率で独立に生成されるという条件なら、この棄却・重複除外の手順で残る各人を対称に扱えます。

途中で読み始める位置を選び直したり、特定の人が入るまで番号を引き直したりしません。名簿そのものから対象者が抜けている問題は、乱数表では解決しないことにも注意します。
''')
corrections.append({'lesson':'F04','change':'範囲外・重複の番号を捨てる乱数表の具体例と、その成立条件を追加。'})

insert_before_questions('src/content/lessons/choosing-basic-graphs.md', 'f09-release-graphs', '''
## 同じ10件を、棒・円・パレート図で見る

<span id="f09-release-graphs"></span>
別の架空例として、徒歩5人、自転車3人、その他2人という通い方を考えます。棒グラフなら件数の差、円グラフなら全体に占める割合が読みやすくなります。どちらでも元の人数は同じです。

<figure><svg viewBox="0 0 620 205" role="img" aria-labelledby="f09-bars-title f09-bars-desc"><title id="f09-bars-title">通い方の件数を比べる棒グラフ</title><desc id="f09-bars-desc">徒歩5人、自転車3人、その他2人。各棒は0人から始まり、1人あたり70の同じ幅で描く。</desc><g fill="currentColor" font-size="16"><text x="8" y="42">徒歩</text><text x="8" y="100">自転車</text><text x="8" y="158">その他</text><text x="454" y="42">5人</text><text x="314" y="100">3人</text><text x="244" y="158">2人</text><text x="95" y="194">0</text></g><g fill="#144a56"><rect x="100" y="20" width="350" height="32"/><rect x="100" y="78" width="210" height="32"/><rect x="100" y="136" width="140" height="32"/></g><path d="M100 10V176H520" fill="none" stroke="currentColor"/></svg><figcaption>棒の長さは件数に比例します。0からの長さを比較する図なので、基準を途中から省きません。</figcaption></figure>

<figure><svg viewBox="0 0 620 230" role="img" aria-labelledby="f09-pie-title f09-pie-desc"><title id="f09-pie-title">同じ10人の構成比を示す円グラフ</title><desc id="f09-pie-desc">徒歩50パーセントが180度、自転車30パーセントが108度、その他20パーセントが72度。凡例にも数値を記載。</desc><path d="M125 115L125 25A90 90 0 0 1 125 205Z" fill="#144a56" stroke="white"/><path d="M125 115L125 205A90 90 0 0 1 39.405 87.188Z" fill="#6f96a0" stroke="white"/><path d="M125 115L39.405 87.188A90 90 0 0 1 125 25Z" fill="#d5e4e8" stroke="white"/><g fill="currentColor" font-size="16"><text x="255" y="65">徒歩：5 / 10 = 50%</text><text x="255" y="112">自転車：3 / 10 = 30%</text><text x="255" y="159">その他：2 / 10 = 20%</text></g></svg><figcaption>円の全体を10人としています。別の全体人数の円と、扇形の面積だけで人数を比較しません。</figcaption></figure>

同じデータを件数の多い順に並べ、累積割合を重ねるのがパレート図の基本です。この例では、徒歩まで50%、徒歩と自転車まで80%、全カテゴリで100%になります。累積する順序と、件数の軸・割合の軸を区別して読みます。

|多い順のカテゴリ|徒歩|自転車|その他|
|---|---:|---:|---:|
|件数|5|3|2|
|累積割合|50%|80%|100%|
''')
corrections.append({'lesson':'F09','change':'同じ人数の棒グラフ・円グラフとパレート図の累積割合表を追加。'})

# Horizontal scrolling is local to wide data tables, not to the entire page.
write('scripts/rehype-learning-tables.mjs', '''export default function learningTables() {
  return function transform(tree) {
    function visit(node) {
      if (!Array.isArray(node.children)) return;
      node.children = node.children.map((child) => {
        visit(child);
        if (child.type !== 'element' || child.tagName !== 'table') return child;
        let columns = 0;
        function countRows(element) {
          if (element.type === 'element' && element.tagName === 'tr') columns = Math.max(columns, (element.children ?? []).filter((cell) => cell.type === 'element' && ['th', 'td'].includes(cell.tagName)).length);
          for (const next of element.children ?? []) countRows(next);
        }
        countRows(child);
        return { type: 'element', tagName: 'div', properties: { className: ['learning-table-scroll', ...(columns > 4 ? ['learning-table-wide'] : [])], role: 'region', ariaLabel: 'データ表。横に収まらない場合はスクロールできます。', tabIndex: 0 }, children: [child] };
      });
    }
    visit(tree);
  };
}
''')
config = read('astro.config.mjs')
if 'rehype-learning-tables' not in config:
    config = "import learningTables from './scripts/rehype-learning-tables.mjs';\n" + config
    config, count = re.subn(r'rehypePlugins:\s*\[', 'rehypePlugins: [learningTables, ', config, count=1)
    if count != 1:
        raise RuntimeError('Cannot safely register the table renderer.')
    write('astro.config.mjs', config)

write('src/styles/learning-release.css', '''
.learning-table-scroll{max-width:100%;overflow-x:auto;margin:1rem 0;overscroll-behavior-x:contain}.learning-table-scroll table{margin:0!important}.learning-table-wide table{min-width:540px}.lesson-body,.lesson-shell{min-width:0}.lesson-body figure svg{max-width:100%;height:auto}.release-box{border:1px solid var(--line);background:var(--surface);padding:1.1rem;border-radius:12px;margin:1.25rem 0}.release-box h2{font-size:1.2rem;line-height:1.6;margin-bottom:.65rem}.release-box p{margin:.6rem 0}.release-box a,.release-prose a{color:var(--brand-strong);text-decoration:underline;text-underline-offset:.18em}.release-prose{line-height:1.95;overflow-wrap:anywhere}.release-prose h2{font-size:1.35rem;line-height:1.65;margin:2rem 0 .8rem}.release-prose h3{font-size:1.1rem;line-height:1.65;margin:1.3rem 0 .6rem}.release-prose p{margin:1rem 0}.release-prose li{margin:.5rem 0}.release-prose table{border-collapse:collapse;width:100%;font-size:.92rem}.release-prose td,.release-prose th{border:1px solid var(--line);padding:.6rem;vertical-align:top}.lab-controls{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}.lab-controls label{display:flex;flex-direction:column;gap:.3rem;font-size:.9rem}.lab-controls input,.lab-controls select,.course-search-input{width:100%;min-width:0;min-height:44px;border:1px solid var(--line-strong);border-radius:6px;padding:.6rem;background:white;color:var(--text)}.lab-controls button{align-self:end;min-height:44px;border:0;background:var(--brand-strong);color:white;border-radius:6px;padding:.7rem;cursor:pointer}.lab-result{font-weight:700;margin:1rem 0;font-size:1.05rem;line-height:1.8;overflow-wrap:anywhere}.lab-error{color:#872b22;font-weight:700}.lab-graph{display:block;width:100%;height:auto;max-height:620px}.lab-caption{font-size:.87rem;line-height:1.8;margin:.8rem 0}.lab-value-table{max-width:100%;overflow-x:auto}.lab-value-table table{width:100%;border-collapse:collapse;font-size:.86rem}.lab-value-table td,.lab-value-table th{border:1px solid var(--line);padding:.45rem;text-align:left}.lab-links{display:flex;flex-wrap:wrap;gap:.7rem}.lab-links a{display:inline-flex;align-items:center;min-height:44px;padding:.55rem .8rem;border:1px solid var(--line-strong);border-radius:7px;background:var(--surface)}.course-search-results{list-style:none;padding:0}.course-search-results li{padding:1rem 0;border-bottom:1px solid var(--line)}.course-search-results strong{display:block;font-size:1.05rem}.course-search-results p{font-size:.9rem;color:var(--muted);line-height:1.8;margin:.5rem 0}.course-search-form{display:flex;gap:.5rem;align-items:end}.course-search-form label{flex:1;min-width:0}.course-search-form button{min-height:44px;border:0;background:var(--brand-strong);color:white;padding:.6rem 1rem;border-radius:6px}.release-footer-links{display:flex;flex-wrap:wrap;gap:.75rem;font-size:.85rem;padding:1rem 0;line-height:1.8}.release-footer-links a{min-height:28px;display:inline-flex;align-items:center}.release-note{font-size:.88rem;color:var(--muted)}@media(max-width:600px){.lab-controls{grid-template-columns:1fr}.release-box{padding:.85rem}.course-search-form{flex-wrap:wrap}.course-search-form label{flex-basis:100%}}@media print{.learning-table-scroll{overflow:visible}.learning-table-wide table{min-width:0}.lab-controls{display:none}.lab-graph{max-height:450px}.release-footer-links{display:none}}
''')
layout = read('src/layouts/BaseLayout.astro')
if "learning-release.css" not in layout:
    layout = layout.replace("import '../styles/global.css';", "import '../styles/global.css';\nimport '../styles/learning-release.css';")
    if "learning-release.css" not in layout:
        raise RuntimeError('Cannot register release styles.')
    write('src/layouts/BaseLayout.astro', layout)

write('src/lib/foundation-labs.mjs', '''import { normalSF, normalInterval, normalDensity } from './learning-math.mjs';
export { normalSF, normalInterval, normalDensity };
function finite(value, name) { if (!Number.isFinite(value)) throw new RangeError(`${name}は有限の数値にしてください。`); return value; }
function integer(value, min, max, name) { finite(value,name); if (!Number.isInteger(value) || value < min || value > max) throw new RangeError(`${name}は${min}〜${max}の整数にしてください。`); return value; }
export function randomGenerator(seed) { let state = integer(seed,1,2147483646,'seed'); return () => { state = state * 16807 % 2147483647; return state / 2147483647; }; }
export function normalTailModel({mean,sd,z,mode}) { finite(mean,'平均'); finite(sd,'標準偏差'); finite(z,'z値'); if(sd<=0)throw new RangeError('標準偏差は0より大きくしてください。'); if(Math.abs(z)>4)throw new RangeError('この実験のz値は−4〜4です。'); if(!['upper','lower','central'].includes(mode))throw new RangeError('領域を選んでください。'); const probability=mode==='upper'?normalSF(z):mode==='lower'?normalSF(-z):normalInterval(-Math.abs(z),Math.abs(z)); return {mean,sd,z,mode,boundary:mean+sd*z,probability}; }
export function bernoulliExperiment({p,n,seed}) { finite(p,'成功確率');if(p<0||p>1)throw new RangeError('成功確率は0〜1にしてください。');integer(n,1,5000,'試行回数'); const random=randomGenerator(seed); let successes=0;const history=[];for(let i=1;i<=n;i++){if(random()<p)successes++;history.push({trial:i,successes,frequency:successes/i});}return {p,n,seed,successes,frequency:successes/n,history}; }
export function coverageExperiment({mean,sd,n,repetitions,level,seed}) { finite(mean,'母平均');finite(sd,'母標準偏差');if(sd<=0)throw new RangeError('母標準偏差は0より大きくしてください。');integer(n,1,10000,'標本サイズ');integer(repetitions,1,1000,'繰返し回数');const critical={90:1.6448536269514722,95:1.959963984540054,99:2.5758293035489004}[level];if(!critical)throw new RangeError('信頼係数を選んでください。');const random=randomGenerator(seed);const se=sd/Math.sqrt(n),halfWidth=critical*se;let covered=0;const intervals=[];for(let i=0;i<repetitions;i++){const normal=Math.sqrt(-2*Math.log(random()))*Math.cos(2*Math.PI*random());const estimate=mean+se*normal,lower=estimate-halfWidth,upper=estimate+halfWidth;const contains=lower<=mean&&mean<=upper;if(contains)covered++;intervals.push({index:i+1,estimate,lower,upper,contains});}return {mean,sd,n,repetitions,level,seed,se,halfWidth,covered,intervals}; }
''')

lab_specs = [
 ('normal-area','正規分布の面積を動かす','平均・標準偏差・境界のz値を変え、片側と中央の確率を確かめます。','normal','normal-table-and-tail-area'),
 ('probability-frequency','確率と観測頻度を比べる','同じ成功確率でも、有限回の結果は揺れます。seedを固定して回数の違いを比較します。','frequency','probability-and-repetition'),
 ('confidence-coverage','信頼区間を繰り返し作る','既知の母分散を使う正規モデルで、区間を繰り返したときの被覆を観察します。','coverage','mean-confidence-interval-basics')
]
forms = {
'normal': '''<label for="normal-mean">平均 μ<input id="normal-mean" name="mean" type="number" value="0" min="-1000000" max="1000000" step="any" required /></label><label for="normal-sd">標準偏差 σ<input id="normal-sd" name="sd" type="number" value="1" min="0.000001" max="1000000" step="any" required /></label><label for="normal-z">境界の z値（−4〜4）<input id="normal-z" name="z" type="number" value="1.96" min="-4" max="4" step="any" required /></label><label for="normal-mode">確率を求める領域<select id="normal-mode" name="mode"><option value="upper">右側：Z ≥ z</option><option value="lower">左側：Z ≤ z</option><option value="central">中央：−|z| ≤ Z ≤ |z|</option></select></label><button type="submit">図と確率を更新する</button>''',
'frequency': '''<label for="frequency-p">成功確率 p（0〜1）<input id="frequency-p" name="p" type="number" value="0.5" min="0" max="1" step="any" required /></label><label for="frequency-n">試行回数（1〜5,000）<input id="frequency-n" name="n" type="number" value="100" min="1" max="5000" step="1" required /></label><label for="frequency-seed">seed（同じ値で再現）<input id="frequency-seed" name="seed" type="number" value="12345" min="1" max="2147483646" step="1" required /></label><button type="submit">同じ条件で実行する</button>''',
'coverage': '''<label for="coverage-mean">母平均 μ<input id="coverage-mean" name="mean" type="number" value="50" min="-1000000" max="1000000" step="any" required /></label><label for="coverage-sd">既知の母標準偏差 σ<input id="coverage-sd" name="sd" type="number" value="10" min="0.000001" max="1000000" step="any" required /></label><label for="coverage-n">1区間あたりの標本サイズ n<input id="coverage-n" name="n" type="number" value="100" min="1" max="10000" step="1" required /></label><label for="coverage-repetitions">繰返し回数（1〜1,000）<input id="coverage-repetitions" name="repetitions" type="number" value="100" min="1" max="1000" step="1" required /></label><label for="coverage-level">信頼係数<select id="coverage-level" name="level"><option value="90">90%</option><option value="95" selected>95%</option><option value="99">99%</option></select></label><label for="coverage-seed">seed<input id="coverage-seed" name="seed" type="number" value="12345" min="1" max="2147483646" step="1" required /></label><button type="submit">区間を繰り返し作る</button>'''
}
notes = {
'normal': '''<h2>予想してから動かす</h2><p>右側を選びzを0にすると何%になるでしょうか。zを1.96に戻し、平均と標準偏差だけを変えたとき、元の単位の境界と確率がどう変わるかを比べてください。</p><h2>条件と読み方</h2><p>Xが平均μ・標準偏差σの正規分布に従うモデルです。z=(X−μ)/σとして同じ標準化された境界を指定しています。標準化するだけで任意のデータが正規分布に変わるわけではありません。</p><p>曲線の表示範囲はμ±4σです。確率の表示値は、描画範囲の外の裾も含めて数値計算します。密度の高さではなく、曲線下の面積が確率です。中央を選ぶと境界の絶対値を左右に使います。</p><p>z=1.96より右の確率は約2.4998%です。正確な97.5%分位点を丸めた1.96を使っているため、厳密に2.5%ではありません。</p>''',
'frequency': '''<h2>予想してから動かす</h2><p>p=0.5、seedを同じにしたまま、回数を10、100、1,000と変えてください。割合が毎回0.5に近づき続けるとは限らないことと、長い目での安定を区別して観察します。</p><h2>条件と再現性</h2><p>独立で同じ成功確率を持つベルヌーイ試行のシミュレーションです。擬似乱数はseedで再現します。同じseed・同じpで回数だけ増やすと、最初の試行列は共通になります。これは乱数の暗号学的安全性や、現実の試行の独立性を保証する機能ではありません。</p><p>グラフの基準線は設定したp、折れ線は各時点までの相対度数です。次の試行が過去の不足分を埋め合わせる、という意味ではありません。図は表示点を間引くことがありますが、成功回数と最終割合は全試行から計算します。</p>''',
'coverage': '''<h2>予想してから動かす</h2><p>同じseedで信頼係数を90%、95%、99%と変え、区間の幅と真の母平均を含む本数を比べてください。標本サイズnを増やすと幅がどう変わるかも確かめます。</p><h2>この実験で仮定していること</h2><p>独立な正規標本と既知の母標準偏差σを仮定します。標本平均はN(μ,σ²/n)に従うので、その分布から標本平均を直接生成し、標本平均±z×σ/√nの区間を作ります。毎回n個の元データを描いているわけではありません。</p><p>真のμをここで指定できるのは、仕組みを学ぶためのシミュレーションだからです。実データの解析ではμは未知です。95%は同じ手順を繰り返したときの長期的な被覆率で、今回100回中ちょうど95本になる保証ではありません。</p><p>図は先頭30本まで、集計は設定したすべての区間を使います。●はμを含む区間、×は含まない区間です。色だけで判定しないよう記号も表示します。計算した観測例は定理の証明の代わりではありません。</p>'''
}
for slug, title, description, kind, lesson_slug in lab_specs:
    source = "---\nimport BaseLayout from '../../../layouts/BaseLayout.astro';\nimport { withBase } from '../../../lib/site';\nimport '../../../styles/learning.css';\n---\n"
    source += f'''<BaseLayout title="{title}" description="{description}"><div class="learning-shell lesson-shell"><nav class="learning-breadcrumb" aria-label="パンくず"><a href={{withBase('/courses/foundation/')}}>基礎コース</a><span> / </span><a href={{withBase('/labs/')}}>動かして学ぶ</a></nav><header class="learning-hero"><h1>{title}</h1><p>{description}</p></header><section class="release-box" data-foundation-lab="{kind}"><form class="lab-controls" data-lab-form>{forms[kind]}</form><p class="lab-result" data-lab-result aria-live="polite">実行すると、条件に対応する数値と図を表示します。</p><p class="lab-error" data-lab-error role="alert"></p><svg class="lab-graph" data-lab-graph viewBox="0 0 680 330" role="img" aria-labelledby="lab-figure-title lab-figure-desc"><title id="lab-figure-title">{title}</title><desc id="lab-figure-desc">操作後の図を表示する領域です。数値は図の上と下にも表示します。</desc></svg><div class="lab-value-table" data-lab-table></div><noscript><p>操作型の計算にはJavaScriptが必要です。下の説明と、関連する講座の図・数値例はJavaScriptなしでも読めます。</p></noscript></section><div class="release-prose">{notes[kind]}<p><a href={{withBase('/learn/{lesson_slug}/')}}>式・具体例・詳しい説明を講座で読む →</a></p></div><p class="release-note">計算はこのブラウザ内で行います。値を運営者のサーバーへ送信する機能はありません。</p></div></BaseLayout>\n<script>import '../../../scripts/foundation-labs.js';</script>'''
    write(f'src/pages/labs/{slug}/index.astro', source)

write('src/pages/labs/index.astro', '''---
import BaseLayout from '../../layouts/BaseLayout.astro';
import { withBase } from '../../lib/site';
import '../../styles/learning.css';
const labs = [
 {slug:'normal-area', title:'正規分布の面積', text:'平均・標準偏差・境界と、片側・中央の確率。'},
 {slug:'probability-frequency', title:'確率と観測頻度', text:'試行回数を変え、同じseedで相対度数を比較。'},
 {slug:'confidence-coverage', title:'信頼区間の繰返し', text:'区間の幅と、真の母平均を含む割合を観察。'}
];
---
<BaseLayout title="動かして学ぶ" description="統計の基礎を、条件を明示した再現可能な数値実験で確かめます。"><div class="learning-shell"><header class="learning-hero"><h1>動かして学ぶ</h1><p>操作する前に結果を予想し、数値と図で確かめます。</p></header>{labs.map(lab => <section class="release-box"><h2><a href={withBase(`/labs/${lab.slug}/`)}>{lab.title}</a></h2><p>{lab.text}</p></section>)}<p class="learning-note">実験は理解の補助です。使用条件や数学的な根拠は、対応する講座で確認してください。</p><a href={withBase('/courses/foundation/')}>基礎コースへ戻る</a></div></BaseLayout>
''')

write('src/scripts/foundation-labs.js', '''import { normalTailModel, normalDensity, bernoulliExperiment, coverageExperiment } from '../lib/foundation-labs.mjs';
const host=document.querySelector('[data-foundation-lab]');
const NS='http://www.w3.org/2000/svg';
function svgNode(name,attributes,text){const element=document.createElementNS(NS,name);for(const [key,value]of Object.entries(attributes??{}))element.setAttribute(key,String(value));if(text!==undefined)element.textContent=String(text);return element;}
function number(value){return Number(value).toLocaleString('ja-JP',{maximumFractionDigits:6});}
function table(container,headers,rows){container.replaceChildren();const element=document.createElement('table');const head=document.createElement('thead'),tr=document.createElement('tr');for(const value of headers){const th=document.createElement('th');th.scope='col';th.textContent=value;tr.append(th);}head.append(tr);element.append(head);const body=document.createElement('tbody');for(const row of rows){const r=document.createElement('tr');for(const value of row){const td=document.createElement('td');td.textContent=String(value);r.append(td);}body.append(r);}element.append(body);container.append(element);}
if(host){const form=host.querySelector('[data-lab-form]'),result=host.querySelector('[data-lab-result]'),error=host.querySelector('[data-lab-error]'),graph=host.querySelector('[data-lab-graph]'),values=host.querySelector('[data-lab-table]');
function resetGraph(description,height=330){const title=graph.querySelector('title').textContent;graph.replaceChildren(svgNode('title',{id:'lab-figure-title'},title),svgNode('desc',{id:'lab-figure-desc'},description));graph.setAttribute('viewBox',`0 0 680 ${height}`);}
function line(x1,y1,x2,y2,extra={}){graph.append(svgNode('line',{x1,y1,x2,y2,stroke:'#526371',...extra}));}
function label(x,y,text,extra={}){graph.append(svgNode('text',{x,y,fill:'#17222f','font-size':14,...extra},text));}
function run(event){event?.preventDefault();error.textContent='';host.dataset.ready='false';try{const input=Object.fromEntries(new FormData(form));for(const key of Object.keys(input))if(key!=='mode')input[key]=Number(input[key]);
if(host.dataset.foundationLab==='normal'){const model=normalTailModel(input);const probability=model.probability;result.textContent=`確率 ${number(probability*100)}% ／ 元の単位の境界 ${number(model.boundary)}`;result.dataset.probability=String(probability);resetGraph(`正規分布。z=${model.z}、領域=${model.mode}、確率=${probability}。曲線は標準化した−4から4まで。`);const x=z=>50+(z+4)/8*580,y=d=>275-d*540;line(50,275,630,275);const points=[];for(let i=0;i<=320;i++){const z=-4+i/40;points.push([z,x(z),y(normalDensity(z))]);}let region=points.filter(([z])=>model.mode==='upper'?z>=model.z:model.mode==='lower'?z<=model.z:Math.abs(z)<=Math.abs(model.z));if(region.length){const d=`M${region[0][1]},275 `+region.map(([,px,py])=>`L${px},${py}`).join(' ')+` L${region.at(-1)[1]},275 Z`;graph.append(svgNode('path',{d,fill:'#d6eaee'}));}graph.append(svgNode('path',{d:points.map(([,px,py],i)=>`${i?'L':'M'}${px},${py}`).join(' '),fill:'none',stroke:'#144a56','stroke-width':2.5}));for(const z of [-4,-2,0,2,4]){line(x(z),275,x(z),281);label(x(z),302,number(model.mean+model.sd*z),{'text-anchor':'middle'});}line(x(model.z),275,x(model.z),y(normalDensity(model.z)),{stroke:'#144a56','stroke-dasharray':'5 4'});label(52,23,'密度の下の面積が確率');table(values,['項目','値'],[['平均 μ',number(model.mean)],['標準偏差 σ',number(model.sd)],['z値',number(model.z)],['確率',`${number(probability*100)}%`]]);}
else if(host.dataset.foundationLab==='frequency'){const data=bernoulliExperiment(input);result.textContent=`${data.n}回中 ${data.successes}回成功 ／ 相対度数 ${number(data.frequency)}（設定したp=${number(data.p)}）`;result.dataset.successes=String(data.successes);resetGraph(`設定確率${data.p}、${data.n}回中${data.successes}回成功。最終相対度数${data.frequency}。`);const x=i=>50+(i-1)/Math.max(1,data.n-1)*580,y=p=>275-p*230;line(50,45,50,275);line(50,275,630,275);line(50,y(data.p),630,y(data.p),{stroke:'#526371','stroke-dasharray':'5 4'});const every=Math.max(1,Math.ceil(data.n/300));const selected=data.history.filter((_,index)=>index%every===0||index===data.n-1);graph.append(svgNode('path',{d:selected.map((row,index)=>`${index?'L':'M'}${x(row.trial)},${y(row.frequency)}`).join(' '),stroke:'#144a56','stroke-width':2,fill:'none'}));for(const p of [0,.5,1])label(40,y(p)+5,number(p),{'text-anchor':'end'});label(50,302,'1回');label(630,302,`${data.n}回`,{'text-anchor':'end'});label(52,23,'実線：相対度数 ／ 破線：設定した確率');const positions=[...new Set([1,2,5,10,20,50,100,500,1000,data.n].filter(n=>n<=data.n))].sort((a,b)=>a-b);table(values,['試行回数','累積成功数','相対度数'],positions.map(n=>{const row=data.history[n-1];return[n,row.successes,number(row.frequency)];}));}
else{const data=coverageExperiment(input);result.textContent=`${data.repetitions}区間中 ${data.covered}区間がμを含む（${number(data.covered/data.repetitions*100)}%）／ 標準誤差 ${number(data.se)}`;result.dataset.covered=String(data.covered);const shown=data.intervals.slice(0,30);const lower=Math.min(data.mean-data.halfWidth,...shown.map(row=>row.lower)),upper=Math.max(data.mean+data.halfWidth,...shown.map(row=>row.upper));const span=Math.max(upper-lower,Number.EPSILON),left=lower-span*.06,right=upper+span*.06;const height=70+shown.length*17;resetGraph(`信頼係数${data.level}%。${data.repetitions}区間中${data.covered}区間が真の母平均${data.mean}を含む。図は先頭${shown.length}本。`,height);const x=value=>55+(value-left)/(right-left)*555;line(x(data.mean),20,x(data.mean),height-30,{stroke:'#526371','stroke-dasharray':'5 4'});label(x(data.mean),16,`μ=${number(data.mean)}`,{'text-anchor':'middle'});for(const [i,row]of shown.entries()){const y=37+i*17;line(x(row.lower),y,x(row.upper),y,{stroke:row.contains?'#144a56':'#872b22','stroke-width':2});label(18,y+4,row.index);label(639,y+4,row.contains?'●':'×',{'text-anchor':'middle'});}label(55,height-7,number(left));label(610,height-7,number(right),{'text-anchor':'end'});table(values,['区間','標本平均','下限','上限','μを含む'],shown.slice(0,10).map(row=>[row.index,number(row.estimate),number(row.lower),number(row.upper),row.contains?'含む':'含まない']));}host.dataset.ready='true';}
catch(problem){error.textContent=problem instanceof Error?problem.message:'入力値を確認してください。';result.textContent='計算を更新していません。条件を修正して再実行してください。';values.replaceChildren();}}
form.addEventListener('submit',run);run();}
''')

# A searchable index uses original course text only. Never inject a user's query as HTML.
write('src/pages/search/index.astro', r'''---
import { getCollection } from 'astro:content';
import BaseLayout from '../../layouts/BaseLayout.astro';
import { withBase } from '../../lib/site';
import '../../styles/learning.css';
const lessons = (await getCollection('lessons', ({data}) => data.status === 'published')).sort((a,b)=>a.data.lesson_id.localeCompare(b.data.lesson_id));
function plain(value: string){return value.replace(/<[^>]*>/g,' ').replace(/\[([^\]]+)\]\([^)]+\)/g,'$1').replace(/[#*`]/g,'').replace(/\s+/g,' ').trim();}
const index = lessons.map(lesson=>({id:lesson.data.lesson_id,title:lesson.data.title,url:withBase(`/learn/${lesson.data.slug}/`),text:plain(lesson.body??''),details:Array.from((lesson.body??'').matchAll(/<details\b[^>]*id="([^"]+)"[^>]*>([\s\S]*?)<\/details>/g),match=>({id:match[1],text:plain(match[2])}))}));
---
<BaseLayout title="基礎講座を検索" description="全40講座の本文・詳しい説明・解答を検索し、該当する講座へ戻れます。"><div class="learning-shell lesson-shell"><header class="learning-hero"><h1>基礎講座を検索</h1><p>用語だけでなく、「なぜ」「違い」などの本文も探せます。</p></header><form class="course-search-form" data-course-search method="get"><label for="course-search-query">探したい言葉<input class="course-search-input" id="course-search-query" name="q" type="search" maxlength="200" autocomplete="off" /></label><button type="submit">検索</button></form><p class="release-note" data-search-count aria-live="polite">全{index.length}講座</p><ul class="course-search-results" data-search-results>{index.map(item=><li><a href={item.url}><strong>{item.id} {item.title}</strong></a></li>)}</ul><noscript><p>本文の絞り込みにはJavaScriptを使用します。この一覧から全講座へ移動できます。</p></noscript><a href={withBase('/courses/foundation/')}>章別の目次へ戻る</a></div></BaseLayout>
<script type="application/json" id="foundation-search-index" is:inline set:html={JSON.stringify(index).replace(/</g,'\\u003c')} />
<script>
const form=document.querySelector<HTMLFormElement>('[data-course-search]');
const input=document.querySelector<HTMLInputElement>('#course-search-query');
const result=document.querySelector<HTMLElement>('[data-search-results]');
const count=document.querySelector<HTMLElement>('[data-search-count]');
const raw=document.getElementById('foundation-search-index')?.textContent;
type Item={id:string;title:string;url:string;text:string;details:{id:string;text:string}[]};
const index:Item[]=raw?JSON.parse(raw):[];
function search(){if(!input||!result||!count)return;const query=input.value.trim().slice(0,200);const words=query.toLocaleLowerCase().split(/\s+/).filter(Boolean);const found=index.filter(item=>words.every(word=>(item.title+' '+item.text).toLocaleLowerCase().includes(word)));result.replaceChildren();for(const item of found){const li=document.createElement('li'),link=document.createElement('a'),strong=document.createElement('strong');const detail=words.length?item.details.find(part=>words.every(word=>part.text.toLocaleLowerCase().includes(word))):undefined;link.href=item.url+(detail?'#'+encodeURIComponent(detail.id):'');strong.textContent=item.id+' '+item.title;link.append(strong);li.append(link);if(query){const p=document.createElement('p');const text=detail?.text??item.text;const start=Math.max(0,text.toLocaleLowerCase().indexOf(words[0])-40);p.textContent=(detail?'詳しい説明・解答：':'')+(start?'…':'')+text.slice(start,start+180)+'…';li.append(p);}result.append(li);}count.textContent=words.length?found.length+'講座が見つかりました':'全'+index.length+'講座';}
if(input){input.value=new URLSearchParams(window.location.search).get('q')?.slice(0,200)??'';input.addEventListener('input',search);}
form?.addEventListener('submit',event=>{event.preventDefault();search();if(input){const url=new URL(window.location.href);if(input.value.trim())url.searchParams.set('q',input.value.trim());else url.searchParams.delete('q');history.replaceState(null,'',url);}});search();
</script>
''')

# Course links are descriptive; they do not claim completion of grade 2/pre-1/1 courses.
course_path='src/pages/courses/foundation/index.astro'
course_page=read(course_path)
if 'data-release-navigation' not in course_page:
    nav='''<section class="release-box" data-release-navigation><h2>学び方を選ぶ</h2><div class="lab-links"><a href={withBase('/search/')}>講座の本文を検索</a><a href={withBase('/labs/')}>図を動かして確かめる</a><a href={withBase('/courses/foundation/coverage/')}>学習範囲を見る</a></div></section>'''
    course_page=course_page.replace('<section class="course-contents"',nav+'\n<section class="course-contents"',1)
course_page=course_page.replace('準備中の講座はまだ読めず、現時点で全範囲の教材が揃っているわけではありません。','この基礎コースの全40講座を掲載しています。公式範囲の項目は学習範囲表で確認できますが、合格や公式教材との同等性を保証するものではありません。')
write(course_path,course_page)

page_map={row['slug']:row for row in planned}
for lesson_slug,lab_slug in [('normal-density-basics','normal-area'),('normal-table-and-tail-area','normal-area'),('probability-and-repetition','probability-frequency'),('mean-confidence-interval-basics','confidence-coverage')]:
    p=f'src/content/lessons/{lesson_slug}.md'
    body=read(p)
    marker=f'<!-- release-lab:{lab_slug} -->'
    if marker not in body:
        link=f'{marker}\n\n### 図を動かして確かめる\n\n[関連する数値実験を開く](https://matsu71.github.io/Statistics_Blog/labs/{lab_slug}/)。まず結果を予想し、条件を変えて確かめてから、この講座の式と説明へ戻ってください。数値実験は証明の代わりではありません。\n\n'
        body=body.replace('## まとめと次の一歩',link+'## まとめと次の一歩',1)
        write(p,body)

coverage_groups=[
 ('問題解決・データの種類',['F01','F02','F03','F39']),
 ('全数調査・標本調査・実験',['F04','F05','F34']),
 ('度数・相対度数・累積度数',['F06','F07','F08']),
 ('基本グラフ・クロス集計・特殊な図',['F09','F10','F11']),
 ('代表値と重み',['F12','F13']),
 ('四分位数・箱ひげ図・散らばり',['F14','F15','F16']),
 ('標準化・偏差値・変動係数',['F17','F18']),
 ('相関・回帰・擬相関・因果',['F19','F20','F21']),
 ('時系列・指数・増減率・移動平均',['F06','F22']),
 ('事象・場合の数・独立・条件付き確率',['F23','F24','F25','F26','F27','F28']),
 ('確率変数・期待値・分散',['F29']),
 ('二項分布・正規分布・近似',['F30','F31','F32','F33']),
 ('標本平均・比率の分布と標準誤差',['F34']),
 ('母平均・母比率の区間推定',['F35','F36']),
 ('仮説・p値・平均・比率の検定',['F37','F38']),
 ('分析の報告・横断的な理解確認',['F39','F40'])
]
lookup={row['id']:row for row in planned}
coverage=[{'topic':topic,'lessons':[{'id':ident,'slug':lookup[ident]['slug'],'title':lookup[ident]['title']} for ident in ids]} for topic,ids in coverage_groups]
write_json('src/data/foundation-coverage.json',coverage)
write('src/pages/courses/foundation/coverage/index.astro', '''---
import BaseLayout from '../../../../layouts/BaseLayout.astro';
import { withBase } from '../../../../lib/site';
import coverage from '../../../../data/foundation-coverage.json';
import '../../../../styles/learning.css';
---
<BaseLayout title="基礎コースの学習範囲" description="基礎全40講座の内容と、参照した統計検定4級・3級の公式範囲を確認できます。"><div class="learning-shell lesson-shell"><header class="learning-hero"><h1>基礎コースの学習範囲</h1><p>4級・3級の内容を統合し、2級へ進むための学習順に並べています。</p></header><div class="release-prose"><p>以下の分類は学習用の整理です。各公式小項目の出題頻度、公式問題との同等性、合格を保証するものではありません。実施方法や最新の出題範囲は公式案内をご確認ください。</p><p><a href="https://www.toukei-kentei.jp/grade/grade3/">3級の公式案内</a> · <a href="https://www.toukei-kentei.jp/grade/grade4/">4級の公式案内</a></p>{coverage.map(group=><section class="release-box"><h2>{group.topic}</h2><ul>{group.lessons.map(lesson=><li><a href={withBase(`/learn/${lesson.slug}/`)}>{lesson.id} {lesson.title}</a></li>)}</ul></section>)}<p>図・説明・確認問題・解答を各講座に用意しています。計算中心の講座では適用条件を確認し、必要な導出を折りたたんで掲載しています。2級・準1級・1級の順序コースは、別の制作段階です。</p></div><a href={withBase('/courses/foundation/')}>基礎コースの目次へ戻る</a></div></BaseLayout>
''')

public_pages={
'about':('このサイトについて','''<p>統計ラボは、具体例から統計を学び、必要な数式や根拠を確かめる日本語の学習サイトです。基礎コースは4級・3級の内容を統合した全40講座です。</p><p>統計検定の公式教材・公認講座ではありません。問題、説明用データ、図は独自に作成し、参照した資料を各講座に示しています。架空データを実際の調査結果として扱いません。</p><h2>内容の確認</h2><p>式・具体例・解答の自己点検と、数値の再計算、表示・リンク・操作のテストを行っています。独立した第三者の数学監修や、学習効果の比較試験が済んだという意味ではありません。AIを制作・点検の補助に使用しています。</p><p>誤りを見つけた場合は、該当する講座・箇所・理由を訂正窓口へお知らせください。学習内容は教育用であり、個別の医療・法律・投資などの判断を提供するものではありません。</p>'''),
'editorial-policy':('教材の編集方針','''<h2>入口は読みやすく、根拠は省かない</h2><p>基本の説明、使用条件、具体例は開いた状態で表示します。詳しい導出・証明・発展は、その内容と前提が分かる見出しで折りたたみます。定義、定理、近似、モデルの仮定、数値実験を区別します。</p><h2>問題と出典</h2><p>各講座の確認問題は独自制作です。答えだけでなく、計算の理由と典型的な取り違えを説明します。外部教材の文章・図・問題を、そのまま転載したり数値だけ変更して使用したりしません。参照資料へのリンクを付けます。</p><h2>訂正と限界</h2><p>訂正はGitHubの変更履歴に残します。解答や適用条件に影響する変更は訂正情報にも記載します。自己点検を第三者監修と表示せず、自動テストの成功を教育効果の証明とは扱いません。</p>'''),
'privacy':('入力情報の扱い','''<p>基礎講座の閲覧に、氏名やメールアドレスの登録は必要ありません。</p><h2>検索と数値実験</h2><p>講座内検索の絞り込みと数値実験は、ブラウザ内で処理します。これらの機能には入力を運営者のサーバーへ送信する処理を実装していません。検索語をURLに反映した場合はブラウザの履歴や共有URLに残るため、個人情報や機密情報を入力しないでください。</p><h2>配信元と外部サービス</h2><p>サイトはGitHub Pagesで配信します。配信に伴うアクセス情報や、外部リンク先の情報の扱いは、それぞれのサービスの方針が適用されます。訂正窓口のGitHub Issueは公開情報になるため、個人情報を書かないでください。</p><p><a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHubのプライバシーに関する説明</a></p>'''),
'contact':('訂正・お問い合わせ','''<p>講座の誤りや表示の問題は、GitHub Issueで受け付けます。GitHubへのログインが必要です。講座のURL、問題の箇所、期待する内容、使用端末を、必要な範囲で記載してください。</p><p><a href="https://github.com/Matsu71/Statistics_Blog/issues/new?title=%E6%95%99%E6%9D%90%E3%81%AE%E8%A8%82%E6%AD%A3%E3%83%BB%E8%A1%A8%E7%A4%BA%E3%81%AE%E5%A0%B1%E5%91%8A">訂正を報告する</a></p><p>Issueは公開されます。氏名、連絡先、顧客情報、非公開の試験問題などは書き込まないでください。確認後、必要に応じて本文・問題・訂正情報を更新します。</p>'''),
'errata':('訂正情報','''<h2>基礎コース初版の監査</h2><p>第14講の箱ひげ図では、五数要約と目盛りの位置を同じ比例尺度に統一しました。第15講では、不偏分散の平方根から求める標準偏差の不偏性について、対象を明確にする表現へ訂正しました。</p><p>第4講には乱数表で範囲外・重複を除外する具体例を、第9講には棒・円グラフによる同じデータの比較を追加しました。これらは初版公開前の補強です。</p><p>最新の変更内容は<a href="https://github.com/Matsu71/Statistics_Blog/commits/main/">GitHubの変更履歴</a>で確認できます。以前の記述に基づいて学習した場合は、該当講座の説明を読み直してください。</p>''')
}
for slug,(title,body) in public_pages.items():
    write(f'src/pages/{slug}/index.astro',f'''---\nimport BaseLayout from '../../layouts/BaseLayout.astro';\nimport {{ withBase }} from '../../lib/site';\nimport '../../styles/learning.css';\n---\n<BaseLayout title="{title}" description="統計ラボの{title}。"><div class="learning-shell lesson-shell"><header class="learning-hero"><h1>{title}</h1></header><div class="release-prose">{body}</div><a href={{withBase('/courses/foundation/')}}>基礎コースへ戻る</a></div></BaseLayout>''')
footer_path='src/components/SiteFooter.astro'
footer=read(footer_path)
if 'release-footer-links' not in footer:
    # Links include the deployment base and work without JavaScript.
    links='<nav class="release-footer-links site-shell" aria-label="運営と学習の案内">'+''.join(f'<a href="/Statistics_Blog/{slug}/">{title}</a>' for slug,(title,_) in public_pages.items())+'<a href="/Statistics_Blog/search/">講座を検索</a><a href="/Statistics_Blog/labs/">数値実験</a></nav>'
    footer=footer.replace('</footer>',links+'\n</footer>',1)
    if 'release-footer-links' not in footer:
        raise RuntimeError('Cannot safely extend the site footer.')
    write(footer_path,footer)

# Record dated source retrieval without republishing third-party pages.
sources=[
 ('bellcurve','https://bellcurve.jp/statistics/course/','段階別の教材と練習問題を参照する比較対象。'),
 ('toketarou','https://toketarou.com/cheatsheet/','要点整理と関連講義への導線を参照する比較対象。'),
 ('openintro','https://openintro-ims.netlify.app/data-design','研究設計と結論の範囲を結び付ける入門教材。'),
 ('openstax','https://openstax.org/books/introductory-statistics-2e/pages/1-1-definitions-of-statistics-probability-and-key-terms','定義・具体例・練習を組み合わせる入門教材。'),
 ('seeing-theory','https://seeing-theory.brown.edu/','操作と観察による確率・統計教材。'),
 ('statlect','https://www.statlect.com/probability-distributions/normal-distribution','正規分布の定義・性質・証明の確認先。'),
 ('exam3','https://www.toukei-kentei.jp/grade/grade3/','3級の公式案内。'),
 ('exam4','https://www.toukei-kentei.jp/grade/grade4/','4級の公式案内。')
]
evidence=[]
for ident,url,purpose in sources:
    item={'id':ident,'url':url,'purpose':purpose,'checked_at':NOW}
    try:
        request=Request(url,headers={'User-Agent':'Statistics-Lab-Editorial-Review/1.0'})
        with urlopen(request,timeout=35) as response:
            payload=response.read(4_000_000)
            item.update(http_status=response.status,final_url=response.url,sha256=hashlib.sha256(payload).hexdigest())
        decoded=payload.decode('utf-8','replace')
        title=re.search(r'<title[^>]*>([\s\S]*?)</title>',decoded,re.I)
        item['page_title']=html.unescape(re.sub('<[^>]*>','',title.group(1))).strip()[:160] if title else None
        item['retrieval']='success'
    except Exception as exc:
        item['retrieval']='unconfirmed'
        item['error']=str(exc)[:200]
    evidence.append(item)
write_json('project-docs/learning-platform-design/18-reference-check.json',evidence)
write_json('project-docs/learning-platform-design/17-editorial-corrections.json',{'checked_at':NOW,'corrections':corrections,'method':'Targeted corrections inherited from the preceding content review; arithmetic and rendering gates run separately.','independent_human_review':False})

report='''# 基礎コースの競合比較・不足の修正・リリース判断

対象は今回合意した基礎40講座です。2級・準1級・1級の将来コースや307候補全体が完成したという意味ではありません。

## 比較の方法と限界

既存の調査01・09と今回の公開ページの到達確認を組み合わせ、学習順序、説明、例、問題、導出、図、操作、検索、出典、訂正の観点で本サイトの不足を点検しました。全競合記事の数学監査、動画全編の視聴、利用者の学習効果の比較実験ではありません。公開ページの到達記録は18-reference-check.jsonに保存しています。取得できなかったページについて、新しく確認できたとは扱いません。

|比較対象|参考にする点|本サイトで見つけた不足|今回の対応|
|---|---|---|---|
|統計WEB|段階的な教材、図と例、練習問題、数学の補助|後半の予定講座が未制作、いくつかのグラフが説明のみ|全40講座を揃え、解答付き129問を用意。棒・円・箱ひげの図、乱数表の具体例を補強|
|とけたろう|要点を見渡せる整理と関連講義への導線|順序教材の本文を探す導線が不足|章別目次と全文検索を追加。必要な詳説・解答へ直接移動|
|OpenIntro / OpenStax|問い・データ収集・分析・結論を結ぶ例と演習|手法の暗記だけで終わる危険、再計算できる事例の不足|観察と実験、抽出と割付、欠測、解釈の限界を明示。CSVによる再現可能な総合例を掲載|
|Seeing Theory|操作によって分布や標本変動を観察|静的な説明だけでは標本変動をつかみにくい|正規分布の面積、確率と頻度、信頼区間の被覆の3実験を追加。seedと仮定を表示|
|Statlect|仮定を伴う定義・性質・証明|基本説明と数学的な確認が混ざる危険|正規化積分・平均分散・変数変換を分離。導出・証明は折りたたみ、使用条件は基本表示|

これらの特徴は各教材の公開構成を参照したもので、同じ機能が他サイトに存在しないと断定していません。記事数や字数だけで品質の順位を付けず、競合を上回る学習効果が実証されたとも表示しません。

## リリース前の必須条件

全40講座に目標・具体例・問題・解答・条件・出典があり、数値検証・別実装の照合・数式表示・内部リンク・モバイルとPCの操作テストを通すこと。重大な既知の誤りと本番依存の重大な監査警告を残さないこと。検証した生成物を公開し、そのURLが実際に取得できること。

40講座が存在するだけで自動的に公開可とはしません。実際の検証結果は10・12・13および19以降の機械記録、公開確認はリリース進捗を参照してください。

## 公開後も残る改善点

本サイトには講義動画、独立した専門家による監修、実利用者による学習効果比較、網羅的な支援技術・実機試験はまだありません。問題の数値だけを増やすのではなく、別の文脈へ応用できる追加問題と利用者の誤解を確認する必要があります。これらを実施済みとは表示しません。

この基礎版では会員登録・課金・自動採点・学習履歴同期は必須機能にしません。教材・解答・全文検索・数値実験・訂正窓口を提供する無料の静的学習サイトとして公開判定します。

## 次の作業

基礎版の公開後は、訂正受付と利用者のつまずきの確認を継続し、その結果を反映しながら2級コースの詳細対応表・初期教材へ進みます。次の制作対象と未実施項目は11-completion-progress.mdを正本として更新します。
'''
write('project-docs/learning-platform-design/15-competitor-comparison-and-release.md',report)

release=json.loads(read('src/data/foundation-release.json'))
release.update(stage='release_candidate',scope='foundation_40_lessons',expected_lessons=40,expected_questions=129,prepared_at=NOW)
write_json('src/data/foundation-release.json',release)
write('project-docs/learning-platform-design/11-completion-progress.md',f'''# 基礎コース完成作業の進捗

更新：{NOW}

## 目的

基礎40講座を全件制作し、内容・計算・表示・公式範囲とのつながり・競合との不足比較を確認して、検証したものをサービスとして公開する。品質を下げて本数だけを揃えない。

## このチェックポイント

全40講座の原稿と129問を引き継ぎ、F04・F09・F14・F15の補強と修正、横長表の局所スクロール、3つの数値実験、講座の全文検索、学習範囲表、運営・訂正窓口を準備した。

**状態は公開候補です。ここに準備しただけでは全検証・公開完了とはしません。** 次のCIで既存講座を含むビルドと数式・リンク・計算・ブラウザ・依存関係を検証します。検証後に生成物と結果を保存し、mainと公開URLを確認して完了を記録します。

## 次の実行

1. package-lockを固定し、全既存テストと追加の数値実験・検索テストを実行。
2. 不合格があれば、その内容を修正して同じ検証を再実行。
3. 成功したソース・生成物・監査記録を保存し、mainへ非強制で反映。
4. GitHub Pagesの公開と全40URLを確認し、次の作業を2級コースへ更新。

独立した人間の監修、学習効果比較、全端末・スクリーンリーダーでの確認は未実施です。競合比較の限界と未着手の改善は15の文書に記載しています。
''')
readme=read('README.md')
if '<!-- FOUNDATION_FULL_RELEASE_20260911 -->' not in readme:
    intro='''<!-- FOUNDATION_FULL_RELEASE_20260911 -->
# 統計ラボ：基礎コース全40講座

基礎（4級・3級統合）→2級→準1級→1級の構成で学ぶためのサイトです。今回の公開候補は基礎40講座と独自問題129問です。2級以降の順序コース全体が完成したという意味ではありません。

[基礎コース](https://matsu71.github.io/Statistics_Blog/courses/foundation/) · [全文検索](https://matsu71.github.io/Statistics_Blog/search/) · [数値実験](https://matsu71.github.io/Statistics_Blog/labs/) · [最新の進捗・次の作業](project-docs/learning-platform-design/11-completion-progress.md) · [競合比較と公開基準](project-docs/learning-platform-design/15-competitor-comparison-and-release.md)

以下の初期6講座・未実装に関する文章は過去の段階の記録です。現在の実装範囲・検証状態・公開確認は上記の進捗と最新の監査記録を優先してください。

---

'''
    write('README.md',intro+readme)
print(json.dumps({'stage':'release_candidate_prepared','lessons':40,'questions':129,'corrections':corrections,'sources':len(evidence)},ensure_ascii=False))
