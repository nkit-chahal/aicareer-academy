(function () {
  "use strict";

  var YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028];
  var LAST_OBS = 2026;

  /* Illustrative relative demand index (2018 analytics ≈ 100). Not ACA counts. */
  var SERIES = {
    an: {
      name: "Analytics roles",
      style: "dashed",
      values: [100, 112, 124, 142, 158, 170, 180, 190, 198, 206, 212]
    },
    ds: {
      name: "Data science titles",
      style: "solid",
      values: [78, 102, 128, 168, 205, 192, 208, 222, 234, 246, 256]
    },
    ai: {
      name: "AI / ML / GenAI titles",
      style: "solid-accent",
      values: [36, 48, 62, 88, 128, 215, 292, 348, 392, 428, 452]
    }
  };

  var STEPS = {
    0: { focus: ["an", "ds", "ai"], year: null, label: "" },
    1: { focus: ["an", "ds"], year: 2018, label: "2018 · floor" },
    2: { focus: ["an", "ds"], year: 2021, label: "2021 · digital hiring" },
    3: { focus: ["ai"], year: 2023, label: "2023 · GenAI titles" },
    4: { focus: ["an", "ds", "ai"], year: 2026, label: "2026 · now" },
    5: { focus: ["an", "ds", "ai"], year: 2028, label: "2028 · projection" }
  };

  var JOBS = {
    "data-analyst": {
      title: "Data Analyst",
      time: "About 5–6 months",
      lead: "Best for beginners, business grads, and a first role in data. Volume hiring still lives here — the green line on the chart.",
      steps: [
        ["Python + spreadsheets", "Pandas, Excel, and clean data habits. Load a CSV and answer a business question."],
        ["SQL", "Joins, aggregations, window functions. Most analyst interviews live here."],
        ["BI dashboards", "Power BI or similar: KPIs, filters, and a story a manager can scan in 30 seconds."],
        ["Stats for business", "Averages, trends, A/B intuition — enough not to get fooled by a chart."],
        ["AI-assisted analysis", "Use AI to speed cleaning and commentary, then ship a portfolio dashboard."]
      ],
      href: "../../courses/data-analytics-course-with-placement/index.html",
      cta: "Open Data Analytics"
    },
    "data-scientist": {
      title: "Data Scientist",
      time: "About 6–8 months",
      lead: "Python, models, and experiments — not just dashboards. The black line: titles grew fast, then split toward specialist AI roles.",
      steps: [
        ["Python foundation", "Every path starts here. Syntax, data, and how to think in code."],
        ["Statistics & EDA", "Distributions, leakage, and experiments you can explain to a reviewer."],
        ["Classical ML", "Features, training, and evaluation you can defend — not a leaderboard screenshot."],
        ["Deep learning taste", "Enough neural nets to know when they help, and when they do not."],
        ["Portfolio study", "One end-to-end problem with a write-up, not ten unfinished notebooks."]
      ],
      href: "../../courses/data-science-course/index.html",
      cta: "Open Data Science"
    },
    "ml-engineer": {
      title: "ML Engineer",
      time: "About 5–7 months",
      lead: "Take models out of notebooks and into production. This is where the AI line meets systems work.",
      steps: [
        ["Python engineering", "Packages, tests, typing. Treat model code like product code."],
        ["Classical ML depth", "Feature pipelines, training loops, evaluation you can defend in review."],
        ["Serving", "APIs, batch jobs, latency vs throughput. A model nobody can call is a hobby."],
        ["MLOps layer", "Version data and models, CI for training, monitoring drift."],
        ["Ship a system", "One project from dataset to trained artifact to endpoint with logs."]
      ],
      href: "../../courses/machine-learning-course/index.html",
      cta: "Open Machine Learning"
    },
    "llm-engineer": {
      title: "LLM Engineer",
      time: "About 2–5 months",
      lead: "Embeddings, RAG, evals, and inference that actually scales. The steep part of the red line after 2022.",
      steps: [
        ["Python + APIs", "Call models cleanly. Handle tokens, retries, and cost."],
        ["Embeddings & retrieval", "Chunking, vector search, why RAG fails in production."],
        ["Fine-tuning & PEFT", "When to fine-tune vs prompt vs retrieve. Measure, don’t guess."],
        ["Evals", "Golden sets, hallucination checks, latency/cost tradeoffs."],
        ["Serve", "Batching, caching, safety filters. Optional next: LLMOps."]
      ],
      href: "../../courses/large-language-model-course/index.html",
      cta: "Open LLM course"
    },
    devops: {
      title: "MLOps Engineer",
      time: "About 4–6 months",
      lead: "Pipelines, containers, and reliability. The chart’s projection is not “more notebooks” — it is production.",
      steps: [
        ["Python + Linux basics", "Scripts, env management, enough Python to debug a training job."],
        ["Containers", "Docker images that train and serve. Repeatable on another machine."],
        ["CI/CD for models", "Tests on data contracts, gated deploys, rollback when a model is worse."],
        ["Orchestration", "Kubernetes or equivalent: health checks, scaling, secrets."],
        ["Observe & govern", "Metrics, cost, drift. Then LLMOps if you are running GenAI."]
      ],
      href: "../../courses/mlops-course/index.html",
      cta: "Open MLOps"
    }
  };

  var state = {
    step: 0,
    visible: { an: true, ds: true, ai: true },
    reduce: window.matchMedia("(prefers-reduced-motion: reduce)").matches
  };

  /* ── Chart ── */
  var svg = document.getElementById("demand-chart");
  var tooltip = document.getElementById("chart-tooltip");
  var hoverLine = document.getElementById("hover-line");
  if (svg) {
    drawChart();
    bindChartHover();
    window.addEventListener("resize", debounce(drawChart, 160));
  }

  function chartBox() {
    var w = svg.clientWidth || 720;
    var h = svg.clientHeight || 420;
    return { w: w, h: h, l: 48, r: 18, t: 16, b: 36 };
  }

  function scales(box) {
    var maxV = 480;
    var minV = 0;
    var x0 = box.l;
    var x1 = box.w - box.r;
    var y0 = box.h - box.b;
    var y1 = box.t;
    function x(year) {
      return x0 + ((year - 2018) / (2028 - 2018)) * (x1 - x0);
    }
    function y(v) {
      return y0 - ((v - minV) / (maxV - minV)) * (y0 - y1);
    }
    return { x: x, y: y, x0: x0, x1: x1, y0: y0, y1: y1 };
  }

  function pathFor(key, fromYear, toYear, sc) {
    var vals = SERIES[key].values;
    var d = "";
    YEARS.forEach(function (yr, i) {
      if (yr < fromYear || yr > toYear) return;
      var cmd = d ? " L " : "M ";
      d += cmd + sc.x(yr) + " " + sc.y(vals[i]);
    });
    return d;
  }

  function bandPath(key, sc) {
    var vals = SERIES[key].values;
    var i0 = YEARS.indexOf(LAST_OBS);
    var up = "";
    var down = "";
    for (var i = i0; i < YEARS.length; i++) {
      var lo = vals[i] * 0.9;
      var hi = vals[i] * 1.08;
      up += (i === i0 ? "M " : " L ") + sc.x(YEARS[i]) + " " + sc.y(hi);
      down = sc.x(YEARS[i]) + " " + sc.y(lo) + (down ? " L " + down : "");
    }
    return up + " L " + down + " Z";
  }

  function drawChart() {
    var box = chartBox();
    svg.setAttribute("viewBox", "0 0 " + box.w + " " + box.h);
    var sc = scales(box);
    var ns = "http://www.w3.org/2000/svg";

    var grid = svg.querySelector(".grid");
    grid.innerHTML = "";
    [0, 100, 200, 300, 400].forEach(function (v) {
      var line = document.createElementNS(ns, "line");
      line.setAttribute("x1", sc.x0);
      line.setAttribute("x2", sc.x1);
      line.setAttribute("y1", sc.y(v));
      line.setAttribute("y2", sc.y(v));
      grid.appendChild(line);
      var t = document.createElementNS(ns, "text");
      t.setAttribute("class", "tick-label");
      t.setAttribute("x", sc.x0 - 8);
      t.setAttribute("y", sc.y(v) + 3);
      t.setAttribute("text-anchor", "end");
      t.textContent = String(v);
      grid.appendChild(t);
    });

    var xlabels = svg.querySelector(".xlabels");
    xlabels.innerHTML = "";
    [2018, 2020, 2022, 2024, 2026, 2028].forEach(function (yr) {
      var t = document.createElementNS(ns, "text");
      t.setAttribute("class", "tick-label");
      t.setAttribute("x", sc.x(yr));
      t.setAttribute("y", box.h - 10);
      t.setAttribute("text-anchor", "middle");
      t.textContent = yr === 2028 ? "’28*" : String(yr);
      xlabels.appendChild(t);
    });

    var axis = svg.querySelector(".axis-lines");
    axis.innerHTML = "";
    var ax = document.createElementNS(ns, "line");
    ax.setAttribute("class", "axis");
    ax.setAttribute("x1", sc.x0);
    ax.setAttribute("x2", sc.x1);
    ax.setAttribute("y1", sc.y0);
    ax.setAttribute("y2", sc.y0);
    axis.appendChild(ax);

    var now = svg.querySelector(".now-line");
    now.setAttribute("x1", sc.x(LAST_OBS));
    now.setAttribute("x2", sc.x(LAST_OBS));
    now.setAttribute("y1", sc.y1);
    now.setAttribute("y2", sc.y0);

    var nowLbl = svg.querySelector(".now-label");
    nowLbl.setAttribute("x", sc.x(LAST_OBS) + 6);
    nowLbl.setAttribute("y", sc.y1 + 12);
    nowLbl.textContent = "2026";

    var hit = svg.querySelector(".hit");
    hit.setAttribute("width", box.w);
    hit.setAttribute("height", box.h);

    ["an", "ds", "ai"].forEach(function (key) {
      var hist = svg.querySelector("[data-hist='" + key + "']");
      var proj = svg.querySelector("[data-proj='" + key + "']");
      var band = svg.querySelector("[data-band='" + key + "']");
      hist.setAttribute("d", pathFor(key, 2018, LAST_OBS, sc));
      proj.setAttribute("d", pathFor(key, LAST_OBS, 2028, sc));
      if (key === "ai") band.setAttribute("d", bandPath(key, sc));
    });

    applyStep(state.step, true);
  }

  function applyStep(n, instant) {
    state.step = n;
    var cfg = STEPS[n] || STEPS[0];
    var box = chartBox();
    var sc = scales(box);
    var dur = state.reduce || instant ? 0 : 420;

    ["an", "ds", "ai"].forEach(function (key) {
      var on = cfg.focus.indexOf(key) !== -1 && state.visible[key];
      var hist = svg.querySelector("[data-hist='" + key + "']");
      var proj = svg.querySelector("[data-proj='" + key + "']");
      var band = svg.querySelector("[data-band='" + key + "']");
      var op = on ? "1" : "0.12";
      hist.style.opacity = op;
      proj.style.opacity = n >= 5 && on ? "0.9" : n >= 5 ? "0.12" : "0.35";
      if (band) band.style.opacity = n >= 5 && key === "ai" && on ? "1" : "0";
      if (dur) {
        hist.style.transition = "opacity 280ms ease";
        proj.style.transition = "opacity 280ms ease";
      }
    });

    var anno = svg.querySelector(".anno");
    if (cfg.year) {
      var key = cfg.focus[cfg.focus.length - 1];
      var i = YEARS.indexOf(cfg.year);
      var v = SERIES[key].values[i];
      var cx = sc.x(cfg.year);
      var cy = sc.y(v);
      anno.querySelector("circle").setAttribute("cx", cx);
      anno.querySelector("circle").setAttribute("cy", cy);
      var label = anno.querySelector("text");
      label.setAttribute("x", cx + 10);
      label.setAttribute("y", cy - 10);
      label.textContent = cfg.label;
      anno.style.opacity = "1";
    } else {
      anno.style.opacity = "0";
    }

    document.querySelectorAll(".step").forEach(function (el) {
      el.classList.toggle("is-active", Number(el.getAttribute("data-step")) === n);
    });
  }

  function showYear(year) {
    var box = chartBox();
    var sc = scales(box);
    year = Math.max(2018, Math.min(2028, year));
    var i = YEARS.indexOf(year);
    hoverLine.setAttribute("x1", sc.x(year));
    hoverLine.setAttribute("x2", sc.x(year));
    hoverLine.setAttribute("y1", sc.y1);
    hoverLine.setAttribute("y2", sc.y0);
    hoverLine.style.opacity = "0.45";
    var note = year > LAST_OBS ? " (proj.)" : "";
    tooltip.innerHTML =
      "<strong>" + year + note + "</strong><br>" +
      "Analytics " + SERIES.an.values[i] + "<br>" +
      "Data science " + SERIES.ds.values[i] + "<br>" +
      "AI / ML " + SERIES.ai.values[i];
    tooltip.style.left = ((sc.x(year) / box.w) * 100) + "%";
    tooltip.style.top = "28%";
    tooltip.classList.add("is-on");
    svg.querySelector(".hit").setAttribute("data-year", String(year));
  }

  function bindChartHover() {
    var overlay = svg.querySelector(".hit");
    overlay.addEventListener("mousemove", function (e) {
      var box = chartBox();
      var sc = scales(box);
      var rect = svg.getBoundingClientRect();
      var px = ((e.clientX - rect.left) / rect.width) * box.w;
      var t = (px - sc.x0) / (sc.x1 - sc.x0);
      showYear(Math.round(2018 + t * 10));
    });
    overlay.addEventListener("mouseleave", function () {
      hoverLine.style.opacity = "0";
      tooltip.classList.remove("is-on");
    });
    overlay.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      e.preventDefault();
      var yr = Number(overlay.getAttribute("data-year") || "2026");
      showYear(yr + (e.key === "ArrowRight" ? 1 : -1));
    });
  }

  document.querySelectorAll(".legend button").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var key = btn.getAttribute("data-series");
      state.visible[key] = !state.visible[key];
      btn.setAttribute("aria-pressed", state.visible[key] ? "true" : "false");
      applyStep(state.step, true);
    });
  });

  var tableBtn = document.getElementById("table-toggle");
  var tableWrap = document.getElementById("data-table-wrap");
  if (tableBtn && tableWrap) {
    fillTable();
    tableBtn.addEventListener("click", function () {
      var open = tableWrap.classList.toggle("is-open");
      tableBtn.setAttribute("aria-expanded", open ? "true" : "false");
      tableBtn.textContent = open ? "Hide data table" : "View data table";
    });
  }

  function fillTable() {
    var tb = tableWrap.querySelector("tbody");
    tb.innerHTML = YEARS.map(function (yr, i) {
      var tag = yr > LAST_OBS ? " (proj.)" : "";
      return "<tr><th scope='row'>" + yr + tag + "</th><td>" +
        SERIES.an.values[i] + "</td><td>" +
        SERIES.ds.values[i] + "</td><td>" +
        SERIES.ai.values[i] + "</td></tr>";
    }).join("");
  }

  /* ── Scrolly ── */
  var stepEls = document.querySelectorAll(".step");
  if (stepEls.length && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      var best = null;
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        if (!best || en.intersectionRatio > best.intersectionRatio) best = en;
      });
      if (best) applyStep(Number(best.target.getAttribute("data-step")));
    }, { rootMargin: "-28% 0px -40% 0px", threshold: [0.25, 0.5, 0.75] });
    stepEls.forEach(function (el) { io.observe(el); });
  }

  /* ── Jobs ── */
  var seqRoot = document.getElementById("sequence");
  document.querySelectorAll(".job").forEach(function (btn) {
    btn.addEventListener("click", function () {
      document.querySelectorAll(".job").forEach(function (b) {
        b.setAttribute("aria-pressed", b === btn ? "true" : "false");
      });
      renderJob(btn.getAttribute("data-job"));
    });
  });
  renderJob("data-analyst");

  function renderJob(id) {
    var job = JOBS[id];
    if (!job || !seqRoot) return;
    seqRoot.innerHTML =
      "<header><h3 id='seq-title'>" + job.title + "</h3><span class='seq-time'>" + job.time + "</span></header>" +
      "<p class='seq-lead'>" + job.lead + "</p>" +
      "<ol class='seq-list'>" +
      job.steps.map(function (s, i) {
        return "<li><span class='seq-n'>" + String(i + 1).padStart(2, "0") + "</span><div><h4>" +
          s[0] + "</h4><p>" + s[1] + "</p></div></li>";
      }).join("") +
      "</ol>" +
      "<p class='seq-lead' style='margin-top:8px'>0 · Python — every path starts here, then you specialize.</p>" +
      "<div class='seq-actions'>" +
      "<a class='btn btn-solid' href='" + job.href + "'>" + job.cta + "</a>" +
      "<a class='btn btn-line' href='../../register/index.html'>Book a career call</a>" +
      "</div>";
  }

  /* ── Nav / progress ── */
  var toggle = document.getElementById("nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  var bar = document.getElementById("read-progress");
  window.addEventListener("scroll", function () {
    var h = document.documentElement.scrollHeight - window.innerHeight;
    var p = h > 0 ? (window.scrollY / h) * 100 : 0;
    if (bar) bar.style.width = p + "%";
  }, { passive: true });

  var y = document.getElementById("year");
  if (y) y.textContent = String(new Date().getFullYear());

  function debounce(fn, ms) {
    var t;
    return function () {
      clearTimeout(t);
      t = setTimeout(fn, ms);
    };
  }
})();
