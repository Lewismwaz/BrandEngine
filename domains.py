"""
Domain availability checking using WHOIS/RDAP
"""
import socket
import importlib
import concurrent.futures
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import time
import json


try:
    whois = importlib.import_module("whois")
except ImportError:
    whois = None

try:
    requests = importlib.import_module("requests")
except ImportError:
    requests = None


class DomainChecker:
    """Check domain availability using WHOIS and RDAP"""
    
    def __init__(self):
        self.cache = {}
        self.rdap_servers = {
            '.com': 'https://rdap.verisign.com/com/v1/domain/',
            '.io': 'https://rdap.nic.io/domain/',
            '.ai': 'https://rdap.nic.ai/domain/',
            '.co': 'https://rdap.cointernet.com.co/domain/',
            '.dev': 'https://rdap.nic.google/domain/',
            '.app': 'https://rdap.nic.google/domain/',
            '.tech': 'https://rdap.nic.tech/domain/',
            '.cloud': 'https://rdap.nic.cloud/domain/'
        }
    
    def check_domain(self, domain: str, use_rdap: bool = True) -> Dict:
        """
        Check if a domain is available
        
        Returns:
            Dict with keys: available, checked_at, method, error
        """
        # Check cache
        if domain in self.cache:
            return self.cache[domain]
        
        result = {
            'domain': domain,
            'available': False,
            'checked_at': time.time(),
            'method': 'whois',
            'error': None
        }
        
        try:
            if use_rdap:
                # Try RDAP first
                result = self._check_rdap(domain)
                if result.get('error') is None:
                    self.cache[domain] = result
                    return result
            
            # Fallback to WHOIS
            result = self._check_whois(domain)
            self.cache[domain] = result
            return result
            
        except Exception as e:
            result['error'] = str(e)
            result['available'] = None  # Unknown
            self.cache[domain] = result
            return result
    
    def _check_rdap(self, domain: str) -> Dict:
        """Check domain using RDAP protocol"""
        result = {
            'domain': domain,
            'available': False,
            'checked_at': time.time(),
            'method': 'rdap',
            'error': None
        }
        
        # Find appropriate RDAP server for TLD
        tld = self._get_tld(domain)
        rdap_url = self.rdap_servers.get(tld)
        
        if not rdap_url:
            result['error'] = f"No RDAP server for {tld}"
            return result

        if requests is None:
            result['error'] = "HTTP support unavailable; install 'requests'"
            result['available'] = None
            return result
        
        try:
            response = requests.get(
                rdap_url + domain,
                timeout=10,
                headers={'Accept': 'application/json'}
            )
            
            if response.status_code == 404:
                # Domain not found = available
                result['available'] = True
            elif response.status_code == 200:
                # Domain exists = not available
                data = response.json()
                if 'events' in data and any(e.get('eventAction') == 'expiration' for e in data['events']):
                    # Expired domains might still be unavailable for a grace period
                    result['available'] = False
                else:
                    result['available'] = False
            else:
                result['error'] = f"RDAP returned {response.status_code}"
                result['available'] = None
                
        except requests.exceptions.Timeout:
            result['error'] = "RDAP timeout"
            result['available'] = None
        except requests.exceptions.RequestException as e:
            result['error'] = f"RDAP request failed: {e}"
            result['available'] = None
        except Exception as e:
            result['error'] = f"RDAP error: {e}"
            result['available'] = None
        
        return result
    
    def _check_whois(self, domain: str) -> Dict:
        """Check domain using WHOIS protocol"""
        result = {
            'domain': domain,
            'available': False,
            'checked_at': time.time(),
            'method': 'whois',
            'error': None
        }

        if whois is None:
            result['error'] = "WHOIS support unavailable; install 'python-whois'"
            result['available'] = None
            return result
        
        try:
            # Remove protocol and path
            domain_clean = domain.split('/')[0].split('?')[0]
            
            w = whois.whois(domain_clean)
            
            # If there's no expiration date or domain name, it might be available
            if w.domain_name is None and w.registrar is None:
                result['available'] = True
            else:
                result['available'] = False
                
        except whois.parser.PywhoisError as e:
            if "No match for" in str(e) or "not found" in str(e).lower():
                result['available'] = True
            else:
                result['error'] = str(e)
                result['available'] = None
        except socket.timeout:
            result['error'] = "WHOIS timeout"
            result['available'] = None
        except Exception as e:
            result['error'] = f"WHOIS error: {e}"
            result['available'] = None
        
        return result
    
    def _get_tld(self, domain: str) -> str:
        """Extract TLD from domain"""
        parts = domain.split('.')
        if len(parts) > 1:
            return '.' + '.'.join(parts[1:])
        return ''
    
    def check_domains_batch(self, base_names: List[str], 
                           extensions: List[str]) -> Dict[str, Dict[str, bool]]:
        """
        Check multiple domains in parallel
        
        Args:
            base_names: List of base names (without extension)
            extensions: List of extensions (e.g., ['.com', '.io'])
        
        Returns:
            Dict mapping full domain to availability status
        """
        results = {}
        domains_to_check = []
        
        # Create all domain combinations
        for name in base_names:
            for ext in extensions:
                clean_name = name.lower().replace(' ', '').replace('-', '')
                domain = f"{clean_name}{ext}"
                domains_to_check.append(domain)
        
        # Check domains in parallel with rate limiting
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_domain = {
                executor.submit(self.check_domain, domain): domain 
                for domain in domains_to_check
            }
            
            for future in concurrent.futures.as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    result = future.result(timeout=15)
                    results[domain] = result.get('available', False)
                except Exception as e:
                    print(f"Error checking {domain}: {e}")
                    results[domain] = False
        
        return results
    
    def get_available_domains(self, base_name: str, 
                             extensions: List[str]) -> Dict[str, bool]:
        """Get only available domains for a base name"""
        results = self.check_domains_batch([base_name], extensions)
        return {domain: available for domain, available in results.items() if available}
    
    def clear_cache(self):
        """Clear the domain check cache"""
        self.cache.clear()