#!/usr/bin/env python3
"""
DSF DSGVO Compliance Report -- PDF Generator
=============================================
Professioneller PDF-Report mit Ampelsystem.

(c) 2026 DSF Consulting - AF13-NEXUS
"""

from datetime import datetime, timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas


# =============================================================================
# FARBEN
# =============================================================================

DSF_DARK    = colors.HexColor("#1a1a2e")
DSF_BLUE    = colors.HexColor("#16213e")
DSF_ACCENT  = colors.HexColor("#0f3460")
DSF_LIGHT   = colors.HexColor("#e8e8e8")
DSF_WHITE   = colors.white

COLOR_PASS    = colors.HexColor("#2d6a4f")
COLOR_WARNING = colors.HexColor("#e07c24")
COLOR_FAIL    = colors.HexColor("#c0392b")
COLOR_INFO    = colors.HexColor("#2980b9")
COLOR_GRAY    = colors.HexColor("#7f8c8d")

RISK_COLORS = {
    "HOCH":         colors.HexColor("#c0392b"),
    "MITTEL":       colors.HexColor("#e07c24"),
    "NIEDRIG":      colors.HexColor("#27ae60"),
    "SEHR NIEDRIG": colors.HexColor("#2d6a4f"),
    "UNBEKANNT":    colors.HexColor("#7f8c8d"),
}

STATUS_COLORS = {
    "PASS":    COLOR_PASS,
    "WARNING": COLOR_WARNING,
    "FAIL":    COLOR_FAIL,
    "INFO":    COLOR_INFO,
    "SKIPPED": COLOR_GRAY,
}

STATUS_LABELS = {
    "PASS":    "OK",
    "WARNING": "Warnung",
    "FAIL":    "Mangelhaft",
    "INFO":    "Info",
    "SKIPPED": "Uebersprungen",
}


# =============================================================================
# STYLES
# =============================================================================

def get_styles():
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "DSFTitle", parent=base["Title"],
            fontSize=22, textColor=DSF_DARK,
            spaceAfter=6, fontName="Helvetica-Bold",
        ),
        "subtitle": ParagraphStyle(
            "DSFSubtitle", parent=base["Normal"],
            fontSize=11, textColor=DSF_ACCENT,
            spaceAfter=12, fontName="Helvetica",
        ),
        "h1": ParagraphStyle(
            "DSFH1", parent=base["Heading1"],
            fontSize=16, textColor=DSF_DARK,
            spaceBefore=16, spaceAfter=8,
            fontName="Helvetica-Bold",
        ),
        "h2": ParagraphStyle(
            "DSFH2", parent=base["Heading2"],
            fontSize=13, textColor=DSF_ACCENT,
            spaceBefore=12, spaceAfter=6,
            fontName="Helvetica-Bold",
        ),
        "body": ParagraphStyle(
            "DSFBody", parent=base["Normal"],
            fontSize=10, textColor=colors.black,
            spaceAfter=6, fontName="Helvetica",
            leading=14, alignment=TA_JUSTIFY,
        ),
        "body_small": ParagraphStyle(
            "DSFBodySmall", parent=base["Normal"],
            fontSize=8, textColor=COLOR_GRAY,
            spaceAfter=4, fontName="Helvetica",
            leading=11,
        ),
        "finding": ParagraphStyle(
            "DSFFinding", parent=base["Normal"],
            fontSize=9, textColor=colors.black,
            spaceAfter=2, fontName="Helvetica",
            leading=12, leftIndent=8,
        ),
        "cell": ParagraphStyle(
            "DSFCell", parent=base["Normal"],
            fontSize=9, textColor=colors.black,
            fontName="Helvetica", leading=12,
        ),
        "cell_bold": ParagraphStyle(
            "DSFCellBold", parent=base["Normal"],
            fontSize=9, textColor=colors.black,
            fontName="Helvetica-Bold", leading=12,
        ),
        "verdict": ParagraphStyle(
            "DSFVerdict", parent=base["Normal"],
            fontSize=14, textColor=DSF_DARK,
            fontName="Helvetica-Bold", alignment=TA_CENTER,
            spaceBefore=8, spaceAfter=8,
        ),
        "footer": ParagraphStyle(
            "DSFFooter", parent=base["Normal"],
            fontSize=7, textColor=COLOR_GRAY,
            fontName="Helvetica",
        ),
    }
    return styles


# =============================================================================
# PAGE TEMPLATE
# =============================================================================

class DSFPageTemplate:
    """Header/Footer fuer jede Seite."""

    def __init__(self, scan_id: str, scan_date: str):
        self.scan_id = scan_id
        self.scan_date = scan_date

    def __call__(self, canvas_obj, doc):
        canvas_obj.saveState()
        w, h = A4

        # Header-Linie
        canvas_obj.setStrokeColor(DSF_ACCENT)
        canvas_obj.setLineWidth(2)
        canvas_obj.line(20*mm, h - 15*mm, w - 20*mm, h - 15*mm)

        # Header-Text
        canvas_obj.setFont("Helvetica-Bold", 8)
        canvas_obj.setFillColor(DSF_ACCENT)
        canvas_obj.drawString(20*mm, h - 13*mm, "DSF DSGVO COMPLIANCE REPORT")

        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.setFillColor(COLOR_GRAY)
        canvas_obj.drawRightString(w - 20*mm, h - 13*mm, f"{self.scan_id} | {self.scan_date}")

        # Footer
        canvas_obj.setStrokeColor(DSF_LIGHT)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(20*mm, 15*mm, w - 20*mm, 15*mm)

        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.setFillColor(COLOR_GRAY)
        canvas_obj.drawString(20*mm, 10*mm, "(c) DSF Consulting | AF13-NEXUS | Vertraulich")
        canvas_obj.drawRightString(w - 20*mm, 10*mm, f"Seite {doc.page}")

        canvas_obj.restoreState()


# =============================================================================
# REPORT BUILDER
# =============================================================================

class DSGVOReportPDF:

    def __init__(self, scan_data: dict):
        self.data = scan_data
        self.styles = get_styles()
        self.elements = []

    def build(self, filepath: str):
        """PDF generieren und speichern."""
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            topMargin=22*mm,
            bottomMargin=22*mm,
            leftMargin=20*mm,
            rightMargin=20*mm,
        )

        template = DSFPageTemplate(
            self.data.get("scan_id", ""),
            self.data.get("scan_date", ""),
        )

        self._build_cover()
        self._build_executive_summary()
        self._build_check_details()
        self._build_third_parties()
        self._build_cookies()
        self._build_recommendations()
        self._build_appendix()

        doc.build(self.elements, onFirstPage=template, onLaterPages=template)

    # -------------------------------------------------------------------------

    def _build_cover(self):
        s = self.styles
        summary = self.data.get("summary", {})
        risk_level = self.data.get("risk_level", "UNBEKANNT")
        risk_score = self.data.get("risk_score", 0)

        self.elements.append(Spacer(1, 30*mm))
        self.elements.append(Paragraph("DSGVO COMPLIANCE", s["title"]))
        self.elements.append(Paragraph("ANALYSE-REPORT", s["title"]))
        self.elements.append(Spacer(1, 8*mm))

        self.elements.append(HRFlowable(
            width="100%", thickness=2, color=DSF_ACCENT,
            spaceAfter=8*mm
        ))

        # Meta-Info Tabelle
        meta_data = [
            ["Website:", self.data.get("final_url", self.data.get("url", ""))],
            ["Scan-Datum:", self.data.get("scan_date", "")],
            ["Scan-ID:", self.data.get("scan_id", "")],
            ["Engine:", self.data.get("meta", {}).get("engine", "")],
        ]
        meta_table = Table(meta_data, colWidths=[35*mm, 120*mm])
        meta_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (0, -1), DSF_ACCENT),
            ("TEXTCOLOR", (1, 0), (1, -1), colors.black),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        self.elements.append(meta_table)
        self.elements.append(Spacer(1, 12*mm))

        # Risiko-Ampel
        risk_color = RISK_COLORS.get(risk_level, COLOR_GRAY)

        ampel_data = [[
            Paragraph(f'<font color="white" size="18"><b>RISIKO: {risk_level}</b></font>', s["verdict"]),
        ], [
            Paragraph(f'<font color="white" size="12">Score: {risk_score}/100</font>', s["verdict"]),
        ]]

        ampel_table = Table(ampel_data, colWidths=[160*mm])
        ampel_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), risk_color),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("ROUNDEDCORNERS", [4, 4, 4, 4]),
        ]))
        self.elements.append(ampel_table)

        self.elements.append(Spacer(1, 8*mm))
        verdict = summary.get("verdict", "")
        self.elements.append(Paragraph(verdict, s["body"]))

        self.elements.append(PageBreak())

    # -------------------------------------------------------------------------

    def _build_executive_summary(self):
        s = self.styles
        summary = self.data.get("summary", {})

        self.elements.append(Paragraph("1. ZUSAMMENFASSUNG", s["h1"]))
        self.elements.append(HRFlowable(width="100%", thickness=1, color=DSF_LIGHT, spaceAfter=4*mm))

        # Ampel-Uebersicht
        checks_pass = summary.get("checks_pass", 0)
        checks_warn = summary.get("checks_warning", 0)
        checks_fail = summary.get("checks_fail", 0)
        checks_total = summary.get("checks_total", 0)

        overview_data = [
            [
                Paragraph("<b>Checks gesamt</b>", s["cell_bold"]),
                Paragraph("<b>Bestanden</b>", s["cell_bold"]),
                Paragraph("<b>Warnungen</b>", s["cell_bold"]),
                Paragraph("<b>Mangelhaft</b>", s["cell_bold"]),
                Paragraph("<b>Drittanbieter</b>", s["cell_bold"]),
                Paragraph("<b>Cookies vor Consent</b>", s["cell_bold"]),
            ],
            [
                Paragraph(str(checks_total), s["cell"]),
                Paragraph(f'<font color="{COLOR_PASS.hexval()}">{checks_pass}</font>', s["cell"]),
                Paragraph(f'<font color="{COLOR_WARNING.hexval()}">{checks_warn}</font>', s["cell"]),
                Paragraph(f'<font color="{COLOR_FAIL.hexval()}">{checks_fail}</font>', s["cell"]),
                Paragraph(str(summary.get("third_party_count", 0)), s["cell"]),
                Paragraph(str(summary.get("cookies_before_consent", 0)), s["cell"]),
            ],
        ]

        overview_table = Table(overview_data, colWidths=[27*mm, 25*mm, 25*mm, 27*mm, 28*mm, 38*mm])
        overview_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DSF_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), DSF_WHITE),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, DSF_LIGHT),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        self.elements.append(overview_table)
        self.elements.append(Spacer(1, 8*mm))

        # Checks-Uebersicht als Ampel-Tabelle
        self.elements.append(Paragraph("Ergebnis je Pruefbereich:", s["h2"]))

        checks = self.data.get("checks", [])
        if checks:
            check_overview = [
                [
                    Paragraph("<b>Bereich</b>", s["cell_bold"]),
                    Paragraph("<b>Status</b>", s["cell_bold"]),
                    Paragraph("<b>Bewertung</b>", s["cell_bold"]),
                ]
            ]

            for c in checks:
                status = c.get("status", "SKIPPED")
                sc = STATUS_COLORS.get(status, COLOR_GRAY)
                label = STATUS_LABELS.get(status, status)

                check_overview.append([
                    Paragraph(c.get("title", ""), s["cell"]),
                    Paragraph(f'<font color="{sc.hexval()}"><b>{label}</b></font>', s["cell"]),
                    Paragraph(c.get("detail", "")[:100], s["cell"]),
                ])

            col_widths = [45*mm, 25*mm, 100*mm]
            check_table = Table(check_overview, colWidths=col_widths)
            check_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), DSF_BLUE),
                ("TEXTCOLOR", (0, 0), (-1, 0), DSF_WHITE),
                ("GRID", (0, 0), (-1, -1), 0.5, DSF_LIGHT),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                # Alternating row colors
                *[("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f5f5f5"))
                  for i in range(2, len(check_overview), 2)],
            ]))
            self.elements.append(check_table)

        self.elements.append(PageBreak())

    # -------------------------------------------------------------------------

    def _build_check_details(self):
        s = self.styles
        checks = self.data.get("checks", [])

        self.elements.append(Paragraph("2. DETAILLIERTE ERGEBNISSE", s["h1"]))
        self.elements.append(HRFlowable(width="100%", thickness=1, color=DSF_LIGHT, spaceAfter=4*mm))

        for c in checks:
            status = c.get("status", "SKIPPED")
            sc = STATUS_COLORS.get(status, COLOR_GRAY)
            label = STATUS_LABELS.get(status, status)

            block = []

            # Titel mit Status-Farbe
            title_html = (
                f'<font color="{sc.hexval()}"><b>[{label}]</b></font> '
                f'<b>{c.get("title", "")}</b>'
            )
            block.append(Paragraph(title_html, s["h2"]))

            # Detail
            block.append(Paragraph(c.get("detail", ""), s["body"]))

            # Rechtsgrundlage
            if c.get("rechtsgrundlage"):
                block.append(Paragraph(
                    f'<i>Rechtsgrundlage: {c["rechtsgrundlage"]}</i>',
                    s["body_small"]
                ))

            # Sub-Findings
            for sf in c.get("sub_findings", []):
                block.append(Paragraph(f"- {sf}", s["finding"]))

            # Empfehlung
            if c.get("empfehlung"):
                block.append(Paragraph(
                    f'<font color="{DSF_ACCENT.hexval()}"><b>Empfehlung:</b></font> {c["empfehlung"]}',
                    s["body"]
                ))

            block.append(Spacer(1, 3*mm))

            # Keep together wenn moeglich
            self.elements.append(KeepTogether(block))

    # -------------------------------------------------------------------------

    def _build_third_parties(self):
        s = self.styles
        third_parties = self.data.get("third_parties", [])

        if not third_parties:
            return

        self.elements.append(PageBreak())
        self.elements.append(Paragraph("3. ERKANNTE DRITTANBIETER-DIENSTE", s["h1"]))
        self.elements.append(HRFlowable(width="100%", thickness=1, color=DSF_LIGHT, spaceAfter=4*mm))

        tp_data = [
            [
                Paragraph("<b>Dienst</b>", s["cell_bold"]),
                Paragraph("<b>Kategorie</b>", s["cell_bold"]),
                Paragraph("<b>Land</b>", s["cell_bold"]),
                Paragraph("<b>Risiko</b>", s["cell_bold"]),
            ]
        ]

        risk_colors_map = {
            "hoch": COLOR_FAIL,
            "mittel": COLOR_WARNING,
            "niedrig": COLOR_PASS,
            "keine": COLOR_INFO,
        }

        for tp in third_parties:
            rc = risk_colors_map.get(tp.get("risk", ""), COLOR_GRAY)
            tp_data.append([
                Paragraph(tp.get("name", ""), s["cell"]),
                Paragraph(tp.get("category", ""), s["cell"]),
                Paragraph(tp.get("country", ""), s["cell"]),
                Paragraph(f'<font color="{rc.hexval()}"><b>{tp.get("risk", "")}</b></font>', s["cell"]),
            ])

        tp_table = Table(tp_data, colWidths=[50*mm, 35*mm, 20*mm, 25*mm])
        tp_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DSF_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), DSF_WHITE),
            ("GRID", (0, 0), (-1, -1), 0.5, DSF_LIGHT),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            *[("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f5f5f5"))
              for i in range(2, len(tp_data), 2)],
        ]))
        self.elements.append(tp_table)

    # -------------------------------------------------------------------------

    def _build_cookies(self):
        s = self.styles
        cookies = self.data.get("cookies_before_consent", [])

        if not cookies:
            return

        self.elements.append(Spacer(1, 8*mm))
        self.elements.append(Paragraph("4. COOKIES VOR EINWILLIGUNG", s["h1"]))
        self.elements.append(HRFlowable(width="100%", thickness=1, color=DSF_LIGHT, spaceAfter=4*mm))

        self.elements.append(Paragraph(
            f"Folgende {len(cookies)} nicht-essentiellen Cookies wurden gesetzt, "
            f"BEVOR eine Einwilligung erteilt wurde. "
            f"Dies ist ein Verstoss gegen Art. 6 Abs. 1 lit. a DSGVO und TDDDG Paragraph 25.",
            s["body"]
        ))

        cookie_data = [
            [
                Paragraph("<b>Cookie-Name</b>", s["cell_bold"]),
                Paragraph("<b>Domain</b>", s["cell_bold"]),
                Paragraph("<b>Secure</b>", s["cell_bold"]),
                Paragraph("<b>HttpOnly</b>", s["cell_bold"]),
            ]
        ]

        for c in cookies[:20]:  # Max 20 im Report
            cookie_data.append([
                Paragraph(c.get("name", ""), s["cell"]),
                Paragraph(c.get("domain", ""), s["cell"]),
                Paragraph("Ja" if c.get("secure") else "Nein", s["cell"]),
                Paragraph("Ja" if c.get("httpOnly") else "Nein", s["cell"]),
            ])

        c_table = Table(cookie_data, colWidths=[50*mm, 50*mm, 20*mm, 20*mm])
        c_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DSF_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), DSF_WHITE),
            ("GRID", (0, 0), (-1, -1), 0.5, DSF_LIGHT),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        self.elements.append(c_table)

    # -------------------------------------------------------------------------

    def _build_recommendations(self):
        s = self.styles
        summary = self.data.get("summary", {})
        recommendations = summary.get("top_recommendations", [])

        if not recommendations:
            return

        self.elements.append(PageBreak())
        self.elements.append(Paragraph("5. HANDLUNGSEMPFEHLUNGEN", s["h1"]))
        self.elements.append(HRFlowable(width="100%", thickness=1, color=DSF_LIGHT, spaceAfter=4*mm))

        self.elements.append(Paragraph(
            "Priorisierte Massnahmen zur Verbesserung der DSGVO-Compliance, "
            "sortiert nach Dringlichkeit:",
            s["body"]
        ))

        prio_colors = {
            "HOCH": COLOR_FAIL,
            "MITTEL": COLOR_WARNING,
            "NIEDRIG": COLOR_PASS,
        }

        rec_data = [
            [
                Paragraph("<b>Nr.</b>", s["cell_bold"]),
                Paragraph("<b>Prioritaet</b>", s["cell_bold"]),
                Paragraph("<b>Bereich</b>", s["cell_bold"]),
                Paragraph("<b>Massnahme</b>", s["cell_bold"]),
            ]
        ]

        for i, rec in enumerate(recommendations, 1):
            pc = prio_colors.get(rec.get("prioritaet", ""), COLOR_GRAY)
            rec_data.append([
                Paragraph(str(i), s["cell"]),
                Paragraph(
                    f'<font color="{pc.hexval()}"><b>{rec.get("prioritaet", "")}</b></font>',
                    s["cell"]
                ),
                Paragraph(rec.get("bereich", ""), s["cell"]),
                Paragraph(rec.get("massnahme", ""), s["cell"]),
            ])

        rec_table = Table(rec_data, colWidths=[12*mm, 25*mm, 35*mm, 98*mm])
        rec_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DSF_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), DSF_WHITE),
            ("GRID", (0, 0), (-1, -1), 0.5, DSF_LIGHT),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            *[("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f5f5f5"))
              for i in range(2, len(rec_data), 2)],
        ]))
        self.elements.append(rec_table)

    # -------------------------------------------------------------------------

    def _build_appendix(self):
        s = self.styles

        self.elements.append(Spacer(1, 12*mm))
        self.elements.append(HRFlowable(width="100%", thickness=1, color=DSF_LIGHT, spaceAfter=4*mm))

        self.elements.append(Paragraph("HINWEISE", s["h2"]))

        disclaimer_text = (
            "Dieser Report wurde automatisch durch die DSF DSGVO Compliance Engine erstellt. "
            "Er stellt keine Rechtsberatung dar. Die Analyse basiert auf einer technischen Pruefung "
            "der Website zum angegebenen Zeitpunkt. Dynamische Inhalte, Login-geschuetzte Bereiche "
            "und serverseitige Konfigurationen werden nicht vollstaendig erfasst. "
            "Fuer eine rechtssichere Bewertung wird die Hinzuziehung eines Datenschutzbeauftragten "
            "oder Rechtsanwalts empfohlen."
        )
        self.elements.append(Paragraph(disclaimer_text, s["body_small"]))

        self.elements.append(Spacer(1, 4*mm))

        tech_text = (
            f"Engine: {self.data.get('meta', {}).get('engine', 'DSF-PRO-CORE')} | "
            f"Renderer: {self.data.get('meta', {}).get('renderer', 'n/a')} | "
            f"JS-Rendering: {'Ja' if self.data.get('meta', {}).get('js_rendering') else 'Nein'}"
        )
        self.elements.append(Paragraph(tech_text, s["body_small"]))

        self.elements.append(Spacer(1, 8*mm))
        self.elements.append(Paragraph(
            "(c) 2026 DSF Consulting | AF13-NEXUS | Alle Rechte vorbehalten.",
            s["body_small"]
        ))


# =============================================================================
# CONVENIENCE
# =============================================================================

def generate_report(scan_data, filepath: str):
    """PDF-Report aus Scan-Daten (dict oder ScanResult) generieren."""
    data = scan_data.to_dict() if hasattr(scan_data, "to_dict") else (scan_data if isinstance(scan_data, dict) else scan_data.__dict__)
    report = DSGVOReportPDF(data)
    report.build(filepath)
    return filepath


# Alias for backward and forward compatibility
generate_pdf_report = generate_report

