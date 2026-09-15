/* All content is present in HTML. Navigation and reading also work without JS. */
(() => {
  'use strict';
  document.body.classList.add('enhanced');
  const iconize = () => window.lucide?.createIcons();
  iconize();

  const menu = document.querySelector('[data-menu-toggle]');
  const navigation = document.querySelector('#navigation');
  menu.hidden = false;
  const closeMenu = () => {
    navigation.classList.remove('is-open');
    menu.setAttribute('aria-expanded', 'false');
    menu.setAttribute('aria-label', 'Open navigation');
  };
  menu.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    navigation.classList.toggle('is-open', open);
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') {
      closeMenu();
      menu.focus();
    }
  });
  document.addEventListener('click', event => {
    if (!event.target.closest('.navigation-tools')) closeMenu();
  });
  window.matchMedia('(min-width: 801px)').addEventListener('change', closeMenu);

  const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  const words = query => normalize(query).trim().split(/\s+/).filter(Boolean);
  const matches = (value, query) => query.every(word => normalize(value).includes(word));
  const papers = [...document.querySelectorAll('.publication')];
  if (papers.length) {
    document.querySelector('.publication-tools').hidden = false;
    const form = document.querySelector('.paper-filters');
    const query = document.querySelector('#paper-query');
    const year = document.querySelector('#paper-year');
    const filter = () => {
      let count = 0;
      const terms = words(query.value);
      for (const paper of papers) {
        const visible = (!year.value || paper.dataset.year === year.value) && matches(paper.textContent, terms);
        paper.hidden = !visible;
        if (visible) count++;
      }
      document.querySelector('.paper-count').textContent = `${count} ${count === 1 ? 'entry' : 'entries'}`;
      document.querySelector('.no-papers').hidden = count !== 0;
    };
    query.addEventListener('input', filter);
    year.addEventListener('change', filter);
    form.addEventListener('submit', event => event.preventDefault());
    form.addEventListener('reset', () => setTimeout(filter, 0));
    window.addEventListener('hashchange', () => { form.reset(); });
  }

  const dialog = document.querySelector('.search-dialog');
  const searchButton = document.querySelector('[data-search-open]');
  const query = document.querySelector('#site-query');
  const results = document.querySelector('.search-results');
  const status = document.querySelector('.search-status');
  const prefix = document.body.dataset.prefix;
  searchButton.hidden = false;
  const search = () => {
    results.replaceChildren();
    const terms = words(query.value);
    if (!terms.length) { status.textContent = ''; return; }
    const found = (window.SITE_SEARCH || []).filter(item => matches(item.title + ' ' + item.text, terms));
    status.textContent = found.length ? `${found.length} ${found.length === 1 ? 'result' : 'results'}` : 'No results found.';
    for (const item of found) {
      const li = document.createElement('li');
      const section = document.createElement('small');
      section.textContent = item.section;
      const link = document.createElement('a');
      link.href = prefix + item.url;
      link.textContent = item.title;
      link.addEventListener('click', () => {
        document.querySelector('.paper-filters')?.reset();
        dialog.close();
      });
      const excerpt = document.createElement('p');
      excerpt.textContent = item.text.length > 220 ? item.text.slice(0, 217) + '...' : item.text;
      li.append(section, link, excerpt);
      results.append(li);
    }
  };
  searchButton.addEventListener('click', () => { closeMenu(); dialog.showModal(); query.focus(); });
  document.querySelector('[data-search-close]').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    if (event.target === dialog) {
      const box = dialog.getBoundingClientRect();
      if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) dialog.close();
    }
  });
  query.addEventListener('input', search);
  document.querySelector('.site-search').addEventListener('submit', event => { event.preventDefault(); search(); });
})();
