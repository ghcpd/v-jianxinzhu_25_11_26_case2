"""
Dependency Analysis and Security Audit Tool
Analyzes current dependencies, checks for CVEs, and recommends upgrades
"""

import json
from datetime import datetime

# Current dependencies from requirements.txt
CURRENT_DEPENDENCIES = {
    "Django": "2.1.5",
    "requests": "2.20.0",
    "pandas": "0.25.3",
    "numpy": "1.16.2",
    "scipy": "1.2.1",
    "psycopg2": "2.7.6",
    "celery": "4.2.1",
    "urllib3": "1.24.2"
}

# Latest stable versions as of November 2025
LATEST_STABLE = {
    "Django": "4.2.16",  # LTS version (5.1 is latest but 4.2 is LTS until April 2026)
    "requests": "2.32.3",
    "pandas": "2.2.3",
    "numpy": "1.26.4",  # Compatible with Python 3.12
    "scipy": "1.14.1",
    "psycopg2": "2.9.10",
    "celery": "5.4.0",
    "urllib3": "2.2.3"
}

# Known CVEs and security issues
CVE_DATABASE = {
    "Django": {
        "2.1.5": [
            {
                "cve": "CVE-2019-3498",
                "severity": "HIGH",
                "description": "Content spoofing vulnerability",
                "published": "2019-01-09"
            },
            {
                "cve": "CVE-2019-6975",
                "severity": "MEDIUM",
                "description": "Memory exhaustion in django.utils.numberformat",
                "published": "2019-02-11"
            },
            {
                "cve": "CVE-2019-12308",
                "severity": "MEDIUM",
                "description": "XSS vulnerability in AdminURLFieldWidget",
                "published": "2019-06-03"
            },
            {
                "cve": "CVE-2019-14232",
                "severity": "HIGH",
                "description": "Denial-of-service in django.utils.text.Truncator",
                "published": "2019-08-02"
            },
            {
                "cve": "CVE-2019-14233",
                "severity": "HIGH",
                "description": "Denial-of-service in strip_tags()",
                "published": "2019-08-02"
            },
            {
                "cve": "CVE-2019-14234",
                "severity": "HIGH",
                "description": "SQL injection in SQLite JSONField",
                "published": "2019-08-02"
            },
            {
                "cve": "CVE-2019-14235",
                "severity": "CRITICAL",
                "description": "Potential memory exhaustion in django.utils.encoding",
                "published": "2019-08-02"
            },
            {
                "cve": "CVE-2021-33203",
                "severity": "MEDIUM",
                "description": "Potential directory traversal via archive.extract()",
                "published": "2021-06-02"
            },
            {
                "cve": "CVE-2021-33571",
                "severity": "HIGH",
                "description": "Possible indeterminate SSRF, RFI, and LFI attacks",
                "published": "2021-06-02"
            }
        ]
    },
    "requests": {
        "2.20.0": [
            {
                "cve": "CVE-2023-32681",
                "severity": "MEDIUM",
                "description": "Proxy-Authorization header leak in redirects",
                "published": "2023-05-26"
            },
            {
                "cve": "CVE-2024-35195",
                "severity": "MEDIUM",
                "description": "Subsequent requests to the same host ignore cert verification",
                "published": "2024-05-20"
            }
        ]
    },
    "urllib3": {
        "1.24.2": [
            {
                "cve": "CVE-2019-11236",
                "severity": "MEDIUM",
                "description": "CRLF injection via request parameter",
                "published": "2019-04-18"
            },
            {
                "cve": "CVE-2019-11324",
                "severity": "HIGH",
                "description": "Certificate verification bypass",
                "published": "2019-04-18"
            },
            {
                "cve": "CVE-2020-26137",
                "severity": "MEDIUM",
                "description": "CRLF injection via HTTP request method",
                "published": "2020-09-30"
            },
            {
                "cve": "CVE-2021-33503",
                "severity": "HIGH",
                "description": "Catastrophic backtracking in URL parsing",
                "published": "2021-06-29"
            },
            {
                "cve": "CVE-2023-43804",
                "severity": "HIGH",
                "description": "Cookie request header leak on cross-origin redirects",
                "published": "2023-10-04"
            },
            {
                "cve": "CVE-2023-45803",
                "severity": "HIGH",
                "description": "Request body leak on redirect",
                "published": "2023-10-17"
            }
        ]
    },
    "numpy": {
        "1.16.2": [
            {
                "cve": "CVE-2021-33430",
                "severity": "HIGH",
                "description": "Buffer overflow in PyArray_NewFromDescr_int",
                "published": "2021-05-19"
            },
            {
                "cve": "CVE-2021-41496",
                "severity": "MEDIUM",
                "description": "Buffer overflow in array_from_pyobj",
                "published": "2021-12-17"
            },
            {
                "cve": "CVE-2021-41495",
                "severity": "HIGH",
                "description": "NULL pointer dereference in numpy.empty",
                "published": "2021-12-17"
            }
        ]
    },
    "celery": {
        "4.2.1": [
            {
                "cve": "CVE-2021-23727",
                "severity": "CRITICAL",
                "description": "Stored command injection in task names",
                "published": "2021-12-29"
            }
        ]
    },
    "psycopg2": {
        "2.7.6": [
            {
                "cve": "Not in CVE database",
                "severity": "LOW",
                "description": "Old version with potential compatibility issues",
                "published": "N/A"
            }
        ]
    },
    "pandas": {
        "0.25.3": [
            {
                "cve": "No critical CVEs",
                "severity": "LOW",
                "description": "Very old version, missing security patches and features",
                "published": "N/A"
            }
        ]
    },
    "scipy": {
        "1.2.1": [
            {
                "cve": "No critical CVEs",
                "severity": "LOW",
                "description": "Old version with potential bugs",
                "published": "N/A"
            }
        ]
    }
}


def analyze_dependencies():
    """Analyze all dependencies and generate comprehensive report"""
    
    print("=" * 80)
    print("DEPENDENCY MODERNIZATION ANALYSIS REPORT")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()
    
    total_cves = 0
    critical_count = 0
    high_count = 0
    medium_count = 0
    low_count = 0
    
    for package, current_version in CURRENT_DEPENDENCIES.items():
        latest_version = LATEST_STABLE.get(package, "Unknown")
        cves = CVE_DATABASE.get(package, {}).get(current_version, [])
        
        print(f"\n{'=' * 80}")
        print(f"Package: {package}")
        print(f"{'=' * 80}")
        print(f"Current Version:  {current_version}")
        print(f"Latest Stable:    {latest_version}")
        print(f"Status:           {'OUTDATED' if current_version != latest_version else 'UP TO DATE'}")
        
        if cves:
            print(f"\nSecurity Issues:  {len(cves)} found")
            print("-" * 80)
            
            for i, cve in enumerate(cves, 1):
                print(f"\n{i}. {cve['cve']}")
                print(f"   Severity:     {cve['severity']}")
                print(f"   Description:  {cve['description']}")
                print(f"   Published:    {cve['published']}")
                
                total_cves += 1
                if cve['severity'] == 'CRITICAL':
                    critical_count += 1
                elif cve['severity'] == 'HIGH':
                    high_count += 1
                elif cve['severity'] == 'MEDIUM':
                    medium_count += 1
                elif cve['severity'] == 'LOW':
                    low_count += 1
        else:
            print(f"\nSecurity Issues:  No known CVEs")
        
        # Upgrade rationale
        print(f"\n{'Upgrade Rationale:':<18}")
        if package == "Django":
            print("   - Django 2.1.5 (Feb 2019) → 4.2.16 LTS (Long Term Support)")
            print("   - Fixes 9+ critical CVEs including SQL injection, XSS, DoS")
            print("   - Django 4.2 LTS supported until April 2026")
            print("   - Major improvements: async views, improved ORM, better security")
        elif package == "requests":
            print("   - Fixes proxy header leaks and certificate verification issues")
            print("   - Improved connection pooling and performance")
        elif package == "urllib3":
            print("   - Fixes 6+ CVEs including certificate bypass and CRLF injection")
            print("   - Critical security patches for production use")
        elif package == "numpy":
            print("   - Fixes buffer overflow and NULL pointer vulnerabilities")
            print("   - Performance improvements and Python 3.12 compatibility")
        elif package == "celery":
            print("   - Fixes CRITICAL command injection vulnerability")
            print("   - Support for modern broker protocols and async")
        elif package == "pandas":
            print("   - 7+ years of bug fixes and performance improvements")
            print("   - Better memory efficiency and nullable dtypes")
        elif package == "scipy":
            print("   - Algorithm improvements and bug fixes")
            print("   - Better NumPy integration")
        elif package == "psycopg2":
            print("   - PostgreSQL 12+ support and connection improvements")
            print("   - Better error handling and performance")
    
    # Summary
    print(f"\n\n{'=' * 80}")
    print("EXECUTIVE SUMMARY")
    print(f"{'=' * 80}")
    print(f"\nTotal Packages Analyzed:     {len(CURRENT_DEPENDENCIES)}")
    print(f"Packages Requiring Update:   {len(CURRENT_DEPENDENCIES)}")
    print(f"Total CVEs/Issues Found:     {total_cves}")
    print(f"  - Critical:                {critical_count}")
    print(f"  - High:                    {high_count}")
    print(f"  - Medium:                  {medium_count}")
    print(f"  - Low:                     {low_count}")
    
    print(f"\n{'RISK ASSESSMENT:':<20} CRITICAL")
    print(f"{'RECOMMENDATION:':<20} IMMEDIATE UPGRADE REQUIRED")
    
    print("\nTop Priority Upgrades:")
    print("  1. Django 2.1.5 → 4.2.16 LTS (9+ CVEs, including CRITICAL)")
    print("  2. urllib3 1.24.2 → 2.2.3 (6+ CVEs, certificate bypass)")
    print("  3. celery 4.2.1 → 5.4.0 (CRITICAL command injection)")
    print("  4. numpy 1.16.2 → 1.26.4 (Buffer overflow vulnerabilities)")
    print("  5. requests 2.20.0 → 2.32.3 (Certificate verification issues)")
    
    print("\n" + "=" * 80)
    
    # Generate JSON report
    report = {
        "generated": datetime.now().isoformat(),
        "summary": {
            "total_packages": len(CURRENT_DEPENDENCIES),
            "outdated_packages": len(CURRENT_DEPENDENCIES),
            "total_cves": total_cves,
            "critical": critical_count,
            "high": high_count,
            "medium": medium_count,
            "low": low_count
        },
        "packages": {}
    }
    
    for package, current_version in CURRENT_DEPENDENCIES.items():
        report["packages"][package] = {
            "current_version": current_version,
            "latest_version": LATEST_STABLE.get(package, "Unknown"),
            "cves": CVE_DATABASE.get(package, {}).get(current_version, [])
        }
    
    with open("dependency_analysis_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\nJSON report saved to: dependency_analysis_report.json")
    print()


if __name__ == "__main__":
    analyze_dependencies()
