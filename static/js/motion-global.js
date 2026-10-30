// ===========================================================================
// Motion (fost Framer Motion) — integrare GLOBALA, API vanilla JS (ESM via CDN).
// Tema Swiss/minimalist => miscari SUBTILE si scurte. Respecta
// prefers-reduced-motion si e fail-safe: daca modulul nu se incarca (CDN picat),
// continutul ramane vizibil, pentru ca ascundem elementele doar din JS, dupa
// ce Motion s-a incarcat cu succes.
//
// De ce vanilla si nu `motion.div` (React): proiectul e Django + JS vanilla,
// fara React/build. Motion ofera acelasi motor de animatie prin API-ul imperativ.
//
// INLOCUIESTE IN PRODUCTIE: pentru independenta totala de retea, gazduieste
// local pachetul `motion` (self-host /static) in loc de CDN-ul jsDelivr.
// ===========================================================================
import { animate, inView, hover, press } from "https://cdn.jsdelivr.net/npm/motion@14.2.0/+esm";

const REDUCE = window.matchMedia
  && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Curba „ease-out" lina (fara bounce) — potrivita pentru un ton sobru.
const EASE = [0.22, 1, 0.36, 1];

// --- 1. Reveal la scroll (fade + ridicare usoara) --------------------------
// Tinta: sectiunile de marketing, cardurile si orice element marcat [data-reveal].
// Un element din [data-no-motion] e sarit complet.
function reveal() {
  const SEL = "[data-reveal], .mkt main > section, .card, .stat, .hist-item";
  const els = Array.from(document.querySelectorAll(SEL))
    .filter((el) => !el.closest("[data-no-motion]"));

  // Ascundem abia acum (JS confirmat activ) ca sa nu lasam continut invizibil
  // daca scriptul nu ruleaza.
  els.forEach((el) => { el.style.opacity = "0"; });

  els.forEach((el) => {
    let done = false; // o singura data: nu reanima la re-derulare
    inView(el, () => {
      if (done) return;
      done = true;
      animate(
        el,
        { opacity: [0, 1], transform: ["translateY(16px)", "translateY(0)"] },
        { duration: 0.45, easing: EASE }
      );
    }, { amount: 0.2 });
  });
}

// --- 2. Micro-interactiuni: hover + press pe butoane -----------------------
// Doar pe .btn (si [data-motion-press]) ca sa ramana discret — nu pe orice
// buton-iconita sau rand de lista.
function microInteractions() {
  const els = document.querySelectorAll(".btn, [data-motion-press]");
  els.forEach((el) => {
    hover(el, (element) => {
      animate(element, { scale: 1.03 }, { duration: 0.18, easing: "ease-out" });
      return () => animate(element, { scale: 1 }, { duration: 0.22, easing: "ease-out" });
    });
    press(el, (element) => {
      animate(element, { scale: 0.97 }, { duration: 0.1 });
      return () => animate(element, { scale: 1 }, { type: "spring", stiffness: 400, damping: 22 });
    });
  });
}

function init() {
  if (REDUCE) return; // accesibilitate: nicio animatie
  try { reveal(); } catch (e) { /* fail-safe: continutul ramane asa cum e */ }
  try { microInteractions(); } catch (e) { /* idem */ }
}

if (document.readyState !== "loading") init();
else document.addEventListener("DOMContentLoaded", init);
