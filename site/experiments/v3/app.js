(function () {
  "use strict";

  var YEARS = ["2020", "2021", "2022", "2023", "2024", "2025", "2026+"];
  var SERIES = {
    ds: { label: "Data science", dash: "solid", values: [70, 85, 92, 88, 84, 82, 80] },
    ml: { label: "Machine learning", dash: "solid", values: [40, 52, 62, 70, 78, 84, 88] },
    llm: { label: "LLM / GenAI", dash: "dashed", values: [8, 10, 18, 72, 95, 100, 96] },
    ops: { label: "MLOps", dash: "dotted", values: [18, 24, 32, 48, 62, 74, 82] }
  };

  var PATHS = {
    ds: {
      kicker: "01 · Analyst",
      title: "Data Analyst",
      blurb: "Turn messy tables into decisions a manager can trust.",
      courseHref: "../../courses/data-analytics-course-with-placement/index.html",
      courseLabel: "Open Data Analytics with AI",
      steps: [
        { n: "00", t: "Python", d: "Syntax, data frames, and how to think in code. Every path starts here." },
        { n: "01", t: "Spreadsheets + cleaning", d: "Load a CSV, fix the mess, answer one business question." },
        { n: "02", t: "SQL", d: "Joins, aggregations, window functions — where most analyst interviews live." },
        { n: "03", t: "BI dashboards", d: "KPIs and a story a leader can scan in 30 seconds." },
        { n: "04", t: "Stats for business", d: "Trends, A/B intuition, enough to not get fooled by a chart." },
        { n: "05", t: "Portfolio", d: "Ship one dashboard that shows judgment, not just charts." }
      ]
    },
    ml: {
      kicker: "02 · ML Engineer",
      title: "ML Engineer",
      blurb: "Take models out of notebooks and into production.",
      courseHref: "../../courses/machine-learning-course/index.html",
      courseLabel: "Open Machine Learning",
      steps: [
        { n: "00", t: "Python engineering", d: "Packages, tests, typing. Treat model code like product code." },
        { n: "01", t: "Classical ML depth", d: "Features, training loops, evaluation you can defend in review." },
        { n: "02", t: "Serving", d: "APIs, batch jobs, latency vs throughput." },
        { n: "03", t: "MLOps layer", d: "Version data and models. CI for training. Watch drift." },
        { n: "04", t: "Ship a system", d: "Dataset → trained artifact → endpoint with logs." }
      ]
    },
    llm: {
      kicker: "03 · LLM Engineer",
      title: "LLM Engineer",
      blurb: "Embeddings, RAG, evals, and inference that actually scales.",
      courseHref: "../../courses/large-language-model-course/index.html",
      courseLabel: "Open LLM Mastery",
      steps: [
        { n: "00", t: "Python + APIs", d: "Call models cleanly. Handle tokens, retries, and cost." },
        { n: "01", t: "Embeddings & retrieval", d: "Chunking, vector search, why RAG fails in production." },
        { n: "02", t: "Fine-tune vs retrieve", d: "When to PEFT, when to prompt, when to just retrieve." },
        { n: "03", t: "Evals", d: "Golden sets, hallucination checks, latency and cost." },
        { n: "04", t: "Serve", d: "Batching, caching, safety. LLMOps if you run this at scale." }
      ]
    },
    ops: {
      kicker: "04 · MLOps",
      title: "MLOps Engineer",
      blurb: "Pipelines, containers, and reliability for ML and AI services.",
      courseHref: "../../courses/mlops-course/index.html",
      courseLabel: "Open MLOps",
      steps: [
        { n: "00", t: "Python + Linux", d: "Scripts and env management. Enough Python to debug a training job." },
        { n: "01", t: "Containers", d: "Docker images that train and serve on another machine." },
        { n: "02", t: "CI/CD for models", d: "Data contracts, gated deploys, rollback when a model is worse." },
        { n: "03", t: "Orchestration", d: "Health checks, scaling, secrets — Kubernetes or equivalent." },
        { n: "04", t: "Observe & govern", d: "Metrics, cost, drift. Then LLMOps if you are running GenAI." }
      ]
    }
  };

  var visible = { ds: true, ml: true, llm: true, ops: true };
  var activeRole = "ds";
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var firstPaint = true;

  var svg = document.getElementById("market-chart");
  var tooltip = document.getElementById("chart-tooltip");
  var seqEl = document.getElementById("sequence");
  var nav = document.getElementById("nav");
  var toggle = document.getElementById("nav-toggle");

  var W = 800;
  var H = 360;
  var pad = { t: 24, r: 20, b: 40, l: 44 };
  var innerW = W - pad.l - pad.r;
  var innerH = H - pad.t - pad.b;

  function xAt(i) {
    return pad.l + (i / (YEARS.length - 1)) * innerW;
  }

  function yAt(v) {
    return pad.t + (1 - v / 100) * innerH;
  }

  function pathFor(values) {
    return values
      .map(function (v, i) {
        return (i ? "L" : "M") + xAt(i) + " " + yAt(v);
      })
      .join(" ");
  }

  function ns(name) {
    return document.createElementNS("http://www.w3.org/2000/svg", name);
  }

  function drawGrid() {
    var g = ns("g");
    g.setAttribute("aria-hidden", "true");
    [0, 25, 50, 75, 100].forEach(function (tick) {
      var line = ns("line");
      line.setAttribute("class", "grid-line");
      line.setAttribute("x1", String(pad.l));
      line.setAttribute("x2", String(W - pad.r));
      line.setAttribute("y1", String(yAt(tick)));
      line.setAttribute("y2", String(yAt(tick)));
      g.appendChild(line);
      var lab = ns("text");
      lab.setAttribute("class", "axis-label");
      lab.setAttribute("x", String(pad.l - 8));
      lab.setAttribute("y", String(yAt(tick) + 4));
      lab.setAttribute("text-anchor", "end");
      lab.textContent = String(tick);
      g.appendChild(lab);
    });
    YEARS.forEach(function (year, i) {
      var lab = ns("text");
      lab.setAttribute("class", "axis-label");
      lab.setAttribute("x", String(xAt(i)));
      lab.setAttribute("y", String(H - 12));
      lab.setAttribute("text-anchor", "middle");
      lab.textContent = year;
      g.appendChild(lab);
    });
    return g;
  }

  function seriesClass(id) {
    var cls = "series-line series-" + id;
    if (!visible[id]) cls += " is-hidden";
    else if (id !== activeRole) cls += " is-dim";
    return cls;
  }

  function hideTip() {
    tooltip.classList.remove("is-show");
    tooltip.innerHTML = "";
  }

  function showTip(id, i, el) {
    var s = SERIES[id];
    var wrap = svg.parentElement.getBoundingClientRect();
    var pt = el.getBoundingClientRect();
    tooltip.style.left = pt.left - wrap.left + pt.width / 2 + "px";
    tooltip.style.top = pt.top - wrap.top + "px";
    tooltip.innerHTML =
      "<strong>" +
      YEARS[i] +
      "</strong><span>" +
      s.label +
      " · index " +
      s.values[i] +
      "</span>";
    tooltip.classList.add("is-show");
  }

  function paint() {
    svg.replaceChildren();
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.setAttribute("role", "img");
    svg.setAttribute(
      "aria-label",
      "Relative hiring-attention index for data science, machine learning, LLM, and MLOps from 2020 through 2026 plus. Teaching sketch, not a job-count forecast."
    );
    svg.appendChild(drawGrid());

    Object.keys(SERIES).forEach(function (id) {
      var s = SERIES[id];
      var g = ns("g");
      var p = ns("path");
      p.setAttribute("d", pathFor(s.values));
      p.setAttribute("class", seriesClass(id));
      g.appendChild(p);

      var hit = ns("path");
      hit.setAttribute("d", pathFor(s.values));
      hit.setAttribute("class", "hit");
      hit.setAttribute("tabindex", visible[id] ? "0" : "-1");
      hit.setAttribute("role", "button");
      hit.setAttribute("aria-label", "Map " + s.label + " to a learning sequence");
      hit.addEventListener("click", function () {
        setRole(id);
      });
      hit.addEventListener("keydown", function (ev) {
        if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          setRole(id);
        }
      });
      g.appendChild(hit);

      s.values.forEach(function (v, i) {
        var c = ns("circle");
        c.setAttribute("class", "dot series-" + id);
        c.setAttribute("cx", String(xAt(i)));
        c.setAttribute("cy", String(yAt(v)));
        c.setAttribute("fill", "var(--bg-elev)");
        c.setAttribute("stroke-width", "2");
        c.setAttribute("tabindex", visible[id] ? "0" : "-1");
        c.setAttribute("role", "img");
        c.setAttribute("aria-label", s.label + ", " + YEARS[i] + ", index " + v);
        if (!visible[id]) c.classList.add("is-hidden");
        else if (id !== activeRole) c.classList.add("is-dim");
        c.addEventListener("mouseenter", function () {
          c.classList.add("is-hot");
          showTip(id, i, c);
        });
        c.addEventListener("mouseleave", function () {
          c.classList.remove("is-hot");
          hideTip();
        });
        c.addEventListener("focus", function () {
          c.classList.add("is-hot");
          showTip(id, i, c);
        });
        c.addEventListener("blur", hideTip);
        c.addEventListener("click", function () {
          setRole(id);
        });
        g.appendChild(c);
      });

      svg.appendChild(g);

      if (firstPaint && !reduced && visible[id]) {
        var len = 0;
        try {
          len = p.getTotalLength();
        } catch (err) {
          len = 0;
        }
        if (len) {
          p.style.strokeDasharray = String(len);
          p.style.strokeDashoffset = String(len);
          requestAnimationFrame(function () {
            p.style.transition = "stroke-dashoffset 700ms cubic-bezier(0.22,1,0.36,1), opacity 220ms";
            p.style.strokeDashoffset = "0";
            setTimeout(function () {
              p.style.strokeDasharray = "";
              if (id === "llm") p.style.strokeDasharray = "7 5";
              if (id === "ops") p.style.strokeDasharray = "2 5";
            }, 720);
          });
        }
      }
    });
    firstPaint = false;
  }

  function renderSequence() {
    var path = PATHS[activeRole];
    seqEl.innerHTML = path.steps
      .map(function (step) {
        return (
          '<li class="step"><span class="n" aria-hidden="true">' +
          step.n +
          "</span><div><h3>" +
          step.t +
          "</h3><p>" +
          step.d +
          "</p></div></li>"
        );
      })
      .join("");
    document.getElementById("seq-kicker").textContent = path.kicker;
    document.getElementById("seq-title").textContent = path.title;
    document.getElementById("seq-blurb").textContent = path.blurb;
    var course = document.getElementById("seq-course");
    course.href = path.courseHref;
    course.textContent = path.courseLabel;
    document.querySelectorAll(".role").forEach(function (btn) {
      var on = btn.getAttribute("data-role") === activeRole;
      btn.classList.toggle("is-active", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
  }

  function setRole(id) {
    activeRole = id;
    renderSequence();
    paint();
  }

  document.querySelectorAll(".legend button").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var id = btn.getAttribute("data-series");
      visible[id] = !visible[id];
      btn.classList.toggle("is-on", visible[id]);
      btn.classList.toggle("is-off", !visible[id]);
      btn.setAttribute("aria-pressed", visible[id] ? "true" : "false");
      paint();
    });
  });

  document.querySelectorAll(".role").forEach(function (btn) {
    btn.addEventListener("click", function () {
      setRole(btn.getAttribute("data-role"));
    });
  });

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
  }

  var tableBtn = document.getElementById("table-toggle");
  var table = document.getElementById("index-table");
  if (tableBtn && table) {
    tableBtn.addEventListener("click", function () {
      var open = table.classList.toggle("is-open");
      tableBtn.setAttribute("aria-expanded", open ? "true" : "false");
      tableBtn.textContent = open ? "Hide index table" : "Show index table";
    });
  }

  renderSequence();
  paint();
})();
