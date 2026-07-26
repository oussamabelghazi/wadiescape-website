// Wadi Escape: shared site behavior
document.addEventListener("DOMContentLoaded", function () {
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.querySelector(".main-nav");

  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var isOpen = nav.classList.toggle("open");
      toggle.classList.toggle("open", isOpen);
      toggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });

    nav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("open");
        toggle.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  // Mark current page in nav
  var current = location.pathname.split("/").pop() || "index.html";
  document.querySelectorAll(".main-nav a").forEach(function (link) {
    var href = link.getAttribute("href");
    if (href === current || (current === "" && href === "index.html")) {
      link.classList.add("active");
    }
  });

  // Pre-select package on the contact form when arriving via ?package=muscat-escape|coast-explorer|desert-mountains|ultimate-oman|custom
  var packageSelect = document.getElementById("package");
  var params = new URLSearchParams(location.search);
  if (packageSelect) {
    var wanted = params.get("package");
    if (wanted) {
      packageSelect.value = wanted.toLowerCase();
    }
  }

  // Pre-fill "What are you most excited about?" when arriving via ?interest=<tag> (Activities "Build Your Own")
  var excitedField = document.getElementById("excited");
  if (excitedField) {
    var interest = params.get("interest");
    if (interest && !excitedField.value) {
      excitedField.value = interest;
    }
  }
});
