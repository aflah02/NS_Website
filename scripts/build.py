#!/usr/bin/env python3
"""Build a portable, dependency-free static website from reviewed JSON content."""
import html
import json
import re
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
def read(name): return json.loads((ROOT / 'content' / (name + '.json')).read_text())
def e(value): return html.escape(str(value), quote=True)
PUBS, PEOPLE, ALUMNI, AREAS, RESOURCES = [read(x) for x in ('publications','people','alumni','research','resources')]
LABELS = {a['id']: a['title'] for a in AREAS}
ARROW = '<span aria-hidden="true">↗</span>'
RIGHT = '<span aria-hidden="true">↗</span>'

def link(url, text, cls='text-link'):
    return f'<a class="{cls}" href="{e(url)}">{text} {ARROW}</a>'

def mark():
    return '<span class="brand-mark" aria-hidden="true">n<span>/</span>s</span>'

def header(page):
    nav=[('index','Overview'),('research','Research'),('publications','Publications'),('people','People'),('resources','Code & data'),('contact','Contact')]
    links=''.join(f'<a href="{p}.html"'+(' aria-current="page"' if page==p or page=='home' and p=='index' else '')+f'><span class="nav-number">{i:02}</span>{t}<span class="nav-indicator" aria-hidden="true">↗</span></a>' for i,(p,t) in enumerate(nav))
    return f'''<a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header"><div class="header-inner">
    <a class="rail-institution" href="https://www.mpi-sws.org/">MPI–SWS <span aria-hidden="true">↗</span></a>
    <a class="brand" href="index.html" aria-label="Networked Systems Research Group home">{mark()}<span class="brand-name">Networked Systems<br>Research Group</span></a>
    <button class="menu-toggle" aria-label="Open navigation" aria-expanded="false" aria-controls="site-nav"><span></span><span></span></button>
    <nav id="site-nav" aria-label="Main navigation">{links}</nav>
    <div class="rail-bottom"><p>Max Planck Institute<br>for Software Systems</p><p>Saarbrücken<br>Kaiserslautern<br>Germany</p><a href="https://people.mpi-sws.org/~gummadi/">Krishna P. Gummadi {ARROW}</a></div>
    </div></header>'''

def footer():
    return '''<footer class="site-footer"><div class="container footer-inner"><p>Networked Systems Research Group<br><a href="https://www.mpi-sws.org/">Max Planck Institute for Software Systems ↗</a></p><div><a href="https://imprint.mpi-klsb.mpg.de/sws/www.mpi-sws.org">Imprint</a><a href="privacy.html">Privacy</a><span>© 2026</span></div></div></footer>'''

def layout(page,title,description,body):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · Networked Systems Research Group</title><meta name="description" content="{e(description)}">
<meta name="theme-color" content="#f4f4ef"><meta property="og:title" content="{e(title)} · Networked Systems Research Group"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="website">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css"><script src="assets/app.js" defer></script></head>
<body data-page="{page}">{header(page)}<div class="document-shell"><main id="main">{body}</main>{footer()}</div><p class="sr-only" id="action-status" role="status"></p></body></html>'''

def intro(kicker,title,desc,extra=''):
    return f'<section class="page-intro container"><p class="eyebrow">{kicker}</p><h1>{title}</h1><div class="intro-bottom"><p class="lede">{desc}</p>{extra}</div></section>'


def paper(p,compact=False):
    tags=''.join(f'<a class="tag" href="publications.html?topic={t}">{e(LABELS[t])}</a>' for t in p['topics'])
    badge='' if p['status']=='published' else f'<span class="status-badge">{e(p["status"])}</span>'
    summary=f'<p class="paper-summary">{e(p["summary"])}</p>' if p.get('summary') and not compact else ''
    pdf=link(p['pdf'],'PDF','paper-action') if p.get('pdf') else ''
    cite='' if compact else f'<button class="cite-button" data-cite="{e(p["id"])}" aria-label="View citation for {e(p["title"])}">BibTeX</button>'
    return f'''<article class="paper" data-paper data-year="{p['year']}" data-topics="{' '.join(p['topics'])}" data-status="{p['status']}" data-search="{e((p['title']+' '+p['authors']+' '+p['venue']).casefold())}">
    <div class="paper-meta"><span>{e(p['venue'])} · {p['year']}</span>{badge}</div><div class="paper-main"><h3><a href="{e(p['url'])}">{e(p['title'])} {ARROW}</a></h3><p class="authors">{e(p['authors'])}</p>{summary}<div class="paper-bottom"><div class="tags">{tags}</div><div class="paper-actions">{pdf}{cite}</div></div></div></article>'''

def people_card(p):
    initials=''.join(n[0] for n in p['name'].split() if n not in ('P.',))[:2]
    img=f'<img src="assets/{p["image"]}" alt="{e(p["name"])}" loading="lazy" width="360" height="360">' if p.get('image') and (ROOT/'assets'/p['image']).exists() else f'<div class="person-initials" aria-hidden="true">{initials}</div>'
    return f'<article class="person"><a class="person-photo" href="{e(p["url"])}" aria-label="{e(p["name"])}’s website">{img}{ARROW}</a><p class="person-role">{e(p["role"])}</p><h3><a href="{e(p["url"])}">{e(p["name"])}</a></h3><p class="person-interests">{e(p["interests"])}</p></article>'

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
            {link('contact.html', 'Contact')}
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
        sections.append(f'<section id="{a["id"]}" class="research-area {a["color"]}"><div class="area-number">{a["number"]}</div><div><h2>{e(a["title"])}</h2><p>{e(a["description"])}</p><div class="tags">{keywords}</div></div><aside><p class="eyebrow">SELECTED PAPERS</p><ul class="related-papers">{examples}</ul>{link("publications.html?topic="+a["id"],"See related publications")}</aside></section>')
    body=intro('01 / Research','Research areas','We measure deployed systems, build computational models, and design new methods. Across research areas, we ask how systems behave—and what their behavior means for people.')
    body+='<nav class="container topic-nav" aria-label="Research areas">'+''.join(f'<a href="#{a["id"]}">{a["number"]} {e(a["title"])}</a>' for a in AREAS)+'</nav><div class="container">'+''.join(sections)+'</div>'
    body+='<section id="foundations" class="section foundations"><div class="container section-heading"><div><p class="eyebrow">FOUNDATIONS & CONTINUITY</p><h2>Earlier projects</h2></div><div><p>Early work on Internet access, peer-to-peer systems, and cloud computing remains part of our research story. The original project pages preserve that history.</p><div class="resource-links">'+link('https://people.mpi-sws.org/~gummadi/broadband_access.html','Broadband access')+link('https://people.mpi-sws.org/~gummadi/trusted_cloud.html','Trusted cloud computing')+link('https://people.mpi-sws.org/~gummadi/p2p_overlay.html','Peer-to-peer systems')+'</div></div></div></section>'+join_banner()
    return layout('research','Research','Explore research on language models, fairness, social computing, privacy, and networked systems.',body)

def publications():
    years=sorted({p['year'] for p in PUBS},reverse=True)
    chips='<button class="filter-chip active" data-topic="all" aria-pressed="true">All research</button>'+''.join(f'<button class="filter-chip" data-topic="{a["id"]}" aria-pressed="false">{e(a["title"])}</button>' for a in AREAS)
    groups=''.join(f'<section class="pub-year" data-year-group><h2>{year}</h2><div>{"".join(paper(p) for p in PUBS if p["year"]==year)}</div></section>' for year in years)
    body=intro('02 / Publications','Publications','Explore selected recent work alongside the group’s historical publication archive. Search by title, author, or venue, and filter by research area and year.',f'<a class="text-link" href="publications.bib" download>Download bibliography ↓</a>')
    body+=f'''<div class="container publication-browser"><form class="filter-panel" role="search" id="publication-filters"><div class="filter-fields"><label class="search-field"><span class="sr-only">Search publications</span><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></svg><input id="publication-search" name="q" type="search" placeholder="Search titles, authors, venues…" autocomplete="off"></label><label class="select-field"><span>Year</span><select id="year-filter" name="year"><option value="all">All years</option>{''.join(f'<option>{y}</option>' for y in years)}</select></label><label class="select-field"><span>Type</span><select id="type-filter" name="type"><option value="all">All work</option><option value="published">Published</option><option value="accepted">Accepted</option><option value="preprint">Preprints</option></select></label></div><div class="filter-topics" aria-label="Filter by research area">{chips}</div></form><div class="results-bar"><p id="publication-count" role="status">{len(PUBS)} publications</p><button id="clear-filters" class="plain-button" type="button">Reset filters <span aria-hidden="true">↺</span></button></div><div id="publication-results">{groups}</div><div class="empty-state" id="no-publications" hidden><h2>No matching publications.</h2><p>Try a different title, author, year, or research area.</p><button class="button" data-reset-publications>Reset filters</button></div><aside class="archive-note"><p class="eyebrow">BIBLIOGRAPHIC SOURCES</p><p>This archive combines historical entries with a curated selection of recent papers; it is not a complete bibliography. Preprints and accepted papers are labeled separately.</p><div class="resource-links">{link('https://scholar.google.com/citations?user=Bz3APTsAAAAJ','Google Scholar')}{link('https://www.semanticscholar.org/search?q=Krishna%20P.%20Gummadi&sort=pub-date','Semantic Scholar')}{link('https://dblp.org/pid/g/PKrishnaGummadi.html','DBLP')}</div></aside></div>
    <dialog id="citation-dialog" aria-labelledby="citation-title"><div class="dialog-heading"><h2 id="citation-title">Citation</h2><button class="dialog-close" aria-label="Close citation">×</button></div><p id="citation-paper-title"></p><label class="sr-only" for="citation-text">BibTeX citation</label><textarea id="citation-text" rows="10" readonly></textarea><div class="dialog-actions"><button class="button" id="copy-citation">Copy BibTeX</button><span id="copy-status" role="status"></span></div></dialog>'''
    return layout('publications','Publications','Search and filter historical and recent publications from the Networked Systems Research Group.',body)

def people():
    body=intro('03 / People','People','Meet researchers and co-advised students working with Krishna Gummadi across systems, social computing, and AI.', '<a class="text-link" href="#alumni">Alumni ↓</a>')
    body+='<div class="container section people-section"><div class="leader-feature">'+people_card(PEOPLE[0])+'<div><p class="eyebrow">GROUP HEAD</p><h2>Krishna P. Gummadi</h2><p>Scientific Director at the Max Planck Institute for Software Systems and head of the Networked Systems Research Group.</p><p>His research spans the measurement, analysis, design, and evaluation of Internet-scale systems, from networks and social platforms to fair and responsible AI.</p><div class="resource-links">'+link(PEOPLE[0]['url'],'Personal website')+link('https://scholar.google.com/citations?user=Bz3APTsAAAAJ','Google Scholar')+'</div></div></div>'
    for category,title in [('postdoc','Postdoctoral researchers'),('phd','Doctoral researchers')]:
        body+=f'<div class="people-heading"><h2>{title}</h2><span class="eyebrow">MPI-SWS</span></div><div class="people-grid">'+''.join(people_card(p) for p in PEOPLE if p['category']==category)+'</div>'
    body += '</div>' + alumni()
    return layout('people','People','Researchers and co-advised students in and around the Networked Systems Research Group at MPI-SWS.',body)

def alumni():
    rows=[]
    for p in ALUMNI:
        current=f'<p class="alumni-current">Now: <a href="{e(p["currentSource"])}">{e(p["current"])} {ARROW}</a></p>' if p.get('current') else ''
        rows.append(f'''<article class="alumni-row" data-alumnus data-kind="{p['kind']}" data-search="{e(' '.join(str(x) for x in p.values()).casefold())}"><div class="alumni-name"><h3><a href="{e(p['url'])}">{e(p['name'])} {ARROW}</a></h3><p>{e(p['formerRole'])}</p></div><span class="journey-arrow" aria-hidden="true">→</span><div class="alumni-destination"><span class="eyebrow">{e(p['destinationType'])}</span><h4>{e(p['destination'])}</h4><p>{e(p['destinationRole'])}</p>{current}</div><div class="alumni-source">{link(p['source'],'Source','subtle-link')}</div></article>''')
    return f'''<section class="container alumni-section" id="alumni" aria-labelledby="alumni-title"><div class="people-heading"><h2 id="alumni-title">Alumni</h2></div><div class="alumni-context"><p>“First destination” means the first recorded appointment after MPI.</p></div><form id="alumni-filters" class="alumni-filters" role="search"><label class="search-field"><span class="sr-only">Search alumni by name or destination</span><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></svg><input id="alumni-search" type="search" placeholder="Search a name or destination…" autocomplete="off"></label><label class="select-field"><span>At MPI</span><select id="alumni-kind"><option value="all">All alumni</option><option value="phd">Doctoral researchers</option><option value="postdoc">Postdoctoral researchers</option></select></label></form><div class="results-bar"><p id="alumni-count" role="status">{len(ALUMNI)} alumni</p><button id="reset-alumni" class="plain-button">Reset filters ↺</button></div><div class="alumni-list">{''.join(rows)}</div><div id="no-alumni" class="empty-state" hidden><h2>No matching alumni.</h2><p>Try a different name or destination, or reset the filters.</p></div></section>'''

def resources():
    cards=''.join(f'<article class="resource-card"><div class="card-top"><span class="eyebrow">{e(r["type"])}</span><span aria-hidden="true">↗</span></div><h2><a href="{e(r["url"])}">{e(r["title"])}</a></h2><p>{e(r["description"])}</p><span class="tag">{e(r["tag"])}</span><div class="resource-card-links">{link(r["url"],"Explore resource")}{link(r["paper"],"Research context","subtle-link")}</div></article>' for r in RESOURCES)
    body=intro('04 / Open research','Code & data','Software, models, and data from our research and collaborations. Follow each project for documentation, licensing, and access details.')+f'<section class="container section resources-grid">{cards}</section><section class="container historical-note"><h2>Looking for an older project?</h2><p>The original website documents historical systems such as TrulyTweeting, Friendlist Manager, and privacy-awareness tools. Those services may no longer be maintained; their research remains part of the archive.</p>{link("https://people.mpi-sws.org/~gummadi/","Visit the original project archive")}</section>'
    return layout('resources','Resources','Open-source software, models, datasets, and historical projects from the group and its collaborators.',body)

def contact():
    body=intro('05 / Contact','Contact','Interested in a research collaboration, doctoral study, or an internship? Explore our work and the institute’s application routes.')
    body+='''<section class="container contact-grid section"><article><p class="eyebrow">RESEARCH & COLLABORATION</p><h2>Research inquiries</h2><p>For research inquiries, contact Krishna through his MPI-SWS profile. For a specific project, the researchers’ personal pages are a good starting point.</p>'''+link('https://people.mpi-sws.org/~gummadi/','Krishna’s contact information')+link('people.html','Find a researcher')+'''</article><article><p class="eyebrow">STUDY & RESEARCH AT MPI-SWS</p><h2>Doctoral & research positions</h2><p>Applications are handled through the institute’s official channels. Consult MPI-SWS for current doctoral, internship, and postdoctoral opportunities and application requirements.</p>'''+link('https://www.mpi-sws.org/graduate-studies/','Doctoral studies')+link('https://www.mpi-sws.org/research-careers/','Research careers')+'''</article></section><section class="location-section"><div class="container"><div><p class="eyebrow">MPI-SWS LOCATIONS</p><h2>Max Planck Institute<br>for Software Systems</h2><p>MPI-SWS has sites in Saarbrücken and Kaiserslautern.</p>'''+link('https://www.mpi-sws.org/about-us/#contact','Directions & institute contacts')+'''</div><div class="address-list"><address><span class="eyebrow">SAARBRÜCKEN</span><p>Campus E1 5<br>66123 Saarbrücken<br>Germany</p></address><address><span class="eyebrow">KAISERSLAUTERN</span><p>Paul-Ehrlich-Straße G 26<br>67663 Kaiserslautern<br>Germany</p></address></div></div></section>'''
    return layout('contact','Contact','Research collaboration and study opportunities with the Networked Systems Research Group and MPI-SWS.',body)

def privacy():
    body=intro('About this site','Privacy','This site serves research information and links to external resources.')+'<section class="container prose section"><h2>What this site stores</h2><p>The website does not include analytics, advertising, tracking cookies, forms, or accounts. Publication and alumni filters run in your browser. Search terms appear in the publication page URL so you can share a filtered view.</p><h2>Hosting and external links</h2><p>The hosting provider may process request information such as IP addresses and server logs. External websites have their own privacy practices. Fonts, scripts, and portraits are served with this website rather than loaded from third-party services.</p><h2>Institute information</h2><p>For institutional privacy information and contacts, see the <a href="https://data-protection.mpi-klsb.mpg.de/sws/www.mpi-sws.org">MPI-SWS data protection page</a>.</p></section>'
    return layout('privacy','Privacy','Privacy information for this static research website.',body)

def bibtex(p):
    authors=p['authors']
    if ', ' in authors: authors=' and '.join(x.strip().removeprefix('and ') for x in authors.split(', ') if x.strip())
    title=p['title'].replace('{',r'\{').replace('}',r'\}')
    journals=('TMLR','TON','TWeb','CCR','Population and Development Review','IEEE Internet Computing','ACM Multimedia Systems Journal','Elsevier Computer Networks')
    if p['status']=='preprint': typ,field='misc','howpublished'
    elif p['status']=='accepted': typ,field='unpublished','note'
    elif p['venue'] in journals or 'Transactions' in p['venue']: typ,field='article','journal'
    else: typ,field='inproceedings','booktitle'
    venue=('Accepted at ' if p['status']=='accepted' else '')+p['venue']
    return f'@{typ}{{ns-{p["id"]},\n  title = {{{{{title}}}}},\n  author = {{{authors}}},\n  year = {{{p["year"]}}},\n  {field} = {{{venue}}},\n  url = {{{p["url"]}}}\n}}'

def main():
    OUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True)
    for name,fn in [('index',home),('research',research),('publications',publications),('people',people),('resources',resources),('contact',contact),('privacy',privacy)]:
        (OUT/(name+'.html')).write_text(fn())
    (OUT/'publications.bib').write_text('\n\n'.join(bibtex(p) for p in PUBS)+'\n')
    (OUT/'assets/citations.json').write_text(json.dumps({p['id']:{'title':p['title'],'bibtex':bibtex(p)} for p in PUBS},ensure_ascii=False))
    (OUT/'.nojekyll').write_text('')
    (OUT/'sources.html').unlink(missing_ok=True)
    (OUT/'alumni.html').write_text('''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Alumni · Networked Systems Research Group</title>
<meta http-equiv="refresh" content="0; url=people.html#alumni"></head>
<body><main><h1>Alumni</h1><p><a href="people.html#alumni">Go to the alumni section on People</a>.</p></main></body></html>''')
    (OUT/'404.html').write_text(layout('404','Page not found','Page not found.',intro('404','Page not found','This page could not be found. Use the navigation to explore our research, or return to the homepage.','<a class="button" href="index.html">Back to home →</a>')))
    print(f'Built {len(list(OUT.glob("*.html")))} pages, {len(PUBS)} publication records, {len(ALUMNI)} alumni profiles → dist/')

if __name__=='__main__': main()
