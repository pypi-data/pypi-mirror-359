from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import Dict, List, Optional
from functools import lru_cache

class AutoDiscoveryTemplateLoader:
    """
    Maintenance-free template loader that automatically discovers templates.
    No more manual mapping - just drop .tf.j2 files in the right directory!
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

        # Cache for performance (cleared when templates change)
        self._template_cache = {}
        self._discovery_cache = None

    def _find_main_templates_dir(self):
        """Find the templates directory automatically"""
        candidates = [
            Path.cwd() / "templates",
            Path.cwd() / "terraback" / "templates",
            Path(__file__).parent.parent / "templates",
            Path(__file__).parent / "templates",
        ]

        for candidate in candidates:
            if candidate.exists() and candidate.is_dir():
                providers = [d for d in candidate.iterdir() if d.is_dir() and not d.name.startswith("__")]
                if providers:
                    return candidate.resolve()
        return None

    @lru_cache(maxsize=128)
    def _discover_all_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Discover all templates and build a searchable index.
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
        """
        Find template path using smart search strategies.
        """
        discovery = self._discover_all_templates()

        # Strategy 1: Direct path mapping (provider/category/resource.tf.j2)
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

        # Strategy 3: Cross-provider search (maybe it's in a different provider)
        for prov, categories in discovery.items():
            for category, templates in categories.items():
                if resource_type in templates:
                    print(f"Found '{resource_type}' in {prov}/{category} instead of {provider}")
                    return f"{prov}/{category}/{resource_type}.tf.j2"

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
                        similarity = self._calculate_similarity(requested_type, template)
                        marker = " <-- similar" if similarity > 0.7 else ""
                        print(f"    - {template}{marker}")

        # Show other providers that might have this template
        found_in_other_providers = []
        for prov, categories in discovery.items():
            if prov != provider:
                for category, templates in categories.items():
                    if requested_type in templates:
                        found_in_other_providers.append(f"{prov}/{category}")

        if found_in_other_providers:
            print(f"\nFound '{requested_type}' in other providers: {', '.join(found_in_other_providers)}")

        print(f"\nSuggestions:")
        print(f"  - Check spelling of '{requested_type}'")
        print(f"  - Try provider='{provider}' with a different resource name")
        print(f"  - Create template at: {provider}/[category]/{requested_type}.tf.j2")

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Simple similarity calculation for suggestions"""
        if str1 == str2:
            return 1.0

        # Simple similarity based on common characters
        set1, set2 = set(str1.lower()), set(str2.lower())
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0

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

    def get_template_stats(self) -> Dict:
        """Get statistics about available templates"""
        discovery = self._discover_all_templates()

        total_templates = 0
        total_categories = 0

        for provider, categories in discovery.items():
            total_categories += len(categories)
            for templates in categories.values():
                total_templates += len(templates)

        return {
            'providers': len(discovery),
            'categories': total_categories,
            'templates': total_templates,
            'by_provider': {
                prov: sum(len(templates) for templates in categories.values())
                for prov, categories in discovery.items()
            }
        }

    def add_template_alias(self, alias: str, actual_name: str, provider: str = 'aws'):
        """
        Add a runtime alias for backward compatibility
        Example: loader.add_template_alias('ec2', 'ec2_instance', 'aws')
        """
        cache_key = f"{provider}:{alias}"
        actual_path = self.get_template_path(actual_name, provider)
        self._template_cache[cache_key] = actual_path
        print(f"Added alias: {alias} -> {actual_name} ({provider})")

    def refresh_cache(self):
        """Refresh the template discovery cache (use after adding new templates)"""
        self._template_cache.clear()
        self._discover_all_templates.cache_clear()
        print("Template cache refreshed")

    def validate_all_templates(self) -> Dict:
        """Validate that all discovered templates can be loaded"""
        discovery = self._discover_all_templates()
        results = {'valid': [], 'invalid': []}

        for provider, categories in discovery.items():
            for category, templates in categories.items():
                for template_name in templates:
                    template_path = f"{provider}/{category}/{template_name}.tf.j2"
                    try:
                        self.env.get_template(template_path)
                        results['valid'].append(template_path)
                    except Exception as e:
                        results['invalid'].append((template_path, str(e)))

        return results

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

# Utility functions for template management
def list_all_templates():
    """Convenience function to list all available templates"""
    loader = get_template_loader()
    return loader.list_available_templates()

def show_template_stats():
    """Show template statistics"""
    loader = get_template_loader()
    stats = loader.get_template_stats()

    print("Template Statistics:")
    print(f"  Providers: {stats['providers']}")
    print(f"  Categories: {stats['categories']}")
    print(f"  Total Templates: {stats['templates']}")
    print("\nBy Provider:")
    for provider, count in stats['by_provider'].items():
        print(f"  {provider}: {count} templates")

def validate_templates():
    """Validate all templates can be loaded"""
    loader = get_template_loader()
    results = loader.validate_all_templates()

    print(f"Valid templates: {len(results['valid'])}")
    if results['invalid']:
        print(f"Invalid templates: {len(results['invalid'])}")
        for template_path, error in results['invalid']:
            print(f"  {template_path}: {error}")

    return len(results['invalid']) == 0
