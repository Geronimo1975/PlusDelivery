# Dashboard Faza 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Un folder `dashboard/` cu 5 module Django independente, dashboard-ul Admin/Operațional funcțional, poarta de validare a contului (stub) și securizarea login-ului — fără a atinge SPA `/app` sau API-urile `delivery/`.

**Architecture:** `dashboard/` e un pachet-container cu 5 app-uri de sine stătătoare (`dashboard.authorization`, `dashboard.accounts`, `dashboard.finance`, `dashboard.logistics`, `dashboard.core`). Modulele comunică între ele doar prin `services.py`; `delivery.Order`/`delivery.Profile` sunt nucleu legacy exceptat și pot fi importate direct. UI bogat doar pentru Admin/Operațional; Client/Business/Șofer rămân scheletelor. DRF doar pentru API-urile noi.

**Tech Stack:** Django 5.x, DRF (nou), django-axes (nou), server-rendered templates, sesiuni cookie + CSRF, SQLite local / Postgres prod.

**Spec:** `docs/superpowers/specs/2026-10-31-dashboard-architecture-design.md`

## Global Constraints

- Django 5.x, ASGI (Daphne + Channels) — neatins.
- `manage.py check` și `makemigrations --check` trebuie să treacă (CI le rulează).
- Fiecare modul = app propriu cu `apps.py` (AppConfig `name="dashboard.<mod>"`, `label="<mod>"`), migrații commise.
- Regula de independență: niciun modul nou nu importă modelele altui modul nou în views; doar prin `services.py`. `delivery.*` e exceptat.
- SPA `/app`, rutele `/api/*` din `delivery/` și fluxul `delivery/auth_api.py` rămân NEATINSE. Înregistrările existente sunt grandfather-uite.
- `verified_via` stochează `"stub"` acum; valori viitoare `"google"/"facebook"/"linkedin"`.
- Dashboard servit sub prefix `/dashboard/`.

## Review Focus

- **Utilizator nevalidat care forțează un POST de comandă/aplicație șofer** direct (fără butonul de confirmare) → serverul trebuie să refuze (403/redirect), nu doar să ascundă butonul. Test în Task 4/6.
- **Acces la view-uri Admin/Operațional de către non-staff** → 403/redirect la login, nu 200. Test în Task 6.
- **`DriverApplication` dublă** (același user aplică de două ori) → o singură aplicație activă, nu duplicate. Test în Task 3.
- **`Wallet` cu ambii owner setați sau niciunul** → constrângere de integritate respinge. Test în Task 5.
- **Lockout la login după N încercări eșuate** apoi acces legitim blocat corect/deblocat după fereastră → test axes în Task 7.

---

## Task 1: Scaffold pachetul `dashboard/` + 5 app-uri + settings

**Files:**
- Create: `dashboard/__init__.py`, `dashboard/urls.py`
- Create (per modul `m` in authorization, accounts, finance, logistics, core): `dashboard/m/__init__.py`, `dashboard/m/apps.py`, `dashboard/m/urls.py`
- Modify: `plusdelivery/settings.py` (INSTALLED_APPS + DRF + password validators), `plusdelivery/urls.py` (include `dashboard.urls` sub `dashboard/`)
- Create: `requirements.txt` (adaugă `djangorestframework`, `django-axes`)
- Test: `dashboard/tests/test_scaffold.py`

**Interfaces:**
- Produces: fiecare app încărcat cu `label` scurt; `dashboard/urls.py` cu `app_name="dashboard"` include-uind sub-namespace-urile `authorization/ accounts/ finance/ logistics/` și rădăcina `core`.

- [ ] **Step 1: Write the failing test** — `test_apps_loaded`: `django.apps.apps.get_app_config("authorization")` ... pentru toate 5 labels, nu ridică excepție; `test_dashboard_url_resolves`: `reverse("dashboard:home")` întoarce path care începe cu `/dashboard/`.
- [ ] **Step 2: Run** `pytest dashboard/tests/test_scaffold.py -v` → FAIL (apps/urls lipsesc).
- [ ] **Step 3:** Creează pachetele + AppConfig-urile (`name="dashboard.<mod>"`, `label="<mod>"`). Adaugă cele 5 în INSTALLED_APPS + `rest_framework` + `axes`. Reactivează `AUTH_PASSWORD_VALIDATORS` (cele 4 standard Django). `dashboard/core/urls.py` definește `path("", views.home, name="home")` (placeholder view întoarce `HttpResponse`). Include în `plusdelivery/urls.py`: `path("dashboard/", include("dashboard.urls"))`.
- [ ] **Step 4: Run** test → PASS; apoi `python manage.py check` → 0 erori.
- [ ] **Step 5: Commit** `feat(dashboard): scaffold package, 5 apps, DRF+axes+password validators`.

## Task 2: Modulul `accounts` — tipuri cont, Organization, Membership

**Files:**
- Create: `dashboard/accounts/models.py`, `dashboard/accounts/services.py`, `dashboard/accounts/migrations/`
- Test: `dashboard/accounts/tests/test_models.py`

**Interfaces:**
- Produces: `Organization(id, name, owner→User, created_at)`; `Membership(user→User, organization→Organization, role∈{admin,manager,employee})` unique(user, organization); `AccountProfile(user OneToOne, account_type∈{personal,business,premium} default personal)`. `services.get_account_type(user)->str`, `services.organizations_for(user)->QuerySet`.

- [ ] **Step 1: Write failing tests** — `test_membership_unique` (al doilea Membership identic ridică IntegrityError); `test_default_account_type` (`get_account_type(user)=="personal"`); `test_organizations_for_returns_member_orgs`.
- [ ] **Step 2: Run** → FAIL (modele lipsesc).
- [ ] **Step 3:** Definește modelele + `services.py`. `role` ca `TextChoices`. `account_type` ca `TextChoices`.
- [ ] **Step 4:** `makemigrations accounts` apoi rulează testele → PASS.
- [ ] **Step 5: Commit** `feat(accounts): Organization, Membership, AccountProfile + services`.

## Task 3: Modulul `authorization` — verificare, aplicație șofer, permisiuni

**Files:**
- Create: `dashboard/authorization/models.py`, `services.py`, `permissions.py`, `migrations/`
- Test: `dashboard/authorization/tests/test_models.py`, `test_permissions.py`

**Interfaces:**
- Consumes: `delivery.models.Profile` (rol client/driver).
- Produces: `AccountVerification(user OneToOne, is_verified bool default False, verified_via CharField default "", verified_at DateTime null)`; `DriverApplication(user→User, status∈{pending,approved,rejected} default pending, submitted_at, reviewed_by→User null, reviewed_at null)` cu constrângere „o singură aplicație ne-rejected per user". `services.confirm_account(user, via="stub")->AccountVerification`; `services.submit_driver_application(user)->DriverApplication`; `services.approve_driver(application, reviewer)`. `permissions.is_verified(user)->bool`; `permissions.can_order(user)->bool`; `permissions.can_drive(user)->bool`; DRF `IsVerified`, `IsDriverApproved`; decorator `require_verified(view)`.

- [ ] **Step 1: Write failing tests** — `test_confirm_sets_flags` (`is_verified True`, `verified_via "stub"`, `verified_at` setat); `test_duplicate_active_application_rejected` (a doua aplicație pending ridică IntegrityError/ValidationError); `test_can_order_requires_verified`; `test_can_drive_requires_verified_and_approved`.
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3:** Implementează modelele, serviciile și `permissions.py`. Constrângere unică prin `UniqueConstraint(fields=["user"], condition=Q(status__in=["pending","approved"]))`.
- [ ] **Step 4:** `makemigrations authorization` + teste → PASS.
- [ ] **Step 5: Commit** `feat(authorization): verification gate, driver application, permissions`.

## Task 4: Modulul `logistics` — strat de servicii peste `delivery.Order`

**Files:**
- Create: `dashboard/logistics/services.py`, `dashboard/logistics/__init__.py` (fără modele noi acum)
- Test: `dashboard/logistics/tests/test_services.py`

**Interfaces:**
- Consumes: `delivery.models.Order`, `authorization.permissions.can_order`.
- Produces: `services.all_orders()->QuerySet`; `services.orders_for_dispatch()->QuerySet` (fără șofer asignat); `services.place_order_guard(user)` ridică `PermissionDenied` dacă `not can_order(user)`.

- [ ] **Step 1: Write failing test** — `test_place_order_guard_blocks_unverified` (ridică PermissionDenied); `test_orders_for_dispatch_excludes_assigned`.
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3:** Implementează serviciile peste `delivery.Order`.
- [ ] **Step 4:** Teste → PASS.
- [ ] **Step 5: Commit** `feat(logistics): service layer over delivery.Order + order guard`.

## Task 5: Modulul `finance` — portofel polimorf, tranzacții, extrase

**Files:**
- Create: `dashboard/finance/models.py`, `services.py`, `migrations/`
- Test: `dashboard/finance/tests/test_models.py`

**Interfaces:**
- Consumes: `accounts.Organization`.
- Produces: `Wallet(user→User null, organization→Organization null, balance Decimal default 0)` cu `CheckConstraint`: exact unul dintre user/organization setat; `Transaction(wallet, amount, kind∈{credit,debit}, order_code CharField blank, created_at)`; `Statement(wallet, period_start, period_end)`; `DriverEarning(user, amount, order_code, created_at)`. `services.wallet_for(user|org)->Wallet` (get_or_create); `services.record_transaction(wallet, amount, kind, order_code="")`.

- [ ] **Step 1: Write failing tests** — `test_wallet_requires_exactly_one_owner` (ambii seturi → IntegrityError; niciunul → IntegrityError); `test_record_transaction_updates_balance`.
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3:** Implementează. Constrângere: `CheckConstraint(check=(Q(user__isnull=False) & Q(organization__isnull=True)) | (Q(user__isnull=True) & Q(organization__isnull=False)))`.
- [ ] **Step 4:** `makemigrations finance` + teste → PASS.
- [ ] **Step 5: Commit** `feat(finance): polymorphic Wallet, Transaction, Statement, DriverEarning`.

## Task 6: Modulul `core` — poarta de validare + dashboard Admin/Operațional + stub-uri

**Files:**
- Create: `dashboard/core/views.py`, `dashboard/core/urls.py` (extinde Task 1), `dashboard/core/templates/dashboard/{base,home,gate,admin,stub}.html`
- Test: `dashboard/core/tests/test_views.py`
- Note: invocă `ui-ux-pro-max` înainte de a scrie template-urile (CLAUDE.md global).

**Interfaces:**
- Consumes: `authorization.services.confirm_account`, `authorization.permissions`, `authorization.services.submit_driver_application`, `authorization.services.approve_driver`, `logistics.services`, `accounts.services`.
- Produces: `views.home` (rutează pe rol → admin dacă staff, altfel stub pe rol); `views.gate` (GET afișează bannerul; POST "confirm" → `confirm_account`); `views.driver_apply` (POST → `submit_driver_application`, guard: verificat); `views.admin_home` (staff-only: comenzi, coadă aplicații șofer); `views.approve_driver` (POST staff-only).

- [ ] **Step 1: Write failing tests** — `test_admin_home_forbidden_for_non_staff` (non-staff → 302/403); `test_admin_home_ok_for_staff`; `test_gate_post_confirms` (după POST, `is_verified True`); `test_driver_apply_blocked_when_unverified` (403/redirect); `test_approve_driver_sets_approved`.
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3:** Invocă `ui-ux-pro-max`, apoi implementează views (toate `@login_required`; admin cu `user_passes_test(is_staff)`) + template-uri. Stub-urile Client/Business/Șofer = pagină schelet + bannerul porții dacă nevalidat.
- [ ] **Step 4:** Teste → PASS.
- [ ] **Step 5: Commit** `feat(core): validation gate, admin/ops dashboard, role stubs`.

## Task 7: Securizare login — django-axes

**Files:**
- Modify: `plusdelivery/settings.py` (AXES_* + backend auth + MIDDLEWARE), `requirements.txt`
- Test: `dashboard/tests/test_login_security.py`

**Interfaces:**
- Produces: lockout după `AXES_FAILURE_LIMIT` încercări eșuate pe fereastra `AXES_COOLOFF_TIME`.

- [ ] **Step 1: Write failing test** — `test_lockout_after_failed_attempts`: N+1 login-uri greșite → al (N+1)-lea răspunde cu lockout (status 429/403 per config axes); `test_valid_login_before_limit_ok`.
- [ ] **Step 2: Run** → FAIL.
- [ ] **Step 3:** Adaugă `axes` în INSTALLED_APPS (dacă nu la Task 1), `AxesStandaloneBackend` în `AUTHENTICATION_BACKENDS`, `AxesMiddleware`, `AXES_FAILURE_LIMIT=5`, `AXES_COOLOFF_TIME=1` (oră), `AXES_LOCKOUT_PARAMETERS`. `makemigrations` (axes aduce migrații).
- [ ] **Step 4:** Teste → PASS; `manage.py check` → 0 erori.
- [ ] **Step 5: Commit** `feat(security): login rate-limiting via django-axes`.

## Task 8: Smoke CI + verificare finală

**Files:**
- Modify: `.github/workflows/ci.yml` (adaugă `/dashboard/` la smoke test), eventual `requirements.txt`
- Test: extinde smoke-ul existent.

- [ ] **Step 1:** Adaugă în smoke-ul CI o cerere la `/dashboard/` (așteaptă 302 redirect la login pentru anonim).
- [ ] **Step 2: Run** local: `manage.py check`, `makemigrations --check`, toată suita `pytest`.
- [ ] **Step 3: Commit** `ci: smoke /dashboard/ route`.

---

## Self-Review

- **Spec coverage:** folder+5 module (T1–T6), categorii dashboard (T6), validare stub+aprobare șofer (T3,T6), securitate parole+axes+CSRF+permisiuni (T1,T3,T6,T7), DRF (T1), Wallet polimorf (T5), `delivery/` neatins (toate). ✔
- **Review Focus:** fiecare linie are test în T3/T4/T5/T6/T7. ✔
- **Type consistency:** `confirm_account`/`is_verified`/`can_order`/`can_drive`/`wallet_for` folosite consecvent între T3→T4→T6. ✔
- **Proporție:** plan ≈ lungime comparabilă cu spec-ul, semnături nu corpuri. ✔
