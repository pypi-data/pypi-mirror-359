import typer
from pathlib import Path
from typing import Optional
from terraback.utils.parallel_scan import ParallelScanManager, ScanTask, create_scan_tasks


app = typer.Typer(
    name="aws",
    help="Work with Amazon Web Services resources.",
    no_args_is_help=True
)

# Import all AWS service modules
from . import (
    ec2, vpc, s3, iam, rds, lambda_func, elbv2, elb, 
    route53, sns, sqs, acm, apigateway, autoscaling,
    cloudfront, cloudwatch, ecr, ecs, efs, eips,
    elasticache, secretsmanager, ssm
)

# Registration flag to avoid multiple registrations
_registered = False

# Service modules to register
SERVICE_MODULES = [
    ("EC2", ec2),
    ("VPC", vpc),
    ("S3", s3),
    ("IAM", iam),
    ("RDS", rds),
    ("Lambda", lambda_func),
    ("ELBv2", elbv2),
    ("ELB", elb),
    ("Route53", route53),
    ("SNS", sns),
    ("SQS", sqs),
    ("ACM", acm),
    ("API Gateway", apigateway),
    ("Auto Scaling", autoscaling),
    ("CloudFront", cloudfront),
    ("CloudWatch", cloudwatch),
    ("ECR", ecr),
    ("ECS", ecs),
    ("EFS", efs),
    ("EIPs", eips),
    ("ElastiCache", elasticache),
    ("Secrets Manager", secretsmanager),
    ("SSM", ssm),
]

# Professional-only dependencies
PROFESSIONAL_DEPENDENCIES = [
    # EC2 dependencies
    ("ec2", "vpc"),
    ("ec2", "security_groups"),
    ("ec2", "subnets"),
    ("ec2", "eips"),
    ("ec2", "volumes"),
    ("ec2", "amis"),
    ("ec2", "key_pairs"),
    ("ec2", "iam_roles"),
    
    # VPC dependencies
    ("vpc", "internet_gateway"),
    ("vpc", "nat_gateway"),
    ("vpc", "route_table"),
    ("vpc", "vpc_endpoint"),
    
    # Subnet dependencies
    ("subnets", "vpc"),
    ("subnets", "route_table"),
    
    # Security group dependencies
    ("security_groups", "vpc"),
    
    # NAT Gateway dependencies
    ("nat_gateway", "subnets"),
    ("nat_gateway", "eips"),
    
    # Route table dependencies
    ("route_table", "vpc"),
    ("route_table", "internet_gateway"),
    ("route_table", "nat_gateway"),
    
    # Load balancer dependencies
    ("elbv2_load_balancer", "subnets"),
    ("elbv2_load_balancer", "security_groups"),
    ("elbv2_load_balancer", "acm_certificate"),
    ("elbv2_target_group", "vpc"),
    ("elbv2_listener", "elbv2_load_balancer"),
    ("elbv2_listener", "elbv2_target_group"),
    
    # RDS dependencies
    ("rds_instance", "security_groups"),
    ("rds_instance", "db_subnet_group"),
    ("db_subnet_group", "subnets"),
    
    # Lambda dependencies
    ("lambda_function", "iam_roles"),
    ("lambda_function", "security_groups"),
    ("lambda_function", "subnets"),
    
    # ECS dependencies
    ("ecs_service", "ecs_cluster"),
    ("ecs_service", "ecs_task_definition"),
    ("ecs_service", "elbv2_target_group"),
    ("ecs_task_definition", "iam_roles"),
    ("ecs_task_definition", "ecr_repository"),
]

def register():
    """Register all AWS resources with cross-scan registry."""
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
app.add_typer(ec2.app, name="ec2", help="EC2 instances, volumes, AMIs, and compute resources")
app.add_typer(vpc.app, name="vpc", help="VPCs, subnets, security groups, and network infrastructure")
app.add_typer(s3.app, name="s3", help="S3 buckets and object storage")
app.add_typer(iam.app, name="iam", help="IAM roles, policies, and identity management")
app.add_typer(rds.app, name="rds", help="RDS databases and related resources")
app.add_typer(lambda_func.app, name="lambda", help="Lambda functions and layers")
app.add_typer(elbv2.app, name="elbv2", help="Application/Network/Gateway Load Balancers")
app.add_typer(elb.app, name="elb", help="Classic Load Balancers")
app.add_typer(route53.app, name="route53", help="Route 53 DNS and hosted zones")
app.add_typer(sns.app, name="sns", help="SNS topics and subscriptions")
app.add_typer(sqs.app, name="sqs", help="SQS queues and messaging")
app.add_typer(acm.app, name="acm", help="ACM SSL/TLS certificates")
app.add_typer(apigateway.app, name="apigateway", help="API Gateway REST APIs")
app.add_typer(autoscaling.app, name="autoscaling", help="Auto Scaling groups and policies")
app.add_typer(cloudfront.app, name="cloudfront", help="CloudFront CDN distributions")
app.add_typer(cloudwatch.app, name="cloudwatch", help="CloudWatch logs, alarms, and dashboards")
app.add_typer(ecr.app, name="ecr", help="ECR container repositories")
app.add_typer(ecs.app, name="ecs", help="ECS clusters, services, and task definitions")
app.add_typer(efs.app, name="efs", help="EFS file systems and mount targets")
app.add_typer(eips.app, name="eips", help="Elastic IP addresses")
app.add_typer(elasticache.app, name="elasticache", help="ElastiCache Redis and Memcached clusters")
app.add_typer(secretsmanager.app, name="secretsmanager", help="Secrets Manager secrets")
app.add_typer(ssm.app, name="ssm", help="Systems Manager parameters and documents")

@app.command("scan-all")
def scan_all_aws(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory for generated Terraform files"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile name"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Recursively scan dependencies"),
    parallel: int = typer.Option(1, "--parallel", help="Number of parallel workers")
):
    """Scan all AWS resources across all services."""
    # Ensure resources are registered
    register()
    
    from terraback.cli.aws.session import get_boto_session
    from terraback.core.license import check_feature_access, Tier, get_active_tier
    from terraback.utils.parallel_scan import ParallelScanManager, ScanTask, create_scan_tasks
    
    # Get session to validate credentials
    try:
        session = get_boto_session(profile, region or "us-east-1")
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        typer.echo(f"Scanning AWS resources in account {identity['Account']}")
        if region:
            typer.echo(f"Region: {region}")
        else:
            typer.echo("Region: us-east-1 (default)")
    except Exception as e:
        typer.echo(f"Error: AWS authentication failed: {e}", err=True)
        raise typer.Exit(code=1)
    
    if with_deps:
        if check_feature_access(Tier.PROFESSIONAL):
            # Start with EC2 instances as they have the most dependencies
            from terraback.utils.cross_scan_registry import recursive_scan
            
            typer.echo("\nScanning with dependency resolution (Professional feature)...")
            recursive_scan(
                "ec2",
                output_dir=output_dir,
                profile=profile,
                region=region
            )
            return  # Exit early - recursive_scan handles everything
        else:
            typer.echo("\nDependency scanning (--with-deps) requires a Professional license")
            typer.echo("Falling back to independent scanning of each service...")
            typer.echo("To unlock dependency scanning: terraback license activate <key> or terraback trial start\n")
            with_deps = False
    
    # Get active tier for feature gating
    tier = get_active_tier()
    
    # Define all available scan configurations
    all_scan_configs = [
        # Community tier resources (always available)
        {'name': 'ec2', 'function': ec2.instances.scan_ec2},
        {'name': 'vpc', 'function': vpc.vpcs.scan_vpcs},
        {'name': 's3_bucket', 'function': s3.buckets.scan_buckets},
        {'name': 'security_groups', 'function': vpc.security_groups.scan_security_groups},
        {'name': 'iam_roles', 'function': iam.roles.scan_roles},
        {'name': 'iam_policies', 'function': iam.policies.scan_policies},
        
        # Professional tier resources
        # VPC components
        {'name': 'subnets', 'function': vpc.subnets.scan_subnets},
        {'name': 'internet_gateways', 'function': vpc.internet_gateways.scan_internet_gateways},
        {'name': 'nat_gateways', 'function': vpc.nat_gateways.scan_nat_gateways},
        {'name': 'route_tables', 'function': vpc.route_tables.scan_route_tables},
        {'name': 'vpc_endpoints', 'function': vpc.vpc_endpoints.scan_vpc_endpoints},
        
        # EC2 components
        {'name': 'eips', 'function': eips.addresses.scan_eips},
        {'name': 'volumes', 'function': ec2.volumes.scan_volumes},
        {'name': 'snapshots', 'function': ec2.snapshots.scan_snapshots},
        {'name': 'amis', 'function': ec2.amis.scan_amis},
        {'name': 'key_pairs', 'function': ec2.key_pairs.scan_key_pairs},
        {'name': 'launch_templates', 'function': ec2.launch_templates.scan_launch_templates},
        {'name': 'network_interfaces', 'function': ec2.network_interfaces.scan_network_interfaces},
        
        # RDS
        {'name': 'rds', 'function': rds.instances.scan_rds_instances},
        {'name': 'db_subnet_groups', 'function': rds.subnet_groups.scan_db_subnet_groups},
        {'name': 'db_parameter_groups', 'function': rds.parameter_groups.scan_db_parameter_groups},
        
        # Lambda
        {'name': 'lambda', 'function': lambda_func.functions.scan_lambda_functions},
        {'name': 'lambda_layers', 'function': lambda_func.layers.scan_lambda_layers},
        
        # ECS
        {'name': 'ecs_clusters', 'function': ecs.clusters.scan_clusters},
        {'name': 'ecs_services', 'function': ecs.services.scan_services},
        {'name': 'ecs_task_definitions', 'function': ecs.task_definitions.scan_task_definitions},
        
        # Route53
        {'name': 'route53_zones', 'function': route53.zones.scan_hosted_zones},
        {'name': 'route53_records', 'function': route53.records.scan_records},
        
        # SNS
        {'name': 'sns_topics', 'function': sns.topics.scan_topics},
        {'name': 'sns_subscriptions', 'function': sns.subscriptions.scan_subscriptions},
        
        # SQS
        {'name': 'sqs_queues', 'function': sqs.queues.scan_queues},
        
        # ACM
        {'name': 'acm_certificates', 'function': acm.certificates.scan_certificates},
        
        # API Gateway
        {'name': 'api_gateway_rest_apis', 'function': apigateway.rest_apis.scan_rest_apis},
        
        # Auto Scaling
        {'name': 'autoscaling_groups', 'function': autoscaling.auto_scaling_groups.scan_auto_scaling_groups},
        {'name': 'launch_configurations', 'function': autoscaling.launch_configurations.scan_launch_configurations},
        {'name': 'autoscaling_policies', 'function': autoscaling.scaling_policies.scan_scaling_policies},
        
        # CloudFront
        {'name': 'cloudfront_distributions', 'function': cloudfront.distributions.scan_distributions},
        {'name': 'cloudfront_origin_access_controls', 'function': cloudfront.origin_access_controls.scan_origin_access_controls},
        {'name': 'cloudfront_cache_policies', 'function': cloudfront.cache_policies.scan_cache_policies},
        {'name': 'cloudfront_origin_request_policies', 'function': cloudfront.origin_request_policies.scan_origin_request_policies},
        
        # CloudWatch
        {'name': 'cloudwatch_log_groups', 'function': cloudwatch.log_groups.scan_log_groups},
        {'name': 'cloudwatch_alarms', 'function': cloudwatch.alarms.scan_alarms},
        {'name': 'cloudwatch_dashboards', 'function': cloudwatch.dashboards.scan_dashboards},
        
        # ECR
        {'name': 'ecr_repositories', 'function': ecr.repositories.scan_repositories},
        
        # EFS
        {'name': 'efs_file_systems', 'function': efs.file_systems.scan_file_systems},
        {'name': 'efs_mount_targets', 'function': efs.mount_targets.scan_mount_targets},
        {'name': 'efs_access_points', 'function': efs.access_points.scan_access_points},
        
        # ElastiCache
        {'name': 'elasticache_redis_clusters', 'function': elasticache.redis_clusters.scan_redis_clusters},
        {'name': 'elasticache_memcached_clusters', 'function': elasticache.memcached_clusters.scan_memcached_clusters},
        {'name': 'elasticache_replication_groups', 'function': elasticache.replication_groups.scan_replication_groups},
        {'name': 'elasticache_subnet_groups', 'function': elasticache.subnet_groups.scan_subnet_groups},
        {'name': 'elasticache_parameter_groups', 'function': elasticache.parameter_groups.scan_parameter_groups},
        
        # Classic ELB
        {'name': 'classic_load_balancers', 'function': elb.classic_load_balancers.scan_classic_lbs},
        
        # ELBv2
        {'name': 'elbv2_load_balancers', 'function': elbv2.load_balancers.scan_load_balancers},
        {'name': 'elbv2_target_groups', 'function': elbv2.target_groups.scan_target_groups},
        {'name': 'elbv2_listeners', 'function': elbv2.listeners.scan_listeners},
        {'name': 'elbv2_listener_rules', 'function': elbv2.listener_rules.scan_listener_rules},
        
        # Secrets Manager
        {'name': 'secretsmanager_secrets', 'function': secretsmanager.secrets.scan_secrets},
        {'name': 'secretsmanager_secret_versions', 'function': secretsmanager.secret_versions.scan_secret_versions},
        
        # Systems Manager
        {'name': 'ssm_parameters', 'function': ssm.parameters.scan_parameters},
        {'name': 'ssm_documents', 'function': ssm.documents.scan_documents},
        {'name': 'ssm_maintenance_windows', 'function': ssm.maintenance_windows.scan_maintenance_windows},
    ]
    
    # Filter resources based on tier
    if tier == Tier.COMMUNITY:
        community_resources = [
            'ec2', 'vpc', 's3_bucket', 'security_groups', 'iam_roles', 'iam_policies',
            'subnets', 'internet_gateways', 'nat_gateways', 'route_tables', 'vpc_endpoints'
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
        'profile': profile,
        'region': region
    }
    
    # Execute scans
    if parallel > 1:
        # Parallel scanning
        typer.echo(f"Scanning {len(scan_configs)} resource types in parallel...")
        
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
        typer.echo(f"Scanning {len(scan_configs)} resource types sequentially...")
        typer.echo("Tip: Use --parallel=8 for faster scanning\n")
        
        # Always perform independent scans when not using with_deps
        typer.echo("\nPerforming independent scan of core services...")
        
        # Scan core services independently
        core_scans = [
            ("EC2 instances", "terraback.cli.aws.ec2.instances", "scan_ec2"),
            ("VPC resources", "terraback.cli.aws.vpc.vpcs", "scan_vpcs"),
            ("S3 buckets", "terraback.cli.aws.s3.buckets", "scan_buckets"),
            ("IAM resources", "terraback.cli.aws.iam.roles", "scan_roles"),
        ]
        
        for service_name, module_path, func_name in core_scans:
            typer.echo(f"\nScanning {service_name}...")
            try:
                module = __import__(module_path, fromlist=[func_name])
                scan_func = getattr(module, func_name)
                scan_func(output_dir, profile, region)
            except (ImportError, AttributeError):
                typer.echo(f"{service_name} scanning not available")
    
    typer.echo("\nScan complete!")
    typer.echo(f"Results saved to: {output_dir}/")

@app.command("list-resources")
def list_aws_resources(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory containing import files")
):
    """List all AWS resources previously scanned."""
    from terraback.utils.importer import ImportManager
    
    resource_types = [
        "ec2", "vpc", "security_groups", "subnets", "s3_bucket",
        "iam_roles", "iam_policies", "rds_instance", "lambda_function",
        "elbv2_load_balancer", "route53_zone",
    ]
    
    for resource_type in resource_types:
        import_file = output_dir / f"{resource_type}_import.json"
        if import_file.exists():
            typer.echo(f"\n=== {resource_type} ===")
            ImportManager(output_dir, resource_type).list_all()

@app.command("clean")
def clean_aws_files(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir", help="Directory to clean"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation")
):
    """Clean all AWS-related generated files."""
    from terraback.utils.cleanup import clean_generated_files
    
    if not yes:
        confirm = typer.confirm(f"This will delete all AWS .tf and _import.json files in {output_dir}. Continue?")
        if not confirm:
            raise typer.Abort()
    
    aws_prefixes = [
        "ec2", "vpc", "security_groups", "subnets", "s3_bucket",
        "iam_roles", "iam_policies", "rds_instance", "lambda_function",
        "elbv2_load_balancer", "route53_zone", "sns_topic", "sqs_queue"
    ]
    
    for prefix in aws_prefixes:
        clean_generated_files(output_dir, prefix)
    
    typer.echo("AWS generated files cleaned successfully!")

# Core service commands
@app.command("ec2-scan")
def ec2_scan(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile name"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan with dependencies")
):
    """Scan EC2 instances."""
    try:
        from terraback.cli.aws.ec2.instances import scan_ec2
        scan_ec2(output_dir, profile, region)
    except ImportError:
        typer.echo("Error: EC2 scanning module not found", err=True)
        raise typer.Exit(code=1)

@app.command("vpc-scan")
def vpc_scan(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile name"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region"),
    with_deps: bool = typer.Option(False, "--with-deps", help="Scan with dependencies")
):
    """Scan VPC resources."""
    try:
        from terraback.cli.aws.vpc.vpcs import scan_vpcs
        scan_vpcs(output_dir, profile, region)
    except ImportError:
        typer.echo("Error: VPC scanning module not found", err=True)
        raise typer.Exit(code=1)

@app.command("s3-scan")
def s3_scan(
    output_dir: Path = typer.Option("generated", "-o", "--output-dir"),
    profile: Optional[str] = typer.Option(None, "--profile", "-p", help="AWS profile name"),
    region: Optional[str] = typer.Option(None, "--region", "-r", help="AWS region")
):
    """Scan S3 buckets."""
    try:
        from terraback.cli.aws.s3.buckets import scan_buckets
        scan_buckets(output_dir, profile, region)
    except ImportError:
        typer.echo("Error: S3 scanning module not found", err=True)
        raise typer.Exit(code=1)
