/* =========================================================================
   BuhoStock website - configuration (the only file you normally edit)
   ========================================================================= */
window.BUHO_CONFIG = {
  // URL of the deployed Google Apps Script web app (ends with /exec).
  // Empty = the form falls back to opening a prefilled e-mail to CONTACT_EMAIL.
  // How to create it: grok-bot-opensource/website-entwurf/apps-script/EINRICHTEN.md (KI-Firma repo)
  APPS_SCRIPT_URL: "",

  // Public contact address shown on the page and used by the fallback.
  // Switch to hola@buhostock.com once the domain forwarding is confirmed (F-6).
  CONTACT_EMAIL: "buhostock.team@gmail.com",

  // Version of the terms the visitor accepts (stored with every sign-up).
  TERMS_VERSION: "2026-10-23",
};
