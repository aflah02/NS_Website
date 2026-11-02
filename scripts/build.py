#!/usr/bin/env python3
"""Build a portable, dependency-free static website from reviewed JSON content."""
import html
import json
import random
import re
import shutil
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
    return '''<svg class="brand-mark" viewBox="0 0 44 44" aria-hidden="true"><path d="M10 32 13 10 33 16 30 35 13 10M10 32 33 16M10 32 30 35"/><circle cx="13" cy="10" r="4"/><circle cx="33" cy="16" r="4"/><circle cx="10" cy="32" r="4"/><circle cx="30" cy="35" r="4"/></svg>'''

def header(page):
    nav=[('research','Research'),('publications','Publications'),('people','People'),('alumni','Alumni'),('resources','Resources')]
    links=''.join(f'<a href="{p}.html"'+(' aria-current="page"' if page==p else '')+f'>{t}</a>' for p,t in nav)
    return f'''<a class="skip-link" href="#main">Skip to content</a>
    <header class="site-header"><div class="container header-inner">
    <a class="brand" href="index.html" aria-label="Networked Systems Research Group home">{mark()}<span>Networked Systems<span class="brand-small">Research Group · MPI-SWS</span></span></a>
    <button class="menu-toggle" aria-label="Open navigation" aria-expanded="false" aria-controls="site-nav"><span></span><span></span></button>
    <nav id="site-nav" aria-label="Main navigation">{links}<a class="nav-contact" href="contact.html"{' aria-current="page"' if page=='contact' else ''}>Get in touch {ARROW}</a></nav>
    </div></header>'''

def footer():
    return f'''<footer class="site-footer"><div class="container"><div class="footer-top">
    <div><a class="brand footer-brand" href="index.html">{mark()}<span>Networked Systems<span class="brand-small">Research Group · MPI-SWS</span></span></a><p>Studying the systems.<br>Understanding the connections.</p></div>
    <div class="footer-col"><span class="eyebrow">Explore</span><a href="research.html">Research</a><a href="publications.html">Publications</a><a href="people.html">People</a><a href="alumni.html">Alumni</a></div>
    <div class="footer-col"><span class="eyebrow">Connect</span><a href="contact.html">Contact & opportunities</a><a href="https://www.mpi-sws.org/">MPI for Software Systems {ARROW}</a><a href="https://aics.mpi-sws.org/">AI, Computing & Society {ARROW}</a><a href="https://people.mpi-sws.org/~gummadi/">Krishna’s personal website {ARROW}</a></div>
    </div><div class="footer-bottom"><span>© 2026 Networked Systems Research Group</span><div><a href="sources.html">Sources & content notes</a><a href="https://imprint.mpi-klsb.mpg.de/sws/www.mpi-sws.org">Imprint</a><a href="privacy.html">Privacy</a></div></div></div></footer>'''

def layout(page,title,description,body):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} · Networked Systems Research Group</title><meta name="description" content="{e(description)}">
<meta name="theme-color" content="#182b3a"><meta property="og:title" content="{e(title)} · Networked Systems Research Group"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="website">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css"><script src="assets/app.js" defer></script></head>
<body data-page="{page}">{header(page)}<main id="main">{body}</main>{footer()}<p class="sr-only" id="action-status" role="status"></p></body></html>'''

def intro(kicker,title,desc,extra=''):
    return f'<section class="page-intro container"><p class="eyebrow">{kicker}</p><h1>{title}</h1><div class="intro-bottom"><p class="lede">{desc}</p>{extra}</div></section>'

def network():
    rng=random.Random(24)
    centers=[(145,200),(335,175),(270,345)]
    colors=['#d66b4b','#6a8e97','#b1b195']
    points=[]; lines=[];nodes=[]
    for k,(cx,cy) in enumerate(centers):
        group=[(cx+rng.gauss(0,48),cy+rng.gauss(0,46)) for _ in range(24)]
        for i,(x,y) in enumerate(group):
            points.append((x,y))
            for j in range(i):
                px,py=group[j]
                if (x-px)**2+(y-py)**2<3100 and rng.random()<.52:lines.append(f'<path d="M{x:.1f} {y:.1f}L{px:.1f} {py:.1f}" stroke="{colors[k]}" opacity=".26"/>')
            nodes.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rng.choice([2,2.5,3,4])}" fill="{colors[k]}"/>')
    for i,j in [(3,29),(7,45),(30,56),(13,65),(38,63),(5,54),(12,39),(19,51)]:
        x,y=points[i];px,py=points[j];lines.append(f'<path d="M{x} {y}Q255 250 {px} {py}" stroke="#182b3a" opacity=".14" fill="none"/>')
    return f'''<div class="research-figure"><div class="figure-label"><span>FIG. 01</span><span>CONNECTED BY QUESTIONS</span></div>
    <svg viewBox="0 0 500 470" role="img" aria-labelledby="network-title network-desc"><title id="network-title">People, platforms, and AI: our research landscape</title><desc id="network-desc">An illustrative network connects three clusters representing systems, people, and artificial intelligence. These are research themes, not measured data.</desc>
    <circle cx="250" cy="254" r="190" class="orbit"/><circle cx="250" cy="254" r="132" class="orbit"/>
    <g stroke-width="1">{''.join(lines)}</g>{''.join(nodes)}
    <a href="research.html#ai" aria-label="Explore AI and language models"><circle cx="145" cy="200" r="20" fill="#d66b4b"/><path d="m137 200 5 5 10-10" stroke="#fff" fill="none" stroke-width="1.5"/><text x="68" y="105">ARTIFICIAL INTELLIGENCE</text></a>
    <a href="research.html#social" aria-label="Explore social computing"><circle cx="335" cy="175" r="22" fill="#6a8e97"/><circle cx="335" cy="170" r="4" stroke="#fff" fill="none"/><path d="M328 184v-3a7 7 0 0 1 14 0v3" stroke="#fff" fill="none"/><text x="330" y="84">PEOPLE</text></a>
    <a href="research.html#systems" aria-label="Explore networked systems"><circle cx="270" cy="345" r="20" fill="#182b3a"/><path d="M262 338h16v11h-16zM267 353h6M270 349v4" stroke="#fff" fill="none"/><text x="286" y="429">NETWORKED SYSTEMS</text></a>
    </svg><div class="figure-caption"><span class="small-dot"></span>Different systems. Interconnected questions.</div></div>'''

def paper(p,compact=False):
    tags=''.join(f'<a class="tag" href="publications.html?topic={t}">{e(LABELS[t])}</a>' for t in p['topics'])
    badge='' if p['status']=='published' else f'<span class="status-badge">{e(p["status"])}</span>'
    summary=f'<p class="paper-summary">{e(p["summary"])}</p>' if p.get('summary') and not compact else ''
    pdf=link(p['pdf'],'PDF','paper-action') if p.get('pdf') else ''
    cite='' if compact else f'<button class="cite-button" data-cite="{e(p["id"])}" aria-label="View citation for {e(p["title"])}">Cite <span aria-hidden="true">⌘</span></button>'
    return f'''<article class="paper" data-paper data-year="{p['year']}" data-topics="{' '.join(p['topics'])}" data-status="{p['status']}" data-search="{e((p['title']+' '+p['authors']+' '+p['venue']).casefold())}">
    <div class="paper-meta"><span>{e(p['venue'])} · {p['year']}</span>{badge}</div><div class="paper-main"><h3><a href="{e(p['url'])}">{e(p['title'])} {ARROW}</a></h3><p class="authors">{e(p['authors'])}</p>{summary}<div class="paper-bottom"><div class="tags">{tags}</div><div class="paper-actions">{pdf}{cite}</div></div></div></article>'''

def people_card(p):
    initials=''.join(n[0] for n in p['name'].split() if n not in ('P.',))[:2]
    img=f'<img src="assets/{p["image"]}" alt="{e(p["name"])}" loading="lazy" width="360" height="360">' if p.get('image') and (ROOT/'assets'/p['image']).exists() else f'<div class="person-initials" aria-hidden="true">{initials}</div>'
    return f'<article class="person"><a class="person-photo" href="{e(p["url"])}" aria-label="{e(p["name"])}’s website">{img}{ARROW}</a><p class="person-role">{e(p["role"])}</p><h3><a href="{e(p["url"])}">{e(p["name"])}</a></h3><p class="person-interests">{e(p["interests"])}</p></article>'

def home():
    cards=''.join(f'<a class="area-card {a["color"]}" href="research.html#{a["id"]}"><div class="card-top"><span>{a["number"]}</span>{ARROW}</div><h3>{e(a["title"])}</h3><p>{e(a["question"])}</p></a>' for a in AREAS)
    chosen=[next(p for p in PUBS if term in p['title']) for term in ('Fractional Rotation','Characterizing Web Search in The Age','Fine-tuning vs.','Fairness Constraints: Mechanisms')]
    body=f'''<section class="hero container"><div class="hero-copy"><p class="eyebrow"><span class="accent-rule"></span>MAX PLANCK INSTITUTE FOR SOFTWARE SYSTEMS</p><h1>Understanding<br>systems that<br><em>connect us.</em></h1><p class="lede">From Internet networks to social platforms and AI, we study how large-scale systems work—and how they can work better for people.</p><div class="hero-actions"><a class="button" href="research.html">Explore our research <span aria-hidden="true">↗</span></a><a class="text-link" href="publications.html">Read our work <span aria-hidden="true">→</span></a></div></div>{network()}</section>
    <div class="institution-strip"><div class="container"><span>Networked Systems Research Group</span><span>Led by <a href="people.html">Krishna P. Gummadi {ARROW}</a></span><span>Saarbrücken & Kaiserslautern, Germany</span></div></div>
    <section class="section container"><div class="section-heading"><div><p class="eyebrow">OUR RESEARCH</p><h2>Connected systems.<br>Consequential questions.</h2></div><div><p>We bring measurement, modeling, and system design together to understand technology in its human context.</p>{link('research.html','Explore our research areas')}</div></div><div class="area-grid">{cards}</div></section>
    <section class="work-section"><div class="container section"><div class="section-heading"><div><p class="eyebrow">SELECTED PUBLICATIONS</p><h2>Ideas, put to the test.</h2></div>{link('publications.html','Browse the publication archive')}</div><div class="paper-list">{''.join(paper(p,True) for p in chosen)}</div></div></section>
    <section class="section container history"><div><p class="eyebrow">A CONTINUING THREAD</p><h2>New systems.<br>The same curiosity.</h2><p>Our questions have evolved with the Internet. A commitment to understanding real systems through evidence connects our early networking research with our work on platforms, fairness, and AI.</p>{link('research.html#foundations','Trace our research')}</div><ol class="timeline"><li><span>FOUNDATIONS</span><h3>The networked Internet</h3><p>Peer-to-peer systems, routing, broadband access, and cloud trust.</p></li><li><span>PEOPLE & PLATFORMS</span><h3>Social computing at scale</h3><p>Online communities, information diffusion, privacy, and algorithmic fairness.</p></li><li><span>NEW FRONTIERS</span><h3>AI in the world</h3><p>Language-model learning, agent behavior, knowledge, and responsible deployment.</p></li></ol></section>
    <section class="aics-band"><div class="container aics-inner"><span class="aics-wordmark">AI <i>×</i> Computing <i>×</i> Society</span><div><p class="eyebrow">RESEARCH ACROSS BOUNDARIES</p><h2>Part of a wider conversation.</h2><p>Krishna contributes expertise in social computing and responsible AI to AICS, an interdisciplinary initiative connecting MPI-SWS and RPTU.</p>{link('https://aics.mpi-sws.org/','Discover AICS')}</div></div></section>
    <section class="section container"><div class="section-heading"><div><p class="eyebrow">THE PEOPLE BEHIND THE QUESTIONS</p><h2>Research is a shared pursuit.</h2></div>{link('people.html','Meet the researchers')}</div><div class="people-grid home-people">{''.join(people_card(p) for p in [PEOPLE[0],PEOPLE[1],PEOPLE[4],PEOPLE[6]])}</div><div class="alumni-prompt"><div><h3>Our connections continue beyond MPI.</h3><p>Meet former researchers and see where their work took them next.</p></div>{link('alumni.html','Explore our alumni')}</div></section>
    {join_banner()}'''
    return layout('home','Home','Networked Systems Research Group at MPI-SWS. Research on AI, fairness, social computing, privacy, and Internet-scale systems.',body)

def join_banner():
    return '<section class="join-banner"><div class="container"><div><p class="eyebrow">KEEP ASKING QUESTIONS</p><h2>Let’s explore what’s next.</h2></div><a class="button light" href="contact.html">Contact & opportunities <span aria-hidden="true">↗</span></a></div></section>'

def research():
    sections=[]
    for a in AREAS:
        related=[p for p in PUBS if a['id'] in p['topics']]
        preferred=next((p for p in related if a['featured'].lower() in p['title'].lower()),None)
        selected=([preferred] if preferred else [])+[p for p in related if p is not preferred][:1]
        examples=''.join(f'<li><span>{p["year"]} · {e(p["venue"])}</span><a href="{e(p["url"])}">{e(p["title"])} {ARROW}</a></li>' for p in selected)
        keywords=''.join(f'<span class="tag">{e(t)}</span>' for t in a['keywords'])
        sections.append(f'<section id="{a["id"]}" class="research-area {a["color"]}"><div class="area-number">{a["number"]}</div><div><p class="eyebrow">{e(a["title"])}</p><h2>{e(a["question"])}</h2><p>{e(a["description"])}</p><div class="tags">{keywords}</div></div><aside><p class="eyebrow">A WAY INTO THE WORK</p><ul class="related-papers">{examples}</ul>{link("publications.html?topic="+a["id"],"See related publications")}</aside></section>')
    body=intro('RESEARCH','The systems change.<br><em>The questions connect.</em>','We measure deployed systems, build computational models, and design new methods. Across research areas, we ask how systems behave—and what their behavior means for people.')
    body+='<nav class="container topic-nav" aria-label="Research areas">'+''.join(f'<a href="#{a["id"]}">{a["number"]} {e(a["title"])}</a>' for a in AREAS)+'</nav><div class="container">'+''.join(sections)+'</div>'
    body+='<section id="foundations" class="section foundations"><div class="container section-heading"><div><p class="eyebrow">FOUNDATIONS & CONTINUITY</p><h2>A measurement-driven tradition.</h2></div><div><p>Early work on Internet access, peer-to-peer systems, and cloud computing remains part of our research story. The original project pages preserve that history.</p><div class="resource-links">'+link('https://people.mpi-sws.org/~gummadi/broadband_access.html','Broadband access')+link('https://people.mpi-sws.org/~gummadi/trusted_cloud.html','Trusted cloud computing')+link('https://people.mpi-sws.org/~gummadi/p2p_overlay.html','Peer-to-peer systems')+'</div></div></div></section>'+join_banner()
    return layout('research','Research','Explore research on language models, fairness, social computing, privacy, and networked systems.',body)

def publications():
    years=sorted({p['year'] for p in PUBS},reverse=True)
    chips='<button class="filter-chip active" data-topic="all" aria-pressed="true">All research</button>'+''.join(f'<button class="filter-chip" data-topic="{a["id"]}" aria-pressed="false">{e(a["title"])}</button>' for a in AREAS)
    groups=''.join(f'<section class="pub-year" data-year-group><h2>{year}</h2><div>{"".join(paper(p) for p in PUBS if p["year"]==year)}</div></section>' for year in years)
    body=intro('PUBLICATIONS','A record of<br><em>shared inquiry.</em>','Explore selected recent work alongside the group’s historical publication archive. Search by title, author, or venue, and filter by research area and year.',f'<a class="text-link" href="publications.bib" download>Download bibliography ↓</a>')
    body+=f'''<div class="container publication-browser"><form class="filter-panel" role="search" id="publication-filters"><div class="filter-fields"><label class="search-field"><span class="sr-only">Search publications</span><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></svg><input id="publication-search" name="q" type="search" placeholder="Search titles, authors, venues…" autocomplete="off"></label><label class="select-field"><span>Year</span><select id="year-filter" name="year"><option value="all">All years</option>{''.join(f'<option>{y}</option>' for y in years)}</select></label><label class="select-field"><span>Type</span><select id="type-filter" name="type"><option value="all">All work</option><option value="published">Published</option><option value="accepted">Accepted</option><option value="preprint">Preprints</option></select></label></div><div class="filter-topics" aria-label="Filter by research area">{chips}</div></form><div class="results-bar"><p id="publication-count" role="status">{len(PUBS)} publications</p><button id="clear-filters" class="plain-button" type="button">Reset filters <span aria-hidden="true">↺</span></button></div><div id="publication-results">{groups}</div><div class="empty-state" id="no-publications" hidden><h2>No matching publications.</h2><p>Try a different title, author, year, or research area.</p><button class="button" data-reset-publications>Reset filters</button></div><aside class="archive-note"><p class="eyebrow">BEYOND THIS SELECTION</p><p>This archive combines historical entries with a curated selection of recent papers; it is not a complete bibliography. Preprints and accepted papers are labeled separately.</p><div class="resource-links">{link('https://scholar.google.com/citations?user=Bz3APTsAAAAJ','Google Scholar')}{link('https://www.semanticscholar.org/search?q=Krishna%20P.%20Gummadi&sort=pub-date','Semantic Scholar')}{link('https://dblp.org/pid/g/PKrishnaGummadi.html','DBLP')}{link('sources.html','Content sources')}</div></aside></div>
    <dialog id="citation-dialog" aria-labelledby="citation-title"><div class="dialog-heading"><h2 id="citation-title">Citation</h2><button class="dialog-close" aria-label="Close citation">×</button></div><p id="citation-paper-title"></p><label class="sr-only" for="citation-text">BibTeX citation</label><textarea id="citation-text" rows="10" readonly></textarea><div class="dialog-actions"><button class="button" id="copy-citation">Copy BibTeX</button><span id="copy-status" role="status"></span></div></dialog>'''
    return layout('publications','Publications','Search and filter historical and recent publications from the Networked Systems Research Group.',body)

def people():
    body=intro('PEOPLE','Different perspectives.<br><em>Shared curiosity.</em>','Meet researchers and co-advised students working with Krishna Gummadi across systems, social computing, and AI.')
    body+='<div class="container section people-section"><div class="leader-feature">'+people_card(PEOPLE[0])+'<div><p class="eyebrow">GROUP HEAD</p><h2>Krishna P. Gummadi</h2><p>Scientific Director at the Max Planck Institute for Software Systems and head of the Networked Systems Research Group.</p><p>His research spans the measurement, analysis, design, and evaluation of Internet-scale systems, from networks and social platforms to fair and responsible AI.</p><div class="resource-links">'+link(PEOPLE[0]['url'],'Personal website')+link('https://scholar.google.com/citations?user=Bz3APTsAAAAJ','Google Scholar')+'</div></div></div>'
    for category,title in [('postdoc','Postdoctoral researchers'),('phd','Doctoral researchers')]:
        body+=f'<div class="people-heading"><h2>{title}</h2><span class="eyebrow">RESEARCH THROUGH COLLABORATION</span></div><div class="people-grid">'+''.join(people_card(p) for p in PEOPLE if p['category']==category)+'</div>'
    body+='<p class="content-note">Profiles reflect the public sources reviewed in November 2026. This is a selected roster, including co-advised students; see the <a href="https://www.mpi-sws.org/people/">MPI-SWS directory</a> for institute-wide listings.</p><div class="alumni-prompt"><div><h3>The network keeps growing.</h3><p>Our alumni carry their research into universities, institutes, and industry.</p></div>'+link('alumni.html','Meet our alumni')+'</div></div>'+join_banner()
    return layout('people','People','Researchers and co-advised students in and around the Networked Systems Research Group at MPI-SWS.',body)

def alumni():
    rows=[]
    for p in ALUMNI:
        current=f'<p class="alumni-current">Now: <a href="{e(p["currentSource"])}">{e(p["current"])} {ARROW}</a></p>' if p.get('current') else ''
        rows.append(f'''<article class="alumni-row" data-alumnus data-kind="{p['kind']}" data-search="{e(' '.join(str(x) for x in p.values()).casefold())}"><div class="alumni-name"><h3><a href="{e(p['url'])}">{e(p['name'])} {ARROW}</a></h3><p>{e(p['formerRole'])}</p></div><span class="journey-arrow" aria-hidden="true">→</span><div class="alumni-destination"><span class="eyebrow">{e(p['destinationType'])}</span><h4>{e(p['destination'])}</h4><p>{e(p['destinationRole'])}</p>{current}</div><div class="alumni-source">{link(p['source'],'Source','subtle-link')}</div></article>''')
    body=intro('ALUMNI','Their next chapter.<br><em>Our lasting connections.</em>','Former doctoral and postdoctoral researchers have taken their ideas to research labs, universities, and industry around the world.')
    body+=f'''<section class="container alumni-section"><div class="alumni-context"><span class="context-symbol" aria-hidden="true">↗</span><div><h2>Where people went after MPI.</h2><p>“First destination” records the first appointment listed on Krishna’s original website or the researcher’s own profile. It is a historical placement, not a claim about their current employer. Other destinations are explicitly labeled.</p></div></div><form id="alumni-filters" class="alumni-filters" role="search"><label class="search-field"><span class="sr-only">Search alumni by name or destination</span><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></svg><input id="alumni-search" type="search" placeholder="Search a name or destination…" autocomplete="off"></label><label class="select-field"><span>At MPI</span><select id="alumni-kind"><option value="all">All alumni</option><option value="phd">Doctoral researchers</option><option value="postdoc">Postdoctoral researchers</option></select></label></form><div class="results-bar"><p id="alumni-count" role="status">{len(ALUMNI)} alumni</p><button id="reset-alumni" class="plain-button">Reset filters ↺</button></div><div class="alumni-list">{''.join(rows)}</div><div id="no-alumni" class="empty-state" hidden><h2>No matching alumni.</h2><p>Try a different name or destination, or reset the filters.</p></div><p class="content-note">A sourced selection of alumni, including co-advised researchers. Dates are omitted where they could not be verified. <a href="sources.html#alumni">See the alumni content notes</a>.</p></section>'''+join_banner()
    return layout('alumni','Alumni','Meet former researchers and discover their post-MPI destinations in academia and industry.',body)

def resources():
    cards=''.join(f'<article class="resource-card"><div class="card-top"><span class="eyebrow">{e(r["type"])}</span><span aria-hidden="true">↗</span></div><h2><a href="{e(r["url"])}">{e(r["title"])}</a></h2><p>{e(r["description"])}</p><span class="tag">{e(r["tag"])}</span><div class="resource-card-links">{link(r["url"],"Explore resource")}{link(r["paper"],"Research context","subtle-link")}</div></article>' for r in RESOURCES)
    body=intro('OPEN RESEARCH','Methods to build on.<br><em>Tools to explore.</em>','Software, models, and data from our research and collaborations. Follow each project for documentation, licensing, and access details.')+f'<section class="container section resources-grid">{cards}</section><section class="container historical-note"><h2>Looking for an older project?</h2><p>The original website documents historical systems such as TrulyTweeting, Friendlist Manager, and privacy-awareness tools. Those services may no longer be maintained; their research remains part of the archive.</p>{link("https://people.mpi-sws.org/~gummadi/","Visit the original project archive")}</section>'
    return layout('resources','Resources','Open-source software, models, datasets, and historical projects from the group and its collaborators.',body)

def contact():
    body=intro('CONTACT & OPPORTUNITIES','Good questions<br><em>start conversations.</em>','Interested in a research collaboration, doctoral study, or an internship? Explore our work and the institute’s application routes.')
    body+='''<section class="container contact-grid section"><article><p class="eyebrow">RESEARCH & COLLABORATION</p><h2>Connect with the group.</h2><p>For research inquiries, contact Krishna through his MPI-SWS profile. For a specific project, the researchers’ personal pages are a good starting point.</p>'''+link('https://people.mpi-sws.org/~gummadi/','Krishna’s contact information')+link('people.html','Find a researcher')+'''</article><article><p class="eyebrow">STUDY & RESEARCH AT MPI-SWS</p><h2>Explore the opportunities.</h2><p>Applications are handled through the institute’s official channels. Consult MPI-SWS for current doctoral, internship, and postdoctoral opportunities and application requirements.</p>'''+link('https://www.mpi-sws.org/graduate-studies/','Doctoral studies')+link('https://www.mpi-sws.org/research-careers/','Research careers')+'''</article></section><section class="location-section"><div class="container"><div><p class="eyebrow">BASED IN GERMANY · CONNECTED GLOBALLY</p><h2>Max Planck Institute<br>for Software Systems</h2><p>MPI-SWS has sites in Saarbrücken and Kaiserslautern.</p>'''+link('https://www.mpi-sws.org/about-us/#contact','Directions & institute contacts')+'''</div><div class="address-list"><address><span class="eyebrow">SAARBRÜCKEN</span><p>Campus E1 5<br>66123 Saarbrücken<br>Germany</p></address><address><span class="eyebrow">KAISERSLAUTERN</span><p>Paul-Ehrlich-Straße G 26<br>67663 Kaiserslautern<br>Germany</p></address></div></div></section>'''
    return layout('contact','Contact','Research collaboration and study opportunities with the Networked Systems Research Group and MPI-SWS.',body)

def sources():
    source_links=[('Original group and personal website','https://people.mpi-sws.org/~gummadi/','Historical research themes, alumni first placements, and group leadership.'),('Original publication archive','https://people.mpi-sws.org/~gummadi/publications.html','Historical bibliographic records, 2000–2018. Duplicate titles are consolidated.'),('ACL Anthology','https://aclanthology.org/people/krishna-p-gummadi/','Publication metadata for recent ACL and EMNLP papers.'),('MPI-SWS people directory','https://www.mpi-sws.org/people/','Researcher roles and institutional profiles.'),('AI, Computing & Society','https://aics.mpi-sws.org/','The interdisciplinary initiative and Krishna’s participation.'),('Qinyuan Wu’s publications','https://qinyuanwu0710.github.io/publications/','Recent publication venues and acceptance information.'),('Mohammad Aflah Khan’s website','https://aflah02.github.io/','Recent papers, acceptance information, and doctoral affiliation.'),('Till Speicher’s website','https://tillspeicher.com/','Current destination and research history.'),('Preethi Lahoti’s website','https://www.plahoti.de/about-me','Co-advising and first post-PhD destination.')]
    body=intro('CONTENT & ATTRIBUTION','A website grounded<br><em>in the research.</em>','Content reviewed on 2 November 2026. Publication entries and alumni placements link back to their sources.')
    body+='<section class="container prose section"><h2>Research and publications</h2><p>The research areas are an editorial synthesis of historical projects and recent publications. They are not an official organizational taxonomy. The archive is a selection, with historical coverage and recent additions, rather than a complete list of all group work. Each record includes a source URL in the underlying data.</p><p>Google Scholar denied automated access. Semantic Scholar’s website also denied access and its public author-search API returned a rate-limit response. Neither service was used to infer citation metrics or completeness. Bibliographic metadata was checked against the original website, author pages, ACL Anthology, arXiv, and publication venues.</p><h2 id="alumni">Alumni destinations</h2><p>The original website explicitly labels alumni placements as first employment. Those appointments are preserved as historical facts. Till Speicher’s destination is labeled current because his first appointment was not specified. Preethi Lahoti’s first destination is supported by her own dated announcement. A current appointment is added only where a public profile supports it. Graduation years have not been guessed.</p><h2>People and images</h2><p>The people page is a selected roster of researchers and co-advised students. Public profiles were used to verify roles; it is not a complete membership register. Portraits are sourced from the respective MPI-SWS or personal profile, with original URLs recorded in the repository’s asset credits. The network illustration is original and conceptual, not an empirical graph.</p><h2>Source directory</h2><ul class="source-list">'+''.join(f'<li>{link(u,e(t))}<p>{e(d)}</p></li>' for t,u,d in source_links)+'</ul></section>'
    return layout('sources','Sources & content notes','Sources and editorial notes for publication records, alumni destinations, and researcher profiles.',body)

def privacy():
    body=intro('PRIVACY','A simple website.<br><em>A clear footprint.</em>','This site serves research information and links to external resources.')+'<section class="container prose section"><h2>What this site stores</h2><p>The website does not include analytics, advertising, tracking cookies, forms, or accounts. Publication and alumni filters run in your browser. Search terms appear in the publication page URL so you can share a filtered view.</p><h2>Hosting and external links</h2><p>The hosting provider may process request information such as IP addresses and server logs. External websites have their own privacy practices. Fonts, scripts, and portraits are served with this website rather than loaded from third-party services.</p><h2>Institute information</h2><p>For institutional privacy information and contacts, see the <a href="https://data-protection.mpi-klsb.mpg.de/sws/www.mpi-sws.org">MPI-SWS data protection page</a>.</p></section>'
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
    for name,fn in [('index',home),('research',research),('publications',publications),('people',people),('alumni',alumni),('resources',resources),('contact',contact),('sources',sources),('privacy',privacy)]:
        (OUT/(name+'.html')).write_text(fn())
    (OUT/'publications.bib').write_text('\n\n'.join(bibtex(p) for p in PUBS)+'\n')
    (OUT/'assets/citations.json').write_text(json.dumps({p['id']:{'title':p['title'],'bibtex':bibtex(p)} for p in PUBS},ensure_ascii=False))
    (OUT/'.nojekyll').write_text('')
    (OUT/'404.html').write_text(layout('404','Page not found','Page not found.',intro('404','A missing connection.','This page could not be found. Use the navigation to explore our research, or return to the homepage.','<a class="button" href="index.html">Back to home →</a>')))
    print(f'Built {len(list(OUT.glob("*.html")))} pages, {len(PUBS)} publication records, {len(ALUMNI)} alumni profiles → dist/')

if __name__=='__main__': main()
