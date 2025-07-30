# terraback/cli/azure/__init__.py (Corrected)
import typer
from pathlib import Path
from typing import Optional

app = typer.Typer(
    name="azure",
    help="Work with Microsoft Azure resources.",
    no_args_is_help=True
)

# Import service-level Typer apps
from . import compute, network, storage, loadbalancer, resources

# Registration flag to avoid multiple registrations
_registered = False

# Service modules to register
SERVICE_MODULES = [
    ("Compute", compute),
    ("Network", network),
    ("Storage", storage),
    ("Load Balancer", loadbalancer),
    ("Resources", resources),
]

# Professional-only dependencies
PROFESSIONAL_DEPENDENCIES = [
    # VM dependencies
    ("azure_virtual_machine", "azure_virtual_network"),
    ("azure_virtual_machine", "azure_managed_disk"),
    ("azure_virtual_machine", "azure_network_interface"),
    ("azure_virtual_machine", "azure_availability_set"),
    ("azure_virtual_machine", "azure_resource_group"),
    
    # Disk dependencies
    ("azure_managed_disk", "azure_resource_group"),
    ("azure_managed_disk", "azure_snapshot"),
    
    # Network dependencies
    ("azure_virtual_network", "azure_resource_group"),
    ("azure_subnet", "azure_virtual_network"),
    ("azure_subnet", "azure_network_security_group"),
    ("azure_subnet", "azure_route_table"),
    
    # Network interface dependencies
    ("azure_network_interface", "azure_subnet"),
    ("azure_network_interface", "azure_network_security_group"),
    ("azure_network_interface", "azure_public_ip"),
    ("azure_network_interface", "azure_resource_group"),
    
    # NSG dependencies
    ("azure_network_security_group", "azure_resource_group"),
    
    # Public IP dependencies
    ("azure_public_ip", "azure_resource_group"),
    
    # Load balancer dependencies
    ("azure_lb", "azure_resource_group"),
    ("azure_lb", "azure_public_ip"),
    ("azure_lb", "azure_subnet"),
    ("azure_lb_backend_address_pool", "azure_lb"),
    ("azure_lb_rule", "azure_lb"),
    ("azure_lb_rule", "azure_lb_backend_address_pool"),
    ("azure_lb_probe", "azure_lb"),
    
    # Storage dependencies
    ("azure_storage_account", "azure_resource_group"),
    ("azure_storage_container", "azure_storage_account"),
    ("azure_storage_blob", "azure_storage_container"),
    
    # Route table dependencies
    ("azure_route_table", "azure_resource_group"),
    ("azure_route", "azure_route_table"),
]

def register():
    """Register all Azure resources with cross-scan registry."""
    global _registered
    if _registered:
        return
    _registered = True
    
    # Register all service modules
    for service_name, module in SERVICE_MODULES:
        try:
            module.register()
        except Exception as e:
            typer.echo(f"Warning: Failed to register {service_name}: {e}", err=True)
    
    # Register dependencies for Professional+ tiers
    from terraback.core.license import check_feature_access, Tier
    
    if check_feature_access(Tier.PROFESSIONAL):
        from terraback.utils.cross_scan_registry import cross_scan_registry
        
        for source, target in PROFESSIONAL_DEPENDENCIES:
            cross_scan_registry.register_dependency(source, target)

# Add service subcommands
app.add_typer(compute.app, name="compute", help="VMs, disks, and compute resources")
app.add_typer(network.app, name="network", help="VNets, subnets, NSGs, and network interfaces")
app.add_typer(storage.app, name="storage", help="Storage accounts and related resources")
app.add_typer(loadbalancer.app, name="lb", help="Load balancers")
app.add_typer(resources.app, name="resources", help="Resource groups and management resources")

@app.command("scan-all")
def scan_all_azure(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files"),
    subscription_id: Optional[str] = typer.Option(None, "--subscription-id", "-s", help="Azure Subscription ID", envvar="AZURE_SUBSCRIPTION_ID"),
    location: Optional[str] = typer.Option(None, "--location", "-l", help="Filter by Azure location", envvar="AZURE_LOCATION"),
    resource_group_name: Optional[str] = typer.Option(None, "--resource-group", "-g", help="Filter by a specific resource group"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Recursively scan dependencies")
):
    """Scan all Azure resources across all services."""
    # Ensure resources are registered
    register()
    
    from terraback.cli.azure.session import get_default_subscription_id
    from terraback.core.license import check_feature_access, Tier
    
    # Get default subscription if not provided
    if not subscription_id:
        subscription_id = get_default_subscription_id()
        if not subscription_id:
            typer.echo("Error: No Azure subscription found. Please run 'az login' or set AZURE_SUBSCRIPTION_ID", err=True)
            raise typer.Exit(code=1)
    
    typer.echo(f"Scanning all Azure resources in subscription '{subscription_id}'...")
    if location:
        typer.echo(f"Filtering by location: {location}")
    if resource_group_name:
        typer.echo(f"Filtering by resource group: {resource_group_name}")
    
    if with_deps:
        if check_feature_access(Tier.PROFESSIONAL):
            # Start with resource groups as the base
            from terraback.utils.cross_scan_registry import recursive_scan
            
            typer.echo("\nScanning with dependency resolution (Professional feature)...")
            
            # Define scan targets
            scan_targets = [
                ("azure_resource_group", {}),
                ("azure_virtual_machine", {"resource_group_name": resource_group_name}),
                ("azure_virtual_network", {"resource_group_name": resource_group_name}),
                ("azure_lb", {"resource_group_name": resource_group_name}),
            ]
            
            for resource_type, extra_kwargs in scan_targets:
                kwargs = {
                    "output_dir": output_dir,
                    "subscription_id": subscription_id,
                    "location": location,
                    **extra_kwargs
                }
                recursive_scan(resource_type, **kwargs)
        else:
            typer.echo("\nDependency scanning (--with-deps) requires a Professional license")
            with_deps = False
    
    if not with_deps:
        # Scan each service independently
        scan_functions = [
            ("resource groups", resources.scan_all_resources, {"location": location}),
            ("compute resources", compute.scan_all_compute, {"location": location, "resource_group_name": resource_group_name}),
            ("network resources", network.scan_all_network, {"location": location, "resource_group_name": resource_group_name}),
            ("storage resources", storage.scan_all, {"location": location, "resource_group_name": resource_group_name}),
            ("load balancers", loadbalancer.scan_all_lb, {"location": location, "resource_group_name": resource_group_name}),
        ]
        
        for service_name, scan_func, extra_kwargs in scan_functions:
            typer.echo(f"\nScanning {service_name}...")
            # Corrected: Removed the "with_deps": False line
            kwargs = {
                "output_dir": output_dir,
                "subscription_id": subscription_id,
                **extra_kwargs
            }
            scan_func(**kwargs)

@app.command("list-resources")
def list_azure_resources(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory containing import files")
):
    """List all Azure resources previously scanned."""
    from terraback.utils.importer import ImportManager
    
    resource_types = [
        "azure_resource_group",
        "azure_virtual_machine",
        "azure_managed_disk",
        "azure_virtual_network",
        "azure_subnet",
        "azure_network_security_group",
        "azure_network_interface",
        "azure_storage_account",
        "azure_lb",
    ]
    
    for resource_type in resource_types:
        import_file = output_dir / f"{resource_type}_import.json"
        if import_file.exists():
            typer.echo(f"\n=== {resource_type} ===")
            ImportManager(output_dir, resource_type).list_all()

@app.command("clean")
def clean_azure_files(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory to clean"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Clean all Azure-related generated files."""
    from terraback.utils.cleanup import clean_generated_files
    
    if not yes:
        confirm = typer.confirm(f"This will delete all Azure .tf and _import.json files in {output_dir}. Continue?")
        if not confirm:
            raise typer.Abort()
    
    azure_prefixes = [
        "azure_resource_group",
        "azure_virtual_machine",
        "azure_managed_disk", 
        "azure_virtual_network",
        "azure_subnet",
        "azure_network_security_group",
        "azure_network_interface",
        "azure_storage_account",
        "azure_lb",
    ]
    
    for prefix in azure_prefixes:
        clean_generated_files(output_dir, prefix)
    
    typer.echo("Azure generated files cleaned successfully!")