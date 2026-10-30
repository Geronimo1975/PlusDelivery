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
// Trei straturi, fara suprapuneri:
//   1) Tranzitie de pagina: <main> intra (fade + ridicare) la fiecare incarcare.
//   2) Stagger: grupurile de carduri (.grid, .footer-grid) apar in cascada.
//   3) Reveal: elementele razlete de sub fold (sectiuni text, carduri solo).
// Strajuit de o regula: procesam DOAR ce e sub fold la incarcare, ca sa nu se
// bata cu tranzitia de pagina pe primul ecran.
//
// INLOCUIESTE IN PRODUCTIE: pentru independenta totala de retea, gazduieste
// local pachetul `motion` (self-host /static) in loc de CDN-ul jsDelivr.
// ===========================================================================
import { animate, inView, hover, press } from "https://cdn.jsdelivr.net/npm/motion@14.2.0/+esm";

const REDUCE = window.matchMedia
  && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

// Curba „ease-out" lina (fara bounce) — ton sobru.
const EASE = [0.22, 1, 0.36, 1];
const STAGGER_SEL = ".grid, .footer-grid, [data-stagger]";

// Un element e „sub fold" daca partea lui de sus e dincolo de ~90% din ecran.
function belowFold(el) {
  return el.getBoundingClientRect().top > window.innerHeight * 0.9;
}

// --- 1. Tranzitie de pagina: <main> intra la incarcare ---------------------
function pageEnter() {
  const main = document.querySelector("main");
  if (!main) return;
  animate(
    main,
    { opacity: [0, 1], transform: ["translateY(10px)", "translateY(0)"] },
    { duration: 0.4, easing: EASE }
  );
}

// --- 2. Stagger pe grupurile de carduri ------------------------------------
// Copiii directi ai unui container-grup apar unul dupa altul. Intoarce setul
// de elemente deja tratate, ca reveal-ul sa nu le mai atinga.
function staggerGroups(handled) {
  document.querySelectorAll(STAGGER_SEL).forEach((group) => {
    if (group.closest("[data-no-motion]")) return;
    const kids = Array.from(group.children);
    kids.forEach((k) => handled.add(k));

    // Pe primul fold le lasam pe seama tranzitiei de pagina.
    if (!belowFold(group)) return;

    kids.forEach((k) => { k.style.opacity = "0"; });
    let done = false;
    inView(group, () => {
      if (done) return;
      done = true;
      kids.forEach((k, i) => {
        animate(
          k,
          { opacity: [0, 1], transform: ["translateY(14px)", "translateY(0)"] },
          { duration: 0.4, delay: i * 0.08, easing: EASE }
        );
      });
    }, { amount: 0.15 });
  });
}

// --- 3. Reveal pentru elementele razlete de sub fold -----------------------
function reveal(handled) {
  const SEL = "[data-reveal], .mkt main > section, .card, .stat, .hist-item";
  const els = Array.from(document.querySelectorAll(SEL)).filter((el) => {
    if (handled.has(el)) return false;                 // deja in stagger
    if (el.closest("[data-no-motion]")) return false;
    if (el.closest(STAGGER_SEL) && el.matches(".card")) return false; // card din grid
    // Sectiunile care contin un grup sunt lasate grupului (altfel dublare).
    if (el.matches(".mkt main > section") && el.querySelector(STAGGER_SEL)) return false;
    if (!belowFold(el)) return false;                  // primul fold => page enter
    return true;
  });

  els.forEach((el) => {
    el.style.opacity = "0";
    let done = false;
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

// --- 4. Micro-interactiuni: hover + press pe butoane -----------------------
function microInteractions() {
  document.querySelectorAll(".btn, [data-motion-press]").forEach((el) => {
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
  const handled = new Set();
  try { pageEnter(); } catch (e) { /* fail-safe */ }
  try { staggerGroups(handled); } catch (e) { /* fail-safe */ }
  try { reveal(handled); } catch (e) { /* fail-safe */ }
  try { microInteractions(); } catch (e) { /* fail-safe */ }
}

if (document.readyState !== "loading") init();
else document.addEventListener("DOMContentLoaded", init);
