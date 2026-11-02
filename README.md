# Networked Systems Research Group

A portable research-group website for Krishna P. Gummadi’s group at the Max Planck Institute for Software Systems. It connects the group’s historical systems and social-computing research with recent work on AI and language models.

## Preview locally

Python 3.10 or newer is the only build requirement. There are no packages to install, runtime services, analytics, external font requests, or API keys.

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8000 --directory dist
```

Open http://localhost:8000. Open the site through a web server so the citation dialog can load its local JSON file.

## Deploy on GitHub Pages

1. Merge the website pull request into `main`.
2. In **Settings → Pages → Build and deployment**, choose **GitHub Actions** as the source.
3. Run **Build and deploy research website** from the Actions tab, or push a subsequent content update to `main`.

The included workflow builds and checks pull requests without deploying them. Pushes to `main` and manual runs build and deploy the `dist/` artifact using GitHub’s official Pages actions. Set Pages up before expecting the deployment job to succeed; rerun the workflow after changing its settings. For a private repository, GitHub Pages requires a plan that supports Pages from private repositories. The repository’s visibility is not changed by this project.

All links are relative: the site works under `/NS_Website/`, on an MPI server, or on a custom domain. There is no hardcoded hostname. To use another static host, upload the **contents** of `dist/` after building. The generated site has no server-side dependencies. Configure the host to serve `404.html` for missing pages if supported.

## What is included

- Home, Research, Publications, People, Alumni, Resources, Contact, Sources, and Privacy pages, plus a 404 page.
- 122 sourced publication records from 2000–2026, with title/author/venue search, research-area filters, year filters, publication-type filters, shareable filter URLs, citation dialogs, clipboard copy, and a downloadable BibTeX bibliography.
- A dedicated searchable alumni page with 17 profiles, first post-MPI destinations, source links, and explicit labels where a destination is current rather than first.
- A numbered navigation rail, self-hosted IBM Plex typography, paper-led overview, local portraits, keyboard focus states, reduced-motion support, semantic HTML, and content that remains readable without JavaScript.
- A dependency-free static generator and validation command, with GitHub Actions integration.

## Edit the content

| Content | File |
| --- | --- |
| Publications and paper links | `content/publications.json` |
| People, roles, profiles, and portrait filenames | `content/people.json` |
| Alumni destinations and supporting sources | `content/alumni.json` |
| Research areas and topic labels | `content/research.json` |
| Software and data resources | `content/resources.json` |
| Page structure and shared components | `scripts/build.py` |
| Styling and responsive layout | `assets/style.css` |
| Browser interactions | `assets/app.js` |

After editing, run the build and check commands. `dist/` is generated and intentionally untracked. Research-area IDs are `ai`, `fairness`, `social`, `privacy`, and `systems`. Publication IDs must be unique and stable. Use `published`, `accepted`, or `preprint` for publication status; use `arXiv` as the venue for preprints. Add a `source` URL for every paper, person, and alumni placement.

For an alumnus, set `destinationType` to `First destination` only when the source explicitly supports that interpretation. Otherwise use `Current destination`. Add a verified current role in `current` and its source in `currentSource` if desired. Do not infer graduation dates or current employment from old first-placement records.

## Content provenance and scope

See [docs/content-sources.md](docs/content-sources.md) and [docs/asset-credits.md](docs/asset-credits.md). Historical publication entries come from Krishna’s original bibliography; recent additions were checked against research-author pages and publication venues. This is a curated archive, not a claim of bibliographic completeness. The people page is a selected roster, including co-advised students, rather than a membership register.

Google Scholar denied automated access. Semantic Scholar’s website denied access and its public author-search API returned HTTP 429. No citation counts or rankings have been inferred from those sources. The site links to both services for readers.

## Verification

`scripts/check.py` checks all generated local links, anchors, and assets; page semantics; source fields; research topics; preprint labels; unique publication IDs; citation coverage; portrait availability; and alumni destination labels. JavaScript syntax can additionally be checked with `node --check assets/app.js` when Node is installed.

The managed preview service was unavailable in the build environment. Browser rendering and interactive behavior still need a visual review after opening the local preview; no browser QA result is claimed.
