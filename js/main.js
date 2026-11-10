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

  // Mark current page in nav (works with or without the .html extension)
  var norm = function (p) {
    return p.replace(/\/index(\.html)?$/, "/").replace(/\.html$/, "").replace(/(.)\/$/, "$1");
  };
  var currentPath = norm(location.pathname);
  document.querySelectorAll(".main-nav a").forEach(function (link) {
    if (link.closest(".lang-switch")) return;
    if (norm(link.pathname) === currentPath) {
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

// Contact forms: submit via fetch to Web3Forms, then go to the site's own thank-you page
(function () {
  document.querySelectorAll('form[data-redirect]').forEach(function (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var btn = form.querySelector('button[type="submit"]');
      if (btn) btn.disabled = true;
      fetch(form.action, { method: 'POST', headers: { Accept: 'application/json' }, body: new FormData(form) })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d && d.success) { window.location.href = form.getAttribute('data-redirect'); }
          else { throw new Error('failed'); }
        })
        .catch(function () {
          if (btn) btn.disabled = false;
          window.alert(form.getAttribute('data-error'));
        });
    });
  });
})();

// Visual polish: header shrinks on scroll, sections fade in
document.addEventListener("DOMContentLoaded", function () {
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () { header.classList.toggle("scrolled", window.scrollY > 24); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  if (!("IntersectionObserver" in window) || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  var targets = document.querySelectorAll(
    ".section-head, .pkg-card, .card, .activity-card, .guide-card, .testimonial-card, .why-item, .founder-card, .value-item, .gallery-grid > *, .faq-item"
  );
  if (!targets.length) return;
  document.documentElement.classList.add("js-reveal");
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
  targets.forEach(function (el, i) {
    el.classList.add("reveal");
    el.style.transitionDelay = (i % 4) * 80 + "ms";
    io.observe(el);
  });
  // Safety net: never leave content hidden
  setTimeout(function () { targets.forEach(function (el) { el.classList.add("in"); }); }, 4000);
});
