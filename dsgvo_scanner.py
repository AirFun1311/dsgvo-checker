#!/usr/bin/env python3
"""
DSF DSGVO/GDPR Compliance Scanner - Production Grade
=====================================================
Engine: DSF-PRO-CORE v2.0
Modus: Zero Trust / Fail Closed
Rendering: Playwright (JS) + requests (Fallback)

(c) 2026 DSF Consulting - AF13-NEXUS
"""

import re
import ssl
import json
import socket
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin
from typing import Optional
from dataclasses import dataclass, field

import requests

# Playwright optional - Fallback auf requests
try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


# =============================================================================
# TRACKER / DRITTANBIETER DATENBANK
# =============================================================================

KNOWN_TRACKERS = {
    # --- Analytics ---
    "google-analytics.com":     {"name": "Google Analytics",     "category": "analytics",  "country": "US", "risk": "hoch"},
    "googletagmanager.com":     {"name": "Google Tag Manager",   "category": "analytics",  "country": "US", "risk": "hoch"},
    "analytics.google.com":     {"name": "Google Analytics",     "category": "analytics",  "country": "US", "risk": "hoch"},
    "hotjar.com":               {"name": "Hotjar",               "category": "analytics",  "country": "EU", "risk": "mittel"},
    "clarity.ms":               {"name": "Microsoft Clarity",    "category": "analytics",  "country": "US", "risk": "hoch"},
    "matomo.cloud":             {"name": "Matomo Cloud",         "category": "analytics",  "country": "EU", "risk": "niedrig"},
    "plausible.io":             {"name": "Plausible",            "category": "analytics",  "country": "EU", "risk": "niedrig"},
    "hubspot.com":              {"name": "HubSpot",              "category": "analytics",  "country": "US", "risk": "hoch"},
    "segment.com":              {"name": "Segment",              "category": "analytics",  "country": "US", "risk": "hoch"},
    "mixpanel.com":             {"name": "Mixpanel",             "category": "analytics",  "country": "US", "risk": "hoch"},
    "heap.io":                  {"name": "Heap Analytics",       "category": "analytics",  "country": "US", "risk": "hoch"},
    "amplitude.com":            {"name": "Amplitude",            "category": "analytics",  "country": "US", "risk": "hoch"},
    # --- Advertising / Tracking Pixel ---
    "facebook.net":             {"name": "Meta Pixel",           "category": "advertising","country": "US", "risk": "hoch"},
    "facebook.com":             {"name": "Meta/Facebook",        "category": "advertising","country": "US", "risk": "hoch"},
    "connect.facebook.net":     {"name": "Meta Pixel",           "category": "advertising","country": "US", "risk": "hoch"},
    "doubleclick.net":          {"name": "Google Ads",           "category": "advertising","country": "US", "risk": "hoch"},
    "googlesyndication.com":    {"name": "Google AdSense",       "category": "advertising","country": "US", "risk": "hoch"},
    "googleadservices.com":     {"name": "Google Ads",           "category": "advertising","country": "US", "risk": "hoch"},
    "tiktok.com":               {"name": "TikTok Pixel",         "category": "advertising","country": "CN", "risk": "hoch"},
    "snap.licdn.com":           {"name": "LinkedIn Insight",     "category": "advertising","country": "US", "risk": "hoch"},
    "linkedin.com":             {"name": "LinkedIn",             "category": "advertising","country": "US", "risk": "hoch"},
    "ads-twitter.com":          {"name": "X/Twitter Ads",        "category": "advertising","country": "US", "risk": "hoch"},
    "pinterest.com":            {"name": "Pinterest Tag",        "category": "advertising","country": "US", "risk": "hoch"},
    "criteo.com":               {"name": "Criteo",               "category": "advertising","country": "FR", "risk": "mittel"},
    "taboola.com":              {"name": "Taboola",              "category": "advertising","country": "US", "risk": "hoch"},
    "outbrain.com":             {"name": "Outbrain",             "category": "advertising","country": "US", "risk": "hoch"},
    # --- CDN / Externe Ressourcen ---
    "fonts.googleapis.com":     {"name": "Google Fonts",         "category": "cdn",        "country": "US", "risk": "hoch"},
    "fonts.gstatic.com":        {"name": "Google Fonts Static",  "category": "cdn",        "country": "US", "risk": "hoch"},
    "ajax.googleapis.com":      {"name": "Google CDN",           "category": "cdn",        "country": "US", "risk": "mittel"},
    "cdnjs.cloudflare.com":     {"name": "Cloudflare CDN",       "category": "cdn",        "country": "US", "risk": "niedrig"},
    "cdn.jsdelivr.net":         {"name": "jsDelivr CDN",         "category": "cdn",        "country": "EU", "risk": "niedrig"},
    "unpkg.com":                {"name": "unpkg CDN",            "category": "cdn",        "country": "US", "risk": "mittel"},
    "stackpath.bootstrapcdn.com": {"name": "Bootstrap CDN",      "category": "cdn",        "country": "US", "risk": "niedrig"},
    # --- Embeds ---
    "youtube.com":              {"name": "YouTube Embed",        "category": "embed",      "country": "US", "risk": "hoch"},
    "youtube-nocookie.com":     {"name": "YouTube (No-Cookie)",  "category": "embed",      "country": "US", "risk": "mittel"},
    "youtu.be":                 {"name": "YouTube",              "category": "embed",      "country": "US", "risk": "hoch"},
    "maps.googleapis.com":      {"name": "Google Maps",          "category": "embed",      "country": "US", "risk": "hoch"},
    "maps.google.com":          {"name": "Google Maps",          "category": "embed",      "country": "US", "risk": "hoch"},
    "vimeo.com":                {"name": "Vimeo",                "category": "embed",      "country": "US", "risk": "mittel"},
    "player.vimeo.com":         {"name": "Vimeo Player",         "category": "embed",      "country": "US", "risk": "mittel"},
    "open.spotify.com":         {"name": "Spotify Embed",        "category": "embed",      "country": "SE", "risk": "mittel"},
    "soundcloud.com":           {"name": "SoundCloud",           "category": "embed",      "country": "DE", "risk": "niedrig"},
    # --- Social ---
    "platform.twitter.com":     {"name": "X/Twitter Widget",     "category": "social",     "country": "US", "risk": "hoch"},
    "platform.instagram.com":   {"name": "Instagram Widget",     "category": "social",     "country": "US", "risk": "hoch"},
    # --- Consent Tools (Positivliste) ---
    "cookiebot.com":            {"name": "Cookiebot",            "category": "consent",    "country": "DK", "risk": "keine"},
    "usercentrics.eu":          {"name": "Usercentrics",         "category": "consent",    "country": "DE", "risk": "keine"},
    "cookiefirst.com":          {"name": "CookieFirst",          "category": "consent",    "country": "NL", "risk": "keine"},
    "onetrust.com":             {"name": "OneTrust",             "category": "consent",    "country": "US", "risk": "niedrig"},
    "cookieyes.com":            {"name": "CookieYes",            "category": "consent",    "country": "GB", "risk": "niedrig"},
    "borlabs.io":               {"name": "Borlabs Cookie",       "category": "consent",    "country": "DE", "risk": "keine"},
    "complianz.io":             {"name": "Complianz",            "category": "consent",    "country": "NL", "risk": "keine"},
    "consentmanager.net":       {"name": "consentmanager",       "category": "consent",    "country": "DE", "risk": "keine"},
    "klaro.org":                {"name": "Klaro!",               "category": "consent",    "country": "DE", "risk": "keine"},
    # --- Hosting / Infrastruktur ---
    "cloudfront.net":           {"name": "AWS CloudFront",       "category": "cdn",        "country": "US", "risk": "mittel"},
    "akamaized.net":            {"name": "Akamai CDN",           "category": "cdn",        "country": "US", "risk": "mittel"},
    "fastly.net":               {"name": "Fastly CDN",           "category": "cdn",        "country": "US", "risk": "mittel"},
    # --- Chat / Support ---
    "intercom.io":              {"name": "Intercom",             "category": "chat",       "country": "US", "risk": "hoch"},
    "zendesk.com":              {"name": "Zendesk",              "category": "chat",       "country": "US", "risk": "hoch"},
    "tawk.to":                  {"name": "Tawk.to",              "category": "chat",       "country": "US", "risk": "hoch"},
    "crisp.chat":               {"name": "Crisp Chat",           "category": "chat",       "country": "FR", "risk": "mittel"},
    "livechatinc.com":          {"name": "LiveChat",             "category": "chat",       "country": "US", "risk": "hoch"},
    # --- Payment ---
    "stripe.com":               {"name": "Stripe",               "category": "payment",    "country": "US", "risk": "mittel"},
    "js.stripe.com":            {"name": "Stripe.js",            "category": "payment",    "country": "US", "risk": "mittel"},
    "paypal.com":               {"name": "PayPal",               "category": "payment",    "country": "US", "risk": "mittel"},
    # --- Sonstiges ---
    "recaptcha.net":            {"name": "Google reCAPTCHA",     "category": "security",   "country": "US", "risk": "hoch"},
    "google.com/recaptcha":     {"name": "Google reCAPTCHA",     "category": "security",   "country": "US", "risk": "hoch"},
    "gstatic.com/recaptcha":    {"name": "Google reCAPTCHA",     "category": "security",   "country": "US", "risk": "hoch"},
    "hcaptcha.com":             {"name": "hCaptcha",             "category": "security",   "country": "US", "risk": "mittel"},
    "gravatar.com":             {"name": "Gravatar",             "category": "embed",      "country": "US", "risk": "mittel"},
    "wp.com":                   {"name": "WordPress.com",        "category": "cdn",        "country": "US", "risk": "mittel"},
}

# Pflichtbegriffe fuer Datenschutzerklaerung
DSE_PFLICHTBEGRIFFE = {
    "verantwortlicher":   ["verantwortlich", "verantwortlicher", "responsible", "controller"],
    "rechtsgrundlage":    ["art. 6", "art.6", "rechtsgrundlage", "legal basis"],
    "betroffenenrechte":  ["betroffenenrecht", "auskunft", "recht auf", "data subject rights", "right to"],
    "auskunftsrecht":     ["auskunft", "art. 15", "art.15", "right of access"],
    "loeschung":          ["löschung", "loeschung", "art. 17", "art.17", "erasure", "right to erasure"],
    "aufsichtsbehoerde":  ["aufsichtsbehörde", "aufsichtsbehoerde", "supervisory authority"],
    "kontaktdaten":       ["e-mail", "email", "telefon", "phone", "anschrift", "address"],
    "speicherdauer":      ["speicherdauer", "aufbewahrung", "storage period", "retention"],
    "drittlandtransfer":  ["drittland", "drittstaaten", "usa", "third country", "third countries", "adequacy"],
}

# Pflichtbegriffe fuer Impressum
IMPRESSUM_PFLICHTBEGRIFFE = {
    "name_firma":         ["gmbh", "ug", "ag", "e.k.", "gbr", "ohg", "kg", "inc.", "ltd."],
    "anschrift":          ["straße", "strasse", "str.", "platz", "weg", "allee", "gasse"],
    "kontakt":            ["telefon", "tel.", "tel:", "phone", "e-mail", "email", "mail"],
    "register":           ["handelsregister", "hrb", "hra", "registergericht", "amtsgericht"],
    "ust_id":             ["ust-id", "ust-idnr", "umsatzsteuer", "vat", "de[0-9]{9}"],
    "vertretung":         ["geschäftsführer", "geschaeftsfuehrer", "vorstand", "inhaber", "vertreten durch", "managing director"],
}

# Security Headers
SECURITY_HEADERS = {
    "strict-transport-security":  {"name": "HSTS",                       "weight": 20, "critical": True},
    "x-content-type-options":     {"name": "X-Content-Type-Options",     "weight": 10, "critical": False},
    "x-frame-options":            {"name": "X-Frame-Options",            "weight": 10, "critical": False},
    "content-security-policy":    {"name": "Content-Security-Policy",    "weight": 15, "critical": True},
    "referrer-policy":            {"name": "Referrer-Policy",            "weight": 15, "critical": True},
    "permissions-policy":         {"name": "Permissions-Policy",         "weight": 10, "critical": False},
    "x-xss-protection":          {"name": "X-XSS-Protection",           "weight": 5,  "critical": False},
}


# =============================================================================
# DATENKLASSEN
# =============================================================================

@dataclass
class CheckResult:
    key: str
    status: str            # PASS, WARNING, FAIL, INFO, SKIPPED
    title: str
    detail: str
    penalty: int = 0
    rechtsgrundlage: str = ""
    empfehlung: str = ""
    sub_findings: list = field(default_factory=list)


@dataclass
class ScanResult:
    url: str
    final_url: str = ""
    scan_date: str = ""
    scan_id: str = ""
    risk_score: int = 0
    risk_level: str = "UNBEKANNT"
    checks: list = field(default_factory=list)
    third_parties: list = field(default_factory=list)
    cookies_before_consent: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)
    meta: dict = field(default_factory=dict)
    dse_coverage: dict = field(default_factory=dict)


# =============================================================================
# SCANNER
# =============================================================================

class DSGVOScanner:

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    def __init__(self, url: str, use_playwright: bool = True):
        raw = url.strip().rstrip("/")
        self.input_url = raw if raw.startswith("http") else f"https://{raw}"
        self.use_playwright = use_playwright and HAS_PLAYWRIGHT

        self.session = requests.Session()
        self.session.headers["User-Agent"] = self.USER_AGENT

        now = datetime.now(timezone.utc)
        scan_hash = hashlib.sha256(f"{self.input_url}{now.isoformat()}".encode()).hexdigest()[:12]

        self.result = ScanResult(
            url=self.input_url,
            scan_date=now.strftime("%d.%m.%Y %H:%M:%S UTC"),
            scan_id=f"DSF-{scan_hash.upper()}",
            meta={
                "engine": "DSF-PRO-CORE v2.0",
                "mode": "fail_closed",
                "renderer": "playwright" if self.use_playwright else "requests",
                "js_rendering": self.use_playwright,
            }
        )

        # Interne Daten
        self._html_raw = ""          # Rohes HTML (requests)
        self._html_rendered = ""     # JS-gerendertes HTML (Playwright)
        self._response_headers = {}
        self._status_code = None
        self._final_url = ""
        self._redirect_chain = []
        self._external_domains = set()
        self._page_resources = []    # Alle geladenen URLs (Playwright)
        self._cookies_raw = []       # Cookies vor Consent
        self._consent_system = None

    # =========================================================================
    # FETCH
    # =========================================================================

    def _fetch_requests(self) -> bool:
        """HTTP-Fetch ohne JS-Rendering (Fallback)."""
        try:
            r = self.session.get(self.input_url, timeout=15, allow_redirects=True)
            self._status_code = r.status_code
            self._html_raw = r.text
            self._final_url = r.url
            self._response_headers = {k.lower(): v for k, v in r.headers.items()}

            # Redirect-Chain
            self._redirect_chain = []
            for resp in r.history:
                self._redirect_chain.append({
                    "url": resp.url,
                    "status": resp.status_code
                })

            if self._status_code != 200:
                self._add_check(CheckResult(
                    key="http_status", status="FAIL",
                    title="HTTP-Status",
                    detail=f"Website liefert HTTP {self._status_code} statt 200.",
                    penalty=25,
                    empfehlung="Webserver-Konfiguration pruefen."
                ))
                return False

            if len(self._html_raw) < 300:
                self._add_check(CheckResult(
                    key="content_integrity", status="FAIL",
                    title="Seiteninhalt",
                    detail="Seiteninhalt zu kurz oder leer -- Auswertung nicht moeglich.",
                    penalty=40,
                    empfehlung="Pruefen ob die Website korrekt ausgeliefert wird."
                ))
                return False

            return True

        except requests.exceptions.SSLError as e:
            self._add_check(CheckResult(
                key="connectivity", status="FAIL",
                title="Verbindung",
                detail=f"SSL-Fehler beim Verbindungsaufbau: {e}",
                penalty=40,
                empfehlung="SSL-Zertifikat und HTTPS-Konfiguration pruefen."
            ))
            return False

        except requests.exceptions.ConnectionError as e:
            self._add_check(CheckResult(
                key="connectivity", status="FAIL",
                title="Verbindung",
                detail=f"Website nicht erreichbar: {e}",
                penalty=50,
                empfehlung="DNS und Server-Verfuegbarkeit pruefen."
            ))
            return False

        except requests.exceptions.Timeout:
            self._add_check(CheckResult(
                key="connectivity", status="FAIL",
                title="Verbindung",
                detail="Timeout nach 15 Sekunden.",
                penalty=30,
                empfehlung="Server-Performance pruefen."
            ))
            return False

        except Exception as e:
            self._add_check(CheckResult(
                key="connectivity", status="FAIL",
                title="Verbindung",
                detail=f"Unerwarteter Fehler: {e}",
                penalty=50,
            ))
            return False

    def _fetch_playwright(self) -> bool:
        """Vollstaendiges JS-Rendering mit Playwright."""
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=self.USER_AGENT,
                    viewport={"width": 1920, "height": 1080},
                    locale="de-DE",
                )

                page = context.new_page()

                # Alle Netzwerk-Requests mitschneiden
                loaded_urls = []

                def on_response(response):
                    loaded_urls.append({
                        "url": response.url,
                        "status": response.status,
                        "resource_type": response.request.resource_type,
                    })

                page.on("response", on_response)

                # Navigieren
                response = page.goto(self.input_url, wait_until="networkidle", timeout=30000)

                if response:
                    self._status_code = response.status
                    self._final_url = page.url
                    self._response_headers = {k.lower(): v for k, v in response.headers.items()}

                # Warten bis Seite komplett
                page.wait_for_timeout(2000)

                # HTML nach JS-Rendering
                self._html_rendered = page.content()
                self._html_raw = self._html_rendered  # Unified

                # Geladene Ressourcen
                self._page_resources = loaded_urls

                # Externe Domains extrahieren
                site_domain = urlparse(self._final_url or self.input_url).hostname
                for res in loaded_urls:
                    try:
                        res_domain = urlparse(res["url"]).hostname
                        if res_domain and res_domain != site_domain:
                            # Auch Subdomains der eigenen Domain rausfiltern
                            if not res_domain.endswith(f".{site_domain}"):
                                self._external_domains.add(res_domain)
                    except Exception:
                        pass

                # Cookies VOR Consent auslesen (nichts angeklickt)
                cookies = context.cookies()
                self._cookies_raw = [
                    {
                        "name": c["name"],
                        "domain": c["domain"],
                        "path": c["path"],
                        "secure": c.get("secure", False),
                        "httpOnly": c.get("httpOnly", False),
                        "sameSite": c.get("sameSite", "None"),
                        "expires": c.get("expires", -1),
                    }
                    for c in cookies
                ]

                browser.close()

                if self._status_code and self._status_code != 200:
                    self._add_check(CheckResult(
                        key="http_status", status="FAIL",
                        title="HTTP-Status",
                        detail=f"Website liefert HTTP {self._status_code}.",
                        penalty=25,
                    ))
                    return False

                if len(self._html_rendered) < 300:
                    self._add_check(CheckResult(
                        key="content_integrity", status="FAIL",
                        title="Seiteninhalt",
                        detail="Nach JS-Rendering zu wenig Inhalt vorhanden.",
                        penalty=40,
                    ))
                    return False

                return True

        except Exception as e:
            # Fallback auf requests
            self.result.meta["renderer"] = "requests (playwright-fallback)"
            self.result.meta["js_rendering"] = False
            self._add_check(CheckResult(
                key="playwright_fallback", status="INFO",
                title="Rendering",
                detail=f"Playwright fehlgeschlagen ({e}). Fallback auf requests -- eingeschraenkte Erkennung.",
                penalty=0,
            ))
            return self._fetch_requests()

    # =========================================================================
    # CHECKS
    # =========================================================================

    def check_https_and_redirect(self):
        """HTTPS-Verschluesselung und Redirect-Verhalten pruefen."""
        final_scheme = urlparse(self._final_url or self.input_url).scheme
        input_scheme = urlparse(self.input_url).scheme

        if final_scheme == "https":
            # Pruefe ob HTTP automatisch redirected
            if input_scheme == "http":
                detail = "HTTPS aktiv. HTTP wird korrekt auf HTTPS umgeleitet."
            else:
                detail = "HTTPS aktiv."

            # HSTS pruefen
            hsts = self._response_headers.get("strict-transport-security", "")
            if hsts:
                detail += f" HSTS aktiv (max-age vorhanden)."
                self._add_check(CheckResult(
                    key="https", status="PASS", title="HTTPS-Verschluesselung",
                    detail=detail, rechtsgrundlage="Art. 32 DSGVO (Sicherheit der Verarbeitung)"
                ))
            else:
                detail += " HSTS-Header fehlt."
                self._add_check(CheckResult(
                    key="https", status="WARNING", title="HTTPS-Verschluesselung",
                    detail=detail, penalty=10,
                    rechtsgrundlage="Art. 32 DSGVO",
                    empfehlung="Strict-Transport-Security Header setzen (min. max-age=31536000)."
                ))
        else:
            self._add_check(CheckResult(
                key="https", status="FAIL", title="HTTPS-Verschluesselung",
                detail="Keine HTTPS-Verschluesselung. Daten werden unverschluesselt uebertragen.",
                penalty=35,
                rechtsgrundlage="Art. 32 DSGVO (Sicherheit der Verarbeitung)",
                empfehlung="Sofort SSL-Zertifikat einrichten und HTTPS erzwingen."
            ))

    def check_ssl_certificate(self):
        """SSL-Zertifikat: Gueltigkeit, Protokollversion."""
        host = urlparse(self._final_url or self.input_url).hostname
        if not host:
            return

        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_default_certs()

            with socket.create_connection((host, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()
                    protocol = ssock.version()

                    # Ablaufdatum
                    expires_str = cert.get("notAfter", "")
                    expires = datetime.strptime(expires_str, "%b %d %H:%M:%S %Y %Z")
                    days_left = (expires - datetime.now(timezone.utc).replace(tzinfo=None)).days

                    # Aussteller
                    issuer_parts = dict(x[0] for x in cert.get("issuer", []))
                    issuer = issuer_parts.get("organizationName", "Unbekannt")

                    sub_findings = []
                    penalty = 0

                    # Protokollversion
                    if protocol in ("TLSv1", "TLSv1.1"):
                        sub_findings.append(f"Unsicheres Protokoll: {protocol}")
                        penalty += 20
                    elif protocol == "TLSv1.2":
                        sub_findings.append(f"Protokoll: {protocol} (akzeptabel, TLS 1.3 empfohlen)")
                    else:
                        sub_findings.append(f"Protokoll: {protocol}")

                    # Zertifikat-Gueltigkeit
                    if days_left > 30:
                        sub_findings.append(f"Gueltig noch {days_left} Tage (Aussteller: {issuer})")
                        if penalty == 0:
                            self._add_check(CheckResult(
                                key="ssl", status="PASS", title="SSL-Zertifikat",
                                detail=f"Zertifikat gueltig ({days_left} Tage). {protocol}. Aussteller: {issuer}.",
                                sub_findings=sub_findings,
                                rechtsgrundlage="Art. 32 DSGVO"
                            ))
                        else:
                            self._add_check(CheckResult(
                                key="ssl", status="WARNING", title="SSL-Zertifikat",
                                detail=f"Zertifikat gueltig, aber veraltetes Protokoll.",
                                penalty=penalty, sub_findings=sub_findings,
                                rechtsgrundlage="Art. 32 DSGVO",
                                empfehlung="Auf TLS 1.3 upgraden, TLS 1.0/1.1 deaktivieren."
                            ))
                    elif days_left > 0:
                        self._add_check(CheckResult(
                            key="ssl", status="WARNING", title="SSL-Zertifikat",
                            detail=f"Zertifikat laeuft in {days_left} Tagen ab.",
                            penalty=15, sub_findings=sub_findings,
                            rechtsgrundlage="Art. 32 DSGVO",
                            empfehlung="Zertifikat umgehend erneuern."
                        ))
                    else:
                        self._add_check(CheckResult(
                            key="ssl", status="FAIL", title="SSL-Zertifikat",
                            detail="SSL-Zertifikat ist abgelaufen.",
                            penalty=30, sub_findings=sub_findings,
                            rechtsgrundlage="Art. 32 DSGVO",
                            empfehlung="Zertifikat sofort erneuern."
                        ))

        except ssl.SSLCertVerificationError as e:
            self._add_check(CheckResult(
                key="ssl", status="FAIL", title="SSL-Zertifikat",
                detail=f"Zertifikat ungueltig: {e}",
                penalty=30,
                rechtsgrundlage="Art. 32 DSGVO",
                empfehlung="Gueltiges SSL-Zertifikat installieren."
            ))
        except Exception as e:
            self._add_check(CheckResult(
                key="ssl", status="WARNING", title="SSL-Zertifikat",
                detail=f"SSL-Pruefung fehlgeschlagen: {e}",
                penalty=15,
            ))

    def check_privacy_policy(self):
        """Datenschutzerklaerung: Existenz und Pflichtinhalte."""
        paths = [
            "/datenschutz", "/datenschutzerklaerung", "/privacy",
            "/privacy-policy", "/datenschutzhinweise", "/data-privacy",
            "/datenschutz.html", "/datenschutzerklaerung.html",
        ]

        html_lower = self._html_raw.lower() if self._html_raw else ""

        # Schritt 1: Link in der Seite suchen
        dse_url = None
        for p in paths:
            if p in html_lower or p.replace("/", "") in html_lower:
                dse_url = urljoin(self._final_url or self.input_url, p)
                break

        # Auch explizite Links suchen
        if not dse_url:
            link_patterns = [
                r'href=["\']([^"\']*datenschutz[^"\']*)["\']',
                r'href=["\']([^"\']*privacy[^"\']*)["\']',
            ]
            for pattern in link_patterns:
                match = re.search(pattern, html_lower)
                if match:
                    found = match.group(1)
                    dse_url = urljoin(self._final_url or self.input_url, found)
                    break

        if not dse_url:
            # Trotzdem alle Pfade direkt testen
            base = self._final_url or self.input_url
            for p in paths:
                try:
                    test_url = urljoin(base, p)
                    r = self.session.get(test_url, timeout=8)
                    if r.status_code == 200 and len(r.text) > 800:
                        dse_url = test_url
                        break
                except Exception:
                    continue

        if not dse_url:
            self._add_check(CheckResult(
                key="privacy_policy", status="FAIL",
                title="Datenschutzerklaerung",
                detail="Keine Datenschutzerklaerung gefunden.",
                penalty=40,
                rechtsgrundlage="Art. 13/14 DSGVO",
                empfehlung="Datenschutzerklaerung erstellen und verlinken."
            ))
            return

        # Schritt 2: DSE abrufen und Pflichtinhalte pruefen
        try:
            r = self.session.get(dse_url, timeout=10)
            if r.status_code != 200 or len(r.text) < 800:
                self._add_check(CheckResult(
                    key="privacy_policy", status="FAIL",
                    title="Datenschutzerklaerung",
                    detail=f"Seite unter {dse_url} nicht abrufbar oder zu kurz.",
                    penalty=35,
                    rechtsgrundlage="Art. 13/14 DSGVO",
                    empfehlung="Datenschutzerklaerung muss mindestens alle Pflichtangaben enthalten."
                ))
                return

            dse_text = r.text.lower()
            found_terms = {}
            missing_terms = {}

            for category, keywords in DSE_PFLICHTBEGRIFFE.items():
                if any(kw in dse_text for kw in keywords):
                    found_terms[category] = True
                else:
                    missing_terms[category] = keywords[0]

            completeness = len(found_terms) / len(DSE_PFLICHTBEGRIFFE) * 100

            # DSE-Abdeckung speichern (fuer spaeter: Abgleich mit gefundenen Diensten)
            self.result.dse_coverage = {
                "url": dse_url,
                "found": list(found_terms.keys()),
                "missing": missing_terms,
                "completeness_pct": round(completeness),
                "text_length": len(dse_text),
            }

            if completeness >= 80:
                status = "PASS"
                penalty = 0
                detail = f"Datenschutzerklaerung vorhanden ({dse_url}). Vollstaendigkeit: {completeness:.0f}%."
            elif completeness >= 50:
                status = "WARNING"
                penalty = 15
                detail = f"Datenschutzerklaerung vorhanden, aber unvollstaendig ({completeness:.0f}%)."
            else:
                status = "FAIL"
                penalty = 30
                detail = f"Datenschutzerklaerung stark unvollstaendig ({completeness:.0f}%)."

            sub = []
            if missing_terms:
                sub.append("Fehlende Pflichtangaben: " + ", ".join(missing_terms.keys()))

            self._add_check(CheckResult(
                key="privacy_policy", status=status,
                title="Datenschutzerklaerung",
                detail=detail, penalty=penalty,
                sub_findings=sub,
                rechtsgrundlage="Art. 13/14 DSGVO",
                empfehlung="Fehlende Pflichtangaben ergaenzen." if missing_terms else ""
            ))

        except Exception as e:
            self._add_check(CheckResult(
                key="privacy_policy", status="WARNING",
                title="Datenschutzerklaerung",
                detail=f"DSE-Seite konnte nicht vollstaendig analysiert werden: {e}",
                penalty=20,
                rechtsgrundlage="Art. 13/14 DSGVO"
            ))

    def check_impressum(self):
        """Impressum: Existenz und Pflichtangaben nach DDG § 5."""
        paths = [
            "/impressum", "/imprint", "/impressum.html",
            "/about", "/kontakt", "/contact",
        ]

        html_lower = self._html_raw.lower() if self._html_raw else ""
        imp_url = None

        # Link in Seite suchen
        match = re.search(r'href=["\']([^"\']*impressum[^"\']*)["\']', html_lower)
        if match:
            imp_url = urljoin(self._final_url or self.input_url, match.group(1))

        if not imp_url:
            match = re.search(r'href=["\']([^"\']*imprint[^"\']*)["\']', html_lower)
            if match:
                imp_url = urljoin(self._final_url or self.input_url, match.group(1))

        if not imp_url:
            base = self._final_url or self.input_url
            for p in paths:
                try:
                    test_url = urljoin(base, p)
                    r = self.session.get(test_url, timeout=8)
                    if r.status_code == 200 and len(r.text) > 400:
                        # Pruefen ob es wirklich Impressum-Inhalt hat
                        if any(kw in r.text.lower() for kw in ["impressum", "imprint", "angaben gemäß", "angaben gemaess"]):
                            imp_url = test_url
                            break
                except Exception:
                    continue

        if not imp_url:
            self._add_check(CheckResult(
                key="impressum", status="FAIL",
                title="Impressum",
                detail="Kein Impressum gefunden.",
                penalty=35,
                rechtsgrundlage="DDG § 5 (ehemals TMG § 5)",
                empfehlung="Impressum mit allen Pflichtangaben erstellen. Haeufigster Abmahngrund in Deutschland."
            ))
            return

        try:
            r = self.session.get(imp_url, timeout=10)
            imp_text = r.text.lower()

            found = {}
            missing = {}

            for category, keywords in IMPRESSUM_PFLICHTBEGRIFFE.items():
                matched = False
                for kw in keywords:
                    if re.search(kw, imp_text):
                        matched = True
                        break
                if matched:
                    found[category] = True
                else:
                    missing[category] = keywords[0]

            completeness = len(found) / len(IMPRESSUM_PFLICHTBEGRIFFE) * 100

            if completeness >= 80:
                status, penalty = "PASS", 0
                detail = f"Impressum vorhanden ({imp_url}). Vollstaendigkeit: {completeness:.0f}%."
            elif completeness >= 50:
                status, penalty = "WARNING", 15
                detail = f"Impressum vorhanden, aber unvollstaendig ({completeness:.0f}%)."
            else:
                status, penalty = "FAIL", 25
                detail = f"Impressum stark unvollstaendig ({completeness:.0f}%)."

            sub = []
            if missing:
                sub.append("Fehlend: " + ", ".join(missing.keys()))

            self._add_check(CheckResult(
                key="impressum", status=status,
                title="Impressum", detail=detail,
                penalty=penalty, sub_findings=sub,
                rechtsgrundlage="DDG § 5",
                empfehlung="Fehlende Pflichtangaben ergaenzen." if missing else ""
            ))

        except Exception as e:
            self._add_check(CheckResult(
                key="impressum", status="WARNING",
                title="Impressum",
                detail=f"Impressum konnte nicht analysiert werden: {e}",
                penalty=15,
                rechtsgrundlage="DDG § 5"
            ))

    def check_consent_system(self):
        """Cookie-Consent: System vorhanden? Cookies vor Einwilligung?"""
        html_lower = self._html_raw.lower() if self._html_raw else ""

        # Consent-System erkennen (im gerenderten HTML + geladene Ressourcen)
        consent_found = None

        # Methode 1: Im HTML-Content
        consent_indicators = {
            "cookiebot":       "Cookiebot",
            "usercentrics":    "Usercentrics",
            "borlabs":         "Borlabs Cookie",
            "complianz":       "Complianz",
            "cookiefirst":     "CookieFirst",
            "onetrust":        "OneTrust",
            "cookieyes":       "CookieYes",
            "consentmanager":  "consentmanager",
            "klaro":           "Klaro!",
            "tarteaucitron":   "tarteaucitron",
            "cookie-notice":   "Cookie Notice",
            "gdpr-cookie":     "GDPR Cookie",
            "cookie-law-info": "Cookie Law Info",
            "real-cookie-banner": "Real Cookie Banner",
        }

        for key, name in consent_indicators.items():
            if key in html_lower:
                consent_found = name
                break

        # Methode 2: Geladene externe Domains (Playwright)
        if not consent_found:
            consent_domains = ["cookiebot.com", "usercentrics.eu", "cookiefirst.com",
                               "onetrust.com", "cookieyes.com", "consentmanager.net"]
            for domain in self._external_domains:
                for cd in consent_domains:
                    if cd in domain:
                        consent_found = KNOWN_TRACKERS.get(cd, {}).get("name", cd)
                        break
                if consent_found:
                    break

        self._consent_system = consent_found

        # Cookies vor Consent analysieren (nur mit Playwright)
        pre_consent_cookies = []
        essential_patterns = ["session", "csrf", "xsrf", "phpsessid", "jsessionid",
                              "asp.net", "__host-", "__secure-", "lang", "locale"]

        for cookie in self._cookies_raw:
            name_lower = cookie["name"].lower()
            is_essential = any(pat in name_lower for pat in essential_patterns)
            if not is_essential:
                pre_consent_cookies.append(cookie)

        self.result.cookies_before_consent = pre_consent_cookies

        # Bewertung
        if consent_found and len(pre_consent_cookies) == 0:
            self._add_check(CheckResult(
                key="consent", status="PASS",
                title="Cookie-Consent",
                detail=f"Consent-System erkannt: {consent_found}. Keine nicht-essentiellen Cookies vor Einwilligung.",
                rechtsgrundlage="Art. 6 Abs. 1 lit. a DSGVO, § 25 TDDDG"
            ))
        elif consent_found and len(pre_consent_cookies) > 0:
            cookie_names = ", ".join(c["name"] for c in pre_consent_cookies[:5])
            self._add_check(CheckResult(
                key="consent", status="WARNING",
                title="Cookie-Consent",
                detail=f"Consent-System erkannt ({consent_found}), aber {len(pre_consent_cookies)} "
                       f"nicht-essentielle Cookies werden VOR Einwilligung gesetzt.",
                penalty=25,
                sub_findings=[f"Cookies vor Consent: {cookie_names}"],
                rechtsgrundlage="Art. 6 Abs. 1 lit. a DSGVO, § 25 TDDDG",
                empfehlung="Consent-Tool so konfigurieren, dass keine Cookies vor Einwilligung gesetzt werden."
            ))
        elif not consent_found:
            # Gibt es ueberhaupt Cookies/Tracker?
            has_tracking = len(pre_consent_cookies) > 0 or self._has_trackers()
            if has_tracking:
                self._add_check(CheckResult(
                    key="consent", status="FAIL",
                    title="Cookie-Consent",
                    detail="Kein Consent-System erkannt, aber Cookies/Tracker vorhanden.",
                    penalty=35,
                    rechtsgrundlage="Art. 6 Abs. 1 lit. a DSGVO, § 25 TDDDG",
                    empfehlung="Cookie-Consent-Tool implementieren (z.B. Cookiebot, Usercentrics, Borlabs)."
                ))
            else:
                self._add_check(CheckResult(
                    key="consent", status="INFO",
                    title="Cookie-Consent",
                    detail="Kein Consent-System erkannt. Keine offensichtlichen Tracker gefunden.",
                    penalty=0,
                    empfehlung="Falls zukuenftig Tracking eingesetzt wird, Consent-Tool einrichten."
                ))

    def _has_trackers(self) -> bool:
        """Prueft ob Tracking-relevante Dienste gefunden wurden."""
        tracking_cats = {"analytics", "advertising", "social"}
        for domain in self._external_domains:
            for known_domain, info in KNOWN_TRACKERS.items():
                if known_domain in domain and info["category"] in tracking_cats:
                    return True
        return False

    def check_third_parties(self):
        """Drittanbieter-Ressourcen erkennen und klassifizieren."""
        found_services = {}

        # Methode 1: Externe Domains aus Playwright
        for domain in self._external_domains:
            for known_domain, info in KNOWN_TRACKERS.items():
                if known_domain in domain:
                    service_key = info["name"]
                    if service_key not in found_services:
                        found_services[service_key] = {
                            **info,
                            "domain": domain,
                        }

        # Methode 2: HTML-Pattern (Fallback fuer requests-Modus)
        if not self._external_domains:
            html_lower = self._html_raw.lower() if self._html_raw else ""
            # URLs extrahieren
            url_pattern = r'(?:src|href|data-src)\s*=\s*["\']?(https?://[^"\'>\s]+)'
            found_urls = re.findall(url_pattern, html_lower)

            site_domain = urlparse(self._final_url or self.input_url).hostname or ""

            for url in found_urls:
                try:
                    parsed = urlparse(url)
                    ext_domain = parsed.hostname
                    if ext_domain and ext_domain != site_domain and not ext_domain.endswith(f".{site_domain}"):
                        self._external_domains.add(ext_domain)
                        for known_domain, info in KNOWN_TRACKERS.items():
                            if known_domain in ext_domain:
                                service_key = info["name"]
                                if service_key not in found_services:
                                    found_services[service_key] = {**info, "domain": ext_domain}
                except Exception:
                    pass

        self.result.third_parties = list(found_services.values())

        # Bewertung
        high_risk = [s for s in found_services.values() if s["risk"] == "hoch"]
        medium_risk = [s for s in found_services.values() if s["risk"] == "mittel"]
        consent_tools = [s for s in found_services.values() if s["category"] == "consent"]

        # Google Fonts spezifisch (Abmahnwelle)
        google_fonts = any("Google Fonts" in s["name"] for s in found_services.values())

        total_ext = len(found_services) - len(consent_tools)

        if total_ext == 0:
            self._add_check(CheckResult(
                key="third_parties", status="PASS",
                title="Drittanbieter-Dienste",
                detail="Keine externen Drittanbieter-Dienste erkannt.",
                rechtsgrundlage="Art. 44ff. DSGVO (Drittlandtransfer)"
            ))
        else:
            penalty = len(high_risk) * 8 + len(medium_risk) * 3
            if google_fonts:
                penalty += 10  # Abmahnrisiko

            sub = []
            for s in found_services.values():
                if s["category"] != "consent":
                    sub.append(f"{s['name']} ({s['category']}, {s['country']}, Risiko: {s['risk']})")

            if high_risk:
                status = "FAIL" if len(high_risk) >= 3 else "WARNING"
            else:
                status = "WARNING" if medium_risk else "PASS"

            detail = f"{total_ext} externe Dienste erkannt, davon {len(high_risk)} mit hohem Risiko."
            if google_fonts:
                detail += " ACHTUNG: Google Fonts extern geladen (Abmahnrisiko)."

            self._add_check(CheckResult(
                key="third_parties", status=status,
                title="Drittanbieter-Dienste",
                detail=detail,
                penalty=min(penalty, 40),
                sub_findings=sub,
                rechtsgrundlage="Art. 44ff. DSGVO, Schrems II",
                empfehlung="Google Fonts lokal einbinden. Fuer US-Dienste AVV und SCCs pruefen."
                if high_risk else ""
            ))

    def check_tracking(self):
        """Tracking-Dienste erkennen (aus Drittanbieter-Analyse)."""
        tracking = [s for s in self.result.third_parties
                    if s["category"] in ("analytics", "advertising")]

        if not tracking:
            self._add_check(CheckResult(
                key="tracking", status="PASS",
                title="Tracking & Analytics",
                detail="Keine Tracking- oder Werbe-Dienste erkannt.",
            ))
            return

        # Pruefen ob in DSE erwaehnt
        dse_text = ""
        if self.result.dse_coverage.get("url"):
            try:
                r = self.session.get(self.result.dse_coverage["url"], timeout=8)
                dse_text = r.text.lower()
            except Exception:
                pass

        not_in_dse = []
        for t in tracking:
            name_lower = t["name"].lower().replace(" ", "")
            # Vereinfachte Pruefung
            search_terms = [t["name"].lower(), name_lower, t["domain"].split(".")[0]]
            if not any(term in dse_text for term in search_terms):
                not_in_dse.append(t["name"])

        sub = [f"{t['name']} ({t['country']})" for t in tracking]

        penalty = len(tracking) * 5
        if not_in_dse:
            penalty += len(not_in_dse) * 8
            sub.append(f"NICHT in Datenschutzerklaerung erwaehnt: {', '.join(not_in_dse)}")

        self._add_check(CheckResult(
            key="tracking", status="WARNING" if not not_in_dse else "FAIL",
            title="Tracking & Analytics",
            detail=f"{len(tracking)} Tracking-Dienste erkannt.",
            penalty=min(penalty, 35),
            sub_findings=sub,
            rechtsgrundlage="Art. 6 Abs. 1 lit. a DSGVO, § 25 TDDDG",
            empfehlung="Alle Tracking-Dienste muessen in der Datenschutzerklaerung aufgefuehrt "
                       "und per Consent-Tool einwilligungspflichtig sein."
        ))

    def check_security_headers(self):
        """HTTP Security Headers analysieren."""
        if not self._response_headers:
            self._add_check(CheckResult(
                key="security_headers", status="SKIPPED",
                title="Security Headers",
                detail="Keine Response-Headers verfuegbar.",
            ))
            return

        found = []
        missing = []
        missing_critical = []

        for header, info in SECURITY_HEADERS.items():
            if header in self._response_headers:
                found.append(info["name"])
            else:
                missing.append(info["name"])
                if info["critical"]:
                    missing_critical.append(info["name"])

        score_pct = len(found) / len(SECURITY_HEADERS) * 100

        if score_pct >= 80:
            status, penalty = "PASS", 0
            detail = f"Security Headers gut konfiguriert ({score_pct:.0f}%). {len(found)}/{len(SECURITY_HEADERS)} vorhanden."
        elif score_pct >= 50:
            status, penalty = "WARNING", 10
            detail = f"Security Headers teilweise vorhanden ({score_pct:.0f}%)."
        else:
            status, penalty = "FAIL", 20
            detail = f"Security Headers mangelhaft ({score_pct:.0f}%)."

        sub = []
        if missing:
            sub.append(f"Fehlend: {', '.join(missing)}")
        if missing_critical:
            sub.append(f"Kritisch fehlend: {', '.join(missing_critical)}")

        self._add_check(CheckResult(
            key="security_headers", status=status,
            title="Security Headers", detail=detail,
            penalty=penalty, sub_findings=sub,
            rechtsgrundlage="Art. 32 DSGVO (technische Massnahmen)",
            empfehlung="Fehlende Security Headers im Webserver konfigurieren." if missing else ""
        ))

    def check_dse_vs_services(self):
        """Abgleich: Werden alle gefundenen Dienste in der DSE erwaehnt?"""
        if not self.result.third_parties or not self.result.dse_coverage.get("url"):
            return

        dse_text = ""
        try:
            r = self.session.get(self.result.dse_coverage["url"], timeout=8)
            dse_text = r.text.lower()
        except Exception:
            return

        not_covered = []
        covered = []

        for service in self.result.third_parties:
            if service["category"] == "consent":
                continue

            name_lower = service["name"].lower()
            domain_base = service["domain"].split(".")[0] if "domain" in service else ""

            search_terms = [name_lower, domain_base]
            # Spezialfaelle
            if "google" in name_lower:
                search_terms.append("google")
            if "meta" in name_lower or "facebook" in name_lower:
                search_terms.extend(["meta", "facebook"])

            if any(term in dse_text for term in search_terms if term):
                covered.append(service["name"])
            else:
                not_covered.append(service["name"])

        if not not_covered:
            if covered:
                self._add_check(CheckResult(
                    key="dse_coverage", status="PASS",
                    title="DSE-Abdeckung",
                    detail=f"Alle {len(covered)} erkannten Dienste werden in der Datenschutzerklaerung erwaehnt.",
                    rechtsgrundlage="Art. 13 Abs. 1 lit. d/e DSGVO"
                ))
        else:
            self._add_check(CheckResult(
                key="dse_coverage", status="FAIL",
                title="DSE-Abdeckung",
                detail=f"{len(not_covered)} Dienste werden auf der Website verwendet, "
                       f"aber NICHT in der Datenschutzerklaerung erwaehnt.",
                penalty=min(len(not_covered) * 10, 30),
                sub_findings=[f"Nicht erwaehnt: {', '.join(not_covered)}"],
                rechtsgrundlage="Art. 13 Abs. 1 lit. d/e DSGVO",
                empfehlung="Alle eingesetzten Dienste muessen in der DSE mit Zweck, "
                           "Rechtsgrundlage und ggf. Drittlandtransfer aufgefuehrt werden."
            ))

    def check_forms(self):
        """Formulare auf der Seite: Verschluesselung und Hinweise."""
        html = self._html_raw or ""

        forms = re.findall(r'<form[^>]*>(.*?)</form>', html, re.DOTALL | re.IGNORECASE)

        if not forms:
            return  # Keine Formulare, kein Check noetig

        issues = []

        for i, form_html in enumerate(forms):
            form_lower = form_html.lower()

            # Input-Felder mit personenbezogenen Daten?
            personal_fields = re.findall(
                r'(?:type|name|id|placeholder)\s*=\s*["\']?'
                r'(email|phone|tel|name|vorname|nachname|address|adresse|message|nachricht|password)',
                form_lower
            )

            if personal_fields:
                # Pruefe ob action HTTPS ist
                action_match = re.search(r'action\s*=\s*["\']?(https?://[^"\'>\s]+)', form_html, re.IGNORECASE)
                if action_match and action_match.group(1).startswith("http://"):
                    issues.append(f"Formular {i+1}: Action-URL ohne HTTPS")

                # Pruefe ob Datenschutz-Hinweis beim Formular
                has_dse_link = any(kw in form_lower for kw in ["datenschutz", "privacy", "einwillig", "consent"])
                if not has_dse_link:
                    issues.append(f"Formular {i+1} mit personenbezogenen Feldern ({', '.join(set(personal_fields))}): "
                                  f"kein Datenschutzhinweis erkennbar")

        if issues:
            self._add_check(CheckResult(
                key="forms", status="WARNING",
                title="Kontaktformulare",
                detail=f"{len(forms)} Formular(e) gefunden, {len(issues)} Auffaelligkeit(en).",
                penalty=min(len(issues) * 8, 20),
                sub_findings=issues,
                rechtsgrundlage="Art. 13 DSGVO, Art. 32 DSGVO",
                empfehlung="Bei jedem Formular mit personenbezogenen Daten: "
                           "Datenschutzhinweis und Link zur DSE direkt am Formular anbringen."
            ))
        else:
            self._add_check(CheckResult(
                key="forms", status="PASS",
                title="Kontaktformulare",
                detail=f"{len(forms)} Formular(e) gefunden, keine Auffaelligkeiten.",
            ))

    # =========================================================================
    # AGGREGATION
    # =========================================================================

    def _add_check(self, check: CheckResult):
        self.result.checks.append(check)
        self.result.risk_score += check.penalty

    def finalize(self):
        """Score begrenzen, Risk-Level setzen, Summary bauen."""
        # Score cap NACH allen Checks
        self.result.risk_score = min(self.result.risk_score, 100)
        self.result.final_url = self._final_url or self.input_url

        if self.result.risk_score >= 70:
            self.result.risk_level = "HOCH"
        elif self.result.risk_score >= 40:
            self.result.risk_level = "MITTEL"
        elif self.result.risk_score >= 15:
            self.result.risk_level = "NIEDRIG"
        else:
            self.result.risk_level = "SEHR NIEDRIG"

        # Counts
        fails = sum(1 for c in self.result.checks if c.status == "FAIL")
        warnings = sum(1 for c in self.result.checks if c.status == "WARNING")
        passes = sum(1 for c in self.result.checks if c.status == "PASS")

        # Summary
        if self.result.risk_level == "HOCH":
            verdict = "Erhebliche DSGVO-Risiken. Sofortiger Handlungsbedarf."
        elif self.result.risk_level == "MITTEL":
            verdict = "Erhoehtes Risiko. Massnahmen empfohlen."
        elif self.result.risk_level == "NIEDRIG":
            verdict = "Grundanforderungen weitgehend erfuellt. Optimierungspotenzial vorhanden."
        else:
            verdict = "Guter Compliance-Stand. Geringes Risiko."

        # Top-Empfehlungen (sortiert nach Penalty)
        sorted_checks = sorted(
            [c for c in self.result.checks if c.penalty > 0],
            key=lambda c: c.penalty, reverse=True
        )
        top_recommendations = []
        for c in sorted_checks[:5]:
            if c.empfehlung:
                top_recommendations.append({
                    "bereich": c.title,
                    "prioritaet": "HOCH" if c.penalty >= 25 else "MITTEL" if c.penalty >= 10 else "NIEDRIG",
                    "massnahme": c.empfehlung,
                })

        self.result.summary = {
            "verdict": verdict,
            "risk_level": self.result.risk_level,
            "risk_score": self.result.risk_score,
            "checks_total": len(self.result.checks),
            "checks_pass": passes,
            "checks_warning": warnings,
            "checks_fail": fails,
            "top_recommendations": top_recommendations,
            "third_party_count": len(self.result.third_parties),
            "cookies_before_consent": len(self.result.cookies_before_consent),
        }

    # =========================================================================
    # RUN
    # =========================================================================

    def scan(self) -> ScanResult:
        """Hauptmethode: Alle Checks ausfuehren."""

        # Fetch
        if self.use_playwright:
            success = self._fetch_playwright()
        else:
            success = self._fetch_requests()

        if not success:
            self.finalize()
            return self.result

        # Alle Checks
        self.check_https_and_redirect()
        self.check_ssl_certificate()
        self.check_privacy_policy()
        self.check_impressum()
        self.check_consent_system()
        self.check_third_parties()
        self.check_tracking()
        self.check_security_headers()
        self.check_dse_vs_services()
        self.check_forms()

        self.finalize()
        return self.result

    # =========================================================================
    # CLI OUTPUT
    # =========================================================================

    def print_report(self):
        """Terminal-Ausgabe (fuer Entwicklung/Debug)."""
        r = self.result
        print()
        print("=" * 60)
        print("  DSF DSGVO COMPLIANCE SCAN")
        print("=" * 60)
        print(f"  URL:        {r.final_url or r.url}")
        print(f"  Datum:      {r.scan_date}")
        print(f"  Scan-ID:    {r.scan_id}")
        print(f"  Renderer:   {r.meta.get('renderer', 'n/a')}")
        print(f"  Risiko:     {r.risk_level} ({r.risk_score}/100)")
        print("-" * 60)

        if r.summary:
            print(f"\n  {r.summary['verdict']}")
            print(f"  Checks: {r.summary['checks_pass']} OK / "
                  f"{r.summary['checks_warning']} Warnung / "
                  f"{r.summary['checks_fail']} Fehler")

        print("\n" + "-" * 60)
        print("  DETAILS")
        print("-" * 60)

        status_symbol = {"PASS": "[OK]", "WARNING": "[!!]", "FAIL": "[XX]", "INFO": "[ii]", "SKIPPED": "[--]"}

        for c in r.checks:
            sym = status_symbol.get(c.status, "[??]")
            print(f"\n  {sym} {c.title}")
            print(f"      {c.detail}")
            if c.rechtsgrundlage:
                print(f"      Rechtsgrundlage: {c.rechtsgrundlage}")
            if c.empfehlung:
                print(f"      Empfehlung: {c.empfehlung}")
            for sf in c.sub_findings:
                print(f"      - {sf}")

        if r.third_parties:
            print("\n" + "-" * 60)
            print("  ERKANNTE DRITTANBIETER")
            print("-" * 60)
            for tp in r.third_parties:
                if tp["category"] != "consent":
                    print(f"  - {tp['name']} ({tp['category']}, {tp['country']}, Risiko: {tp['risk']})")

        if r.cookies_before_consent:
            print("\n" + "-" * 60)
            print("  COOKIES VOR EINWILLIGUNG")
            print("-" * 60)
            for cookie in r.cookies_before_consent:
                print(f"  - {cookie['name']} (Domain: {cookie['domain']})")

        print("\n" + "=" * 60)
        print(f"  (c) DSF Consulting | Engine: {r.meta.get('engine', 'DSF-PRO-CORE')}")
        print("=" * 60)
        print()

    def to_dict(self) -> dict:
        """Komplettes Ergebnis als Dictionary (fuer JSON/PDF)."""
        return {
            "url": self.result.url,
            "final_url": self.result.final_url,
            "scan_date": self.result.scan_date,
            "scan_id": self.result.scan_id,
            "risk_score": self.result.risk_score,
            "risk_level": self.result.risk_level,
            "summary": self.result.summary,
            "checks": [
                {
                    "key": c.key,
                    "status": c.status,
                    "title": c.title,
                    "detail": c.detail,
                    "penalty": c.penalty,
                    "rechtsgrundlage": c.rechtsgrundlage,
                    "empfehlung": c.empfehlung,
                    "sub_findings": c.sub_findings,
                }
                for c in self.result.checks
            ],
            "third_parties": self.result.third_parties,
            "cookies_before_consent": self.result.cookies_before_consent,
            "dse_coverage": self.result.dse_coverage,
            "meta": self.result.meta,
        }

    def to_json(self, filepath: Optional[str] = None) -> str:
        """JSON-Export."""
        data = self.to_dict()
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)
        return json_str
