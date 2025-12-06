import streamlit as st
import json
from dsgvo_scanner import DSGVOScanner
from datetime import datetime

st.set_page_config(
    page_title="DSGVO Compliance Scanner",
    page_icon="🔒",
    layout="wide"
)

# Header
st.title("🔒 DSGVO/GDPR Compliance Scanner")
st.markdown("Automated compliance checking for German SMEs and healthcare providers")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    website_url = st.text_input("Website URL", "https://example.com")
    
    scan_options = st.multiselect(
        "Scan Options",
        ["HTTPS Check", "Privacy Policy", "Cookie Banner", "SSL Certificate", "Full Scan"],
        default=["Full Scan"]
    )
    
    if st.button("🚀 Start Scan", type="primary"):
        st.session_state.scan_triggered = True
    else:
        if 'scan_triggered' not in st.session_state:
            st.session_state.scan_triggered = False

# Main content
if st.session_state.scan_triggered:
    with st.spinner("Scanning website for DSGVO compliance..."):
        scanner = DSGVOScanner(website_url)
        results = scanner.scan()
        
        # Display results
        st.header("📊 Scan Results")
        
        # Risk Level
        risk_colors = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
        st.metric(
            "Risk Level",
            f"{risk_colors.get(results['risk_level'], '⚪')} {results['risk_level']}",
            f"Score: {results['risk_score']}/100"
        )
        
        # Compliance Checks
        st.subheader("Compliance Checks")
        
        for check_name, check_result in results['compliance_checks'].items():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                status = check_result['status']
                if status == "PASS":
                    st.success("✓ " + check_name.replace('_', ' ').title())
                elif status == "FAIL":
                    st.error("✗ " + check_name.replace('_', ' ').title())
                else:
                    st.warning("⚠ " + check_name.replace('_', ' ').title())
            
            with col2:
                st.write(check_result['details'])
        
        # Recommendations
        if results['recommendations']:
            st.subheader("📋 Recommendations")
            for i, rec in enumerate(results['recommendations'], 1):
                st.write(f"{i}. {rec}")
        
        # Download report
        st.subheader("📥 Download Report")
        
        report_json = json.dumps(results, indent=2, ensure_ascii=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="Download JSON Report",
                data=report_json,
                file_name=f"dsgvo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            # Simple HTML report
            html_report = f'''
            <html>
            <head><title>DSGVO Compliance Report</title></head>
            <body>
                <h1>DSGVO Compliance Report</h1>
                <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <h2>Website: {results['url']}</h2>
                <h3>Risk Level: {results['risk_level']} ({results['risk_score']}/100)</h3>
                <h3>Compliance Checks:</h3>
                <ul>
            '''
            
            for check_name, check_result in results['compliance_checks'].items():
                html_report += f'<li>{check_name}: {check_result["status"]} - {check_result["details"]}</li>'
            
            html_report += '''
                </ul>
                <h3>Recommendations:</h3>
                <ol>
            '''
            
            for rec in results['recommendations']:
                html_report += f'<li>{rec}</li>'
            
            html_report += '''
                </ol>
            </body>
            </html>
            '''
            
            st.download_button(
                label="Download HTML Report",
                data=html_report,
                file_name=f"dsgvo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )

else:
    # Landing page
    st.markdown("""
    ## 🎯 Why DSGVO Compliance Matters
    
    Non-compliance can result in:
    - **Fines up to €20 million or 4% of global turnover**
    - **Legal liability** for data breaches
    - **Reputation damage** and loss of customer trust
    
    ## 🚀 How It Works
    
    1. **Enter your website URL**
    2. **Select scan options**
    3. **Get instant compliance report**
    4. **Implement recommendations**
    
    ## 📈 Benefits
    
    - **Automated scanning** - Save hours of manual work
    - **Actionable insights** - Clear remediation steps
    - **Regular monitoring** - Stay compliant over time
    - **Professional reporting** - Ready for auditors
    
    ## 💼 Professional Services
    
    For complete compliance solutions:
    - **Full infrastructure audit**
    - **Document template creation**
    - **Staff training sessions**
    - **Ongoing compliance support**
    
    Contact: compliance@datenschutz-consulting.de
    """)

# Footer
st.markdown("---")
st.markdown("**Disclaimer:** This tool provides automated analysis. For legally binding assessments, consult a certified data protection officer.")
