/* =========================================================================
   BuhoStock website - behaviour
   Small on purpose: header border, plan picker, mobile sticky CTA, sign-up form.
   Settings live in assets/config.js (window.BUHO_CONFIG).
   ========================================================================= */
(function () {
  "use strict";

  var config = window.BUHO_CONFIG || {};

  /* Texts the script writes into the page, per language (<html lang="..">). */
  var STRINGS = {
    es: {
      yourPlan: "Tu plan: ", custom: "Más de 1.000: te hacemos un precio a medida.",
      acceptTerms: "Para seguir, acepta las condiciones de uso.", checkFields: "Revisa los campos marcados.",
      sending: "Enviando…", submit: "Quiero probarlo gratis",
      sendError: "No hemos podido enviarlo. Revisa tu conexión o escríbenos a ",
      mailOpened: "Se ha abierto tu programa de correo con tus datos. Envía el mensaje y te escribimos en menos de 48 horas (días laborables).",
      mailSubject: "Quiero probar BuhoStock", mailIntro: "Hola, quiero probar BuhoStock.",
      labels: ["Nombre / tienda", "Correo", "Perfil de Wallapop", "Anuncios", "WhatsApp", "Novedades por correo", "Condiciones aceptadas", "versión", "PC encendido de noche"],
    },
    en: {
      yourPlan: "Your plan: ", custom: "More than 1,000: we'll make you a custom price.",
      acceptTerms: "To continue, please accept the terms of use.", checkFields: "Please check the highlighted fields.",
      sending: "Sending…", submit: "Try it for free",
      sendError: "We couldn't send it. Check your connection or write to us at ",
      mailOpened: "Your e-mail program has opened with your details. Send the message and we'll get back to you within 48 hours (working days).",
      mailSubject: "I want to try BuhoStock", mailIntro: "Hello, I want to try BuhoStock.",
      labels: ["Name / shop", "E-mail", "Wallapop profile", "Listings", "WhatsApp", "News by e-mail", "Terms accepted", "version", "PC on at night"],
    },
    de: {
      yourPlan: "Dein Plan: ", custom: "Mehr als 1.000: Wir machen dir einen individuellen Preis.",
      acceptTerms: "Bitte akzeptiere die Nutzungsbedingungen, um fortzufahren.", checkFields: "Bitte prüfe die markierten Felder.",
      sending: "Wird gesendet …", submit: "Gratis testen",
      sendError: "Senden hat nicht geklappt. Prüfe deine Verbindung oder schreib uns an ",
      mailOpened: "Dein E-Mail-Programm hat sich mit deinen Daten geöffnet. Schick die Nachricht ab, wir melden uns innerhalb von 48 Stunden (Werktage).",
      mailSubject: "Ich möchte BuhoStock testen", mailIntro: "Hallo, ich möchte BuhoStock testen.",
      labels: ["Name / Shop", "E-Mail", "Wallapop-Profil", "Anzeigen", "WhatsApp", "Neuigkeiten per E-Mail", "Bedingungen akzeptiert", "Version", "PC nachts an"],
    },
  };
  var lang = (document.documentElement.lang || "es").slice(0, 2);
  var text = STRINGS[lang] || STRINGS.es;

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
        output.textContent = text.yourPlan + match.querySelector("h3").textContent + ".";
      } else {
        output.textContent = text.custom;
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
    var nightPc = form.elements.pc_noche;

    remember(name, name.value.trim().length >= 2);
    remember(email, /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email.value.trim()));
    remember(profile, profile.value.trim().length >= 2);
    remember(nightPc, /^(windows|mac|no)$/.test(nightPc.value));
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
      pc_noche: form.elements.pc_noche.value,     // windows | mac | no (required)
      whatsapp: form.elements.whatsapp.value.trim(),
      novedades: form.elements.novedades.checked ? "si" : "no",
      condiciones: form.elements.condiciones.checked ? "si" : "no",
      condiciones_version: config.TERMS_VERSION || "",
      web: form.elements.web.value,               // honeypot, must stay empty
      segundos: String(Math.round((Date.now() - startedAt) / 1000)),
      pagina: location.href.split("#")[0],
      idioma: lang,
    };
  }

  /** Fallback while no Apps Script URL is configured: open a prefilled e-mail. */
  function sendByEmail(data) {
    var label = text.labels;
    var body = [
      text.mailIntro,
      "",
      label[0] + ": " + data.nombre,
      label[1] + ": " + data.email,
      label[2] + ": " + data.perfil,
      label[3] + ": " + (data.anuncios || "-"),
      label[8] + ": " + data.pc_noche,
      label[4] + ": " + (data.whatsapp ? "+34 " + data.whatsapp : "-"),
      label[5] + ": " + data.novedades,
      label[6] + ": " + data.condiciones + " (" + label[7] + " " + data.condiciones_version + ", " + data.idioma + ")",
    ].join("\n");
    location.href = "mailto:" + (config.CONTACT_EMAIL || "") +
      "?subject=" + encodeURIComponent(text.mailSubject) +
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
    var doneText = document.getElementById("form-done-text");
    var optin = document.getElementById("form-done-optin");
    if (viaEmail) {
      doneText.textContent = text.mailOpened;
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
          ? text.acceptTerms
          : text.checkFields;
        firstInvalid.focus();
        return;
      }

      var data = collectData(form, startedAt);
      if (data.web) { showDone(form, data, false); return; }   // bot filled the honeypot: pretend success

      if (!config.APPS_SCRIPT_URL) { sendByEmail(data); showDone(form, data, true); return; }

      button.disabled = true;
      button.textContent = text.sending;
      sendToAppsScript(data)
        .then(function () { showDone(form, data, false); })
        .catch(function () {
          status.textContent = text.sendError + (config.CONTACT_EMAIL || "") + ".";
          button.disabled = false;
          button.textContent = text.submit;
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
