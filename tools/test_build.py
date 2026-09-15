#!/usr/bin/env python3
"""Focused regression tests for generated link destinations."""

import unittest
from html.parser import HTMLParser

from build import is_external_url, link, localize


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


if __name__ == '__main__':
    unittest.main()
