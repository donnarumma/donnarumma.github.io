#!/usr/bin/env python3
"""One-time, explicit import of the author's public Google Site.

Requires beautifulsoup4 and Pillow. Normal offline builds do not use this tool.
Never run against edited content without making a Git commit or backup first.
"""

import argparse
import hashlib
import html
import io
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['home', 'research', 'papers', 'personal', 'contacts', 'researchmore']
BASE = 'https://www.francescodonnarumma.net'


def fetch(url):
    cache = ROOT / '.local/cache' / hashlib.sha256(url.encode()).hexdigest()
    if cache.exists():
        return cache.read_bytes()
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(request, timeout=35) as response:
                return response.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1)


def clean_url(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.hostname in ('www.google.com', 'google.com') and parsed.path == '/url':
        url = urllib.parse.parse_qs(parsed.query).get('q', [url])[0]
    if url.startswith(BASE):
        url = url[len(BASE):] or '/home'
    return url


def inline(node):
    if isinstance(node, NavigableString):
        return html.escape(str(node).replace('\xa0', ' '))
    if node.name in ('script', 'style', 'iframe'):
        return ''
    if node.name == 'br':
        return '<br>'
    inside = ''.join(inline(child) for child in node.children)
    if node.name == 'a':
        href = clean_url(node.get('href', ''))
        if href.startswith(('https://', 'http://', '/', '#', 'mailto:')):
            return '<a href="' + html.escape(href, quote=True) + '">' + inside + '</a>'
    style = node.get('style', '')
    if node.name in ('strong', 'b') or 'font-weight: 700' in style:
        inside = '<strong>' + inside + '</strong>'
    if node.name in ('em', 'i') or 'font-style: italic' in style:
        inside = '<em>' + inside + '</em>'
    if node.name in ('sub', 'sup'):
        inside = '<' + node.name + '>' + inside + '</' + node.name + '>'
    return inside


def paragraphs(section):
    result = []
    for node in section.select('p, h2, h3, li'):
        if node.find_parent(['p', 'li']):
            continue
        value = re.sub(r'\s+', ' ', inline(node)).strip()
        if BeautifulSoup(value, 'html.parser').get_text(strip=True):
            result.append(value)
    return result


class Assets:
    def __init__(self):
        self.records = []
        self.by_url = {}
        self.by_hash = {}

    def image(self, url, name, alt=''):
        if url in self.by_url:
            return dict(self.by_url[url], alt=alt or name.replace('-', ' '))
        data = fetch(url)
        digest = hashlib.sha256(data).hexdigest()
        picture = Image.open(io.BytesIO(data))
        extension = {'JPEG': 'jpg', 'PNG': 'png', 'GIF': 'gif', 'WEBP': 'webp'}[picture.format]
        path = self.by_hash.get(digest)
        if not path:
            path = 'assets/images/' + name + '.' + extension
            (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
            (ROOT / path).write_bytes(data)
            self.by_hash[digest] = path
        record = {'src': path, 'alt': alt or name.replace('-', ' '),
                  'width': picture.width, 'height': picture.height}
        self.records.append(dict(record, source=url, sha256=digest, bytes=len(data),
                                 frames=getattr(picture, 'n_frames', 1)))
        self.by_url[url] = record
        print('Image:', path, picture.size, flush=True)
        return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, help='Directory containing PAGE.html snapshots')
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    destination = ROOT / 'content/site.json'
    if destination.exists() and not args.overwrite:
        parser.error('content/site.json exists; the import is not an update command')
    soups = {}
    archive = ROOT / '.local/source'
    archive.mkdir(parents=True, exist_ok=True)
    for page in PAGES:
        data = (args.source_dir / ('francesco-site-' + page + '.html')).read_bytes() if args.source_dir else fetch(BASE + '/' + page)
        (archive / (page + '.html')).write_bytes(data)
        soups[page] = BeautifulSoup(data, 'html.parser')
    assets = Assets()
    home = soups['home'].select('section.yaqOZd')
    background_url = lambda section: re.search(r'url\(([^)]+)\)', section.select_one('.IFuOkc').get('style', '')).group(1)
    data = {
        'name': 'Francesco Donnarumma',
        'description': 'Researcher at ISTC-CNR. Computational models of cognition, active inference, social interaction and planning.',
        'imported_on': '2026-09-14',
        'source': BASE + '/',
        'background': assets.image(background_url(home[0]), 'angel-background'),
        'banner': assets.image(background_url(home[1]), 'shoreline-banner'),
        'logo': assets.image(soups['home'].select_one('header img')['src'], 'site-logo'),
        'profiles': [],
        'pages': {},
    }
    labels = ['ISTC-CNR', 'Scopus', 'Google Scholar', 'Web of Science', 'ORCID',
              'DBLP', 'ResearchGate', 'Academia.edu', 'Mastodon', 'X / Twitter',
              'Facebook', 'LinkedIn']
    for label, anchor in zip(labels, home[0].select('a:has(img)')):
        name = re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')
        data['profiles'].append({'label': label, 'url': clean_url(anchor['href']),
                                 'image': assets.image(anchor.img['src'], 'profile-' + name, label)})
    data['brain'] = assets.image(home[0].select('img')[-1]['src'], 'brain-animation', 'Animated brain')
    letters = []
    for section, word in zip(home[1:3], ['FRANCESCO', 'DONNARUMMA']):
        letters.append([assets.image(i['src'], 'letter-' + char.lower() + '-' + str(n), char)
                        for n, (char, i) in enumerate(zip(word, section.select('img')))])
    video_titles = {'kU0Ls9hQt3M': 'Incremental Clustering', '8uWHWMVYt54': 'Rat sub-goals',
                    'z0DkRyb_NRU': 'StageX4', 'yloebx_MLfI': 'Goal Recognition'}
    videos = []
    for frame in soups['home'].select('iframe[src*="youtube.com/embed/"]'):
        video_id = urllib.parse.urlsplit(frame['src']).path.split('/')[-1]
        title = video_titles[video_id]
        videos.append({'id': video_id, 'title': title,
                       'poster': assets.image('https://i.ytimg.com/vi/' + video_id + '/hqdefault.jpg', 'video-' + video_id, title)})
    data['pages']['home'] = {
        'letters': letters,
        'angel': assets.image(home[3].select_one('img')['src'], 'angel', 'Angel'),
        'videos': sorted(videos, key=lambda video: list(video_titles).index(video['id'])),
        'highlights': paragraphs(home[5]),
    }
    for page in ['research', 'researchmore', 'personal']:
        sections = []
        for index, section in enumerate(soups[page].select('section.yaqOZd')[3:], start=3):
            images = [assets.image(i['src'], page + '-' + str(index) + '-' + str(n),
                                   'Francesco Donnarumma' if page == 'research' else 'Citation map')
                      for n, i in enumerate(section.select('img'))]
            text = paragraphs(section)
            if text or images:
                sections.append({'paragraphs': text, 'images': images})
        data['pages'][page] = {'sections': sections}
    papers = []
    for index, section in enumerate(soups['papers'].select('section.yaqOZd')[3:], start=1):
        blocks = paragraphs(section)
        if not blocks:
            continue
        text = BeautifulSoup(' '.join(blocks), 'html.parser').get_text(' ', strip=True)
        dates = []
        for block in reversed(blocks):
            dates = re.findall(r'\b(?:19|20)\d{2}\b', BeautifulSoup(block, 'html.parser').get_text())
            if dates:
                break
        papers.append({'id': 'paper-' + str(index).zfill(2), 'year': dates[-1] if dates else '', 'paragraphs': blocks})
    data['pages']['papers'] = {'entries': papers}
    data['pages']['contacts'] = {'email': 'francesco.donnarumma@istc.cnr.it'}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(data, indent=2, ensure_ascii=True) + '\n')
    manifest = ROOT / 'migration/assets.json'
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(assets.records, indent=2, ensure_ascii=True) + '\n')
    print('Imported', len(papers), 'bibliographic entries and', len(assets.by_hash), 'distinct assets.')


if __name__ == '__main__':
    main()
