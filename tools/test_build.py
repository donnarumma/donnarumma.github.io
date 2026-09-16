#!/usr/bin/env python3
"""Focused regression tests for generated link destinations."""

import unittest
import json
from html.parser import HTMLParser

from build import ROOT, home_body, is_external_url, link, localize, make_search_index, plain


class Anchors(HTMLParser):
    def __init__(self, value):
        super().__init__()
        self.anchors = []
        self.feed(value)

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.anchors.append(dict(attrs))


class LinkTests(unittest.TestCase):
    def test_external_urls(self):
        urls = [
            'https://doi.org/10.1016/j.plrev.2026.03.001',
            'http://example.org/paper.pdf',
            '//arxiv.org/abs/2506.14453',
            'https://example.org/?next=www.francescodonnarumma.net',
            'https://www.francescodonnarumma.net.example.org/papers/',
            'https://www.francescodonnarumma.net@example.org/papers/',
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertTrue(is_external_url(url))
                anchor = Anchors(link(url, 'Paper')).anchors[0]
                self.assertEqual(anchor['target'], '_blank')
                self.assertEqual(set(anchor['rel'].split()), {'noopener', 'noreferrer'})

    def test_internal_and_non_web_urls(self):
        urls = [
            '', '#paper-02', '?year=2026', '/papers/', '../research/index.html',
            'assets/downloads/DONNARUMMA_CV.pdf',
            'https://www.francescodonnarumma.net/papers/',
            'http://francescodonnarumma.net/papers/',
            '//donnarumma.github.io/papers/',
            'https://WWW.FRANCESCODONNARUMMA.NET./papers/',
            'mailto:francesco.donnarumma@istc.cnr.it', 'tel:+390600000000',
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertFalse(is_external_url(url))
                self.assertNotIn('target', Anchors(link(url, 'Link')).anchors[0])

    def test_imported_external_link_preserves_attributes(self):
        value = '<a href="https://example.org/paper?x=1&amp;y=2" target="_self" rel="nofollow noopener" title="Paper"><em>Title</em></a>'
        anchor = Anchors(localize(value, '../')).anchors[0]
        self.assertEqual(anchor['href'], 'https://example.org/paper?x=1&y=2')
        self.assertEqual(anchor['target'], '_blank')
        self.assertEqual(anchor['rel'].split(), ['nofollow', 'noopener', 'noreferrer'])
        self.assertEqual(anchor['title'], 'Paper')

    def test_target_is_decided_after_url_repair(self):
        cases = [
            ('#BAD_URL', 'https://doi.org/10.1080/09540091.2012.684670', '_blank'),
            ('http://donnarumma10differential.bib', '../assets/downloads/donnarumma.bib', None),
            ('/papers/#paper-02', '../papers/index.html#paper-02', None),
            ('assets/downloads/donnarumma.bib', '../assets/downloads/donnarumma.bib', None),
        ]
        for url, expected, target in cases:
            with self.subTest(url=url):
                anchor = Anchors(localize(f'<a href="{url}" target="_blank">Link</a>', '../')).anchors[0]
                self.assertEqual(anchor['href'], expected)
                self.assertEqual(anchor.get('target'), target)

    def test_link_title_is_escaped(self):
        anchor = Anchors(link('https://example.org/', 'Profile', 'profile-link', title='A "profile"')).anchors[0]
        self.assertEqual(anchor['title'], 'A "profile"')


class HighlightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'content/site.json').read_text())
        cls.settings = json.loads((ROOT / 'content/settings.json').read_text())

    def test_highlights_link_to_existing_papers(self):
        highlights = self.data['pages']['home']['highlights']
        papers = self.data['pages']['papers']['entries']
        by_doi = {
            anchor['href']: entry
            for entry in papers
            for anchor in Anchors(' '.join(entry['paragraphs'])).anchors
            if anchor.get('href', '').startswith('https://doi.org/')
        }
        self.assertEqual(len(highlights), 8)
        self.assertIn('Inferential planning in the frontal cortex', plain(highlights[0]))
        years = []
        for highlight in highlights:
            anchor = Anchors(highlight).anchors[0]
            self.assertIn(anchor['href'], by_doi)
            paper = by_doi[anchor['href']]
            self.assertTrue(plain(highlight).endswith(paper['year']))
            years.append(paper['year'])
        self.assertEqual(years, sorted(years, reverse=True))

    def test_home_highlight_links_open_new_tabs(self):
        for prefix in ('', '../'):
            anchors = Anchors(home_body(self.data, prefix)).anchors
            highlights = [a for a in anchors if a['href'].startswith('https://doi.org/')]
            self.assertEqual(len(highlights), 8)
            for anchor in highlights:
                self.assertEqual(anchor['target'], '_blank')
                self.assertEqual(set(anchor['rel'].split()), {'noopener', 'noreferrer'})

    def test_search_finds_highlight_and_full_publication(self):
        matches = [item['url'] for item in make_search_index(self.data, self.settings)
                   if 'inferential planning' in (item['title'] + ' ' + item['text']).lower()]
        self.assertEqual(matches, ['home/index.html', 'papers/index.html#paper-01'])


if __name__ == '__main__':
    unittest.main()
