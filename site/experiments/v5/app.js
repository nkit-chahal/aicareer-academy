(function () {
  var menu = document.getElementById("menu");
  var openBtn = document.getElementById("navToggle");
  var closeBtn = document.getElementById("menuClose");
  var stage = document.querySelector(".chart-stage");
  var listbox = document.querySelector(".towers");
  var towers = Array.prototype.slice.call(document.querySelectorAll(".tower"));
  var readoutTitle = document.getElementById("readoutTitle");
  var readoutBody = document.getElementById("readoutBody");
  var facts = {
    ds: {
      title: "Data scientists · +33.5%",
      body: "U.S. BLS projects data scientist employment to grow 33.5% from 2024 to 2034 — among the fastest of all occupations, versus 3.1% for all jobs. That is a labour forecast, not an Indian placement promise. If this is the job you want, we map Excel/SQL/Python into a live program."
    },
    sec: {
      title: "Information security analysts · +28.5%",
      body: "BLS: +28.5% employment change, 2024–34. Security is not our core catalog, but production AI work still needs people who can think about access, logs, and failure. A career call will say so if another path fits better."
    },
    rs: {
      title: "Computer & information research scientists · +19.7%",
      body: "BLS: +19.7%, 2024–34. Research-scientist titles usually want a deeper academic track than a 3–6 month cohort. We still teach the engineering stack used next to that work — models, evaluation, shipping."
    },
    sw: {
      title: "Software developers · +16%",
      body: "BLS: software developers +16% (2024–34); the broader developers / QA / testers group is +15%. Developers who can work with data, APIs, and LLMs are the people companies actually interview. That is the sequence we teach."
    },
    all: {
      title: "All occupations · +3.1%",
      body: "The grey stub is the average. AI-adjacent roles sit far above it in this U.S. table. India does not publish an equivalent official series — so we refuse to invent one. Book a call if you want a role map, not a slogan."
    }
  };

  function setOpen(open) {
    menu.classList.toggle("is-open", open);
    menu.setAttribute("aria-hidden", open ? "false" : "true");
    openBtn.setAttribute("aria-expanded", open ? "true" : "false");
    document.body.style.overflow = open ? "hidden" : "";
    if (open) closeBtn.focus();
    else openBtn.focus();
  }

  openBtn.addEventListener("click", function () {
    setOpen(true);
  });
  closeBtn.addEventListener("click", function () {
    setOpen(false);
  });
  menu.addEventListener("click", function (e) {
    if (e.target.tagName === "A") setOpen(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && menu.classList.contains("is-open")) setOpen(false);
  });

  function selectTower(btn, focus) {
    towers.forEach(function (t) {
      t.classList.toggle("is-on", t === btn);
      t.setAttribute("aria-selected", t === btn ? "true" : "false");
    });
    var fact = facts[btn.getAttribute("data-id")];
    if (fact) {
      readoutTitle.textContent = fact.title;
      readoutBody.textContent = fact.body;
    }
    if (listbox) listbox.setAttribute("aria-activedescendant", btn.id);
    if (focus) btn.focus();
  }

  towers.forEach(function (btn, i) {
    btn.addEventListener("click", function () {
      selectTower(btn, false);
    });
    btn.addEventListener("keydown", function (e) {
      var next = i;
      if (e.key === "ArrowRight" || e.key === "ArrowDown") next = (i + 1) % towers.length;
      else if (e.key === "ArrowLeft" || e.key === "ArrowUp") next = (i - 1 + towers.length) % towers.length;
      else return;
      e.preventDefault();
      selectTower(towers[next], true);
    });
  });

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            stage.classList.add("is-drawn");
            io.disconnect();
          }
        });
      },
      { threshold: 0.25 }
    );
    io.observe(stage);
  } else {
    stage.classList.add("is-drawn");
  }

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    stage.classList.add("is-drawn");
  }
})();
