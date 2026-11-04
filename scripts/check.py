#!/usr/bin/env python3
"""Validate content and every generated local asset, navigation target, and anchor."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
errors = []

class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = set(); self.refs = []; self.h1s = 0; self.lang = None
        self.titles = 0; self.has_main = False; self.images = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html': self.lang = attrs.get('lang')
        if tag == 'title': self.titles += 1
        if tag == 'main': self.has_main = True
        if tag == 'h1': self.h1s += 1
        if tag == 'img':
            self.images += 1
            if 'alt' not in attrs: errors.append('Image missing alt text')
        if 'id' in attrs:
            if attrs['id'] in self.ids: errors.append('Duplicate HTML ID: ' + attrs['id'])
            self.ids.add(attrs['id'])
        for key in ('src', 'href'):
            if attrs.get(key): self.refs.append(attrs[key])

docs = {}
for path in OUT.glob('*.html'):
    doc = Document(); doc.feed(path.read_text()); docs[path.resolve()] = doc
    if doc.h1s != 1: errors.append(f'{path.name}: expected one h1, got {doc.h1s}')
    if not doc.lang or not doc.has_main or not doc.titles: errors.append(f'{path.name}: missing document semantics')
    for bad in ('Lorem ipsum', 'TODO', 'undefined', 'href="#"', 'PLACEHOLDER'):
        if bad in path.read_text(): errors.append(f'{path.name}: placeholder {bad}')

local_refs = 0
for path, doc in docs.items():
    for ref in doc.refs:
        url = urlsplit(ref)
        if url.scheme or url.netloc: continue
        target = (path.parent / unquote(url.path)).resolve() if url.path else path
        if not target.is_relative_to(OUT.resolve()): errors.append(f'{path.name}: nonportable or escaping link {ref}'); continue
        if not target.exists(): errors.append(f'{path.name}: missing local target {ref}'); continue
        if url.fragment and target in docs and unquote(url.fragment) not in docs[target].ids:
            errors.append(f'{path.name}: missing anchor {ref}')
        local_refs += 1

pubs = json.loads((ROOT/'content/publications.json').read_text())
for stylesheet in (OUT/'assets').glob('*.css'):
    for ref in re.findall(r'url\([\x22\x27]?([^\x22\x27)]+)',stylesheet.read_text()):
        if not urlsplit(ref).scheme and not (stylesheet.parent/ref).is_file():
            errors.append(f'{stylesheet.name}: missing stylesheet asset {ref}')
ids = set()
for p in pubs:
    for field in ('id', 'title', 'authors', 'year', 'venue', 'topics', 'url', 'source', 'status'):
        if not p.get(field): errors.append(f'{p.get("title")}: missing {field}')
    if p['id'] in ids: errors.append('Duplicate publication ID: '+p['id'])
    ids.add(p['id'])
    if not 1990 <= p['year'] <= 2026: errors.append('Invalid publication year')
    if p['status'] not in ('preprint','published','accepted'): errors.append('Invalid publication status')
    if p['venue']=='arXiv' and p['status']!='preprint': errors.append('Preprint presented as published')
    if p['status']=='preprint' and p['venue']!='arXiv': errors.append('Preprint lacks explicit venue label')
    if not set(p['topics']) <= {'ai','fairness','social','privacy','systems'}: errors.append('Invalid research topic')
    for field in ('source','url'):
        if urlsplit(p[field]).scheme != 'https': errors.append('Invalid source URL: '+p[field])
    seen_links = {p['url'], p.get('pdf')}
    for resource in p.get('links', []):
        url = urlsplit(resource['url'])
        if not resource.get('label') or url.scheme != 'https' or not url.netloc or resource['url'] in seen_links:
            errors.append(f'Invalid or duplicate resource for {p["title"]}: {resource}')
        seen_links.add(resource['url'])
alumni = json.loads((ROOT/'content/alumni.json').read_text())
for p in json.loads((ROOT/'content/people.json').read_text()):
    if p.get('image') and not (OUT/'assets'/p['image']).exists(): errors.append('Missing portrait: '+p['name'])
for p in alumni:
    if p.get('destination') and p.get('destinationType') != 'First destination': errors.append('Alumni destination must be first employment: '+p['name'])
    if not p.get('source') or not p.get('url'): errors.append('Alumni missing source/profile: '+p['name'])
if errors:
    raise SystemExit('\n'.join(errors))
print(f'PASS: {len(docs)} HTML pages; {local_refs} local links/assets/anchors; {len(pubs)} sourced publications; {len(alumni)} alumni profiles; all portrait assets present.')
