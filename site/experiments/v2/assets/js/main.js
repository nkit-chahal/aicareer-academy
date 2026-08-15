(function () {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const years = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028];
  const ai = [18, 24, 31, 42, 55, 70, 86, 98, 112, 124, 136];
  const data = [48, 54, 60, 66, 73, 80, 86, 91, 96, 100, 104];
  const ops = [6, 9, 13, 20, 30, 44, 58, 72, 88, 100, 114];

  const svg = document.getElementById("jobs-chart");
  const yearEl = document.getElementById("year-num");
  const stage = document.querySelector(".chart-stage");
  if (!svg || !stage) return;

  const W = 1200;
  const H = 520;
  const pad = { t: 28, r: 36, b: 48, l: 48 };
  const innerW = W - pad.l - pad.r;
  const innerH = H - pad.t - pad.b;
  const yMax = 150;

  const xAt = (i) => pad.l + (i / (years.length - 1)) * innerW;
  const yAt = (v) => pad.t + (1 - v / yMax) * innerH;

  function pathFrom(series) {
    return series
      .map((v, i) => `${i === 0 ? "M" : "L"} ${xAt(i).toFixed(1)} ${yAt(v).toFixed(1)}`)
      .join(" ");
  }

  function areaFrom(series) {
    const line = pathFrom(series);
    const last = xAt(series.length - 1).toFixed(1);
    const first = xAt(0).toFixed(1);
    const base = pad.t + innerH;
    return `${line} L ${last} ${base} L ${first} ${base} Z`;
  }

  const ns = "http://www.w3.org/2000/svg";
  function el(name, attrs) {
    const node = document.createElementNS(ns, name);
    Object.entries(attrs).forEach(([k, v]) => node.setAttribute(k, v));
    return node;
  }

  const defs = el("defs", {});
  defs.innerHTML = `
    <linearGradient id="goldFade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#e4c27a" stop-opacity="0.28"/>
      <stop offset="100%" stop-color="#e4c27a" stop-opacity="0"/>
    </linearGradient>
  `;
  svg.appendChild(defs);

  [0, 50, 100, 150].forEach((tick) => {
    const y = yAt(tick);
    svg.appendChild(el("line", { class: "grid-line", x1: pad.l, x2: W - pad.r, y1: y, y2: y }));
    const t = el("text", { class: "axis-text", x: 8, y: y + 4 });
    t.textContent = String(tick);
    svg.appendChild(t);
  });

  years.forEach((yr, i) => {
    if (i % 2 !== 0) return;
    const t = el("text", { class: "axis-text", x: xAt(i), y: H - 16, "text-anchor": "middle" });
    t.textContent = String(yr);
    svg.appendChild(t);
  });

  const area = el("path", { class: "area-ai", d: areaFrom(ai), "clip-path": "url(#drawClip)" });
  const clip = el("clipPath", { id: "drawClip" });
  const clipRect = el("rect", { x: "0", y: "0", width: "0", height: String(H) });
  clip.appendChild(clipRect);
  defs.appendChild(clip);

  const pAi = el("path", { class: "series-ai", d: pathFrom(ai) });
  const pData = el("path", { class: "series-data", d: pathFrom(data) });
  const pOps = el("path", { class: "series-ops", d: pathFrom(ops) });
  svg.appendChild(area);
  svg.appendChild(pData);
  svg.appendChild(pOps);
  svg.appendChild(pAi);

  const dots = [
    { series: ai, cls: "dot-ai" },
    { series: data, cls: "dot-data" },
    { series: ops, cls: "dot-ops" },
  ].map(({ series, cls }) => {
    const c = el("circle", {
      class: `dot ${cls}`,
      r: "5",
      cx: String(xAt(0)),
      cy: String(yAt(series[0])),
    });
    svg.appendChild(c);
    return { el: c, series };
  });

  function len(path) {
    return path.getTotalLength();
  }

  const paths = [pAi, pData, pOps];
  paths.forEach((p) => {
    const L = len(p);
    p.style.strokeDasharray = String(L);
    p.style.strokeDashoffset = reduce ? "0" : String(L);
  });

  function lerp(a, b, t) {
    return a + (b - a) * t;
  }

  function atProgress(series, t) {
    const max = series.length - 1;
    const f = t * max;
    const i = Math.min(max - 1, Math.floor(f));
    const local = f - i;
    return { x: lerp(xAt(i), xAt(i + 1), local), y: lerp(yAt(series[i]), yAt(series[i + 1]), local) };
  }

  function setProgress(t) {
    const clamped = Math.max(0, Math.min(1, t));
    paths.forEach((p) => {
      const L = len(p);
      p.style.strokeDashoffset = String(L * (1 - clamped));
    });
    clipRect.setAttribute("width", String(pad.l + clamped * innerW));
    dots.forEach(({ el: c, series }) => {
      const pt = atProgress(series, clamped);
      c.setAttribute("cx", String(pt.x));
      c.setAttribute("cy", String(pt.y));
    });
    const yi = Math.round(clamped * (years.length - 1));
    yearEl.textContent = String(years[yi]);
  }

  function measure() {
    const rect = stage.getBoundingClientRect();
    const total = stage.offsetHeight - window.innerHeight;
    const scrolled = -rect.top;
    return total <= 0 ? 0 : scrolled / total;
  }

  let ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      setProgress(reduce ? 1 : measure());
      ticking = false;
    });
  }

  if (reduce) {
    setProgress(1);
  } else {
    setProgress(0);
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    onScroll();
  }

  const seqItems = document.querySelectorAll(".sequence-list li");
  if ("IntersectionObserver" in window && !reduce) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) e.target.classList.add("in");
        });
      },
      { threshold: 0.35 }
    );
    seqItems.forEach((li) => io.observe(li));
  } else {
    seqItems.forEach((li) => li.classList.add("in"));
  }
})();
