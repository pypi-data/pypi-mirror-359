"""Parallel scanning utilities for terraback."""
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Callable
from dataclasses import dataclass
import typer
import threading

@dataclass
class ScanTask:
    """Represents a scan task for a specific resource type."""
    name: str
    function: Callable
    kwargs: Dict[str, Any]

class ParallelScanManager:
    """Manages parallel scanning of cloud resources."""
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self._lock = threading.Lock()
        self._failed = {}

    def scan_parallel(self, tasks: List[ScanTask]) -> Dict[str, Any]:
        """Execute scan tasks in parallel."""
        start_time = time.time()
        total_tasks = len(tasks)
        results = {}

        typer.echo(f"\nStarting parallel scan with {self.max_workers} workers")
        typer.echo(f"Total tasks: {total_tasks}\n")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {executor.submit(self._execute_task, task): task for task in tasks}
            completed = 0
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                completed += 1
                try:
                    result = future.result()
                    results[task.name] = result
                    status = "OK"
                    status_color = typer.colors.GREEN
                except Exception as e:
                    self._failed[task.name] = str(e)
                    status = "FAIL"
                    status_color = typer.colors.RED
                    results[task.name] = {"error": str(e)}
                typer.secho(
                    f"[{status}] {task.name:<25} ({completed}/{total_tasks})",
                    fg=status_color
                )

        total_time = time.time() - start_time
        successful = len(results) - len(self._failed)
        speedup = (total_tasks * 2) / total_time if total_time > 0 else 1  # crude estimate

        # Summary
        typer.echo("\n" + "-"*50)
        typer.echo("PARALLEL SCAN SUMMARY")
        typer.echo("-"*50)
        typer.echo(f"Total time:       {total_time:.2f} seconds")
        typer.echo(f"Successful:       {successful}/{total_tasks}")
        if self._failed:
            typer.echo(f"Failed:           {len(self._failed)}")
        typer.echo(f"Estimated speedup: ~{speedup:.1f}x\n")

        if self._failed:
            typer.echo("Failed tasks:")
            for name, error in self._failed.items():
                typer.echo(f"   - {name}: {error}")

        return {
            'results': results,
            'errors': self._failed,
            'total_time': total_time,
            'successful': successful,
            'failed': len(self._failed),
            'speedup': speedup
        }

    def _execute_task(self, task: ScanTask) -> Any:
        """Execute a single scan task."""
        return task.function(**task.kwargs)

def create_scan_tasks(resource_configs: List[Dict[str, Any]],
                     base_kwargs: Dict[str, Any]) -> List[ScanTask]:
    """Create scan tasks from resource configurations."""
    tasks = []
    for config in resource_configs:
        kwargs = base_kwargs.copy()
        kwargs.update(config.get('extra_kwargs', {}))
        tasks.append(ScanTask(
            name=config['name'],
            function=config['function'],
            kwargs=kwargs
        ))
    return tasks
