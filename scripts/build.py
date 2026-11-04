#!/usr/bin/env python3
"""Build a portable, dependency-free static website from reviewed JSON content."""
import html
import json
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
def read(name): return json.loads((ROOT / 'content' / (name + '.json')).read_text())
def e(value): return html.escape(str(value), quote=True)
PUBS, PEOPLE, ALUMNI, AREAS = [read(x) for x in ('publications','people','alumni','research')]
LABELS = {a['id']: a['title'] for a in AREAS}
ARROW = '<span aria-hidden="true">↗</span>'
RIGHT = '<span aria-hidden="true">↗</span>'

def link(url, text, cls='text-link'):
    return f'<a class="{cls}" href="{e(url)}">{text} {ARROW}</a>'

def mark():
    return '<span class="brand-mark" aria-hidden="true">n<span>/</span>s</span>'

def header(page):
    nav=[('index','Overview'),('research','Research'),('publications','Publications'),('people','People')]
    links=''.join(f'<a href="{p}.html"'+(' aria-current="page"' if page==p or page=='home' and p=='index' else '')+f'>{t}<span class="nav-indicator" aria-hidden="true">↗</span></a>' for p,t in nav)
    return f'''<a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header"><div class="header-inner">
    <a class="rail-institution" href="https://www.mpi-sws.org/">MPI–SWS <span aria-hidden="true">↗</span></a>
    <a class="brand" href="index.html" aria-label="Networked Systems Research Group home">{mark()}<span class="brand-name">Networked Systems<br>Research Group</span></a>
    <button class="menu-toggle" aria-label="Open navigation" aria-expanded="false" aria-controls="site-nav"><span></span><span></span></button>
    <nav id="site-nav" aria-label="Main navigation">{links}</nav>
    </div></header>'''

def footer():
    return '''<footer class="site-footer"><div class="container footer-inner"><p>Networked Systems Research Group<br><a href="https://www.mpi-sws.org/">Max Planck Institute for Software Systems ↗</a></p><div><a href="https://imprint.mpi-klsb.mpg.de/sws/www.mpi-sws.org">Imprint</a><a href="privacy.html">Privacy</a><span>© 2026</span></div></div></footer>'''

def layout(page,title,description,body):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · Networked Systems Research Group</title><meta name="description" content="{e(description)}">
<meta name="theme-color" content="#f4f4ef"><meta property="og:title" content="{e(title)} · Networked Systems Research Group"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="website">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css"><script src="assets/app.js" defer></script></head>
<body data-page="{page}">{header(page)}<div class="document-shell"><main id="main">{body}</main>{footer()}</div></body></html>'''

def intro(kicker,title,desc,extra=''):
    eyebrow = f'<p class="eyebrow">{kicker}</p>' if kicker else ''
    return f'<section class="page-intro container">{eyebrow}<h1>{title}</h1><div class="intro-bottom"><p class="lede">{desc}</p>{extra}</div></section>'


def paper_resources(p):
    resources = [link(p['pdf'], 'PDF', 'paper-action')] if p.get('pdf') else []
    resources.extend(link(item['url'], e(item['label']), 'paper-action') for item in p.get('links', []))
    return ''.join(resources)

def paper(p):
    tags=''.join(f'<a class="tag" href="publications.html?topic={t}">{e(LABELS[t])}</a>' for t in p['topics'])
    badge='' if p['status']=='published' else f'<span class="status-badge">{e(p["status"])}</span>'
    summary=f'<p class="paper-summary">{e(p["summary"])}</p>' if p.get('summary') else ''
    return f'''<article class="paper" data-paper data-year="{p['year']}" data-topics="{' '.join(p['topics'])}" data-status="{p['status']}" data-search="{e((p['title']+' '+p['authors']+' '+p['venue']).casefold())}">
    <div class="paper-meta"><span>{e(p['venue'])} · {p['year']}</span>{badge}</div><div class="paper-main"><h3><a href="{e(p['url'])}">{e(p['title'])} {ARROW}</a></h3><p class="authors">{e(p['authors'])}</p>{summary}<div class="paper-bottom"><div class="tags">{tags}</div><div class="paper-actions">{paper_resources(p)}</div></div></div></article>'''

def people_card(p):
    initials=''.join(n[0] for n in p['name'].split() if n not in ('P.',))[:2]
    img=f'<img src="assets/{p["image"]}" alt="{e(p["name"])}" loading="lazy" width="360" height="360">' if p.get('image') and (ROOT/'assets'/p['image']).exists() else f'<div class="person-initials" aria-hidden="true">{initials}</div>'
    detail = p.get('interests')
    if p['category'] == 'phd':
        co_advisor = p.get('coAdvisor')
        detail = f'Co-advised with {co_advisor}' if co_advisor else ''
    detail_line = f'<p class="person-interests">{e(detail)}</p>' if detail else ''
    return f'<article class="person"><a class="person-photo" href="{e(p["url"])}" aria-label="{e(p["name"])}’s website">{img}{ARROW}</a><p class="person-role">{e(p["role"])}</p><h3><a href="{e(p["url"])}">{e(p["name"])}</a></h3>{detail_line}</article>'

def home():
    head = PEOPLE[0]
    recent = sorted(
        (paper for paper in PUBS if paper.get('publication_date')),
        key=lambda paper: paper['publication_date'],
        reverse=True,
    )[:5]
    recent_rows = []
    for paper in recent:
        published = paper['publication_date']
        month_only = len(published) == 7
        publication_date = date.fromisoformat(published + '-01' if month_only else published)
        label = publication_date.strftime('%b %Y')
        if not month_only:
            label = f'{publication_date.day} {label}'
        recent_rows.append(f'''<article class="reading-entry">
        <p class="entry-meta">{e(paper['venue'])} · <time datetime="{e(published)}">{label}</time></p>
        <h3><a href="{e(paper['url'])}">{e(paper['title'])} {ARROW}</a></h3>
        <p class="authors">{e(paper['authors'])}</p>
        </article>''')

    body = f'''<section class="container profile-overview">
    <div class="profile-introduction">
        <h1>{e(head['name'])}</h1>
        <p class="profile-role">Scientific Director, <a href="https://www.mpi-sws.org/">Max Planck Institute for Software Systems</a><br>Head of the Networked Systems Research Group</p>
        <p class="lede">My research spans Internet-scale systems, social computing, and responsible AI. I study how networks, platforms, and AI systems behave and how they affect the people who use them.</p>
        <div class="resource-links">
            {link('research.html', 'Research')}
            {link('people.html', 'People & alumni')}
            {link('https://scholar.google.com/citations?user=Bz3APTsAAAAJ', 'Google Scholar')}
        </div>
    </div>
    <img class="profile-portrait" src="assets/{e(head['image'])}" alt="{e(head['name'])}" width="170" height="210">
    </section>
    <section class="container section recent-work">
        <div class="index-heading"><h2>Recent work</h2>{link('publications.html', 'All publications')}</div>
        {''.join(recent_rows)}
    </section>'''
    return layout('home', head['name'], 'Krishna P. Gummadi, Scientific Director at MPI-SWS and head of the Networked Systems Research Group.', body)

def join_banner():
    return ''


def research():
    sections=[]
    for a in AREAS:
        related=[p for p in PUBS if a['id'] in p['topics']]
        preferred=next((p for p in related if a['featured'].lower() in p['title'].lower()),None)
        selected=([preferred] if preferred else [])+[p for p in related if p is not preferred][:1]
        examples=''.join(f'<li><span>{p["year"]} · {e(p["venue"])}</span><a href="{e(p["url"])}">{e(p["title"])} {ARROW}</a></li>' for p in selected)
        keywords=''.join(f'<span class="tag">{e(t)}</span>' for t in a['keywords'])
        sections.append(f'<section id="{a["id"]}" class="research-area {a["color"]}"><div><h2>{e(a["title"])}</h2><p>{e(a["description"])}</p><div class="tags">{keywords}</div></div><aside><p class="eyebrow">SELECTED PAPERS</p><ul class="related-papers">{examples}</ul>{link("publications.html?topic="+a["id"],"See related publications")}</aside></section>')
    body=intro('','Research areas','We measure deployed systems, build computational models, and design new methods. Across research areas, we ask how systems behave—and what their behavior means for people.')
    body+='<nav class="container topic-nav" aria-label="Research areas">'+''.join(f'<a href="#{a["id"]}">{e(a["title"])}</a>' for a in AREAS)+'</nav><div class="container">'+''.join(sections)+'</div>'
    body+='<section id="foundations" class="section foundations"><div class="container section-heading"><div><p class="eyebrow">FOUNDATIONS & CONTINUITY</p><h2>Earlier projects</h2></div><div><p>Early work on Internet access, peer-to-peer systems, and cloud computing remains part of our research story. The original project pages preserve that history.</p><div class="resource-links">'+link('https://people.mpi-sws.org/~gummadi/broadband_access.html','Broadband access')+link('https://people.mpi-sws.org/~gummadi/trusted_cloud.html','Trusted cloud computing')+link('https://people.mpi-sws.org/~gummadi/p2p_overlay.html','Peer-to-peer systems')+'</div></div></div></section>'+join_banner()
    return layout('research','Research','Explore research on language models, fairness, social computing, privacy, and networked systems.',body)

def publications():
    years=sorted({p['year'] for p in PUBS},reverse=True)
    chips='<button class="filter-chip active" data-topic="all" aria-pressed="true">All research</button>'+''.join(f'<button class="filter-chip" data-topic="{a["id"]}" aria-pressed="false">{e(a["title"])}</button>' for a in AREAS)
    groups=''.join(f'<section class="pub-year" data-year-group><h2>{year}</h2><div>{"".join(paper(p) for p in PUBS if p["year"]==year)}</div></section>' for year in years)
    body=intro('','Publications','Browse Krishna Gummadi’s publication archive. Search by title, author, or venue, and filter by research area and year.')
    body+=f'''<div class="container publication-browser"><form class="filter-panel" role="search" id="publication-filters"><div class="filter-fields"><label class="search-field"><span class="sr-only">Search publications</span><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></svg><input id="publication-search" name="q" type="search" placeholder="Search titles, authors, venues…" autocomplete="off"></label><label class="select-field"><span>Year</span><select id="year-filter" name="year"><option value="all">All years</option>{''.join(f'<option>{y}</option>' for y in years)}</select></label><label class="select-field"><span>Type</span><select id="type-filter" name="type"><option value="all">All work</option><option value="published">Published</option><option value="accepted">Accepted</option><option value="preprint">Preprints</option></select></label></div><div class="filter-topics" aria-label="Filter by research area">{chips}</div></form><div class="results-bar"><p id="publication-count" role="status">{len(PUBS)} publications</p><button id="clear-filters" class="plain-button" type="button">Reset filters <span aria-hidden="true">↺</span></button></div><div id="publication-results">{groups}</div><div class="empty-state" id="no-publications" hidden><h2>No matching publications.</h2><p>Try a different title, author, year, or research area.</p><button class="button" data-reset-publications>Reset filters</button></div><aside class="archive-note"><p class="eyebrow">BIBLIOGRAPHIC SOURCES</p><p>This archive brings together Krishna Gummadi’s MPI-SWS publications since October 2005 and earlier work. Preprints and accepted papers are labeled separately.</p><div class="resource-links">{link('https://people.mpi-sws.org/~gummadi/publications.html','Original bibliography')}{link('https://pure.mpg.de/cone/persons/resource/persons144524','Max Planck repository')}{link('https://orcid.org/0000-0003-1256-8800','ORCID')}{link('https://dblp.org/pid/g/PKrishnaGummadi.html','DBLP')}</div></aside></div>'''
    return layout('publications','Publications','Search and filter historical and recent publications from the Networked Systems Research Group.',body)

def people():
    body=intro('','People','Meet researchers and co-advised students working with Krishna Gummadi across systems, social computing, and AI.', '<a class="text-link" href="#alumni">Alumni ↓</a>')
    body+='<div class="container section people-section"><div class="leader-feature">'+people_card(PEOPLE[0])+'<div><p class="eyebrow">GROUP HEAD</p><h2>Krishna P. Gummadi</h2><p>Scientific Director at the Max Planck Institute for Software Systems and head of the Networked Systems Research Group.</p><p>His research spans the measurement, analysis, design, and evaluation of Internet-scale systems, from networks and social platforms to fair and responsible AI.</p><div class="resource-links">'+link(PEOPLE[0]['url'],'Personal website')+link('https://scholar.google.com/citations?user=Bz3APTsAAAAJ','Google Scholar')+'</div></div></div>'
    for category,title in [('postdoc','Postdoctoral researchers'),('phd','Doctoral researchers')]:
        body+=f'<div class="people-heading"><h2>{title}</h2><span class="eyebrow">MPI-SWS</span></div><div class="people-grid">'+''.join(people_card(p) for p in PEOPLE if p['category']==category)+'</div>'
    body += '</div>' + alumni()
    return layout('people','People','Researchers and co-advised students in and around the Networked Systems Research Group at MPI-SWS.',body)

def alumni():
    rows=[]
    for p in ALUMNI:
        placement = ''
        if p.get('destinationType') == 'First destination':
            role = f'<p>{e(p["destinationRole"])}</p>' if p.get('destinationRole') else ''
            placement = f'''<span class="journey-arrow" aria-hidden="true">→</span>
            <div class="alumni-destination"><h4><strong>{e(p['destination'])}</strong></h4>{role}</div>'''
        rows.append(f'''<article class="alumni-row"><div class="alumni-name"><h3><a href="{e(p['url'])}">{e(p['name'])} {ARROW}</a></h3><p>{e(p['formerRole'])}</p></div>{placement}</article>''')
    return f'''<section class="container alumni-section" id="alumni" aria-labelledby="alumni-title">
    <div class="people-heading"><h2 id="alumni-title">Alumni</h2></div>
    <div class="alumni-context"><p>First destinations after MPI are highlighted where known.</p></div>
    <div class="alumni-list">{''.join(rows)}</div>
    </section>'''

def privacy():
    body=intro('About this site','Privacy','This site serves research information and links to external resources.')+'<section class="container prose section"><h2>What this site stores</h2><p>The website does not include analytics, advertising, tracking cookies, forms, or accounts. Publication filters run in your browser. Search terms appear in the publication page URL so you can share a filtered view.</p><h2>Hosting and external links</h2><p>The hosting provider may process request information such as IP addresses and server logs. External websites have their own privacy practices. Fonts, scripts, and portraits are served with this website rather than loaded from third-party services.</p><h2>Institute information</h2><p>For institutional privacy information and contacts, see the <a href="https://data-protection.mpi-klsb.mpg.de/sws/www.mpi-sws.org">MPI-SWS data protection page</a>.</p></section>'
    return layout('privacy','Privacy','Privacy information for this static research website.',body)

def main():
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
    for name,fn in [('index',home),('research',research),('publications',publications),('people',people),('privacy',privacy)]:
        (OUT/(name+'.html')).write_text(fn())
    (OUT/'.nojekyll').write_text('')
    for retired_page in ('sources.html', 'contact.html', 'resources.html', 'publications.bib', 'assets/citations.json'):
        (OUT / retired_page).unlink(missing_ok=True)
    (OUT/'alumni.html').write_text('''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Alumni · Networked Systems Research Group</title>
<meta http-equiv="refresh" content="0; url=people.html#alumni"></head>
<body><main><h1>Alumni</h1><p><a href="people.html#alumni">Go to the alumni section on People</a>.</p></main></body></html>''')
    (OUT/'404.html').write_text(layout('404','Page not found','Page not found.',intro('404','Page not found','This page could not be found. Use the navigation to explore our research, or return to the homepage.','<a class="button" href="index.html">Back to home →</a>')))
    print(f'Built {len(list(OUT.glob("*.html")))} pages, {len(PUBS)} publication records, {len(ALUMNI)} alumni profiles → dist/')

if __name__=='__main__': main()
