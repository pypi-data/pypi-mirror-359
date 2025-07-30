from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
import os
from typing import Dict, List, Optional
from functools import lru_cache
import pkg_resources

class AutoDiscoveryTemplateLoader:
    """
    Auto-discovery template loader that works with both development and installed packages
    """
    
    def __init__(self, template_dir_override=None):
        # Find template directory
        if template_dir_override:
            self.template_dir = Path(template_dir_override)
        else:
            self.template_dir = self._find_main_templates_dir()
        
        if not self.template_dir or not self.template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {self.template_dir}")
        
        # Validate directory structure
        providers = [d for d in self.template_dir.iterdir() if d.is_dir() and not d.name.startswith("__")]
        if not providers:
            raise FileNotFoundError(f"No provider directories found in: {self.template_dir}")
        
        print(f"Auto-discovering templates from: {self.template_dir.absolute()}")
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=select_autoescape()
        )
        
        # Cache for performance
        self._template_cache = {}
        self._discovery_cache = None

    def _find_main_templates_dir(self):
        """Find templates directory for both development and installed packages"""
        
        # Method 1: Try package resource (for installed packages)
        try:
            import terraback
            package_path = Path(terraback.__file__).parent
            package_templates = package_path / "templates"
            if package_templates.exists():
                providers = [d for d in package_templates.iterdir() if d.is_dir() and not d.name.startswith("__")]
                if providers:
                    return package_templates.resolve()
        except (ImportError, AttributeError):
            pass
        
        # Method 2: Try using pkg_resources (alternative for installed packages)
        try:
            resource_path = pkg_resources.resource_filename('terraback', 'templates')
            resource_templates = Path(resource_path)
            if resource_templates.exists():
                providers = [d for d in resource_templates.iterdir() if d.is_dir() and not d.name.startswith("__")]
                if providers:
                    return resource_templates.resolve()
        except (ImportError, pkg_resources.DistributionNotFound):
            pass
        
        # Method 3: Try relative to the writer.py file (for development)
        try:
            writer_file = Path(__file__)
            candidates = [
                writer_file.parent.parent / "templates",  # ../templates
                writer_file.parent / "templates",         # ./templates
            ]
            
            for candidate in candidates:
                if candidate.exists() and candidate.is_dir():
                    providers = [d for d in candidate.iterdir() if d.is_dir() and not d.name.startswith("__")]
                    if providers:
                        return candidate.resolve()
        except:
            pass
        
        # Method 4: Try common development locations
        dev_candidates = [
            Path.cwd() / "templates",
            Path.cwd() / "terraback" / "templates",
            Path(__file__).parent.parent / "templates",
            Path(__file__).parent / "templates",
        ]
        
        for candidate in dev_candidates:
            try:
                if candidate.exists() and candidate.is_dir():
                    providers = [d for d in candidate.iterdir() if d.is_dir() and not d.name.startswith("__")]
                    if providers:
                        return candidate.resolve()
            except:
                continue
        
        return None

    @lru_cache(maxsize=128)
    def _discover_all_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Discover all templates and build a searchable index
        Returns: {provider: {category: [template_names]}}
        """
        discovery = {}
        
        for provider_dir in self.template_dir.iterdir():
            if not provider_dir.is_dir() or provider_dir.name.startswith("__"):
                continue
                
            provider_name = provider_dir.name
            discovery[provider_name] = {}
            
            for category_dir in provider_dir.iterdir():
                if not category_dir.is_dir() or category_dir.name.startswith("__"):
                    continue
                    
                category_name = category_dir.name
                discovery[provider_name][category_name] = []
                
                for template_file in category_dir.glob("*.tf.j2"):
                    # Extract clean template name (remove .tf.j2)
                    template_name = template_file.stem.replace('.tf', '')
                    discovery[provider_name][category_name].append(template_name)
        
        return discovery

    def _find_template_path(self, resource_type: str, provider: str = 'aws') -> Optional[str]:
        """Find template path using smart search strategies"""
        discovery = self._discover_all_templates()
        
        # Strategy 1: Direct path mapping
        if provider in discovery:
            for category, templates in discovery[provider].items():
                if resource_type in templates:
                    return f"{provider}/{category}/{resource_type}.tf.j2"
        
        # Strategy 2: Fuzzy matching for common variations
        fuzzy_candidates = [
            resource_type,
            f"{resource_type}_instance",
            f"{resource_type}_cluster", 
            f"{resource_type}_group",
            resource_type.replace('_instance', ''),
            resource_type.replace('_cluster', ''),
            resource_type.replace('_group', ''),
        ]
        
        if provider in discovery:
            for category, templates in discovery[provider].items():
                for candidate in fuzzy_candidates:
                    if candidate in templates:
                        return f"{provider}/{category}/{candidate}.tf.j2"
        
        return None

    def get_template_path(self, resource_type: str, provider: str = 'aws') -> str:
        """Get template path with auto-discovery"""
        
        # Check cache first
        cache_key = f"{provider}:{resource_type}"
        if cache_key in self._template_cache:
            return self._template_cache[cache_key]
        
        # Find the template
        template_path = self._find_template_path(resource_type, provider)
        
        if template_path and (self.template_dir / template_path).exists():
            # Cache the result
            self._template_cache[cache_key] = template_path
            return template_path
        
        # Template not found - provide helpful error
        self._show_available_templates(resource_type, provider)
        raise FileNotFoundError(f"Template not found: {resource_type} (provider: {provider})")

    def _show_available_templates(self, requested_type: str, provider: str):
        """Show available templates when one isn't found"""
        discovery = self._discover_all_templates()
        
        print(f"\nTemplate '{requested_type}' not found for provider '{provider}'")
        print(f"Templates directory: {self.template_dir}")
        
        if provider in discovery:
            print(f"\nAvailable templates in '{provider}':")
            for category, templates in discovery[provider].items():
                if templates:
                    print(f"  {category}/:")
                    for template in sorted(templates):
                        print(f"    - {template}")
        else:
            available_providers = list(discovery.keys())
            print(f"Provider '{provider}' not found. Available providers: {', '.join(available_providers)}")

    def render_template(self, resource_type: str, resources: list, provider: str = 'aws') -> str:
        """Render template with resources"""
        template_path = self.get_template_path(resource_type, provider)
        template = self.env.get_template(template_path)
        return template.render(resources=resources)

    def list_available_templates(self, provider: str = None) -> Dict:
        """List all available templates, optionally filtered by provider"""
        discovery = self._discover_all_templates()
        
        if provider:
            return discovery.get(provider, {})
        return discovery

# Backward compatibility functions
_loader = None

def get_template_loader():
    """Get the global template loader instance"""
    global _loader
    if _loader is None:
        _loader = AutoDiscoveryTemplateLoader()
    return _loader

def generate_tf(resources, resource_type: str, output_path: Path, provider: str = 'aws'):
    """Generate Terraform file with auto-discovery"""
    loader = get_template_loader()
    tf_output = loader.render_template(resource_type, resources, provider)
    
    with open(output_path, "w") as f:
        f.write(tf_output)
