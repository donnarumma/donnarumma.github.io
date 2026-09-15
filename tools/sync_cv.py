#!/usr/bin/env python3
"""Explicitly refresh the public CV and BibTeX snapshots from CurriculumVitae."""

import argparse
import hashlib
import json
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=ROOT.parent)
    args = parser.parse_args()
    pairs = [('DONNARUMMA_CV.pdf', 'francesco-donnarumma-cv.pdf'), ('donnarumma.bib', 'donnarumma.bib')]
    if not all((args.source / name).is_file() for name, _ in pairs):
        parser.error('Expected DONNARUMMA_CV.pdf and donnarumma.bib in the source directory')
    records = []
    for name, target in pairs:
        source = args.source / name
        destination = ROOT / 'assets/downloads' / target
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        records.append({'source': name, 'destination': str(destination.relative_to(ROOT)),
                        'sha256': hashlib.sha256(destination.read_bytes()).hexdigest()})
        print(f'Updated {destination.relative_to(ROOT)}')
    (ROOT / 'migration/cv-snapshot.json').write_text(json.dumps({'copied_on': date.today().isoformat(), 'files': records}, indent=2) + '\n')
    print('The Papers page is intentionally unchanged. Review content/site.json separately.')


if __name__ == '__main__':
    main()
