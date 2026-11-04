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
}
