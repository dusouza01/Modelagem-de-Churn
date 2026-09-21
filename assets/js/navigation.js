(() => {
  if (window.churnNavigationCleanup) window.churnNavigationCleanup();
  const root = document.querySelector('[data-testid="stMain"]');
  const links = [...document.querySelectorAll('.main-nav a[href^="#"]')];
  const update = (id) => links.forEach(link => {
    if (link.getAttribute('href') === '#' + id) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => { if (entry.isIntersecting) update(entry.target.id); });
  }, { root, rootMargin: '-10% 0px -55% 0px', threshold: 0 });
  const observe = () => ['inicio', 'carteira', 'graficos', 'insights', 'dados'].forEach(id => {
    const element = document.getElementById(id);
    if (element) observer.observe(element);
  });
  observe();
  // Streamlit streams the remaining sections after this component mounts.
  const mutations = new MutationObserver(observe);
  mutations.observe(root || document.body, {childList: true, subtree: true});
  const click = event => {
    const link = event.target.closest('.main-nav a, .hero-actions a');
    if (!link) return;
    const target = document.querySelector(link.getAttribute('href'));
    if (!target) return;
    event.preventDefault();
    target.scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start'});
    update(target.id);
  };
  document.addEventListener('click', click);
  window.churnNavigationCleanup = () => {
    observer.disconnect(); mutations.disconnect(); document.removeEventListener('click', click);
  };
})();
