"""Import the documented UCI Iris file; never synthesize missing observations."""
from __future__ import annotations
import csv, hashlib, io, json, time, urllib.request, zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, variance

URL = 'https://archive.ics.uci.edu/static/public/53/iris.zip'
SOURCE = 'https://archive.ics.uci.edu/dataset/53/iris'
DEST = Path('public/data/grade2-iris.csv')
META = Path('public/data/grade2-iris-provenance.json')


def main():
    if DEST.exists() and META.exists():
        meta = json.loads(META.read_text())
        assert hashlib.sha256(DEST.read_bytes()).hexdigest() == meta['csv_sha256'], 'Pinned dataset changed'
        print('Using committed UCI dataset with verified fingerprint.')
        return
    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(URL, headers={'User-Agent': 'Statistics-Lab-Educational-Import/1.0'}), timeout=40) as response:
                raw = response.read(200000)
                assert response.status == 200
            assert len(raw) < 200000
            break
        except Exception as error:
            last_error = error
            if attempt == 2:
                raise RuntimeError('UCI source could not be retrieved; no fallback data will be invented') from last_error
            time.sleep(2 ** attempt)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        matches = [name for name in archive.namelist() if name.split('/')[-1] == 'bezdekIris.data']
        assert len(matches) == 1, 'Expected the specifically selected UCI data file'
        source_bytes = archive.read(matches[0])
    rows = [row for row in csv.reader(io.StringIO(source_bytes.decode('ascii'))) if row]
    assert len(rows) == 150 and all(len(row) == 5 for row in rows)
    counts = Counter(row[4] for row in rows)
    assert counts == {'Iris-setosa': 50, 'Iris-versicolor': 50, 'Iris-virginica': 50}
    for row in rows:
        assert all(0 < float(value) < 10 for value in row[:4])
    output = io.StringIO(newline='')
    writer = csv.writer(output, lineterminator='\n')
    writer.writerow(['sepal_length_cm', 'sepal_width_cm', 'petal_length_cm', 'petal_width_cm', 'species'])
    writer.writerows(rows)
    data = output.getvalue().encode('utf-8')
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_bytes(data)
    meta = {
        'dataset': 'Iris', 'creator': 'R. A. Fisher', 'year': 1936,
        'repository': 'UCI Machine Learning Repository', 'doi': '10.24432/C56C76',
        'source_page': SOURCE, 'download_url': URL, 'source_file': 'bezdekIris.data',
        'license': 'CC BY 4.0', 'license_url': 'https://creativecommons.org/licenses/by/4.0/',
        'license_checked_date': '2026-09-11', 'retrieved_at': datetime.now(timezone.utc).isoformat(),
        'archive_sha256': hashlib.sha256(raw).hexdigest(),
        'source_file_sha256': hashlib.sha256(source_bytes).hexdigest(),
        'csv_sha256': hashlib.sha256(data).hexdigest(),
        'rows': len(rows), 'class_counts': dict(counts),
        'modifications': ['Added descriptive CSV header with measurement units; excluded blank trailing lines; retained numeric strings and row order from bezdekIris.data.'],
        'version_note': 'UCI distributes iris.data and bezdekIris.data; its description notes differences from the Fisher article. This course pins bezdekIris.data and does not silently combine versions.',
        'limits': ['A historical observational dataset, not a randomized treatment experiment or a newly collected representative sample.']
    }
    META.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    result = {}
    for species in counts:
        values = [float(row[2]) for row in rows if row[4] == species]
        result[species] = {'n': len(values), 'petal_length_mean': mean(values), 'petal_length_variance_n_minus_1': variance(values)}
    print(json.dumps({'provenance': meta, 'descriptive_summary': result}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
