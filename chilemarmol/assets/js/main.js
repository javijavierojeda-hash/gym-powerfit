/* ==========================================================================
   Chile Mármol — Interacciones y animaciones
   - Lenis: scroll suave · GSAP + ScrollTrigger: animaciones ligadas al scroll
   - Todo el contenido se arma con métodos DOM (sin innerHTML con datos)
     para evitar inyección de HTML y cumplir la CSP.
   - Si el usuario pide "movimiento reducido" o GSAP no carga, el sitio
     funciona completo sin animaciones.
   ========================================================================== */
(function () {
  "use strict";

  var root = document.documentElement;
  var SITE = window.SITE || {};
  var PROJECTS = window.PROJECTS || [];
  var CATEGORIES = window.CATEGORIES || [];
  var img = window.img;

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var motion = !reduceMotion && !!(window.gsap && window.ScrollTrigger);
  if (!motion) root.classList.remove("js-motion", "js-preload", "is-entering");

  var gsap = window.gsap;
  var lenis = null;

  /* ---------- Utilidades ---------- */
  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }

  /* Crea un elemento: el("a", { class: "x", href: "..." }, [hijos | "texto"]) */
  function el(tag, attrs, children) {
    var node = document.createElement(tag);
    if (attrs) {
      Object.keys(attrs).forEach(function (key) {
        var value = attrs[key];
        if (value === null || value === undefined || value === false) return;
        node.setAttribute(key, value === true ? "" : String(value));
      });
    }
    (children || []).forEach(function (child) {
      if (child === null || child === undefined) return;
      node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
    });
    return node;
  }

  function storage(action, key, value) {
    try {
      if (action === "get") return sessionStorage.getItem(key);
      if (action === "set") sessionStorage.setItem(key, value);
      if (action === "remove") sessionStorage.removeItem(key);
    } catch (e) { /* modo privado o almacenamiento bloqueado */ }
    return null;
  }

  var categoryBySlug = {};
  CATEGORIES.forEach(function (c) { categoryBySlug[c.slug] = c; });

  function projectsOf(slug) {
    return PROJECTS.filter(function (p) { return p.category === slug; });
  }

  function srcset(ref) {
    return [600, 1000, 1600].map(function (w) { return img(ref, w) + " " + w + "w"; }).join(", ");
  }

  function waLink(message) {
    var number = String(SITE.whatsapp || "").replace(/\D/g, "");
    return "https://wa.me/" + number + "?text=" + encodeURIComponent(message || SITE.whatsappMessage || "");
  }

  function scrollToTarget(target) {
    if (lenis) lenis.scrollTo(target, { offset: 0, duration: 1.4 });
    else if (typeof target === "number") window.scrollTo(0, target);
    else target.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth" });
  }

  /* ---------- Contacto (WhatsApp, email, etc.) ---------- */
  function bindContact() {
    $$("[data-wa]").forEach(function (a) {
      a.href = waLink(a.getAttribute("data-wa"));
      a.target = "_blank";
      a.rel = "noopener noreferrer";
    });
    $$("[data-email]").forEach(function (a) {
      a.href = "mailto:" + SITE.email;
      if (!a.textContent.trim()) a.textContent = SITE.email;
    });
    $$("[data-instagram]").forEach(function (a) { a.href = SITE.instagram; });
    $$("[data-hours]").forEach(function (n) { n.textContent = SITE.hours; });
    $$("[data-year]").forEach(function (n) { n.textContent = new Date().getFullYear(); });
  }

  /* ---------- Componentes de proyectos ---------- */
  function projectCard(p, options) {
    var category = categoryBySlug[p.category] || { name: "" };
    var sizes = (options && options.sizes) || "(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw";
    return el("a", { class: "project-card", href: "proyecto.html?p=" + encodeURIComponent(p.slug), "data-card": true }, [
      el("div", { class: "project-card__media", "data-reveal-media": true }, [
        el("span", { class: "project-card__badge label" }, [category.name]),
        el("div", { class: "project-card__zoom" }, [
          el("img", {
            src: img(p.images[0], 1000), srcset: srcset(p.images[0]), sizes: sizes,
            alt: p.title + ", proyecto de " + category.name.toLowerCase() + " en " + p.location,
            loading: "lazy", decoding: "async", "data-card-img": true,
          }),
        ]),
        el("span", { class: "project-card__view", "aria-hidden": "true" }, ["Ver proyecto"]),
      ]),
      el("div", { class: "project-card__meta" }, [
        el("h3", { class: "project-card__title" }, [p.title]),
        el("span", { class: "project-card__info" }, [p.location + " · " + p.year]),
      ]),
    ]);
  }

  function renderFeatured() {
    var host = $("[data-featured]");
    if (!host) return;
    PROJECTS.filter(function (p) { return p.featured; }).slice(0, 6).forEach(function (p) {
      host.appendChild(projectCard(p, { sizes: "(min-width: 768px) 60vw, 100vw" }));
    });
  }

  function renderDisciplines() {
    var host = $("[data-disciplines]");
    if (!host) return;
    var cursorHost = $("[data-cursor-media]");
    CATEGORIES.forEach(function (c, i) {
      var cover = (projectsOf(c.slug)[0] || PROJECTS[0]).images[0];
      host.appendChild(el("li", { class: "discipline", "data-reveal": true }, [
        el("a", { class: "discipline__link", href: "proyectos.html?cat=" + c.slug, "data-index": i }, [
          el("span", { class: "discipline__num label" }, [String(i + 1).padStart(2, "0")]),
          el("img", { class: "discipline__thumb", src: img(cover, 200), alt: "", loading: "lazy" }),
          el("span", { class: "discipline__name" }, [c.name]),
          el("span", { class: "discipline__lead" }, [c.lead]),
          el("span", { class: "discipline__arrow", "aria-hidden": "true" }, ["→"]),
        ]),
      ]));
      if (cursorHost) cursorHost.appendChild(el("img", { src: img(cover, 700), alt: "", loading: "lazy" }));
    });
  }

  function renderStats() {
    var host = $("[data-stats]");
    if (!host) return;
    (SITE.stats || []).forEach(function (s) {
      var value = el("span", { class: "stat__value", "data-count": s.value, "data-prefix": s.prefix, "data-suffix": s.suffix }, [s.prefix + s.value + s.suffix]);
      host.appendChild(el("div", { class: "stat", "data-reveal": true }, [value, el("p", { class: "stat__label" }, [s.label])]));
    });
  }

  function renderFooterCategories() {
    $$("[data-footer-categories]").forEach(function (host) {
      CATEGORIES.forEach(function (c) {
        host.appendChild(el("li", null, [el("a", { href: "proyectos.html?cat=" + c.slug }, [c.name])]));
      });
    });
  }

  /* ---------- Página: listado de proyectos con filtros ---------- */
  function initProjectsPage() {
    var grid = $("[data-projects-grid]");
    var filters = $("[data-filters]");
    if (!grid || !filters) return;
    var intro = $("[data-category-intro]");

    var requested = new URLSearchParams(location.search).get("cat");
    var current = categoryBySlug[requested] ? requested : "todos";

    var options = [{ slug: "todos", name: "Todos", count: PROJECTS.length }].concat(
      CATEGORIES.map(function (c) { return { slug: c.slug, name: c.name, count: projectsOf(c.slug).length }; })
    );
    options.forEach(function (o) {
      var button = el("button", { class: "filter", type: "button", "data-filter": o.slug, "aria-pressed": String(o.slug === current) }, [
        o.name, el("sup", null, [String(o.count)]),
      ]);
      filters.appendChild(button);
    });

    function paint(animate) {
      var list = current === "todos" ? PROJECTS : projectsOf(current);
      var category = categoryBySlug[current];

      if (intro) {
        intro.textContent = "";
        intro.appendChild(el("span", { class: "label muted" }, [category ? category.name : "Todas las especialidades"]));
        intro.appendChild(el("p", null, [category ? category.lead : "Una selección de proyectos para empresas, locales, oficinas, cocinas, inmobiliarias y hogares."]));
      }

      grid.textContent = "";
      if (!list.length) {
        grid.appendChild(el("p", { class: "empty-state" }, ["Pronto publicaremos proyectos en esta categoría."]));
        return;
      }
      list.forEach(function (p) { grid.appendChild(projectCard(p)); });

      if (motion) {
        if (animate) {
          // Al filtrar: las tarjetas entran en cascada sin esperar el scroll
          var medias = $$("[data-reveal-media]", grid);
          gsap.set(medias, { clipPath: "inset(100% 0% 0% 0%)" });
          gsap.to(medias, { clipPath: "inset(0% 0% 0% 0%)", duration: 1.1, ease: "expo.out", stagger: 0.08 });
          gsap.from($$(".project-card__meta", grid), { opacity: 0, y: 20, duration: 0.8, ease: "expo.out", stagger: 0.08, delay: 0.2 });
          initParallaxCards(grid);
          window.ScrollTrigger.refresh();
        } else {
          initMediaReveals(grid);
          initParallaxCards(grid);
        }
      }
    }

    filters.addEventListener("click", function (event) {
      var button = event.target.closest("[data-filter]");
      if (!button || button.getAttribute("data-filter") === current) return;
      current = button.getAttribute("data-filter");
      $$("[data-filter]", filters).forEach(function (b) { b.setAttribute("aria-pressed", String(b === button)); });
      var url = new URL(location.href);
      if (current === "todos") url.searchParams.delete("cat"); else url.searchParams.set("cat", current);
      history.replaceState(null, "", url);
      paint(true);
      var top = grid.getBoundingClientRect().top + window.scrollY - 160;
      if (window.scrollY > top) scrollToTarget(Math.max(0, top));
    });

    paint(false);
  }

  /* ---------- Página: detalle de proyecto ---------- */
  function initProjectDetail() {
    var page = $("[data-project-detail]");
    if (!page) return;
    var slug = new URLSearchParams(location.search).get("p");
    var index = PROJECTS.findIndex(function (p) { return p.slug === slug; });
    var p = PROJECTS[index];

    if (!p) {
      page.textContent = "";
      page.appendChild(el("section", { class: "page-hero" }, [
        el("h1", { class: "display" }, ["Proyecto no encontrado"]),
        el("p", { class: "page-hero__lead" }, ["Puede que el enlace haya cambiado. Revisa todos nuestros proyectos."]),
        el("p", { class: "page-hero__lead" }, [el("a", { class: "link-line label", href: "proyectos.html" }, ["Ver proyectos →"])]),
      ]));
      return;
    }

    var category = categoryBySlug[p.category];
    document.title = p.title + " — Proyectos | Chile Mármol";
    var meta = $('meta[name="description"]');
    if (meta) meta.setAttribute("content", p.summary);

    var heroImg = $("[data-detail-hero-img]");
    heroImg.src = img(p.images[0], 1600);
    heroImg.srcset = [900, 1600, 2400].map(function (w) { return img(p.images[0], w) + " " + w + "w"; }).join(", ");
    heroImg.alt = p.title + " — " + category.name;

    $("[data-detail-category]").textContent = category.name + " · " + p.location;
    $("[data-detail-title]").textContent = p.title;
    $("[data-detail-summary]").textContent = p.summary;

    var facts = $("[data-detail-facts]");
    [["Categoría", category.name], ["Ubicación", p.location], ["Año", String(p.year)], ["Superficie", p.area], ["Servicios", p.services.join(", ")]]
      .forEach(function (f) {
        facts.appendChild(el("div", null, [el("dt", { class: "label" }, [f[0]]), el("dd", null, [f[1]])]));
      });

    var gallery = $("[data-detail-gallery]");
    p.images.slice(1).forEach(function (ref, i) {
      gallery.appendChild(el("figure", { "data-reveal-media": true }, [
        el("img", { src: img(ref, 1400), srcset: srcset(ref), sizes: "(min-width: 768px) 60vw, 100vw", alt: p.title + " — imagen " + (i + 2), loading: "lazy" }),
      ]));
    });

    // WhatsApp con mensaje específico del proyecto: mejora la conversión
    $$("[data-wa]").forEach(function (a) {
      a.setAttribute("data-wa", "Hola Chile Mármol, vi el proyecto \"" + p.title + "\" y quiero cotizar algo similar.");
    });

    var next = PROJECTS[(index + 1) % PROJECTS.length];
    var nextLink = $("[data-next-project]");
    nextLink.href = "proyecto.html?p=" + encodeURIComponent(next.slug);
    $("[data-next-title]").textContent = next.title;
  }

  /* ---------- Header: se oculta al bajar y aparece al subir ---------- */
  function initHeader() {
    var header = $("[data-header]");
    if (!header) return;
    var lastY = window.scrollY;
    var ticking = false;
    window.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(function () {
        var y = window.scrollY;
        var goingDown = y > lastY && y > 160;
        if (!root.classList.contains("menu-open")) header.classList.toggle("is-hidden", goingDown);
        lastY = y;
        ticking = false;
      });
    }, { passive: true });
  }

  /* ---------- Menú fullscreen ---------- */
  function initMenu() {
    var toggle = $("[data-menu-toggle]");
    var menu = $("[data-menu]");
    if (!toggle || !menu) return;
    var label = $("[data-menu-label]", toggle);
    var links = $$(".menu__link", menu);
    var isOpen = false;

    menu.setAttribute("role", "dialog");
    menu.setAttribute("aria-modal", "true");
    menu.setAttribute("aria-label", "Menú");

    function open() {
      isOpen = true;
      root.classList.add("menu-open");
      toggle.setAttribute("aria-expanded", "true");
      menu.setAttribute("aria-hidden", "false");
      label.textContent = "Cerrar";
      if (lenis) lenis.stop();
      if (motion) {
        gsap.killTweensOf([menu, links]);
        gsap.fromTo(menu, { clipPath: "inset(0% 0% 100% 0%)", visibility: "visible" }, { clipPath: "inset(0% 0% 0% 0%)", duration: 0.9, ease: "expo.inOut" });
        gsap.fromTo(links, { yPercent: 110 }, { yPercent: 0, duration: 1, ease: "expo.out", stagger: 0.06, delay: 0.35 });
      }
      setTimeout(function () { if (links[0]) links[0].focus({ preventScroll: true }); }, motion ? 500 : 0);
    }

    function close(returnFocus) {
      isOpen = false;
      root.classList.remove("menu-open");
      toggle.setAttribute("aria-expanded", "false");
      menu.setAttribute("aria-hidden", "true");
      label.textContent = "Menú";
      if (lenis) lenis.start();
      if (motion) {
        gsap.killTweensOf([menu, links]);
        gsap.to(menu, { clipPath: "inset(0% 0% 100% 0%)", duration: 0.7, ease: "expo.inOut", onComplete: function () { gsap.set(menu, { visibility: "hidden" }); } });
      }
      if (returnFocus) toggle.focus();
    }

    toggle.addEventListener("click", function () { isOpen ? close(true) : open(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && isOpen) close(true); });
    menu.addEventListener("click", function (e) { if (e.target.closest("a")) close(false); });
  }

  /* ---------- Botón flotante de WhatsApp ---------- */
  function initWhatsAppFloat() {
    var wrap = $("[data-wa-float]");
    if (!wrap) return;
    var APPEAR_DELAY = 2000;      // aparece a los 2 s, como pidió el cliente
    var BUBBLE_DELAY = 4500;      // la burbuja aparece poco después
    var BUBBLE_DURATION = 7000;   // y se esconde sola para no molestar

    setTimeout(function () { wrap.classList.add("is-visible"); }, APPEAR_DELAY);

    if (storage("get", "cm-wa-bubble") !== "closed") {
      setTimeout(function () {
        wrap.classList.add("has-bubble");
        setTimeout(function () { wrap.classList.remove("has-bubble"); }, BUBBLE_DURATION);
      }, BUBBLE_DELAY);
    }
    var close = $("[data-wa-close]", wrap);
    if (close) close.addEventListener("click", function () {
      wrap.classList.remove("has-bubble");
      storage("set", "cm-wa-bubble", "closed");
    });
  }

  /* ---------- Transiciones entre páginas ---------- */
  function initPageTransitions() {
    var curtain = $(".curtain");
    if (!curtain) return;

    document.addEventListener("click", function (e) {
      var a = e.target.closest("a[href]");
      if (!a || e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      if (a.target === "_blank" || a.hasAttribute("download")) return;
      var url = new URL(a.href, location.href);
      if (url.origin !== location.origin) return;

      var samePage = url.pathname === location.pathname && url.search === location.search;
      if (samePage && url.hash) {
        // Ancla en la misma página: scroll suave en vez de salto
        var target = document.getElementById(url.hash.slice(1));
        if (target) { e.preventDefault(); scrollToTarget(target); history.replaceState(null, "", url.hash); }
        return;
      }
      if (!motion) return;

      e.preventDefault();
      storage("set", "cm-transition", "1");
      gsap.set(curtain, { yPercent: 100 });
      gsap.to(curtain, { yPercent: 0, duration: 0.7, ease: "expo.inOut", onComplete: function () { location.href = url.href; } });
    });

    // Al volver con el botón "atrás", la página viene del caché con la cortina cerrada
    window.addEventListener("pageshow", function (e) {
      if (e.persisted && motion) gsap.set(curtain, { yPercent: 100 });
    });
  }

  function playEntering(done) {
    var curtain = $(".curtain");
    var entering = root.classList.contains("is-entering");
    storage("remove", "cm-transition");
    if (!motion || !entering || !curtain) { done(); return; }
    gsap.set(curtain, { yPercent: 0 });
    root.classList.remove("is-entering");
    gsap.to(curtain, { yPercent: -100, duration: 0.9, ease: "expo.inOut", delay: 0.05, onComplete: function () { gsap.set(curtain, { yPercent: 100 }); } });
    setTimeout(done, 350);
  }

  /* ---------- Preloader (primera visita) ---------- */
  function playPreloader(done) {
    var pre = $(".preloader");
    var shouldPlay = motion && pre && root.classList.contains("js-preload");
    storage("set", "cm-visited", "1");
    if (!shouldPlay) { root.classList.remove("js-preload"); done(); return; }

    var count = $(".preloader__count", pre);
    var bar = $(".preloader__bar i", pre);
    var state = { v: 0 };
    gsap.timeline({ onComplete: function () { root.classList.remove("js-preload"); } })
      .from($(".preloader__word span", pre), { yPercent: 110, duration: 0.8, ease: "expo.out" })
      .to(state, { v: 100, duration: 1.3, ease: "power2.inOut", onUpdate: function () { count.textContent = Math.round(state.v); } }, 0.1)
      .to(bar, { scaleX: 1, duration: 1.3, ease: "power2.inOut" }, 0.1)
      .to(pre, { yPercent: -100, duration: 1, ease: "expo.inOut" }, "+=0.15")
      .add(done, "-=0.55");
  }

  /* ---------- Animaciones ---------- */
  /* Separa un párrafo en palabras (respetando <span class="script">) */
  function splitWords(node) {
    var words = [];
    Array.prototype.slice.call(node.childNodes).forEach(function (child) {
      if (child.nodeType === 3) {
        var parts = child.textContent.split(/(\s+)/);
        var frag = document.createDocumentFragment();
        parts.forEach(function (part) {
          if (!part) return;
          if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
          var w = el("span", { class: "word" }, [part]);
          words.push(w);
          frag.appendChild(w);
        });
        node.replaceChild(frag, child);
      } else if (child.nodeType === 1) {
        child.classList.add("word");
        words.push(child);
      }
    });
    return words;
  }

  function initMediaReveals(scope) {
    $$("[data-reveal-media]", scope).forEach(function (media) {
      if (media.dataset.revealed) return;
      media.dataset.revealed = "1";
      var zoom = media.querySelector(".project-card__zoom") || media.querySelector("img");
      gsap.timeline({ scrollTrigger: { trigger: media, start: "top 88%", once: true } })
        .to(media, { clipPath: "inset(0% 0% 0% 0%)", duration: 1.4, ease: "expo.inOut" })
        .from(zoom, { scale: 1.35, duration: 1.8, ease: "expo.out", clearProps: "transform" }, 0);
    });
  }

  function initParallaxCards(scope) {
    $$("[data-card-img]", scope).forEach(function (image) {
      gsap.fromTo(image, { yPercent: -6 }, {
        yPercent: 6, ease: "none",
        scrollTrigger: { trigger: image.closest(".project-card__media"), start: "top bottom", end: "bottom top", scrub: true },
      });
    });
  }

  function initHero() {
    var hero = $("[data-hero]");
    if (!hero) return null;
    var media = $("[data-hero-media]", hero);
    var image = $("img", media);
    var content = $(".hero__content", hero);
    var lines = $$(".hero__title .line > span", hero);
    var meta = $(".hero__meta", hero);

    // Intro: se reproduce después del preloader / cortina
    gsap.set(lines, { yPercent: 115 });
    gsap.set(meta, { opacity: 0, y: 24 });
    gsap.set(image, { scale: 1.3 });
    var intro = gsap.timeline({ paused: true })
      .to(image, { scale: 1.12, duration: 2.2, ease: "expo.out" }, 0)
      .to(lines, { yPercent: 0, duration: 1.4, ease: "expo.out", stagger: 0.12 }, 0.1)
      .to(meta, { opacity: 1, y: 0, duration: 1.2, ease: "expo.out" }, 0.5);

    // Al hacer scroll: la imagen se "encoge" hacia un marco y el texto sube
    gsap.timeline({ scrollTrigger: { trigger: hero, start: "top top", end: "bottom top", scrub: true } })
      .to(media, { clipPath: "inset(0% 4% 14% 4% round 12px)", ease: "none" }, 0)
      .to(image, { yPercent: 12, ease: "none" }, 0)
      .to(content, { yPercent: -40, opacity: 0, ease: "none" }, 0);

    return intro;
  }

  function initPageHero() {
    var lines = $$(".page-hero .line > span");
    if (!lines.length) return null;
    gsap.set(lines, { yPercent: 115 });
    return gsap.timeline({ paused: true })
      .to(lines, { yPercent: 0, duration: 1.3, ease: "expo.out", stagger: 0.1 })
      .from(".page-hero__lead, .filters", { opacity: 0, y: 20, duration: 1, ease: "expo.out", stagger: 0.1 }, 0.4);
  }

  function initScrollAnimations() {
    var ST = window.ScrollTrigger;

    // Revelado genérico de bloques
    ST.batch("[data-reveal]", {
      start: "top 88%", once: true,
      onEnter: function (batch) { gsap.to(batch, { opacity: 1, y: 0, duration: 1.2, ease: "expo.out", stagger: 0.1 }); },
    });

    initMediaReveals(document);
    initParallaxCards(document);

    // Manifiesto: las palabras se "encienden" al leerlas
    $$("[data-words], [data-words-light]").forEach(function (node) {
      var words = splitWords(node);
      gsap.fromTo(words, { opacity: node.hasAttribute("data-words-light") ? 0.25 : 0.12 }, {
        opacity: 1, ease: "none", stagger: 0.1,
        scrollTrigger: { trigger: node, start: "top 80%", end: "bottom 45%", scrub: true },
      });
    });

    // Imagen de la cita con parallax
    $$("[data-parallax]").forEach(function (layer) {
      gsap.fromTo(layer, { yPercent: -10 }, {
        yPercent: 10, ease: "none",
        scrollTrigger: { trigger: layer.parentElement, start: "top bottom", end: "bottom top", scrub: true },
      });
    });

    // Contadores
    $$("[data-count]").forEach(function (node) {
      var target = Number(node.getAttribute("data-count"));
      var prefix = node.getAttribute("data-prefix") || "";
      var suffix = node.getAttribute("data-suffix") || "";
      var state = { v: 0 };
      node.textContent = prefix + "0" + suffix;
      gsap.to(state, {
        v: target, duration: 2, ease: "power3.out",
        scrollTrigger: { trigger: node, start: "top 90%", once: true },
        onUpdate: function () { node.textContent = prefix + Math.round(state.v).toLocaleString("es-CL") + suffix; },
      });
    });

    // Proceso: scroll horizontal fijado solo en pantallas grandes
    var mm = gsap.matchMedia();
    mm.add("(min-width: 1024px)", function () {
      var section = $("[data-process]");
      var track = $("[data-process-track]");
      if (!section || !track) return;
      var progress = $("[data-process-progress]");
      function distance() { return Math.max(0, track.scrollWidth - window.innerWidth); }
      var tween = gsap.to(track, {
        x: function () { return -distance(); }, ease: "none",
        scrollTrigger: {
          trigger: section, start: "top top", end: function () { return "+=" + distance(); },
          pin: true, scrub: 1, invalidateOnRefresh: true,
          onUpdate: function (self) { if (progress) gsap.set(progress, { scaleX: self.progress }); },
        },
      });
      $$(".step__media img", track).forEach(function (image) {
        gsap.fromTo(image, { scale: 1.25 }, {
          scale: 1, ease: "none",
          scrollTrigger: { trigger: image, containerAnimation: tween, start: "left right", end: "right left", scrub: true },
        });
      });
    });

    // Palabra gigante del footer
    $$(".footer__word").forEach(function (word) {
      gsap.from(word, { yPercent: 60, ease: "none", scrollTrigger: { trigger: word, start: "top bottom", end: "bottom bottom", scrub: true } });
    });

    // Imagen flotante que sigue al cursor sobre las especialidades
    var list = $("[data-disciplines]");
    var follower = $("[data-cursor-media]");
    if (list && follower && window.matchMedia("(hover: hover) and (pointer: fine) and (min-width: 900px)").matches) {
      var images = $$("img", follower);
      var xTo = gsap.quickTo(follower, "x", { duration: 0.6, ease: "power3" });
      var yTo = gsap.quickTo(follower, "y", { duration: 0.6, ease: "power3" });
      gsap.set(follower, { xPercent: -50, yPercent: -50 });
      list.addEventListener("mousemove", function (e) { xTo(e.clientX); yTo(e.clientY); });
      list.addEventListener("mouseenter", function (e) {
        gsap.set(follower, { x: e.clientX, y: e.clientY });
        gsap.to(follower, { opacity: 1, scale: 1, duration: 0.5, ease: "expo.out" });
      });
      list.addEventListener("mouseleave", function () { gsap.to(follower, { opacity: 0, scale: 0.6, duration: 0.4, ease: "expo.out" }); });
      $$("[data-index]", list).forEach(function (link) {
        link.addEventListener("mouseenter", function () {
          var i = Number(link.getAttribute("data-index"));
          images.forEach(function (image, j) { image.classList.toggle("is-active", i === j); });
        });
      });
    }
  }

  function initLenis() {
    if (!motion || typeof window.Lenis !== "function") return;
    lenis = new window.Lenis({ lerp: 0.09, wheelMultiplier: 1 });
    lenis.on("scroll", window.ScrollTrigger.update);
    gsap.ticker.add(function (time) { lenis.raf(time * 1000); });
    gsap.ticker.lagSmoothing(0);
  }

  /* ---------- Inicio ---------- */
  function init() {
    renderFeatured();
    renderDisciplines();
    renderStats();
    renderFooterCategories();
    initProjectDetail();
    bindContact();
    initHeader();
    initWhatsAppFloat();

    if (!motion) {
      initMenu();
      initPageTransitions();
      initProjectsPage();
      window.__cmReady = true;
      return;
    }

    gsap.registerPlugin(window.ScrollTrigger);
    initLenis();
    initMenu();
    initPageTransitions();
    initProjectsPage();

    var intro = initHero() || initPageHero();
    initScrollAnimations();
    window.__cmReady = true;

    // Si la URL trae un ancla (ej: index.html#contacto), ir ahí al cargar
    if (location.hash) {
      var target = document.getElementById(location.hash.slice(1));
      if (target) setTimeout(function () { scrollToTarget(target); }, 400);
    }

    var start = function () { if (intro) intro.play(); };
    playEntering(function () { playPreloader(start); });

    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { window.ScrollTrigger.refresh(); });
    window.addEventListener("load", function () { window.ScrollTrigger.refresh(); });
  }

  init();
})();
