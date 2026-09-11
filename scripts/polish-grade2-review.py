"""Apply findings to review copies; keep published foundation content unchanged."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'review/grade2/20260911'

def change(text, old, new):
    if new in text: return text
    if old not in text: raise ValueError('Review change no longer matches: '+old[:90])
    return text.replace(old,new)

def main():
    report_path=ROOT/'project-docs/grade2/review-workspace.json'
    report=json.loads(report_path.read_text(encoding='utf-8'))
    path=WORK/'candidate/errors-power-sample-size.md'
    text=path.read_text(encoding='utf-8')
    text=change(text,'上の一側既知分散モデルで、差Δ>0、目標検出力1−βを事前に定めると、',
        '上の一側既知分散モデルで、σ>0、Δ>0、0<α<1、0<β<1とします。通常の設計として、目標検出力1−βが有意水準αより大きい場合、')
    text=change(text,'Δ>0なので整理し、√n≥(z_{1−α}+z_{1−β})σ/Δを二乗して本文の式になります。',
        'Δ>0なので整理し、√n≥(z_{1−α}+z_{1−β})σ/Δです。本文では1−β>αを仮定しており、右辺が正なので、二乗して同値な条件を得られます。\n\n目標検出力がα以下の場合は右辺が0以下で、この不等式はすでにすべての正の整数nで満たされます。負の右辺をそのまま二乗して、必要な標本数を大きくしてはいけません。一般には、正の整数という条件も含め、次で最小数を表せます。\n\n$$\nn_{\\min}=\\max\\left\\{1,\\left\\lceil\\left(\\frac{\\sigma}{\\Delta}\\max\\{0,z_{1-\\alpha}+z_{1-\\beta}\\}\\right)^2\\right\\rceil\\right\\}.\n$$\n\nこれは指定した一側・既知分散・正規モデルの設計式です。目標80%などの通常の設定では本文の式に一致します。')
    if '[NIST: Sample sizes required]' not in text:
        text += '\n[NIST: Sample sizes required](https://www.itl.nist.gov/div898/handbook/prc/section2/prc222.htm)も、差・分散・有意水準・検出力を先に指定する設計の関連資料として確認しました。追加確認日2026-09-11。\n'
    path.write_text(text,encoding='utf-8')
    (ROOT/'src/content/grade2'/path.name).write_text(text,encoding='utf-8')
    for record in report['records']:
        if record['id']=='G26':
            record['candidate_sha256']=sha256(text.encode()).hexdigest()
    report['polish']={'checked_at':datetime.now(timezone.utc).isoformat(),
        'findings':['Positive-right-hand-side condition before squaring the power inequality.',
                    'Prevent line wrapping within numerical table cells on a small screen.'],
        'status':'candidate_changes_await_full_reverification'}
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    css=ROOT/'src/styles/learning.css'
    old=css.read_text(encoding='utf-8')
    marker='/* grade2-numeric-table-legibility */'
    if marker not in old:
        old += '''
/* grade2-numeric-table-legibility */
[data-grade2-lesson] .lesson-body td[align="right"]{white-space:nowrap;overflow-wrap:normal;text-align:right;font-variant-numeric:tabular-nums}
[data-grade2-lesson] .lesson-body th[align="right"]{min-width:5rem}
[data-grade2-lesson] .lesson-body tbody td:first-child{overflow-wrap:normal;word-break:normal}
[data-lesson-id="G39"] tbody td:first-child{min-width:6rem}
.grade2-table-note{font-size:.8rem;color:var(--muted);margin:.5rem 0}
@media(min-width:601px){.grade2-table-note{display:none}}
'''
        css.write_text(old,encoding='utf-8')
    page=ROOT/'src/pages/learn/grade2/[slug].astro'
    raw=page.read_text(encoding='utf-8')
    raw=change(raw,'    <article class="lesson-body" data-lesson-id={lesson.data.lesson_id}><Content /></article>',
        '    <p class="grade2-table-note">横長の表や数式は、その部分を横へスクロールして確認できます。</p>\n    <article class="lesson-body" data-lesson-id={lesson.data.lesson_id}><Content /></article>')
    if 'function refreshScrollableTables()' not in raw:
        insertion='''    // Preserve native table semantics; make only overflowing tables focusable.
    function refreshScrollableTables() {
      root?.querySelectorAll<HTMLTableElement>('.lesson-body table').forEach((table, index) => {
        if (table.scrollWidth > table.clientWidth + 1) {
          table.tabIndex = 0;
          table.setAttribute('aria-label', `表${index + 1}。左右の矢印キーでもスクロールできます。`);
        } else {
          table.removeAttribute('tabindex');
          table.removeAttribute('aria-label');
        }
      });
    }
    void document.fonts.ready.then(refreshScrollableTables);
    window.addEventListener('resize', refreshScrollableTables);
    root?.addEventListener('toggle', refreshScrollableTables, true);
'''
        raw=raw.replace("    const details = () =>",insertion+"    const details = () =>")
    page.write_text(raw,encoding='utf-8')
    tests=ROOT/'scripts/test-grade2-browser.mjs'
    raw=tests.read_text(encoding='utf-8')
    if 'const brokenNumbers=' not in raw:
        anchor="          const ids=await page.locator('[id]').evaluateAll(items=>items.map(item=>item.id));"
        addition='''          const brokenNumbers=await page.locator('.lesson-body td[align="right"]').evaluateAll(cells=>cells.flatMap(cell=>{
            const text=(cell.textContent??'').trim();
            if(!/^[+\\-−]?[0-9]+(?:\\.[0-9]+)?(?:e[+\\-]?[0-9]+)?%?$/i.test(text))return [];
            const range=document.createRange();range.selectNodeContents(cell);
            const lines=new Set(Array.from(range.getClientRects()).map(rect=>Math.round(rect.top)));
            return lines.size>1?[text]:[];
          }));
          assert.deepEqual(brokenNumbers,[],`${name} ${lesson.id}: number split across lines`);assertions++;
'''
        if anchor not in raw:raise ValueError('Browser test insertion point changed')
        raw=raw.replace(anchor,addition+anchor)
        raw=raw.replace("['G03','G18','G23','G33','G39']","['G03','G18','G23','G25','G26','G33','G35','G38','G39','G40']")
    # A fragment-only navigation returns null, not an HTTP Response. Fetch the
    # document separately so every target still has both HTTP and DOM checks.
    raw=change(raw,
        "        const response=await page.goto(target,{waitUntil:'domcontentloaded'});assert.equal(response.status(),200);assertions++;",
        "        const documentUrl=new URL(target);documentUrl.hash='';\n"
        "        const http=await page.request.get(documentUrl.href);assert.equal(http.status(),200);assertions++;\n"
        "        await page.goto(target,{waitUntil:'domcontentloaded'});\n"
        "        assert.equal(new URL(page.url()).pathname,documentUrl.pathname);assertions++;")
    tests.write_text(raw,encoding='utf-8')
    numeric=ROOT/'scripts/check-grade2-complete-math.py'
    raw=numeric.read_text(encoding='utf-8')
    if 'sample-size boundary with a below-alpha power target' not in raw:
        anchor="    check('G27','same statistic different reference distributions'"
        insertion="""    check('G26','n=24 falls short while n=25 meets 80-percent power',
          [float(stats.norm.sf(stats.norm.ppf(.95)-.5*math.sqrt(24))<.8),
           float(stats.norm.sf(stats.norm.ppf(.95)-.5*math.sqrt(25))>=.8)],[1,1])
    low_target=.01; a=.05; delta=.1; sigma=10
    bound=max(0.,stats.norm.ppf(1-a)+stats.norm.ppf(low_target))*sigma/delta
    n_required=max(1,math.ceil(bound**2))
    check('G26','sample-size boundary with a below-alpha power target',
          [n_required,float(stats.norm.sf(stats.norm.ppf(1-a)-delta*math.sqrt(n_required)/sigma)>=low_target)],[1,1])
    if '1−β>α' not in SOURCES['G26']['text']:
        raise ValueError('The reviewed positivity condition must remain in the manuscript')
"""
        if anchor not in raw:raise ValueError('Numerical test insertion point changed')
        raw=raw.replace(anchor,insertion+anchor)
    numeric.write_text(raw,encoding='utf-8')
    print('Review copies polished: power-domain condition, numeric table legibility, regression checks added.')

if __name__=='__main__':main()
