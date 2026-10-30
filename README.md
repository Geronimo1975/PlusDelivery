# PlusDelivery — prototip marketplace de livrari & transport la cerere

Prototip funcțional inspirat de **Lalamove**: conectează **clienți** care au nevoie
de o livrare cu **șoferi/curieri** independenți, plus o vedere pentru **business**
(companii care trimit multe livrări).

- **Zona de serviciu:** Hamburg și împrejurimi, pe o **rază de maximum 100 km**.
- **Autentificare + roluri:** conturi reale (sesiuni Django) pentru **client** și **șofer**;
  clientul poate fi „business”. Fiecare rol are dashboard-ul lui (model ca la Lalamove:
  portaluri separate pentru *Benutzer* și *Fahrer*).
- **Hartă reală:** Leaflet + tile-uri Esri (fără cheie API) cu urmărire live.
- **Urmărire live prin WebSocket (Django Channels):** poziția șoferului și starea comenzii
  se trimit *push* către client/șofer, fără polling din browser (fallback automat pe polling lent).
- **Notificări (toast + sunet):** șoferul e anunțat la comandă nouă (feed WebSocket), clientul
  la livrare. **Rating după cursă:** clientul dă 1–5 stele, media șoferului se actualizează.
- **Rute reale pe străzi:** OSRM — distanța, prețul, ETA și traseul desenat urmează drumurile reale.
- **Adrese scrise liber:** geocodare cu Nominatim (OSM) — tastezi orice adresă din zona Hamburg, cu sugestii instant; reperele presetate rămân ca alegere rapidă.
- **Stack:** Django (Python) pentru backend + HTML/CSS/JavaScript pentru frontend.

> **Notă despre sursă:** fluxul este aliniat cu site-ul live **lalamove.eu/de-de**
> (verificat: trei audiențe — Privatkunden / Geschäftskunden / Lieferpartner, portaluri
> separate de login pentru clienți și șoferi, urmărire live „Echtzeit-Tracking”):
> tip serviciu → rută → alegere vehicul → preț instant → comandă → urmărire live.

---

## 1. Ce îți trebuie (o singură dată)

- **Python 3.10+**. Verifică în terminal:
  ```bash
  python3 --version
  ```
  Dacă nu ai Python, descarcă-l de la <https://www.python.org/downloads/>.

## 2. Instalare și pornire (pas cu pas)

Deschide un terminal în folderul proiectului (`PlusDelivery`) și rulează:

1. Creează și activează un **mediu virtual** *(un folder izolat pentru bibliotecile
   proiectului, ca să nu „murdărești” sistemul)*:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate        # pe Windows: .venv\Scripts\activate
   ```
2. Instalează dependențele (Django + Channels/Daphne pentru WebSocket):
   ```bash
   pip install -r requirements.txt
   ```
3. Creează baza de date locală *(aplică „migrările” = structura tabelelor în SQLite)*:
   ```bash
   python manage.py migrate
   ```
4. Pornește serverul:
   ```bash
   python manage.py runserver
   ```
5. Deschide în browser: **<http://localhost:8000/app>** (aplicația funcțională).
   Rădăcina `/` servește site-ul public de prezentare; aplicația cu login e la `/app`.

Oprire: `Ctrl + C`. Data viitoare e suficient: `source .venv/bin/activate` + `python manage.py runserver`.

*(Opțional)* Cont de administrator pentru panoul Django (`/admin`), unde vezi comenzile în DB:
```bash
python manage.py createsuperuser
```

---

## 3. Cum se folosește (demo)

Întâi **creezi un cont** (sau te autentifici). La înregistrare alegi rolul:

- **Client** — alegi serviciul (*Colete & marfă* / *Transport & fret*), ruta (din zona
  Hamburg), vezi prețul pe fiecare vehicul, comanzi, apoi urmărești comanda pe **harta
  reală** și pe linia de stare, actualizate la fiecare 2 secunde. Dacă bifezi **cont
  business**, primești în plus un panou cu statistici (comenzi, venit, șoferi online) și
  un buton care generează comenzi demo în serie.
- **Șofer** — comuți **online/offline**, vezi comenzile disponibile, le accepți, urmărești
  livrarea pe hartă și avansezi starea. (Serverul avansează și automat stările — vezi
  secțiunea „simulat”.) Vezi și castigul din livrările finalizate.

**Flux rapid (recomandat în 2 ferestre / 2 conturi):** autentifică-te ca *client* și
creează o comandă → într-o altă fereastră, autentifică-te ca *șofer*, apasă „Acceptă” →
revino pe fereastra clientului și privește șoferul mișcându-se pe hartă spre livrare.

---

## 4. De ce acest stack

| Parte | Tehnologie | De ce |
|------|------------|-------|
| Backend | **Django 5 (Python)** | Robust, cu ORM și panou de admin incluse; ușor de extins spre produs real. |
| Bază de date | **SQLite** (implicit în Django) | Zero configurare; se poate schimba pe PostgreSQL printr-o singură setare. |
| Frontend | **HTML + CSS + JavaScript simplu** | Fără pas de build; servit de Django prin template + fișiere statice. |
| Hartă | **Leaflet + tile-uri Esri** | Hărți reale, gratuite, fără cheie API. |
| Autentificare | **Sesiuni Django** | Conturi + roluri incluse, fără dependințe noi. |
| Timp real | **Django Channels + Daphne** | WebSocket push pentru urmărire live; `runserver` pornește automat ASGI. |

---

## 5. Structura fișierelor

```
PlusDelivery/
├─ manage.py                 # utilitarul Django (migrate, runserver, ...)
├─ requirements.txt
├─ plusdelivery/             # configurarea proiectului
│  ├─ settings.py            # setări (DB, aplicații, fișiere statice, Channels)
│  ├─ asgi.py                # punctul de intrare ASGI (HTTP + WebSocket)
│  └─ urls.py                # rutele de nivel înalt (+ /admin)
├─ delivery/                 # aplicația de livrări
│  ├─ data.py                # vehicule, locații Hamburg, prețuri, zona de 100 km
│  ├─ models.py              # modelele Profile (rol client/șofer) + Order + serializare
│  ├─ auth_api.py            # înregistrare / login / logout / me (sesiuni Django)
│  ├─ views.py               # pagina + API-ul REST (JSON), cu gating pe rol
│  ├─ urls.py                # rutele /api/... (+ site public)
│  ├─ ws_urls.py             # rutele WebSocket (ws/track/<cod>/)
│  ├─ consumers.py           # consumer WebSocket pentru urmărirea unei comenzi
│  ├─ realtime.py            # „ceasul” async care face push la starea comenzilor urmărite
│  ├─ routing.py             # rute reale pe străzi prin OSRM (+ fallback linie dreaptă)
│  ├─ geocoding.py           # geocodare adresă liberă prin Nominatim (OSM), limitată la Hamburg
│  ├─ simulation.py          # firul care mișcă șoferul pe traseul real și avansează stările
│  └─ admin.py               # Order + Profile vizibile în /admin
├─ templates/index.html      # shell-ul aplicației funcționale (/app)
├─ static/
│  ├─ css/styles.css         # stiluri + temă light/dark
│  └─ js/app.js              # autentificare + dashboard client / șofer + harta Leaflet
├─ Dockerfile                # imaginea de producție (Daphne/ASGI, utilizator ne-privilegiat)
├─ entrypoint.sh             # așteaptă DB → migrate → collectstatic → pornește Daphne
├─ docker-compose.prod.yml   # stack producție: Postgres + web (Daphne) + Nginx
├─ nginx/default.conf        # TLS, static, proxy /ws/ (WebSocket) + aplicație
├─ .env.example              # șablon de variabile de mediu pentru producție
└─ .dockerignore
```

### API pe scurt (pentru extindere)
- `POST /api/auth/register` · `POST /api/auth/login` · `POST /api/auth/logout` · `GET /api/auth/me` — autentificare (sesiuni)
- `GET  /api/config` — vehicule, locații, tipuri de serviciu, flux de stări, zona de serviciu
- `GET  /api/geocode?q=...` — caută adrese (Nominatim), limitat la zona Hamburg
- `POST /api/quote` — preț pe fiecare vehicul (acceptă reper presetat sau adresă liberă; validează zona de 100 km)
- `GET  /api/orders` (comenzile proprii) · `POST /api/orders` — creare (doar client autentificat)
- `GET  /api/orders/<cod>` — o comandă (doar clientul proprietar sau șoferul atribuit)
- `GET  /api/driver/jobs` — comenzi disponibile + ale mele + castig (doar șofer)
- `POST /api/driver/online` — comută online/offline (doar șofer)
- `POST /api/orders/<cod>/accept` · `POST /api/orders/<cod>/status` — șofer acceptă / avansează
- `POST /api/orders/<cod>/rate` — client dă nota (1–5) după livrare; actualizează media șoferului
- `GET  /api/stats` — statistici pe comenzile clientului business
- `WS   ws/track/<cod>/` — **WebSocket**: push live cu starea comenzii (doar proprietar/șofer atribuit)
- `WS   ws/driver/` — **WebSocket**: feed de comenzi disponibile pentru șoferi (notificare comandă nouă)

---

## 6. Ce este real vs. simulat

**Implementat (funcțional):**
- **Autentificare reală (sesiuni Django)** cu roluri **client** și **șofer**; clientul poate fi
  business. Comenzile sunt legate de cont; accesul la API e restricționat pe rol (401/403) —
  un client nu vede comenzile altuia, doar șoferul atribuit poate avansa o comandă.
- **Dashboard pe rol:** clientul (booking + urmărire live + panou business opțional);
  șoferul (online/offline, comenzi disponibile, comenzile mele cu hartă live, castig)
- Zona de serviciu Hamburg + rază de **100 km** (validată pe server la ofertă și la comandă)
- **Rute reale pe străzi (OSRM):** traseul desenat pe hartă, distanța, prețul și ETA
  urmează drumurile reale; șoferul se mișcă de-a lungul traseului, nu în linie dreaptă
- **Adrese scrise liber (Nominatim/OSM):** autocomplete accesibil (tastatură: săgeți/Enter/Escape); adresele din afara razei de 100 km sunt marcate și nu pot fi alese
- Hartă reală (Leaflet + tile-uri Esri) cu ruta, punctele de ridicare/livrare și poziția șoferului
- Preț pe distanță (bază + per km + per minut, pe distanța reală de la OSRM)
- Comenzi **persistente** în baza de date (SQLite), cu cod `PD-####`
- Acceptare de către șofer, flux de stări
- **Urmărire live prin WebSocket (Django Channels):** harta și starea comenzii se actualizează
  prin *push*, nu prin polling; pollingul lent rămâne doar ca fallback. Rulează fără Redis
  (channel layer în memorie, un singur proces).
- **Notificări în timp real (toast + sunet WebAudio):** șoferul primește „Comandă nouă
  disponibilă!” prin feed-ul `ws/driver/`; clientul primește „... a fost livrată!” din
  WebSocket-ul comenzii. Fără fișiere audio (ton scurt generat în browser).
- **Rating după cursă:** clientul acordă 1–5 stele unei comenzi livrate (`/rate`); media
  șoferului se recalculează din toate comenzile lui evaluate. O comandă se evaluează o singură dată.
- **Opriri intermediare (multi-stop):** clientul poate adăuga 0..N opriri între ridicare și
  livrare (listă editabilă: adaugă / șterge / reordonează ↑↓, fiecare cu același autocomplete).
  Ruta OSRM trece prin toate punctele, prețul se calculează pe distanța totală, iar harta le
  afișează ca marcaje numerotate; șoferul simulat urmează traseul complet prin opriri.
- **Istoric + câștiguri în timp:** clientul are „Comenzi active” (carduri live cu hartă) separate
  de „Istoric livrări” (listă compactă cu dată, rută, preț și evaluare); șoferul vede un grafic
  „Câștig pe zile (ultimele 7)” (bare cu valori în €, cu tabel-fallback accesibil).
- Panou business cu statistici + comenzi în serie (demo) + panou de admin Django
- **Securitate:** protecție **CSRF activă** pe toate cererile POST (antet `X-CSRFToken`, 403 fără el)
  și escapare HTML a datelor introduse de utilizatori (anti-XSS)

**Simulat (de înlocuit pentru producție) — caută `INLOCUIESTE IN PRODUCTIE` în cod:**
- **Server Nominatim** — `delivery/geocoding.py` folosește serverul public OSM Nominatim (cere un
  `User-Agent` real și are o limită de ~1 cerere/secundă). Real: Nominatim găzduit de tine sau
  Mapbox/Google Geocoding cu cheie API. Reperele presetate din `delivery/data.py` rămân ca fallback rapid.
- **Server OSRM** — `delivery/routing.py` folosește serverul public demo OSRM (fără garanții de
  uptime, cu limite de utilizare) și cade pe linie dreaptă dacă e indisponibil. Real: OSRM
  găzduit de tine sau Mapbox/Google Directions cu cheie API.
- **Poziția șoferului** — `delivery/simulation.py`: un fir de execuție o mută la 2s. Real:
  GPS trimis de aplicația șoferului prin WebSocket; task-uri cu Celery în loc de thread.
- **Timp real** — `delivery/realtime.py` + `InMemoryChannelLayer` (un singur proces, fără Redis);
  „ceasul” citește DB și face push la ~1,2s. Real: `channels_redis` + broadcast direct din codul
  care schimbă starea, pentru mai multe procese/servere.
- **Plăți** — inexistente. Real: Stripe.
- **Tile-uri hartă** — `static/js/app.js` folosește tile-uri Esri gratuite (fără cheie API).
  Real: plan plătit (Mapbox/Esri/CARTO) sau server propriu de tile-uri.
- **Securitate / autentificare** — autentificarea e reală (sesiuni Django, parole hash-uite) și
  **protecția CSRF este activă**: cererile POST cer antetul `X-CSRFToken` (frontend-ul îl trimite
  din cookie-ul `csrftoken`, setat la încărcarea paginii prin `@ensure_csrf_cookie`); fără el,
  serverul răspunde 403. Datele introduse de utilizatori (adrese, nume, notițe) sunt **escapate
  HTML** (`esc()` în `app.js`) înainte de afișare, ca măsură anti-XSS. Rămâne pentru producție:
  verificare email + resetare parolă, politici de parolă și **rate limiting** la login.

---

## 7. Pași următori spre un produs real

1. ✅ **PostgreSQL + deployment** (Docker + Nginx + HTTPS) — gata, vezi secțiunea 8.
   Peste CSRF-ul deja activ rămân: verificare email, resetare parolă, politici de parolă
   și rate limiting la login.
2. **OSRM propriu** (sau Mapbox/Google) + poziție GPS reală de la aplicația șoferului,
   trimisă prin WebSocket-ul deja existent (Channels), în loc de firul de simulare;
   `channels_redis` (Redis) pentru a scala pe mai multe procese/servere.
3. **Plăți** (Stripe) și facturare pentru clienți business.
4. Aplicație mobilă pentru șoferi (React Native / Flutter) peste același API.
5. Notificări **push/SMS** (peste cele in-app deja existente) și prețuri dinamice pe zone și cerere.
6. Întărirea securității (CSRF, rate limiting, validare și sanitizare a intrărilor).

---

## 8. Deployment în producție (Docker)

Aplicația e pregătită pentru producție: **Postgres** în loc de SQLite, **WhiteNoise**
pentru fișierele statice, **Daphne** (ASGI) pentru HTTP + WebSocket, totul în spatele
**Nginx** cu HTTPS. Setările se citesc din mediu (`.env`), iar local, fără nicio variabilă,
aplicația rulează neschimbată pe SQLite.

### Ce rulează
- **db** — PostgreSQL 16 (volum persistent).
- **web** — un singur proces Daphne. ⚠️ Un singur worker e intenționat: „ceasul" realtime
  (`realtime._loop`) presupune un singur event-loop. Pentru a scala pe mai multe procese,
  setează `REDIS_URL` (comută automat pe `channels_redis`) și mută broadcaster-ul într-un
  worker dedicat.
- **nginx** — terminare TLS, servire `/static/`, proxy pentru `/ws/` (WebSocket) și aplicație.

### Pași pe server (VPS cu Docker + Docker Compose)
```bash
# 1. Codul pe server
git clone <repo> /opt/plusdelivery && cd /opt/plusdelivery

# 2. Variabilele de mediu
cp .env.example .env
#    editează .env: DJANGO_SECRET_KEY, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS,
#    POSTGRES_PASSWORD și DATABASE_URL (aceeași parolă)
python -c "import secrets; print(secrets.token_urlsafe(50))"   # generează SECRET_KEY

# 3. Domeniul în Nginx (3 locuri)
sed -i 's/DOMENIU.EXEMPLU.RO/domeniul-tau.ro/g' nginx/default.conf

# 4. Certificat TLS (Let's Encrypt) — o singură dată
#    pune fullchain.pem + privkey.pem sub nginx/certs/live/domeniul-tau.ro/
#    (ex. cu certbot pe host, apoi montezi folderul; vezi certbot --webroot)

# 5. Pornire
docker compose -f docker-compose.prod.yml up -d --build
#    entrypoint-ul rulează automat migrate + collectstatic
```

`migrate` și `collectstatic` rulează automat la fiecare pornire a containerului `web`
(în `entrypoint.sh`). Loguri: `docker compose -f docker-compose.prod.yml logs -f web`.

### Backup bază de date
```bash
docker compose -f docker-compose.prod.yml exec -T db \
  pg_dump -U plusdelivery -Fc plusdelivery > backup_$(date +%F).dump
```

### Verificat local (fără Docker)
`python manage.py check --deploy` → **0 probleme** în mod producție (DEBUG=0, Postgres,
HSTS, cookie-uri Secure). Comanda de producție (`daphne … plusdelivery.asgi:application`)
servește `/app` și fișierele statice prin WhiteNoise. (Build-ul imaginii Docker necesită
daemon-ul Docker pornit.)
