"""Copy manuscripts into a review workspace; bind promotion to actual release gates."""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse, json, os, re, shutil

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'review/grade2/20260911'
REPORT = ROOT / 'project-docs/grade2/review-workspace.json'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def replace_checked(text, old, new):
    if old in text:
        return text.replace(old, new)
    if new in text:
        return text
    raise ValueError(f'Review patch no longer matches its source: {old[:90]}')


def prepare():
    submitted = WORK / 'submitted'
    candidate = WORK / 'candidate'
    submitted.mkdir(parents=True, exist_ok=True)
    candidate.mkdir(parents=True, exist_ok=True)
    source = ROOT / 'src/content/grade2'
    files = sorted(source.glob('*.md'))
    if len(files) != 40:
        raise ValueError('Exactly 40 manuscripts must exist before review')
    for path in files:
        original = submitted / path.name
        if not original.exists():
            shutil.copy2(path, original)
        shutil.copy2(path, candidate / path.name)
    edits = {
        'hypotheses-p-values-and-tails.md': [
            ('帰無仮説H₀:μ=100、対立仮説H₁:μ≠100', r'帰無仮説 $H_0:\mu=100$、対立仮説 $H_1:\mu\ne100$'),
            ('|上側|P(Z≥2)|', r'|上側|$P(Z\ge2)$|'),
            ('|下側|P(Z≤2)|', r'|下側|$P(Z\le2)$|'),
            ('|両側|P(|Z|≥2)|', r'|両側|$P(\lvert Z\rvert\ge2)$|'),
            ('標準正規の両側検定ではp=2{1−Φ(|z|)}です。', r'標準正規の両側検定では $p=2\{1-\Phi(\lvert z\rvert)\}$ です。'),
            ('p≤αはΦ(|z|)≥1−α/2、すなわち|z|≥z_{1−α/2}と同値です。', r'$p\le\alpha$ は $\Phi(\lvert z\rvert)\ge1-\alpha/2$、すなわち $\lvert z\rvert\ge z_{1-\alpha/2}$ と同値です。'),
        ],
        'multiple-regression-and-dummies.md': [
            ('Y=β₀+β₁x+β₂D+ε', r'$Y=\beta_0+\beta_1x+\beta_2D+\varepsilon$'),
            ('正規方程式はXᵀXβ̂=Xᵀyです。', r'正規方程式は $X^{\mathsf T}X\hat{\boldsymbol\beta}=X^{\mathsf T}\mathbf y$ です。'),
            ('β̂=(XᵀX)⁻¹Xᵀyと一意に求まります。', r'$\hat{\boldsymbol\beta}=(X^{\mathsf T}X)^{-1}X^{\mathsf T}\mathbf y$ と一意に求まります。'),
        ],
        'reading-analysis-output.md': [
            ('Y=β₀+β₁x+β₂D+ε', r'$Y=\beta_0+\beta_1x+\beta_2D+\varepsilon$'),
            ('t値は、推定値を標準誤差で割った数値です。', r'帰無値が0のとき、$t=\hat\beta_j/\operatorname{SE}(\hat\beta_j)$ です。t値は、推定値を標準誤差で割った数値です。'),
            ('95%信頼区間はEstimate±t₀.₉₇₅,₅×SEです。', r'95%信頼区間は $\hat\beta_j\pm t_{0.975,5}\operatorname{SE}(\hat\beta_j)$ です。'),
        ],
        'grade2-integrated-practice.md': [
            ('Σx²と(Σx)²は別です。', r'$\sum_i x_i^2$ と $(\sum_i x_i)^2$ は別です。'),
            ('残差平方和はSyy−Sxy²/Sxx=9−36/5=1.8です。', r'残差平方和は $S_{yy}-S_{xy}^2/S_{xx}=9-36/5=1.8$ です。'),
        ],
    }
    for name, changes in edits.items():
        path = candidate / name
        text = path.read_text(encoding='utf-8')
        for old, new in changes:
            if new not in text:
                text = replace_checked(text, old, new)
        path.write_text(text, encoding='utf-8')
    records=[]
    for path in sorted(candidate.glob('*.md')):
        text=path.read_text(encoding='utf-8')
        match=re.search(r'^lesson_id:\s*(G\d{2})$',text,re.M)
        count=len(re.findall(r'data-question="G\d{2}-Q\d+"',text))
        if not match or count != (16 if match[1]=='G40' else 4):
            raise ValueError(f'Missing identity or questions: {path}')
        if not re.search(r'\$[^$]+\$',text):
            raise ValueError(f'Missing meaningful mathematical notation: {path}')
        # src is a disposable staging copy for Astro, not the live main branch.
        shutil.copy2(path, source / path.name)
        records.append({'id':match[1], 'name':path.name,'questions':count,
                        'submitted_sha256':digest(submitted/path.name),'candidate_sha256':digest(path)})
    state_path=ROOT/'src/data/grade2-release.json'
    state=json.loads(state_path.read_text(encoding='utf-8'))
    state.update(authored_through='G40',authored_lessons=40,authored_questions=172,questions=172,
                 review_workspace='review/grade2/20260911/candidate',
                 next='Verify the copied candidate, bind evidence, then publish the verified files only.')
    state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tools=ROOT/'src/components/Grade2Tools.astro'
    raw=tools.read_text(encoding='utf-8')
    raw=replace_checked(raw,r"replace(/</g, '\u003c')",r"replace(/</g, '\\u003c')")
    tools.write_text(raw,encoding='utf-8')
    report={'status':'copied_candidate_ready_for_verification','source_commit':os.getenv('GITHUB_SHA'),
            'created_at':datetime.now(timezone.utc).isoformat(),'lesson_count':40,'question_count':172,
            'records':sorted(records,key=lambda x:x['id']),
            'limits':['A staging copy is not approval to publish.', 'Seal only after actual numerical, reference and browser gates pass.']}
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (WORK.parent/'README.md').write_text('# 2級の検証用コピー\n\n20260911/submitted は修正前の保存コピー、candidate は表示・数式等を修正する検証用原稿です。src/content/grade2 は検証時の表示用コピーであり、mainへ未検証の内容を公開しません。数値・出典・ブラウザの全ゲート成功後だけ verified を作成し、ハッシュで検証記録と結び付けます。\n\n公開済み基礎コースの原稿は変更しません。次の制作段階は2級公開後に準1級です。\n',encoding='utf-8')
    print('40 manuscripts copied for review; mathematical notation and counts repaired. Publication not established.')


def seal():
    report=json.loads(REPORT.read_text(encoding='utf-8'))
    gates=json.loads((ROOT/'project-docs/grade2/release/final-gates.json').read_text(encoding='utf-8'))
    if gates.get('math_status')!='passed' or gates.get('browser_status')!='passed':
        raise ValueError('Actual final gates are required before promotion')
    numeric=json.loads((ROOT/'project-docs/grade2/math-validation.json').read_text(encoding='utf-8'))
    verified=WORK/'verified'; verified.mkdir(parents=True,exist_ok=True)
    for record in report['records']:
        path=ROOT/'src/content/grade2'/record['name']
        if digest(path)!=record['candidate_sha256'] or digest(WORK/'candidate'/record['name'])!=record['candidate_sha256']:
            raise ValueError(f'Candidate changed after snapshot: {record["id"]}')
        if numeric['sources'][record['id']]['sha256']!=digest(path):
            raise ValueError('Numerical evidence does not match the promotion candidate')
        shutil.copy2(path,verified/record['name'])
    report.update(status='verified_candidate_sealed',sealed_at=datetime.now(timezone.utc).isoformat(),
                  final_gates_sha256=digest(ROOT/'project-docs/grade2/release/final-gates.json'))
    REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Verified copies sealed; publication is a separate subsequent operation.')

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('phase',choices=['prepare','seal'])
    {'prepare':prepare,'seal':seal}[parser.parse_args().phase]()
