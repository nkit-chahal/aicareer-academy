
(function () {
  var toggle = document.getElementById('navToggle');
  var menu = document.getElementById('menu');
  var closeBtn = document.getElementById('menuClose');
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
  if (!toggle || !menu) return;

  function setOpen(open) {
    menu.classList.toggle('is-open', open);
    menu.setAttribute('aria-hidden', open ? 'false' : 'true');
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.style.overflow = open ? 'hidden' : '';
    if (open) {
      if (closeBtn) closeBtn.focus();
      return;
    }
    if (closeBtn) closeBtn.blur();
    if (document.activeElement && menu.contains(document.activeElement)) {
      document.activeElement.blur();
    }
    if (window.getSelection) {
      var sel = window.getSelection();
      if (sel && sel.removeAllRanges) sel.removeAllRanges();
    }
    toggle.focus();
  }

  toggle.addEventListener('click', function () {
    setOpen(!menu.classList.contains('is-open'));
  });
  if (closeBtn) {
    closeBtn.addEventListener('click', function () { setOpen(false); });
  }
  menu.addEventListener('click', function (e) {
    if (e.target.tagName === 'A') setOpen(false);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && menu.classList.contains('is-open')) setOpen(false);
  });
})();
