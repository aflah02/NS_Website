'use strict';

// All content is rendered at build time. JavaScript only adds local interactions.
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const normalize = value => value.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase();
const menuButton = $('.menu-toggle');
const navigation = $('#site-nav');
const closeMenu = () => { navigation.classList.remove('open'); menuButton.setAttribute('aria-expanded', 'false'); menuButton.setAttribute('aria-label', 'Open navigation'); };
menuButton.addEventListener('click', () => {
  const open = !navigation.classList.contains('open');
  navigation.classList.toggle('open', open);
  menuButton.setAttribute('aria-expanded', String(open));
  menuButton.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
});
navigation.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
document.addEventListener('keydown', event => { if (event.key === 'Escape' && navigation.classList.contains('open')) { closeMenu(); menuButton.focus(); } });

if ($('#publication-filters')) {
  const search = $('#publication-search'), year = $('#year-filter'), type = $('#type-filter');
  const papers = $$('[data-paper]'), chips = $$('[data-topic]');
  let topic = 'all';
  const params = new URLSearchParams(location.search);
  search.value = params.get('q') || '';
  if ($$('option', year).some(o => o.value === params.get('year'))) year.value = params.get('year');
  if ($$('option', type).some(o => o.value === params.get('type'))) type.value = params.get('type');
  if (chips.some(c => c.dataset.topic === params.get('topic'))) topic = params.get('topic');

  function filter(updateUrl = true) {
    const query = normalize(search.value.trim());
    let count = 0;
    for (const paper of papers) {
      const visible = (!query || normalize(paper.dataset.search).includes(query)) &&
        (year.value === 'all' || paper.dataset.year === year.value) &&
        (type.value === 'all' || paper.dataset.status === type.value) &&
        (topic === 'all' || paper.dataset.topics.split(' ').includes(topic));
      paper.hidden = !visible;
      if (visible) count++;
    }
    for (const group of $$('[data-year-group]')) group.hidden = !$$('[data-paper]', group).some(p => !p.hidden);
    for (const chip of chips) { chip.classList.toggle('active', chip.dataset.topic === topic); chip.setAttribute('aria-pressed', String(chip.dataset.topic === topic)); }
    $('#publication-count').textContent = `${count} publication${count === 1 ? '' : 's'}`;
    $('#no-publications').hidden = count !== 0;
    if (updateUrl) {
      const url = new URL(location.href);
      for (const [key, value] of [['q', search.value.trim()], ['year', year.value], ['type', type.value], ['topic', topic]]) {
        if (value && value !== 'all') url.searchParams.set(key, value); else url.searchParams.delete(key);
      }
      history.replaceState(null, '', url.pathname + url.search + url.hash);
    }
  }
  const reset = () => { search.value = ''; year.value = type.value = topic = 'all'; filter(); search.focus(); };
  $('#publication-filters').addEventListener('submit', event => event.preventDefault());
  search.addEventListener('input', () => filter());
  year.addEventListener('change', () => filter());
  type.addEventListener('change', () => filter());
  for (const chip of chips) chip.addEventListener('click', event => { event.preventDefault(); topic = chip.dataset.topic; filter(); });
  $('#clear-filters').addEventListener('click', reset);
  $('[data-reset-publications]').addEventListener('click', reset);
  filter(false);

  const dialog = $('#citation-dialog');
  let citations;
  document.addEventListener('click', async event => {
    const button = event.target.closest('[data-cite]');
    if (!button) return;
    button.disabled = true;
    try {
      if (!citations) {
        const response = await fetch('assets/citations.json');
        if (!response.ok) throw new Error('Citation data could not be loaded.');
        citations = await response.json();
      }
      const citation = citations[button.dataset.cite];
      if (!citation) throw new Error('Citation not found.');
      $('#citation-paper-title').textContent = citation.title;
      $('#citation-text').value = citation.bibtex;
      $('#copy-status').textContent = '';
      $('#copy-citation').textContent = 'Copy BibTeX';
      dialog.showModal();
    } catch {
      $('#action-status').textContent = 'Citation unavailable. Please use the Download bibliography link at the top of this page.';
      button.textContent = 'Use bibliography download';
    } finally { button.disabled = false; }
  });
  $('.dialog-close', dialog).addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } });
  $('#copy-citation').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText($('#citation-text').value); $('#copy-status').textContent = 'Copied to clipboard.'; }
    catch { $('#citation-text').focus(); $('#citation-text').select(); $('#copy-status').textContent = 'Select and copy the citation using your keyboard.'; }
  });
}

if ($('#alumni-filters')) {
  const search = $('#alumni-search'), kind = $('#alumni-kind'), alumni = $$('[data-alumnus]');
  function filterAlumni() {
    const query = normalize(search.value.trim()); let count = 0;
    for (const person of alumni) {
      const visible = (!query || normalize(person.dataset.search).includes(query)) && (kind.value === 'all' || person.dataset.kind === kind.value);
      person.hidden = !visible; if (visible) count++;
    }
    $('#alumni-count').textContent = `${count} alumn${count === 1 ? 'us' : 'i'}`;
    $('#no-alumni').hidden = count !== 0;
  }
  $('#alumni-filters').addEventListener('submit', event => event.preventDefault());
  search.addEventListener('input', filterAlumni); kind.addEventListener('change', filterAlumni);
  $('#reset-alumni').addEventListener('click', () => { search.value = ''; kind.value = 'all'; filterAlumni(); search.focus(); });
}
