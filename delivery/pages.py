"""View-uri pentru paginile de marketing / conținut (structura „site public"),
construite după arhitectura sitemap-ului Lalamove (de + en).

Textul sursă este în germană; engleza vine din locale/en (.po → .mo).
Fiecare pagină are acum template dedicat (home, persoane, business, curieri,
servicii, prețuri, blog, legal etc.) — nu mai există placeholdere generice.
"""

from django.shortcuts import render
from django.http import Http404
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


# ---------------------------------------------------------------------------
# Pagini cu template dedicat (design complet)
# ---------------------------------------------------------------------------
def home(request):
    return render(request, "marketing/home.html", {"active": "home"})


def persoane(request):
    return render(request, "marketing/persoane.html", {"active": "persoane"})


def business(request):
    return render(request, "marketing/business.html", {"active": "business"})


def curieri(request):
    return render(request, "marketing/curieri.html", {"active": "curieri"})


def servicii(request):
    return render(request, "marketing/servicii.html", {"active": "servicii"})


def preturi(request):
    return render(request, "marketing/preturi.html", {"active": "preturi"})


def faq(request):
    return render(request, "marketing/faq.html", {})


def contact(request):
    return render(request, "marketing/contact.html", {})


def sitemap_page(request):
    return render(request, "marketing/sitemap.html", {})


# ---------------------------------------------------------------------------
# Blog (date demonstrative; se poate înlocui ulterior cu un model)
# ---------------------------------------------------------------------------
# Fiecare articol are slug pe limba (DE sursa + EN); link-ul din lista si ruta
# se rezolva dupa limba activa (vezi blog.html si POSTS_BY_SLUG de mai jos).
POSTS = [
    {
        "slug": "das-richtige-fahrzeug-waehlen",
        "slug_en": "choose-the-right-vehicle",
        "tag": _("Ratgeber"),
        "title": _("So wählst du das richtige Fahrzeug für deine Lieferung"),
        "excerpt": _("Vom Fahrrad bis zum Transporter — der Schnellratgeber, damit du korrekt zahlst und alles sicher ankommt."),
    },
    {
        "slug": "lieferung-am-selben-tag-fuer-deinen-shop",
        "slug_en": "same-day-delivery-for-your-shop",
        "tag": _("Business"),
        "title": _("Lieferung am selben Tag für deinen Onlineshop"),
        "excerpt": _("Wie die Conversion steigt, wenn du schnelle lokale Lieferung anbietest — und wie du sie mit PlusDelivery automatisierst."),
    },
    {
        "slug": "5-gruende-fahrer-zu-werden",
        "slug_en": "5-reasons-to-become-a-driver",
        "tag": _("Fahrer"),
        "title": _("5 Gründe, PlusDelivery-Fahrer zu werden"),
        "excerpt": _("Flexible Zeiten, transparenter Verdienst und volle Kontrolle über die Fahrten, die du annimmst."),
    },
    {
        "slug": "tipps-pakete-verpacken",
        "slug_en": "tips-packing-parcels",
        "tag": _("Tipps"),
        "title": _("7 Tipps, damit deine Sendung heil ankommt"),
        "excerpt": _("Einfache Verpackungsregeln für Pakete, Glas und zerbrechliche Gegenstände."),
    },
    {
        "slug": "umzug-ohne-stress",
        "slug_en": "stress-free-move",
        "tag": _("Ratgeber"),
        "title": _("Umzug ohne Stress: was du tust und was wir übernehmen"),
        "excerpt": _("Plane deinen Umzug Schritt für Schritt und erfahre, wann sich ein Transporter mit Beladehilfe lohnt."),
    },
    {
        "slug": "plusdelivery-waechst",
        "slug_en": "plusdelivery-grows",
        "tag": _("Neuigkeiten"),
        "title": _("PlusDelivery wächst in neue Städte"),
        "excerpt": _("Wir bauen das Fahrernetz und die Abdeckung aus. Das kommt als Nächstes."),
    },
]
# Rezolva un articol din oricare slug (DE sau EN), indiferent de limba din URL.
POSTS_BY_SLUG = {}
for _p in POSTS:
    POSTS_BY_SLUG[_p["slug"]] = _p
    POSTS_BY_SLUG[_p["slug_en"]] = _p


def blog(request):
    return render(request, "marketing/blog.html", {"active": "blog", "posts": POSTS})


def blog_post(request, slug):
    post = POSTS_BY_SLUG.get(slug)
    if not post:
        raise Http404("Artikel nicht gefunden")
    return render(request, "marketing/blog_post.html", {"active": "blog", "post": post})


# ---------------------------------------------------------------------------
# Servicii (sub-pagini) — landing SEO cu design complet (service_landing.html)
# ---------------------------------------------------------------------------
_ICON_CAR = mark_safe('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 11l2-5h8l3 5M3 11h18v5H3zM7 16a2 2 0 1 0 0 .01M17 16a2 2 0 1 0 0 .01"/></svg>')
_ICON_BOLT = mark_safe('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M13 2 3 14h7l-1 8 10-12h-7l1-8z"/></svg>')
_ICON_TRUCK = mark_safe('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M3 7h11v8H3zM14 10h4l3 3v2h-7z"/><circle cx="7" cy="18" r="1.6"/><circle cx="17" cy="18" r="1.6"/></svg>')
_ICON_CUBE = mark_safe('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 17V7l8-4 8 4v10l-8 4z"/><path d="m4 7 8 4 8-4M12 11v10"/></svg>')
_ICON_PIN = mark_safe('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="10" r="3"/><path d="M12 21s-7-5.6-7-11a7 7 0 0 1 14 0c0 5.4-7 11-7 11z"/></svg>')


def _service(ctx):
    def view(request):
        return render(request, "marketing/service_landing.html", {"sl": ctx})
    return view


serv_zilnice = _service({
    "eyebrow": _("Service"),
    "title": _("Tägliche Lieferungen"),
    "lead": _("Pakete, Einkäufe und Dokumente mit dem PKW geliefert — am selben Tag, ohne Umwege."),
    "icon": _ICON_CAR,
    "features_title": _("Für den Alltag gemacht"),
    "features": [
        (_("Lieferung am selben Tag"), _("Bestelle am Morgen, geliefert am Nachmittag — innerhalb deiner Stadt.")),
        (_("Passendes Fahrzeug"), _("Vom Fahrrad bis zum PKW, je nach Größe deiner Sendung.")),
        (_("Transparenter Preis"), _("Du siehst die Kosten vor der Bestätigung, ganz ohne Überraschungen.")),
    ],
    "cta_title": _("Hast du etwas zu senden?"),
    "cta_text": _("Erstelle in weniger als einer Minute einen Auftrag."),
})

serv_urgente = _service({
    "eyebrow": _("Service"),
    "title": _("Eillieferungen in der Stadt"),
    "lead": _("Sofortige Abholung für Sendungen, die nicht warten können. Der nächste Fahrer übernimmt direkt."),
    "icon": _ICON_BOLT,
    "features_title": _("Wenn jede Minute zählt"),
    "features": [
        (_("Abholung in Minuten"), _("Der nächstgelegene Fahrer übernimmt deine Fahrt sofort.")),
        (_("Direkte Route"), _("Ohne Zwischenstopps — vom Abholort direkt zum Ziel.")),
        (_("Live-Verfolgung"), _("Verfolge die Sendung in Echtzeit bis zur Zustellung.")),
    ],
    "cta_title": _("Eine dringende Sendung?"),
    "cta_text": _("Bestelle jetzt und der nächste Fahrer ist unterwegs."),
})

serv_mutari = _service({
    "eyebrow": _("Service"),
    "title": _("Umzug & Möbeltransport"),
    "lead": _("Transporter und Hilfe beim Beladen für sperrige Gegenstände — vom einzelnen Sofa bis zum kompletten Umzug."),
    "icon": _ICON_TRUCK,
    "features_title": _("Für große Teile"),
    "features": [
        (_("Transporter in mehreren Größen"), _("Vom Kleintransporter bis zum großen Transporter für Paletten.")),
        (_("Hilfe beim Beladen"), _("Optionale Unterstützung beim Tragen und Verladen.")),
        (_("Sicher ans Ziel"), _("Geprüfte Fahrer, die auch empfindliche Möbel sorgfältig transportieren.")),
    ],
    "cta_title": _("Planst du einen Transport?"),
    "cta_text": _("Hol dir eine Schätzung für dein Möbelstück oder deinen Umzug."),
})

integrari = _service({
    "eyebrow": _("Für Unternehmen"),
    "title": _("E-Commerce-Integrationen"),
    "lead": _("Verbinde deinen Onlineshop und automatisiere die Letzte-Meile-Lieferung — ohne manuelle Schritte."),
    "icon": _ICON_CUBE,
    "features_title": _("In deinen Ablauf integriert"),
    "features": [
        (_("Shop-Plugins"), _("Shopify und WooCommerce verbinden sich in wenigen Minuten.")),
        (_("API & Webhooks"), _("Erstelle Aufträge automatisch und erhalte Status-Updates in Echtzeit.")),
        (_("Zentrale Abrechnung"), _("Eine einzige monatliche Rechnung für alle Lieferungen.")),
    ],
    "cta_title": _("Bereit zu integrieren?"),
    "cta_text": _("Fordere ein Angebot an und verbinde deinen Shop mit PlusDelivery."),
})

puncte = _service({
    "eyebrow": _("Service"),
    "title": _("Abholorte"),
    "lead": _("Ein Netz von Punkten für bequeme Abholung und Abgabe — in deiner Nähe und zu flexiblen Zeiten."),
    "icon": _ICON_PIN,
    "features_title": _("Bequem und flexibel"),
    "features": [
        (_("In deiner Nähe"), _("Punkte über die ganze Stadt verteilt, immer in Reichweite.")),
        (_("Flexible Zeiten"), _("Gib ab oder hol ab, wann es dir passt.")),
        (_("Sichere Übergabe"), _("Deine Sendung wartet sicher bis zur Abholung.")),
    ],
    "cta_title": _("Punkt in der Nähe finden"),
    "cta_text": _("Öffne die App, um den nächstgelegenen Abholort zu sehen."),
})


# ---------------------------------------------------------------------------
# Companie — pagini cu design dedicat
# ---------------------------------------------------------------------------
def despre(request):
    return render(request, "marketing/about.html", {})


def cariere(request):
    return render(request, "marketing/careers.html", {"active": None})


def business_thanks(request):
    return render(request, "marketing/thank_you.html", {})


# ---------------------------------------------------------------------------
# Legal — continut real (acelasi text ca pe georgeai.dev), data-driven.
# Textul sursa e germana; engleza vine din locale/en (.po). Operator / date
# firma sunt reale (George Sebastian Cucuiet, Hanstedt).
# ---------------------------------------------------------------------------
_LEGAL_UPDATED = _("Oktober 2026")


def _legal(ctx):
    def view(request):
        return render(request, "marketing/legal.html", {"lg": ctx})
    return view


date_firma = _legal({  # Impressum
    "title": _("Impressum"),
    "sub": _("Angaben gemäß § 5 DDG"),
    "updated": _LEGAL_UPDATED,
    "sections": [
        (_("Anbieter"), _("George Sebastian Cucuiet\nGreuner Brook 1\n21271 Hanstedt, Deutschland")),
        (_("Kontakt"), _("Telefon: +49 160 4155546\nE-Mail: contact@plusdelivery.de")),
        (_("Umsatzsteuer-ID"), _("Gemäß § 19 UStG (Kleinunternehmerregelung) wird keine Umsatzsteuer berechnet; eine Umsatzsteuer-Identifikationsnummer liegt daher nicht vor.\nSteuernummer: 50/108/03727")),
        (_("Verantwortlich für den Inhalt"), _("George Sebastian Cucuiet, Anschrift wie oben.")),
        (_("Streitschlichtung"), _("Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: https://ec.europa.eu/consumers/odr. Ich bin nicht verpflichtet und nicht bereit, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.")),
    ],
})


confidentialitate = _legal({  # Datenschutz
    "title": _("Datenschutzerklärung"),
    "sub": _("Wie Ihre Daten erhoben, genutzt und geschützt werden"),
    "updated": _LEGAL_UPDATED,
    "sections": [
        (_("Überblick"), _("Der Schutz Ihrer personenbezogenen Daten ist mir wichtig. Diese Website wird im Einklang mit der EU-Datenschutz-Grundverordnung (DSGVO) betrieben. Personenbezogene Daten werden nur verarbeitet, wenn dafür eine Rechtsgrundlage besteht.")),
        (_("Erhobene Daten"), _("Wenn Sie mich kontaktieren, einen Termin buchen oder den Konfigurator nutzen, verarbeite ich die von Ihnen übermittelten Daten (z. B. Name, E-Mail, Telefon und Ihre Nachricht). Beim Besuch der Website können technische Daten wie IP-Adresse, Browser und Zeitstempel verarbeitet werden.")),
        (_("Zweck & Rechtsgrundlage"), _("Ihre Daten werden ausschließlich zur Beantwortung Ihrer Anfrage, zur Angebotserstellung und zur Leistungserbringung (Art. 6 Abs. 1 lit. b DSGVO) sowie zum Betrieb und zur Sicherheit der Website (Art. 6 Abs. 1 lit. f DSGVO) verwendet. Die Newsletter-Anmeldung erfolgt auf Grundlage Ihrer Einwilligung (Art. 6 Abs. 1 lit. a DSGVO), die Sie jederzeit widerrufen können.")),
        (_("Weitergabe & Hosting"), _("Daten werden, soweit möglich, bei meinen Dienstleistern innerhalb der EU gehostet. Ich verkaufe Ihre Daten nicht. Auftragsverarbeiter sind durch Verträge zur Auftragsverarbeitung gebunden.")),
        (_("Ihre Rechte"), _("Sie haben das Recht auf Auskunft, Berichtigung, Löschung, Einschränkung und Übertragbarkeit Ihrer Daten sowie auf Widerspruch. Zur Ausübung genügt eine E-Mail an contact@plusdelivery.de. Zudem können Sie sich bei einer Aufsichtsbehörde beschweren.")),
        (_("Speicherdauer"), _("Daten werden nur so lange gespeichert, wie es für die genannten Zwecke erforderlich oder gesetzlich vorgeschrieben ist, und danach gelöscht.")),
    ],
})


termeni = _legal({  # AGB / Terms
    "title": _("Allgemeine Geschäftsbedingungen"),
    "sub": _("Bedingungen für die Leistungserbringung"),
    "updated": _LEGAL_UPDATED,
    "sections": [
        (_("Geltungsbereich"), _("Diese Bedingungen gelten für alle über PlusDelivery angebotenen Leistungen — Automatisierung, KI, Web, Daten und zugehörige Beratung — soweit keine gesonderte schriftliche Vereinbarung gilt.")),
        (_("Leistungen"), _("Der konkrete Umfang, die Ergebnisse und der Zeitplan jedes Auftrags werden in einem individuellen Angebot festgelegt, das vor Arbeitsbeginn vereinbart wird.")),
        (_("Angebote & Preise"), _("Angebote werden projektbezogen erstellt und sind, sofern nicht anders angegeben, 30 Tage gültig. Preise verstehen sich ggf. zzgl. USt.")),
        (_("Haftung"), _("Die Haftung ist auf Vorsatz und grobe Fahrlässigkeit beschränkt, ausgenommen Schäden aus der Verletzung des Lebens, des Körpers oder der Gesundheit. Für mittelbare Schäden hafte ich im gesetzlich zulässigen Rahmen nicht.")),
        (_("Anwendbares Recht"), _("Es gilt das Recht der Bundesrepublik Deutschland. Gerichtsstand ist, soweit gesetzlich zulässig, mein Geschäftssitz.")),
    ],
})


cookies = _legal({  # Cookie-Richtlinie
    "title": _("Cookie-Richtlinie"),
    "sub": _("Wie Cookies und ähnliche Technologien genutzt werden"),
    "updated": _LEGAL_UPDATED,
    "sections": [
        (_("Was Cookies sind"), _("Cookies sind kleine Textdateien, die auf Ihrem Gerät gespeichert werden. Sie sorgen für die Funktion der Website und helfen zu verstehen, wie sie genutzt wird.")),
        (_("Kategorien"), _("Essenzielle Cookies sind für den Betrieb der Website erforderlich und immer aktiv. Optionale Analyse-Cookies helfen mir, die Website zu verbessern, und werden nur mit Ihrer Einwilligung gesetzt.")),
        (_("Ihre Wahl"), _("Beim ersten Besuch können Sie optionale Cookies annehmen oder ablehnen. Sie können Ihre Wahl jederzeit ändern, indem Sie Cookies im Browser löschen oder den Einwilligungsbanner erneut öffnen.")),
        (_("Cookies verwalten"), _("Die meisten Browser erlauben das Blockieren oder Löschen von Cookies in den Einstellungen. Das Blockieren essenzieller Cookies kann die Funktion der Website beeinträchtigen.")),
    ],
})
