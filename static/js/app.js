// ===========================================================================
// PlusDelivery - logica frontend (fara framework, doar JavaScript modern).
// Flux: autentificare -> dashboard dupa rol (client sau sofer).
// Model inspirat de Lalamove: portaluri separate pentru clienti si soferi,
// pret instant, comanda si urmarire live. Toate textele sunt in STR.
// ===========================================================================

// ---- TEXTE / i18n: germana (implicit), engleza, romana --------------------
// Modifica textele mai jos; limba implicita este DE, alternativele EN si RO.
const DICT = {
  de: {
    common: { error: "Fehler" },
    auth: {
      welcome: "Willkommen bei PlusDelivery",
      sub: "Melde dich an oder erstelle ein Konto, um fortzufahren.",
      tabLogin: "Anmelden", tabRegister: "Neues Konto",
      role: "Ich möchte mich registrieren als", asClient: "Kunde", asDriver: "Fahrer",
      name: "Vollständiger Name", email: "E-Mail", password: "Passwort (mind. 6 Zeichen)",
      phone: "Telefon (optional)", company: "Firma (optional)",
      business: "Geschäftskonto (viele Lieferungen)",
      vehicle: "Dein Fahrzeug",
      doLogin: "Anmelden", doRegister: "Konto erstellen",
      logout: "Abmelden",
      roleClientHint: "Du bestellst Lieferungen und verfolgst sie live.",
      roleDriverHint: "Du erhältst Aufträge und lieferst nach deinem Zeitplan.",
      roleClient: "Kunde", roleDriver: "Fahrer", roleBusiness: "Business",
    },
    client: {
      title: "Lieferung bestellen",
      sub: "Wähle Service, Route und Fahrzeug. Der Preis wird sofort berechnet.",
      service: "Serviceart",
      from: "Abholung von",
      to: "Lieferung an",
      choose: "Wählen...",
      addrPh: "Adresse eingeben oder einen Ort wählen...",
      typeMore: "Mindestens 3 Zeichen eingeben...",
      noMatch: "Keine Adresse im Raum Hamburg gefunden.",
      outArea: "Die Adresse liegt außerhalb des Servicegebiets (100 km um Hamburg).",
      pickAddr: "Wähle Abhol- und Lieferadresse.",
      note: "Paketdetails (optional)",
      notePh: "Z. B. 2 Kartons, ca. 15 kg, zerbrechlich",
      contact: "Kontakttelefon (optional)",
      getQuote: "Preis anzeigen",
      vehicles: "Fahrzeug wählen",
      book: "Jetzt bestellen",
      tracking: "Meine Bestellungen",
      noOrders: "Du hast noch keine Bestellung. Erstelle links eine.",
      delivered: "wurde geliefert!",
      rateTitle: "Wie war es? Bewerte den Fahrer:",
      rated: "Du hast bewertet",
      thanks: "Danke für deine Bewertung!",
      domain: "Bereich", domainAny: "Allgemein (ohne Sonderanforderungen)",
      stopsLabel: "Zwischenstopps (optional)",
      addStop: "Stopp hinzufügen",
      stopPh: "Stoppadresse oder Ort...",
      removeStop: "Stopp entfernen",
      moveUp: "Nach oben",
      moveDown: "Nach unten",
      activeOrders: "Aktive Bestellungen",
      history: "Lieferverlauf",
      noHistory: "Noch keine abgeschlossene Lieferung.",
      stopsBadge: (n) => `${n} ${n === 1 ? "Stopp" : "Stopps"}`,
      mapStop: "Stopp",
      mapPickup: "Abholung", mapDrop: "Lieferung",
      detailsStep: "Lieferdetails",
      fillRoute: (q) => `Route ergänzen und „${q}“ drücken.`,
      routeChanged: (q) => `Route geändert — „${q}“ erneut drücken.`,
      orderCreated: (id) => `Bestellung erstellt: ${id}. Wir suchen einen Fahrer...`,
      schedTime: "Lieferzeit",
      schedNow: "Sofort", schedLater: "Planen",
      schedAt: "Datum und Uhrzeit",
      schedBadge: "Geplant",
      schedFor: (dt) => `Geplant für ${dt}`,
      orderScheduled: (id, dt) => `Bestellung ${id} geplant für ${dt}.`,
    },
    business: {
      title: "Business-Dashboard", total: "Bestellungen gesamt", active: "Aktiv", done: "Geliefert",
      revenue: "Auftragswert", drivers: "Fahrer online",
      bulk: "Sammelbestellung (Demo)",
      bulkHint: "In einem echten Produkt würdest du hier eine CSV mit Dutzenden Lieferungen importieren. Der Button erzeugt 3 Demo-Bestellungen auf zufälligen Routen.",
      genBulk: "3 Demo-Bestellungen erzeugen",
      demoNote: "Business-Demo-Bestellung", bulkDone: "3 Demo-Bestellungen erzeugt.",
    },
    driver: {
      title: "Fahrer-Dashboard",
      sub: "Verfügbare Aufträge erhalten und den Lieferstatus aktualisieren.",
      available: "Verfügbare Aufträge",
      mine: "Meine aktiven Aufträge",
      accept: "Annehmen",
      advance: "Status weiterschalten",
      none: "Derzeit keine Aufträge verfügbar.",
      noneMine: "Du hast keine aktiven Aufträge.",
      statusOnline: "Du bist online — du erhältst Aufträge",
      statusOffline: "Du bist offline — keine neuen Aufträge",
      earnings: "Verdienst (geliefert)", delivered: "Abgeschlossene Lieferungen", onlineLbl: "Status",
      newOrder: "Neue Bestellung verfügbar!",
      earnChart: "Verdienst pro Tag (letzte 7)",
      earnTotal7: "Summe 7 Tage",
      earnTable: "Daten als Tabelle anzeigen",
      earnDay: "Tag", earnSum: "Verdienst", earnCount: "Lieferungen",
      noEarn: "Noch keine abgeschlossene Lieferung.",
      accepted: "Bestellung angenommen.",
      vehTitle: "Fahrzeug & Fähigkeiten",
      vehClass: "Fahrzeugklasse", vehCaps: "Fähigkeiten (was du transportieren kannst)",
      vehLabel: "Bezeichnung", vehPlate: "Kennzeichen",
      vehResp: "Ich übernehme die Verantwortung für diese Transportart.",
      vehSave: "Fahrzeug speichern", vehSaved: "Fahrzeug gespeichert.",
      vehNone: "Noch kein Fahrzeug. Lege eines an, um passende Aufträge zu sehen.",
      vehDoc: "benötigt Nachweis",
      vehFilter: "Du siehst nur Aufträge, die dein Fahrzeug transportieren darf.",
      vehPending: "In Prüfung — du erhältst Aufträge nach der Freigabe.",
      vehVerifiedLbl: "Verifiziert — du erhältst passende Aufträge.",
      vehRejected: "Antrag abgelehnt. Bitte Support kontaktieren.",
    },
  },
  en: {
    common: { error: "Error" },
    auth: {
      welcome: "Welcome to PlusDelivery",
      sub: "Log in or create an account to continue.",
      tabLogin: "Log in", tabRegister: "Sign up",
      role: "I want to register as", asClient: "Customer", asDriver: "Driver",
      name: "Full name", email: "Email", password: "Password (min. 6 characters)",
      phone: "Phone (optional)", company: "Company (optional)",
      business: "Business account (I send many deliveries)",
      vehicle: "Your vehicle",
      doLogin: "Log in", doRegister: "Create account",
      logout: "Log out",
      roleClientHint: "Order deliveries and track them live.",
      roleDriverHint: "Receive orders and deliver on your own schedule.",
      roleClient: "Customer", roleDriver: "Driver", roleBusiness: "Business",
    },
    client: {
      title: "Order a delivery",
      sub: "Choose the service, route and vehicle. The price is calculated instantly.",
      service: "Service type",
      from: "Pickup from",
      to: "Deliver to",
      choose: "Choose...",
      addrPh: "Type an address or pick a landmark...",
      typeMore: "Type at least 3 characters...",
      noMatch: "No address found in the Hamburg area.",
      outArea: "Address is outside the service area (100 km around Hamburg).",
      pickAddr: "Choose a pickup and a delivery address.",
      note: "Parcel details (optional)",
      notePh: "E.g. 2 boxes, approx. 15 kg, fragile",
      contact: "Contact phone (optional)",
      getQuote: "See price",
      vehicles: "Choose a vehicle",
      book: "Order now",
      tracking: "My orders",
      noOrders: "You have no orders yet. Create one on the left.",
      delivered: "has been delivered!",
      rateTitle: "How was it? Rate the driver:",
      rated: "You rated",
      thanks: "Thanks for your rating!",
      domain: "Domain", domainAny: "General (no special requirements)",
      stopsLabel: "Intermediate stops (optional)",
      addStop: "Add stop",
      stopPh: "Stop address or landmark...",
      removeStop: "Remove stop",
      moveUp: "Move up",
      moveDown: "Move down",
      activeOrders: "Active orders",
      history: "Delivery history",
      noHistory: "No completed deliveries yet.",
      stopsBadge: (n) => `${n} ${n === 1 ? "stop" : "stops"}`,
      mapStop: "Stop",
      mapPickup: "Pickup", mapDrop: "Delivery",
      detailsStep: "Delivery details",
      fillRoute: (q) => `Complete the route and press “${q}”.`,
      routeChanged: (q) => `Route changed — press “${q}” again.`,
      orderCreated: (id) => `Order created: ${id}. Looking for a driver...`,
      schedTime: "Delivery time",
      schedNow: "Now", schedLater: "Schedule",
      schedAt: "Date and time",
      schedBadge: "Scheduled",
      schedFor: (dt) => `Scheduled for ${dt}`,
      orderScheduled: (id, dt) => `Order ${id} scheduled for ${dt}.`,
    },
    business: {
      title: "Business dashboard", total: "Total orders", active: "Active", done: "Delivered",
      revenue: "Order value", drivers: "Drivers online",
      bulk: "Bulk order (demo)",
      bulkHint: "In a real product you'd import a CSV with dozens of deliveries here. The button generates 3 demo orders on random routes.",
      genBulk: "Generate 3 demo orders",
      demoNote: "Business demo order", bulkDone: "3 demo orders generated.",
    },
    driver: {
      title: "Driver dashboard",
      sub: "Receive available orders and update the delivery status.",
      available: "Available orders",
      mine: "My active orders",
      accept: "Accept",
      advance: "Advance status",
      none: "No orders available right now.",
      noneMine: "You have no active orders.",
      statusOnline: "You're online — receiving orders",
      statusOffline: "You're offline — no new orders",
      earnings: "Earnings (delivered)", delivered: "Completed deliveries", onlineLbl: "Status",
      newOrder: "New order available!",
      earnChart: "Earnings per day (last 7)",
      earnTotal7: "7-day total",
      earnTable: "View data as table",
      earnDay: "Day", earnSum: "Earnings", earnCount: "Deliveries",
      noEarn: "No completed deliveries yet.",
      accepted: "Order accepted.",
      vehTitle: "Vehicle & capabilities",
      vehClass: "Vehicle class", vehCaps: "Capabilities (what you can carry)",
      vehLabel: "Label", vehPlate: "Plate",
      vehResp: "I take responsibility for this type of transport.",
      vehSave: "Save vehicle", vehSaved: "Vehicle saved.",
      vehNone: "No vehicle yet. Add one to see matching jobs.",
      vehDoc: "needs document",
      vehFilter: "You only see jobs your vehicle is allowed to carry.",
      vehPending: "In review — you will get jobs after approval.",
      vehVerifiedLbl: "Verified — you receive matching jobs.",
      vehRejected: "Application rejected. Please contact support.",
    },
  },
  ro: {
    common: { error: "Eroare" },
    auth: {
      welcome: "Bine ai venit la PlusDelivery",
      sub: "Autentifica-te sau creeaza un cont ca sa continui.",
      tabLogin: "Autentificare", tabRegister: "Cont nou",
      role: "Vreau sa ma inregistrez ca", asClient: "Client", asDriver: "Sofer",
      name: "Nume complet", email: "Email", password: "Parola (min. 6 caractere)",
      phone: "Telefon (optional)", company: "Companie (optional)",
      business: "Cont business (trimit multe livrari)",
      vehicle: "Vehiculul tau",
      doLogin: "Intra in cont", doRegister: "Creeaza cont",
      logout: "Iesire",
      roleClientHint: "Comanzi livrari si le urmaresti live.",
      roleDriverHint: "Primesti comenzi si le livrezi dupa programul tau.",
      roleClient: "Client", roleDriver: "Sofer", roleBusiness: "Business",
    },
    client: {
      title: "Comanda o livrare",
      sub: "Alege serviciul, ruta si vehiculul. Pretul se calculeaza instant.",
      service: "Tip de serviciu",
      from: "Ridicare de la",
      to: "Livrare la",
      choose: "Alege...",
      addrPh: "Scrie o adresa sau alege un reper...",
      typeMore: "Scrie cel putin 3 litere...",
      noMatch: "Nicio adresa gasita in zona Hamburg.",
      outArea: "Adresa este in afara zonei de serviciu (100 km Hamburg).",
      pickAddr: "Alege adresa de ridicare si de livrare.",
      note: "Detalii colet (optional)",
      notePh: "Ex: 2 cutii, aprox. 15 kg, fragil",
      contact: "Telefon de contact (optional)",
      getQuote: "Vezi pretul",
      vehicles: "Alege vehiculul",
      book: "Comanda acum",
      tracking: "Comenzile mele",
      noOrders: "Nu ai nicio comanda inca. Creeaza una din stanga.",
      delivered: "a fost livrata!",
      rateTitle: "Cum a fost? Evalueaza soferul:",
      rated: "Ai evaluat",
      thanks: "Multumim pentru evaluare!",
      domain: "Domeniu", domainAny: "General (fără cerințe speciale)",
      stopsLabel: "Opriri intermediare (optional)",
      addStop: "Adauga oprire",
      stopPh: "Adresa oprire sau reper...",
      removeStop: "Sterge oprirea",
      moveUp: "Muta mai sus",
      moveDown: "Muta mai jos",
      activeOrders: "Comenzi active",
      history: "Istoric livrari",
      noHistory: "Nicio livrare finalizata inca.",
      stopsBadge: (n) => `${n} ${n === 1 ? "oprire" : "opriri"}`,
      mapStop: "Oprire",
      mapPickup: "Ridicare", mapDrop: "Livrare",
      detailsStep: "Detalii livrare",
      fillRoute: (q) => `Completeaza ruta si apasa „${q}“.`,
      routeChanged: (q) => `Ruta s-a schimbat — apasa „${q}“.`,
      orderCreated: (id) => `Comanda creata: ${id}. Cautam un sofer...`,
      schedTime: "Timp livrare",
      schedNow: "Acum", schedLater: "Programeaza",
      schedAt: "Data si ora",
      schedBadge: "Programat",
      schedFor: (dt) => `Programat pentru ${dt}`,
      orderScheduled: (id, dt) => `Comanda ${id} programata pentru ${dt}.`,
    },
    business: {
      title: "Panou business", total: "Comenzi totale", active: "Active", done: "Livrate",
      revenue: "Valoare comenzi", drivers: "Soferi online",
      bulk: "Comanda in serie (demo)",
      bulkHint: "Intr-un produs real, aici ai importa un CSV cu zeci de livrari. Butonul genereaza 3 comenzi demo pe rute aleatorii.",
      genBulk: "Genereaza 3 comenzi demo",
      demoNote: "Comanda business demo", bulkDone: "3 comenzi demo generate.",
    },
    driver: {
      title: "Panou sofer",
      sub: "Primeste comenzi disponibile si actualizeaza starea livrarii.",
      available: "Comenzi disponibile",
      mine: "Comenzile mele active",
      accept: "Accepta",
      advance: "Avanseaza starea",
      none: "Nicio comanda disponibila momentan.",
      noneMine: "Nu ai comenzi active.",
      statusOnline: "Esti online — primesti comenzi",
      statusOffline: "Esti offline — nu primesti comenzi noi",
      earnings: "Castig (livrate)", delivered: "Livrari finalizate", onlineLbl: "Status",
      newOrder: "Comanda noua disponibila!",
      earnChart: "Castig pe zile (ultimele 7)",
      earnTotal7: "Total 7 zile",
      earnTable: "Vezi datele in tabel",
      earnDay: "Ziua", earnSum: "Castig", earnCount: "Livrari",
      noEarn: "Inca nicio livrare finalizata.",
      accepted: "Comanda acceptata.",
      vehTitle: "Vehicul & capabilități",
      vehClass: "Clasă vehicul", vehCaps: "Capabilități (ce poți transporta)",
      vehLabel: "Denumire", vehPlate: "Număr înmatriculare",
      vehResp: "Îmi asum răspunderea pentru acest tip de transport.",
      vehSave: "Salvează vehiculul", vehSaved: "Vehicul salvat.",
      vehNone: "Niciun vehicul încă. Adaugă unul ca să vezi comenzile potrivite.",
      vehDoc: "necesită document",
      vehFilter: "Vezi doar comenzile pe care vehiculul tău are voie să le ducă.",
      vehPending: "În verificare — vei primi comenzi după aprobare.",
      vehVerifiedLbl: "Verificat — primești comenzile potrivite.",
      vehRejected: "Cerere respinsă. Contactează suportul.",
    },
  },
};

// ---- Limba activa: localStorage -> limba browserului -> germana -----------
const LANGS = ["de", "en", "ro"];
const LOCALES = { de: "de-DE", en: "en-GB", ro: "ro-RO" };
function pickLang() {
  const saved = localStorage.getItem("pd-lang");
  if (LANGS.includes(saved)) return saved;
  const nav = (navigator.language || "").slice(0, 2).toLowerCase();
  return LANGS.includes(nav) ? nav : "de";
}
const LANG = pickLang();
const LOCALE = LOCALES[LANG];
const STR = DICT[LANG];
document.documentElement.lang = LANG;

// ---- Iconite SVG (fara emoji) --------------------------------------------
const IC = {
  bicicleta: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="6" cy="17" r="3.5"/><circle cx="18" cy="17" r="3.5"/><path d="M6 17l4-7h5l-3 7M10 10l-1.5-3H6.5M15 10l2-3h2"/></svg>',
  scuter: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="6" cy="17" r="3"/><circle cx="18" cy="17" r="3"/><path d="M6 17h7l2-7h3M9 10h5M13 7h4l1 3"/></svg>',
  masina: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 13l2-5h11l3 5M2 13h20v4H2zM5 17v2M19 17v2"/><circle cx="7" cy="15" r="1"/><circle cx="17" cy="15" r="1"/></svg>',
  transporter: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 6h12v10H2zM14 9h4l3 3v4h-7z"/><circle cx="6" cy="18" r="1.6"/><circle cx="17" cy="18" r="1.6"/></svg>',
  camion35: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 5h13v11H2zM15 8h4l3 4v4h-7z"/><circle cx="6" cy="18" r="1.6"/><circle cx="18" cy="18" r="1.6"/></svg>',
  camion75: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 4h14v12H2zM16 7h4l3 5v4h-7z"/><circle cx="6" cy="18" r="1.7"/><circle cx="19" cy="18" r="1.7"/></svg>',
  check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M20 6L9 17l-5-5"/></svg>',
  pin: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 21s7-6 7-11a7 7 0 1 0-14 0c0 5 7 11 7 11z"/><circle cx="12" cy="10" r="2.3"/></svg>',
  arrow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
  user: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg>',
  logout: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/></svg>',
  plus: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>',
  x: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>',
  up: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M18 15l-6-6-6 6"/></svg>',
  down: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M6 9l6 6 6-6"/></svg>',
};
const vehIcon = (id) => IC[id] || IC.masina;

// ---- API helper ----------------------------------------------------------
// Citeste un cookie (ex. token-ul CSRF pus de Django la incarcarea paginii).
function getCookie(name) {
  const m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
  return m ? decodeURIComponent(m.pop()) : "";
}
const api = {
  async get(url) { return (await fetch(url)).json(); },
  async post(url, body) {
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
      body: JSON.stringify(body || {}),
    });
    const data = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(data.error || STR.common.error);
    return data;
  },
};

let CONFIG = null; // date de referinta (vehicule, locatii, flow)
const toast = (msg) => {
  const t = document.getElementById("toast");
  t.textContent = msg; t.classList.add("show");
  clearTimeout(t._t); t._t = setTimeout(() => t.classList.remove("show"), 2600);
};
const eur = (n) => Number(n).toLocaleString(LOCALE, { style: "currency", currency: "EUR" });
const fmtDateTime = (ms) => ms
  ? new Date(ms).toLocaleString(LOCALE, { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })
  : "";
// Valoarea minima pentru <input type="datetime-local">: acum + 5 min, in ora locala.
const schedMinValue = () => {
  const d = new Date(Date.now() + 5 * 60000); d.setSeconds(0, 0);
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
};
// Mic indicator cu numarul de opriri intermediare (sau "" daca nu sunt).
const stopsInfo = (o) => {
  const n = (o.stops || []).length;
  return n ? `<span class="stop-chip">${IC.pin}${STR.client.stopsBadge(n)}</span>` : "";
};
// Sunet scurt de notificare (WebAudio, fara fisier audio).
function beep() {
  try {
    const AC = window.AudioContext || window.webkitAudioContext;
    const a = new AC();
    const o = a.createOscillator(), g = a.createGain();
    o.connect(g); g.connect(a.destination);
    o.type = "sine"; o.frequency.value = 880;
    g.gain.setValueAtTime(0.0001, a.currentTime);
    g.gain.exponentialRampToValueAtTime(0.18, a.currentTime + 0.01);
    g.gain.exponentialRampToValueAtTime(0.0001, a.currentTime + 0.28);
    o.start(); o.stop(a.currentTime + 0.3);
  } catch { /* audio indisponibil */ }
}
const notify = (msg) => { toast(msg); beep(); };
// Escapare HTML pentru text din surse externe (ex. nume adrese de la Nominatim).
const esc = (s) => String(s).replace(/[&<>"']/g, (c) =>
  ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

// ---- Tema (luminos / intunecat) ------------------------------------------
const themeBtn = document.getElementById("themeBtn");
const savedTheme = localStorage.getItem("pd-theme");
if (savedTheme) document.documentElement.setAttribute("data-theme", savedTheme);
themeBtn.addEventListener("click", () => {
  const cur = document.documentElement.getAttribute("data-theme");
  const next = cur === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", next);
  localStorage.setItem("pd-theme", next);
});

// ---- Selector de limba (DE implicit / EN / RO) ---------------------------
// Schimbarea limbii reincarca pagina: sesiunea e pe cookie, deci starea
// (login, rol) se restaureaza curat, fara re-render partial riscant.
const langSelect = document.getElementById("langSelect");
if (langSelect) {
  langSelect.value = LANG;
  langSelect.addEventListener("change", () => {
    localStorage.setItem("pd-lang", langSelect.value);
    location.reload();
  });
}

function showView(id) {
  document.querySelectorAll(".view").forEach((v) => v.classList.toggle("active", v.id === id));
}

// ===========================================================================
// HARTA REALA (Leaflet + OpenStreetMap, fara cheie API).
// Pastram o harta vie per comanda intr-un registru, ca sa NU o distrugem la
// fiecare reimprospatare (la 2s) ci doar sa mutam marcajul soferului.
// ===========================================================================
const LiveMap = {
  reg: {}, // orderId -> { map, driver, driverShown }

  ensure(order) {
    const el = document.getElementById("map-" + order.id);
    if (!el || typeof L === "undefined") return;
    let m = this.reg[order.id];

    if (!m) {
      const map = L.map(el, { zoomControl: false, attributionControl: true, scrollWheelZoom: false });
      // Tile-uri Esri (gratuite, fara cheie API) - fundal clar, minimalist.
      // INLOCUIESTE IN PRODUCTIE: pentru volum mare foloseste un plan platit de
      // tile-uri (Mapbox/Esri/CARTO) sau gazduieste-ti propriul server de tile-uri.
      L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}", {
        maxZoom: 16, attribution: "© Esri",
      }).addTo(map);
      const from = [order.from.lat, order.from.lng];
      const to = [order.to.lat, order.to.lng];
      // traseul real pe strazi (OSRM); daca lipseste, cade pe linie dreapta
      const coords = (order.routeGeometry && order.routeGeometry.length > 1)
        ? order.routeGeometry : [from, to];
      const poly = L.polyline(coords, { color: "#2563EB", weight: 4, opacity: 0.8 }).addTo(map);
      L.circleMarker(from, { radius: 8, color: "#fff", weight: 2, fillColor: "#EA580C", fillOpacity: 1 })
        .addTo(map).bindTooltip(STR.client.mapPickup);
      L.circleMarker(to, { radius: 8, color: "#fff", weight: 2, fillColor: "#2563EB", fillOpacity: 1 })
        .addTo(map).bindTooltip(STR.client.mapDrop);
      // Opriri intermediare: marcaje numerotate cu eticheta permanenta.
      (order.stops || []).forEach((st, i) => {
        if (st.lat == null || st.lng == null) return;
        L.marker([st.lat, st.lng], {
          icon: L.divIcon({ className: "stop-marker", html: String(i + 1), iconSize: [22, 22] }),
        }).addTo(map).bindTooltip(STR.client.mapStop + " " + (i + 1) + (st.name ? " · " + esc(st.name) : ""));
      });
      const driver = L.circleMarker(from, { radius: 7, color: "#2563EB", weight: 3, fillColor: "#fff", fillOpacity: 1 })
        .bindTooltip(STR.auth.roleDriver);
      map.fitBounds(poly.getBounds().pad(0.35));
      m = this.reg[order.id] = { map, driver, driverShown: false };
      setTimeout(() => map.invalidateSize(), 60);
    }

    if (order.driverPos) {
      m.driver.setLatLng([order.driverPos.lat, order.driverPos.lng]);
      if (!m.driverShown) { m.driver.addTo(m.map); m.driverShown = true; }
    }
  },

  remove(id) { if (this.reg[id]) { this.reg[id].map.remove(); delete this.reg[id]; } },
  reset() { Object.keys(this.reg).forEach((id) => this.remove(id)); },
};

// ===========================================================================
// URMARIRE LIVE prin WebSocket (Django Channels). Pentru fiecare comanda activa
// deschidem o conexiune ws/track/<cod>/ si primim actualizari push (pozitia
// soferului, starea) fara polling. Daca WebSocket-ul pica, raman pollingul lent
// de reimprospatare a listei ca plasa de siguranta.
// ===========================================================================
const Track = {
  socks: {}, // cod -> WebSocket

  open(code, onUpdate) {
    if (this.socks[code]) return;
    const proto = location.protocol === "https:" ? "wss" : "ws";
    let ws;
    try { ws = new WebSocket(`${proto}://${location.host}/ws/track/${code}/`); }
    catch { return; }
    ws.onmessage = (e) => { try { onUpdate(JSON.parse(e.data)); } catch { /* ignoram */ } };
    ws.onclose = () => { if (this.socks[code] === ws) delete this.socks[code]; };
    ws.onerror = () => { try { ws.close(); } catch {} };
    this.socks[code] = ws;
  },

  close(code) { const w = this.socks[code]; if (w) { delete this.socks[code]; try { w.close(); } catch {} } },
  closeAll() { Object.keys(this.socks).forEach((c) => this.close(c)); },
  // inchide conexiunile pentru comenzi care nu mai sunt afisate
  prune(activeCodes) { Object.keys(this.socks).forEach((c) => { if (!activeCodes.has(c)) this.close(c); }); },
};

// Construieste linia de status (timeline) pentru o comanda.
function timelineHTML(order) {
  const flow = CONFIG.flow;
  const curIdx = flow.findIndex((f) => f.id === order.status);
  return flow.map((f, i) => {
    const cls = i < curIdx ? "done" : i === curIdx ? "current" : "pending";
    return `<li class="${cls}"><span class="tl-dot">${i < curIdx ? IC.check : ""}</span>
      <span class="tl-label">${f.label}</span></li>`;
  }).join("");
}

// Mini-grafic „castig pe zile" (bare CSS, responsive + tabel ascuns ca fallback
// accesibil). Valorile sunt afisate ca text, nu doar prin inaltimea barei.
function earningsChartHTML(days) {
  const s = STR.driver;
  const total = days.reduce((a, d) => a + d.total, 0);
  const count = days.reduce((a, d) => a + d.count, 0);
  if (count === 0) return `<div class="empty">${s.noEarn}</div>`;
  const max = Math.max(1, ...days.map((d) => d.total));
  const bars = days.map((d) => {
    const h = d.total > 0 ? Math.max(Math.round((d.total / max) * 100), 8) : 2;
    return `
      <div class="eb" role="listitem" title="${d.label}: ${eur(d.total)} (${d.count})">
        <div class="eb-val">${d.total > 0 ? eur(d.total) : ""}</div>
        <div class="eb-track"><div class="eb-fill${d.total > 0 ? "" : " zero"}" style="height:${h}%"></div></div>
        <div class="eb-lbl">${d.label}</div>
      </div>`;
  }).join("");
  const rows = days.map((d) =>
    `<tr><td>${d.label} · ${d.date}</td><td>${eur(d.total)}</td><td>${d.count}</td></tr>`).join("");
  return `
    <div class="earn-summary">${s.earnTotal7}: <strong>${eur(total)}</strong> · ${count} ${s.earnCount.toLowerCase()}</div>
    <div class="earn-bars" role="list" aria-label="${s.earnChart}">${bars}</div>
    <details class="earn-table"><summary>${s.earnTable}</summary>
      <table>
        <thead><tr><th>${s.earnDay}</th><th>${s.earnSum}</th><th>${s.earnCount}</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </details>`;
}

// ===========================================================================
// AUTOCOMPLETE DE ADRESA (combobox accesibil): repere presetate + Nominatim.
// ===========================================================================
const AddressPicker = {
  pickers: {},

  attach(key, onSelect) {
    const inputEl = document.getElementById(key + "Inp");
    const listEl = document.getElementById(key + "List");
    if (!inputEl || !listEl) return;
    const p = { key, inputEl, listEl, items: [], active: -1, selected: null, onSelect, t: null };
    this.pickers[key] = p;

    inputEl.addEventListener("input", () => {
      clearTimeout(p.t);
      p.selected = null;
      const q = inputEl.value.trim();
      this.render(p, this.presets(q), false);
      p.t = setTimeout(() => this.search(p, q), 300);
    });
    inputEl.addEventListener("keydown", (e) => this.onKey(e, p));
    inputEl.addEventListener("focus", () => this.render(p, this.presets(inputEl.value.trim()), false));
    document.addEventListener("click", (e) => {
      if (!listEl.parentElement.contains(e.target)) this.close(p);
    });
  },

  presets(q) {
    const ql = q.toLowerCase();
    return CONFIG.locations
      .filter((l) => !ql || l.name.toLowerCase().includes(ql))
      .map((l) => ({ name: l.name, lat: l.lat, lng: l.lng, inArea: true, preset: true }));
  },

  async search(p, q) {
    if (q.length < 3) return;
    try {
      const data = await api.get("/api/geocode?q=" + encodeURIComponent(q));
      this.render(p, this.presets(q).concat(data.results || []), true);
    } catch { /* pastram ce e afisat */ }
  },

  render(p, items, searched) {
    p.items = items; p.active = -1;
    if (!items.length) {
      p.listEl.innerHTML = `<li class="ac-empty">${searched ? STR.client.noMatch : STR.client.typeMore}</li>`;
      this.open(p); return;
    }
    p.listEl.innerHTML = items.map((it, i) => `
      <li role="option" id="ac-${p.key}-${i}" data-i="${i}"
          class="ac-opt${it.inArea ? "" : " out"}" aria-disabled="${it.inArea ? "false" : "true"}">
        <span class="ac-ic">${IC.pin}</span>
        <span class="ac-name">${esc(it.name)}</span>
        ${it.preset ? `<span class="ac-tag">reper</span>`
          : it.inArea ? "" : `<span class="ac-tag out">in afara zonei</span>`}
      </li>`).join("");
    p.listEl.querySelectorAll(".ac-opt").forEach((li) =>
      li.addEventListener("mousedown", (e) => { e.preventDefault(); this.choose(p, +li.dataset.i); }));
    this.open(p);
  },

  onKey(e, p) {
    const n = p.items.length;
    if (e.key === "ArrowDown" && n) { e.preventDefault(); this.move(p, 1); }
    else if (e.key === "ArrowUp" && n) { e.preventDefault(); this.move(p, -1); }
    else if (e.key === "Enter") { if (p.active >= 0) { e.preventDefault(); this.choose(p, p.active); } }
    else if (e.key === "Escape") { this.close(p); }
  },

  move(p, dir) {
    p.active = (p.active + dir + p.items.length) % p.items.length;
    p.listEl.querySelectorAll(".ac-opt").forEach((li, i) => {
      const on = i === p.active;
      li.classList.toggle("active", on);
      if (on) { li.scrollIntoView({ block: "nearest" }); p.inputEl.setAttribute("aria-activedescendant", li.id); }
    });
  },

  choose(p, i) {
    const it = p.items[i];
    if (!it) return;
    if (!it.inArea) { toast(STR.client.outArea); return; }
    p.selected = it;
    p.inputEl.value = it.name;
    this.close(p);
    if (p.onSelect) p.onSelect(it);
  },

  open(p) { p.listEl.hidden = false; p.inputEl.setAttribute("aria-expanded", "true"); },
  close(p) {
    p.listEl.hidden = true; p.active = -1;
    p.inputEl.setAttribute("aria-expanded", "false");
    p.inputEl.removeAttribute("aria-activedescendant");
  },
};

// ===========================================================================
// AUTENTIFICARE (login / inregistrare), cu ecran dedicat.
// ===========================================================================
const Auth = {
  mode: "login",   // "login" | "register"
  role: "client",  // la inregistrare

  render() {
    const s = STR.auth;
    const el = document.getElementById("view-auth");
    const isReg = this.mode === "register";
    const vehOpts = CONFIG.vehicles.map((v) =>
      `<option value="${v.id}">${v.name} — ${v.capacity}</option>`).join("");

    el.innerHTML = `
      <div class="auth-wrap">
        <div class="card auth-card">
          <h1 class="page-title">${s.welcome}</h1>
          <p class="page-sub">${s.sub}</p>

          <div class="seg auth-seg" id="authModeSeg" role="tablist">
            <button role="tab" data-mode="login" class="${!isReg ? "active" : ""}"><strong>${s.tabLogin}</strong></button>
            <button role="tab" data-mode="register" class="${isReg ? "active" : ""}"><strong>${s.tabRegister}</strong></button>
          </div>

          <div class="auth-err" id="authErr" role="alert" tabindex="-1" hidden></div>

          <form id="authForm" novalidate>
            ${isReg ? `
              <div class="field">
                <span class="lbl">${s.role}</span>
                <div class="role-pick" id="rolePick">
                  <label class="role-opt ${this.role === "client" ? "active" : ""}">
                    <input type="radio" name="role" value="client" ${this.role === "client" ? "checked" : ""} />
                    <span class="r-ic">${IC.user}</span>
                    <span><strong>${s.asClient}</strong><small>${s.roleClientHint}</small></span>
                  </label>
                  <label class="role-opt ${this.role === "driver" ? "active" : ""}">
                    <input type="radio" name="role" value="driver" ${this.role === "driver" ? "checked" : ""} />
                    <span class="r-ic">${vehIcon("scuter")}</span>
                    <span><strong>${s.asDriver}</strong><small>${s.roleDriverHint}</small></span>
                  </label>
                </div>
              </div>
              <div class="field"><label for="nameInp">${s.name}</label><input id="nameInp" autocomplete="name" /></div>
            ` : ""}

            <div class="field"><label for="emailInp">${s.email}</label>
              <input id="emailInp" type="email" autocomplete="email" inputmode="email" /></div>
            <div class="field"><label for="passInp">${s.password}</label>
              <input id="passInp" type="password" autocomplete="${isReg ? "new-password" : "current-password"}" /></div>

            ${isReg && this.role === "client" ? `
              <div class="field"><label for="phoneInp">${s.phone}</label><input id="phoneInp" autocomplete="tel" /></div>
              <label class="check"><input type="checkbox" id="bizInp" /> <span>${s.business}</span></label>
              <div class="field" id="companyWrap" hidden><label for="companyInp">${s.company}</label><input id="companyInp" /></div>
            ` : ""}
            ${isReg && this.role === "driver" ? `
              <div class="field"><label for="phoneInp">${s.phone}</label><input id="phoneInp" autocomplete="tel" /></div>
              <div class="field"><label for="vehInp">${s.vehicle}</label><select id="vehInp">${vehOpts}</select></div>
            ` : ""}

            <button type="submit" class="btn btn-primary" style="width:100%;margin-top:6px">
              ${isReg ? s.doRegister : s.doLogin}</button>
          </form>
        </div>
      </div>`;

    el.querySelector("#authModeSeg").addEventListener("click", (e) => {
      const b = e.target.closest("button"); if (!b) return;
      this.mode = b.dataset.mode; this.render();
    });
    const rolePick = el.querySelector("#rolePick");
    if (rolePick) rolePick.addEventListener("change", (e) => { this.role = e.target.value; this.render(); });
    const biz = el.querySelector("#bizInp");
    if (biz) biz.addEventListener("change", () => { el.querySelector("#companyWrap").hidden = !biz.checked; });
    el.querySelector("#authForm").addEventListener("submit", (e) => { e.preventDefault(); this.submit(); });
  },

  error(msg) {
    const box = document.getElementById("authErr");
    box.textContent = msg; box.hidden = false; box.focus();
  },

  async submit() {
    const val = (id) => { const e = document.getElementById(id); return e ? e.value.trim() : ""; };
    try {
      let user;
      if (this.mode === "login") {
        user = await api.post("/api/auth/login", { email: val("emailInp"), password: document.getElementById("passInp").value });
      } else {
        const payload = {
          role: this.role, name: val("nameInp"), email: val("emailInp"),
          password: document.getElementById("passInp").value, phone: val("phoneInp"),
        };
        if (this.role === "client") {
          payload.isBusiness = document.getElementById("bizInp")?.checked || false;
          payload.company = val("companyInp");
        } else {
          payload.vehicleId = document.getElementById("vehInp")?.value;
        }
        user = await api.post("/api/auth/register", payload);
      }
      App.enter(user);
    } catch (err) { this.error(err.message); }
  },
};

// ===========================================================================
// VEDEREA CLIENT: booking + urmarire live (+ panou business daca e cazul)
// ===========================================================================
const Client = {
  state: { serviceType: "paket", vertical: "", quotes: [], selectedVehicle: null, from: null, to: null, stops: [] },
  user: null, poll: null,
  notifiedDelivered: new Set(), seeded: false,

  // Notifica (o singura data) cand o comanda tocmai a fost livrata.
  maybeNotifyDelivered(o) {
    if (o.status === "livrat" && !this.notifiedDelivered.has(o.id)) {
      this.notifiedDelivered.add(o.id);
      if (this.seeded) notify(`${o.id} ${STR.client.delivered}`);
    }
  },

  init(user) {
    this.user = user;
    this.render();
    // Pollingul listei e doar plasa de siguranta (apar comenzi noi, dispar cele
    // livrate). Miscarea live a soferului vine prin WebSocket (vezi Track).
    if (this.poll) clearInterval(this.poll);
    this.poll = setInterval(() => {
      if (document.getElementById("view-client").classList.contains("active")) {
        this.renderMyOrders();
        if (this.user.isBusiness) this.renderStats();
      }
    }, 5000);
  },

  render() {
    const el = document.getElementById("view-client");
    const s = STR.client;
    LiveMap.reset();
    // Camp de adresa (combobox). `value` precompleteaza (ex. o oprire deja aleasa).
    const addrInput = (key, label, value, ph) => `
        <div class="ac" id="${key}Ac">
          <input id="${key}Inp" class="ac-input" type="text" autocomplete="off" spellcheck="false"
                 role="combobox" aria-expanded="false" aria-autocomplete="list" aria-controls="${key}List"
                 placeholder="${ph || s.addrPh}" value="${value ? esc(value.name) : ""}" />
          <ul class="ac-list" id="${key}List" role="listbox" aria-label="${label}" hidden></ul>
        </div>`;
    const addrField = (key, label) => `
      <div class="field">
        <label for="${key}Inp">${label}</label>
        ${addrInput(key, label, this.state[key])}
      </div>`;
    this._addrInput = addrInput;  // reutilizat de renderStops()

    el.innerHTML = `
      <h1 class="page-title">${s.title}</h1>
      <p class="page-sub">${s.sub}</p>
      ${this.user.isBusiness ? `<div class="stats" id="bizStats"></div>` : ""}
      <div class="grid grid-2">
        <div class="card">
          <h3>1. ${s.detailsStep}</h3>
          <div class="seg" id="serviceSeg">
            ${CONFIG.serviceTypes.map((t) => `
              <button data-id="${t.id}" class="${t.id === this.state.serviceType ? "active" : ""}">
                <strong>${t.name}</strong><small>${t.description}</small>
              </button>`).join("")}
          </div>
          <div class="field">
            <label for="domainSel">${s.domain}</label>
            <select id="domainSel">
              <option value="">${s.domainAny}</option>
              ${(CONFIG.verticals || []).map((v) => `<option value="${v.slug}" ${this.state.vertical === v.slug ? "selected" : ""}>${esc(v.name)}</option>`).join("")}
            </select>
          </div>
          <div id="domainFields"></div>
          ${addrField("from", s.from)}
          <div class="stops-block">
            <div class="stops-head">
              <span class="lbl">${s.stopsLabel}</span>
              <button type="button" class="btn-link add-stop" id="addStopBtn">
                <span class="bl-ic">${IC.plus}</span>${s.addStop}
              </button>
            </div>
            <div id="stopsWrap"></div>
          </div>
          ${addrField("to", s.to)}
          <div class="field"><label for="noteInp">${s.note}</label><textarea id="noteInp" rows="2" placeholder="${s.notePh}"></textarea></div>
          <div class="field"><label for="contactInp">${s.contact}</label><input id="contactInp" placeholder="+49 ..." /></div>
          <div class="field sched-field">
            <label>${s.schedTime}</label>
            <div class="seg sched-seg" id="schedSeg">
              <button type="button" data-mode="now" class="active">${s.schedNow}</button>
              <button type="button" data-mode="later">${s.schedLater}</button>
            </div>
            <input type="datetime-local" id="schedAt" class="sched-at" aria-label="${s.schedAt}" hidden />
          </div>
          <button class="btn btn-primary" id="quoteBtn">${s.getQuote}</button>
        </div>

        <div class="card">
          <h3>2. ${s.vehicles}</h3>
          <div id="quoteList"><div class="empty">${s.fillRoute(s.getQuote)}</div></div>
          <div id="bookWrap"></div>
        </div>
      </div>

      ${this.user.isBusiness ? `
      <div class="card" style="margin-top:20px">
        <h3>${STR.business.bulk}</h3>
        <div class="notice">${STR.business.bulkHint}</div>
        <button class="btn btn-accent" id="bulkBtn">${STR.business.genBulk}</button>
      </div>` : ""}

      <div class="card" style="margin-top:20px">
        <h3>${s.activeOrders}</h3>
        <div id="myOrders"></div>
      </div>

      <div class="card" style="margin-top:20px">
        <h3>${s.history}</h3>
        <div id="history"></div>
      </div>`;

    el.querySelector("#serviceSeg").addEventListener("click", (e) => {
      const b = e.target.closest("button"); if (!b) return;
      this.state.serviceType = b.dataset.id;
      this.state.quotes = []; this.state.selectedVehicle = null;
      this.render();
    });
    const dom = el.querySelector("#domainSel");
    if (dom) dom.addEventListener("change", (e) => { this.state.vertical = e.target.value; this.renderDomainFields(); });
    this.renderDomainFields();
    el.querySelector("#quoteBtn").addEventListener("click", () => this.getQuote());
    const bulk = el.querySelector("#bulkBtn");
    if (bulk) bulk.addEventListener("click", () => this.bulk());
    AddressPicker.attach("from", (it) => { this.state.from = it; });
    AddressPicker.attach("to", (it) => { this.state.to = it; });
    el.querySelector("#addStopBtn").addEventListener("click", () => this.addStop());
    this._wireSchedule(el);
    this.renderStops();
    this.renderMyOrders();
    if (this.user.isBusiness) this.renderStats();
  },

  // --- Programare in avans: comutator Acum / Programeaza + selector data-ora ---
  _wireSchedule(el) {
    const seg = el.querySelector("#schedSeg");
    const input = el.querySelector("#schedAt");
    if (!seg || !input) return;
    input.min = schedMinValue();
    seg.addEventListener("click", (e) => {
      const b = e.target.closest("button"); if (!b) return;
      seg.querySelectorAll("button").forEach((x) => x.classList.toggle("active", x === b));
      const later = b.dataset.mode === "later";
      input.hidden = !later;
      if (later) { input.min = schedMinValue(); if (!input.value) input.value = input.min; input.focus(); }
    });
  },

  // Timestampul (ms) ales pentru programare, sau null daca e comanda instant.
  scheduledMs() {
    const mode = document.querySelector("#schedSeg .active")?.dataset.mode;
    const input = document.getElementById("schedAt");
    if (mode !== "later" || !input || !input.value) return null;
    const ms = new Date(input.value).getTime();
    return Number.isFinite(ms) ? ms : null;
  },

  // --- Opriri intermediare: lista editabila (adauga / sterge / reordoneaza) ---
  renderStops() {
    const wrap = document.getElementById("stopsWrap");
    if (!wrap) return;
    const s = STR.client, stops = this.state.stops;
    wrap.innerHTML = stops.map((st, i) => {
      const key = "stop" + i;
      return `
      <div class="stop-row">
        <span class="stop-num">${i + 1}</span>
        ${this._addrInput(key, s.stopsLabel + " " + (i + 1), st, s.stopPh)}
        <div class="stop-ctrls">
          <button type="button" class="stop-btn" data-move="up" data-i="${i}"
                  aria-label="${s.moveUp}" ${i === 0 ? "disabled" : ""}>${IC.up}</button>
          <button type="button" class="stop-btn" data-move="down" data-i="${i}"
                  aria-label="${s.moveDown}" ${i === stops.length - 1 ? "disabled" : ""}>${IC.down}</button>
          <button type="button" class="stop-btn danger" data-remove="${i}"
                  aria-label="${s.removeStop}">${IC.x}</button>
        </div>
      </div>`;
    }).join("");

    // Atasam cate un combobox pentru fiecare oprire (indexul e „inghetat" prin closure).
    stops.forEach((_, i) => {
      AddressPicker.attach("stop" + i, (it) => { this.state.stops[i] = it; this.invalidateQuote(); });
    });
    wrap.querySelectorAll("[data-remove]").forEach((b) =>
      b.addEventListener("click", () => this.removeStop(+b.dataset.remove)));
    wrap.querySelectorAll("[data-move]").forEach((b) =>
      b.addEventListener("click", () => this.moveStop(+b.dataset.i, b.dataset.move === "up" ? -1 : 1)));
  },

  addStop() { this.state.stops.push(null); this.renderStops(); this.invalidateQuote(); },
  removeStop(i) { this.state.stops.splice(i, 1); this.renderStops(); this.invalidateQuote(); },
  moveStop(i, dir) {
    const j = i + dir, st = this.state.stops;
    if (j < 0 || j >= st.length) return;
    [st[i], st[j]] = [st[j], st[i]];
    this.renderStops(); this.invalidateQuote();
  },

  // Ruta s-a schimbat -> pretul afisat nu mai e valabil pana la un nou „Vezi pretul”.
  invalidateQuote() {
    this.state.quotes = []; this.state.selectedVehicle = null;
    const list = document.getElementById("quoteList");
    if (list) list.innerHTML = `<div class="empty">${STR.client.routeChanged(STR.client.getQuote)}</div>`;
    const bw = document.getElementById("bookWrap");
    if (bw) bw.innerHTML = "";
  },

  // Opririle alese (fara cele goale), gata de trimis catre server.
  collectStops() {
    return this.state.stops.filter(Boolean).map((s) => ({ name: s.name, lat: s.lat, lng: s.lng }));
  },

  // --- Campuri specifice domeniului ales (din taxonomie) -------------------
  _verticalDef(slug) {
    return (CONFIG.verticals || []).find((v) => v.slug === slug) || null;
  },

  renderDomainFields() {
    const box = document.getElementById("domainFields"); if (!box) return;
    const v = this._verticalDef(this.state.vertical);
    const fields = (v && v.orderFields) || [];
    if (!fields.length) { box.innerHTML = ""; return; }
    box.innerHTML = `<div class="vf-block">` + fields.map((f) => {
      const id = "vf_" + f.key;
      const req = f.required ? ` <span class="req">*</span>` : "";
      if (f.type === "bool") {
        return `<label class="cap-opt"><input type="checkbox" id="${id}" data-vf="${f.key}" /><span>${esc(f.label)}${req}</span></label>`;
      }
      const t = f.type === "number" ? "number" : "text";
      return `<div class="field"><label for="${id}">${esc(f.label)}${req}</label><input type="${t}" id="${id}" data-vf="${f.key}" /></div>`;
    }).join("") + `</div>`;
  },

  collectVerticalFields() {
    const out = {};
    document.querySelectorAll("#domainFields [data-vf]").forEach((el) => {
      out[el.dataset.vf] = el.type === "checkbox" ? el.checked : el.value;
    });
    return out;
  },

  async getQuote() {
    if (!this.state.from || !this.state.to) { toast(STR.client.pickAddr); return; }
    try {
      const data = await api.post("/api/quote", {
        from: this.state.from, to: this.state.to, stops: this.collectStops(),
        serviceType: this.state.serviceType,
      });
      this.state.quotes = data.quotes;
      this.state.selectedVehicle = data.quotes[0]?.vehicleId || null;
      this.renderQuotes(data);
    } catch (err) { toast(err.message); }
  },

  renderQuotes(data) {
    const list = document.getElementById("quoteList");
    list.innerHTML = `<p class="hint">Distanta estimata: <strong>${data.distanceKm} km</strong></p>` +
      this.state.quotes.map((q) => `
        <div class="vehicle ${q.vehicleId === this.state.selectedVehicle ? "active" : ""}" data-id="${q.vehicleId}">
          <span class="v-ic">${vehIcon(q.vehicleId)}</span>
          <div><div class="v-name">${q.name}</div><div class="v-cap">${q.capacity}</div></div>
          <div class="v-meta"><div class="v-price">${eur(q.price)}</div><div class="v-eta">~${q.etaMin} min</div></div>
        </div>`).join("");
    list.querySelectorAll(".vehicle").forEach((v) =>
      v.addEventListener("click", () => { this.state.selectedVehicle = v.dataset.id; this.renderQuotes(data); }));
    document.getElementById("bookWrap").innerHTML =
      `<button class="btn btn-accent" id="bookBtn" style="margin-top:12px">${STR.client.book}</button>`;
    document.getElementById("bookBtn").addEventListener("click", () => this.book());
  },

  async book() {
    if (!this.state.from || !this.state.to) { toast(STR.client.pickAddr); return; }
    try {
      const scheduledFor = this.scheduledMs();
      const order = await api.post("/api/orders", {
        from: this.state.from, to: this.state.to, stops: this.collectStops(),
        vehicleId: this.state.selectedVehicle,
        serviceType: this.state.serviceType,
        verticalSlug: this.state.vertical || "",
        verticalFields: this.state.vertical ? this.collectVerticalFields() : {},
        note: document.getElementById("noteInp").value,
        contact: document.getElementById("contactInp").value,
        scheduledFor,
      });
      toast(order.scheduledFor
        ? STR.client.orderScheduled(order.id, fmtDateTime(order.scheduledFor))
        : STR.client.orderCreated(order.id));
      this.renderMyOrders();
    } catch (err) { toast(err.message); }
  },

  async renderMyOrders() {
    const wrap = document.getElementById("myOrders"); if (!wrap) return;
    const orders = await api.get("/api/orders").catch(() => []);
    const active = orders.filter((o) => o.status !== "livrat");
    const past = orders.filter((o) => o.status === "livrat");

    // --- Comenzi active: carduri live cu harta + urmarire prin WebSocket ---
    if (wrap.querySelector(".empty")) wrap.innerHTML = "";
    const seen = new Set();
    for (const o of active) {
      seen.add(o.id);
      let card = document.getElementById("card-" + o.id);
      if (!card) { wrap.insertAdjacentHTML("beforeend", this.cardShell(o)); card = document.getElementById("card-" + o.id); }
      this.updateCard(card, o);
      LiveMap.ensure(o);
      this.maybeNotifyDelivered(o);
      Track.open(o.id, (u) => {
        const c = document.getElementById("card-" + u.id);
        if (c) {
          this.updateCard(c, u); LiveMap.ensure(u); this.maybeNotifyDelivered(u);
          if (u.status === "livrat") { Track.close(u.id); this.renderMyOrders(); } // mutare in istoric
        }
      });
    }
    // Scoatem cardurile care nu mai sunt active (livrate sau disparute).
    wrap.querySelectorAll(".order-card").forEach((c) => {
      const id = c.id.replace("card-", "");
      if (!seen.has(id)) { LiveMap.remove(id); Track.close(id); c.remove(); }
    });
    if (!wrap.querySelector(".order-card")) wrap.innerHTML = `<div class="empty">${STR.client.noOrders}</div>`;

    // Istoricul se randeaza cat timp `seeded` e inca fals, ca livrarile deja
    // existente la incarcare sa NU declanseze notificari. Abia apoi marcam seeded.
    this.renderHistory(past);
    this.seeded = true; // de la a doua randare incolo, livrarile noi notifica
  },

  // --- Istoric: livrarile finalizate, lista compacta (fara harta) + evaluare ---
  renderHistory(past) {
    const box = document.getElementById("history"); if (!box) return;
    if (!past.length) { box.innerHTML = `<div class="empty">${STR.client.noHistory}</div>`; return; }
    box.innerHTML = past.map((o) => this.historyItem(o)).join("");
    for (const o of past) {
      this.renderRating(box.querySelector(`#hist-${o.id} .oc-rate`), o);
      this.maybeNotifyDelivered(o);
    }
  },

  historyItem(o) {
    const extra = (o.stops || []).length ? ` · ${o.stops.length} opriri` : "";
    return `
    <div class="hist-item" id="hist-${o.id}">
      <div class="hist-top">
        <strong>${o.id}</strong>
        <span class="badge ok">Livrat</span>
        <span class="hist-date">${fmtDateTime(o.createdAt)}</span>
        <span class="muted" style="margin-left:auto">${eur(o.price)}</span>
      </div>
      <div class="j-route">${esc(o.from.name)} ${stopsInfo(o)} ${IC.arrow} ${esc(o.to.name)}</div>
      <div class="hint">${o.vehicleName} · ${o.distanceKm} km${extra}${o.driver ? " · " + esc(o.driver.name) : ""}</div>
      <div class="oc-rate"></div>
    </div>`;
  },

  cardShell(o) {
    return `
    <div class="order-card grid grid-2" id="card-${o.id}">
      <div>
        <div class="oc-head">
          <strong>${o.id}</strong>
          <span class="badge oc-badge"></span>
          <span class="muted" style="margin-left:auto">${eur(o.price)}</span>
        </div>
        <div class="j-route">${esc(o.from.name)} ${stopsInfo(o)} ${IC.arrow} ${esc(o.to.name)}</div>
        <div class="hint">${o.vehicleName} · ${o.distanceKm} km · ~${o.etaMin} min</div>
        <div class="hint oc-driver"></div>
        <ul class="timeline oc-timeline" style="margin-top:14px"></ul>
        <div class="oc-rate"></div>
      </div>
      <div class="map oc-map" id="map-${o.id}"></div>
    </div>`;
  },

  updateCard(card, o) {
    const done = o.status === "livrat";
    const scheduled = o.status === "programat";
    const badge = card.querySelector(".oc-badge");
    badge.className = "badge oc-badge " + (done ? "ok" : scheduled ? "sched" : "live");
    badge.textContent = done ? "Livrat" : scheduled ? STR.client.schedBadge : "In curs";
    const driverLine = card.querySelector(".oc-driver");
    if (scheduled) {
      driverLine.innerHTML = `<span class="sched-for">${STR.client.schedFor(fmtDateTime(o.scheduledFor))}</span>`;
    } else {
      driverLine.innerHTML = o.driver
        ? `${STR.auth.roleDriver}: <strong>${esc(o.driver.name)}</strong> (${o.driver.rating}★)` : "";
    }
    card.querySelector(".oc-timeline").innerHTML = timelineHTML(o);
    this.renderRating(card.querySelector(".oc-rate"), o);
  },

  renderRating(box, o) {
    if (!box) return;
    if (o.status !== "livrat") { box.innerHTML = ""; return; }
    if (o.rating) {
      box.innerHTML = `<span class="rated">${STR.client.rated}: ` +
        `<span class="stars">${"★".repeat(o.rating)}${"☆".repeat(5 - o.rating)}</span></span>`;
      return;
    }
    box.innerHTML = `<span class="hint">${STR.client.rateTitle}</span>
      <div class="rate-stars" role="group" aria-label="${STR.client.rateTitle}">
        ${[1, 2, 3, 4, 5].map((n) => `<button class="star" data-n="${n}" aria-label="${n} stele">★</button>`).join("")}
      </div>`;
    box.querySelectorAll(".star").forEach((b) => {
      b.addEventListener("mouseenter", () => this._hoverStars(box, +b.dataset.n));
      b.addEventListener("focus", () => this._hoverStars(box, +b.dataset.n));
      b.addEventListener("click", () => this.rate(o.id, +b.dataset.n));
    });
    box.addEventListener("mouseleave", () => this._hoverStars(box, 0));
  },

  _hoverStars(box, n) {
    box.querySelectorAll(".star").forEach((b, i) => b.classList.toggle("on", i < n));
  },

  async rate(code, n) {
    try {
      await api.post(`/api/orders/${code}/rate`, { rating: n });
      toast(STR.client.thanks);
      this.renderMyOrders();
    } catch (e) { toast(e.message); }
  },

  async renderStats() {
    const box = document.getElementById("bizStats"); if (!box) return;
    const st = await api.get("/api/stats").catch(() => null); if (!st) return;
    const b = STR.business;
    box.innerHTML = `
      <div class="stat"><div class="s-val">${st.total}</div><div class="s-lbl">${b.total}</div></div>
      <div class="stat"><div class="s-val">${st.active}</div><div class="s-lbl">${b.active}</div></div>
      <div class="stat"><div class="s-val">${st.livrate}</div><div class="s-lbl">${b.done}</div></div>
      <div class="stat"><div class="s-val">${eur(st.venit)}</div><div class="s-lbl">${b.revenue}</div></div>
      <div class="stat"><div class="s-val">${st.soferiOnline}</div><div class="s-lbl">${b.drivers}</div></div>`;
  },

  async bulk() {
    const locs = CONFIG.locations, veh = CONFIG.vehicles;
    for (let i = 0; i < 3; i++) {
      let a = locs[Math.floor(Math.random() * locs.length)];
      let b = locs[Math.floor(Math.random() * locs.length)];
      while (b.id === a.id) b = locs[Math.floor(Math.random() * locs.length)];
      const v = veh[Math.floor(Math.random() * veh.length)];
      await api.post("/api/orders", {
        from: { name: a.name, lat: a.lat, lng: a.lng }, to: { name: b.name, lat: b.lat, lng: b.lng },
        vehicleId: v.id, serviceType: v.service, note: STR.business.demoNote,
      }).catch(() => {});
    }
    toast(STR.business.bulkDone);
    this.renderMyOrders(); this.renderStats();
  },
};

// ===========================================================================
// VEDEREA SOFER: status online, comenzi disponibile, comenzile mele, castig
// ===========================================================================
const Driver = {
  user: null, poll: null,
  feedSock: null, knownAvailable: new Set(), feedSeeded: false,

  init(user) {
    this.user = user;
    this.render();
    this.openFeed();
    // Pollingul reimprospateaza castigul/comenzile mele (fallback). Comenzile
    // disponibile vin prin WebSocket (feed), miscarea live prin Track.
    if (this.poll) clearInterval(this.poll);
    this.poll = setInterval(() => {
      if (document.getElementById("view-driver").classList.contains("active")) this.refresh();
    }, 4000);
  },

  renderAvailable(list) {
    const avail = document.getElementById("availJobs");
    if (!avail) return;
    avail.innerHTML = list.length
      ? list.map((o) => this.jobCard(o, true)).join("") : `<div class="empty">${STR.driver.none}</div>`;
    avail.querySelectorAll("[data-accept]").forEach((b) =>
      b.addEventListener("click", async () => {
        try { await api.post(`/api/orders/${b.dataset.accept}/accept`, {}); toast(STR.driver.accepted); this.refresh(); }
        catch (e) { toast(e.message); }
      }));
  },

  // Feed WebSocket: comenzi disponibile + notificare la comanda noua.
  openFeed() {
    if (this.feedSock) return;
    const proto = location.protocol === "https:" ? "wss" : "ws";
    let ws;
    try { ws = new WebSocket(`${proto}://${location.host}/ws/driver/`); } catch { return; }
    ws.onmessage = (e) => { try { this.onFeed(JSON.parse(e.data).available || []); } catch {} };
    ws.onclose = () => { if (this.feedSock === ws) this.feedSock = null; };
    ws.onerror = () => { try { ws.close(); } catch {} };
    this.feedSock = ws;
  },

  // Reconecteaza feed-ul (ex: dupa ce profilul de vehicul s-a schimbat), ca
  // filtrarea pe server sa reflecte noile capabilitati.
  reopenFeed() {
    if (this.feedSock) { try { this.feedSock.close(); } catch {} this.feedSock = null; }
    this.feedSeeded = false; this.knownAvailable = new Set();
    this.openFeed();
  },

  onFeed(list) {
    if (this.feedSeeded && list.some((o) => !this.knownAvailable.has(o.id))) {
      notify(STR.driver.newOrder);
    }
    this.knownAvailable = new Set(list.map((o) => o.id));
    this.feedSeeded = true;
    if (document.getElementById("view-driver").classList.contains("active")) this.renderAvailable(list);
  },

  closeFeed() { if (this.feedSock) { try { this.feedSock.close(); } catch {} this.feedSock = null; } this.feedSeeded = false; this.knownAvailable = new Set(); },

  async render() {
    const el = document.getElementById("view-driver");
    const s = STR.driver;
    el.innerHTML = `
      <h1 class="page-title">${s.title}</h1>
      <p class="page-sub">${s.sub}</p>
      <div class="stats" id="drvStats"></div>
      <div class="card" style="margin-top:4px"><h3>${s.vehTitle}</h3><div id="vehBox"><div class="empty">...</div></div></div>
      <div class="card" style="margin-top:4px"><h3>${s.earnChart}</h3><div id="earnChart"><div class="empty">...</div></div></div>
      <div class="grid grid-2">
        <div class="card"><h3>${s.available}</h3><div class="hint" style="margin:-4px 0 10px">${s.vehFilter}</div><div id="availJobs"><div class="empty">...</div></div></div>
        <div class="card"><h3>${s.mine}</h3><div id="myJobs"><div class="empty">...</div></div></div>
      </div>`;
    this.renderVehicle();
    this.refresh();
  },

  // --- Profilul de vehicul: clasa + capabilitati + asumarea raspunderii ----
  async renderVehicle() {
    const box = document.getElementById("vehBox"); if (!box) return;
    const s = STR.driver;
    const res = await api.get("/api/driver/vehicle").catch(() => null);
    const v = res && res.vehicle;
    const classes = (CONFIG.vehicleClasses || []);
    const caps = (CONFIG.capabilities || []);
    const curCaps = new Set(v ? v.capabilities : []);
    let statusHtml = "";
    if (v) {
      if (v.verified) statusHtml = `<div class="notice veh-ok">${s.vehVerifiedLbl}</div>`;
      else if (v.applicationStatus === "rejected") statusHtml = `<div class="notice veh-bad">${s.vehRejected}</div>`;
      else statusHtml = `<div class="notice veh-wait">${s.vehPending}</div>`;
    }
    box.innerHTML = `
      ${v ? statusHtml : `<div class="notice">${s.vehNone}</div>`}
      <div class="field">
        <label for="vehClass">${s.vehClass}</label>
        <select id="vehClass">
          ${classes.map((c) => `<option value="${c.slug}" ${v && v.classSlug === c.slug ? "selected" : ""}>${esc(c.name)}</option>`).join("")}
        </select>
      </div>
      <div class="field">
        <span class="lbl">${s.vehCaps}</span>
        <div class="cap-grid">
          ${caps.map((c) => `
            <label class="cap-opt">
              <input type="checkbox" value="${c.slug}" ${curCaps.has(c.slug) ? "checked" : ""} />
              <span>${esc(c.name)}${c.needsDocument ? ` <em class="cap-doc">(${s.vehDoc})</em>` : ""}</span>
            </label>`).join("")}
        </div>
      </div>
      <div class="grid grid-2">
        <div class="field"><label for="vehLabel">${s.vehLabel}</label><input id="vehLabel" value="${v ? esc(v.label) : ""}" placeholder="VW Caddy" /></div>
        <div class="field"><label for="vehPlate">${s.vehPlate}</label><input id="vehPlate" value="${v ? esc(v.plate) : ""}" placeholder="HH-AB 123" /></div>
      </div>
      <label class="cap-opt" style="margin:4px 0 12px"><input type="checkbox" id="vehResp" ${v && v.responsibilityAccepted ? "checked" : ""} /><span>${s.vehResp}</span></label>
      <button class="btn btn-primary" id="vehSave">${s.vehSave}</button>`;
    box.querySelector("#vehSave").addEventListener("click", () => this.saveVehicle(box));
  },

  async saveVehicle(box) {
    const caps = [...box.querySelectorAll(".cap-grid input:checked")].map((i) => i.value);
    const payload = {
      classSlug: box.querySelector("#vehClass").value,
      capabilities: caps,
      label: box.querySelector("#vehLabel").value,
      plate: box.querySelector("#vehPlate").value,
      responsibilityAccepted: box.querySelector("#vehResp").checked,
    };
    try {
      await api.post("/api/driver/vehicle", payload);
      toast(STR.driver.vehSaved);
      this.renderVehicle();   // reafiseaza statusul (in verificare / verificat)
      // Reconectam feed-ul ca filtrarea live sa reflecte noul profil.
      this.reopenFeed();
      this.refresh();
    } catch (e) { toast(e.message); }
  },

  async refresh() {
    const d = await api.get("/api/driver/jobs").catch(() => null); if (!d) return;
    const s = STR.driver;
    this.user.online = d.online;

    document.getElementById("drvStats").innerHTML = `
      <div class="stat stat-wide">
        <div class="online-row">
          <span class="dot-status ${d.online ? "on" : "off"}"></span>
          <div><div class="s-lbl">${s.onlineLbl}</div>
            <div class="s-val-sm">${d.online ? s.statusOnline : s.statusOffline}</div></div>
          <button class="switch ${d.online ? "on" : ""}" id="onlineBtn" role="switch"
                  aria-checked="${d.online}" aria-label="${s.onlineLbl}"><span></span></button>
        </div>
      </div>
      <div class="stat"><div class="s-val">${eur(d.earnings)}</div><div class="s-lbl">${s.earnings}</div></div>
      <div class="stat"><div class="s-val">${d.deliveredCount}</div><div class="s-lbl">${s.delivered}</div></div>`;
    document.getElementById("onlineBtn").addEventListener("click", () => this.toggleOnline(!d.online));

    const earn = document.getElementById("earnChart");
    if (earn) earn.innerHTML = earningsChartHTML(d.earningsByDay || []);

    this.renderAvailable(d.available);

    // comenzile mele active: pastram hartile vii (ca la client)
    const mineWrap = document.getElementById("myJobs");
    if (!d.mine.length) { mineWrap.innerHTML = `<div class="empty">${s.noneMine}</div>`; this.resetMineMaps(mineWrap); return; }
    if (mineWrap.querySelector(".empty")) mineWrap.innerHTML = "";
    const seen = new Set();
    for (const o of d.mine) {
      seen.add(o.id);
      let card = document.getElementById("card-" + o.id);
      if (!card) { mineWrap.insertAdjacentHTML("beforeend", this.mineShell(o)); card = document.getElementById("card-" + o.id);
        card.querySelector("[data-advance]").addEventListener("click", async (e) => {
          await api.post(`/api/orders/${e.currentTarget.dataset.advance}/status`).catch((x) => toast(x.message)); this.refresh();
        });
      }
      this.updateMine(card, o);
      LiveMap.ensure(o);
      Track.open(o.id, (u) => {
        const c = document.getElementById("card-" + u.id);
        if (c) { this.updateMine(c, u); LiveMap.ensure(u); }
      });
    }
    mineWrap.querySelectorAll(".order-card").forEach((c) => {
      const id = c.id.replace("card-", "");
      if (!seen.has(id)) { LiveMap.remove(id); Track.close(id); c.remove(); }
    });
  },

  resetMineMaps(wrap) {
    wrap.querySelectorAll(".order-card").forEach((c) => {
      const id = c.id.replace("card-", ""); LiveMap.remove(id); Track.close(id);
    });
  },

  async toggleOnline(next) {
    try { await api.post("/api/driver/online", { online: next }); this.refresh(); }
    catch (e) { toast(e.message); }
  },

  jobCard(o, isAvailable) {
    return `
    <div class="job">
      <div class="j-top">
        <div><strong>${o.id}</strong><div class="hint">${o.vehicleName}</div></div>
        <div class="j-price">${eur(o.price)}</div>
      </div>
      <div class="j-route">${IC.pin} ${esc(o.from.name)} ${stopsInfo(o)} ${IC.arrow} ${esc(o.to.name)}</div>
      <div class="hint">${o.distanceKm} km · ~${o.etaMin} min${o.note ? " · " + esc(o.note) : ""}</div>
      ${isAvailable ? `<button class="btn btn-primary" data-accept="${o.id}" style="margin-top:10px">${STR.driver.accept}</button>` : ""}
    </div>`;
  },

  mineShell(o) {
    return `
    <div class="order-card" id="card-${o.id}" style="margin-bottom:12px">
      <div class="oc-head"><strong>${o.id}</strong><span class="badge oc-badge live"></span>
        <span class="muted" style="margin-left:auto">${eur(o.price)}</span></div>
      <div class="j-route">${esc(o.from.name)} ${stopsInfo(o)} ${IC.arrow} ${esc(o.to.name)}</div>
      <div class="hint">${o.vehicleName} · ${o.distanceKm} km</div>
      <div class="map oc-map" id="map-${o.id}" style="margin-top:12px"></div>
      <ul class="timeline oc-timeline" style="margin-top:12px"></ul>
      <button class="btn btn-ghost oc-adv" data-advance="${o.id}" style="margin-top:10px">${STR.driver.advance}</button>
    </div>`;
  },

  updateMine(card, o) {
    const done = o.status === "livrat";
    const badge = card.querySelector(".oc-badge");
    badge.className = "badge oc-badge " + (done ? "ok" : "live");
    badge.textContent = CONFIG.flow.find((f) => f.id === o.status)?.label || o.status;
    card.querySelector(".oc-timeline").innerHTML = timelineHTML(o);
    card.querySelector(".oc-adv").disabled = done;
  },
};

// ===========================================================================
// APLICATIE: boot, intrare dupa rol, iesire
// ===========================================================================
const App = {
  async boot() {
    CONFIG = await api.get("/api/config");
    const user = await api.get("/api/auth/me").catch(() => ({ authenticated: false }));
    if (user.authenticated) this.enter(user);
    else this.showAuth();
  },

  showAuth() {
    document.getElementById("userBox").hidden = true;
    showView("view-auth");
    Auth.render();
  },

  enter(user) {
    this.user = user;
    const box = document.getElementById("userBox");
    const roleLbl = user.role === "driver" ? STR.auth.roleDriver : (user.isBusiness ? STR.auth.roleBusiness : STR.auth.roleClient);
    box.hidden = false;
    box.innerHTML = `
      <span class="ub-ic">${IC.user}</span>
      <span class="ub-txt"><strong>${esc(user.name)}</strong><small>${roleLbl}</small></span>
      <button class="icon-btn" id="logoutBtn" title="${STR.auth.logout}" aria-label="${STR.auth.logout}">${IC.logout}</button>`;
    box.querySelector("#logoutBtn").addEventListener("click", () => this.logout());

    if (user.role === "driver") { showView("view-driver"); Driver.init(user); }
    else { showView("view-client"); Client.init(user); }
  },

  async logout() {
    await api.post("/api/auth/logout", {}).catch(() => {});
    if (Client.poll) clearInterval(Client.poll);
    if (Driver.poll) clearInterval(Driver.poll);
    Driver.closeFeed();
    Track.closeAll();
    LiveMap.reset();
    this.showAuth();
  },
};

App.boot();
