#!/usr/bin/env python3
"""Check generated pages, local links, assets and content without network access."""

import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ROUTES = ['home', 'research', 'papers', 'personal', 'contacts', 'researchmore']


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.links = []
        self.assets = []
        self.ids = []
        self.h1 = 0
        self.publications = []
        self.errors = []
        self.feed(path.read_text())

    def handle_starttag(self, tag, pairs):
        attrs = dict(pairs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'h1':
            self.h1 += 1
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
        if tag in ['img', 'script', 'iframe', 'source'] and attrs.get('src'):
            self.assets.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') in ['stylesheet', 'icon']:
            self.assets.append(attrs['href'])
        if tag == 'img' and not all(key in attrs for key in ['alt', 'width', 'height']):
            self.errors.append('Image missing alt text or dimensions')
        if tag == 'article' and 'publication' in attrs.get('class', '').split():
            self.publications.append(attrs.get('id'))
        for key in attrs:
            if key.startswith('on'):
                self.errors.append('Inline event handler: ' + key)


def main():
    pages = [Page(ROOT / 'index.html')] + [Page(ROOT / route / 'index.html') for route in ROUTES]
    lookup = {p.path.resolve(): p for p in pages}
    errors = []
    for page in pages:
        errors += [str(page.path.relative_to(ROOT)) + ': ' + message for message in page.errors]
        if page.h1 != 1:
            errors.append(str(page.path) + ': expected one h1')
        if len(page.ids) != len(set(page.ids)):
            errors.append(str(page.path) + ': duplicate IDs')
        for url in page.assets + page.links:
            parsed = urlsplit(url)
            if parsed.scheme in ['https', 'http', 'mailto', 'tel']:
                if url in page.assets:
                    errors.append('Remote runtime asset: ' + url)
                continue
            if parsed.scheme or parsed.netloc or not url:
                errors.append('Invalid or unsupported local URL: ' + url)
                continue
            destination = (page.path.parent / unquote(parsed.path)).resolve() if parsed.path else page.path.resolve()
            if destination.is_dir():
                destination /= 'index.html'
            if not destination.exists():
                errors.append(str(page.path.relative_to(ROOT)) + ': missing ' + url)
            if parsed.fragment and destination in lookup and unquote(parsed.fragment) not in lookup[destination].ids:
                errors.append(str(page.path.relative_to(ROOT)) + ': missing fragment ' + url)
    css = ROOT / 'assets/css/site.css'
    for url in re.findall(r'url\([\'"]?([^\)\'\"]+)', css.read_text()):
        if not (css.parent / url).is_file():
            errors.append('Missing CSS asset: ' + url)
    data = json.loads((ROOT / 'content/site.json').read_text())
    expected = [entry['id'] for entry in data['pages']['papers']['entries']]
    if lookup[(ROOT / 'papers/index.html').resolve()].publications != expected:
        errors.append('Publication count/order does not match the content source')
    for entry in data['pages']['papers']['entries']:
        if not re.fullmatch(r'(19|20)\d{2}', entry['year']):
            errors.append('Missing/invalid publication year: ' + entry['id'])
    for asset in json.loads((ROOT / 'migration/assets.json').read_text()):
        path = ROOT / asset['src']
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != asset['sha256']:
            errors.append('Original asset is missing or changed: ' + asset['src'])
    text = (ROOT / 'papers/index.html').read_text()
    if 'Cell Reports (Accepted)' in text or '10.1016/j.celrep.2026.117905' not in text:
        errors.append('Inferential planning is not using the final publication record')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'PASS: {len(pages)} HTML files, {len(expected)} bibliographic entries, local assets, links, fragments and original-image hashes.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
