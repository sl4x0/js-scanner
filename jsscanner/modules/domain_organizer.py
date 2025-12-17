"""
Enhanced AST Analyzer with domain-specific extraction organization
"""
from pathlib import Path
import json
from typing import Dict, Any
from ..utils.file_ops import FileOps


class DomainExtractOrganizer:
    """Organizes extracts by domain while maintaining backward compatibility"""
    
    def __init__(self, base_extracts_path: str, logger):
        """
        Initialize domain extract organizer
        
        Args:
            base_extracts_path: Base path for extracts directory
            logger: Logger instance
        """
        self.base_path = Path(base_extracts_path)
        self.logger = logger
    
    async def save_by_domain(self, extracts_db: dict):
        """
        Save extracts organized by domain
        
        Args:
            extracts_db: Dictionary with endpoints, params, domains, links
        """
        # Build domain-specific data
        domain_data = {}
        
        for extract_type in ['endpoints', 'domains', 'links']:
            for value, data in extracts_db.get(extract_type, {}).items():
                # Group by source domain
                for source in data['sources']:
                    domain = source.get('domain', 'unknown')
                    
                    if domain not in domain_data:
                        domain_data[domain] = {
                            'endpoints': set(),
                            'domains': set(),
                            'links': set(),
                            'endpoints_detailed': {}
                        }
                    
                    # Add to appropriate set
                    domain_data[domain][extract_type].add(value)
                    
                    # Store detailed info for endpoints
                    if extract_type in ['endpoints']:
                        key = f"{extract_type}_detailed"
                        if value not in domain_data[domain][key]:
                            domain_data[domain][key][value] = {
                                'occurrences': 0,
                                'files': []
                            }
                        domain_data[domain][key][value]['occurrences'] += source.get('occurrences', 1)
                        domain_data[domain][key][value]['files'].append(source.get('file', ''))
        
        # Save each domain's extracts to separate directory
        for domain, data in domain_data.items():
            domain_dir = self.base_path / domain
            domain_dir.mkdir(parents=True, exist_ok=True)
            
            # Save endpoints.json
            if data['endpoints']:
                endpoints_file = domain_dir / 'endpoints.json'
                endpoints_data = {
                    'domain': domain,
                    'count': len(data['endpoints']),
                    'endpoints': sorted(list(data['endpoints'])),
                    'detailed': {
                        k: {'occurrences': v['occurrences'], 'files': v['files']}
                        for k, v in data['endpoints_detailed'].items()
                    }
                }
                with open(endpoints_file, 'w', encoding='utf-8') as f:
                    json.dump(endpoints_data, f, indent=2)
        
        self.logger.info(f"✅ Organized extracts for {len(domain_data)} domains")
        return domain_data
    
    async def save_legacy_format(self, extracts_db: dict):
        """
        Maintain backward compatibility by saving flat files
        
        Args:
            extracts_db: Dictionary with endpoints, params, domains, links
        """
        # Save flat files in base extracts directory (backward compatibility)
        for extract_type in ['endpoints', 'domains', 'links']:
            file_ext = 'txt'
            file_path = self.base_path / f'{extract_type}.{file_ext}'
            
            # Collect all unique values
            values = set(extracts_db[extract_type].keys())
            
            if values:
                await FileOps.append_unique_lines(
                    str(file_path),
                    sorted(list(values))
                )
        
        self.logger.info("✅ Saved legacy format for backward compatibility")
    
    def get_domain_summary(self) -> Dict[str, Any]:
        """
        Get summary of all domain-specific extracts
        
        Returns:
            Dictionary with domain statistics
        """
        summary = {}
        
        if not self.base_path.exists():
            return summary
        
        for domain_dir in self.base_path.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                summary[domain] = {
                    'endpoints_count': 0
                }
                
                # Count endpoints
                endpoints_file = domain_dir / 'endpoints.json'
                if endpoints_file.exists():
                    with open(endpoints_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        summary[domain]['endpoints_count'] = data.get('count', 0)
        
        return summary
