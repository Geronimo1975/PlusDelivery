# PlusDelivery — Arhitectura Dashboard (Django backend)

**Data:** 2026-10-31
**Autor:** Claude (senior Django) — pe baza cerințelor lui George
**Status:** PROPUNERE — așteaptă aprobare înainte de implementare

---

## 1. Intenție și „de ce"

Astăzi tot backend-ul trăiește într-un singur app `delivery/`: `User` default +
`Profile` (rol `client`/`driver`, business = flag `is_business`), un singur model
`Order` denormalizat (comandă + rută + tracking + asignare șofer), date hardcodate
în `data.py`, API scris de mână cu `JsonResponse` (fără DRF), sesiuni pe cookie,
WebSockets prin Channels. Nu există: validare de cont, aprobare șofer, finanțe,
roluri de echipă, sau un dashboard server-rendered (doar Django admin).

Vrem un **Dashboard coordonat din Django**, cu module **separate și independente**
(`dashboard`, `authorization`, `finance`, `logistics`, `accounts`) ca să se poată
lucra pe fiecare separat, flexibil pentru schimbări viitoare. După login, un
utilizator capătă dreptul de a plasa comenzi; dacă e șofer, vede joburi și — după
validare — accesează comenzi de transport. Partea de login/dashboard trebuie
securizată clar.

## 2. Obiective

- Folder `dashboard/` care conține modulele backend, URL-urile și fișierele unui
  Dashboard Django complet.
- Cinci module **independente**, fiecare cu modelele, URL-urile și serviciile lui:
  `authorization`, `accounts`, `finance`, `logistics`, și `core` (prezentarea
  dashboard-ului care asamblează din celelalte).
- Categorii de dashboard clar definite, pe tip de audiență: **Client**, **Business**,
  **Șofer**, **Admin/Operațional**.
- Securizarea login-ului și a dashboard-ului (sesiuni, CSRF, permisiuni pe rol,
  rate-limiting la autentificare, protecție la forța brută).
- Poartă de **validare a contului** prin Google/Facebook/LinkedIn (confirmare unică),
  ca precondiție pentru a plasa comenzi / a șofa.
- Separare curată: fiecare modul poate fi dezvoltat, testat și modificat izolat.

## 3. Non-obiective (acum)

- Implementarea efectivă OAuth Google/FB/LinkedIn (rămâne pas separat — vezi
  [[plusdelivery-social-login]]). Acum pregătim doar *structura* și *poarta*.
- Plăți reale / integrare procesator (Stripe etc.). `finance` capătă modele și API,
  dar fără gateway live.
- Rescrierea `delivery/` existent. Rămâne funcțional; migrăm treptat.
- Mobile app nativ.

## 4. Anti-obiective (ce ar însemna eșec, chiar dacă „merge tehnic")

- Module care se importă unele pe altele în lanț (cuplaj strâns) — ar anula
  independența cerută.
- Dublarea logicii din `delivery/` în loc de reutilizare prin servicii.
- Un dashboard unic monolit care decide totul cu `if role == ...` împrăștiat.
- Validarea socială devenită obligatorie *înainte* de login (trebuie să fie
  **după** login, ca pas de deblocare).

## 5. Constrângeri

- Stack existent: Django 5.x, ASGI (Daphne + Channels), SQLite local / Postgres prod,
  sesiuni pe cookie + CSRF, fără Celery, fără allauth (încă).
- Deploy live pe plusdelivery.de (VPS, Traefik, GitHub Actions). CI rulează
  `manage.py check`, `makemigrations --check`, smoke pe rute. Orice modul nou trebuie
  să treacă `check` și să aibă migrații commise.
- `AUTH_PASSWORD_VALIDATORS` e gol acum — îl reactivăm pentru dashboard.
- SPA la `/app` rămâne; dashboard-ul nou e server-rendered sub `/dashboard/`.

## 6. Arhitectura — decizii luate (ale mele, de confirmat)

### 6.1 Layout fizic
```
dashboard/                      # pachet container
  __init__.py
  urls.py                       # agregă URL-urile tuturor sub-modulelor
  core/                         # prezentarea dashboard-ului (views pe rol)
    apps.py  (label="dashboard_core")
    views.py  urls.py  templates/dashboard/...
  authorization/                # app independent
    apps.py  (label="authorization")
    models.py  services.py  permissions.py  urls.py  api.py
  accounts/
    apps.py  (label="accounts")
    models.py  services.py  urls.py  api.py
  finance/
    apps.py  (label="finance")
    models.py  services.py  urls.py  api.py
  logistics/
    apps.py  (label="logistics")
    models.py  services.py  urls.py  api.py
```
Fiecare sub-folder e un **app Django de sine stătător** (AppConfig cu `name`
complet `dashboard.authorization` și `label` scurt). Intră individual în
INSTALLED_APPS. `dashboard/urls.py` le include sub namespace-uri
(`authorization:`, `accounts:`, `finance:`, `logistics:`, `dashboard:`).

**Regulă de independență:** modulele comunică DOAR prin `services.py`
(funcții publice) și prin semnale, niciodată importând modele unele din altele în
views. Astfel fiecare se poate muta/rescrie izolat.

### 6.2 DRF
Introduc **Django REST Framework** doar pentru API-urile noi de dashboard
(serializers + `permissions` pe rol/validare). API-urile vechi `/api/*` din
`delivery/` rămân neatinse; migrare treptată ulterior.

### 6.3 Poarta de validare — confirmare unică, cu mecanism provizoriu
După login, utilizatorul ajunge pe dashboard dar cu cont **nevalidat**. Un singur
pas marchează contul `is_verified=True` permanent și deblochează: pentru client →
plasarea comenzilor; pentru șofer → depunerea aplicației de șofer (care apoi trece
prin aprobare manuală). Nu e al doilea factor per-sesiune.

**Mecanism ACUM (OAuth amânat) — decizia lui George:** banner „Cont nevalidat"
pe dashboard cu buton **„Confirmă contul"** care setează provizoriu
`is_verified=True` (fără provider real). Șoferul, suplimentar, creează o
`DriverApplication` care trece prin **aprobare manuală din admin**. Când vine
OAuth Google/FB/LinkedIn, înlocuim DOAR mecanismul din spatele butonului;
`AccountVerification`, UI-ul și poarta rămân aceleași. `verified_via` va stoca
`"stub"` acum, apoi `"google"/"facebook"/"linkedin"`.

### 6.4 Categoriile de dashboard (pe audiență) + scopul fazei ACUM
SPA-ul `/app` rămâne **suprafața principală** pentru client/șofer/business.
Dashboard-ul server-rendered `/dashboard/` se construiește astfel (decizia lui
George):

1. **Admin/Operațional** (staff) — **construit REAL acum**: toate comenzile, aprobă
   șoferi (`DriverApplication`), reconciliere financiară, dispecerat.
2. **Client** (personal) — **stub acum** (schelet pagină + poarta de validare).
3. **Business** — **stub acum** (echipă Admin/Manager/Employee, portofel comun,
   extrase; tipuri cont personal/business/premium — structură pregătită, UI minimal).
4. **Șofer** — **stub acum** (schelet + starea de validare/aprobare).

Modelele și serviciile celor 5 module se creează pentru toate categoriile (ca
structura să fie completă și independentă), dar **UI-ul bogat** se implementează
acum doar pentru Admin/Operațional; restul rămân scheletelor pentru faze viitoare.

## 7. Modelele per modul (schiță — builder completează detaliile)

- **authorization**: `AccountVerification(user OneToOne, is_verified, verified_via,
  verified_at)`; `DriverApplication(user, status=pending/approved/rejected,
  documents, submitted_at, reviewed_by, reviewed_at)`; `permissions.py` cu helperi
  `require_verified`, `require_driver_approved`, `require_role`.
- **accounts**: `AccountType` (personal/business/premium) pe profil;
  `Organization(name, owner, ...)`; `Membership(user, organization,
  role=admin/manager/employee)`. (Pe termen scurt reutilizează `delivery.Profile`;
  migrarea câmpurilor e temă separată.)
- **finance**: `Wallet(owner, balance)`; `Transaction(wallet, amount, type, order_ref)`;
  `Invoice`, `Statement(period)`, `DriverEarning`. Prețurile vin din
  `delivery.data.quote_for_vehicle` printr-un serviciu, fără gateway live acum.
- **logistics**: strat subțire peste `delivery.Order` prin servicii; modele proprii
  noi (zone, dispecerat) adăugate ulterior. Nu dublează `Order`.
- **core**: fără modele; doar views + context builders per rol.

## 8. Securitate

- Reactivăm `AUTH_PASSWORD_VALIDATORS`.
- Login dashboard: throttling / lockout la încercări eșuate; mesaje de eroare
  neutre; CSRF pe toate formularele; `login_required` + verificări de permisiune
  pe fiecare view; redirect la poarta de validare dacă `is_verified=False`.
- Separarea permisiunilor în `authorization.permissions` (sursă unică de adevăr).
- Sesiuni: cookie `Secure`+`HttpOnly`+`SameSite` în prod (deja parțial în settings).

## 8bis. Decizii fixate la review (ale mele, răsturnabile)

- **`delivery/` = nucleu legacy exceptat.** Regula de independență (modulele nu-și
  importă modelele între ele) se aplică *între cele 5 module noi*. `delivery.Order`
  și `delivery.Profile` POT fi importate direct de module ca nucleu partajat; totuși
  accesul se preferă printr-un `delivery`-facing service subțire unde există.
- **Înregistrările existente sunt grandfather-uite.** Fluxul SPA de register/login
  rămâne neschimbat acum; noua poartă de validare + aprobarea șoferului se aplică
  pe suprafața de dashboard. Șoferii deja existenți nu sunt blocați retroactiv în
  această fază.
- **Rate-limiting login = DB-backed (`django-axes`).** Adaugă o dependență + migrații,
  dar supraviețuiește restartului și scalării pe procese — mai sigur decât un
  contor in-memory per-proces (stack-ul n-are Redis garantat, nici Celery).
- **`finance.Wallet.owner` = polimorf prin două FK nullable** (`user` XOR
  `organization`), cu constrângere de integritate. Permite portofel personal și
  portofel comun de echipă fără rescriere de schemă.

## 9. Ce rămâne la builder

- Schema exactă a câmpurilor fiecărui model + migrații.
- Template-urile și layout-ul vizual al fiecărei categorii de dashboard
  (va trece prin skill-ul `ui-ux-pro-max` înainte de orice cod UI).
- Rutele DRF concrete și serializers.
- Planul de migrare treptată dinspre `delivery/`.
- Testele (TDD) per modul.

## 10. Dimensiune

Proiect cu document scris → după aprobare urmează un plan complet
(`superpowers:writing-plans`), apoi implementare modul cu modul.
