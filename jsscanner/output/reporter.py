from pathlib import Path
import json
from datetime import datetime

def generate_report(target_name: str, base_path: str, stats: dict, logger=None) -> bool:
    """Generate Hunter's Report markdown file
    
    Args:
        target_name: Target name
        base_path: Base results path
        stats: Scan statistics
        logger: Optional logger instance
        
    Returns:
        True if report generated successfully, False otherwise
    """
    try:
        base = Path(base_path)
        report_path = base / 'REPORT.md'
        
        # Ensure stats is a dict
        if not isinstance(stats, dict):
            stats = {}
        
        secrets = []
        endpoints = []
        params = []
        domains = []
        
        for p in [base/'findings'/'trufflehog.json', base/'.warehouse'/'db'/'trufflehog.json']:
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

        extracts_dir = base / 'findings'
        if extracts_dir.exists():
            try:
                for filename, data_list in [('endpoints.txt', endpoints), ('params.txt', params), ('domains.txt', domains)]:
                    file_path = extracts_dir / filename
                    if file_path.exists():
                        with open(file_path, encoding='utf-8') as f:
                            data_list.extend([line.strip() for line in f if line.strip()])
            except Exception:
                pass  # Skip if extracts can't be loaded

        try:
            verified = [s for s in secrets if isinstance(s, dict) and s.get('Verified')]
        except Exception:
            verified = []
        
        duration = stats.get('scan_duration', 0) if isinstance(stats, dict) else 0
        total_files = stats.get('total_files', 0) if isinstance(stats, dict) else 0
        
        md = f"# 🎯 Scan Report: {target_name}\n"
        md += f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')} | **Duration:** {duration:.1f}s | **Files:** {total_files}\n\n---\n\n"
        md += "## 🚨 Critical Findings\n\n| Severity | Type | File | Secret |\n|----------|------|------|--------|\n"
        
        if verified:
            for s in verified[:10]:
                try:
                    raw = s.get('Raw', '')[:40].replace('|', ' ')
                    file = s.get('SourceMetadata', {}).get('Data', {}).get('Filesystem', {}).get('file', '?')
                    md += f"| 🔴 **VERIFIED** | {s.get('DetectorName')} | `{file}` | `{raw}...` |\n"
                except Exception:
                    continue
            if len(verified) > 10:
                md += f"\n*...and {len(verified)-10} more verified secrets*\n"
        elif secrets:
            md += f"| 🟠 Unverified | {len(secrets)} potential | Check secrets/ | - |\n"
        else:
            md += "| 🟢 Clean | No secrets | - | - |\n"

        md += f"\n---\n\n## 🔗 Endpoints ({len(endpoints)})\n\n"
        if endpoints:
            md += "```\n" + "\n".join(endpoints[:20]) + "\n```\n"
        
        md += f"\n## 🔑 Parameters ({len(params)})\n\n"
        if params:
            md += ", ".join([f"`{p}`" for p in params[:30]]) + "\n"
        
        md += "\n---\n\n## 📂 Output Structure\n\n"
        md += "- **REPORT.md** - Executive summary (you are here)\n"
        md += "- **findings/** - Intelligence (secrets, endpoints, params) 🎯\n"
        md += "- **artifacts/source_code/** - Beautified JS for review\n"
        md += "- **logs/** - Scan audit trail\n"
        md += "- **.warehouse/** - Raw data (pipe to other tools)\n"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(md)
        
        if logger:
            logger.info(f'📄 Hunter Report: {report_path}')
        
        return True
    except Exception as e:
        if logger:
            logger.warning(f"Failed to generate report: {e}")
        return False