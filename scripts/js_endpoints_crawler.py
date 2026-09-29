import sys
import re
import os
from pathlib import Path
from datetime import datetime
import urllib.request
import urllib.parse

# Regex categories for client-side static analysis
PATTERNS = {
    "API Endpoints": [
        r"[`'\"](/(?:api|rest|auth|v[0-9]+)/[^`'\"?$\s]*)",
        r"\+\s*[`'\"](/[^`'\"?$\s]+)[`'\"]",
    ],
    "Angular / Client Routes": [
        r"path:\s*['\"]([^'\"]+)['\"]"
    ],
    "Potential Secrets & Key Names": [
        r"(?i)['\"]?([a-z0-9_-]*(?:secret|apikey|access_token|bearer|private_key)[a-z0-9_-]*)['\"]?\s*[:=]\s*['\"]([^'\"]+)['\"]"
    ],
}

def resolve_target(target: str) -> Path:
    """Returns a Path object, downloading the file first if target is a URL."""
    parsed = urllib.parse.urlparse(target)

    # Check if input is an HTTP(S) URL
    if parsed.scheme in ("http", "https"):
        filename = Path(parsed.path).name or "downloaded_bundle.js"
        local_path = Path.cwd() / filename

        print(f"[*] Downloading '{target}' -> {local_path.name}...")
        try:
            req = urllib.request.Request(
                target,
                headers={"User-Agent": "Mozilla/5.0 (Security Recon/1.0)"}
            )
            with urllib.request.urlopen(req) as response, open(local_path, "wb") as out_file:
                out_file.write(response.read())
            print(f"[+] Download complete: {local_path.resolve()}")
            return local_path
        except Exception as exc:
            print(f"[-] Download failed: {exc}")
            sys.exit(1)

    # Treat input as a local file path
    local_path = Path(target)
    if not local_path.is_file():
        print(f"[-] Error: Target file '{target}' not found.")
        sys.exit(1)
    return local_path

def analyze_and_export(target: str, output_filename: str = "js_endpoints_crawler.txt"):
    input_path = resolve_target(target)

    try:
        content = input_path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        print(f"[-] Error reading file '{input_path.name}': {exc}")
        sys.exit(1)

    # Collect unique findings per category
    findings = {}
    for category, regex_list in PATTERNS.items():
        results = set()
        for pattern in regex_list:
            matches = re.findall(pattern, content)
            for m in matches:
                if isinstance(m, tuple):
                    results.add(f"{m[0]}: {m[1]}")
                else:
                    results.add(m)
        findings[category] = sorted(results)

    # Build structured text report
    border = "=" * 80
    sub_border = "-" * 80
    report = []

    # 1. Header & Metadata
    report.append(border)
    report.append("STATIC JAVASCRIPT RECONNAISSANCE REPORT".center(80))
    report.append(border)
    report.append(f"Source Target : {target}")
    report.append(f"Saved Path    : {input_path.resolve()}")
    report.append(f"File Size     : {len(content):,} bytes")
    report.append(f"Generated On  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # 2. Executive Summary
    report.append("[ SUMMARY OF FINDINGS ]")
    report.append(sub_border)
    for category, items in findings.items():
        report.append(f"  * {category:<35} : {len(items):>4} unique item(s)")
    report.append("")

    # 3. Detailed Categorized Sections
    for category, items in findings.items():
        report.append(border)
        report.append(f"[ {category.upper()} ] (Count: {len(items)})")
        report.append(border)

        if not items:
            report.append("  (No patterns matched in this category)")
        else:
            if category == "API Endpoints":
                grouped = {}
                for ep in items:
                    prefix = ep.split("/")[1] if ep.startswith("/") and len(ep.split("/")) > 1 else "other"
                    grouped.setdefault(f"/{prefix}", []).append(ep)

                for grp, eps in sorted(grouped.items()):
                    report.append(f"\n  -- Namespace: {grp} ({len(eps)} endpoints) --")
                    for ep in eps:
                        report.append(f"     [+] {ep}")
            else:
                for idx, item in enumerate(items, 1):
                    report.append(f"  {idx:>3}. {item}")

        report.append("")

    # 4. Write to disk
    output_path = Path(output_filename)
    try:
        output_path.write_text("\n".join(report), encoding="utf-8")
        print(f"[+] Scan complete.")
        print(f"[+] Structured output written to: {output_path.resolve()}")
    except Exception as exc:
        print(f"[-] Error writing output to '{output_filename}': {exc}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_js_endpoints.py <path_or_url>")
        sys.exit(1)

    analyze_and_export(sys.argv[1])
