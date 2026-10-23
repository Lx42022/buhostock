/* =========================================================================
   BuhoStock website - behaviour
   Small on purpose: header border, plan picker, mobile sticky CTA, sign-up form.
   Settings live in assets/config.js (window.BUHO_CONFIG).
   ========================================================================= */
(function () {
  "use strict";

  var config = window.BUHO_CONFIG || {};

  /** Add a border under the sticky header once the page is scrolled. */
  function setupHeader() {
    var header = document.querySelector(".site-header");
    if (!header) return;
    var update = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    update();
    window.addEventListener("scroll", update, { passive: true });
  }

  /** Put the configured contact address into every mailto link. */
  function setupEmailLinks() {
    if (!config.CONTACT_EMAIL) return;
    document.querySelectorAll(".js-email").forEach(function (link) {
      link.href = "mailto:" + config.CONTACT_EMAIL;
      link.textContent = config.CONTACT_EMAIL;
    });
  }

  /**
   * Plan picker: the visitor types how many listings they have and the
   * matching plan gets highlighted (Mini 50 / Starter 150 / Pro 400 / Business 1000).
   */
  function setupPlanPicker() {
    var input = document.getElementById("num-anuncios");
    var output = document.getElementById("picker-out");
    var plans = Array.prototype.slice.call(document.querySelectorAll(".plan[data-max]"));
    if (!input || !output || plans.length === 0) return;

    input.addEventListener("input", function () {
      var count = parseInt(input.value, 10);
      plans.forEach(function (plan) { plan.classList.remove("is-match"); });
      if (!count || count < 1) { output.textContent = ""; return; }
      var match = plans.find(function (plan) { return count <= Number(plan.dataset.max); });
      if (match) {
        match.classList.add("is-match");
        output.textContent = "Tu plan: " + match.querySelector("h3").textContent + ".";
      } else {
        output.textContent = "Más de 1.000: te hacemos un precio a medida.";
      }
    });
  }

  /** Mobile only (CSS hides it on desktop): show a bottom CTA after the hero, hide it at the form. */
  function setupStickyCta() {
    var bar = document.getElementById("sticky-cta");
    var heroCta = document.getElementById("hero-cta");
    var form = document.getElementById("alta");
    if (!bar || !heroCta || !form || !("IntersectionObserver" in window)) return;

    var heroVisible = true;
    var formVisible = false;
    var render = function () { bar.classList.toggle("is-visible", !heroVisible && !formVisible); };
    new IntersectionObserver(function (entries) { heroVisible = entries[0].isIntersecting; render(); }).observe(heroCta);
    new IntersectionObserver(function (entries) { formVisible = entries[0].isIntersecting; render(); }, { rootMargin: "0px 0px -20% 0px" }).observe(form);
  }

  /* ---------------- Sign-up form ---------------- */

  /** Mark one field as wrong (or right) and return whether it is valid. */
  function markField(input, isValid) {
    var wrapper = input.closest(".field") || input.closest(".check");
    if (wrapper) wrapper.classList.toggle("has-error", !isValid);
    input.setAttribute("aria-invalid", isValid ? "false" : "true");
    return isValid;
  }

  /** Spanish mobile/landline number: 9 digits after removing spaces, dots and dashes. */
  function isValidSpanishPhone(value) {
    var digits = value.replace(/[\s.\-()]/g, "").replace(/^(\+34|0034)/, "");
    return /^[6789]\d{8}$/.test(digits);
  }

  /** Check all fields; returns the first invalid element (or null when everything is fine). */
  function validateForm(form) {
    var firstInvalid = null;
    var remember = function (input, ok) { if (!markField(input, ok) && !firstInvalid) firstInvalid = input; };

    var name = form.elements.nombre;
    var email = form.elements.email;
    var profile = form.elements.perfil;
    var phone = form.elements.whatsapp;
    var terms = form.elements.condiciones;

    remember(name, name.value.trim().length >= 2);
    remember(email, /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email.value.trim()));
    remember(profile, profile.value.trim().length >= 2);
    remember(phone, phone.value.trim() === "" || isValidSpanishPhone(phone.value));
    remember(terms, terms.checked);
    return firstInvalid;
  }

  /** Collect the form values that are sent to the Apps Script. */
  function collectData(form, startedAt) {
    return {
      nombre: form.elements.nombre.value.trim(),
      email: form.elements.email.value.trim(),
      perfil: form.elements.perfil.value.trim(),
      anuncios: form.elements.anuncios.value,
      whatsapp: form.elements.whatsapp.value.trim(),
      novedades: form.elements.novedades.checked ? "si" : "no",
      condiciones: form.elements.condiciones.checked ? "si" : "no",
      condiciones_version: config.TERMS_VERSION || "",
      web: form.elements.web.value,               // honeypot, must stay empty
      segundos: String(Math.round((Date.now() - startedAt) / 1000)),
      pagina: location.href.split("#")[0],
    };
  }

  /** Fallback while no Apps Script URL is configured: open a prefilled e-mail. */
  function sendByEmail(data) {
    var body = [
      "Hola, quiero probar BuhoStock.",
      "",
      "Nombre / tienda: " + data.nombre,
      "Correo: " + data.email,
      "Perfil de Wallapop: " + data.perfil,
      "Anuncios: " + (data.anuncios || "-"),
      "WhatsApp: " + (data.whatsapp ? "+34 " + data.whatsapp : "-"),
      "Novedades por correo: " + data.novedades,
      "Condiciones aceptadas: " + data.condiciones + " (versión " + data.condiciones_version + ")",
    ].join("\n");
    location.href = "mailto:" + (config.CONTACT_EMAIL || "") +
      "?subject=" + encodeURIComponent("Quiero probar BuhoStock") +
      "&body=" + encodeURIComponent(body);
  }

  /**
   * Send to the Google Apps Script web app. "no-cors" is needed because Apps
   * Script does not send CORS headers; the response cannot be read, so a
   * network error is the only failure we can detect.
   */
  function sendToAppsScript(data) {
    return fetch(config.APPS_SCRIPT_URL, {
      method: "POST",
      mode: "no-cors",
      headers: { "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8" },
      body: new URLSearchParams(data).toString(),
    });
  }

  /** Replace the form with the thank-you box. */
  function showDone(form, data, viaEmail) {
    var done = document.getElementById("form-done");
    var text = document.getElementById("form-done-text");
    var optin = document.getElementById("form-done-optin");
    if (viaEmail) {
      text.textContent = "Se ha abierto tu programa de correo con tus datos. Envía el mensaje y te escribimos en menos de 48 horas (días laborables).";
    }
    optin.hidden = viaEmail || data.novedades !== "si";
    form.hidden = true;
    done.hidden = false;
    done.focus();
  }

  function setupForm() {
    var form = document.getElementById("signup-form");
    if (!form) return;
    var status = document.getElementById("form-status");
    var button = document.getElementById("signup-submit");
    var startedAt = Date.now();

    // Clear an error as soon as the visitor fixes the field.
    form.addEventListener("input", function (event) {
      var target = event.target;
      var wrapper = target.closest(".has-error");
      if (wrapper) { wrapper.classList.remove("has-error"); target.setAttribute("aria-invalid", "false"); }
    });
    form.addEventListener("change", function (event) {
      if (event.target.name === "condiciones" && event.target.checked) markField(event.target, true);
    });

    form.addEventListener("submit", function (event) {
      event.preventDefault();
      status.textContent = "";
      var firstInvalid = validateForm(form);
      if (firstInvalid) {
        status.textContent = firstInvalid.name === "condiciones"
          ? "Para seguir, acepta las condiciones de uso."
          : "Revisa los campos marcados.";
        firstInvalid.focus();
        return;
      }

      var data = collectData(form, startedAt);
      if (data.web) { showDone(form, data, false); return; }   // bot filled the honeypot: pretend success

      if (!config.APPS_SCRIPT_URL) { sendByEmail(data); showDone(form, data, true); return; }

      button.disabled = true;
      button.textContent = "Enviando…";
      sendToAppsScript(data)
        .then(function () { showDone(form, data, false); })
        .catch(function () {
          status.textContent = "No hemos podido enviarlo. Revisa tu conexión o escríbenos a " + (config.CONTACT_EMAIL || "nuestro correo") + ".";
          button.disabled = false;
          button.textContent = "Quiero probarlo gratis";
        });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    setupHeader();
    setupEmailLinks();
    setupPlanPicker();
    setupStickyCta();
    setupForm();
  });
})();
