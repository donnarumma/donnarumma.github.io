#!/usr/bin/env python3
"""Check Papers against the canonical BibTeX using Biber's structured export."""

import json
import re
import subprocess
import sys
import tempfile
import unicodedata
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from build import ROOT, plain

NS = {'b': 'http://biblatex-biber.sourceforge.net/biblatexml'}


class Titles(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.depth = 0
        self.parts = []
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == 'em':
            self.depth += 1
        if tag == 'a':
            self.links.append(dict(attrs).get('href', ''))

    def handle_endtag(self, tag):
        if tag == 'em':
            self.depth -= 1

    def handle_data(self, value):
        if self.depth:
            self.parts.append(value)


def normalized(value):
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode().lower()
    return re.sub('[^a-z0-9]', '', value)


def main():
    public_bib = ROOT / 'assets/downloads/donnarumma.bib'
    canonical_bib = ROOT.parent / 'donnarumma.bib'
    source = canonical_bib if canonical_bib.exists() else public_bib
    errors = []
    if source.read_bytes() != public_bib.read_bytes():
        errors.append('The public BibTeX snapshot differs from the canonical CV bibliography; run tools/sync_cv.py.')
    canonical_pdf = ROOT.parent / 'DONNARUMMA_CV.pdf'
    public_pdf = ROOT / 'assets/downloads/francesco-donnarumma-cv.pdf'
    if canonical_pdf.exists() and canonical_pdf.read_bytes() != public_pdf.read_bytes():
        errors.append('The downloadable CV PDF differs from the canonical compiled CV; run tools/sync_cv.py.')
    with tempfile.TemporaryDirectory(prefix='cv-publication-check-') as directory:
        xml = Path(directory) / 'bibliography.xml'
        subprocess.run(['biber', '--tool', '--quiet', '--nolog', '--no-bltxml-schema',
                        '--output-format=biblatexml', '--output-file=' + str(xml), str(source)], check=True)
        bibliography = {e.attrib['id']: e for e in ET.parse(xml).getroot()}
    entries = json.loads((ROOT / 'content/site.json').read_text())['pages']['papers']['entries']
    keys = [e.get('bibkey') for e in entries]
    if None in keys or len(set(keys)) != len(keys):
        errors.append('Each Papers entry must have one unique bibkey.')
    if set(keys) != set(bibliography):
        errors.append('BibTeX-only entries: ' + ', '.join(sorted(set(bibliography) - set(keys))))
        errors.append('Papers-only entries: ' + ', '.join(sorted(str(k) for k in set(keys) - set(bibliography))))
    years = [e['year'] for e in entries]
    if years != sorted(years, reverse=True):
        errors.append('Papers entries are not ordered by descending publication year.')
    for entry in entries:
        record = bibliography.get(entry.get('bibkey'))
        if record is None:
            continue
        if entry['year'] != record.findtext('b:date', '', NS)[:4]:
            errors.append(entry['id'] + ': publication year differs from the CV.')
        title_html = Titles(' '.join(entry['paragraphs']))
        site_title = normalized(' '.join(title_html.parts) or plain(entry['paragraphs'][1]))
        bib_title = normalized(record.findtext('b:title', '', NS))
        if not site_title or not (bib_title.startswith(site_title) or site_title.startswith(bib_title)):
            errors.append(entry['id'] + ': title differs from the CV.')
        doi = record.findtext('b:doi', '', NS)
        if doi and not any(urlsplit(url).hostname in ('doi.org', 'dx.doi.org')
                           and unquote(urlsplit(url).path).lstrip('/').lower() == doi.lower()
                           for url in title_html.links):
            errors.append(entry['id'] + ': title does not link to the canonical DOI.')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'PASS: {len(entries)} Papers entries match the CV bibliography, titles, years and DOI links; PDF and BibTeX snapshots are identical.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
