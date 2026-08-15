(function () {
  "use strict";

  var years = [2021, 2022, 2023, 2024, 2025, 2026, 2027];
  var actual = [100, 118, 132, 148, 167, null, null];
  var forecast = [null, null, null, null, 167, 186, 204];
  var bandLow = [null, null, null, null, 167, 176, 188];
  var bandHigh = [null, null, null, null, 167, 198, 222];
  var notes = {
    2021: "Index base year (illustrative).",
    2023: "GCC hiring accelerates in Hyderabad and NCR.",
    2025: "Last solid point before the dashed projection.",
    2026: "Projection — labelled illustrative, not a forecast you should bet a career on.",
    2027: "Beyond 2026: still climbing in this sketch, with a wide band of uncertainty."
  };

  var canvas = document.getElementById("hiringChart");
  var tooltip = document.getElementById("chartTooltip");
  var tableBody = document.getElementById("chartTableBody");
  var toggle = document.getElementById("tableToggle");
  var tableWrap = document.getElementById("chartTableWrap");
  if (!canvas) return;

  var ctx = canvas.getContext("2d");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hoverIndex = -1;
  var anim = 0;
  var points = [];

  function fillTable() {
    if (!tableBody) return;
    tableBody.innerHTML = years
      .map(function (y, i) {
        var kind = y <= 2025 ? "Observed (illustrative)" : "Projected (illustrative)";
        var val = y <= 2025 ? actual[i] : forecast[i];
        var range =
          y <= 2025 ? "—" : bandLow[i] + "–" + bandHigh[i];
        return (
          "<tr><th scope='row'>" +
          y +
          "</th><td>" +
          val +
          "</td><td>" +
          range +
          "</td><td>" +
          kind +
          "</td></tr>"
        );
      })
      .join("");
  }

  function sizeCanvas() {
    var wrap = canvas.parentElement;
    var w = wrap.clientWidth;
    var h = wrap.clientHeight || Math.round(w * 0.62);
    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.max(320, w) * dpr;
    canvas.height = Math.max(200, h) * dpr;
    canvas.style.width = w + "px";
    canvas.style.height = h + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function layout() {
    var w = canvas.clientWidth;
    var h = canvas.clientHeight;
    var pad = { t: 18, r: 18, b: 36, l: 40 };
    var innerW = w - pad.l - pad.r;
    var innerH = h - pad.t - pad.b;
    var minY = 80;
    var maxY = 240;
    points = years.map(function (year, i) {
      var x = pad.l + (i / (years.length - 1)) * innerW;
      var yVal = year <= 2025 ? actual[i] : forecast[i];
      var y = pad.t + innerH - ((yVal - minY) / (maxY - minY)) * innerH;
      var yLo = pad.t + innerH - ((bandLow[i] - minY) / (maxY - minY)) * innerH;
      var yHi = pad.t + innerH - ((bandHigh[i] - minY) / (maxY - minY)) * innerH;
      return { i: i, year: year, x: x, y: y, yLo: yLo, yHi: yHi, val: yVal };
    });
    return { w: w, h: h, pad: pad, innerW: innerW, innerH: innerH, minY: minY, maxY: maxY };
  }

  function draw() {
    var L = layout();
    ctx.clearRect(0, 0, L.w, L.h);

    ctx.strokeStyle = "rgba(26,22,18,0.12)";
    ctx.lineWidth = 1;
    ctx.font = "11px 'IBM Plex Mono', ui-monospace, monospace";
    ctx.fillStyle = "#6b5e4e";
    ctx.textAlign = "right";
    ctx.textBaseline = "middle";
    [100, 140, 180, 220].forEach(function (tick) {
      var y =
        L.pad.t +
        L.innerH -
        ((tick - L.minY) / (L.maxY - L.minY)) * L.innerH;
      ctx.beginPath();
      ctx.moveTo(L.pad.l, y);
      ctx.lineTo(L.w - L.pad.r, y);
      ctx.stroke();
      ctx.fillText(String(tick), L.pad.l - 8, y);
    });

    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    points.forEach(function (p) {
      ctx.fillText(String(p.year), p.x, L.h - L.pad.b + 10);
    });

    var t = reduceMotion ? 1 : anim;
    var reveal = points.filter(function (p) {
      return p.i / (points.length - 1) <= t + 0.02;
    });
    if (!reveal.length) return;

    var startF = points.findIndex(function (p) {
      return p.year >= 2025;
    });

    ctx.beginPath();
    var firstBand = true;
    reveal.forEach(function (p) {
      if (p.year < 2025) return;
      if (firstBand) {
        ctx.moveTo(p.x, p.yHi);
        firstBand = false;
      } else {
        ctx.lineTo(p.x, p.yHi);
      }
    });
    reveal
      .slice()
      .reverse()
      .forEach(function (p) {
        if (p.year < 2025) return;
        ctx.lineTo(p.x, p.yLo);
      });
    ctx.closePath();
    ctx.fillStyle = "rgba(154,107,47,0.18)";
    ctx.fill();

    function strokeSeries(fromYear, toYear, dashed, color) {
      ctx.beginPath();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2.25;
      ctx.setLineDash(dashed ? [7, 5] : []);
      var started = false;
      reveal.forEach(function (p) {
        if (p.year < fromYear || p.year > toYear) return;
        if (!started) {
          ctx.moveTo(p.x, p.y);
          started = true;
        } else {
          ctx.lineTo(p.x, p.y);
        }
      });
      ctx.stroke();
      ctx.setLineDash([]);
    }

    strokeSeries(2021, 2025, false, "#0f4c4a");
    if (t > startF / (points.length - 1) - 0.05) {
      strokeSeries(2025, 2027, true, "#9a6b2f");
    }

    reveal.forEach(function (p) {
      ctx.beginPath();
      ctx.fillStyle = p.year <= 2025 ? "#0f4c4a" : "#9a6b2f";
      var r = hoverIndex === p.i ? 6 : 4;
      ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
      ctx.fill();
      if (hoverIndex === p.i) {
        ctx.strokeStyle = "#1a1612";
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }
    });
  }

  function tick() {
    if (reduceMotion) {
      anim = 1;
      draw();
      return;
    }
    anim = Math.min(1, anim + 0.035);
    draw();
    if (anim < 1) requestAnimationFrame(tick);
  }

  function nearest(mx) {
    var best = 0;
    var dist = Infinity;
    points.forEach(function (p) {
      var d = Math.abs(p.x - mx);
      if (d < dist) {
        dist = d;
        best = p.i;
      }
    });
    return best;
  }

  function showTip(i, clientRect) {
    hoverIndex = i;
    draw();
    if (!tooltip) return;
    var p = points[i];
    var kind = p.year <= 2025 ? "illustrative observed" : "illustrative projection";
    tooltip.textContent = p.year + " · index " + p.val + " · " + kind;
    tooltip.classList.add("is-on");
    var left = (p.x / canvas.clientWidth) * clientRect.width;
    var top = (p.y / canvas.clientHeight) * clientRect.height;
    tooltip.style.left = left + "px";
    tooltip.style.top = top + "px";
  }

  function hideTip() {
    hoverIndex = -1;
    draw();
    if (tooltip) tooltip.classList.remove("is-on");
  }

  canvas.addEventListener("mousemove", function (e) {
    var r = canvas.getBoundingClientRect();
    var mx = e.clientX - r.left;
    showTip(nearest(mx), r);
  });

  canvas.addEventListener("mouseleave", hideTip);

  canvas.addEventListener("click", function (e) {
    var r = canvas.getBoundingClientRect();
    showTip(nearest(e.clientX - r.left), r);
  });

  canvas.addEventListener("keydown", function (e) {
    if (e.key === "ArrowRight") {
      e.preventDefault();
      showTip(Math.min(years.length - 1, (hoverIndex < 0 ? 0 : hoverIndex + 1)), canvas.getBoundingClientRect());
    }
    if (e.key === "ArrowLeft") {
      e.preventDefault();
      showTip(Math.max(0, (hoverIndex < 0 ? 0 : hoverIndex - 1)), canvas.getBoundingClientRect());
    }
    if (e.key === "Escape") hideTip();
  });

  if (toggle && tableWrap) {
    toggle.addEventListener("click", function () {
      var open = tableWrap.hidden;
      tableWrap.hidden = !open;
      toggle.setAttribute("aria-expanded", String(open));
      toggle.textContent = open ? "Hide data table" : "Show data table";
    });
  }

  fillTable();
  sizeCanvas();
  requestAnimationFrame(tick);

  var resizeTimer;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      sizeCanvas();
      draw();
    }, 120);
  });
})();
