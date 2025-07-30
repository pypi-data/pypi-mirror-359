import typer
from pathlib import Path
from typing import Optional

# Parallel scan imports (for updated scan_all_azure)
from terraback.utils.parallel_scan import ParallelScanManager, ScanTask, create_scan_tasks

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
    with_deps: bool = typer.Option(False, "--with-deps", help="Recursively scan dependencies"),
    parallel: int = typer.Option(1, "--parallel", help="Number of parallel scans")
):
    """Scan all Azure resources, optionally in parallel."""
    register()

    from terraback.cli.azure.session import get_default_subscription_id
    from terraback.core.license import check_feature_access, Tier
    from terraback.core.license import get_active_tier

    if not subscription_id:
        subscription_id = get_default_subscription_id()
        if not subscription_id:
            typer.echo("Error: No Azure subscription found. Please run 'az login' or set AZURE_SUBSCRIPTION_ID", err=True)
            raise typer.Exit(code=1)

    output_dir.mkdir(parents=True, exist_ok=True)

    typer.echo(f"Scanning all Azure resources in subscription '{subscription_id}'...")
    if location:
        typer.echo(f"Filtering by location: {location}")
    if resource_group_name:
        typer.echo(f"Filtering by resource group: {resource_group_name}")

    tier = get_active_tier()

    # Define all available scan configurations
    all_scan_configs = [
        # Community tier resources
        {'name': 'azure_virtual_machine', 'function': compute.scan_azure_virtual_machines},
        {'name': 'azure_virtual_network', 'function': network.scan_azure_virtual_networks},
        {'name': 'azure_subnet', 'function': network.scan_azure_subnets},
        {'name': 'azure_network_security_group', 'function': network.scan_azure_network_security_groups},
        {'name': 'azure_storage_account', 'function': storage.scan_azure_storage_accounts},
        {'name': 'azure_managed_disk', 'function': compute.scan_azure_managed_disks},
        # Professional tier resources
        {'name': 'azure_sql_server', 'function': compute.scan_azure_sql_servers},
        {'name': 'azure_sql_database', 'function': compute.scan_azure_sql_databases},
        {'name': 'azure_app_service_plan', 'function': compute.scan_azure_app_service_plans},
        {'name': 'azure_web_app', 'function': compute.scan_azure_web_apps},
        {'name': 'azure_function_app', 'function': compute.scan_azure_function_apps},
        {'name': 'azure_key_vault', 'function': compute.scan_azure_key_vaults},
        {'name': 'azure_container_registry', 'function': compute.scan_azure_container_registries},
        {'name': 'azure_kubernetes_cluster', 'function': compute.scan_azure_kubernetes_clusters},
        {'name': 'azure_load_balancer', 'function': loadbalancer.scan_azure_load_balancers},
        {'name': 'azure_application_gateway', 'function': loadbalancer.scan_azure_application_gateways},
    ]

    # Filter resources based on tier
    if tier == Tier.COMMUNITY:
        community_resources = [
            'azure_virtual_machine', 'azure_virtual_network', 'azure_subnet',
            'azure_network_security_group', 'azure_storage_account', 'azure_managed_disk'
        ]
        scan_configs = [c for c in all_scan_configs if c['name'] in community_resources]

        # Show what's being skipped
        skipped = [c['name'] for c in all_scan_configs if c['name'] not in community_resources]
        if skipped:
            typer.echo("\nCommunity Edition - Skipping advanced resources:")
            typer.echo(f"   {', '.join(skipped)}")
            typer.echo("   Upgrade to Professional: terraback license activate <key>\n")
    else:
        scan_configs = all_scan_configs

    # Base kwargs for all scans
    base_kwargs = {
        'output_dir': output_dir,
        'subscription_id': subscription_id,
        'location': location,
        'resource_group_name': resource_group_name
    }

    # Execute scans
    if parallel > 1:
        # Parallel scanning
        typer.echo(f"Scanning {len(scan_configs)} Azure resource types in parallel...")

        # Create scan tasks
        tasks = create_scan_tasks(scan_configs, base_kwargs)

        # Execute parallel scan
        manager = ParallelScanManager(max_workers=parallel)
        results = manager.scan_parallel(tasks)

        # Show cache statistics if caching is enabled
        from terraback.utils.scan_cache import get_scan_cache
        cache = get_scan_cache()
        cache_stats = cache.get_stats()
        if cache_stats['hits'] > 0:
            typer.echo("\nCache Statistics:")
            typer.echo(f"   Hit Rate: {cache_stats['hit_rate']}")
            typer.echo(f"   API calls saved: {cache_stats['hits']}")

    else:
        # Sequential scanning (existing behavior)
        typer.echo(f"Scanning {len(scan_configs)} Azure resource types sequentially...")
        typer.echo("Tip: Use --parallel=8 for faster scanning\n")

        for config in scan_configs:
            try:
                typer.echo(f"Scanning {config['name']}...")
                config['function'](**base_kwargs)
            except Exception as e:
                typer.echo(f"Error scanning {config['name']}: {e}", err=True)

    # Handle dependency scanning if requested and licensed
    if with_deps and check_feature_access(Tier.PROFESSIONAL):
        typer.echo("\nRunning dependency analysis...")
        # Your existing dependency scanning logic here

    typer.echo("\nScan complete!")
    typer.echo(f"Results saved to: {output_dir}/")

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
