from pathlib import Path
import json
from datetime import datetime

def generate_report(target_name: str, base_path: str, stats: dict) -> None:
    base = Path(base_path)
    report_path = base / 'REPORT.md'
    
    secrets = []
    endpoints = []
    params = []
    domains = []
    
    for p in [base/'trufflehog.json', base/'raw_data'/'trufflehog.json']:
        if p.exists():
            try:
                with open(p, encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        for line in content.splitlines():
                            if line.strip():
                                secrets.append(json.loads(line))
                break
            except: pass

    extracts_dir = base / 'extracts'
    if extracts_dir.exists():
        for filename, data_list in [('endpoints.txt', endpoints), ('params.txt', params), ('domains.txt', domains)]:
            file_path = extracts_dir / filename
            if file_path.exists():
                with open(file_path, encoding='utf-8') as f:
                    data_list.extend([line.strip() for line in f if line.strip()])

    verified = [s for s in secrets if s.get('Verified')]
    duration = stats.get('scan_duration', 0)
    
    md = f"#  Scan Report: {target_name}\n"
    md += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')} | **Duration:** {duration:.1f}s | **Files:** {stats.get('total_files', 0)}\n\n---\n\n"
    md += "##  Critical Findings\n\n| Severity | Type | File | Secret |\n|----------|------|------|--------|\n"
    
    if verified:
        for s in verified[:10]:
            raw = s.get('Raw', '')[:40].replace('|', ' ')
            file = s.get('SourceMetadata', {}).get('Data', {}).get('Filesystem', {}).get('file', '?')
            md += f"|  **VERIFIED** | {s.get('DetectorName')} | `{file}` | `{raw}...` |\n"
        if len(verified) > 10:
            md += f"\n*...and {len(verified)-10} more verified secrets*\n"
    elif secrets:
        md += f"|  Unverified | {len(secrets)} potential | Check secrets/ | - |\n"
    else:
        md += "|  Clean | No secrets | - | - |\n"

    md += f"\n---\n\n##  Endpoints ({len(endpoints)})\n\n"
    if endpoints:
        md += "```\n" + "\n".join(endpoints[:20]) + "\n```\n"
    
    md += f"\n##  Parameters ({len(params)})\n\n"
    if params:
        md += ", ".join([f"`{p}`" for p in params[:30]]) + "\n"
    
    md += "\n---\n\n##  Output\n\n"
    md += "- **REPORT.md** - You are here\n"
    md += "- **secrets/** - Organized findings\n"
    md += "- **extracts/** - Wordlists\n"
    md += "- **source_code/** - Beautified JS\n"
    md += "- **raw_data/unique_js/** - Raw files (pipe to other tools)\n"
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print(f' Hunter Report: {report_path}')