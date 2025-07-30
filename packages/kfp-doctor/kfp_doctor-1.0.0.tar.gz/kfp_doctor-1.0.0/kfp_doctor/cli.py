import click
import yaml
import json
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from kfp_doctor.parser import get_components_from_argo_workflow
from kfp_doctor.config import load_config
from kfp_doctor.analyzer import analyze_pipeline
from kfp_doctor.autofix import auto_fix_pipeline
from kfp_doctor.config_generator import ConfigGenerator, generate_optimal_config

# Check descriptions for user information
CHECK_DESCRIPTIONS = {
    "MISSING_RESOURCES": "Ensures all components have CPU and memory requests defined",
    "LATEST_IMAGE_TAG": "Warns against using ':latest' image tags for reproducibility",
    "NO_RETRY_POLICY": "Checks that components have retry policies for robustness",
    "PRIVILEGED_CONTAINER": "Detects containers running in privileged mode (security risk)",
    "RUN_AS_ROOT": "Warns about containers that may run as root user",
    "HARDCODED_SECRET": "Identifies potential hardcoded secrets in environment variables",
    "UNUSED_COMPONENT": "Finds components defined but not used in the pipeline DAG",
    "EXCESSIVE_RESOURCES": "Warns about over-provisioned CPU/memory requests",
    "MISSING_LIMITS": "Ensures components have resource limits to prevent resource contention",
    "INSECURE_IMAGE_REGISTRY": "Validates that images come from approved registries"
}

@click.group()
def main():
    """A comprehensive linter for healthy Kubeflow Pipelines."""
    pass

@main.command("list-checks")
def list_checks():
    """List all available checks and their descriptions."""
    console = Console()
    config = load_config()
    
    console.print("\n[bold blue]📋 Available Checks[/bold blue]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Check Name", style="cyan", width=25)
    table.add_column("Description", width=50)
    table.add_column("Enabled", justify="center", width=8)
    table.add_column("Severity", justify="center", width=10)
    
    for check_name, description in CHECK_DESCRIPTIONS.items():
        check_config = config["checks"].get(check_name, {})
        enabled = "✅" if check_config.get("enabled", False) else "❌"
        severity = check_config.get("severity", "N/A")
        
        # Color code severity
        if severity == "ERROR":
            severity_display = f"[red]{severity}[/red]"
        elif severity == "WARNING":
            severity_display = f"[yellow]{severity}[/yellow]"
        else:
            severity_display = severity
            
        table.add_row(check_name, description, enabled, severity_display)
    
    console.print(table)
    console.print(f"\n[dim]💡 Configure checks in .kfp-doctor.yaml or use --config flag[/dim]")

@main.command("analyze")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
@click.option("--output", "-o", type=click.Choice(["console", "json", "yaml"]), default="console", help="Output format")
@click.option("--output-file", type=click.Path(), help="File to write analysis results")
@click.option("--include-cost", is_flag=True, help="Include cost analysis")
@click.option("--include-performance", is_flag=True, help="Include performance analysis")
def analyze(file, output, output_file, include_cost, include_performance):
    """Advanced pipeline analysis: performance, cost, and complexity."""
    console = Console()
    
    if output == "console":
        console.print(f"🔍 Analyzing {file} for performance and cost insights...")

    try:
        with open(file, "r") as f:
            pipeline = yaml.safe_load(f)
    except yaml.YAMLError as e:
        console.print(f"[bold red]❌ Invalid YAML: {e}[/bold red]")
        raise click.Abort()

    parsed_data = get_components_from_argo_workflow(pipeline)
    components = parsed_data["components"]
    used_templates = parsed_data["used_templates"]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running analysis...", total=100)
        
        progress.update(task, advance=30, description="Analyzing resources...")
        analysis_results = analyze_pipeline(components, used_templates)
        
        progress.update(task, advance=40, description="Calculating complexity...")
        progress.update(task, advance=30, description="Generating insights...")

    if output == "console":
        display_analysis_results(console, analysis_results, include_cost, include_performance)
    else:
        # Format for JSON/YAML output
        output_data = format_analysis_for_export(analysis_results)
        
        if output == "json":
            if output_file:
                with open(output_file, "w") as f:
                    json.dump(output_data, f, indent=2, default=str)
                console.print(f"Analysis results written to {output_file}")
            else:
                console.print(json.dumps(output_data, indent=2, default=str))
        else:  # yaml
            if output_file:
                with open(output_file, "w") as f:
                    yaml.dump(output_data, f, default_flow_style=False)
                console.print(f"Analysis results written to {output_file}")
            else:
                console.print(yaml.dump(output_data, default_flow_style=False))

@main.command("fix")
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
@click.option("--output-file", "-o", type=click.Path(), help="Write fixed pipeline to file")
@click.option("--dry-run", is_flag=True, help="Show what would be fixed without applying changes")
@click.option("--backup", is_flag=True, help="Create backup of original file")
def fix(file, output_file, dry_run, backup):
    """Auto-fix common pipeline issues."""
    console = Console()
    
    console.print(f"🔧 {'Analyzing fixes for' if dry_run else 'Auto-fixing'} {file}...")

    try:
        with open(file, "r") as f:
            pipeline = yaml.safe_load(f)
    except yaml.YAMLError as e:
        console.print(f"[bold red]❌ Invalid YAML: {e}[/bold red]")
        raise click.Abort()

    parsed_data = get_components_from_argo_workflow(pipeline)
    components = parsed_data["components"]
    config = load_config()

    # Apply auto-fixes
    fixed_pipeline, fix_summary = auto_fix_pipeline(pipeline, components, config)

    if fix_summary["total_fixes"] == 0:
        success_panel = Panel.fit(
            "✅ No fixes needed!\n\nYour pipeline is already following best practices.",
            title="[green]Pipeline is optimal![/green]",
            border_style="green"
        )
        console.print(success_panel)
        return

    # Display fix summary
    display_fix_summary(console, fix_summary, dry_run)

    if not dry_run:
        # Determine output file
        if not output_file:
            output_file = file  # Overwrite original
        
        # Create backup if requested
        if backup and output_file == file:
            backup_file = f"{file}.backup"
            with open(file, "r") as original, open(backup_file, "w") as backup_f:
                backup_f.write(original.read())
            console.print(f"📁 Backup created: {backup_file}")

        # Write fixed pipeline
        with open(output_file, "w") as f:
            yaml.dump(fixed_pipeline, f, default_flow_style=False, sort_keys=False)
        
        console.print(f"✅ Fixed pipeline written to: {output_file}")

def display_analysis_results(console: Console, results: dict, include_cost: bool, include_performance: bool):
    """Display analysis results in console format."""
    complexity = results["complexity_metrics"]
    
    # Complexity Overview
    console.print("\n[bold blue]📊 Pipeline Complexity Analysis[/bold blue]")
    
    complexity_table = Table(show_header=True, header_style="bold magenta")
    complexity_table.add_column("Metric", style="cyan")
    complexity_table.add_column("Value", justify="center")
    complexity_table.add_column("Assessment", justify="center")
    
    # Complexity scoring
    if complexity.complexity_score < 5:
        score_assessment = "[green]Simple[/green]"
    elif complexity.complexity_score < 10:
        score_assessment = "[yellow]Moderate[/yellow]"
    else:
        score_assessment = "[red]Complex[/red]"
    
    complexity_table.add_row("Total Components", str(complexity.total_components), "")
    complexity_table.add_row("Dependency Depth", str(complexity.dependency_depth), "")
    complexity_table.add_row("Max Parallelism", str(complexity.max_parallelism), "")
    complexity_table.add_row("Complexity Score", str(complexity.complexity_score), score_assessment)
    
    console.print(complexity_table)

    if include_cost:
        # Cost Analysis
        cost_data = results["cost_analysis"]
        console.print("\n[bold blue]💰 Cost Analysis[/bold blue]")
        
        cost_summary_panel = Panel.fit(
            f"💵 Estimated Cost per Hour: ${cost_data['total_cost_per_hour']}\n"
            f"📅 Estimated Cost per Day: ${cost_data['total_cost_per_day']}\n"
            f"📅 Estimated Cost per Month: ${cost_data['total_cost_per_month']}\n"
            f"🎯 Optimization Potential: ${cost_data['optimization_potential']}/hour",
            title="[cyan]Cost Summary[/cyan]",
            border_style="cyan"
        )
        console.print(cost_summary_panel)
        
        # Component cost breakdown
        if len(cost_data['component_breakdown']) > 1:
            cost_table = Table(show_header=True, header_style="bold magenta", title="Cost Breakdown by Component")
            cost_table.add_column("Component", style="cyan")
            cost_table.add_column("CPU Cores", justify="center")
            cost_table.add_column("Memory (GB)", justify="center")
            cost_table.add_column("Cost/Hour", justify="center")
            cost_table.add_column("Cost/Month", justify="center")
            
            for item in cost_data['component_breakdown']:
                cost_table.add_row(
                    item['component'][:25] + "..." if len(item['component']) > 25 else item['component'],
                    str(item['cpu_cores']),
                    str(item['memory_gb']),
                    f"${item['cost_per_hour']}",
                    f"${item['cost_per_month']}"
                )
            
            console.print(cost_table)

    if include_performance:
        # Performance Insights
        performance = results["performance_insights"]
        console.print("\n[bold blue]⚡ Performance Insights[/bold blue]")
        
        if performance.bottleneck_components:
            console.print("\n[bold red]🚨 Potential Bottlenecks:[/bold red]")
            for bottleneck in performance.bottleneck_components:
                console.print(f"  • {bottleneck}")
        
        if performance.resource_imbalance:
            console.print("\n[bold yellow]⚠️  Resource Imbalances:[/bold yellow]")
            for imbalance in performance.resource_imbalance:
                console.print(f"  • {imbalance}")
        
        if performance.optimization_suggestions:
            console.print("\n[bold green]💡 Optimization Suggestions:[/bold green]")
            for suggestion in performance.optimization_suggestions:
                console.print(f"  • {suggestion}")
        
        runtime_panel = Panel.fit(
            f"⏱️  Estimated Runtime: {performance.estimated_runtime_minutes} minutes\n"
            f"🎯 Based on resource allocation and component complexity",
            title="[magenta]Runtime Estimate[/magenta]",
            border_style="magenta"
        )
        console.print(runtime_panel)

def display_fix_summary(console: Console, fix_summary: dict, dry_run: bool):
    """Display auto-fix summary."""
    total_fixes = fix_summary["total_fixes"]
    categories = fix_summary["categories"]
    
    title = f"🔍 Potential Fixes ({total_fixes})" if dry_run else f"🔧 Applied Fixes ({total_fixes})"
    
    # Summary panel
    summary_text = f"{'Would apply' if dry_run else 'Applied'} {total_fixes} fix(es):\n\n"
    if categories["resources"] > 0:
        summary_text += f"🔋 Resources: {categories['resources']} fixes\n"
    if categories["security"] > 0:
        summary_text += f"🔒 Security: {categories['security']} fixes\n"
    if categories["reliability"] > 0:
        summary_text += f"🛡️  Reliability: {categories['reliability']} fixes\n"
    if categories["images"] > 0:
        summary_text += f"🏷️  Images: {categories['images']} fixes\n"
    if categories["secrets"] > 0:
        summary_text += f"🔐 Secrets: {categories['secrets']} fixes\n"
    
    panel_style = "yellow" if dry_run else "green"
    summary_panel = Panel.fit(
        summary_text.strip(),
        title=f"[{panel_style}]{title}[/{panel_style}]",
        border_style=panel_style
    )
    console.print(summary_panel)
    
    # Detailed fixes
    if fix_summary["fixes_applied"]:
        console.print(f"\n[bold blue]📋 Detailed {'Preview' if dry_run else 'Changes'}:[/bold blue]")
        for i, fix in enumerate(fix_summary["fixes_applied"], 1):
            console.print(f"  {i}. {fix}")

def format_analysis_for_export(results: dict) -> dict:
    """Format analysis results for JSON/YAML export."""
    return {
        "complexity_metrics": {
            "total_components": results["complexity_metrics"].total_components,
            "max_parallelism": results["complexity_metrics"].max_parallelism,
            "dependency_depth": results["complexity_metrics"].dependency_depth,
            "complexity_score": results["complexity_metrics"].complexity_score
        },
        "cost_analysis": results["cost_analysis"],
        "performance_insights": {
            "bottleneck_components": results["performance_insights"].bottleneck_components,
            "resource_imbalance": results["performance_insights"].resource_imbalance,
            "optimization_suggestions": results["performance_insights"].optimization_suggestions,
            "estimated_runtime_minutes": results["performance_insights"].estimated_runtime_minutes
        },
        "resource_usage": [
            {
                "cpu_request": usage.cpu_request,
                "memory_request_gb": usage.memory_request_gb,
                "cpu_limit": usage.cpu_limit,
                "memory_limit_gb": usage.memory_limit_gb,
                "estimated_cost_per_hour": usage.estimated_cost_per_hour
            }
            for usage in results["resource_usage"]
        ]
    }

def run_check(check_name, config, component, issues, verbose=False, console=None):
    check_config = config["checks"].get(check_name)
    if not check_config or not check_config.get("enabled"):
        if verbose and console:
            console.print(f"  [dim]⏭️  Skipping {check_name} (disabled)[/dim]")
        return

    if verbose and console:
        console.print(f"  🔍 Running {check_name}...")

    component_name = component["name"]
    container = component["container"]
    severity = check_config.get("severity", "WARNING")

    # --- Validation Checks ---
    if check_name == "MISSING_RESOURCES":
        resources = container.get("resources", {})
        requests = resources.get("requests", {})
        if "cpu" not in requests or "memory" not in requests:
            issues.append({"severity": severity, "component": component_name, "message": "Missing resource requests.", "suggestion": "Add .set_cpu_request() and .set_memory_request()."})
    
    elif check_name == "LATEST_IMAGE_TAG":
        image = container.get("image", "")
        if image.endswith(":latest"):
            issues.append({"severity": severity, "component": component_name, "message": f"Image '{image}' uses a ':latest' tag.", "suggestion": "Use a specific version for reproducible runs."})

    elif check_name == "NO_RETRY_POLICY":
        if not component["retry_strategy"]:
            issues.append({"severity": severity, "component": component_name, "message": "No retry policy defined.", "suggestion": "Consider adding a .set_retry() policy for robustness."})

    # --- Security Checks ---
    elif check_name == "PRIVILEGED_CONTAINER":
        if container.get("securityContext", {}).get("privileged"):
            issues.append({"severity": severity, "component": component_name, "message": "Container runs in privileged mode.", "suggestion": "Set `securityContext.privileged` to `false` or remove it."})

    elif check_name == "RUN_AS_ROOT":
        run_as_user = container.get("securityContext", {}).get("runAsUser")
        if run_as_user is None or run_as_user == 0:
            issues.append({"severity": severity, "component": component_name, "message": "Container may run as root user.", "suggestion": "Set `securityContext.runAsUser` to a non-zero value (e.g., 1000)."})

    elif check_name == "HARDCODED_SECRET":
        env_vars = container.get("env", [])
        secret_keywords = ["SECRET", "PASSWORD", "API_KEY", "TOKEN", "ACCESS_KEY"]
        for env_var in env_vars:
            var_name = env_var.get("name", "").upper()
            if any(keyword in var_name for keyword in secret_keywords):
                if "valueFrom" not in env_var or "secretKeyRef" not in env_var.get("valueFrom", {}):
                    issues.append({"severity": severity, "component": component_name, "message": f"Potential hardcoded secret in env var '{env_var.get('name')}'.", "suggestion": "Load secrets using `secretKeyRef` instead of direct values."})

    # --- New Enhanced Checks ---
    elif check_name == "EXCESSIVE_RESOURCES":
        resources = container.get("resources", {})
        requests = resources.get("requests", {})
        
        max_cpu = check_config.get("max_cpu", "8")
        max_memory = check_config.get("max_memory", "16Gi")
        
        # Simple CPU check (assumes numeric values or "m" suffix)
        cpu_request = requests.get("cpu", "")
        if cpu_request:
            try:
                cpu_val = float(cpu_request.rstrip("m")) / 1000 if cpu_request.endswith("m") else float(cpu_request)
                max_cpu_val = float(max_cpu.rstrip("m")) / 1000 if max_cpu.endswith("m") else float(max_cpu)
                if cpu_val > max_cpu_val:
                    issues.append({"severity": severity, "component": component_name, "message": f"CPU request '{cpu_request}' exceeds maximum '{max_cpu}'.", "suggestion": f"Consider reducing CPU request to '{max_cpu}' or below."})
            except ValueError:
                pass  # Skip if we can't parse the values
        
        # Simple memory check (assumes Gi suffix for simplicity)
        memory_request = requests.get("memory", "")
        if memory_request and memory_request.endswith("Gi"):
            try:
                memory_val = float(memory_request.rstrip("Gi"))
                max_memory_val = float(max_memory.rstrip("Gi"))
                if memory_val > max_memory_val:
                    issues.append({"severity": severity, "component": component_name, "message": f"Memory request '{memory_request}' exceeds maximum '{max_memory}'.", "suggestion": f"Consider reducing memory request to '{max_memory}' or below."})
            except ValueError:
                pass  # Skip if we can't parse the values

    elif check_name == "MISSING_LIMITS":
        resources = container.get("resources", {})
        limits = resources.get("limits", {})
        if "cpu" not in limits or "memory" not in limits:
            issues.append({"severity": severity, "component": component_name, "message": "Missing resource limits.", "suggestion": "Add .set_cpu_limit() and .set_memory_limit() to prevent resource contention."})

    elif check_name == "INSECURE_IMAGE_REGISTRY":
        image = container.get("image", "")
        allowed_registries = check_config.get("allowed_registries", [])
        if allowed_registries and image:
            registry_allowed = any(image.startswith(registry) for registry in allowed_registries)
            if not registry_allowed:
                issues.append({"severity": severity, "component": component_name, "message": f"Image '{image}' uses an untrusted registry.", "suggestion": f"Use images from approved registries: {', '.join(allowed_registries)}."})

def show_scan_summary(console, components, config, verbose=False):
    """Show what was scanned and what checks were performed."""
    if not verbose:
        return
        
    # Show component summary
    console.print(f"\n[bold blue]📊 Scan Summary[/bold blue]")
    console.print(f"  • Found {len(components)} component(s)")
    
    if components:
        component_names = [c["name"] for c in components]
        console.print(f"  • Components: {', '.join(component_names)}")
    
    # Show enabled checks
    enabled_checks = [name for name, check_config in config["checks"].items() 
                     if check_config.get("enabled", False)]
    console.print(f"  • Enabled checks: {len(enabled_checks)}")
    
    if verbose:
        for check_name in enabled_checks:
            severity = config["checks"][check_name].get("severity", "WARNING")
            console.print(f"    - {check_name} ({severity})")

def output_issues(issues, output_format, output_file, console, verbose=False, components_count=0, enabled_checks_count=0):
    """Output issues in the specified format."""
    if output_format == "json":
        output_data = {
            "summary": {
                "total_issues": len(issues), 
                "errors": sum(1 for i in issues if i["severity"] == "ERROR"), 
                "warnings": sum(1 for i in issues if i["severity"] == "WARNING"),
                "components_scanned": components_count,
                "checks_performed": enabled_checks_count
            },
            "issues": issues
        }
        if output_file:
            with open(output_file, "w") as f:
                json.dump(output_data, f, indent=2)
            console.print(f"Results written to {output_file}")
        else:
            console.print(json.dumps(output_data, indent=2))
    
    elif output_format == "yaml":
        output_data = {
            "summary": {
                "total_issues": len(issues), 
                "errors": sum(1 for i in issues if i["severity"] == "ERROR"), 
                "warnings": sum(1 for i in issues if i["severity"] == "WARNING"),
                "components_scanned": components_count,
                "checks_performed": enabled_checks_count
            },
            "issues": issues
        }
        if output_file:
            with open(output_file, "w") as f:
                yaml.dump(output_data, f, default_flow_style=False)
            console.print(f"Results written to {output_file}")
        else:
            console.print(yaml.dump(output_data, default_flow_style=False))
    
    else:  # console format
        if not issues:
            # Show success message with summary
            success_panel = Panel.fit(
                f"✅ All checks passed!\n\n"
                f"[dim]📊 Scanned {components_count} component(s) with {enabled_checks_count} check(s)[/dim]",
                title="[green]Pipeline is healthy![/green]",
                border_style="green"
            )
            console.print(success_panel)
            return

        table = Table(title="🩺 kfp-doctor Report")
        table.add_column("Severity", style="bold", width=10)
        table.add_column("Component", width=25)
        table.add_column("Issue", width=40)
        table.add_column("Suggestion", width=45)

        error_count = 0
        warning_count = 0
        for issue in issues:
            style = ""
            if issue["severity"] == "ERROR":
                style = "red"
                error_count += 1
            elif issue["severity"] == "WARNING":
                style = "yellow"
                warning_count += 1
            
            table.add_row(
                f"[{style}]{issue['severity']}[/{style}]",
                issue["component"],
                issue["message"],
                issue["suggestion"]
            )

        console.print(table)

        # Summary with more detail
        if error_count > 0:
            summary_text = f"❌ Found {len(issues)} issue(s): {error_count} error(s), {warning_count} warning(s)"
            summary_style = "red"
            health_status = "Pipeline has errors"
        else:
            summary_text = f"⚠️  Found {len(issues)} warning(s)"
            summary_style = "yellow"
            health_status = "Pipeline is healthy with suggestions"
            
        summary_panel = Panel.fit(
            f"{summary_text}\n\n"
            f"[dim]📊 Scanned {components_count} component(s) with {enabled_checks_count} check(s)[/dim]",
            title=f"[{summary_style}]{health_status}[/{summary_style}]",
            border_style=summary_style
        )
        console.print(summary_panel)

@main.command()
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
@click.option("--config", "-c", type=click.Path(exists=True), help="Path to configuration file")
@click.option("--output", "-o", type=click.Choice(["console", "json", "yaml"]), default="console", help="Output format")
@click.option("--output-file", type=click.Path(), help="File to write output to (default: stdout)")
@click.option("--fail-on", type=click.Choice(["error", "warning", "never"]), default="error", help="When to exit with non-zero code")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed information about checks being performed")
@click.option("--dry-run", is_flag=True, help="Show what would be checked without actually running checks")
def check(file, config, output, output_file, fail_on, verbose, dry_run):
    """Check a compiled Kubeflow Pipeline file for issues."""
    console = Console()
    
    if output == "console":
        console.print(f"🩺 Analyzing {file}...")
    
    # Load configuration
    if config:
        config_data = load_config(os.path.dirname(config))
        if verbose:
            console.print(f"📄 Using config: {config}")
    else:
        config_data = load_config()
        if verbose:
            console.print("📄 Using default configuration")

    try:
        with open(file, "r") as f:
            pipeline = yaml.safe_load(f)
    except yaml.YAMLError as e:
        if output == "console":
            console.print(f"[bold red]❌ Invalid YAML: {e}[/bold red]")
        else:
            error_data = {"error": f"Invalid YAML: {e}"}
            if output == "json":
                console.print(json.dumps(error_data))
            else:
                console.print(yaml.dump(error_data))
        raise click.Abort()

    parsed_data = get_components_from_argo_workflow(pipeline)
    components = parsed_data["components"]
    used_templates = parsed_data["used_templates"]
    
    # Count enabled checks
    enabled_checks = [name for name, check_config in config_data["checks"].items() 
                     if check_config.get("enabled", False)]
    
    if dry_run:
        console.print(f"\n[bold blue]🔍 Dry Run - What would be checked:[/bold blue]")
        console.print(f"  • Components found: {len(components)}")
        if components:
            for component in components:
                console.print(f"    - {component['name']}")
        console.print(f"  • Enabled checks: {len(enabled_checks)}")
        for check_name in enabled_checks:
            severity = config_data["checks"][check_name].get("severity", "WARNING")
            description = CHECK_DESCRIPTIONS.get(check_name, "No description available")
            console.print(f"    - {check_name} ({severity}): {description}")
        return

    if verbose:
        show_scan_summary(console, components, config_data, verbose)
        console.print(f"\n[bold blue]🔍 Running Checks[/bold blue]")

    issues = []

    # Run component-level checks
    for component in components:
        if verbose:
            console.print(f"\n📦 Checking component: [cyan]{component['name']}[/cyan]")
        
        for check_name in config_data["checks"]:
            if check_name != "UNUSED_COMPONENT": # Handle this separately
                run_check(check_name, config_data, component, issues, verbose, console)

    # --- Graph-based Checks ---
    if config_data["checks"].get("UNUSED_COMPONENT", {}).get("enabled"):
        if verbose:
            console.print(f"\n🔗 Running graph-based checks...")
            console.print(f"  🔍 Checking for unused components...")
            
        all_component_names = {c["name"] for c in components}
        unused_components = all_component_names - used_templates
        for component_name in unused_components:
            issues.append({
                "severity": config_data["checks"]["UNUSED_COMPONENT"].get("severity", "WARNING"),
                "component": component_name,
                "message": "Component is defined but not used in the pipeline DAG.",
                "suggestion": "Remove the component definition if it is no longer needed."
            })

    if verbose:
        console.print(f"\n[bold blue]📋 Check Results[/bold blue]")

    # Output results
    output_issues(issues, output, output_file, console, verbose, len(components), len(enabled_checks))

    # Determine exit code based on fail_on setting
    if fail_on == "never":
        return
    elif fail_on == "warning" and issues:
        raise click.Abort()
    elif fail_on == "error":
        error_count = sum(1 for i in issues if i["severity"] == "ERROR")
        if error_count > 0:
            raise click.Abort()

@main.command("generate-config")
@click.option("--template", "-t", type=click.Choice(["development", "staging", "production", "security-focused", "cost-optimized"]), help="Configuration template to use")
@click.option("--output-file", "-o", type=click.Path(), default=".kfp-doctor.yaml", help="Output file for configuration")
@click.option("--analyze-pipeline", type=click.Path(exists=True), help="Analyze this pipeline file to suggest optimal config")
@click.option("--list-templates", is_flag=True, help="List available configuration templates")
def generate_config(template, output_file, analyze_pipeline, list_templates):
    """Generate optimal kfp-doctor configuration files."""
    console = Console()
    generator = ConfigGenerator()
    
    if list_templates:
        console.print("\n[bold blue]📋 Available Configuration Templates[/bold blue]\n")
        
        templates_table = Table(show_header=True, header_style="bold magenta")
        templates_table.add_column("Template", style="cyan", width=20)
        templates_table.add_column("Description", width=60)
        
        for name, description in generator.get_available_templates().items():
            templates_table.add_row(name, description)
        
        console.print(templates_table)
        console.print(f"\n[dim]💡 Use --template <name> to generate configuration[/dim]")
        return
    
    # Analyze pipeline if provided
    suggestions = None
    components = []
    issues = []
    
    if analyze_pipeline:
        console.print(f"🔍 Analyzing {analyze_pipeline} to suggest optimal configuration...")
        
        try:
            with open(analyze_pipeline, "r") as f:
                pipeline = yaml.safe_load(f)
        except yaml.YAMLError as e:
            console.print(f"[bold red]❌ Invalid YAML: {e}[/bold red]")
            raise click.Abort()
        
        # Parse pipeline and run basic checks to get issues
        parsed_data = get_components_from_argo_workflow(pipeline)
        components = parsed_data["components"]
        
        # Run a quick analysis to identify issues
        current_config = load_config()
        for component in components:
            for check_name in current_config["checks"]:
                if check_name != "UNUSED_COMPONENT":
                    run_check(check_name, current_config, component, issues, verbose=False)
        
        config, suggestions = generate_optimal_config(components, issues, template)
        
        # Display analysis results
        console.print(f"\n[bold blue]📊 Pipeline Analysis Results[/bold blue]")
        console.print(f"  • Components found: {len(components)}")
        console.print(f"  • Issues detected: {len(issues)}")
        console.print(f"  • Recommended template: [cyan]{suggestions['recommended_template']}[/cyan]")
        
        if suggestions['reasoning']:
            console.print(f"\n[bold yellow]💡 Reasoning:[/bold yellow]")
            for reason in suggestions['reasoning']:
                console.print(f"  • {reason}")
    
    else:
        # Use provided template or default
        template_name = template or "staging"
        config = generator.generate_config(template_name)
        console.print(f"🎯 Generating configuration from template: [cyan]{template_name}[/cyan]")
    
    # Save configuration
    generator.save_config(config, output_file)
    
    success_panel = Panel.fit(
        f"✅ Configuration generated successfully!\n\n"
        f"📁 File: {output_file}\n"
        f"📋 Template: {config.get('# Template', 'Custom')}\n"
        f"📝 Description: {config.get('# Description', 'Generated configuration')}\n\n"
        f"[dim]💡 Use this config with: kfp-doctor check --config {output_file} <pipeline.yaml>[/dim]",
        title="[green]Configuration Ready![/green]",
        border_style="green"
    )

@main.command("help")
@click.option("--examples", is_flag=True, help="Show usage examples")
def help_command(examples):
    """Show comprehensive help and feature overview."""
    console = Console()
    
    # Main header
    console.print("\n[bold blue]🩺 kfp-doctor - Comprehensive Kubeflow Pipeline Linter[/bold blue]\n")
    
    # Feature overview
    features_table = Table(title="🚀 Available Features", show_header=True, header_style="bold magenta")
    features_table.add_column("Command", style="cyan", width=20)
    features_table.add_column("Description", width=50)
    features_table.add_column("Key Benefits", width=30)
    
    features_table.add_row(
        "check", 
        "Lint pipeline files for issues and best practices", 
        "Quality assurance, CI/CD integration"
    )
    features_table.add_row(
        "list-checks", 
        "Show all available checks with descriptions", 
        "Transparency, customization"
    )
    features_table.add_row(
        "analyze", 
        "Advanced performance, cost, and complexity analysis", 
        "Cost optimization, performance tuning"
    )
    features_table.add_row(
        "fix", 
        "Auto-fix common pipeline issues", 
        "Automated remediation, time saving"
    )
    features_table.add_row(
        "generate-config", 
        "Generate optimal configurations for different environments", 
        "Environment-specific settings, best practices"
    )
    
    console.print(features_table)
    
    # Key highlights
    highlights_panel = Panel.fit(
        "✅ [bold]10 comprehensive checks[/bold] covering security, performance, and best practices\n"
        "💰 [bold]Cost analysis[/bold] with per-component breakdown and optimization suggestions\n"
        "🔧 [bold]Auto-fix capabilities[/bold] for common issues like missing resources and security contexts\n"
        "📊 [bold]Performance insights[/bold] including bottleneck detection and runtime estimation\n"
        "🎯 [bold]Environment-specific configs[/bold] for development, staging, and production\n"
        "🔍 [bold]Rich UI[/bold] with real-time progress, verbose mode, and beautiful reporting\n"
        "📈 [bold]CI/CD ready[/bold] with JSON/YAML output and configurable fail conditions",
        title="[green]🌟 Key Highlights[/green]",
        border_style="green"
    )
    console.print(highlights_panel)
    
    if examples:
        console.print("\n[bold blue]📋 Usage Examples[/bold blue]\n")
        
        examples_data = [
            ("Basic pipeline check", "kfp-doctor check pipeline.yaml"),
            ("Verbose check with real-time progress", "kfp-doctor check pipeline.yaml --verbose"),
            ("Check with custom config", "kfp-doctor check pipeline.yaml --config .kfp-doctor.yaml"),
            ("Show all available checks", "kfp-doctor list-checks"),
            ("Performance and cost analysis", "kfp-doctor analyze pipeline.yaml --include-cost --include-performance"),
            ("Auto-fix pipeline issues", "kfp-doctor fix pipeline.yaml --backup"),
            ("Preview fixes without applying", "kfp-doctor fix pipeline.yaml --dry-run"),
            ("Generate production config", "kfp-doctor generate-config --template production"),
            ("Smart config based on pipeline", "kfp-doctor generate-config --analyze-pipeline pipeline.yaml"),
            ("CI/CD integration", "kfp-doctor check pipeline.yaml --output json --fail-on error"),
        ]
        
        for description, command in examples_data:
            console.print(f"[bold yellow]→[/bold yellow] {description}")
            console.print(f"  [dim]{command}[/dim]\n")
    
    # Quick start
    quickstart_panel = Panel.fit(
        "1️⃣ [bold]Install:[/bold] pip install kfp-doctor\n"
        "2️⃣ [bold]Basic check:[/bold] kfp-doctor check your-pipeline.yaml\n"
        "3️⃣ [bold]Generate config:[/bold] kfp-doctor generate-config --template staging\n"
        "4️⃣ [bold]Auto-fix issues:[/bold] kfp-doctor fix your-pipeline.yaml --backup\n"
        "5️⃣ [bold]Analyze performance:[/bold] kfp-doctor analyze your-pipeline.yaml --include-cost\n\n"
        "[dim]💡 Use --help with any command for detailed options[/dim]",
        title="[cyan]🚀 Quick Start[/cyan]",
        border_style="cyan"
    )
    console.print(quickstart_panel)

if __name__ == "__main__":
    main()