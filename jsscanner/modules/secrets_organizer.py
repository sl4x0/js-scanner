"""
Domain-specific secrets organizer
"""
import json
from pathlib import Path
from typing import List, Dict, Any
from urllib.parse import urlparse


class DomainSecretsOrganizer:
    """Organizes secrets by domain while maintaining full results"""
    
    def __init__(self, base_path: str, logger):
        """
        Initialize domain secrets organizer
        
        Args:
            base_path: Base result path for the target
            logger: Logger instance
        """
        self.base_path = Path(base_path)
        self.secrets_dir = self.base_path / 'findings'
        self.logger = logger
        
        # Create findings directory
        self.secrets_dir.mkdir(parents=True, exist_ok=True)
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain from URL
        
        Args:
            url: URL to extract domain from
            
        Returns:
            Domain name (without www.)
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            return domain if domain else 'unknown'
        except:
            return 'unknown'
    
    async def organize_secrets(self, all_secrets: List[dict]):
        """
        Organize secrets by domain
        
        Args:
            all_secrets: List of all secret findings from TruffleHog
        """
        # Group secrets by domain
        secrets_by_domain = {}
        
        for secret in all_secrets:
            # Extract domain from source URL
            source_url = secret.get('SourceMetadata', {}).get('url', '')
            domain = self._extract_domain(source_url)
            
            if domain not in secrets_by_domain:
                secrets_by_domain[domain] = []
            
            secrets_by_domain[domain].append(secret)
        
        # Save each domain's secrets
        for domain, secrets in secrets_by_domain.items():
            domain_dir = self.secrets_dir / domain
            domain_dir.mkdir(parents=True, exist_ok=True)
            
            secrets_file = domain_dir / 'secrets.json'
            
            # Create structured output
            output = {
                'domain': domain,
                'total_secrets': len(secrets),
                'verified_count': sum(1 for s in secrets if s.get('Verified', False)),
                'secrets': secrets
            }
            
            with open(secrets_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2)
            
            self.logger.info(f"  ├─ {domain}: {len(secrets)} secrets")
        
        self.logger.info(f"✅ Organized secrets for {len(secrets_by_domain)} domains")
        
        return secrets_by_domain
    
    async def save_full_results(self, all_secrets: List[dict]):
        """
        Save complete TruffleHog results (all findings)
        
        Args:
            all_secrets: List of all secret findings
        """
        # Save to trufflehog_full.json (complete results)
        full_results_file = self.base_path / 'trufflehog_full.json'
        
        with open(full_results_file, 'w', encoding='utf-8') as f:
            json.dump(all_secrets, f, indent=2)
        
        self.logger.info(f"✅ Saved {len(all_secrets)} total findings to trufflehog_full.json")
    
    def get_secrets_summary(self) -> Dict[str, Any]:
        """
        Get summary of secrets organized by domain
        
        Returns:
            Dictionary with domain statistics
        """
        summary = {
            'total_domains': 0,
            'total_secrets': 0,
            'verified_secrets': 0,
            'domains': {}
        }
        
        if not self.secrets_dir.exists():
            return summary
        
        for domain_dir in self.secrets_dir.iterdir():
            if domain_dir.is_dir():
                domain = domain_dir.name
                secrets_file = domain_dir / 'secrets.json'
                
                if secrets_file.exists():
                    with open(secrets_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        summary['domains'][domain] = {
                            'total': data.get('total_secrets', 0),
                            'verified': data.get('verified_count', 0)
                        }
                        
                        summary['total_secrets'] += data.get('total_secrets', 0)
                        summary['verified_secrets'] += data.get('verified_count', 0)
                        summary['total_domains'] += 1
        
        return summary
