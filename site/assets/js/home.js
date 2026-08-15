
(function () {
  var stage = document.querySelector('.chart-stage');
  var listbox = document.querySelector('.lanes');
  var towers = Array.prototype.slice.call(document.querySelectorAll('.lane'));
  var readoutTitle = document.getElementById('readoutTitle');
  var readoutBody = document.getElementById('readoutBody');
  if (!towers.length) return;

  var facts = {
    ds: {
      title: 'Data scientists · U.S. BLS +33.5%',
      body: 'U.S. BLS (not MoSPI/PLFS, not Indian CTC) projects data scientist employment to grow 33.5% from 2024 to 2034 — among the fastest of all occupations, versus 3.1% for all jobs. We show it as a published international benchmark because India has no matching official occupation series. Not a placement promise. If this is the job you want, we map Excel/SQL/Python into a live program.'
    },
    sec: {
      title: 'Information security analysts · U.S. BLS +28.5%',
      body: 'U.S. BLS: +28.5% employment change, 2024–34 — an international benchmark, not an Indian official occupation rate. Security is not our core catalog, but production AI work still needs people who can think about access, logs, and failure. A career call will say so if another path fits better.'
    },
    rs: {
      title: 'Computer & information research scientists · U.S. BLS +19.7%',
      body: 'U.S. BLS: +19.7%, 2024–34. Not Indian CTC and not a placement rate. Research-scientist titles usually want a deeper academic track than a 3–6 month cohort. We still teach the engineering stack used next to that work — models, evaluation, shipping.'
    },
    sw: {
      title: 'Software developers · U.S. BLS +16%',
      body: 'U.S. BLS: software developers +16% (2024–34); the broader developers / QA / testers group is +15%. This is a U.S. labour forecast shown for Indian learners as a published benchmark, not an Indian salary table. Developers who can work with data, APIs, and LLMs are the people companies actually interview. That is the sequence we teach.'
    },
    all: {
      title: 'All occupations · U.S. BLS +3.1%',
      body: 'The short bar is the U.S. BLS all-occupations average. AI-adjacent roles sit far above it in this table. India does not publish an equivalent official occupation-level series — so we refuse to invent one. Book a call if you want a role map, not a slogan.'
    }
  };

  function selectTower(btn, focus) {
    towers.forEach(function (t) {
      t.classList.toggle('is-on', t === btn);
      t.setAttribute('aria-selected', t === btn ? 'true' : 'false');
    });
    var fact = facts[btn.getAttribute('data-id')];
    if (fact && readoutTitle && readoutBody) {
      readoutTitle.textContent = fact.title;
      readoutBody.textContent = fact.body;
    }
    if (listbox) listbox.setAttribute('aria-activedescendant', btn.id);
    if (focus) btn.focus();
  }

  towers.forEach(function (btn, i) {
    btn.addEventListener('click', function () { selectTower(btn, false); });
    btn.addEventListener('keydown', function (e) {
      var next = i;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') next = (i + 1) % towers.length;
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') next = (i - 1 + towers.length) % towers.length;
      else return;
      e.preventDefault();
      selectTower(towers[next], true);
    });
  });

  function draw() {
    if (stage) stage.classList.add('is-drawn');
  }

  if (!stage) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    draw();
    return;
  }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          draw();
          io.disconnect();
        }
      });
    }, { threshold: 0.25 });
    io.observe(stage);
  } else {
    draw();
  }
})();

(function () {
  var boards = Array.prototype.slice.call(document.querySelectorAll('#market-shift .js-reveal'));
  if (!boards.length) return;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function formatCount(el, value) {
    var suf = el.getAttribute('data-suf') || '';
    var pre = el.getAttribute('data-pre') || '';
    var decimals = String(el.getAttribute('data-to') || '').indexOf('.') >= 0 ? 1 : 0;
    el.textContent = pre + value.toFixed(decimals) + suf;
  }

  function countUp(el) {
    if (el.getAttribute('data-done') === '1') return;
    el.setAttribute('data-done', '1');
    var to = parseFloat(el.getAttribute('data-to') || '0');
    if (reduce) {
      formatCount(el, to);
      return;
    }
    var start = performance.now();
    var dur = 900;
    function tick(now) {
      var t = Math.min(1, (now - start) / dur);
      var eased = 1 - Math.pow(1 - t, 3);
      formatCount(el, to * eased);
      if (t < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  function activate(board) {
    if (board.classList.contains('is-in')) return;
    board.classList.add('is-in');
    Array.prototype.forEach.call(board.querySelectorAll('.js-count'), countUp);
  }

  if (reduce || !('IntersectionObserver' in window)) {
    boards.forEach(activate);
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        activate(entry.target);
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.28, rootMargin: '0px 0px -8% 0px' });
  boards.forEach(function (b) { io.observe(b); });
})();
