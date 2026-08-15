(function () {
  var canvas = document.getElementById("gridCanvas");
  var field = document.querySelector(".playfield");
  if (!canvas || !field) return;

  var ctx = canvas.getContext("2d");
  var CELL = 28;
  var palette = ["#c5d4e8", "#f3e2a7", "#e8b6a8", "#b9d0b8", "#b7b7b7", "#9eb6d4"];
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var cols = 0;
  var rows = 0;
  var cells = [];
  var t0 = performance.now();

  function seedKey(c, r) {
    return (c * 92821 + r * 1327) % 97;
  }

  function rebuild() {
    var rect = field.getBoundingClientRect();
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.floor(rect.width * dpr);
    canvas.height = Math.floor(rect.height * dpr);
    canvas.style.width = rect.width + "px";
    canvas.style.height = rect.height + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    cols = Math.ceil(rect.width / CELL) + 1;
    rows = Math.ceil(rect.height / CELL) + 1;
    cells = [];
    var c, r, k;
    for (r = 0; r < rows; r++) {
      for (c = 0; c < cols; c++) {
        k = seedKey(c, r);
        cells.push({
          c: c, r: r,
          color: k < 8 ? palette[k % palette.length] : null,
          phase: (c * 0.35 + r * 0.22) % (Math.PI * 2),
          lift: 0,
          heat: k < 8 ? 0.35 : 0
        });
      }
    }
  }

  function paintAt(x, y) {
    var c = Math.floor(x / CELL);
    var r = Math.floor(y / CELL);
    var rad = 3, dc, dr, idx, cell, dist;
    for (dr = -rad; dr <= rad; dr++) {
      for (dc = -rad; dc <= rad; dc++) {
        dist = Math.hypot(dc, dr);
        if (dist > rad) continue;
        idx = (r + dr) * cols + (c + dc);
        cell = cells[idx];
        if (!cell) continue;
        cell.heat = Math.max(cell.heat, 1 - dist / (rad + 0.2));
        if (!cell.color) cell.color = palette[(c + dc + r + dr + 3) % palette.length];
        cell.lift = Math.max(cell.lift, (1 - dist / rad) * 14);
      }
    }
  }

  function tick(now) {
    var w = canvas.clientWidth;
    var h = canvas.clientHeight;
    var i, cell, bob, x, y;
    ctx.clearRect(0, 0, w, h);
    ctx.strokeStyle = "#ececec";
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (x = 0; x <= w; x += CELL) { ctx.moveTo(x + 0.5, 0); ctx.lineTo(x + 0.5, h); }
    for (y = 0; y <= h; y += CELL) { ctx.moveTo(0, y + 0.5); ctx.lineTo(w, y + 0.5); }
    ctx.stroke();
    for (i = 0; i < cells.length; i++) {
      cell = cells[i];
      if (!reduce) {
        bob = Math.sin((now - t0) / 520 + cell.phase) * (cell.color ? 6 : 0);
        cell.lift += (bob - cell.lift) * 0.08;
        if (seedKey(cell.c, cell.r) >= 8) {
          cell.heat *= 0.982;
          if (cell.heat < 0.04) { cell.color = null; cell.heat = 0; }
        }
      }
      if (!cell.color) continue;
      ctx.globalAlpha = 0.35 + cell.heat * 0.65;
      ctx.fillStyle = cell.color;
      ctx.fillRect(cell.c * CELL + 1, cell.r * CELL + 1 + (reduce ? 0 : -cell.lift), CELL - 2, CELL - 2);
    }
    ctx.globalAlpha = 1;
    requestAnimationFrame(tick);
  }

  field.addEventListener("pointermove", function (e) {
    var rect = canvas.getBoundingClientRect();
    paintAt(e.clientX - rect.left, e.clientY - rect.top);
  });
  window.addEventListener("resize", rebuild);
  rebuild();
  requestAnimationFrame(tick);
})();
