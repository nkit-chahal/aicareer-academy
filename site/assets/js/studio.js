(function () {
  var WA = "https://wa.me/918368122877?text=";

  function openWa(lines) {
    window.open(WA + encodeURIComponent(lines.join("\n")), "_blank", "noopener");
  }

  var chat = document.getElementById("chatBtn");
  if (chat) {
    chat.addEventListener("click", function () {
      openWa([
        "Hi Prerna — I'd like a career call.",
        "Page: " + window.location.href
      ]);
    });
  }

  var dockForm = document.getElementById("dockEnquire");
  if (dockForm) {
    dockForm.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!dockForm.reportValidity()) return;
      var name = document.getElementById("dqName").value.trim();
      var phone = document.getElementById("dqPhone").value.trim();
      var course = document.getElementById("dqCourse").value;
      var city = document.getElementById("dqCity").value.trim();
      var status = document.getElementById("dqStatus");
      openWa([
        "Hi Prerna, I'd like to book a career call.",
        "Name: " + name,
        "Phone: " + phone,
        "Program: " + course,
        "City: " + city,
        "Page: " + window.location.href
      ]);
      if (status) status.textContent = "Opening WhatsApp with your details.";
    });
  }

  var tabs = document.querySelectorAll(".offer-tabs button");
  var panels = document.querySelectorAll(".offer-panel");
  if (tabs.length && panels.length) {
    tabs.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var id = btn.getAttribute("data-offer");
        tabs.forEach(function (t) { t.classList.toggle("is-on", t === btn); });
        panels.forEach(function (p) {
          var on = p.id === "offer-" + id;
          p.hidden = !on;
        });
      });
    });
  }

  document.querySelectorAll("[data-wa-course]").forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      openWa([
        "Hi Prerna, I want to talk about " + a.getAttribute("data-wa-course") + ".",
        "Page: " + window.location.href
      ]);
    });
  });
})();
