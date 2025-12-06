#!/usr/bin/env python3
"""
DSGVO/GDPR Compliance Scanner - Basic Website Check
"""

import requests
from urllib.parse import urlparse
import ssl
import socket
from datetime import datetime
import json

class DSGVOScanner:
    def __init__(self, url):
        self.url = url if url.startswith('http') else f'https://{url}'
        self.results = {
            'scan_date': datetime.now().isoformat(),
            'url': self.url,
            'compliance_checks': {},
            'risk_score': 0,
            'recommendations': []
        }
    
    def check_https(self):
        """Check if website uses HTTPS"""
        try:
            parsed = urlparse(self.url)
            is_https = parsed.scheme == 'https'
            
            self.results['compliance_checks']['https'] = {
                'status': 'PASS' if is_https else 'FAIL',
                'details': 'HTTPS is required for data protection'
            }
            
            if not is_https:
                self.results['risk_score'] += 30
                self.results['recommendations'].append('Implement HTTPS encryption')
                
            return is_https
        except Exception as e:
            return False
    
    def check_privacy_policy(self):
        """Check for privacy policy link"""
        try:
            response = requests.get(self.url, timeout=10)
            content = response.text.lower()
            
            has_policy = any(term in content for term in [
                'datenschutz', 'datenschutzerklärung', 'privacy policy',
                'datenschutzbestimmungen', 'privacy'
            ])
            
            self.results['compliance_checks']['privacy_policy'] = {
                'status': 'PASS' if has_policy else 'FAIL',
                'details': 'Privacy policy must be easily accessible'
            }
            
            if not has_policy:
                self.results['risk_score'] += 40
                self.results['recommendations'].append('Add privacy policy page')
                
            return has_policy
        except Exception as e:
            return False
    
    def check_cookie_banner(self):
        """Check for cookie consent banner"""
        try:
            response = requests.get(self.url, timeout=10)
            content = response.text.lower()
            
            # Common cookie banner indicators
            cookie_indicators = [
                'cookie', 'cookies', 'einwilligung', 'consent',
                'datenschutzhinweise', 'cookie-richtlinie'
            ]
            
            has_cookie_banner = any(indicator in content for indicator in cookie_indicators)
            
            self.results['compliance_checks']['cookie_banner'] = {
                'status': 'PASS' if has_cookie_banner else 'WARNING',
                'details': 'Cookie consent banner is required for tracking cookies'
            }
            
            if not has_cookie_banner:
                self.results['risk_score'] += 20
                self.results['recommendations'].append('Implement cookie consent banner')
                
            return has_cookie_banner
        except Exception as e:
            return False
    
    def check_ssl_certificate(self):
        """Check SSL certificate validity"""
        try:
            parsed = urlparse(self.url)
            hostname = parsed.hostname
            
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check expiration
                    expires = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_valid = (expires - datetime.now()).days
                    
                    is_valid = days_valid > 0
                    
                    self.results['compliance_checks']['ssl_certificate'] = {
                        'status': 'PASS' if is_valid else 'FAIL',
                        'details': f'SSL certificate valid for {days_valid} days',
                        'expires': expires.isoformat()
                    }
                    
                    if not is_valid or days_valid < 30:
                        self.results['risk_score'] += 25
                        self.results['recommendations'].append('Renew SSL certificate')
                    
                    return is_valid
        except Exception as e:
            return False
    
    def scan(self):
        """Run all compliance checks"""
        print(f"Scanning: {self.url}")
        print("=" * 50)
        
        checks = [
            ('HTTPS Check', self.check_https),
            ('Privacy Policy', self.check_privacy_policy),
            ('Cookie Banner', self.check_cookie_banner),
            ('SSL Certificate', self.check_ssl_certificate)
        ]
        
        for check_name, check_function in checks:
            print(f"Running: {check_name}")
            result = check_function()
            print(f"  Result: {'✓ PASS' if result else '✗ FAIL'}")
        
        # Calculate overall risk level
        if self.results['risk_score'] >= 70:
            risk_level = 'HIGH'
        elif self.results['risk_score'] >= 40:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        self.results['risk_level'] = risk_level
        
        return self.results
    
    def generate_report(self, filename='dsgvo_report.json'):
        """Generate JSON report"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\nReport saved to: {filename}")
        return filename

def main():
    """Command-line interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python dsgvo_scanner.py <website-url>")
        print("Example: python dsgvo_scanner.py https://example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    scanner = DSGVOScanner(url)
    
    results = scanner.scan()
    
    print(f"\n{'='*50}")
    print("SCAN RESULTS SUMMARY")
    print("=" * 50)
    
    for check_name, check_result in results['compliance_checks'].items():
        print(f"{check_name.replace('_', ' ').title()}: {check_result['status']}")
    
    print(f"\nRisk Score: {results['risk_score']}/100")
    print(f"Risk Level: {results['risk_level']}")
    
    if results['recommendations']:
        print("\nRECOMMENDATIONS:")
        for i, rec in enumerate(results['recommendations'], 1):
            print(f"{i}. {rec}")
    
    # Generate report
    report_file = scanner.generate_report()
    
    print(f"\nDetailed report: {report_file}")
    print("=" * 50)

if __name__ == "__main__":
    main()
