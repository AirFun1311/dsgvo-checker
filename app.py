"""
DSF DSGVO/GDPR Compliance Scanner - Streamlit Web Dashboard
============================================================
Interactive web dashboard for automated website privacy & security audits.
Engine: DSF-PRO-CORE v2.0
(c) 2026 DSF Consulting - AF13-NEXUS
"""

import io
import json
from datetime import datetime
import streamlit as st

from dsgvo_scanner import DSGVOScanner, ScanResult
from report_pdf import generate_pdf_report

st.set_page_config(
    page_title="DSF DSGVO Compliance Scanner",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.0rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #555555;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 4px;
        padding: 1rem;
        border-left: 4px solid #0f3460;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown('<div class="main-header">DSF DSGVO / GDPR Compliance Scanner</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Automated zero-trust privacy and technical compliance auditing for web assets.</div>',
    unsafe_allow_html=True,
)

# Sidebar
with st.sidebar:
    st.header("Audit-Konfiguration")
    website_url = st.text_input("Website URL", "https://example.com")
    
    use_browser = st.toggle("Playwright Browser-Rendering (JS)", value=True, help="Aktiviert Headless Chromium zur Erkennung dynamischer Tracker")
    
    st.divider()
    st.markdown("**Regulatorische Standards:**")
    st.caption("• Art. 32 DSGVO (TOM & TLS)\n• Art. 13 DSGVO (Transparenz)\n• § 25 TDDDG (Cookies & Telemetrie)\n• BGH & EuGH Rechtsprechung")
    
    st.divider()
    start_scan = st.button("Audit Starten", type="primary", use_container_width=True)

if "scan_result" not in st.session_state:
    st.session_state.scan_result = None

if start_scan:
    with st.spinner(f"Führe DSGVO-Audit für {website_url} durch..."):
        try:
            scanner = DSGVOScanner(website_url, use_playwright=use_browser)
            result = scanner.scan()
            st.session_state.scan_result = result
        except Exception as e:
            st.error(f"Fehler bei der Durchführung des Scans: {e}")

res: ScanResult = st.session_state.scan_result

if res:
    # Top KPI Metrics
    st.header(f"Audit-Ergebnis: {res.final_url or res.url}")
    st.caption(f"Scan-ID: {res.scan_id} | Datum: {res.scan_date} | Engine: {res.meta.get('engine', 'DSF-PRO-CORE')}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Severity label mapping
    risk_label = {
        "HOCH": "[HOCH]",
        "MITTEL": "[MITTEL]",
        "NIEDRIG": "[NIEDRIG]",
        "SEHR NIEDRIG": "[SEHR NIEDRIG]",
    }.get(res.risk_level, "[UNBEKANNT]")
    
    with col1:
        st.metric("Risikostufe", f"{risk_label} {res.risk_level}", f"Score: {res.risk_score}/100")
    with col2:
        st.metric("Prüfpunkte Gesamt", len(res.checks), f"Fehlgeschlagen: {res.summary.get('checks_fail', 0)}")
    with col3:
        st.metric("Drittanbieter / Tracker", len(res.third_parties), f"Cookies: {len(res.cookies_before_consent)}")
    with col4:
        st.metric("Gesamturteil", "Handlungsbedarf" if res.risk_score >= 40 else "Konform")
        
    st.divider()
    
    # Detailed Tabs
    tab_checks, tab_trackers, tab_recommendations, tab_export = st.tabs([
        "Prüfergebnisse", 
        "Drittanbieter & Cookies", 
        "Handlungsempfehlungen", 
        "Berichte & Export"
    ])
    
    with tab_checks:
        st.subheader("Detailergebnisse der Compliance-Prüfungen")
        for chk in res.checks:
            status_tag = f"[{chk.status}]"
            with st.expander(f"{status_tag} {chk.title} (Strafe: {chk.penalty} Pkt.)"):
                st.write(f"**Details:** {chk.detail}")
                if chk.rechtsgrundlage:
                    st.write(f"**Rechtsgrundlage:** {chk.rechtsgrundlage}")
                if chk.empfehlung:
                    st.info(f"**Empfehlung:** {chk.empfehlung}")
                if chk.sub_findings:
                    st.write("**Befunde:**")
                    for sf in chk.sub_findings:
                        st.write(f"- {sf}")
                        
    with tab_trackers:
        st.subheader("Gefundene Drittanbieter-Dienste & Telemetrie")
        if res.third_parties:
            for tp in res.third_parties:
                st.markdown(f"- **{tp.get('name', 'Unbekannt')}** (`{tp.get('domain', '')}`) — Kategorie: `{tp.get('category', 'Unbekannt')}` | Land: `{tp.get('country', 'Unbekannt')}` | Risiko: `{tp.get('risk', 'niedrig')}`")
        else:
            st.success("Keine externen Drittanbieter-Tracker oder Telemetrie-Dienste vor Consent gefunden.")
            
        st.subheader("Cookies vor Einwilligung")
        if res.cookies_before_consent:
            for c in res.cookies_before_consent:
                st.markdown(f"- Cookie: `{c.get('name')}` (Domain: `{c.get('domain')}`, Secure: `{c.get('secure')}`)")
        else:
            st.success("Keine Cookies vor Nutzereinwilligung gesetzt.")
            
    with tab_recommendations:
        st.subheader("Priorisierte Sofortmaßnahmen")
        top_recs = res.summary.get("top_recommendations", [])
        if top_recs:
            for i, rec in enumerate(top_recs, 1):
                prio = rec.get("prioritaet", "MITTEL")
                badge = f"[{prio}]"
                st.markdown(f"**{i}. {rec.get('bereich', 'Bereich')}** {badge}")
                st.write(f"{rec.get('massnahme', '')}")
                st.markdown("---")
        else:
            st.success("Keine kritischen Handlungsempfehlungen vorhanden. Die Website erfüllt alle Kernvorgaben.")

    with tab_export:
        st.subheader("Audit-Bericht herunterladen")
        
        col_pdf, col_json = st.columns(2)
        
        with col_pdf:
            try:
                temp_pdf_name = f"audit_{res.scan_id}.pdf"
                generate_pdf_report(res, temp_pdf_name)
                with open(temp_pdf_name, "rb") as f:
                    pdf_data = f.read()
                st.download_button(
                    label="PDF-Auditbericht herunterladen",
                    data=pdf_data,
                    file_name=f"DSF_DSGVO_Audit_{res.scan_id}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
            except Exception as ex:
                st.warning(f"PDF-Generierung konnte nicht initialisiert werden: {ex}")
                
        with col_json:
            json_str = json.dumps(res.to_dict() if hasattr(res, "to_dict") else res.__dict__, indent=2, default=str)
            st.download_button(
                label="JSON-Auditdaten exportieren",
                data=json_str,
                file_name=f"DSF_DSGVO_Data_{res.scan_id}.json",
                mime="application/json",
                use_container_width=True
            )

else:
    # Default Welcome & Information
    st.markdown("""
    ### Warum automatisierte DSGVO-Audits unverzichtbar sind
    
    * **Bußgeldrisiken minimieren:** DSGVO Art. 83 sieht Bußgelder von bis zu 20 Mio. EUR oder 4 % des weltweiten Jahresumsatzes vor.
    * **§ 25 TDDDG Konformität:** Externe Dienste und Tracker dürfen erst nach aktiver, informierter Einwilligung geladen werden.
    * **Technisch-Organisatorische Maßnahmen (Art. 32):** Moderne TLS-Verschlüsselung und Security Header (HSTS, CSP) sind Pflicht.
    
    ---
    
    ### Was dieses System prüft:
    1. **HTTPS, HSTS & TLS-Zertifikatsvalidierung**
    2. **Security Header (CSP, X-Frame-Options, Permissions-Policy)**
    3. **Drittanbieter-Erkennung (Google Fonts, Meta Pixel, Analytics, CDNs)**
    4. **Cookie-Setzung vor Nutzertest / Consent-Banner-Funktion**
    5. **Rechtstexte-Abgleich (Impressum & Datenschutzerklärung)**
    """)

st.markdown("---")
st.caption("DSF DSGVO Compliance Platform | Zero Trust Architecture | (c) 2026 DSF Consulting")
