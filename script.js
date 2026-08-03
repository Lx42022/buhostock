/* =========================================================================
   Búho / BuhoStock — script de la landing page
   Muy poco JS a propósito: la web es casi toda estática.
   ========================================================================= */

/* -------------------------------------------------------------------------
   👉 CONFIGURACIÓN — EDITA SOLO ESTO
   Cuando tengas tu número y tu email de verdad, cámbialos aquí una sola vez.
   Todos los botones de la web se actualizan solos.
   ------------------------------------------------------------------------- */
const CONFIG = {
  // Número de WhatsApp en formato internacional, SIN "+", SIN espacios.
  // ⚠️ PLACEHOLDER (número inventado para la preview). Cambiar por el real
  //    antes de publicar de verdad. No escribáis a este número.
  whatsappNumber: "34611222333",

  // Email de contacto (aún por crear).
  email: "hola@buhostock.com",

  // Mensaje que aparece ya escrito cuando alguien abre WhatsApp.
  whatsappMessage: "Hola 🦉 He visto la web de Búho y me gustaría saber más.",
};

/* -------------------------------------------------------------------------
   A partir de aquí no hace falta tocar nada.
   ------------------------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  // 1) Rellenar el año actual en el pie.
  const yearSpan = document.getElementById("year");
  if (yearSpan) yearSpan.textContent = new Date().getFullYear();

  // 2) Construir el enlace de WhatsApp y aplicarlo a todos los botones ".js-whatsapp".
  const waHref =
    "https://wa.me/" +
    CONFIG.whatsappNumber +
    "?text=" +
    encodeURIComponent(CONFIG.whatsappMessage);

  document.querySelectorAll(".js-whatsapp").forEach((link) => {
    link.setAttribute("href", waHref);
    link.setAttribute("target", "_blank");
    link.setAttribute("rel", "noopener");
  });

  // 3) Enlace de email a todos los botones ".js-email".
  document.querySelectorAll(".js-email").forEach((link) => {
    link.setAttribute(
      "href",
      "mailto:" +
        CONFIG.email +
        "?subject=" +
        encodeURIComponent("Interés en Búho")
    );
  });

  // 4) Menú móvil (abrir/cerrar).
  const toggle = document.getElementById("navToggle");
  const links = document.getElementById("navLinks");
  if (toggle && links) {
    toggle.addEventListener("click", () => {
      const isOpen = links.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(isOpen));
    });

    // Cerrar el menú al pulsar cualquier enlace (en móvil).
    links.querySelectorAll("a").forEach((a) => {
      a.addEventListener("click", () => {
        links.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }
});
