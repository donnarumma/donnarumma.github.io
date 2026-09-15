#!/usr/bin/env python3
"""Build the static website without network access or third-party packages."""

import argparse
import html
import json
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from string import Template
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
LABELS = {'home': 'Home', 'research': 'Research', 'papers': 'Papers',
          'personal': 'Personal', 'contacts': 'Contacts', 'researchmore': 'Research Me'}
NAVIGATION = ['home', 'research', 'papers', 'personal', 'contacts']


def escape(value):
    return html.escape(str(value), quote=True)


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, value):
        self.parts.append(value)

    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.parts.append(' ')


class Emphasis(HTMLParser):
    def __init__(self, value):
        super().__init__()
        self.depth = 0
        self.parts = []
        self.feed(value)

    def handle_starttag(self, tag, attrs):
        if tag == 'em':
            self.depth += 1

    def handle_endtag(self, tag):
        if tag == 'em':
            self.depth -= 1

    def handle_data(self, value):
        if self.depth:
            self.parts.append(value)


def plain(value):
    parser = PlainText()
    parser.feed(value)
    return ' '.join(''.join(parser.parts).split())


def image(record, prefix, css='', eager=False):
    return (f'<img src="{prefix}{escape(record["src"])}" alt="{escape(record["alt"])}" '
            f'width="{record["width"]}" height="{record["height"]}" class="{css}" '
            f'loading="{"eager" if eager else "lazy"}" decoding="async">')


def link(url, label, css='', external=False):
    extra = ' target="_blank" rel="noopener noreferrer"' if external else ''
    return f'<a href="{escape(url)}" class="{css}"{extra}>{label}</a>'


class LocalHTML(HTMLParser):
    def __init__(self, value, prefix):
        super().__init__()
        self.prefix = prefix
        self.parts = []
        self.anchor_depth = 0
        self.feed(value)

    def rewrite_url(self, url):
        prefix = self.prefix
        repairs = {
            '#BAD_URL': 'https://doi.org/10.1080/09540091.2012.684670',
            'http://dx.doi.org/doi:10.1177/1059712313488789': 'https://doi.org/10.1177/1059712313488789',
            'http://donnarumma10differential.bib': prefix + 'assets/downloads/donnarumma.bib',
        }
        url = repairs.get(url, url)
        if url.startswith('/') and not url.startswith('//'):
            parsed = urlsplit(url)
            route = parsed.path.strip('/') or 'home'
            if route in LABELS:
                url = prefix + route + '/index.html'
                if parsed.fragment:
                    url += '#' + parsed.fragment
        elif url.startswith('assets/'):
            url = prefix + url
        return url

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.anchor_depth += 1
            attrs = [(key, self.rewrite_url(value) if key == 'href' else value) for key, value in attrs]
        attributes = ''.join(' ' + key + (f'="{escape(value)}"' if value is not None else '') for key, value in attrs)
        self.parts.append('<' + tag + attributes + '>')

    def handle_endtag(self, tag):
        if tag == 'a':
            self.anchor_depth -= 1
        self.parts.append('</' + tag + '>')

    def handle_data(self, value):
        if not self.anchor_depth:
            value = re.sub(r'\[(?:pdf|bib)\]', '', value)
        self.parts.append(html.escape(value))


def localize(value, prefix):
    return ''.join(LocalHTML(value, prefix).parts)


def text_blocks(blocks, prefix):
    return '\n'.join('<p>' + localize(block, prefix) + '</p>' for block in blocks)


def page_heading(page, prefix, settings):
    links = {
        'research': [('papers/index.html', 'Papers'), ('researchmore/index.html', 'More')],
        'papers': [(settings['cv'], 'Curriculum Vitae'), (settings['bibtex'], 'Papers Bibtex'), ('researchmore/index.html', 'More')],
        'personal': [('research/index.html', 'Research'), ('researchmore/index.html', 'More')],
        'contacts': [('research/index.html', 'Research'), ('researchmore/index.html', 'More')],
        'researchmore': [('research/index.html', 'Research'), ('papers/index.html', 'Papers')],
    }
    nav = ''.join(link(prefix + path, label) for path, label in links[page])
    return f'<section class="page-banner"><h1>{LABELS[page]}</h1></section><nav class="page-links" aria-label="Related pages">{nav}</nav>'


def profiles(data, settings, prefix):
    items = []
    for profile in data['profiles']:
        if profile['label'] in settings['archived_profiles']:
            continue
        url = settings['profile_updates'].get(profile['label'], profile['url'])
        items.append(f'<a class="profile-link" href="{escape(url)}" title="{escape(profile["label"])}">' + image(profile['image'], prefix, eager=True) + '</a>')
    openalex = next(p for p in settings['additional_profiles'] if p['label'] == 'OpenAlex')
    items.append(f'<a class="profile-link profile-openalex" href="{escape(openalex["url"])}" title="OpenAlex">'
                 + image(openalex['image'], prefix, eager=True) + '</a>')
    items.append(image(data['brain'], prefix, 'brain', eager=True))
    return ''.join(items)


def home_body(data, prefix):
    page = data['pages']['home']
    letters = ''.join('<div class="letter-row">' + ''.join(image(i, prefix, eager=True) for i in row) + '</div>' for row in page['letters'])
    videos = ''
    for video in page['videos']:
        videos += (f'<a class="video" href="https://www.youtube.com/watch?v={escape(video["id"])}" target="_blank" rel="noopener noreferrer" aria-label="{escape(video["title"])} on YouTube">'
                   + image(video['poster'], prefix, eager=True)
                   + '<span class="video-play"><i data-lucide="play" aria-hidden="true"></i></span>'
                   + f'<span class="video-title">{escape(video["title"])}</span></a>')
    highlights = page['highlights']
    if highlights and plain(highlights[0]).lower().startswith('highlights'):
        highlights = highlights[1:]
    return ('<section class="name-banner"><h1 class="sr-only">Francesco Donnarumma</h1><div class="name-letters" aria-hidden="true">' + letters + '</div></section>'
            + '<section class="home-media surface"><div class="content-width media-layout"><figure class="angel">'
            + image(page['angel'], prefix, eager=True) + '</figure><div class="video-grid">' + videos + '</div></div></section>'
            + '<section class="highlights surface"><div class="content-width"><h2>Highlights</h2><ul>'
            + ''.join('<li>' + localize(p, prefix) + '</li>' for p in highlights)
            + '</ul></div></section>')


def papers_body(data, prefix):
    entries = data['pages']['papers']['entries']
    years = sorted({e['year'] for e in entries if e['year']}, reverse=True)
    options = ''.join(f'<option value="{escape(y)}">{escape(y)}</option>' for y in years)
    toolbar = ('<section class="publication-tools surface" hidden><form class="content-width paper-filters" role="search">'
               '<label class="filter-query"><i data-lucide="search" aria-hidden="true"></i><span class="sr-only">Search publications</span><input type="search" id="paper-query" placeholder="Search publications" autocomplete="off"></label>'
               f'<label class="filter-year"><span class="sr-only">Publication year</span><select id="paper-year"><option value="">All years</option>{options}</select></label>'
               '<button type="reset" class="icon-button" title="Reset filters" aria-label="Reset filters"><i data-lucide="rotate-ccw" aria-hidden="true"></i></button>'
               f'<span class="paper-count" role="status">{len(entries)} entries</span></form></section>')
    articles = []
    for entry in entries:
        paragraphs = []
        for index, block in enumerate(entry['paragraphs']):
            if not plain(localize(block, prefix)).strip():
                continue
            css = 'authors' if index == 0 else 'paper-title' if index == 1 else 'paper-detail'
            paragraphs.append(f'<p class="{css}">' + localize(block, prefix) + '</p>')
        articles.append(f'<article class="publication surface" id="{escape(entry["id"])}" data-year="{escape(entry["year"])}"><div class="content-width">' + ''.join(paragraphs) + '</div></article>')
    return toolbar + '<div class="publications">' + ''.join(articles) + '</div><p class="no-papers content-width" hidden>No publications match your search.</p>'


def research_body(data, page, prefix):
    output = []
    for section in data['pages'][page]['sections']:
        pictures = ''.join(image(i, prefix, eager=True) for i in section['images'])
        text = text_blocks(section['paragraphs'], prefix)
        css = 'research-layout' if pictures else 'prose'
        output.append(f'<section class="surface research-section"><div class="content-width {css}">{pictures}<div>{text}</div></div></section>')
    return ''.join(output)


def personal_body(data, settings, prefix):
    output = []
    for section in data['pages']['personal']['sections']:
        images = ''.join(link(prefix + i['src'], image(i, prefix)) for i in section['images'])
        output.append('<section class="surface map-section"><div class="content-width"><figure>' + images + '<figcaption>' + text_blocks(section['paragraphs'], prefix) + '</figcaption></figure></div></section>')
    social = [p for p in settings['additional_profiles'] if p['group'] == 'social']
    social += [p for p in data['profiles'] if p['label'] in ['Mastodon', 'Facebook']]
    output.append('<section class="surface social-section"><div class="content-width"><h2>Elsewhere</h2><ul class="contact-links">' + ''.join('<li>' + link(p['url'], escape(p['label'])) + '</li>' for p in social) + '</ul></div></section>')
    return ''.join(output)


def contacts_body(data, settings, prefix):
    profiles = [dict(p, url=settings['profile_updates'].get(p['label'], p['url'])) for p in data['profiles'] if p['label'] != 'ISTC-CNR'] + settings['additional_profiles']
    active = [p for p in profiles if p['label'] not in settings['archived_profiles']]
    archived = [p for p in profiles if p['label'] in settings['archived_profiles']]
    return ('<section class="surface contacts-section"><div class="content-width"><h2>Francesco Donnarumma</h2>'
            f'<p>{escape(settings["affiliation"])}</p><p>{escape(settings["location"])}</p>'
            + '<p class="email">' + link('mailto:' + settings['email'], escape(settings['email'])) + '</p>'
            + '<h3>Profiles</h3><ul class="contact-links">' + ''.join('<li>' + link(p['url'], escape(p['label'])) + '</li>' for p in active) + '</ul>'
            + '<details class="archived-profiles"><summary>Archived profiles</summary><ul class="contact-links">' + ''.join('<li>' + link(p['url'], escape(p['label'])) + '</li>' for p in archived) + '</ul></details></div></section>')


def make_search_index(data, settings):
    result = []
    for page in NAVIGATION + ['researchmore']:
        content = data['pages'][page]
        if page == 'papers':
            for entry in content['entries']:
                title = entry.get('title') or plain(entry['paragraphs'][1])
                for block in entry['paragraphs']:
                    candidate = ' '.join(''.join(Emphasis(block).parts).split())
                    if candidate:
                        title = candidate
                        break
                result.append({'title': title, 'section': 'Papers', 'url': 'papers/index.html#' + entry['id'], 'text': plain(localize(' '.join(entry['paragraphs']), ''))})
        else:
            text = ' '.join(' '.join(s['paragraphs']) for s in content.get('sections', []))
            if page == 'home':
                text = ' '.join(content['highlights']) + ' ' + data['name']
            if page == 'contacts':
                text = settings['email'] + ' ' + settings['affiliation'] + ' ' + ' '.join(p['label'] for p in data['profiles'] + settings['additional_profiles'])
            result.append({'title': LABELS[page], 'section': LABELS[page], 'url': page + '/index.html', 'text': plain(text)})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT, help='Build directory (defaults to the repository root)')
    args = parser.parse_args()
    output = args.output.resolve()
    if output != ROOT and ROOT not in output.parents:
        parser.error('Use the repository root or one of its subdirectories as output')
    data = json.loads((ROOT / 'content/site.json').read_text())
    settings = json.loads((ROOT / 'content/settings.json').read_text())
    template = Template((ROOT / 'templates/base.html').read_text())
    output.mkdir(parents=True, exist_ok=True)
    if output != ROOT:
        for path in (ROOT / 'assets').rglob('*'):
            if path.is_file():
                destination = output / path.relative_to(ROOT)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, destination)
    required = [settings['cv'], settings['bibtex'], 'assets/vendor/lucide.min.js']
    for path in required:
        if not (output / path).is_file():
            raise SystemExit('Missing required local asset: ' + path)
    for page in LABELS:
        for root_home in ([False, True] if page == 'home' else [False]):
            prefix = '' if root_home else '../'
            body = home_body(data, prefix) if page == 'home' else page_heading(page, prefix, settings)
            if page == 'papers':
                body += papers_body(data, prefix)
            elif page in ['research', 'researchmore']:
                body += research_body(data, page, prefix)
            elif page == 'personal':
                body += personal_body(data, settings, prefix)
            elif page == 'contacts':
                body += contacts_body(data, settings, prefix)
            nav = ''.join(f'<a href="{prefix}{p}/index.html"' + (' aria-current="page"' if p == page else '') + f'>{LABELS[p]}</a>' for p in NAVIGATION)
            title = data['name'] if page == 'home' else LABELS[page] + ' | ' + data['name']
            canonical = settings['public_url'].rstrip('/') + ('/' if page == 'home' else '/' + page + '/')
            page_html = template.substitute(
                title=escape(title), description=escape(data['description']),
                robots='index, follow' if settings['allow_indexing'] else 'noindex, nofollow',
                canonical=escape(canonical), social_image=escape(settings['public_url'].rstrip('/') + '/' + data['pages']['research']['sections'][0]['images'][0]['src']),
                favicon=prefix + data['logo']['src'], background=prefix + data['background']['src'],
                banner=prefix + data['banner']['src'], prefix=prefix, page=page,
                navigation=nav, profiles=profiles(data, settings, prefix), body=body, cv=prefix + settings['cv'])
            destination = output / 'index.html' if root_home else output / page / 'index.html'
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(page_html)
    search_path = output / 'assets/js/search-index.js'
    search_path.parent.mkdir(parents=True, exist_ok=True)
    search_path.write_text('window.SITE_SEARCH = ' + json.dumps(make_search_index(data, settings), ensure_ascii=True) + ';\n')
    (output / '.nojekyll').write_text('')
    (output / 'robots.txt').write_text('User-agent: *\n' + ('Allow: /\n' if settings['allow_indexing'] else 'Disallow: /\n'))
    print(f'Built 6 pages, root home and {len(data["pages"]["papers"]["entries"])} bibliographic entries in {output}')


if __name__ == '__main__':
    main()
