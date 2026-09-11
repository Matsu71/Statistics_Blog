from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[2]

def patch(path,old,new,required=True):
    p=ROOT/path
    s=p.read_text(encoding='utf-8')
    if old in s:
        p.write_text(s.replace(old,new),encoding='utf-8')
    elif required and new not in s:
        raise RuntimeError(f'Expected source fragment was not found in {path}')

ignore=ROOT/'.gitignore'
s=ignore.read_text() if ignore.exists() else ''
for rule in ['__pycache__/','*.py[cod]','review-assets/']:
    if rule not in s.splitlines():s=s.rstrip()+'\n'+rule+'\n'
ignore.write_text(s)

p=ROOT/'src/content/lessons/quartiles-and-boxplots.md'
s=p.read_text()
s=re.sub(r'(<svg\b[\s\S]*?f14-release-box-title[\s\S]*?</svg>)',lambda m:m.group(1).replace('font-size="13"','font-size="22"'),s,count=1)
p.write_text(s)
p=ROOT/'src/content/lessons/choosing-basic-graphs.md'
s=p.read_text()
for ident in ['f09-bars-title','f09-pie-title']:
    s=re.sub(r'<svg\b(?:(?!</svg>)[\s\S])*?'+ident+r'(?:(?!</svg>)[\s\S])*?</svg>',lambda m:m.group(0).replace('font-size="16"','font-size="24"'),s,count=1)
p.write_text(s)

p=ROOT/'src/content/lessons/reading-unfamiliar-graphs.md'
s=p.read_text()
marker='f11-release-radar-abcd'
if marker not in s:
    supplement='''## レーダー図は、項目の順序でも形が変わる

別の作例として、同じ0〜5の基準にそろえた4項目がA=1、B=2、C=3、D=4だったとします。次の二つの図は数値を変えず、右と下の項目の位置だけを入れ替えています。

<figure><svg viewBox="0 0 500 300" style="max-width:500px" role="img" aria-labelledby="f11-release-radar-abcd f11-radar-abcd-desc"><title id="f11-release-radar-abcd">項目をA・B・C・Dの順に配置したレーダー図</title><desc id="f11-radar-abcd-desc">上から時計回りにA1、B2、C3、D4。各軸の最大値は5。面積だけで総合的な優劣を判断しないための作例。</desc><g stroke="#c7d1db" fill="none"><path d="M250 132L268 150L250 168L232 150Z M250 114L286 150L250 186L214 150Z M250 96L304 150L250 204L196 150Z M250 78L322 150L250 222L178 150Z M250 60L340 150L250 240L160 150Z"/><path d="M250 60V240 M160 150H340"/></g><path d="M250 132L286 150L250 204L178 150Z" fill="#d6eaee" stroke="#144a56" stroke-width="3"/><g fill="currentColor" font-size="22" text-anchor="middle"><text x="250" y="35">A：1</text><text x="393" y="158">B：2</text><text x="250" y="278">C：3</text><text x="105" y="158">D：4</text></g></svg><figcaption>時計回りの順序はA・B・C・Dです。外周はすべて5、目盛りは1刻みです。</figcaption></figure>

<figure><svg viewBox="0 0 500 300" style="max-width:500px" role="img" aria-labelledby="f11-release-radar-acbd f11-radar-acbd-desc"><title id="f11-release-radar-acbd">同じ値をA・C・B・Dの順に配置したレーダー図</title><desc id="f11-radar-acbd-desc">上から時計回りにA1、C3、B2、D4。各値と目盛りは一つ目の図と同じだが、隣り合う項目を変えたため面積が変わる。</desc><g stroke="#c7d1db" fill="none"><path d="M250 132L268 150L250 168L232 150Z M250 114L286 150L250 186L214 150Z M250 96L304 150L250 204L196 150Z M250 78L322 150L250 222L178 150Z M250 60L340 150L250 240L160 150Z"/><path d="M250 60V240 M160 150H340"/></g><path d="M250 132L304 150L250 186L178 150Z" fill="#d6eaee" stroke="#144a56" stroke-width="3"/><g fill="currentColor" font-size="22" text-anchor="middle"><text x="250" y="35">A：1</text><text x="393" y="158">C：3</text><text x="250" y="278">B：2</text><text x="105" y="158">D：4</text></g></svg><figcaption>時計回りの順序だけをA・C・B・Dに変更しました。値が改善したわけではありません。</figcaption></figure>

4本の軸が直交し、隣り合う値を直線で結ぶこの図では、面積は隣の二つの値の積に依存します。したがって、同じ数値でも項目の並びで面積が変わります。レーダー図は各項目の特徴を読む補助として使い、面積だけを根拠のない総合得点にしないようにします。

## 二つの縦軸では、単位を読み分ける

次の架空例は、売上を左軸の万円、問い合わせ数を右軸の件で表しています。実線が売上、破線が問い合わせです。同じ高さでも、同じ量を表しているわけではありません。

<figure><svg viewBox="0 0 500 315" style="max-width:500px" role="img" aria-labelledby="f11-dual-axis-title f11-dual-axis-desc"><title id="f11-dual-axis-title">左軸の売上と右軸の問い合わせ件数を重ねた図</title><desc id="f11-dual-axis-desc">1月、2月、3月の売上は10、20、30万円。問い合わせは100、250、150件。左の0、10、20、30万円と、右の0、100、200、300件が同じ高さにある。</desc><path d="M60 65V250H440V65" fill="none" stroke="currentColor"/><g stroke="#dfe5eb"><path d="M60 70H440 M60 130H440 M60 190H440"/></g><path d="M90 190L250 130L410 70" fill="none" stroke="#144a56" stroke-width="3"/><path d="M90 190L250 100L410 160" fill="none" stroke="#526371" stroke-width="3" stroke-dasharray="8 5"/><g fill="#144a56"><circle cx="90" cy="190" r="5"/><circle cx="250" cy="130" r="5"/><circle cx="410" cy="70" r="5"/></g><g fill="currentColor" font-size="21"><text x="8" y="35">売上（万円）</text><text x="492" y="35" text-anchor="end">問い合わせ（件）</text><text x="49" y="257" text-anchor="end">0</text><text x="49" y="197" text-anchor="end">10</text><text x="49" y="137" text-anchor="end">20</text><text x="49" y="77" text-anchor="end">30</text><text x="447" y="257">0</text><text x="447" y="197">100</text><text x="447" y="137">200</text><text x="447" y="77">300</text><text x="90" y="288" text-anchor="middle">1月</text><text x="250" y="288" text-anchor="middle">2月</text><text x="410" y="288" text-anchor="middle">3月</text></g></svg><figcaption>実線＝売上（左軸）、破線＝問い合わせ（右軸）。二つの軸を同じ単位として読みません。</figcaption></figure>

|月|1月|2月|3月|
|---|---:|---:|---:|
|売上（万円・左軸）|10|20|30|
|問い合わせ（件・右軸）|100|250|150|

問い合わせが増えたから売上が増えた、とこの図だけから因果関係を結論することもできません。別の尺度を重ねる必要があるかを考え、読み取りにくい場合は別々の図に分けます。

'''
    if '## 確認問題' not in s:raise RuntimeError('F11 question section missing')
    s=s.replace('## 確認問題',supplement+'## 確認問題',1)
    p.write_text(s)

css=ROOT/'src/styles/learning-release.css'
s=css.read_text()
if '/* Mobile figure labels */' not in s:
    s+='\n/* Mobile figure labels */\n@media(max-width:600px){.lab-graph text{font-size:26px}.lab-graph{max-height:none}}\n'
    css.write_text(s)

p=ROOT/'src/scripts/foundation-labs.js'
s=p.read_text()
if 'function axisNumber(' not in s:
    s=s.replace('function table(container,headers,rows)',"function axisNumber(value){return value!==0&&(Math.abs(value)>=10000||Math.abs(value)<.001)?value.toExponential(1):number(value);}\nfunction table(container,headers,rows)")
s=s.replace('number(model.mean+model.sd*z)','axisNumber(model.mean+model.sd*z)')
s=s.replace("label(52,23,'実線：相対度数 ／ 破線：設定した確率')","label(52,30,'実線：観測 ／ 破線：確率')")
s=s.replace("label(52,23,'密度の下の面積が確率')","label(52,30,'密度の下の面積が確率')")
s=s.replace('const shown=data.intervals.slice(0,30);','const mobile=window.matchMedia(\'(max-width:600px)\').matches;const shown=data.intervals.slice(0,mobile?12:30);const rowStep=mobile?38:17;')
s=s.replace('const height=70+shown.length*17;','const height=(mobile?100:70)+shown.length*rowStep;')
s=s.replace("label(x(data.mean),16,`μ=${number(data.mean)}`","label(x(data.mean),mobile?30:16,`μ=${axisNumber(data.mean)}`")
s=s.replace('const y=37+i*17;','const y=(mobile?55:37)+i*rowStep;')
s=s.replace('number(left));label(610,height-7,number(right)','axisNumber(left));label(610,height-7,axisNumber(right)')
p.write_text(s)

comparison=ROOT/'project-docs/learning-platform-design/15-competitor-comparison-and-release.md'
s=comparison.read_text()
s=s.replace('棒・円・箱ひげの図、乱数表の具体例を補強','棒・円・箱ひげ・レーダー・二重軸の図、乱数表の具体例を補強')
comparison.write_text(s)
log=ROOT/'project-docs/learning-platform-design/17-editorial-corrections.json'
audit=json.loads(log.read_text())
audit['corrections'].append({'lesson':'F11','change':'レーダー図の並びによる見え方の違いと、二つの縦軸の読み方を、独自の図と元データ表で補強。'})
audit['corrections'].append({'lesson':'labs','change':'小画面の図中文字を拡大し、信頼区間の図は小画面では先頭12本に減らす。集計は全反復を使用。'})
log.write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n')
print('Figure, responsive-layout and reproducibility corrections applied.')
