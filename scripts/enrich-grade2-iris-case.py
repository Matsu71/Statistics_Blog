"""Generate the real-data case from the imported bytes; fail closed on missing evidence."""
from __future__ import annotations
import csv
import hashlib
import json
import math
import platform
import re
import statistics
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'public/data/grade2-iris.csv'
LESSON = ROOT / 'src/content/grade2/reproducible-case-study.md'
PROVENANCE = ROOT / 'public/data/grade2-iris-provenance.json'
REPORT = ROOT / 'project-docs/grade2/iris-analysis.json'


def all_strings(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from all_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from all_strings(item)
    elif isinstance(value, str):
        yield value


def close(actual, expected, label):
    if not math.isclose(float(actual), float(expected), rel_tol=1e-10, abs_tol=1e-12):
        raise ValueError(f'{label}: {actual!r} != {expected!r}')


def replace_block(text, marker, replacement):
    pattern = rf'<!-- {re.escape(marker)}_START -->[\s\S]*?<!-- {re.escape(marker)}_END -->'
    result, count = re.subn(pattern, lambda _: f'<!-- {marker}_START -->\n{replacement}\n<!-- {marker}_END -->', text)
    if count != 1:
        raise ValueError(f'Expected exactly one {marker} block, got {count}')
    return result


def main():
    raw = DATA.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    candidates = [PROVENANCE] + sorted(DATA.parent.glob('grade2*iris*.json'))
    metadata = None
    metadata_path = None
    for candidate in dict.fromkeys(candidates):
        if not candidate.is_file():
            continue
        item = json.loads(candidate.read_text(encoding='utf-8'))
        if digest in set(all_strings(item)):
            metadata = item
            metadata_path = candidate
            break
    if not isinstance(metadata, dict):
        raise ValueError('Import provenance matching the exact CSV SHA-256 is required')
    with DATA.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        required = ['sepal_length_cm', 'sepal_width_cm', 'petal_length_cm', 'petal_width_cm', 'species']
        if not reader.fieldnames or not set(required) <= set(reader.fieldnames):
            raise ValueError('Unexpected CSV column names; do not silently relabel data')
        rows = list(reader)
    if len(rows) != 150:
        raise ValueError(f'Expected 150 imported observations, got {len(rows)}')
    groups = {name: [] for name in ['setosa', 'versicolor', 'virginica']}
    numeric_rows = []
    for row in rows:
        species = row['species'].strip().lower().removeprefix('iris-')
        if species not in groups:
            raise ValueError(f'Unknown species {species!r}')
        values = [float(row[key]) for key in required[:4]]
        if not all(math.isfinite(value) and value > 0 for value in values):
            raise ValueError('Missing, non-finite, or non-positive measurement')
        groups[species].append(values[2])
        numeric_rows.append(tuple(values + [species]))
    if any(len(values) != 50 for values in groups.values()):
        raise ValueError('Expected 50 preserved observations in each named group')

    summaries = {}
    checks = []
    for name, values in groups.items():
        mean, variance = statistics.mean(values), statistics.variance(values)
        close(mean, np.mean(values), f'{name} mean')
        close(variance, np.var(values, ddof=1), f'{name} variance')
        summaries[name] = {'n': len(values), 'mean': mean, 'variance_ddof1': variance,
                           'sd_ddof1': math.sqrt(variance), 'se_mean': math.sqrt(variance / len(values)),
                           'minimum': min(values), 'maximum': max(values)}
        checks.extend([f'{name}: mean statistics vs NumPy', f'{name}: variance statistics vs NumPy'])

    first, second = groups['versicolor'], groups['setosa']
    a, b = statistics.variance(first) / len(first), statistics.variance(second) / len(second)
    difference = statistics.mean(first) - statistics.mean(second)
    se = math.sqrt(a + b)
    df = (a + b) ** 2 / (a * a / (len(first) - 1) + b * b / (len(second) - 1))
    t_value = difference / se
    p_value = float(2 * stats.t.sf(abs(t_value), df))
    critical = float(stats.t.ppf(0.975, df))
    interval = [difference - critical * se, difference + critical * se]
    oracle = stats.ttest_ind(first, second, equal_var=False, alternative='two-sided')
    close(t_value, oracle.statistic, 'Welch statistic')
    close(df, oracle.df, 'Welch degrees of freedom')
    close(p_value, oracle.pvalue, 'Welch p value')
    oracle_ci = oracle.confidence_interval(confidence_level=0.95)
    close(interval[0], oracle_ci.low, 'Welch interval lower')
    close(interval[1], oracle_ci.high, 'Welch interval upper')
    checks.extend(['Welch statistic', 'Welch df', 'Welch p', 'Welch CI lower', 'Welch CI upper'])

    all_values = [value for values in groups.values() for value in values]
    grand = statistics.mean(all_values)
    between = sum(len(values) * (statistics.mean(values) - grand) ** 2 for values in groups.values())
    within = sum(sum((x - statistics.mean(values)) ** 2 for x in values) for values in groups.values())
    total = sum((x - grand) ** 2 for x in all_values)
    close(total, between + within, 'ANOVA partition')
    f_value = (between / 2) / (within / 147)
    f_oracle = stats.f_oneway(*groups.values())
    close(f_value, f_oracle.statistic, 'ANOVA F')
    close(stats.f.sf(f_value, 2, 147), f_oracle.pvalue, 'ANOVA p')
    checks.extend(['ANOVA partition', 'ANOVA F', 'ANOVA p'])

    text = LESSON.read_text(encoding='utf-8')
    table = '|分類|件数n|平均（cm）|標本標準偏差（cm）|最小〜最大（cm）|\n|---|---:|---:|---:|---|\n'
    for name, summary in summaries.items():
        table += f"|{name}|{summary['n']}|{summary['mean']:.6f}|{summary['sd_ddof1']:.6f}|{summary['minimum']:g}〜{summary['maximum']:g}|\n"
    text = replace_block(text, 'IRIS_SUMMARY', table + '\n標準偏差の分散の分母はn−1です。表示は小数6桁に丸め、計算は丸め前の値を用いています。')
    comparison = ('|項目|CSVからの計算値|\n|---|---:|\n'
                  f'|平均差：versicolor−setosa（cm）|{difference:.6f}|\n'
                  f'|推定標準誤差（cm）|{se:.8f}|\n'
                  f'|Welch近似自由度|{df:.6f}|\n'
                  f'|t統計量|{t_value:.6f}|\n'
                  f'|両側p値|{p_value:.8e}|\n'
                  f'|95%信頼区間（cm）|{interval[0]:.6f}〜{interval[1]:.6f}|\n')
    text = replace_block(text, 'IRIS_WELCH', comparison)
    conclusion = (f'この版のIrisデータのsetosaとversicolor各50行について、花弁長を比較しました。'
                  f'差をversicolor−setosaとした平均差は{difference:.6f} cmでした。'
                  f'独立二群のWelch法による95%区間は{interval[0]:.6f}〜{interval[1]:.6f} cm、'
                  f'両側p値は{p_value:.8e}です。これは記載した標本と作業上のモデルに基づく結果で、'
                  '現在の全地域への代表性や介入の因果効果を保証するものではありません。')
    text = replace_block(text, 'IRIS_REPORT', conclusion)
    s = summaries['setosa']
    text = replace_block(text, 'IRIS_Q1', f"平均{s['mean']:.6f} cm、標本標準偏差{s['sd_ddof1']:.6f} cmです。平均の推定標準誤差は標準偏差を√50で割り、{s['se_mean']:.8f} cmとなります。元の計測値の散らばりと、平均の推定精度を区別します。")
    text = replace_block(text, 'IRIS_Q2', f"平均差{difference:.6f} cm、95%区間{interval[0]:.6f}〜{interval[1]:.6f} cmです。差の順序を逆にすると点推定は−{difference:.6f} cm、区間は−{interval[1]:.6f}〜−{interval[0]:.6f} cmです。同じ両側検定のp値は変わりません。")
    if re.search(r'検算後に生成|生成して公開します|後に表示します|報告例を、同じCSVから生成', text):
        raise ValueError('An unresolved case placeholder remains')
    text, replaced = re.subn(r'^status: (?:draft|published)$', 'status: published', text, count=1, flags=re.M)
    if replaced != 1:
        raise ValueError('Missing lesson publication state')
    if len(re.findall(r'data-question="G39-Q[1-4]"', text)) != 4:
        raise ValueError('The four original case questions must remain intact')

    metadata = dict(metadata)
    metadata['teaching_case_csv_sha256'] = digest
    metadata['teaching_case_measurement'] = 'petal_length_cm'
    metadata['preserved_observations'] = 150
    metadata['identical_numeric_rows_extra_occurrences'] = len(numeric_rows) - len(set(numeric_rows))
    metadata['identical_rows_policy'] = 'Preserve the published rows; equal measurements do not alone establish duplicate subjects.'
    PROVENANCE.parent.mkdir(parents=True, exist_ok=True)
    PROVENANCE.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    LESSON.write_text(text, encoding='utf-8')
    report = {
        'status': 'passed', 'computed_at': datetime.now(timezone.utc).isoformat(),
        'csv_sha256': digest, 'import_provenance_file': str(metadata_path.relative_to(ROOT)),
        'row_count': len(rows), 'summaries': summaries,
        'welch': {'difference_definition': 'versicolor - setosa', 'difference': difference, 'se': se,
                  'df': df, 't': t_value, 'p_two_sided': p_value, 'ci95': interval},
        'anova_computation_crosscheck_only': {'ss_between': between, 'ss_within': within,
                  'ss_total': total, 'df': [2, 147], 'f': f_value, 'p': float(f_oracle.pvalue)},
        'checks': checks, 'check_count': len(checks),
        'environment': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
        'lesson_sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
        'limitations': ['Not a newly collected random sample or randomized experiment.',
                       'Numerical agreement does not verify normality, equal variance, independence, representativeness, or causality.',
                       'No independent human mathematical peer review is claimed.'],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
