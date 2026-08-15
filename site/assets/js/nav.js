
(function () {
  var toggle = document.getElementById('navToggle');
  var nav = document.getElementById('nav');
  var header = document.getElementById('header');
  var year = document.getElementById('year');
  var explore = document.getElementById('navExplore');
  var exploreBtn = document.getElementById('exploreToggle');
  if (year) year.textContent = new Date().getFullYear();
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    nav.querySelectorAll('a').forEach(function (link) {
      link.addEventListener('click', function () {
        nav.classList.remove('open');
        toggle.setAttribute('aria-expanded', 'false');
        if (explore) {
          explore.classList.remove('open');
          if (exploreBtn) exploreBtn.setAttribute('aria-expanded', 'false');
        }
      });
    });
  }
  if (explore && exploreBtn) {
    exploreBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = explore.classList.toggle('open');
      exploreBtn.setAttribute('aria-expanded', String(open));
    });
    document.addEventListener('click', function (e) {
      if (!explore.contains(e.target)) {
        explore.classList.remove('open');
        exploreBtn.setAttribute('aria-expanded', 'false');
      }
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        explore.classList.remove('open');
        exploreBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }
  if (header) {
    window.addEventListener('scroll', function () {
      header.classList.toggle('scrolled', window.scrollY > 8);
    }, { passive: true });
  }
})();
