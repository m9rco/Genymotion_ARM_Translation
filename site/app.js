(() => {
  const toolbar = document.getElementById('toolbar');
  const search = document.getElementById('search');
  const cards = [...document.querySelectorAll('.package-card')];
  const filters = [...document.querySelectorAll('[data-filter]')];
  let selected = 'all';
  function apply() {
    const term = search.value.trim().toLowerCase();
    let visible = 0;
    for (const card of cards) {
      const matches = (selected === 'all' || card.dataset.kind === selected) && card.dataset.search.toLowerCase().includes(term);
      card.hidden = !matches;
      if (matches) visible++;
    }
    document.querySelectorAll('[data-section]').forEach(section => {
      section.hidden = ![...section.querySelectorAll('.package-card')].some(card => !card.hidden);
    });
    document.getElementById('empty').hidden = visible !== 0;
    document.getElementById('search-status').textContent = `显示 ${visible} 个包`;
  }
  toolbar.hidden = false;
  search.addEventListener('input', apply);
  filters.forEach(button => button.addEventListener('click', () => {
    selected = button.dataset.filter;
    filters.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    apply();
  }));
  let timeout;
  document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(button.dataset.copy);
      const toast = document.getElementById('toast');
      toast.hidden = false;
      clearTimeout(timeout);
      timeout = setTimeout(() => { toast.hidden = true; }, 2200);
    } catch {
      button.textContent = '请选中上方校验值复制';
    }
  }));
  apply();
})();
