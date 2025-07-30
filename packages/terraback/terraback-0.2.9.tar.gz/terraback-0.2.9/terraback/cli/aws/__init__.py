import typer
from pathlib import Path
from typing import Optional

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
    with_deps: bool = typer.Option(False, "--with-deps", help="Recursively scan dependencies")
):
    """Scan all AWS resources across all services."""
    # Ensure resources are registered
    register()
    
    from terraback.cli.aws.session import get_boto_session
    from terraback.core.license import check_feature_access, Tier
    
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
