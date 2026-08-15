
(function () {
  var tabs = document.querySelectorAll('.path-tab');
  var panels = document.querySelectorAll('.path-panel');
  var picks = document.querySelectorAll('.path-pick');
  var hubs = document.querySelectorAll('.hub-node');
  if (!tabs.length) return;

  function activate(id, updateHash, scroll) {
    tabs.forEach(function (tab) {
      var on = tab.getAttribute('data-path') === id;
      tab.classList.toggle('is-active', on);
      tab.setAttribute('aria-selected', on ? 'true' : 'false');
    });
    panels.forEach(function (panel) {
      var on = panel.getAttribute('data-path') === id;
      panel.classList.toggle('is-active', on);
      if (on) {
        panel.removeAttribute('hidden');
        panel.classList.remove('is-enter');
        void panel.offsetWidth;
        panel.classList.add('is-enter');
      } else {
        panel.setAttribute('hidden', '');
        panel.classList.remove('is-enter');
      }
    });
    picks.forEach(function (el) {
      el.classList.toggle('is-active', el.getAttribute('data-path') === id);
    });
    hubs.forEach(function (el) {
      el.classList.toggle('is-active', el.getAttribute('data-path') === id);
    });
    if (updateHash) {
      history.replaceState(null, '', '#path=' + id);
    }
    if (scroll) {
      var detail = document.getElementById('path-detail');
      if (detail) detail.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  function bind(nodes, shouldScroll) {
    nodes.forEach(function (el) {
      el.addEventListener('click', function () {
        activate(el.getAttribute('data-path'), true, shouldScroll);
      });
    });
  }

  bind(tabs, false);
  bind(picks, true);
  bind(hubs, true);

  var hash = window.location.hash || '';
  var match = hash.match(/path=([a-z0-9-]+)/);
  if (match) {
    var exists = Array.prototype.some.call(tabs, function (t) {
      return t.getAttribute('data-path') === match[1];
    });
    if (exists) activate(match[1], false, false);
  }
})();
