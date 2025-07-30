import typer
from pathlib import Path
from typing import Optional, List, Tuple, Callable

# ADDED for new scan_all_gcp
from terraback.utils.parallel_scan import ParallelScanManager, ScanTask, create_scan_tasks

app = typer.Typer(
    name="gcp",
    help="Work with Google Cloud Platform resources.",
    no_args_is_help=True
)

# Service scan functions to register
SERVICE_SCAN_FUNCTIONS = [
    ("GCP instances", "gcp_instance", "terraback.cli.gcp.compute.instances", "scan_instances"),
    ("GCP disks", "gcp_disk", "terraback.cli.gcp.compute.disks", "scan_disks"),
    ("GCP networks", "gcp_network", "terraback.cli.gcp.network.networks", "scan_networks"),
    ("GCP subnets", "gcp_subnet", "terraback.cli.gcp.network.subnets", "scan_subnets"),
    ("GCP firewalls", "gcp_firewall", "terraback.cli.gcp.network.firewalls", "scan_firewalls"),
    ("GCP buckets", "gcp_bucket", "terraback.cli.gcp.storage.buckets", "scan_buckets"),
]

# Professional-only dependencies
PROFESSIONAL_DEPENDENCIES = [
    # Instance dependencies
    ("gcp_instance", "gcp_network"),
    ("gcp_instance", "gcp_subnet"),
    ("gcp_instance", "gcp_disk"),
    ("gcp_instance", "gcp_firewall"),
    ("gcp_instance", "gcp_service_account"),
    # Disk dependencies
    ("gcp_disk", "gcp_snapshot"),
    ("gcp_disk", "gcp_image"),
    # Network dependencies
    ("gcp_subnet", "gcp_network"),
    ("gcp_firewall", "gcp_network"),
    ("gcp_router", "gcp_network"),
    ("gcp_vpn_gateway", "gcp_network"),
    # Load balancer dependencies
    ("gcp_backend_service", "gcp_instance_group"),
    ("gcp_backend_service", "gcp_health_check"),
    ("gcp_url_map", "gcp_backend_service"),
    ("gcp_target_https_proxy", "gcp_url_map"),
    ("gcp_global_forwarding_rule", "gcp_target_https_proxy"),
    # Instance group dependencies
    ("gcp_instance_group", "gcp_instance_template"),
    ("gcp_instance_template", "gcp_network"),
    ("gcp_instance_template", "gcp_subnet"),
    # Storage dependencies
    ("gcp_bucket", "gcp_bucket_iam_binding"),
]

def register():
    """Register GCP resources with cross-scan registry."""
    from terraback.utils.cross_scan_registry import register_scan_function, cross_scan_registry

    # Register all scan functions
    for service_name, resource_type, module_path, func_name in SERVICE_SCAN_FUNCTIONS:
        try:
            module = __import__(module_path, fromlist=[func_name])
            scan_func = getattr(module, func_name)
            register_scan_function(resource_type, scan_func)
        except (ImportError, AttributeError) as e:
            typer.echo(f"Warning: Failed to register {service_name}: {e}", err=True)

    # Register dependencies for Professional+ tiers
    from terraback.core.license import check_feature_access, Tier

    if check_feature_access(Tier.PROFESSIONAL):
        for source, target in PROFESSIONAL_DEPENDENCIES:
            cross_scan_registry.register_dependency(source, target)

def _get_default_project_id() -> Optional[str]:
    """Helper to get default project ID with error handling."""
    from terraback.cli.gcp.session import get_default_project_id

    project_id = get_default_project_id()
    if not project_id:
        typer.echo("Error: No GCP project found. Please run 'gcloud config set project' or set GOOGLE_CLOUD_PROJECT", err=True)
        raise typer.Exit(code=1)
    return project_id

# ========== UPDATED scan-all COMMAND ==========
@app.command("scan-all")
def scan_all_gcp(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    project_id: Optional[str] = typer.Option(None, "--project-id", "-p"),
    region: Optional[str] = typer.Option(None, "--region", "-r"),
    zone: Optional[str] = typer.Option(None, "--zone", "-z"),
    with_deps: bool = typer.Option(False, "--with-deps"),
    parallel: int = typer.Option(1, "--parallel", help="Number of parallel scans")
):
    """Scan all GCP resources across all services, optionally in parallel."""
    # Ensure resources are registered
    register()

    from terraback.core.license import check_feature_access, Tier
    from terraback.core.license import get_active_tier

    if not project_id:
        project_id = _get_default_project_id()

    output_dir.mkdir(parents=True, exist_ok=True)

    typer.echo(f"Scanning all GCP resources in project '{project_id}'...")

    tier = get_active_tier()

    # Define all available scan configurations
    all_scan_configs = [
        # Community tier resources
        {'name': 'gcp_instance', 'function': scan_gcp_instances},
        {'name': 'gcp_network', 'function': scan_gcp_networks},
        {'name': 'gcp_subnet', 'function': scan_gcp_subnets},
        {'name': 'gcp_firewall', 'function': scan_gcp_firewalls},
        {'name': 'gcp_bucket', 'function': scan_gcp_buckets},
        {'name': 'gcp_disk', 'function': scan_gcp_disks},

        # Professional tier resources
        {'name': 'gcp_sql_instance', 'function': scan_gcp_sql_instances},
        {'name': 'gcp_cloud_function', 'function': scan_gcp_cloud_functions},
        {'name': 'gcp_cloud_run_service', 'function': scan_gcp_cloud_run_services},
        {'name': 'gcp_gke_cluster', 'function': scan_gcp_gke_clusters},
        {'name': 'gcp_load_balancer', 'function': scan_gcp_load_balancers},
        {'name': 'gcp_pubsub_topic', 'function': scan_gcp_pubsub_topics},
        {'name': 'gcp_pubsub_subscription', 'function': scan_gcp_pubsub_subscriptions},
        {'name': 'gcp_secret', 'function': scan_gcp_secrets},
        {'name': 'gcp_container_registry', 'function': scan_gcp_container_registries},
    ]

    # Filter resources based on tier
    if tier == Tier.COMMUNITY:
        community_resources = [
            'gcp_instance', 'gcp_network', 'gcp_subnet',
            'gcp_firewall', 'gcp_bucket', 'gcp_disk'
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
        'project_id': project_id,
        'region': region,
        'zone': zone
    }

    # Execute scans
    if parallel > 1:
        # Parallel scanning
        typer.echo(f"Scanning {len(scan_configs)} GCP resource types in parallel...")

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
        typer.echo(f"Scanning {len(scan_configs)} GCP resource types sequentially...")
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

# ========= OLD scan-all replaced above, rest of your file below ==========

def _create_scan_command(
    service_type: str,
    scan_module: str,
    scan_func_name: str,
    needs_zone: bool = False,
    needs_region: bool = False
) -> Callable:
    """Create a scan command function dynamically."""
    def scan_command(
        output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
        project_id: Optional[str] = typer.Option(None, "--project-id", "-p", help="GCP project ID (uses default if not specified)"),
        region: Optional[str] = typer.Option(None, "--region", "-r", help="GCP region") if needs_region else None,
        zone: Optional[str] = typer.Option(None, "--zone", "-z", help="GCP zone") if needs_zone else None,
        with_deps: bool = typer.Option(False, "--with-deps", help="Scan with dependencies")
    ):
        from terraback.core.license import check_feature_access, Tier

        if not project_id:
            project_id = _get_default_project_id()

        typer.echo(f"Scanning GCP {service_type} in project '{project_id}'...")

        if needs_zone and zone:
            typer.echo(f"Zone: {zone}")
        elif needs_zone:
            typer.echo("Zone: all zones")

        if needs_region and region:
            typer.echo(f"Region: {region}")
        elif needs_region:
            typer.echo("Region: all regions")

        if with_deps and check_feature_access(Tier.PROFESSIONAL):
            from terraback.utils.cross_scan_registry import recursive_scan
            recursive_scan(
                f"gcp_{service_type}",
                output_dir=output_dir,
                project_id=project_id,
                region=region,
                zone=zone
            )
        else:
            if with_deps:
                typer.echo("\nDependency scanning (--with-deps) requires a Professional license")
                typer.echo("Falling back to independent scanning...")
                typer.echo("To unlock: terraback license activate <key> or terraback trial start\n")

            try:
                module = __import__(scan_module, fromlist=[scan_func_name])
                scan_func = getattr(module, scan_func_name)

                # Build kwargs based on what the function needs
                kwargs = {"output_dir": output_dir, "project_id": project_id}
                if needs_zone and zone is not None:
                    kwargs["zone"] = zone
                if needs_region and region is not None:
                    kwargs["region"] = region

                scan_func(**kwargs)
            except Exception as e:
                typer.echo(f"Error scanning {service_type}: {e}", err=True)
                raise typer.Exit(code=1)

    return scan_command

# Instance commands
instance_scan = _create_scan_command("instances", "terraback.cli.gcp.compute.instances", "scan_instances", needs_zone=True)
disk_scan = _create_scan_command("disks", "terraback.cli.gcp.compute.disks", "scan_disks", needs_zone=True)
network_scan = _create_scan_command("networks", "terraback.cli.gcp.network.networks", "scan_networks")
subnet_scan = _create_scan_command("subnets", "terraback.cli.gcp.network.subnets", "scan_subnets", needs_region=True)
firewall_scan = _create_scan_command("firewall rules", "terraback.cli.gcp.network.firewalls", "scan_firewalls")
bucket_scan = _create_scan_command("buckets", "terraback.cli.gcp.storage.buckets", "scan_buckets")

# Register commands
app.command("instance-scan")(instance_scan)
app.command("disk-scan")(disk_scan)
app.command("network-scan")(network_scan)
app.command("subnet-scan")(subnet_scan)
app.command("firewall-scan")(firewall_scan)
app.command("bucket-scan")(bucket_scan)

# List commands (simpler pattern)
@app.command("instance-list")
def instance_list(output_dir: Path = typer.Option("generated", "-o", "--output-dir")):
    """List previously scanned GCP instances."""
    from terraback.cli.gcp.compute.instances import list_instances
    list_instances(output_dir)

@app.command("disk-list")
def disk_list(output_dir: Path = typer.Option("generated", "-o", "--output-dir")):
    """List previously scanned GCP disks."""
    from terraback.cli.gcp.compute.disks import list_disks
    list_disks(output_dir)

@app.command("network-list")
def network_list(output_dir: Path = typer.Option("generated", "-o", "--output-dir")):
    """List previously scanned GCP networks."""
    from terraback.cli.gcp.network.networks import list_networks
    list_networks(output_dir)

@app.command("subnet-list")
def subnet_list(output_dir: Path = typer.Option("generated", "-o", "--output-dir")):
    """List previously scanned GCP subnets."""
    from terraback.cli.gcp.network.subnets import list_subnets
    list_subnets(output_dir)

@app.command("firewall-list")
def firewall_list(output_dir: Path = typer.Option("generated", "-o", "--output-dir")):
    """List previously scanned GCP firewall rules."""
    from terraback.cli.gcp.network.firewalls import list_firewalls
    list_firewalls(output_dir)

@app.command("bucket-list")
def bucket_list(output_dir: Path = typer.Option("generated", "-o", "--output-dir")):
    """List previously scanned GCP buckets."""
    from terraback.cli.gcp.storage.buckets import list_buckets
    list_buckets(output_dir)

# Import commands
@app.command("instance-import")
def instance_import(
    instance_id: str = typer.Argument(..., help="GCP instance ID (project/zone/name)"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Import a specific GCP instance."""
    from terraback.cli.gcp.compute.instances import import_instance
    import_instance(instance_id, output_dir)

@app.command("disk-import")
def disk_import(
    disk_id: str = typer.Argument(..., help="GCP disk ID (project/zone/name)"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Import a specific GCP disk."""
    from terraback.cli.gcp.compute.disks import import_disk
    import_disk(disk_id, output_dir)

@app.command("network-import")
def network_import(
    network_id: str = typer.Argument(..., help="GCP network ID (project/name)"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Import a specific GCP network."""
    from terraback.cli.gcp.network.networks import import_network
    import_network(network_id, output_dir)

@app.command("subnet-import")
def subnet_import(
    subnet_id: str = typer.Argument(..., help="GCP subnet ID (project/region/name)"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Import a specific GCP subnet."""
    from terraback.cli.gcp.network.subnets import import_subnet
    import_subnet(subnet_id, output_dir)

@app.command("firewall-import")
def firewall_import(
    firewall_id: str = typer.Argument(..., help="GCP firewall ID (project/name)"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Import a specific GCP firewall rule."""
    from terraback.cli.gcp.network.firewalls import import_firewall
    import_firewall(firewall_id, output_dir)

@app.command("bucket-import")
def bucket_import(
    bucket_name: str = typer.Argument(..., help="GCP bucket name"),
    output_dir: Path = typer.Option("generated", "-o", "--output-dir")
):
    """Import a specific GCP bucket."""
    from terraback.cli.gcp.storage.buckets import import_bucket
    import_bucket(bucket_name, output_dir)
