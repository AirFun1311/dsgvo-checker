#!/usr/bin/env python3
"""
DSGVO-Checker - PDF-Bericht (klares, ruhiges Design)
====================================================
(c) 2026 DSF Consulting
"""

from urllib.parse import quote
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable,
)

CONTACT = "sf.foodzeit@googlemail.com"

# ── Farben: ruhig, monochrom + gedeckte Status-Toene ───────────────────────
INK      = colors.HexColor("#14161a")   # fast schwarz
MUTED    = colors.HexColor("#6b7280")   # grau fuer Nebeninfos
HAIRLINE = colors.HexColor("#e5e7eb")   # feine Linien
SOFT_BG  = colors.HexColor("#f7f8fa")   # sehr helles Grau fuer Flaechen
WHITE    = colors.white

C_OK    = colors.HexColor("#1a7f4b")    # gedecktes gruen
C_WARN  = colors.HexColor("#b45309")    # gedecktes bernstein
C_FAIL  = colors.HexColor("#b3261e")    # ruhiges rot
C_INFO  = colors.HexColor("#6b7280")    # neutral

RISK_COLOR = {
    "HOCH":         C_FAIL,
    "MITTEL":       C_WARN,
    "NIEDRIG":      C_OK,
    "SEHR NIEDRIG": C_OK,
    "UNBEKANNT":    MUTED,
}
STATUS_COLOR = {"PASS": C_OK, "WARNING": C_WARN, "FAIL": C_FAIL, "INFO": C_INFO, "SKIPPED": MUTED}
STATUS_LABEL = {"PASS": "OK", "WARNING": "Hinweis", "FAIL": "Handlungsbedarf", "INFO": "Info", "SKIPPED": "-"}

# ── Anleitungen fuer den bezahlten Bericht: pro Pruefpunkt, konkret ─────────
REMEDIATION = {
    "privacy_policy": {
        "titel": "Datenschutzerklaerung vervollstaendigen",
        "schritte": [
            "Erstellen Sie eine vollstaendige Datenschutzerklaerung. Seriose, kostenlose Generatoren: e-recht24.de oder datenschutz-generator.de. Beantworten Sie die Fragen zu Ihrer Website ehrlich.",
            "Stellen Sie sicher, dass diese Pflichtangaben enthalten sind: Name und Kontakt des Verantwortlichen, Zweck und Rechtsgrundlage, Speicherdauer, Ihre Rechte (Auskunft, Loeschung, Widerspruch), zustaendige Aufsichtsbehoerde und alle eingesetzten Dienste (z. B. Google, Meta) samt Uebermittlung in die USA.",
            "Veroeffentlichen Sie die Erklaerung als eigene Seite und verlinken Sie sie im Fussbereich JEDER Seite.",
        ],
        "tipp": "WordPress: Seite „Datenschutz“ anlegen, Text einfuegen, im Footer-Widget verlinken.",
        "fertig": "Die Seite ihre-domain.de/datenschutz existiert und enthaelt alle genannten Punkte.",
    },
    "third_parties": {
        "titel": "Externe Dienste entschaerfen (Google Fonts & Co.)",
        "schritte": [
            "Google Fonts lokal einbinden: Schrift bei gwfh.mranftl.com herunterladen, Dateien auf Ihren Server legen, per @font-face einbinden und den Verweis auf fonts.googleapis.com entfernen.",
            "Fuer jeden US-Dienst (Google, Meta, LinkedIn) pruefen, ob Sie ihn wirklich brauchen. Wenn ja: Auftragsverarbeitungsvertrag (AVV) abschliessen und die Uebermittlung auf die EU-Standardvertragsklauseln (SCC) stuetzen.",
            "Diese Dienste erst NACH Einwilligung des Besuchers laden (siehe naechster Punkt).",
        ],
        "tipp": "WordPress: Das Plugin „OMGF“ bindet Google Fonts automatisch lokal ein.",
        "fertig": "Im Browser mit F12 → Netzwerk erscheint beim Neuladen keine Anfrage mehr an fonts.googleapis.com.",
    },
    "tracking": {
        "titel": "Tracking nur mit Einwilligung",
        "schritte": [
            "Ein Einwilligungs-Tool (Consent-Banner) installieren: z. B. Borlabs Cookie, Complianz, Cookiebot oder Usercentrics.",
            "So einstellen, dass ALLE nicht-notwendigen Dienste (Google Ads, Meta Pixel, LinkedIn) erst laden, wenn der Besucher aktiv zustimmt. Vorangekreuzte Haekchen sind nicht erlaubt.",
            "Jeden Dienst in die Datenschutzerklaerung eintragen – mit Zweck, Rechtsgrundlage (Einwilligung, Art. 6 Abs. 1 lit. a) und Hinweis auf die USA-Uebermittlung.",
        ],
        "tipp": "Testen Sie im privaten Browserfenster: Vor dem Klick auf „Zustimmen“ darf kein Tracker laden.",
        "fertig": "Ohne Einwilligung werden keine Tracker geladen, und alle Dienste stehen in der Datenschutzerklaerung.",
    },
    "consent": {
        "titel": "Cookie-Einwilligung einrichten",
        "schritte": [
            "Ein Consent-Tool installieren (Borlabs, Complianz, Cookiebot, Usercentrics).",
            "So konfigurieren, dass nicht-notwendige Cookies erst nach aktiver Zustimmung gesetzt werden.",
        ],
        "tipp": "Das Banner sollte gleichwertige Buttons „Zustimmen“ und „Ablehnen“ haben.",
        "fertig": "Vor der Zustimmung werden keine nicht-notwendigen Cookies gesetzt.",
    },
    "security_headers": {
        "titel": "Sicherheits-Header ergaenzen",
        "schritte": [
            "Die fehlenden Header in der Server-Konfiguration ergaenzen. Wichtig: Content-Security-Policy, Referrer-Policy (Empfehlung: strict-origin-when-cross-origin), Permissions-Policy.",
            "Apache: in die .htaccess eintragen. nginx: per add_header im server-Block. Im Zweifel Ihren Hoster fragen.",
        ],
        "tipp": "WordPress: Plugins wie „Really Simple Security“ setzen viele Header automatisch.",
        "fertig": "Auf securityheaders.com erreicht Ihre Seite mindestens Note B.",
    },
    "forms": {
        "titel": "Formulare mit Datenschutzhinweis versehen",
        "schritte": [
            "Bei jedem Formular mit personenbezogenen Feldern (Name, E-Mail) einen kurzen Datenschutzhinweis direkt darunter einfuegen – mit Link zur Datenschutzerklaerung.",
            "Formulierung z. B.: „Mit dem Absenden stimmen Sie der Verarbeitung Ihrer Daten gemaess unserer Datenschutzerklaerung zu.“",
        ],
        "tipp": "Empfehlenswert ist zusaetzlich eine Pflicht-Checkbox zur Einwilligung.",
        "fertig": "Jedes Formular zeigt sichtbar einen Datenschutzhinweis mit Link.",
    },
    "impressum": {
        "titel": "Impressum vervollstaendigen",
        "schritte": [
            "Fehlende Pflichtangaben ergaenzen. Haeufig fehlt die Vertretung (Geschaeftsfuehrer / Inhaber).",
            "Ein vollstaendiges Impressum enthaelt: Name/Firma, ladungsfaehige Anschrift, Kontakt (Telefon + E-Mail), ggf. Handelsregister + Nummer, ggf. USt-IdNr., Vertretungsberechtigte.",
        ],
        "tipp": "Kostenloser Impressum-Generator: e-recht24.de.",
        "fertig": "ihre-domain.de/impressum enthaelt alle Pflichtangaben.",
    },
    "https": {
        "titel": "HTTPS erzwingen",
        "schritte": [
            "Kostenloses SSL-Zertifikat (Let's Encrypt) bei Ihrem Hoster aktivieren – meist ein Klick im Hosting-Panel.",
            "Alle Aufrufe von http auf https umleiten (Hoster-Einstellung oder .htaccess).",
        ],
        "tipp": "WordPress: Plugin „Really Simple SSL“ stellt automatisch um.",
        "fertig": "Ihre Seite ist nur noch ueber https erreichbar (Schloss-Symbol im Browser).",
    },
    "ssl": {
        "titel": "Verschluesselung aktuell halten",
        "schritte": [
            "Beim Hoster pruefen, dass TLS 1.2/1.3 aktiv und TLS 1.0/1.1 abgeschaltet sind.",
            "Automatische Zertifikatsverlaengerung sicherstellen (bei Let's Encrypt Standard).",
        ],
        "tipp": "Testen Sie Ihre Seite auf ssllabs.com/ssltest – Ziel ist Note A.",
        "fertig": "Das Zertifikat ist gueltig und die Verbindung nutzt TLS 1.2 oder 1.3.",
    },
}


def get_styles():
    base = getSampleStyleSheet()
    return {
        "kicker": ParagraphStyle("kicker", parent=base["Normal"], fontName="Helvetica-Bold",
                                 fontSize=9, textColor=MUTED, spaceAfter=2, leading=12),
        "title": ParagraphStyle("title", parent=base["Title"], fontName="Helvetica-Bold",
                                fontSize=26, textColor=INK, spaceAfter=4, leading=30, alignment=TA_LEFT),
        "sub": ParagraphStyle("sub", parent=base["Normal"], fontName="Helvetica",
                              fontSize=11, textColor=MUTED, spaceAfter=10, leading=15),
        "h": ParagraphStyle("h", parent=base["Heading1"], fontName="Helvetica-Bold",
                            fontSize=13, textColor=INK, spaceBefore=16, spaceAfter=8, leading=16),
        "body": ParagraphStyle("body", parent=base["Normal"], fontName="Helvetica",
                               fontSize=9.5, textColor=INK, leading=14, spaceAfter=5, alignment=TA_LEFT),
        "small": ParagraphStyle("small", parent=base["Normal"], fontName="Helvetica",
                                fontSize=8, textColor=MUTED, leading=11, spaceAfter=3),
        "cell": ParagraphStyle("cell", parent=base["Normal"], fontName="Helvetica",
                               fontSize=9, textColor=INK, leading=12),
        "cellmuted": ParagraphStyle("cellmuted", parent=base["Normal"], fontName="Helvetica",
                                    fontSize=9, textColor=MUTED, leading=12),
        "checkname": ParagraphStyle("checkname", parent=base["Normal"], fontName="Helvetica-Bold",
                                    fontSize=10.5, textColor=INK, leading=14, spaceBefore=8, spaceAfter=1),
    }


class _Page:
    def __init__(self, scan_id, scan_date):
        self.scan_id = scan_id
        self.scan_date = scan_date

    def __call__(self, c, doc):
        c.saveState()
        w, h = A4
        # dezente Kopfzeile ab Seite 2
        if doc.page > 1:
            c.setFont("Helvetica", 7.5)
            c.setFillColor(MUTED)
            c.drawString(20*mm, h - 12*mm, "DSGVO-Bericht")
            c.drawRightString(w - 20*mm, h - 12*mm, f"{self.scan_id}")
            c.setStrokeColor(HAIRLINE); c.setLineWidth(0.5)
            c.line(20*mm, h - 14*mm, w - 20*mm, h - 14*mm)
        # Fusszeile
        c.setStrokeColor(HAIRLINE); c.setLineWidth(0.5)
        c.line(20*mm, 14*mm, w - 20*mm, 14*mm)
        c.setFont("Helvetica", 7.5); c.setFillColor(MUTED)
        c.drawString(20*mm, 10*mm, "DSF Consulting  ·  vertraulich")
        c.drawRightString(w - 20*mm, 10*mm, f"Seite {doc.page}")
        c.restoreState()


class DSGVOReportPDF:
    def __init__(self, scan_data: dict):
        self.data = scan_data
        self.s = get_styles()
        self.el = []

    def build(self, filepath: str, full: bool = False):
        doc = SimpleDocTemplate(filepath, pagesize=A4,
                                topMargin=20*mm, bottomMargin=20*mm,
                                leftMargin=20*mm, rightMargin=20*mm)
        tmpl = _Page(self.data.get("scan_id", ""), self.data.get("scan_date", ""))
        self._cover()
        self._summary()
        self._details()
        self._third_parties()
        self._recommendations()
        if full:
            # Bezahlte Vollversion: konkrete Schritt-fuer-Schritt-Anleitung
            self._remediation_guide()
            self._upsell()
        else:
            # Kostenlose Version: Verweis auf Anleitung / Umsetzung
            self._call_to_action()
        self._notes()
        doc.build(self.el, onFirstPage=tmpl, onLaterPages=tmpl)

    # ── Deckblatt: hell, klar, lesbar ──────────────────────────────────────
    def _cover(self):
        s = self.s
        d = self.data
        risk = d.get("risk_level", "UNBEKANNT")
        score = d.get("risk_score", 0)
        rc = RISK_COLOR.get(risk, MUTED)

        self.el.append(Spacer(1, 24*mm))
        self.el.append(Paragraph("DSGVO-PRUEFUNG", s["kicker"]))
        self.el.append(Paragraph("Ihr Datenschutz-Bericht", s["title"]))
        self.el.append(Paragraph(d.get("final_url", d.get("url", "")), s["sub"]))
        self.el.append(HRFlowable(width="100%", thickness=0.7, color=HAIRLINE, spaceAfter=10*mm))

        # Risiko-Zeile: farbiger Balken links, Text dunkel auf hell
        risk_label = Paragraph(f'<font color="{rc.hexval()}"><b>RISIKO&nbsp;&nbsp;{risk}</b></font>',
                               ParagraphStyle("r", parent=s["body"], fontSize=15, leading=18))
        score_txt = Paragraph(f'<font color="{MUTED.hexval()}">Bewertung {score}/100</font>',
                              ParagraphStyle("rs", parent=s["body"], fontSize=11, leading=18))
        verdict = d.get("summary", {}).get("verdict", "")
        risk_box = Table([[risk_label, score_txt], [Paragraph(verdict, s["body"]), ""]],
                         colWidths=[110*mm, 50*mm])
        risk_box.setStyle(TableStyle([
            ("SPAN", (0, 1), (1, 1)),
            ("BACKGROUND", (0, 0), (-1, -1), SOFT_BG),
            ("LINEBEFORE", (0, 0), (0, -1), 3, rc),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ]))
        self.el.append(risk_box)
        self.el.append(Spacer(1, 14*mm))

        # Meta unten, dezent
        meta = [
            [Paragraph("Geprueft am", s["small"]), Paragraph(d.get("scan_date", ""), s["cell"])],
            [Paragraph("Bericht-Nr.", s["small"]), Paragraph(d.get("scan_id", ""), s["cell"])],
        ]
        mt = Table(meta, colWidths=[30*mm, 130*mm])
        mt.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        self.el.append(mt)
        self.el.append(PageBreak())

    # ── Ueberblick ─────────────────────────────────────────────────────────
    def _summary(self):
        s = self.s
        sm = self.data.get("summary", {})
        self.el.append(Paragraph("Ueberblick", s["h"]))

        stats = [
            ("Geprueft", sm.get("checks_total", 0), INK),
            ("In Ordnung", sm.get("checks_pass", 0), C_OK),
            ("Hinweise", sm.get("checks_warning", 0), C_WARN),
            ("Handlungsbedarf", sm.get("checks_fail", 0), C_FAIL),
            ("Drittanbieter", sm.get("third_party_count", 0), INK),
        ]
        row_num, row_lbl = [], []
        for lbl, val, col in stats:
            row_num.append(Paragraph(f'<font color="{col.hexval()}"><b>{val}</b></font>',
                                     ParagraphStyle("n", parent=s["body"], fontSize=20, leading=22)))
            row_lbl.append(Paragraph(f'<font color="{MUTED.hexval()}">{lbl}</font>',
                                     ParagraphStyle("l", parent=s["small"], fontSize=8)))
        st = Table([row_num, row_lbl], colWidths=[34*mm]*5)
        st.setStyle(TableStyle([
            ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
            ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
        ]))
        self.el.append(st)
        self.el.append(HRFlowable(width="100%", thickness=0.7, color=HAIRLINE, spaceBefore=4, spaceAfter=8))

        # Kurzliste je Pruefbereich
        for c in self.data.get("checks", []):
            col = STATUS_COLOR.get(c.get("status", "SKIPPED"), MUTED)
            lbl = STATUS_LABEL.get(c.get("status", "SKIPPED"), "-")
            name = Paragraph(c.get("title", ""), s["cell"])
            status = Paragraph(f'<font color="{col.hexval()}"><b>{lbl}</b></font>', s["cell"])
            row = Table([[status, name]], colWidths=[34*mm, 126*mm])
            row.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LINEBELOW", (0, 0), (-1, -1), 0.4, HAIRLINE),
            ]))
            self.el.append(row)

    # ── Details ────────────────────────────────────────────────────────────
    def _details(self):
        s = self.s
        self.el.append(Paragraph("Ergebnisse im Detail", s["h"]))
        for c in self.data.get("checks", []):
            col = STATUS_COLOR.get(c.get("status", "SKIPPED"), MUTED)
            lbl = STATUS_LABEL.get(c.get("status", "SKIPPED"), "-")
            self.el.append(Paragraph(
                f'<font color="{col.hexval()}"><b>{lbl}</b></font>&nbsp;&nbsp;{c.get("title","")}',
                s["checkname"]))
            self.el.append(Paragraph(c.get("detail", ""), s["body"]))
            for sf in c.get("sub_findings", []):
                self.el.append(Paragraph(f'<font color="{MUTED.hexval()}">–</font>&nbsp;{sf}', s["small"]))
            if c.get("empfehlung"):
                self.el.append(Paragraph(
                    f'<font color="{MUTED.hexval()}"><b>Empfehlung:</b> {c["empfehlung"]}</font>', s["small"]))
            if c.get("rechtsgrundlage"):
                self.el.append(Paragraph(
                    f'<font color="{MUTED.hexval()}">{c["rechtsgrundlage"]}</font>', s["small"]))
            self.el.append(Spacer(1, 2*mm))

    # ── Drittanbieter ──────────────────────────────────────────────────────
    def _third_parties(self):
        s = self.s
        tp = [t for t in self.data.get("third_parties", []) if t.get("category") != "consent"]
        if not tp:
            return
        self.el.append(Paragraph("Erkannte Drittanbieter", s["h"]))
        data = [[Paragraph("Dienst", s["cellmuted"]), Paragraph("Zweck", s["cellmuted"]),
                 Paragraph("Land", s["cellmuted"]), Paragraph("Risiko", s["cellmuted"])]]
        rcmap = {"hoch": C_FAIL, "mittel": C_WARN, "niedrig": C_OK}
        for t in tp:
            rc = rcmap.get(t.get("risk", ""), MUTED)
            data.append([
                Paragraph(t.get("name", ""), s["cell"]),
                Paragraph(t.get("category", ""), s["cell"]),
                Paragraph(t.get("country", ""), s["cell"]),
                Paragraph(f'<font color="{rc.hexval()}">{t.get("risk","")}</font>', s["cell"]),
            ])
        tbl = Table(data, colWidths=[55*mm, 45*mm, 25*mm, 35*mm])
        tbl.setStyle(TableStyle([
            ("LINEBELOW", (0, 0), (-1, 0), 0.6, INK),
            ("LINEBELOW", (0, 1), (-1, -1), 0.4, HAIRLINE),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        self.el.append(tbl)

    # ── Empfehlungen ───────────────────────────────────────────────────────
    def _recommendations(self):
        s = self.s
        recs = self.data.get("summary", {}).get("top_recommendations", [])
        if not recs:
            return
        self.el.append(Paragraph("Was zu tun ist", s["h"]))
        pc = {"HOCH": C_FAIL, "MITTEL": C_WARN, "NIEDRIG": C_OK}
        data = [[Paragraph("Prioritaet", s["cellmuted"]), Paragraph("Bereich", s["cellmuted"]),
                 Paragraph("Massnahme", s["cellmuted"])]]
        for r in recs:
            c = pc.get(r.get("prioritaet", ""), MUTED)
            data.append([
                Paragraph(f'<font color="{c.hexval()}">{r.get("prioritaet","")}</font>', s["cell"]),
                Paragraph(r.get("bereich", ""), s["cell"]),
                Paragraph(r.get("massnahme", ""), s["cell"]),
            ])
        tbl = Table(data, colWidths=[24*mm, 38*mm, 98*mm])
        tbl.setStyle(TableStyle([
            ("LINEBELOW", (0, 0), (-1, 0), 0.6, INK),
            ("LINEBELOW", (0, 1), (-1, -1), 0.4, HAIRLINE),
            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        self.el.append(tbl)
        self.el.append(Spacer(1, 4*mm))
        self.el.append(Paragraph(
            "Diese Punkte sind kein Grund zur Sorge. Wie Sie sie beheben, lesen Sie auf der naechsten Seite.",
            s["body"]))

    # ── Handlungsaufforderung mit zwei E-Mail-Optionen ─────────────────────
    def _call_to_action(self):
        s = self.s
        self.el.append(PageBreak())
        self.el.append(Paragraph("So beheben Sie das", s["h"]))
        self.el.append(Paragraph(
            "Ihr Ergebnis zeigt Handlungsbedarf - die meisten Punkte sind schnell behoben. "
            "Solche Stellen werden in Deutschland regelmaessig abgemahnt, und eine einzige "
            "Abmahnung kostet oft mehr als ein ganzes Jahr Vorsorge. Sie haben zwei Wege:",
            s["body"]))
        self.el.append(Spacer(1, 5*mm))

        subj1 = quote("DSGVO-Bericht: Anleitung anfordern (29 EUR)")
        subj2 = quote("DSGVO-Bericht: bitte fuer mich umsetzen")
        link1 = f"mailto:{CONTACT}?subject={subj1}"
        link2 = f"mailto:{CONTACT}?subject={subj2}"

        opt_title = ParagraphStyle("ot", parent=s["body"], fontName="Helvetica-Bold", fontSize=11, spaceAfter=2)
        opt_body = ParagraphStyle("ob", parent=s["body"], fontSize=9.5)
        link_st = ParagraphStyle("lk", parent=s["body"], fontName="Helvetica-Bold", fontSize=9.5, textColor=INK)

        card1 = [
            Paragraph("Selbst umsetzen", opt_title),
            Paragraph("Der vollstaendige Bericht erklaert jeden Punkt Schritt fuer Schritt, in klarem Deutsch. "
                      "Einmalig 29 EUR.", opt_body),
            Spacer(1, 2*mm),
            Paragraph(f'<a href="{link1}"><u>Anleitung per E-Mail anfordern &#8594;</u></a>', link_st),
        ]
        card2 = [
            Paragraph("Von mir umsetzen lassen", opt_title),
            Paragraph("Sie schicken mir den Bericht, ich bringe Ihre Website in Ordnung. "
                      "Sie kuemmern sich weiter um Ihr Geschaeft.", opt_body),
            Spacer(1, 2*mm),
            Paragraph(f'<a href="{link2}"><u>Umsetzung anfragen &#8594;</u></a>', link_st),
        ]
        cards = Table([[card1, card2]], colWidths=[80*mm, 80*mm])
        cards.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (-1, -1), SOFT_BG),
            ("LINEBEFORE", (0, 0), (0, -1), 2.5, INK),
            ("LINEBEFORE", (1, 0), (1, -1), 2.5, MUTED),
            ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ]))
        self.el.append(cards)
        self.el.append(Spacer(1, 6*mm))
        self.el.append(Paragraph(
            f'Noch Fragen? Schreiben Sie mir einfach: <b>{CONTACT}</b>', s["body"]))
        self.el.append(Spacer(1, 2*mm))
        self.el.append(Paragraph(
            '<font color="%s"><i>Ein sauberer Auftritt ist kein Luxus. Er haelt Ihnen den Ruecken frei.</i></font>' % MUTED.hexval(),
            s["body"]))

    # ── Bezahlte Vollversion: Schritt-fuer-Schritt-Anleitung ───────────────
    def _remediation_guide(self):
        s = self.s
        self.el.append(PageBreak())
        self.el.append(Paragraph("Ihre Anleitung, Schritt fuer Schritt", s["h"]))
        self.el.append(Paragraph(
            "Auf den folgenden Seiten steht fuer jeden offenen Punkt genau, was zu tun ist. "
            "In klarem Deutsch, in der richtigen Reihenfolge. Arbeiten Sie die Punkte von oben "
            "nach unten ab. Ganz unten steht jeweils, woran Sie erkennen, dass es erledigt ist.",
            s["body"]))
        self.el.append(Spacer(1, 4*mm))

        step_num = ParagraphStyle("sn", parent=s["body"], fontName="Helvetica-Bold",
                                  fontSize=9.5, textColor=WHITE, alignment=1, leading=13)
        step_txt = ParagraphStyle("stx", parent=s["body"], fontSize=9.5, leading=14, spaceAfter=0)
        tip_txt = ParagraphStyle("tip", parent=s["small"], fontSize=8.5, leading=12, textColor=MUTED)
        done_txt = ParagraphStyle("done", parent=s["small"], fontSize=8.5, leading=12, textColor=C_OK)

        # nur offene Punkte, in sinnvoller Reihenfolge (Prioritaet nach Status)
        order = {"FAIL": 0, "WARNING": 1}
        checks = [c for c in self.data.get("checks", [])
                  if c.get("status") in order and c.get("key") in REMEDIATION]
        checks.sort(key=lambda c: order.get(c.get("status"), 9))

        if not checks:
            self.el.append(Paragraph(
                "Erfreulich: Es gibt keine offenen Punkte. Ihre Website ist in den geprueften "
                "Bereichen sauber aufgestellt. Bewahren Sie diesen Bericht als Nachweis auf.",
                s["body"]))
            return

        n = 0
        for c in checks:
            n += 1
            r = REMEDIATION[c["key"]]
            col = STATUS_COLOR.get(c.get("status", "SKIPPED"), MUTED)
            lbl = STATUS_LABEL.get(c.get("status", "SKIPPED"), "-")

            # Kopf: Nummer + Titel + Status
            head = Paragraph(
                f'<font color="{INK.hexval()}"><b>{n}.&nbsp;&nbsp;{r["titel"]}</b></font>'
                f'&nbsp;&nbsp;<font color="{col.hexval()}" size="8">({lbl})</font>',
                ParagraphStyle("gh", parent=s["body"], fontSize=12, leading=16,
                               spaceBefore=8, spaceAfter=4))
            self.el.append(head)

            # nummerierte Schritte als Tabelle (Zahl-Chip + Text)
            rows = []
            for i, schritt in enumerate(r["schritte"], 1):
                chip = Table([[Paragraph(str(i), step_num)]], colWidths=[6*mm], rowHeights=[6*mm])
                chip.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, -1), INK),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]))
                rows.append([chip, Paragraph(schritt, step_txt)])
            steptbl = Table(rows, colWidths=[9*mm, 151*mm])
            steptbl.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (0, -1), 0),
            ]))
            self.el.append(steptbl)

            # Tipp + Fertig-Kontrolle in einem ruhigen Kasten
            info = [
                [Paragraph(f'<b>Tipp:</b>&nbsp; {r["tipp"]}', tip_txt)],
                [Paragraph(f'<b>Fertig, wenn:</b>&nbsp; {r["fertig"]}', done_txt)],
            ]
            box = Table(info, colWidths=[160*mm])
            box.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), SOFT_BG),
                ("LINEBEFORE", (0, 0), (0, -1), 2, HAIRLINE),
                ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            self.el.append(Spacer(1, 2*mm))
            self.el.append(box)
            self.el.append(HRFlowable(width="100%", thickness=0.5, color=HAIRLINE,
                                      spaceBefore=8, spaceAfter=2))

    # ── Bezahlte Vollversion: dezenter Hinweis auf Umsetzung ───────────────
    def _upsell(self):
        s = self.s
        self.el.append(Spacer(1, 6*mm))
        subj = quote("DSGVO-Bericht: bitte fuer mich umsetzen")
        link = f"mailto:{CONTACT}?subject={subj}"

        title = ParagraphStyle("ut", parent=s["body"], fontName="Helvetica-Bold", fontSize=11, spaceAfter=3)
        body = ParagraphStyle("ubd", parent=s["body"], fontSize=9.5)
        link_st = ParagraphStyle("ulk", parent=s["body"], fontName="Helvetica-Bold", fontSize=9.5, textColor=INK)

        block = [
            Paragraph("Keine Zeit oder Lust auf das Technische?", title),
            Paragraph("Sie muessen das nicht selbst machen. Schicken Sie mir diesen Bericht, "
                      "und ich setze die Punkte fuer Sie um. Sie kuemmern sich weiter um Ihr Geschaeft.",
                      body),
            Spacer(1, 2*mm),
            Paragraph(f'<a href="{link}"><u>Umsetzung anfragen &#8594;</u></a>', link_st),
        ]
        card = Table([[block]], colWidths=[160*mm])
        card.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (-1, -1), SOFT_BG),
            ("LINEBEFORE", (0, 0), (0, -1), 2.5, INK),
            ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ]))
        self.el.append(card)
        self.el.append(Spacer(1, 5*mm))
        self.el.append(Paragraph(f'Noch Fragen? Schreiben Sie mir einfach: <b>{CONTACT}</b>', s["body"]))

    def _notes(self):
        s = self.s
        self.el.append(Spacer(1, 10*mm))
        self.el.append(HRFlowable(width="100%", thickness=0.5, color=HAIRLINE, spaceAfter=4))
        self.el.append(Paragraph(
            "Dieser Bericht wurde automatisch vom DSGVO-Checker (DSF Consulting) erstellt und stellt keine "
            "Rechtsberatung dar. Die Analyse ist eine technische Momentaufnahme der Website. Fuer eine "
            "rechtssichere Bewertung ziehen Sie bitte eine Datenschutzbeauftragte oder einen Anwalt hinzu.",
            s["small"]))


def generate_report(scan_data, filepath: str, full: bool = False):
    data = scan_data.to_dict() if hasattr(scan_data, "to_dict") else (
        scan_data if isinstance(scan_data, dict) else scan_data.__dict__)
    DSGVOReportPDF(data).build(filepath, full=full)
    return filepath


generate_pdf_report = generate_report
