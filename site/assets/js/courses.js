const TOTAL = 17;

function applyFilter(filter) {
  var cards = document.querySelectorAll('.card');
  var visible = 0;
  cards.forEach(function(card) {
    var tags = card.dataset.tags.split(',');
    var show = filter === 'all' || tags.indexOf(filter) !== -1;
    card.classList.toggle('hidden', !show);
    if (show) visible++;
  });
  ['featuredSection', 'moreSection'].forEach(function(id) {
    var grid = document.getElementById(id).querySelector('.grid');
    var visibleInSection = grid.querySelectorAll('.card:not(.hidden)').length;
    var existing = grid.querySelector('.empty-state');
    if (visibleInSection === 0) {
      if (!existing) {
        var tpl = document.getElementById('emptyTpl');
        grid.appendChild(tpl.content.cloneNode(true));
      }
    } else if (existing) {
      existing.remove();
    }
  });
  document.getElementById('showingCount').textContent =
    filter === 'all' ? 'Showing all ' + TOTAL + ' programs' : 'Showing ' + visible + ' of ' + TOTAL + ' programs';
}

document.querySelectorAll('.filter-pill').forEach(function(pill) {
  pill.addEventListener('click', function() {
    document.querySelectorAll('.filter-pill').forEach(function(p) {
      p.classList.remove('active');
      p.setAttribute('aria-selected', 'false');
    });
    pill.classList.add('active');
    pill.setAttribute('aria-selected', 'true');
    applyFilter(pill.dataset.filter);
  });
});
