import json
import time
import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, Set, List, Optional, Callable, Any
from functools import wraps
import typer
import inspect

# Import licensing features
from terraback.core.license import check_feature_access, Tier

# Global dictionary to store registered scan functions.
SCAN_FUNCTIONS: Dict[str, Callable] = {}

def performance_monitor(func):
    """
    Decorator to monitor scan function performance, but will NOT
    catch Typer/SystemExit/KeyboardInterrupt.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            typer.echo(f"[PERF] {func.__name__} completed in {duration:.2f}s", err=True)
            return result
        except (ValueError, TypeError, KeyError, AttributeError, IOError, NotImplementedError) as e:
            duration = time.time() - start_time
            typer.echo(f"[PERF] {func.__name__} failed after {duration:.2f}s: {e}", err=True)
            raise
        except (SystemExit, KeyboardInterrupt):  # NEVER catch exit signals
            raise
    return wrapper

class CrossScanRegistry:
    """
    Registry for managing dependencies between resource types,
    with caching, performance monitoring, and cycle detection.
    """

    def __init__(self, cache_file: Optional[Path] = None):
        self.cache_file = cache_file or Path("generated/.terraback/cross_scan_registry.json")
        self.registry: Dict[str, Set[str]] = defaultdict(set)
        self.scan_history: Dict[str, Dict[str, Any]] = {}
        self.performance_stats: Dict[str, List[float]] = defaultdict(list)
        self._version = "2.0"
        self._load()

    def set_output_dir(self, output_dir: Path):
        new_cache_file = output_dir / ".terraback" / "cross_scan_registry.json"
        if new_cache_file != self.cache_file:
            self.cache_file = new_cache_file
            self._load()

    def _normalize(self, name: str) -> str:
        if not isinstance(name, str):
            raise TypeError(f"Resource type must be string, got {type(name)}")
        normalized = name.strip().lower()
        if not normalized:
            raise ValueError("Resource type cannot be empty")
        normalized = normalized.replace("-", "_").replace(" ", "_").replace(".", "_")
        # Remove trailing 's' only if it makes sense (avoid 'was' -> 'wa')
        if len(normalized) > 3 and normalized.endswith('s') and normalized[-2] not in 'ss':
            normalized = normalized[:-1]
        return normalized

    def _generate_cache_hash(self) -> str:
        registry_str = json.dumps(
            {k: sorted(list(v)) for k, v in sorted(self.registry.items())},
            sort_keys=True
        )
        return hashlib.sha256(registry_str.encode()).hexdigest()[:16]

    def _load(self):
        if not self.cache_file.exists():
            self.registry = defaultdict(set)
            return

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            file_version = data.get('_metadata', {}).get('version', '1.0')
            if file_version != self._version:
                typer.echo(f"Warning: Cache version mismatch ({file_version} vs {self._version}). Rebuilding cache.", err=True)
                self.registry = defaultdict(set)
                return
            expected_hash = data.get('_metadata', {}).get('hash')
            registry_data = data.get('registry', {})
            self.registry.clear()
            for k, v_list in registry_data.items():
                try:
                    norm_key = self._normalize(k)
                    if isinstance(v_list, list):
                        valid_deps = {self._normalize(dep) for dep in v_list if isinstance(dep, str) and dep.strip()}
                        self.registry[norm_key].update(valid_deps)
                except (ValueError, TypeError) as e:
                    typer.echo(f"Warning: Skipping invalid registry entry '{k}': {e}", err=True)
                    continue
            if expected_hash:
                actual_hash = self._generate_cache_hash()
                if expected_hash != actual_hash:
                    typer.echo("Warning: Cache integrity check failed. Rebuilding dependencies.", err=True)
                    self.registry = defaultdict(set)
            self.performance_stats = defaultdict(list, data.get('performance_stats', {}))
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            typer.echo(f"Warning: Could not load cross-scan registry from {self.cache_file}. Error: {e}. Starting fresh.", err=True)
            self.registry = defaultdict(set)
            self.performance_stats = defaultdict(list)

    def _save(self):
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            cache_data = {
                '_metadata': {
                    'version': self._version,
                    'hash': self._generate_cache_hash(),
                    'timestamp': time.time(),
                    'total_dependencies': sum(len(deps) for deps in self.registry.values())
                },
                'registry': {k: sorted(list(v)) for k, v in self.registry.items()},
                'performance_stats': {k: v[-10:] for k, v in self.performance_stats.items()}
            }
            temp_file = self.cache_file.with_suffix('.tmp')
            with open(temp_file, "w", encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            temp_file.replace(self.cache_file)
        except IOError as e:
            typer.echo(f"Error: Could not save cross-scan registry to {self.cache_file}. Error: {e}", err=True)

    def register_dependency(self, source_resource_type: str, dependent_resource_type: str):
        try:
            source_key = self._normalize(source_resource_type)
            dep_key = self._normalize(dependent_resource_type)
        except (ValueError, TypeError) as e:
            typer.echo(f"Error: Invalid resource type in dependency registration: {e}", err=True)
            return
        if source_key == dep_key:
            return
        if self._would_create_cycle(source_key, dep_key):
            typer.echo(f"Warning: Skipping dependency {source_key} -> {dep_key} to avoid circular dependency", err=True)
            return
        if dep_key not in self.registry[source_key]:
            self.registry[source_key].add(dep_key)
            self._save()

    def _would_create_cycle(self, source: str, target: str, visited: Optional[Set[str]] = None) -> bool:
        if visited is None:
            visited = set()
        if target == source:
            return True
        if target in visited:
            return False
        visited.add(target)
        for dep in self.registry.get(target, set()):
            if self._would_create_cycle(source, dep, visited.copy()):
                return True
        return False

    def get_dependencies(self, resource_type: str) -> List[str]:
        try:
            norm_type = self._normalize(resource_type)
            return sorted(list(self.registry.get(norm_type, set())))
        except (ValueError, TypeError) as e:
            typer.echo(f"Error: Invalid resource type '{resource_type}': {e}", err=True)
            return []

    def get_dependency_graph(self) -> Dict[str, List[str]]:
        return {k: sorted(list(v)) for k, v in self.registry.items()}

    def validate_registry(self) -> Dict[str, List[str]]:
        issues = {
            'missing_scan_functions': [],
            'circular_dependencies': [],
            'orphaned_dependencies': []
        }
        for resource_type in self.registry.keys():
            if resource_type not in SCAN_FUNCTIONS:
                issues['missing_scan_functions'].append(resource_type)
        for source in self.registry.keys():
            for dep in self.registry[source]:
                if self._has_circular_dependency(source, dep):
                    issues['circular_dependencies'].append(f"{source} -> {dep}")
        return {k: v for k, v in issues.items() if v}

    def _has_circular_dependency(self, start: str, current: str, visited: Optional[Set[str]] = None) -> bool:
        if visited is None:
            visited = set()
        if current == start and visited:
            return True
        if current in visited:
            return False
        visited.add(current)
        for dep in self.registry.get(current, set()):
            if self._has_circular_dependency(start, dep, visited.copy()):
                return True
        return False

    def clear(self):
        if self.cache_file.exists():
            backup_file = self.cache_file.with_suffix('.backup')
            try:
                self.cache_file.rename(backup_file)
                typer.echo(f"Created backup at {backup_file}", err=True)
            except OSError as e:
                typer.echo(f"Warning: Could not create backup: {e}", err=True)
        self.registry.clear()
        self.performance_stats.clear()
        self.scan_history.clear()
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
        except OSError as e:
            typer.echo(f"Error: Could not delete cross-scan registry file {self.cache_file}. Error: {e}", err=True)

# Global instance of the enhanced CrossScanRegistry
cross_scan_registry = CrossScanRegistry()

@performance_monitor
def recursive_scan(
    resource_type: str,
    visited: Optional[Set[str]] = None,
    output_dir: Path = Path("generated"),
    **caller_kwargs
):
    """
    Enhanced recursive scan with better error handling and performance monitoring.
    """
    # License check for recursive scanning
    if not check_feature_access(Tier.PROFESSIONAL):
        typer.secho(
            "Error: Recursive scanning requires a Migration Pass or Enterprise license.",
            fg=typer.colors.RED, bold=True
        )
        typer.echo("To upgrade, visit: https://terraback.io/pricing")
        raise typer.Exit(code=1)

    cross_scan_registry.set_output_dir(output_dir)
    try:
        norm_type = cross_scan_registry._normalize(resource_type)
    except (ValueError, TypeError) as e:
        typer.echo(f"Error: Invalid resource type '{resource_type}': {e}", err=True)
        return

    if visited is None:
        visited = set()
    if norm_type in visited:
        return
    visited.add(norm_type)

    # Prepare kwargs for recursive and scan function calls
    kwargs_for_recursive_call = dict(caller_kwargs)
    kwargs_for_recursive_call.pop('with_deps', None)
    kwargs_for_recursive_call.pop('output_dir', None)
    kwargs_for_current_scan_fn = dict(kwargs_for_recursive_call)
    kwargs_for_current_scan_fn['output_dir'] = output_dir

    typer.echo(f"[RECURSIVE_SCAN] Scanning: {norm_type} -> {output_dir}")
    scan_fn = SCAN_FUNCTIONS.get(norm_type)
    if scan_fn:
        try:
            start_time = time.time()
            sig = inspect.signature(scan_fn)
            filtered_kwargs = {key: value for key, value in kwargs_for_current_scan_fn.items() if key in sig.parameters}
            scan_fn(**filtered_kwargs)
            duration = time.time() - start_time
            cross_scan_registry.performance_stats[norm_type].append(duration)
        except Exception as e:
            typer.echo(f"Error during scan of {norm_type}: {e}", err=True)
    else:
        typer.echo(f"[RECURSIVE_SCAN] No scan function registered for: {norm_type}")

    dependencies = cross_scan_registry.get_dependencies(norm_type)
    for dep_type in dependencies:
        if dep_type not in visited:
            recursive_scan(
                dep_type,
                visited=visited,
                output_dir=output_dir,
                **kwargs_for_recursive_call
            )

def register_scan_function(resource_type: str, fn: Callable):
    """
    Register a scan function for a resource type.
    """
    try:
        norm_type = cross_scan_registry._normalize(resource_type)
    except (ValueError, TypeError) as e:
        typer.echo(f"Error: Cannot register scan function for invalid resource type '{resource_type}': {e}", err=True)
        return
    if not callable(fn):
        typer.echo(f"Error: Scan function for '{resource_type}' must be callable", err=True)
        return
    if norm_type in SCAN_FUNCTIONS:
        typer.echo(f"Warning: Overwriting scan function for resource type '{norm_type}'.", err=True)
    SCAN_FUNCTIONS[norm_type] = fn

def get_scan_statistics() -> Dict[str, Any]:
    """
    Get comprehensive scanning statistics.
    """
    return {
        'registered_functions': len(SCAN_FUNCTIONS),
        'total_dependencies': sum(len(deps) for deps in cross_scan_registry.registry.values()),
        'dependency_graph': cross_scan_registry.get_dependency_graph(),
        'performance_stats': dict(cross_scan_registry.performance_stats),
        'validation_issues': cross_scan_registry.validate_registry()
    }
